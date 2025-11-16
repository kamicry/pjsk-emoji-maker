# Multi-Step Interactive Flow Implementation

## Overview

This implementation adds a complete multi-step interactive flow for the PJSk emoji maker plugin, replicating the original Koishi plugin functionality in AstrBot.

## Features Implemented

### 1. Character Selection Grid
- **Location**: `/pjsk_emoji/assets/list/` directory
- **Content**: Thumbnail images for all 8 characters
- **Format**: 3x3 grid layout with numbered labels (1-8)
- **Fallback**: Text-based list if image generation fails

### 2. Session Management
- **File**: `pjsk_emoji/session.py`
- **Features**:
  - Multi-user session support with platform/user isolation
  - Automatic timeout handling (30s for character selection, 60s for text input)
  - Background cleanup of expired sessions
  - State tracking through the interactive flow

### 3. Interactive Commands

#### `/pjsk.列表.全部`
- Starts the interactive character selection flow
- Sends character selection grid image
- Creates session with 30-second timeout
- Prompts user to select character by number

#### `/pjsk.选择 <number>`
- Handles character selection input
- Validates input (must be 1-8)
- Updates session state to text input phase
- Extends timeout to 60 seconds
- Prompts for text input

#### `/pjsk.输入文字 <text>`
- Handles text input for emoji generation
- Validates text length (max 120 characters)
- Creates RenderState with selected character and text
- Generates and sends the emoji
- Cancels the session

#### `/pjsk.取消`
- Cancels any active session
- Provides user feedback

### 4. Enhanced Help System
- Updated `/pjsk` command with interactive flow instructions
- Updated `/pjsk.列表` with comprehensive usage guide
- Clear step-by-step instructions for users

## Implementation Details

### Session States
```python
class SessionState(Enum):
    WAITING_CHARACTER_SELECTION = "waiting_character_selection"
    WAITING_TEXT_INPUT = "waiting_text_input"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
```

### Flow Sequence
1. **User sends**: `/pjsk.列表.全部`
2. **Bot responds**: Character grid image + selection prompt
3. **User sends**: `1-8` (character number)
4. **Bot responds**: Confirmation + text input prompt
5. **User sends**: Text content
6. **Bot responds**: Generated emoji + session cleanup

### Error Handling
- Invalid character numbers: Prompt for retry
- Session timeouts: Automatic cleanup
- Missing sessions: Clear error messages
- Text length limits: Enforced with user feedback

### Image Generation
- **Primary**: PIL-based grid creation with thumbnails
- **Fallback**: Text-based character list
- **Cleanup**: Automatic temporary file deletion
- **Compatibility**: Works with AstrBot's Comp module

## File Structure

```
pjsk_emoji/
├── assets/
│   ├── list/              # Character thumbnails
│   │   ├── miku.png
│   │   ├── ichika.png
│   │   └── ...
│   └── characters.json    # Updated with list_thumbnail_path
├── session.py            # Session management
├── domain.py            # Grid creation and thumbnail handling
└── main.py              # Updated command handlers

test_interactive_flow.py  # Comprehensive test suite
```

## Configuration Updates

### characters.json
Added `list_thumbnail_path` field for each character:
```json
{
  "初音未来": {
    "id": "miku",
    "name": "初音未来",
    "list_thumbnail_path": "list/miku.png",
    ...
  }
}
```

## Testing

### Test Coverage
- ✅ Thumbnail loading and validation
- ✅ Grid image generation
- ✅ Session lifecycle management
- ✅ Character input validation
- ✅ Complete flow simulation
- ✅ Error handling scenarios

### Running Tests
```bash
cd /home/engine/project
python3 test_interactive_flow.py
```

## Usage Examples

### Basic Interactive Flow
```
User: /pjsk.列表.全部
Bot: [sends character grid]
Bot: 📋 请选择角色（输入数字 1-8）：
     ⏰ 30 秒内有效，输入数字选择角色

User: 3
Bot: ✅ 已选择「天马咲希」，请输入要添加的文字：
     ⏰ 60 秒内有效

User: 生日快乐！
Bot: [sends generated emoji]
Bot: ✨ 已生成「天马咲希」表情包
```

### Error Recovery
```
User: 9
Bot: ❌ 输入无效。请输入 1-8 的数字选择角色。
     💡 提示：发送 /pjsk.列表.全部 重新查看角色列表

User: /pjsk.取消
Bot: ✅ 已取消当前会话。
```

## Compatibility

### AstrBot Integration
- Uses AstrBot's `@filter.command` decorators
- Compatible with `Comp.Image.fromFileSystem()` for image sending
- Supports `chain_result()` for composite messages
- Graceful fallback to `plain_result()` when needed

### Session Management
- Platform-agnostic (works with QQ, Discord, etc.)
- Multi-user support with isolated sessions
- Automatic cleanup to prevent memory leaks
- Async-compatible with AstrBot's event loop

## Performance Considerations

### Memory Management
- Sessions automatically expire and are cleaned up
- Temporary image files are deleted after 5 seconds
- Background cleanup task prevents accumulation

### Error Resilience
- Graceful degradation when PIL is unavailable
- Multiple fallback mechanisms for image sending
- Comprehensive error handling with user-friendly messages

## Future Enhancements

### Potential Improvements
1. **Button-based selection**: Use AstrBot's button components for character selection
2. **Preview mode**: Show text preview before final generation
3. **Batch operations**: Allow multiple emoji generation in one session
4. **Custom timeouts**: User-configurable timeout periods
5. **Session persistence**: Save sessions across bot restarts

### Integration Opportunities
1. **Analytics**: Track popular character choices
2. **Caching**: Cache generated grids for faster responses
3. **Localization**: Support multiple languages for prompts
4. **Themes**: Different grid layouts and color schemes

## Verification

### Acceptance Criteria Met
- ✅ `/pjsk.列表.全部` sends all character thumbnails
- ✅ 30-second timeout for character selection
- ✅ Character selection validation and confirmation
- ✅ 60-second timeout for text input
- ✅ Emoji generation with selected character and text
- ✅ Proper timeout and error handling
- ✅ Complete flow matching original Koishi plugin

### Testing Validation
All test scenarios pass:
- Session lifecycle management
- Character input validation (1-8)
- Text length validation
- Grid image generation
- Complete flow simulation
- Error handling and recovery

The implementation successfully replicates the original Koishi plugin's multi-step interactive flow while adapting to AstrBot's architecture and capabilities.