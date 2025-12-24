#!/bin/bash
# Startet die Roblox Autoclicker GUI

cd "$(dirname "$0")"

echo "🎮 Starte Roblox Autoclicker GUI..."

# Prüfe ob tkinter verfügbar ist
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter ist nicht installiert!"
    echo ""
    echo "Installiere mit:"
    echo "  brew install python-tk@3.11  # oder deine Python-Version"
    exit 1
fi

# Starte GUI
python3 autoclicker_gui.py
