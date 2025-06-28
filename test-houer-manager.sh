#!/bin/bash
# Test script for HoUer Manager in development environment

echo "Testing HoUer Manager..."

# Check if we're in the right directory
if [[ ! -f "Manager/houer-manager.py" ]]; then
    echo "Error: Please run this script from the HoUer OS root directory"
    exit 1
fi

echo "Available commands:"
echo "1. Test GUI mode:"
echo "   ./Manager/houer-manager"
echo ""
echo "2. Test with debug output:"
echo "   ./Manager/houer-manager --debug"
echo ""
echo "3. Test minimized mode:"
echo "   ./Manager/houer-manager --minimized"
echo ""
echo "4. Show help:"
echo "   ./Manager/houer-manager --help"
echo ""
echo "5. Check version:"
echo "   ./Manager/houer-manager --version"

echo ""
echo "Testing basic functionality..."

# Test if Python script runs without errors
output=$(python3 Manager/houer-manager.py --help 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✓ Python script is executable"
elif echo "$output" | grep -q "tkinter is not available"; then
    echo "⚠ Python script works but tkinter is not installed"
    echo "  Install with: sudo pacman -S python-tk (on Arch)"
    echo "              sudo apt install python3-tk (on Ubuntu/Debian)"
    echo "              sudo dnf install python3-tkinter (on Fedora)"
else
    echo "✗ Python script has errors:"
    echo "$output"
    exit 1
fi

# Test if launcher script works
launcher_output=$(./Manager/houer-manager --help 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✓ Launcher script works"
elif echo "$launcher_output" | grep -q "tkinter is not available"; then
    echo "⚠ Launcher script works but tkinter is not installed"
else
    echo "✗ Launcher script has issues:"
    echo "$launcher_output"
    exit 1
fi

echo "✓ All tests passed!"
echo ""
echo "To run HoUer Manager, use: ./Manager/houer-manager" 