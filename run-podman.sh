#!/bin/bash

# Token Golf - Easy Podman Run Script
# This script starts the application using Podman containers

set -e  # Exit on error

echo "🏌️  Token Golf - Starting with Podman"
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
if [ ! -f "docker-compose.yml" ]; then
    print_error "Error: docker-compose.yml not found. Please run this script from the token-golf directory."
    exit 1
fi

print_success "Found project directory"

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

# Check if podman-compose is installed
echo ""
if ! command -v podman-compose &> /dev/null; then
    print_error "podman-compose not found!"
    echo ""
    echo "Install with:"
    echo "  macOS:  brew install podman-compose"
    echo "  Linux:  pip3 install podman-compose"
    echo ""
    echo "Or use Docker instead:"
    echo "  docker-compose up"
    exit 1
fi

print_success "podman-compose found"

# All checks passed
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "Starting containers..."
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
echo "💡 Useful commands:"
echo "   View logs:  podman-compose logs -f"
echo "   Stop:       podman-compose down"
echo ""
echo "Press Ctrl+C to stop (then run: podman-compose down)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start podman-compose
podman-compose up
