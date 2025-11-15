from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig

from .pjsk_emoji.models import RenderState
from .pjsk_emoji.persistence import StatePersistence
from .pjsk_emoji.utils import (
    applyDefaults,
    calculateOffsets,
    calculateFontSize,
    findLongestLine,
    parseKoishiFlags,
    sanitizeText,
    validateCurveIntensity,
)
from .pjsk_emoji.domain import (
    get_character_name,
    get_character_image_buffer,
    get_character_list_image,
    format_character_list,
    format_character_groups,
    format_character_detail,
    CHARACTER_NAMES,
)
from .pjsk_emoji.messaging import (
    MessageAdapter,
    create_adjustment_buttons,
    encode_koishi_button_text,
)
from .pjsk_emoji.renderer import renderer_manager


class ConfigWrapper:
    """Wraps AstrBotConfig to provide convenient access to plugin configuration."""
    
    def __init__(self, config: AstrBotConfig) -> None:
        self.config = config
    
    def get(self, key: str, default=None):
        """Get config value with optional default."""
        try:
            return self.config.get(key, default)
        except (AttributeError, TypeError):
            return default
    
    @property
    def adaptive_text_sizing(self) -> bool:
        return self.get('adaptive_text_sizing', True)
    
    @property
    def enable_markdown_flow(self) -> bool:
        return self.get('enable_markdown_flow', False)
    
    @property
    def show_success_messages(self) -> bool:
        return self.get('show_success_messages', True)
    
    @property
    def mention_user_on_render(self) -> bool:
        return self.get('mention_user_on_render', True)
    
    @property
    def should_wait_for_user_input_before_sending_commands(self) -> bool:
        return self.get('should_wait_for_user_input_before_sending_commands', False)
    
    @property
    def should_mention_user_in_message(self) -> bool:
        return self.get('should_mention_user_in_message', False)
    
    @property
    def retract_delay_ms(self) -> int:
        return self.get('retract_delay_ms', 0)
    
    @property
    def default_curve_intensity(self) -> float:
        return self.get('default_curve_intensity', 0.5)
    
    @property
    def enable_text_shadow(self) -> bool:
        return self.get('enable_text_shadow', True)
    
    @property
    def default_emoji_set(self) -> str:
        return self.get('default_emoji_set', 'apple')
    
    @property
    def persistence_enabled(self) -> bool:
        return self.get('persistence_enabled', True)
    
    @property
    def state_ttl_hours(self) -> int:
        return self.get('state_ttl_hours', 24)
    
    # Validation ranges - hardcoded since not exposed in schema
    @property
    def font_size_min(self) -> int:
        return 18
    
    @property
    def font_size_max(self) -> int:
        return 84
    
    @property
    def font_size_step(self) -> int:
        return 4
    
    @property
    def line_spacing_min(self) -> float:
        return 0.6
    
    @property
    def line_spacing_max(self) -> float:
        return 3.0
    
    @property
    def line_spacing_step(self) -> float:
        return 0.1
    
    @property
    def offset_min(self) -> int:
        return -240
    
    @property
    def offset_max(self) -> int:
        return 240
    
    @property
    def offset_step(self) -> int:
        return 12
    
    @property
    def max_text_length(self) -> int:
        return 120


class StateManager:
    """Simple in-memory state storage keyed by platform/session information."""

    def __init__(self) -> None:
        self._states: Dict[Tuple[str, str], RenderState] = {}

    def get(self, key: Tuple[str, str]) -> Optional[RenderState]:
        # Ensure key is hashable (tuple of strings)
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError(f"StateManager key must be a tuple of (platform, session_id), got: {type(key)}")
        if not all(isinstance(k, str) for k in key):
            raise TypeError(f"StateManager key elements must be strings, got: {key}")
        return self._states.get(key)

    def set(self, key: Tuple[str, str], state: RenderState) -> None:
        # Ensure key is hashable (tuple of strings)
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError(f"StateManager key must be a tuple of (platform, session_id), got: {type(key)}")
        if not all(isinstance(k, str) for k in key):
            raise TypeError(f"StateManager key elements must be strings, got: {key}")
        self._states[key] = state

    def exists(self, key: Tuple[str, str]) -> bool:
        # Ensure key is hashable (tuple of strings)
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError(f"StateManager key must be a tuple of (platform, session_id), got: {type(key)}")
        if not all(isinstance(k, str) for k in key):
            raise TypeError(f"StateManager key elements must be strings, got: {key}")
        return key in self._states


