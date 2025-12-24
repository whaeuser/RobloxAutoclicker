#!/bin/bash
# Startet den Web Controller

echo "🌐 Starte Roblox Autoclicker Web Controller..."
echo ""

# Prüfe ob Flask installiert ist
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask ist nicht installiert!"
    echo ""
    echo "Installiere mit:"
    echo "  pip3 install flask pyyaml"
    exit 1
fi

# Prüfe ob alle Dependencies installiert sind
if ! python3 -c "import pynput, pyautogui, yaml" 2>/dev/null; then
    echo "⚠️  Nicht alle Dependencies installiert!"
    echo ""
    echo "Installiere mit:"
    echo "  pip3 install pynput pyautogui pyyaml flask"
    exit 1
fi

# Starte Web Controller
python3 web_controller.py
