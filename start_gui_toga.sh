#!/bin/bash
# Startet die Roblox Autoclicker Toga GUI

cd "$(dirname "$0")"

echo "🎮 Starte Roblox Autoclicker (Toga)..."

# Prüfe ob toga installiert ist
if ! python3 -c "import toga" 2>/dev/null; then
    echo "❌ Toga ist nicht installiert!"
    echo ""
    echo "Installiere mit:"
    echo "  pip3 install toga briefcase"
    exit 1
fi

# Starte Toga GUI
python3 autoclicker_gui_toga.py