class AdjustError(Exception):
    """Base class for adjustment command errors."""


class MissingStateError(AdjustError):
    """Raised when an adjustment is requested without a prior render."""


class ValidationError(AdjustError):
    """Raised when user input cannot be processed."""


class MessagingHelper:
    """Utility for building consistent AstrBot responses."""

    QUICK_ACTION_LINE = (
        "快捷操作：/pjsk.调整 字号.大 ｜ 字号.小 ｜ 行距.大 ｜ 行距.小 ｜ 位置.上 ｜ 位置.下 ｜ 位置.左 ｜ 位置.右 ｜ 曲线 切换"
    )

    def __init__(self, event: AstrMessageEvent) -> None:
        self.event = event

    def summary(self, state: RenderState, headline: str) -> MessageEventResult:
        lines = [headline, ""]
        lines.extend(self._state_lines(state))
        lines.append("")
        lines.append(self.QUICK_ACTION_LINE)
        return self.event.plain_result("\n".join(lines))

    def guidance(self) -> MessageEventResult:
        lines = [
            "pjsk.调整 指令指南：",
            "• 文本 <内容> —— 更新显示文本。",
            "• 字号 <数值> —— 设置字号；字号.大 / 字号.小 调整字号。",
            "• 行距 <数值> —— 设置行距；行距.大 / 行距.小 调整间距。",
            "• 曲线 [开|关|切换] —— 开关曲线文本效果。",
            "• 位置.<上|下|左|右> [步长] —— 调整文本位置。",
            "• 人物 <名称> —— 切换立绘；人物 -r 随机选择。",
            "",
            "温馨提示：AstrBot 当前不支持会话式 prompt，请直接在指令后提供参数。",
            "",
            self.QUICK_ACTION_LINE,
        ]
        return self.event.plain_result("\n".join(lines))

    def error(self, message: str) -> MessageEventResult:
        lines = [
            f"⚠️ {message}",
            "",
            "发送 /pjsk.draw 创建或刷新卡面，或使用 /pjsk.调整 获取指令帮助。",
            "",
            self.QUICK_ACTION_LINE,
        ]
        return self.event.plain_result("\n".join(lines))

    @staticmethod
    def _state_lines(state: RenderState) -> List[str]:
        curve_state = "开启" if state.curve_enabled else "关闭"
        return [
            f"文本：{state.text}",
            f"字号：{state.font_size}px",
            f"行距：{state.line_spacing:.2f}",
            f"曲线：{curve_state}",
            f"位置：X {state.offset_x} / Y {state.offset_y}",
            f"人物：{state.role}",
        ]


