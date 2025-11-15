from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.star import Context, Star, register


@dataclass
class RenderState:
    """Runtime configuration for a user's PJSk card rendering."""

    text: str
    font_size: int
    line_spacing: float
    curve_enabled: bool
    offset_x: int
    offset_y: int
    role: str


class StateManager:
    """Simple in-memory state storage keyed by platform/session information."""

    def __init__(self) -> None:
        self._states: Dict[Tuple[str, str], RenderState] = {}

    def get(self, key: Tuple[str, str]) -> Optional[RenderState]:
        return self._states.get(key)

    def set(self, key: Tuple[str, str], state: RenderState) -> None:
        self._states[key] = state

    def exists(self, key: Tuple[str, str]) -> bool:
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


@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    """AstrBot plugin providing PJSk draw and adjustment commands."""

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

    def __init__(self, context: Context):
        super().__init__(context)
        self._state_manager = StateManager()
        self._random = random.Random()
        self._command_lookup = self._build_alias_lookup(self.COMMAND_ALIASES)
        self._direction_lookup = self._build_alias_lookup(self.DIRECTION_ALIASES)
        self._role_lookup = self._build_alias_lookup(self.ROLE_ALIASES)
        self._role_names = list(self.ROLE_ALIASES.keys())
        self._pending_headline: Optional[str] = None

    async def initialize(self):
        """插件初始化逻辑。"""

    async def terminate(self):
        """插件卸载时的清理逻辑。"""

    def _state_key(self, event: AstrMessageEvent) -> Tuple[str, str]:
        platform = getattr(event, "platform", "unknown") or "unknown"
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
        if state is None:
            raise MissingStateError("未找到历史渲染，请先执行 /pjsk.draw。")
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
            self._state_manager.set(key, state)
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

        result = await self._render_via_draw(event, headline)
        yield result

    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令"""
        user_name = event.get_sender_name()
        message_str = event.message_str
        message_chain = event.get_messages()
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")
