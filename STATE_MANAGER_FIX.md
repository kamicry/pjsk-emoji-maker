# StateManager Unhashable Type Fix

## 问题描述
当用户调用 `/pjsk.draw` 或 `/pjsk.绘制` 命令时，在 main.py 第 150 行出现错误：
```
TypeError: unhashable type: 'PlatformMetadata'
  File "/AstrBot/data/plugins/pjsk_emoji_maker/main.py", line 150, in get
    return self._states.get(key)
```

## 根本原因
1. `event.platform` 返回的是一个 `PlatformMetadata` 对象，而不是字符串
2. `StateManager.get()` 方法期望接收可哈希的 key（元组），但实际接收到了不可哈希的对象
3. `adjust` 命令中调用了不存在的 `_render_via_draw()` 方法

## 修复方案

### 1. 修复 `_state_key()` 方法 (第311-335行)
```python
def _state_key(self, event: AstrMessageEvent) -> Tuple[str, str]:
    platform = getattr(event, "platform", "unknown") or "unknown"
    # Ensure platform is a string (not an object like PlatformMetadata)
    if not isinstance(platform, str):
        platform = str(platform) or "unknown"
    
    # ... 其余逻辑保持不变
```

### 2. 增强 `StateManager` 类的类型检查 (第143-171行)
为所有方法添加了 key 类型验证：
```python
def get(self, key: Tuple[str, str]) -> Optional[RenderState]:
    # Ensure key is hashable (tuple of strings)
    if not isinstance(key, tuple) or len(key) != 2:
        raise TypeError(f"StateManager key must be a tuple of (platform, session_id), got: {type(key)}")
    if not all(isinstance(k, str) for k in key):
        raise TypeError(f"StateManager key elements must be strings, got: {key}")
    return self._states.get(key)
```

### 3. 修复缺失的方法调用 (第777行)
```python
# 修复前：
result = await self._render_via_draw(event, headline)

# 修复后：
result = await self._render_and_respond(event, state, headline)
```

## 验证结果
✅ 生成表情包时不再出现 'unhashable type' 错误
✅ 用户状态能被正确保存和读取  
✅ 所有命令（draw, adjust, list）都能正常工作
✅ 状态管理器使用的 key 都是字符串或可哈希的值
✅ 代码编译通过，没有语法错误

## 技术细节
- `PlatformMetadata` 对象通过 `str()` 转换为字符串表示
- StateManager 现在提供清晰的错误信息以帮助调试
- 所有的 key 现在都保证是 `Tuple[str, str]` 类型，可哈希且唯一
- 修复保持了向后兼容性，现有的字符串 key 仍然正常工作

## 测试覆盖
- 测试了字符串 key 的正常工作流程
- 测试了对象 key 的正确拒绝和错误处理
- 测试了元组大小验证
- 测试了 platform 对象到字符串的转换
- 测试了完整的集成流程

修复已通过所有测试验证，可以安全部署。