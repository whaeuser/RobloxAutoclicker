#!/bin/bash
# Startet die Autoinput GUI

cd "$(dirname "$0")/.."

echo "🎮 Starte Autoinput GUI..."

# Prüfe ob toga installiert ist
if ! python3 -c "import toga" 2>/dev/null; then
    echo "❌ Toga ist nicht installiert!"
    echo ""
    echo "Installiere mit:"
    echo "  pip3 install toga briefcase"
    exit 1
fi

# Starte Toga GUI (filtere .py Opening Warnung)
python3 src/autoinput_gui_toga.py 2>&1 | grep -v "Don't know how to open documents with extension"
