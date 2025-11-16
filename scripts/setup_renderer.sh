#!/bin/bash

# PJSK Renderer Setup Script
# This script sets up the environment and dependencies for the PJSK renderer

set -e

echo "🎭 PJSK Renderer Setup"
echo "======================"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required (found $python_version)"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install

# Install system dependencies (Ubuntu/Debian)
echo "🔧 Checking system dependencies..."
if command -v apt-get &> /dev/null; then
    echo "📦 Installing system dependencies for Ubuntu/Debian..."
    sudo apt-get update
    sudo apt-get install -y \
        libnspr4 \
        libnss3 \
        libatk1.0-0t64 \
        libatk-bridge2.0-0t64 \
        libcups2t64 \
        libxkbcommon0 \
        libatspi2.0-0t64 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libcairo2 \
        libpango-1.0-0 \
        libasound2t64 \
        fonts-noto-cjk
    echo "✅ System dependencies installed"
else
    echo "⚠️ Not on Ubuntu/Debian. Please install system dependencies manually."
    echo "See docs/RENDERER_SETUP.md for details."
fi

# Setup fonts for rendering
echo "🔤 Setting up fonts..."
mkdir -p pjsk_emoji/assets/fonts
if [ -f "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc" ]; then
    cp /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc pjsk_emoji/assets/fonts/
    cp /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc pjsk_emoji/assets/fonts/
    echo "✅ Fonts installed successfully"
else
    echo "⚠️ Noto Sans CJK fonts not found. Using system fonts instead."
fi

# Generate placeholder images if they don't exist
if [ ! -f "pjsk_emoji/assets/emoji_images/miku.png" ]; then
    echo "🎨 Generating placeholder character images..."
    python3 scripts/generate_placeholder_images.py
fi

# Run quick test
echo "🧪 Running quick renderer test..."
if python3 scripts/quick_renderer_test.py; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Generated test files:"
    ls -la quick_test_*.png 2>/dev/null || echo "  (No test files found)"
    echo ""
    echo "Next steps:"
    echo "1. Activate the environment: source venv/bin/activate"
    echo "2. Run smoke tests: python3 tests/test_renderer_smoke.py"
    echo "3. Check documentation: docs/RENDERER_SETUP.md"
    echo ""
else
    echo ""
    echo "❌ Setup failed during testing"
    echo "Please check the error messages above"
    exit 1
fi