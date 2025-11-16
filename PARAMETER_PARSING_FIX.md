# Parameter Parsing Fix for /pjsk.选择 Command

## Issue
The `/pjsk.选择` command was not properly receiving parameters from users, causing validation errors for both numeric and character name inputs.

## Root Cause
The issue was with how `event.message_str` was being handled. When `event.message_str` is `None` (rather than an empty string), the code would try to call `.strip()` on `None`, which would either:
1. Cause an `AttributeError` (if not handled)
2. Pass `None` to validation, causing silent failure

The original code:
```python
raw_message = getattr(event, "message_str", "").strip()
```

This fails when `message_str` exists as an attribute but has a `None` value, because `getattr` returns the actual value (`None`) rather than the default (`""`).

## Solution
Changed the parameter retrieval to handle `None` values explicitly:

```python
raw_message = (getattr(event, "message_str", "") or "").strip()
```

This ensures that:
1. If `message_str` doesn't exist, use `""`
2. If `message_str` is `None`, use `""` (via the `or` operator)
3. If `message_str` is an empty string `""`, use `""` 
4. Only if `message_str` has a truthy value will it be used

## Files Modified

### main.py
Updated the following commands to use the robust parameter handling:

1. **`@filter.command("pjsk.选择")`** (line ~1135)
   - Added: `raw_message = (getattr(event, "message_str", "") or "").strip()`
   - Added: Debug logging for received parameters
   - Added: Debug logging for validation failures

2. **`@filter.command("pjsk.输入文字")`** (line ~1186)
   - Added: `raw_message = (getattr(event, "message_str", "") or "").strip()`
   - Added: Debug logging for received parameters

3. **`@filter.command("pjsk.绘制")`** (line ~966)
   - Updated: `raw_message = (getattr(event, "message_str", "") or "").strip()`

4. **`@filter.command("pjsk.列表")`** (line ~1043)
   - Updated: `raw_message = (getattr(event, "message_str", "") or "").strip()`

5. **`@filter.command("pjsk.列表.展开指定角色")`** (line ~1109)
   - Updated: `raw_message = (getattr(event, "message_str", "") or "").strip()`

### Tests Added

Created `tests/test_select_validation.py` with comprehensive tests:
- ✅ Numeric selection validation (1-8)
- ✅ Character name resolution (English: miku, ichika, etc.)
- ✅ Character name resolution (Chinese: 初音未来, 星乃一歌, etc.)
- ✅ Character alias resolution (初音, 一歌, etc.)
- ✅ Case-insensitive matching for English names
- ✅ Invalid input handling
- ✅ Whitespace handling
- ✅ Full validation function integration test

All 9 tests pass successfully.

## Verification

The validation logic was tested and confirmed to work correctly:

### Numeric Input (1-8)
```
'1' -> 初音未来
'2' -> 星乃一歌
'3' -> 天马咲希
'4' -> 望月穗波
'5' -> 日野森志步
'6' -> 东云彰人
'7' -> 青柳冬弥
'8' -> 小豆泽心羽
```

### Character Names
```
'miku' -> 初音未来
'ichika' -> 星乃一歌
'saki' -> 天马咲希
'honami' -> 望月穗波
'shiho' -> 日野森志步
'akito' -> 东云彰人
'toya' -> 青柳冬弥
'kohane' -> 小豆泽心羽
```

### Aliases
```
'初音' -> 初音未来
'hatsune' -> 初音未来
'一歌' -> 星乃一歌
```

## Expected Behavior After Fix

✅ `/pjsk.选择 5` → Selects "日野森志步" (character #5)
✅ `/pjsk.选择 miku` → Selects "初音未来"
✅ `/pjsk.选择 初音未来` → Selects "初音未来"
✅ `/pjsk.选择 ichika` → Selects "星乃一歌"
✅ Invalid inputs show clear error messages

## Debugging Features Added

Added debug logging to help diagnose parameter issues in production:
- Logs the received parameter value
- Logs validation failures with the input that failed

This will help identify if there are any remaining edge cases in different AstrBot environments.

## Backwards Compatibility

The fix is fully backwards compatible:
- Existing working commands continue to work
- The fix only adds defensive handling for edge cases
- No changes to command signatures or behavior
- Only internal parameter processing improved
