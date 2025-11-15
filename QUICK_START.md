# Quick Start Guide

A quick reference for getting started with the Hello World AstrBot plugin.

## For End Users

### Install the Plugin
1. Copy plugin to AstrBot plugins directory:
   ```bash
   cd <astrbot-installation>/plugins/
   git clone <repository-url> helloworld
   ```

2. Restart AstrBot or reload plugins

3. Test the plugin:
   ```
   /helloworld Hello World!
   ```

### Commands
- `/helloworld [message]` - Get a greeting with your message echoed back

---

## For Developers

### Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd plugin-template

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=main --cov-report=html

# Run specific test
pytest tests/test_plugin.py::TestMyPlugin::test_plugin_initialization
```

### Build Package
```bash
# Install build tool
pip install build

# Build package
python -m build

# Output: dist/astrbot_plugin_helloworld-1.0.0-py3-none-any.whl
```

---

## For Testers

### Automated Testing
```bash
# Setup
pip install -r requirements-dev.txt

# Run tests
pytest -v
```

### Manual Testing
See [docs/testing.md](docs/testing.md) for 15 manual test scenarios.

**Quick Test Checklist**:
- [ ] Basic command: `/helloworld`
- [ ] With message: `/helloworld test`
- [ ] Special chars: `/helloworld !@#$`
- [ ] Unicode: `/helloworld 你好`
- [ ] Empty: `/helloworld`

---

## Documentation Links

- **Users**: [README.md](README.md)
- **Developers**: [docs/development.md](docs/development.md)
- **Testers**: [docs/testing.md](docs/testing.md)
- **Overview**: [docs/project_summary.md](docs/project_summary.md)

---

## Common Tasks

### Add New Command
1. Edit `main.py`
2. Add method with `@filter.command("commandname")`
3. Write tests in `tests/test_plugin.py`
4. Update documentation in `README.md`
5. Run tests: `pytest`

### Update Documentation
1. Edit appropriate `.md` file
2. Update examples if code changed
3. Update `CHANGELOG.md` with changes
4. Verify links work

### Release New Version
1. Update version in `metadata.yaml` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run tests: `pytest`
4. Build package: `python -m build`
5. Tag release: `git tag v1.x.x`

---

## Troubleshooting

### Tests Fail to Import AstrBot
**Solution**: Tests use mocked AstrBot modules - this is expected and handled automatically.

### Package Build Fails
**Solution**: Ensure you have `build` installed: `pip install build`

### Command Not Triggering
**Solution**: 
1. Check plugin is loaded in AstrBot
2. Verify command name matches exactly
3. Check AstrBot logs for errors

---

## Getting Help

- Check documentation in `docs/` directory
- Read [AstrBot Documentation](https://astrbot.app)
- Open an issue on GitHub
- Review test examples in `tests/` directory

---

## Project Structure Overview

```
.
├── main.py              # Plugin implementation
├── metadata.yaml        # Plugin metadata
├── README.md           # Main documentation
├── tests/              # Test suite
│   ├── test_plugin.py       # Unit tests
│   └── test_integration.py  # Integration tests
└── docs/               # Additional documentation
    ├── testing.md           # Testing guide
    └── development.md       # Developer guide
```

---

**Need more details?** See the full [README.md](README.md)
