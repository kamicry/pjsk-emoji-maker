# Koishi to AstrBot Migration Plan: PJSk Plugin

**Document Status**: Migration Analysis & Design Brief  
**Date**: November 2024  
**Branch**: `docs/migration/koishi-pjsk-to-astrbot-migration-plan`

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Command Tree Mapping](#command-tree-mapping)
3. [Configuration System](#configuration-system)
4. [Asset Requirements](#asset-requirements)
5. [Message Flow Differences](#message-flow-differences)
6. [Persistence Strategy](#persistence-strategy)
7. [Dependency Mapping](#dependency-mapping)
8. [Implementation Status](#implementation-status)
9. [Open Questions & Blockers](#open-questions--blockers)
10. [Design Decisions](#design-decisions)

---

## Executive Summary

The PJSk emoji maker plugin is being migrated from **Koishi.js** (Node.js-based plugin framework) to **AstrBot** (Python-based plugin framework). Both frameworks provide real-time chatbot plugin systems, but with fundamentally different architectures and APIs.

### Key Differences at a Glance

| Aspect | Koishi | AstrBot |
|--------|--------|---------|
| **Language** | TypeScript/JavaScript | Python 3.8+ |
| **Plugin Model** | Command handlers with session/context | Async generator-based message handlers |
| **State Management** | Koishi `ctx.database` ORM | File-based JSON or custom persistence |
| **Message Output** | `session.send()` with inline markdown/buttons | `event.plain_result()` or custom adapters |
| **Prompting** | `session.prompt()` waits for user input | No native prompt API; sequential commands required |
| **Image Handling** | Browser automation (Puppeteer) | Browser automation (Playwright/Pyppeteer) |
| **Event System** | Session-based with middleware | Event-based with decorator routing |

### Migration Scope

- **Source Plugin**: Koishi plugin (`koishi-plugin-pjsk-pptr`) with TypeScript sources
- **Target Plugin**: AstrBot plugin (`pjsk_emoji_maker`) with Python implementation
- **Features Retained**: All command functionality, character database, image rendering
- **Features Added**: Enhanced configuration, test suite, messaging adapter system
- **Status**: Core functionality migrated; documentation & open questions documented below

---

## Command Tree Mapping

### Full Command Hierarchy

```
pjsk (root help)
├── pjsk.draw                    [Initialize/refresh card state]
├── pjsk.绘制                     [Advanced render with flags]
├── pjsk.调整                     [Adjustment root]
│   ├── pjsk.调整 文本            [Text content]
│   ├── pjsk.调整 字号            [Font size]
│   │   ├── 字号.大             [Increase by step]
│   │   └── 字号.小             [Decrease by step]
│   ├── pjsk.调整 行距            [Line spacing]
│   │   ├── 行距.大             [Increase by step]
│   │   └── 行距.小             [Decrease by step]
│   ├── pjsk.调整 曲线            [Curve effect toggle]
│   ├── pjsk.调整 位置            [Position adjustment]
│   │   ├── 位置.上             [Move up]
│   │   ├── 位置.下             [Move down]
│   │   ├── 位置.左             [Move left]
│   │   └── 位置.右             [Move right]
│   └── pjsk.调整 人物            [Character/role change]
├── pjsk.列表                     [List commands root]
│   ├── pjsk.列表.全部           [List all characters]
│   ├── pjsk.列表.角色分类        [List by group]
│   └── pjsk.列表.展开指定角色    [Character detail]
└── pjsk.绘制 (advanced alias)   [Same as pjsk.绘制]
```

### Command Details

#### 1. Root Help Command (/pjsk)

**Arguments**: None  
**Side Effects**: None (read-only display)  
**Response Format**: Plain text with command list and usage examples  
**Status**: ✅ Implemented

#### 2. Initialize/Refresh Card (/pjsk.draw)

**Arguments**: Optional text content  
**Side Effects**: Creates RenderState, stores in memory and persistence, generates image  
**Response Format**: State summary with emoji card preview  
**Status**: ✅ Implemented

#### 3. Advanced Render (/pjsk.绘制)

**Flags**: `-n "text"`, `-s size`, `-l spacing`, `-x offset`, `-y offset`, `-r name|random`, `-c`, `--daf`  
**Side Effects**: Same as draw but with flag parsing  
**Response Format**: Same as draw  
**Status**: ✅ Implemented

#### 4. Adjustment Commands (/pjsk.调整)

| Subcommand | Arguments | Range | Step | Status |
|------------|-----------|-------|------|--------|
| 文本 | text content | ≤120 chars | N/A | ✅ |
| 字号 | size \| .大/.小 | 18-84px | 4px | ✅ |
| 行距 | spacing \| .大/.小 | 0.6-3.0 | 0.1 | ✅ |
| 曲线 | on\|off\|toggle | boolean | N/A | ✅ |
| 位置 | direction [steps] | -240 to 240px | 12px | ✅ |
| 人物 | name\|alias\|-r | 8 characters | N/A | ✅ |

#### 5. List Commands (/pjsk.列表)

**Subcommands**:
- `.全部` - List all 8 characters
- `.角色分类` - List characters by group
- `.展开指定角色 <name>` - Character detail view

**Status**: ✅ Implemented (NEW)

---

## Configuration System

### Configuration File Structure

**File**: `config/pjsk_config.yaml` (auto-created on first run)

```yaml
# Text processing options
adaptive_text_sizing: true
enable_markdown_flow: false

# Messaging options  
show_success_messages: true
mention_user_on_render: false
should_wait_for_user_input_before_sending_commands: false
should_mention_user_in_message: false
retract_delay_ms: null

# Rendering options
default_curve_intensity: 0.5
enable_text_shadow: true
default_emoji_set: "apple"

# Persistence options
persistence_enabled: true
state_ttl_hours: 24

# Validation ranges
font_size_min: 18
font_size_max: 84
font_size_step: 4

line_spacing_min: 0.6
line_spacing_max: 3.0
line_spacing_step: 0.1

offset_min: -240
offset_max: 240
offset_step: 12

max_text_length: 120
```

### Koishi to AstrBot Configuration Mapping

| Koishi Config | AstrBot Config | Purpose |
|---------------|----------------|---------|
| adaptiveTextSizing | adaptive_text_sizing | Auto-adjust font size to fit text |
| enableMarkdownFlow | enable_markdown_flow | Enable markdown text processing |
| showSuccessMessages | show_success_messages | Include success messages in responses |
| mentionUserOnRender | mention_user_on_render | Mention user when rendering |
| retractDelayMs | retract_delay_ms | Message deletion delay (not yet supported) |
| defaultCurveIntensity | default_curve_intensity | Curve effect strength (0.0-1.0) |
| enableTextShadow | enable_text_shadow | Add shadow to rendered text |
| defaultEmojiSet | default_emoji_set | Emoji rendering style |
| persistenceEnabled | persistence_enabled | Store state across sessions |
| stateTtlHours | state_ttl_hours | State expiration time (hours) |

---

## Asset Requirements

### Character Database

8 characters total with Chinese names and multi-language aliases:

```python
CHARACTERS: Dict[str, Iterable[str]] = {
    "初音未来": {"初音未来", "初音", "miku", "hatsune", "hatsune miku"},
    "星乃一歌": {"星乃一歌", "一歌", "ichika"},
    "天马咲希": {"天马咲希", "咲希", "saki"},
    "望月穗波": {"望月穗波", "穗波", "honami"},
    "日野森志步": {"日野森志步", "志步", "shiho"},
    "东云彰人": {"东云彰人", "彰人", "akito"},
    "青柳冬弥": {"青柳冬弥", "冬弥", "toya"},
    "小豆泽心羽": {"小豆泽心羽", "心羽", "kohane"},
}

CHARACTER_GROUPS: Dict[str, List[str]] = {
    "Leo/need": ["星乃一歌", "天马咲希", "望月穗波", "日野森志步"],
    "MORE MORE JUMP!": ["初音未来"],
    "Vivid BAD SQUAD": ["东云彰人", "青柳冬弥"],
    "Nightcord at 25:00": ["小豆泽心羽"],
}
```

### Required Asset Files

```
pjsk_emoji/assets/
├── characters.json           # Character metadata
├── emoji_images/
│   ├── miku.png
│   ├── ichika.png
│   └── ... (8 total)
├── fonts/
│   ├── default.ttf
│   └── fallback.ttf
└── templates/
    ├── card.html
    └── list.html
```

### File Sizes

| Asset Type | Size | Count | Total |
|-----------|------|-------|-------|
| Character images (PNG) | ~150-250 KB each | 8 | ~1.6 MB |
| Fonts (TTF) | ~50-100 KB each | 2 | ~150 KB |
| Templates + CSS | ~10 KB | 2 | ~20 KB |
| Metadata (JSON) | ~5 KB | 1 | ~5 KB |
| **Total** | | | **~1.8 MB** |

### Runtime Dependencies

| Dependency | Version | Purpose | Status |
|-----------|---------|---------|--------|
| astrbot | >=4.5.0 | Plugin framework | ✅ |
| playwright | >=1.40.0 | Browser automation | ✅ |
| pyyaml | >=6.0 | YAML config parsing | ✅ |
| jinja2 | >=3.0 | HTML templating | ✅ |
| pillow | >=9.0 | Image processing | ✅ |

---

## Message Flow Differences

### Koishi Message Flow

```typescript
// User: /pjsk.draw hello
ctx.command('pjsk.draw', '[text]')
  .action(async (session, text) => {
    const state = new RenderState(text || "default")
    
    // Direct session.send() - synchronous operation
    await session.send(`✨ 新卡面已创建\n${formatState(state)}`)
    
    // Optional: Wait for user input
    const userChoice = await session.prompt("要调整什么吗？")
    if (userChoice) {
      // Process follow-up
    }
  })

// Key features:
// - session.send() sends immediately
// - session.prompt() waits for next message
// - Session maintains context across interactions
```

### AstrBot Message Flow

```python
@filter.command('pjsk.draw')
async def draw(self, event: AstrMessageEvent):
    """Initialize or refresh PJSk card."""
    text = event.message_str or self.DEFAULT_TEXT
    
    # Create state
    state = self._build_state(text, config)
    self._state_manager.set(key, state)
    
    # Render image
    image_bytes = await self._renderer.render_emoji_card(...)
    
    # Build response
    messages = [f"✨ 新卡面已创建", formatState(state)]
    
    # Yield result (generator-based)
    yield event.plain_result("\n".join(messages))
    
    # Note: NO prompt() - use sequential commands instead
    # User issues /pjsk.adjust ... as separate invocation

# Key differences:
# - event.plain_result() yields response
# - No native prompt() - use sequential commands
# - Events are stateless; state stored externally
```

### Response Format Mapping

| Koishi | AstrBot | Notes |
|--------|---------|-------|
| session.send(text) | event.plain_result(text) | Plain text response |
| Inline markdown buttons | Custom ButtonMatrix class | NEW in AstrBot |
| session.prompt() | Sequential commands | AstrBot limitation |
| Message components | MessageComponentBuilder | NEW adaptive layer |

---

## Persistence Strategy

### Current Implementation

**File**: `data/pjsk_states.json`

```json
{
  "states": {
    "discord:user123": {
      "state": {
        "text": "Hello World",
        "font_size": 42,
        "line_spacing": 1.2,
        "curve_enabled": false,
        "offset_x": 0,
        "offset_y": 0,
        "role": "初音未来"
      },
      "timestamp": 1700000000.123
    }
  },
  "last_updated": 1700000001.456
}
```

### Storage Strategy

**Key**: `platform:session_id` (e.g., "discord:12345")  
**Value**: RenderState object + timestamp  
**TTL**: Checked on read; expired states removed lazily

### Comparison: Koishi vs AstrBot

| Aspect | Koishi | AstrBot |
|--------|--------|---------|
| Backend | SQL Database (ORM) | JSON File |
| Consistency | ACID transactions | File-level |
| TTL | SQL triggers | Manual checks |
| Scale Limit | Horizontal | ~10k users |
| Deployment | Requires DB service | Self-contained |

### Future Enhancement

**Recommended**: Integrate Redis for horizontal scaling

```python
# TODO: Implement RedisStatePersistence
# with automatic TTL via EXPIRE key
```

---

## Implementation Status

### Completed ✅ (19 features)

| Feature | File | Notes |
|---------|------|-------|
| Core Plugin Structure | main.py | PjskEmojiMaker class |
| State Management | main.py, models.py | StateManager + RenderState |
| Persistence | persistence.py | JSON file-based with TTL |
| Configuration | config.py | PJSkConfig + YAML manager |
| Character Database | pjsk_emoji/domain.py | 8 characters with aliases |
| Font Size Adjustment | main.py | Absolute + relative |
| Line Spacing Adjustment | main.py | Absolute + relative |
| Position Adjustment | main.py | 4-direction with custom step |
| Curve Effect | main.py | SVG transformation |
| Text Content | main.py | Sanitization + validation |
| Character Selection | main.py | Aliases + random option |
| Draw Command | main.py | /pjsk.draw |
| Advanced Render | main.py | /pjsk.绘制 with flags |
| Adjustment Commands | main.py | Full tree |
| List Commands | main.py | /pjsk.列表.* |
| Image Rendering | pjsk_emoji/renderer.py | Playwright-based |
| Messaging Adapter | pjsk_emoji/messaging.py | Button grids + builder |
| Test Suite | tests/ | 91+ tests |
| Documentation | docs/ | User & dev guides |

### Future Features 🟡

| Feature | Blocker | Status |
|---------|---------|--------|
| Redis Persistence | Architecture | Designed |
| Message Retraction | AstrBot API | Config placeholder |
| Inline Image Sending | AstrBot API | Using base64 workaround |
| Session Prompts | AstrBot limitation | Sequential commands instead |

### Known Limitations ❌

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| No session.prompt() | Multi-stage UX requires sequential commands | Designed for sequential flow |
| No image result API | Cannot send images directly | Use base64 in text (temporary) |
| No message deletion | Cannot retract cards | Will fix when API available |
| File persistence | Performance beyond 10k states | Redis integration planned |

---

## Open Questions & Blockers

### Questions ❓

1. **State Storage Location**: File-based JSON vs AstrBot database integration
   - **Current**: File-based (simpler, autonomous)
   - **Alternative**: Use AstrBot's unified DB if available
   - **Decision**: File-based adequate for MVP

2. **Image Delivery**: How to send rendered PNG cards
   - **Current**: Base64-encoded in text response
   - **Alternative**: Wait for `event.image_result()` API
   - **Decision**: Workaround now; upgrade when available

3. **Auto-Render on Adjustment**: Should every adjustment trigger image re-render
   - **Current**: Yes, re-render on every adjustment
   - **Alternative**: Queue adjustments, render on-demand
   - **Decision**: Auto-render for better UX

4. **Multi-Stage UX**: How to implement Koishi's multi-turn prompts
   - **Current**: Sequential slash commands
   - **Alternative**: Ephemeral "prompt state" in StateManager
   - **Decision**: Sequential aligns with AstrBot's design

5. **Dual Language Support**: Support both Chinese and English commands
   - **Current**: Fully implemented
   - **Alternative**: Chinese-only
   - **Decision**: Dual for accessibility

### Blockers 🚫

1. **Image Result API Missing**
   - **Impact**: Cannot send PNG directly; using base64 workaround
   - **Status**: Waiting for AstrBot v4.6+
   - **Workaround**: Text response with image metadata

2. **No Session Prompt API**
   - **Impact**: Cannot implement multi-turn conversations
   - **Status**: Architectural limitation; not planned
   - **Workaround**: Sequential commands model

3. **File Persistence Not Scalable**
   - **Impact**: Performance degrades beyond 10k users
   - **Status**: File locking on concurrent writes
   - **Workaround**: Redis integration (future ticket)

4. **Browser Startup Time**
   - **Impact**: ~3s per render (Playwright init + HTML → PNG)
   - **Status**: Architectural cost
   - **Workaround**: Browser pool for reuse (optimization ticket)

---

## Design Decisions

### Decision 1: File-Based Persistence

**Rationale**: Simple, self-contained, no external service. Adequate for MVP.  
**Trade-off**: Limited horizontal scaling (upgradable to Redis).

### Decision 2: Sequential Commands Instead of Prompts

**Rationale**: Cleanest AstrBot integration; each command self-contained.  
**UX**: `/pjsk.draw` → `/pjsk.adjust 字号.大` → ...

### Decision 3: Generator-Based Response Streaming

**Rationale**: Native to AstrBot's event model; async-friendly.  
**Pattern**: `yield event.plain_result(text)`

### Decision 4: Custom Messaging Adapter

**Rationale**: Encapsulates button logic; future-proof for native component support.  
**Scope**: ButtonMatrix, ButtonMapping, MessageComponentBuilder classes

### Decision 5: Dataclass-Based State

**Rationale**: Type safety, serialization via `asdict()`, IDE autocomplete.  
**Type**: RenderState with 7 fields

### Decision 6: Lazy-Loaded Configuration

**Rationale**: Single file I/O per plugin lifetime; aligned with AstrBot lifecycle.  
**Pattern**: Singleton ConfigManager with lazy initialization

---

## Summary & Next Steps

### What Has Been Migrated ✅

- ✅ Complete command tree (6+ command families)
- ✅ Full feature parity (font, line spacing, position, curve, character)
- ✅ Character database (8 characters with aliases)
- ✅ Configuration system (20+ options via YAML)
- ✅ Persistence layer (file-based with TTL)
- ✅ Browser rendering (Playwright)
- ✅ Test suite (91+ tests)
- ✅ Messaging system (custom adapter)

### What Remains ❓

- 🟡 Image sending API (waiting for AstrBot v4.6+)
- 🟡 Horizontal scalability (Redis integration planned)
- 🟡 Session prompts (designed for sequential commands)
- 🟡 Message retraction (API not yet available)

### Recommended Next Steps 🚀

1. **User Testing**: QA environment feedback
2. **Performance Testing**: Render time & persistence I/O
3. **Error Handling**: Graceful Playwright fallbacks
4. **Documentation**: User guide for sequential workflow
5. **Monitoring**: Logging/metrics for failures
6. **Scalability**: Plan Redis integration

---

## References

### Key Files

- **Plugin Core**: main.py (819 lines)
- **Configuration**: config.py
- **State Management**: models.py, persistence.py
- **Character Database**: pjsk_emoji/domain.py
- **Messaging**: pjsk_emoji/messaging.py
- **Rendering**: pjsk_emoji/renderer.py
- **Tests**: tests/ (91+ tests)

### External Resources

- AstrBot Plugin API: https://astrbot.app/plugin-dev
- Koishi Framework: https://koishi.chat
- Playwright Python: https://playwright.dev/python/

---

**Document Version**: 1.0  
**Last Updated**: November 15, 2024  
**Status**: Ready for Review

