# Development Guide

This guide provides information for developers who want to contribute to or extend the Hello World plugin.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager
- AstrBot development environment
- Git

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd plugin-template
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Install the plugin in development mode:
   ```bash
   pip install -e .
   ```

## Project Structure

```
.
├── main.py                  # Main plugin implementation
├── metadata.yaml            # Plugin metadata
├── README.md               # User documentation
├── LICENSE                 # License file
├── pyproject.toml          # Python project configuration
├── pytest.ini              # Pytest configuration
├── MANIFEST.in             # Package manifest for distribution
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development dependencies
├── __init__.py            # Package initialization
├── tests/                  # Test directory
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration
│   ├── test_plugin.py     # Unit tests
│   └── test_integration.py # Integration tests
└── docs/                   # Documentation
    ├── testing.md         # Testing guide
    └── development.md     # This file
```

## Code Style and Conventions

### Python Style

- Follow PEP 8 conventions
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for all public methods

### Naming Conventions

- Classes: `PascalCase`
- Functions/Methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Docstring Format

```python
async def method_name(self, param: str) -> str:
    """Brief description of method.
    
    Longer description if needed.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    pass
```

## Plugin Architecture

### Registration

The plugin is registered using the `@register` decorator:

```python
@register("plugin_name", "Author", "Description", "Version")
class MyPlugin(Star):
    pass
```

### Lifecycle Hooks

#### `__init__(self, context: Context)`
- Called when plugin is instantiated
- Initialize instance variables here
- Call `super().__init__(context)`

#### `async def initialize(self)`
- Optional async initialization
- Called after `__init__`
- Use for async setup operations

#### `async def terminate(self)`
- Optional cleanup method
- Called when plugin is unloaded
- Close connections, save state, etc.

### Command Handlers

#### Basic Command Handler

```python
@filter.command("commandname")
async def command_handler(self, event: AstrMessageEvent):
    """Command description"""
    # Process event
    user_name = event.get_sender_name()
    message = event.message_str
    
    # Return response
    yield event.plain_result(f"Response: {message}")
```

#### Command Handler Features

- **Async Generator**: Use `yield` to send responses
- **Event Object**: Contains message data and sender info
- **Filters**: Additional filters can be added to decorators

### Event Processing

#### Available Event Properties

- `event.message_str`: Plain text message content
- `event.get_sender_name()`: Sender's display name
- `event.get_messages()`: Full message chain
- `event.session_id`: Unique session identifier
- `event.platform`: Platform (QQ, Discord, etc.)

#### Response Methods

- `event.plain_result(text)`: Send plain text
- `event.image_result(path)`: Send image
- `event.chain_result(chain)`: Send message chain

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=main --cov-report=html

# Run specific test file
pytest tests/test_plugin.py

# Run specific test
pytest tests/test_plugin.py::TestMyPlugin::test_plugin_initialization

# Run only smoke tests
pytest -m smoke

# Run only integration tests
pytest -m integration
```

### Writing Tests

#### Unit Test Template

```python
import pytest
from unittest.mock import Mock

class TestFeature:
    @pytest.fixture
    def setup(self):
        # Setup code
        return object_to_test
    
    def test_feature(self, setup):
        # Test code
        assert setup.method() == expected_value
```

#### Async Test Template

```python
@pytest.mark.asyncio
async def test_async_feature():
    # Test async code
    result = await async_function()
    assert result == expected_value
```

### Test Markers

- `@pytest.mark.unit`: Unit test
- `@pytest.mark.integration`: Integration test
- `@pytest.mark.smoke`: Smoke test
- `@pytest.mark.asyncio`: Async test

## Debugging

### Logging

Use the AstrBot logger:

```python
from astrbot.api import logger

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Debug Mode

Run AstrBot with debug logging:

```bash
astrbot --debug
```

### Common Issues

#### Import Errors

- Ensure AstrBot is installed
- Check `sys.path` includes plugin directory
- Verify `__init__.py` exists in package

#### Command Not Triggering

- Check command name spelling
- Verify `@filter.command()` decorator
- Ensure plugin is loaded in AstrBot

#### Async Issues

- All command handlers must be `async`
- Use `await` for async calls
- Use `yield` for responses

## Building and Distribution

### Building Package

```bash
# Build distribution
python -m build

# Built files will be in dist/
```

### Package Contents

The package includes:

- Source code (`main.py`, `__init__.py`)
- Metadata (`metadata.yaml`)
- Documentation (`README.md`, `docs/`)
- Tests (`tests/`)
- Configuration (`pyproject.toml`, `pytest.ini`)

### Publishing

1. Update version in `metadata.yaml` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Build package: `python -m build`
4. Test package installation
5. Create git tag: `git tag v1.0.0`
6. Push changes and tag

## Contributing

### Contribution Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes
4. Add tests
5. Run test suite: `pytest`
6. Commit changes: `git commit -m "Description"`
7. Push branch: `git push origin feature-name`
8. Create Pull Request

### Pull Request Guidelines

- Include tests for new features
- Update documentation
- Follow code style conventions
- Write clear commit messages
- Reference related issues

### Code Review Process

1. Automated tests must pass
2. Code review by maintainer
3. Address review comments
4. Final approval and merge

## Extending the Plugin

### Adding New Commands

```python
@filter.command("newcommand")
async def new_command(self, event: AstrMessageEvent):
    """New command description"""
    # Implementation
    yield event.plain_result("Response")
```

### Adding Configuration

Update `metadata.yaml`:

```yaml
config:
  setting_name:
    type: string
    default: "default_value"
    description: "Setting description"
```

Access in code:

```python
value = self.context.config.get("setting_name", "default")
```

### Adding Dependencies

1. Add to `requirements.txt`:
   ```
   package-name>=1.0.0
   ```

2. Update documentation with installation instructions

3. Add to `pyproject.toml` dependencies

### Adding Assets

1. Create asset directory (e.g., `assets/`)
2. Update `MANIFEST.in`:
   ```
   recursive-include assets *
   ```
3. Update `pyproject.toml`:
   ```toml
   [tool.setuptools.package-data]
   "*" = ["assets/*"]
   ```

## Performance Optimization

### Best Practices

- Avoid blocking operations in command handlers
- Use async operations where possible
- Cache expensive computations
- Limit message chain size
- Use efficient data structures

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Code to profile
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

## Resources

- [AstrBot Documentation](https://astrbot.app)
- [AstrBot API Reference](https://astrbot.app/api)
- [Plugin Development Guide](https://astrbot.app/plugin-dev)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)
- [pytest Documentation](https://docs.pytest.org/)

## Getting Help

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas
- Documentation: Check official AstrBot docs
- Community: Join AstrBot community channels

## License

See [LICENSE](../LICENSE) file for details.
