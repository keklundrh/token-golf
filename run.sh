#!/bin/bash

# Token Golf - Easy Run Script
# This script handles all setup and starts the application

set -e  # Exit on error

echo "🏌️  Token Golf - Starting Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    print_error "Error: app/main.py not found. Please run this script from the token-golf directory."
    exit 1
fi

print_success "Found project directory"

# Check for Python 3.12
echo ""
echo "Checking Python version..."
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    print_success "Found Python 3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [ "$PYTHON_VERSION" = "3.12" ]; then
        PYTHON_CMD="python3"
        print_success "Found Python 3.12"
    else
        print_error "Python 3.12 is required (found Python $PYTHON_VERSION)"
        echo ""
        echo "Python 3.13+ is not yet supported due to dependency compatibility."
        echo ""
        echo "To install Python 3.12:"
        echo "  macOS:  brew install python@3.12"
        echo "  Linux:  sudo apt install python3.12  (or equivalent)"
        echo ""
        exit 1
    fi
else
    print_error "Python 3 not found"
    echo "Please install Python 3.12"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    print_warning "Virtual environment not found. Creating it..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Check if dependencies are installed
echo ""
echo "Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    print_warning "Dependencies not installed. Installing..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_success "Dependencies already installed"
fi

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Copying from .env.example..."
    cp .env.example .env
    print_warning "IMPORTANT: Edit .env and add your Claude API key!"
    echo ""
    echo "  Open .env in your editor and set:"
    echo "  CLAUDE_API_KEY=your-key-here"
    echo ""
    read -p "Press Enter when you've added your API key..."
fi

# Check if API key is set
if grep -q "your-api-key-here-replace-me" .env 2>/dev/null; then
    print_error "API key not configured in .env file!"
    echo ""
    echo "Please edit .env and replace 'your-api-key-here-replace-me' with your actual Claude API key"
    echo ""
    read -p "Press Enter when ready to continue, or Ctrl+C to exit..."
fi

print_success "Environment configured"

# Check if database exists
echo ""
if [ ! -f "token_golf.db" ]; then
    print_warning "Database not found. Running migrations..."
    alembic upgrade head
    print_success "Database initialized"
else
    print_success "Database exists"
fi

# Check if Tailwind CSS output exists
echo ""
if [ ! -f "static/css/output.css" ]; then
    print_warning "Tailwind CSS not built. Checking for Node.js..."
    if command -v node &> /dev/null; then
        echo "Building Tailwind CSS..."
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css
        print_success "Tailwind CSS built"
    else
        print_warning "Node.js not found. Skipping Tailwind CSS build."
        print_warning "Install Node.js and run: npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css"
    fi
else
    print_success "Tailwind CSS already built"
fi

# All checks passed
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "All checks passed! Starting server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Server will be available at:"
echo "   🌐 http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🏌️  Leaderboard: http://localhost:8000/leaderboard"
echo ""
echo "⚠️  KNOWN ISSUE: 'Generate Username' button has a bug."
echo "   Quick fix in ISSUES.md or QUICKSTART.md"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server (reduced logging: only warnings and errors)
uvicorn app.main:app --reload --port 8000 --log-level warning
