# PJSk Emoji Maker - List Commands Implementation

## Overview

This document describes the implementation of list commands for the PJSk Emoji Maker plugin, including the root help flow and character listing/selection commands.

## Implemented Commands

### 1. Root Help Command (`/pjsk`)
- **Purpose**: Display main menu with quick-action buttons
- **Behavior**: Shows usage options and available subcommands
- **Response Type**: Text menu

### 2. List Guide Command (`/pjsk.列表`)
- **Purpose**: Main entry point for character browsing
- **Behavior**: 
  - No arguments: Display available list views
  - With argument `全部`: Show all characters
  - With argument `角色分类`: Show characters by group
- **Response Type**: Text menu or character list
- **Child Commands**:
  - `/pjsk.列表.全部` - List all characters
  - `/pjsk.列表.角色分类` - List characters by category/group
  - `/pjsk.列表.展开指定角色` - Show details for specific character

### 3. List All Command (`/pjsk.列表.全部`)
- **Purpose**: Display all available characters
- **Format**: Numbered list with character names
- **Response Type**: Text list

### 4. List by Group Command (`/pjsk.列表.角色分类`)
- **Purpose**: Display characters organized by group/project
- **Groups**: 
  - Leo/need
  - MORE MORE JUMP!
  - Vivid BAD SQUAD
  - Nightcord at 25:00
- **Response Type**: Text list with grouping

### 5. Expand Character Command (`/pjsk.列表.展开指定角色`)
- **Purpose**: Show detailed information about a character
- **Input**: Character name or alias
- **Output**: 
  - Character name
  - Known aliases
  - Group/project membership
  - Link to card creation
- **Response Type**: Text detail view
- **Error Handling**: Graceful handling of invalid character names

## Character Resolution System

The plugin uses a flexible character name resolution system in `pjsk_emoji/domain.py`:

### `get_character_name(raw_input: str) -> Optional[str]`
Resolves user input to canonical character names using:
1. Exact string matching (case-sensitive)
2. Lowercase matching (case-insensitive)
3. Alias mapping (e.g., "miku" → "初音未来")

**Supported Aliases:**
- 初音未来: 初音, miku, hatsune, hatsune miku
- 星乃一歌: 一歌, ichika
- 天马咲希: 咲希, saki
- 望月穗波: 穗波, honami
- 日野森志步: 志步, shiho
- 东云彰人: 彰人, akito
- 青柳冬弥: 冬弥, toya
- 小豆泽心羽: 心羽, kohane

### `get_character_image_buffer(...) -> bytes`
Generates image data for a character with rendering parameters using the MockRenderer.

## Follow-up Message Handling (Prompt-Driven Flow)

### Current Status: Awaiting User Direct Input
Due to AstrBot framework limitations, exact parity with traditional prompt-driven flows is not achievable. The current implementation uses a **sequential command approach** where:

1. User views character list: `/pjsk.列表.全部`
2. User views character details: `/pjsk.列表.展开指定角色 初音未来`
3. User creates card: `/pjsk.draw` or `/pjsk.绘制`

### Investigated Approaches

#### 1. **Event Waiters** (Not Available)
- AstrBot's public API does not expose event waiter mechanisms
- No documented way to pause command execution waiting for next message
- Framework focuses on discrete command handling

#### 2. **Context Bus** (Not Available)
- No documented context bus or session state system for cross-command coordination
- Each command is independently executed

#### 3. **Session State Management** (Implemented)
- Plugin maintains state keyed by (platform, session_id/sender_id)
- State persists across multiple commands in same session
- Allows for multi-step workflows without explicit awaiting

### Fallback Implementation

**Sequential Command Flow** (Current)
```
/pjsk                              # Show main menu
/pjsk.列表                          # Show list options
/pjsk.列表.全部                     # View all characters
/pjsk.列表.展开指定角色 初音未来   # View character details
/pjsk.draw                         # Create card for selected role
/pjsk.调整 字号.大                 # Adjust parameters
```

**Advantages:**
- ✓ No framework modifications needed
- ✓ Works reliably on all platforms
- ✓ Stateless from AstrBot's perspective
- ✓ Clear command history

**Trade-offs:**
- Requires explicit input per step (no implicit continuation)
- No automatic character suggestion after list view
- Users must explicitly enter character name when desired

### Recommendation for Future Enhancement

If AstrBot adds event waiting capabilities in future versions:
1. Maintain backward compatibility with current command structure
2. Add optional event-driven flow as supplementary feature
3. Implement with feature detection to handle multiple AstrBot versions

## Testing

Comprehensive test coverage in `tests/test_list_commands.py`:
- Root command help flow (1 test)
- List guide options (3 tests)
- List all characters (1 test)
- List by group (1 test)
- Character expansion with name/alias (3 tests)
- Error handling for invalid characters (1 test)

**All tests passing**: 10/10 ✓

## Integration with Card Creation

After viewing character details, users can create cards using:

```bash
/pjsk.draw                           # Use default role (初音未来)
/pjsk.draw <text>                   # With custom text
/pjsk.调整 人物 初音未来              # Switch role after creation
/pjsk.调整 人物 -r                   # Random character selection
```

## Error Handling

All commands implement graceful error handling:

1. **Missing Character Name**: Display helpful error message
2. **Invalid Character Name**: List available characters
3. **Empty Input**: Show usage instructions
4. **Format Errors**: Suggest correct syntax

## Code Organization

- **`main.py`**: Command handlers and plugin class (PjskEmojiMaker)
- **`pjsk_emoji/domain.py`**: Character data and validation helpers
- **`tests/test_list_commands.py`**: Comprehensive test coverage

## Constants and Configuration

### Character Database (domain.py)
```python
CHARACTERS: Dict[str, Iterable[str]] = {
    "初音未来": {...},
    "星乃一歌": {...},
    # ... 8 characters total
}

CHARACTER_GROUPS: Dict[str, List[str]] = {
    "Leo/need": [...],
    "MORE MORE JUMP!": [...],
    "Vivid BAD SQUAD": [...],
    "Nightcord at 25:00": [...],
}
```

## Usage Examples

### List All Characters
```
User: /pjsk.列表.全部
Bot:  📋 所有角色（共 8 人）：
      1. 初音未来
      2. 星乃一歌
      3. 天马咲希
      ...
```

### View Character Details
```
User: /pjsk.列表.展开指定角色 miku
Bot:  👤 角色信息 - 初音未来
      别名：初音未来, 初音, miku, hatsune, hatsune miku
      所属组合：MORE MORE JUMP!
      
      发送 /pjsk 开始创建表情包吧！
```

### Invalid Character Handling
```
User: /pjsk.列表.展开指定角色 不存在的人物
Bot:  ❌ 未找到角色：不存在的人物
      
      发送 /pjsk.列表 查看可用角色。
```

## Future Enhancements

1. **Quick Actions**: Add button-based character selection (if framework supports)
2. **Character Images**: Display character previews with details
3. **Search Functionality**: Support fuzzy matching for character names
4. **Favorites**: Save user's preferred characters for quick access
5. **Event-Driven Flow**: Implement if AstrBot adds waiter support

## Conclusion

The list commands provide a complete character browsing and selection system that gracefully handles AstrBot framework limitations through sequential command flows while maintaining excellent user experience and comprehensive error handling.