@register("pjsk_emoji_maker", "PJSk Community", "Project SEKAI 表情包制作工具", "2.0.0")
class PjskEmojiMaker(Star):
    """AstrBot plugin providing PJSk emoji maker and card rendering commands."""

    DEFAULT_TEXT = "这是一个新的卡面"
    DEFAULT_FONT_SIZE = 42
    DEFAULT_LINE_SPACING = 1.20
    DEFAULT_ROLE = "初音未来"

    FONT_SIZE_MIN = 18
    FONT_SIZE_MAX = 84
    FONT_SIZE_STEP = 4

    LINE_SPACING_MIN = 0.60
    LINE_SPACING_MAX = 3.00
    LINE_SPACING_STEP = 0.10

    OFFSET_MIN = -240
    OFFSET_MAX = 240
    OFFSET_STEP = 12

    MAX_TEXT_LENGTH = 120

    COMMAND_ALIASES: Dict[str, Iterable[str]] = {
        "text": {"文本", "文字", "内容", "text", "message"},
        "font_size": {"字号", "字体", "字", "font", "fontsize", "font-size"},
        "line_spacing": {"行距", "间距", "行间距", "spacing", "lines"},
        "curve": {"曲线", "弧线", "曲线模式", "curve"},
        "position": {"位置", "坐标", "offset", "pos"},
        "role": {"人物", "角色", "立绘", "role", "avatar"},
    }

    SIZE_VARIANTS: Dict[str, Iterable[str]] = {
        "increase": {"大", "增", "加", "+", "increase", "up", "plus"},
        "decrease": {"小", "减", "降", "-", "decrease", "down", "minus"},
    }

    CURVE_VARIANTS: Dict[str, Iterable[str]] = {
        "on": {"开", "开启", "on", "true", "enable"},
        "off": {"关", "关闭", "off", "false", "disable"},
        "toggle": {"切换", "toggle", "switch"},
    }

    DIRECTION_ALIASES: Dict[str, Iterable[str]] = {
        "up": {"上", "up", "u", "↑"},
        "down": {"下", "down", "d", "↓"},
        "left": {"左", "left", "l", "←"},
        "right": {"右", "right", "r", "→"},
    }

    ROLE_ALIASES: Dict[str, Iterable[str]] = {
        "初音未来": {"初音未来", "初音", "miku", "hatsune", "hatsune miku"},
        "星乃一歌": {"星乃一歌", "一歌", "ichika"},
        "天马咲希": {"天马咲希", "咲希", "saki"},
        "望月穗波": {"望月穗波", "穗波", "honami"},
        "日野森志步": {"日野森志步", "志步", "shiho"},
        "东云彰人": {"东云彰人", "彰人", "akito"},
        "青柳冬弥": {"青柳冬弥", "冬弥", "toya"},
        "小豆泽心羽": {"小豆泽心羽", "心羽", "kohane"},
    }

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = ConfigWrapper(config)
        self._state_manager = StateManager()
        self._persistence = StatePersistence()
        self._renderer = None  # Will be initialized in initialize()
        self._random = random.Random()
        self._command_lookup = self._build_alias_lookup(self.COMMAND_ALIASES)
        self._direction_lookup = self._build_alias_lookup(self.DIRECTION_ALIASES)
        self._role_lookup = self._build_alias_lookup(self.ROLE_ALIASES)
        self._role_names = list(self.ROLE_ALIASES.keys())
        self._pending_headline: Optional[str] = None

    async def initialize(self):
        """插件初始化逻辑。"""
        # Initialize the renderer
        self._renderer = await renderer_manager.get_renderer()

    async def terminate(self):
        """插件卸载时的清理逻辑。"""
        # Close the renderer
        await renderer_manager.close()

    def _state_key(self, event: AstrMessageEvent) -> Tuple[str, str]:
        platform = getattr(event, "platform", "unknown") or "unknown"
        # Ensure platform is a string (not an object like PlatformMetadata)
        if not isinstance(platform, str):
            platform = str(platform) or "unknown"
        
        if hasattr(event, "session_id") and getattr(event, "session_id"):
            return platform, str(getattr(event, "session_id"))

        sender_id = None
        if hasattr(event, "get_sender_id") and callable(getattr(event, "get_sender_id")):
            try:
                sender_id = getattr(event, "get_sender_id")()
            except Exception:  # pragma: no cover - defensive fallback
                sender_id = None
        if sender_id:
            return platform, str(sender_id)

        sender_name = "unknown"
        if hasattr(event, "get_sender_name") and callable(getattr(event, "get_sender_name")):
            try:
                sender_name = getattr(event, "get_sender_name")() or "unknown"
            except Exception:  # pragma: no cover - defensive fallback
                sender_name = "unknown"
        return platform, str(sender_name)

    def _require_state(self, event: AstrMessageEvent) -> Tuple[Tuple[str, str], RenderState]:
        key = self._state_key(event)
        state = self._state_manager.get(key)
        
        # Try to load from persistence if not in memory
        if state is None:
            state = self._persistence.get_state(key[0], key[1], self.config.state_ttl_hours)
            if state:
                self._state_manager.set(key, state)
        
        if state is None:
            raise MissingStateError("未找到历史渲染，请先执行 /pjsk.draw 或 /pjsk.绘制。")
        return key, state

    def _extract_first_token(self, message: str) -> Tuple[str, str]:
        sanitized = message.strip()
        if not sanitized:
            return "", ""
        parts = sanitized.split(maxsplit=1)
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]

    def _split_token(self, token: str) -> Tuple[str, List[str]]:
        pieces = [segment for segment in token.split(".") if segment]
        if not pieces:
            return "", []
        return pieces[0], pieces[1:]

    def _normalize_lookup(self, lookup: Dict[str, str], token: str) -> Optional[str]:
        if not token:
            return None
        stripped = token.strip()
        lowered = stripped.lower()
        if stripped in lookup:
            return lookup[stripped]
        if lowered in lookup:
            return lookup[lowered]
        return None

    def _build_alias_lookup(self, aliases: Dict[str, Iterable[str]]) -> Dict[str, str]:
        lookup: Dict[str, str] = {}
        for canonical, names in aliases.items():
            for name in names:
                lookup[name] = canonical
                lookup[name.lower()] = canonical
        return lookup

    def _normalize_variant(self, token: Optional[str], mapping: Dict[str, Iterable[str]]) -> Optional[str]:
        if not token:
            return None
        stripped = token.strip()
        lowered = stripped.lower()
        for canonical, names in mapping.items():
            if stripped in names or lowered in names:
                return canonical
        return None

    def _split_args(self, text: str) -> List[str]:
        if not text:
            return []
        return [part for part in text.split() if part]

    def _parse_int(self, raw: str) -> int:
        sanitized = raw.strip().lower().replace("px", "")
        sanitized = sanitized.replace("＋", "+").replace("－", "-")
        try:
            return int(float(sanitized))
        except ValueError as exc:  # pragma: no cover - defensive fallback
            raise ValidationError(f"无法解析数值：{raw}") from exc

    def _parse_positive_int(self, raw: str) -> int:
        value = self._parse_int(raw)
        if value <= 0:
            raise ValidationError("位移步长需为正整数。")
        return value

    def _parse_float(self, raw: str) -> float:
        sanitized = raw.strip().lower().replace("倍", "").replace("x", "").replace(",", ".")
        try:
            return float(sanitized)
        except ValueError as exc:  # pragma: no cover - defensive fallback
            raise ValidationError(f"无法解析数值：{raw}") from exc

    def _clamp(self, value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    def _resolve_role(self, raw: str) -> Optional[str]:
        return self._normalize_lookup(self._role_lookup, raw)

    def _pick_random_role(self, exclude: str) -> str:
        candidates = [role for role in self._role_names if role != exclude]
        if not candidates:
            candidates = list(self._role_names)
        return self._random.choice(candidates)

    def _save_state(self, key: Tuple[str, str], state: RenderState) -> None:
        """Save state to both memory and persistence."""
        self._state_manager.set(key, state)
        if self.config.persistence_enabled:
            self._persistence.set_state(key[0], key[1], state)

    def _create_state_from_options(self, options: dict) -> RenderState:
        """Create RenderState from parsed options."""
        text = options.get('text') or self.DEFAULT_TEXT
        if self.config.adaptive_text_sizing and not options.get('font_size'):
            font_size = calculateFontSize(text, min_size=self.config.font_size_min, max_size=self.config.font_size_max)
        else:
            font_size = options.get('font_size') or self.DEFAULT_FONT_SIZE
        
        line_spacing = options.get('line_spacing') or self.DEFAULT_LINE_SPACING
        curve_enabled = options.get('curve') or False
        
        # Calculate offsets if not provided
        if options.get('offset_x') is not None or options.get('offset_y') is not None:
            offset_x = options.get('offset_x', 0)
            offset_y = options.get('offset_y', 0)
        else:
            offset_x, offset_y = calculateOffsets(text, font_size, line_spacing)
        
        # Resolve role
        role = options.get('role')
        if role == '-r':
            role = self._pick_random_role(self.DEFAULT_ROLE)
        elif role:
            resolved = self._resolve_role(role)
            role = resolved or self.DEFAULT_ROLE
        else:
            role = self.DEFAULT_ROLE
        
        # Clamp values to config ranges
        font_size = int(self._clamp(font_size, self.config.font_size_min, self.config.font_size_max))
        line_spacing = round(self._clamp(line_spacing, self.config.line_spacing_min, self.config.line_spacing_max), 2)
        offset_x = int(self._clamp(offset_x, self.config.offset_min, self.config.offset_max))
        offset_y = int(self._clamp(offset_y, self.config.offset_min, self.config.offset_max))
        
        # Sanitize text
        text = sanitizeText(text, self.config.max_text_length)
        
        return RenderState(
            text=text,
            font_size=font_size,
            line_spacing=line_spacing,
            curve_enabled=curve_enabled,
            offset_x=offset_x,
            offset_y=offset_y,
            role=role,
        )

    async def _render_and_respond(
        self, 
        event: AstrMessageEvent, 
        state: RenderState, 
        headline: str
    ) -> MessageEventResult:
        """Render the card and send response."""
        try:
            # Generate the image
            curve_intensity = validateCurveIntensity(self.config.default_curve_intensity)
            image_bytes = await self._renderer.render_emoji_card(
                text=state.text,
                character_name=state.role,
                font_size=state.font_size,
                line_spacing=state.line_spacing,
                curve_enabled=state.curve_enabled,
                offset_x=state.offset_x,
                offset_y=state.offset_y,
                curve_intensity=curve_intensity,
                enable_shadow=self.config.enable_text_shadow,
                emoji_set=self.config.default_emoji_set,
            )
            
            # Create response
            helper = MessagingHelper(event)
            
            # Build message components
            messages = []
            
            # Add mention if enabled
            if self.config.mention_user_on_render:
                try:
                    sender_name = event.get_sender_name()
                    messages.append(f"@{sender_name} ")
                except Exception:
                    pass
            
            # Add success message if enabled
            if self.config.show_success_messages:
                messages.append(f"✨ {headline}")
                messages.append("")
                messages.extend(helper._state_lines(state))
            
            # Convert image bytes to base64 for sending
            import base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Return image result with optional text
            if messages:
                text_result = "\n".join(messages)
                # In a real implementation, this would send both text and image
                # For now, we'll return the text result
                return event.plain_result(text_result + f"\n\n[Image: {len(image_bytes)} bytes]")
            else:
                return event.plain_result(f"[Image: {len(image_bytes)} bytes]")
                
        except Exception as e:
            logger.error("PJSk rendering failed: %s", str(e))
            helper = MessagingHelper(event)
            return helper.error(f"渲染失败：{str(e)}")

    async def _render_via_draw(self, event: AstrMessageEvent, headline: str) -> MessageEventResult:
        original_message = getattr(event, "message_str", "")
        try:
            self._pending_headline = headline
            setattr(event, "message_str", "")
            draw_generator = self.draw(event)
            return await draw_generator.__anext__()
        finally:
            self._pending_headline = None
            setattr(event, "message_str", original_message)

    def _execute_text(self, state: RenderState, text: str) -> str:
        sanitized = text.strip()
        if not sanitized:
            raise ValidationError("请提供要更新的文本内容。")
        if len(sanitized) > self.MAX_TEXT_LENGTH:
            raise ValidationError(f"文本长度不可超过 {self.MAX_TEXT_LENGTH} 个字符。")
        state.text = sanitized
        logger.debug("PJSk 文本已更新：%s", sanitized)
        return "📝 文本已更新"

    def _execute_font_size(self, state: RenderState, variant: Optional[str], args: List[str]) -> str:
        if variant:
            action = self._normalize_variant(variant, self.SIZE_VARIANTS)
            if action is None:
                raise ValidationError("未识别的字号调整方式。")
            previous = state.font_size
            if action == "increase":
                state.font_size = int(self._clamp(previous + self.FONT_SIZE_STEP, self.FONT_SIZE_MIN, self.FONT_SIZE_MAX))
                if state.font_size == previous:
                    return f"🔠 字号已达到上限（{state.font_size}px）"
                return f"🔠 字号已增至 {state.font_size}px"
            state.font_size = int(self._clamp(previous - self.FONT_SIZE_STEP, self.FONT_SIZE_MIN, self.FONT_SIZE_MAX))
            if state.font_size == previous:
                return f"🔠 字号已达到下限（{state.font_size}px）"
            return f"🔠 字号已降至 {state.font_size}px"

        if not args:
            raise ValidationError("请提供字号数值，例如：字号 48。")
        value = self._parse_int(args[0])
        clamped = int(self._clamp(value, self.FONT_SIZE_MIN, self.FONT_SIZE_MAX))
        state.font_size = clamped
        if clamped != value:
            return f"🔠 字号已设置为 {clamped}px（范围 {self.FONT_SIZE_MIN}-{self.FONT_SIZE_MAX}）"
        return f"🔠 字号已设置为 {clamped}px"

    def _execute_line_spacing(self, state: RenderState, variant: Optional[str], args: List[str]) -> str:
        if variant:
            action = self._normalize_variant(variant, self.SIZE_VARIANTS)
            if action is None:
                raise ValidationError("未识别的行距调整方式。")
            previous = state.line_spacing
            if action == "increase":
                state.line_spacing = round(
                    self._clamp(previous + self.LINE_SPACING_STEP, self.LINE_SPACING_MIN, self.LINE_SPACING_MAX),
                    2,
                )
                if state.line_spacing == previous:
                    return f"📏 行距已达到上限（{state.line_spacing:.2f}）"
                return f"📏 行距已增至 {state.line_spacing:.2f}"
            state.line_spacing = round(
                self._clamp(previous - self.LINE_SPACING_STEP, self.LINE_SPACING_MIN, self.LINE_SPACING_MAX),
                2,
            )
            if state.line_spacing == previous:
                return f"📏 行距已达到下限（{state.line_spacing:.2f}）"
            return f"📏 行距已降至 {state.line_spacing:.2f}"

        if not args:
            raise ValidationError("请提供行距数值，例如：行距 1.8。")
        value = self._parse_float(args[0])
        clamped = round(self._clamp(value, self.LINE_SPACING_MIN, self.LINE_SPACING_MAX), 2)
        state.line_spacing = clamped
        if abs(clamped - value) > 1e-6:
            return f"📏 行距已设置为 {clamped:.2f}（范围 {self.LINE_SPACING_MIN}-{self.LINE_SPACING_MAX}）"
        return f"📏 行距已设置为 {clamped:.2f}"

    def _execute_curve(self, state: RenderState, variant: Optional[str], args: List[str]) -> str:
        action = self._normalize_variant(variant, self.CURVE_VARIANTS)
        if action is None and args:
            action = self._normalize_variant(args[0], self.CURVE_VARIANTS)
        if action is None:
            action = "toggle"

        if action == "on":
            state.curve_enabled = True
            return "〰️ 曲线已开启"
        if action == "off":
            state.curve_enabled = False
            return "〰️ 曲线已关闭"
        state.curve_enabled = not state.curve_enabled
        status = "开启" if state.curve_enabled else "关闭"
        return f"〰️ 曲线已{status}"

    def _execute_position(self, state: RenderState, variants: List[str], args: List[str]) -> str:
        direction: Optional[str] = None
        remaining = list(args)

        if variants:
            direction = self._normalize_lookup(self._direction_lookup, variants[0])
        if direction is None and remaining:
            direction = self._normalize_lookup(self._direction_lookup, remaining[0])
            if direction is not None:
                remaining = remaining[1:]
        if direction is None:
            raise ValidationError("请指定方向，例如：位置.上 或 位置 下。")

        amount = self.OFFSET_STEP
        if remaining:
            amount = self._parse_positive_int(remaining[0])

        if direction == "up":
            previous = state.offset_y
            state.offset_y = int(self._clamp(previous - amount, self.OFFSET_MIN, self.OFFSET_MAX))
            applied = previous - state.offset_y
            if applied == 0:
                return f"📍 已到达上边界（Y={state.offset_y}）"
            return f"📍 向上移动 {applied}，当前 Y={state.offset_y}"
        if direction == "down":
            previous = state.offset_y
            state.offset_y = int(self._clamp(previous + amount, self.OFFSET_MIN, self.OFFSET_MAX))
            applied = state.offset_y - previous
            if applied == 0:
                return f"📍 已到达下边界（Y={state.offset_y}）"
            return f"📍 向下移动 {applied}，当前 Y={state.offset_y}"
        if direction == "left":
            previous = state.offset_x
            state.offset_x = int(self._clamp(previous - amount, self.OFFSET_MIN, self.OFFSET_MAX))
            applied = previous - state.offset_x
            if applied == 0:
                return f"📍 已到达左边界（X={state.offset_x}）"
            return f"📍 向左移动 {applied}，当前 X={state.offset_x}"

        previous = state.offset_x
        state.offset_x = int(self._clamp(previous + amount, self.OFFSET_MIN, self.OFFSET_MAX))
        applied = state.offset_x - previous
        if applied == 0:
            return f"📍 已到达右边界（X={state.offset_x}）"
        return f"📍 向右移动 {applied}，当前 X={state.offset_x}"

    def _execute_role(self, state: RenderState, remainder: str, args: List[str]) -> str:
        if args and args[0].lower() == "-r":
            new_role = self._pick_random_role(state.role)
            state.role = new_role
            return f"🧑‍🎤 角色已随机切换为 {new_role}"

        candidate = remainder.strip()
        if not candidate:
            raise ValidationError("请提供角色名称，或使用 -r 随机切换。")
        resolved = self._resolve_role(candidate)
        if not resolved:
            raise ValidationError(f"未识别的角色：{candidate}")
        state.role = resolved
        return f"🧑‍🎤 角色已切换为 {resolved}"

    def _process_adjustment(
        self,
        state: RenderState,
        command_token: str,
        variants: List[str],
        remainder: str,
    ) -> str:
        command_key = self._normalize_lookup(self._command_lookup, command_token)
        if not command_key:
            raise ValidationError(f"未识别的子指令：{command_token}")

        if command_key == "text":
            return self._execute_text(state, remainder)

        args = self._split_args(remainder)
        if command_key == "font_size":
            variant = variants[0] if variants else None
            return self._execute_font_size(state, variant, args)
        if command_key == "line_spacing":
            variant = variants[0] if variants else None
            return self._execute_line_spacing(state, variant, args)
        if command_key == "curve":
            variant = variants[0] if variants else None
            return self._execute_curve(state, variant, args)
        if command_key == "position":
            return self._execute_position(state, variants, args)
        if command_key == "role":
            return self._execute_role(state, remainder, args)

        raise ValidationError(f"未支持的子指令：{command_token}")

    @filter.command("pjsk.draw")
    async def draw(self, event: AstrMessageEvent):
        """PJSk 渲染指令：初始化或刷新当前配置。"""

        helper = MessagingHelper(event)
        key = self._state_key(event)
        state = self._state_manager.get(key)
        message = getattr(event, "message_str", "").strip()
        created = False

        if state is None:
            state = RenderState(
                text=message or self.DEFAULT_TEXT,
                font_size=self.DEFAULT_FONT_SIZE,
                line_spacing=round(self.DEFAULT_LINE_SPACING, 2),
                curve_enabled=False,
                offset_x=0,
                offset_y=0,
                role=self.DEFAULT_ROLE,
            )
            self._save_state(key, state)
            created = True
        elif message:
            state.text = message

        headline = self._pending_headline or ("🎨 已完成初始渲染" if created else "🎨 已重新渲染")
        logger.debug("PJSk 渲染：%s", headline)
        yield helper.summary(state, headline)

    @filter.command("pjsk.调整")
    async def adjust(self, event: AstrMessageEvent):
        """PJSk 调整指令：修改当前配置并重新渲染。"""

        helper = MessagingHelper(event)
        raw_message = getattr(event, "message_str", "").strip()
        if not raw_message:
            yield helper.guidance()
            return

        try:
            _, state = self._require_state(event)
            first_token, remainder = self._extract_first_token(raw_message)
            command_token, variants = self._split_token(first_token)
            headline = self._process_adjustment(state, command_token, variants, remainder)
        except AdjustError as exc:
            yield helper.error(str(exc))
            return

        result = await self._render_and_respond(event, state, headline)
        yield result

    @filter.command("pjsk.绘制")
    async def draw_koishi(self, event: AstrMessageEvent):
         """PJSk 绘制指令：支持 Koishi 风格选项的渲染命令。"""

         helper = MessagingHelper(event)
         raw_message = getattr(event, "message_str", "").strip()

         try:
             # Parse Koishi-style flags
             options = parseKoishiFlags(raw_message)

             # Apply defaults
             defaults = {
                 'text': None,
                 'offset_x': None,
                 'offset_y': None,
                 'role': None,
                 'font_size': None,
                 'line_spacing': None,
                 'curve': None,
                 'default_font': False
             }
             options = applyDefaults(options, defaults)

             # Create state from options
             state = self._create_state_from_options(options)

             # Save state
             key = self._state_key(event)
             self._save_state(key, state)

             # Determine headline
             if options['text']:
                 headline = "🎨 已完成自定义渲染"
             elif options['default_font']:
                 headline = "🎨 已使用默认字体渲染"
             else:
                 headline = "🎨 已完成渲染"

             logger.debug("PJSk Koishi 渲染：%s", headline)

             # Render and respond
             result = await self._render_and_respond(event, state, headline)
             yield result

         except Exception as exc:
             logger.error("PJSk Koishi 渲染失败: %s", str(exc))
             yield helper.error(f"渲染失败：{str(exc)}")

    @filter.command("pjsk")
    async def list_root(self, event: AstrMessageEvent):
        """PJSk 根命令：显示帮助和快捷选项。"""
        lines = [
            "🎨 Project SEKAI 表情包制作工具",
            "",
            "快速开始：",
            "• /pjsk.draw 或 /pjsk.绘制 ─ 创建或刷新表情包",
            "• /pjsk.列表 ─ 查看所有角色",
            "",
            "调整选项：",
            "• /pjsk.调整 ─ 查看所有调整指令",
            "",
            "更多帮助：发送相应指令即可获取详细说明。",
        ]
        yield event.plain_result("\n".join(lines))

    @filter.command("pjsk.列表")
    async def list_guide(self, event: AstrMessageEvent):
        """PJSk 列表指令：主列表流程。"""
        raw_message = getattr(event, "message_str", "").strip()
        
        if not raw_message:
            lines = [
                "📋 角色列表查看",
                "",
                "选择查看方式：",
                "• /pjsk.列表.全部 ─ 查看所有角色",
                "• /pjsk.列表.角色分类 ─ 按组合分类查看",
                "• /pjsk.列表.展开指定角色 <角色名> ─ 查看特定角色详情",
                "",
                "例如：/pjsk.列表.展开指定角色 初音未来",
            ]
            yield event.plain_result("\n".join(lines))
            return
        
        first_token, remainder = self._extract_first_token(raw_message)
        
        if first_token.lower() in {"全部", "all"}:
            yield event.plain_result(format_character_list())
        elif first_token.lower() in {"角色分类", "group"}:
            yield event.plain_result(format_character_groups())
        else:
            yield event.plain_result(
                "未识别的列表选项。发送 /pjsk.列表 查看可用选项。"
            )

    @filter.command("pjsk.列表.全部")
    async def list_all(self, event: AstrMessageEvent):
        """PJSk 列表：显示所有角色。"""
        yield event.plain_result(format_character_list())

    @filter.command("pjsk.列表.角色分类")
    async def list_by_group(self, event: AstrMessageEvent):
        """PJSk 列表：按分类显示角色。"""
        yield event.plain_result(format_character_groups())

    @filter.command("pjsk.列表.展开指定角色")
    async def list_expand_character(self, event: AstrMessageEvent):
        """PJSk 列表：显示特定角色的详情。"""
        raw_message = getattr(event, "message_str", "").strip()
        
        if not raw_message:
            yield event.plain_result(
                "请提供角色名称，例如：/pjsk.列表.展开指定角色 初音未来"
            )
            return
        
        character_name = get_character_name(raw_message)
        if not character_name:
            lines = [
                f"❌ 未找到角色：{raw_message}",
                "",
                "发送 /pjsk.列表 查看可用角色。",
            ]
            yield event.plain_result("\n".join(lines))
            return
        
        yield event.plain_result(format_character_detail(character_name))

    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令"""
        user_name = event.get_sender_name()
        message_str = event.message_str
        message_chain = event.get_messages()
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")
