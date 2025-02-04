#!/bin/bash

# Make script executable from anywhere
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Colors for pretty output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if python3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}Python 3 not found. Trying python...${NC}"
        if ! command -v python &> /dev/null; then
            echo -e "${RED}Neither python3 nor python found. Please install Python 3.${NC}"
            exit 1
        fi
        PYTHON="python"
    else
        PYTHON="python3"
    fi
}

# Function to display the menu
show_menu() {
    clear
    echo -e "${GREEN}Password Manager Analyzer Build System${NC}"
    echo "==================================="
    echo
    echo "1. Build Development Version (Standalone Binary)"
    echo "2. Build Installer"
    echo "3. Build Both"
    echo "4. Exit"
    echo
}

# Main build function
build() {
    local choice=$1
    
    case $choice in
        1)
            $PYTHON build.py --dev-only
            ;;
        2)
            $PYTHON build.py --installer-only
            ;;
        3)
            $PYTHON build.py
            ;;
        *)
            echo -e "${RED}Invalid choice!${NC}"
            exit 1
            ;;
    esac
}

# Main execution
check_python

show_menu

read -p "Enter your choice (1-4): " choice

if [ "$choice" = "4" ]; then
    echo "Exiting..."
    exit 0
fi

build $choice

echo -e "${GREEN}Build process completed!${NC}" 