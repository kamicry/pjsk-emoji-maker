# Testing Guide

This document provides comprehensive testing guidance for the Hello World plugin.

## Automated Testing

### Running Tests

To run the automated test suite:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=main --cov-report=html

# Run specific test file
pytest tests/test_plugin.py

# Run specific test class
pytest tests/test_plugin.py::TestMyPlugin

# Run specific test method
pytest tests/test_plugin.py::TestMyPlugin::test_plugin_initialization
```

### Test Coverage

The test suite covers:

- **Plugin Lifecycle**: Initialization, termination, and instantiation
- **Command Handling**: The `/helloworld` command with various inputs
- **Message Formatting**: Message string formatting with different character sets
- **Event Processing**: Mock event handling and response generation
- **Edge Cases**: Empty messages, special characters, unicode text

### Test Categories

Tests are organized into the following categories:

- `TestMyPlugin`: Core plugin functionality tests
- `TestPluginMetadata`: Plugin metadata and documentation tests
- `TestMessageFormatting`: Message formatting utility tests
- `TestPluginRegistration`: Plugin registration and decorator tests

## Manual Testing Checklist

### Prerequisites

- [ ] AstrBot is installed and running
- [ ] Plugin is loaded in AstrBot
- [ ] Access to a chat interface connected to AstrBot

### Basic Functionality Tests

#### Test 1: Basic Command Execution
**Objective**: Verify the plugin responds to the `/helloworld` command

**Steps**:
1. Send message: `/helloworld`
2. Verify response contains greeting with your username
3. Verify response format: "Hello, {username}, 你发了 !"

**Expected Result**: Bot responds with greeting message

**Status**: [ ] Pass [ ] Fail

---

#### Test 2: Command with Message
**Objective**: Verify the plugin echoes the message content

**Steps**:
1. Send message: `/helloworld This is a test message`
2. Verify response contains "This is a test message"
3. Verify username is included in response

**Expected Result**: Bot responds: "Hello, {username}, 你发了 This is a test message!"

**Status**: [ ] Pass [ ] Fail

---

#### Test 3: Special Characters
**Objective**: Test command with special characters

**Steps**:
1. Send message: `/helloworld !@#$%^&*()`
2. Verify special characters are preserved in response
3. Check for proper encoding/escaping

**Expected Result**: Bot echoes special characters correctly

**Status**: [ ] Pass [ ] Fail

---

#### Test 4: Unicode Characters
**Objective**: Test command with unicode/emoji content

**Steps**:
1. Send message: `/helloworld 你好世界 🌍`
2. Verify unicode characters display correctly
3. Check emoji rendering

**Expected Result**: Bot handles unicode and emoji properly

**Status**: [ ] Pass [ ] Fail

---

#### Test 5: Long Messages
**Objective**: Test command with lengthy message content

**Steps**:
1. Send message: `/helloworld` followed by 200+ characters
2. Verify entire message is captured
3. Check for any truncation issues

**Expected Result**: Bot echoes full message content

**Status**: [ ] Pass [ ] Fail

---

#### Test 6: Empty Command
**Objective**: Test command without additional content

**Steps**:
1. Send message: `/helloworld` (no additional text)
2. Verify bot still responds
3. Check response format with empty message_str

**Expected Result**: Bot responds: "Hello, {username}, 你发了 !"

**Status**: [ ] Pass [ ] Fail

---

### Error Handling Tests

#### Test 7: Multiple Spaces
**Objective**: Test command with extra whitespace

**Steps**:
1. Send message: `/helloworld    test    message`
2. Verify bot handles multiple spaces
3. Check if spaces are preserved or normalized

**Expected Result**: Bot responds appropriately

**Status**: [ ] Pass [ ] Fail

---

#### Test 8: Case Sensitivity
**Objective**: Verify command case sensitivity

**Steps**:
1. Send message: `/HelloWorld`
2. Send message: `/HELLOWORLD`
3. Verify command behavior (should not trigger if case-sensitive)

**Expected Result**: Commands should be case-sensitive (only `/helloworld` works)

**Status**: [ ] Pass [ ] Fail

---

### Integration Tests

#### Test 9: Concurrent Requests
**Objective**: Test plugin handling multiple simultaneous requests

**Steps**:
1. Have multiple users send `/helloworld` at the same time
2. Verify each gets appropriate response with their own username
3. Check for any race conditions or cross-user issues

**Expected Result**: Each user receives personalized response

**Status**: [ ] Pass [ ] Fail

---

#### Test 10: Plugin Reload
**Objective**: Test plugin behavior after reload

**Steps**:
1. Send `/helloworld test` and verify response
2. Reload the plugin through AstrBot interface
3. Send `/helloworld test` again
4. Verify response is identical

**Expected Result**: Plugin works correctly after reload

**Status**: [ ] Pass [ ] Fail

---

#### Test 11: Logging Verification
**Objective**: Verify message chains are logged correctly

**Steps**:
1. Check AstrBot logs before test
2. Send `/helloworld log test`
3. Review logs for message chain output
4. Verify log entry contains expected information

**Expected Result**: Message chain appears in logs

**Status**: [ ] Pass [ ] Fail

---

### Performance Tests

#### Test 12: Response Time
**Objective**: Measure plugin response time

**Steps**:
1. Send `/helloworld` command
2. Measure time from send to response
3. Repeat 10 times and calculate average

**Expected Result**: Average response time < 500ms

**Average Time**: _____ ms

**Status**: [ ] Pass [ ] Fail

---

#### Test 13: Resource Usage
**Objective**: Monitor plugin resource consumption

**Steps**:
1. Monitor AstrBot memory usage before test
2. Send 100 `/helloworld` commands rapidly
3. Monitor memory usage after test
4. Check for memory leaks

**Expected Result**: No significant memory increase

**Status**: [ ] Pass [ ] Fail

---

### Platform-Specific Tests

#### Test 14: Different Chat Platforms
**Objective**: Verify plugin works on all supported platforms

**Platforms to Test**:
- [ ] QQ
- [ ] Discord
- [ ] Telegram
- [ ] WeChat
- [ ] Other: __________

**Steps**:
1. For each platform, send `/helloworld platform test`
2. Verify response format is correct
3. Check username extraction works properly

**Expected Result**: Plugin works consistently across platforms

---

#### Test 15: Different User Types
**Objective**: Test with different user account types

**Steps**:
1. Test with regular user account
2. Test with admin/moderator account
3. Test with bot account (if applicable)

**Expected Result**: Plugin responds to all user types

**Status**: [ ] Pass [ ] Fail

---

## Test Summary

**Date**: _______________

**Tester**: _______________

**Environment**: _______________

**Total Tests**: 15

**Passed**: _____

**Failed**: _____

**Notes**:
```
(Add any additional observations or issues found during testing)
```

## Known Issues

Document any known issues or limitations discovered during testing:

1. 
2. 
3. 

## Test Automation Roadmap

Future automated tests to implement:

- [ ] Integration tests with mock AstrBot instance
- [ ] Performance benchmarking tests
- [ ] Cross-platform compatibility tests
- [ ] Load testing for concurrent users
- [ ] Message chain parsing tests

## Reporting Issues

If you discover bugs during testing:

1. Document the test case number
2. Note the exact input and output
3. Include screenshots if applicable
4. Report in the issue tracker with label `bug`
5. Reference this testing document

## Additional Resources

- [AstrBot Documentation](https://astrbot.app)
- [Plugin Development Guide](https://astrbot.app/plugin-dev)
- [pytest Documentation](https://docs.pytest.org/)
