#!/bin/bash

###############################################################################
# YouTube Video Uploader - Startup Script (Unix/macOS)
# This script automatically handles virtual environment creation,
# dependency installation, and application startup.
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_info "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH if needed
    if ! command -v uv &> /dev/null; then
        export PATH="$HOME/.local/bin:$PATH"
        print_warning "uv has been added to PATH for this session"
        print_warning "To make it permanent, add the following to your shell profile:"
        print_warning "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
else
    print_success "uv is already installed"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment..."
    uv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    print_info "Activating virtual environment..."
    source .venv/bin/activate
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Install or update dependencies
print_info "Installing/updating dependencies..."
uv pip install -r requirements.txt
print_success "Dependencies installed"

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p data/tokens logs
print_success "Directories created"

# Check if Python version is compatible
PYTHON_VERSION=$(python --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_warning "Python version $PYTHON_VERSION detected"
    print_warning "Python 3.10 or higher is recommended"
    print_warning "The application may not work correctly with this version"
    read -p "Do you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Exiting..."
        exit 1
    fi
fi

# Start the application
print_info "Starting YouTube Video Uploader..."
echo ""
print_success "Application will open in your default browser"
echo ""

# Run Streamlit
streamlit run app.py

# Cleanup on exit
cleanup() {
    print_info "Cleaning up temporary files..."
    rm -f temp_*
    print_success "Cleanup complete"
}

# Register cleanup function
trap cleanup EXIT
