#!/bin/bash
# Startet den Autoclicker mit System-Python (umgeht venv-Berechtigungsproblem)

# Prüfe ob Dependencies installiert sind
if ! python3 -c "import pynput" 2>/dev/null; then
    echo "❌ Dependencies fehlen!"
    echo ""
    echo "Installiere mit:"
    echo "  pip3 install pynput pyobjc-framework-Quartz"
    echo ""
    echo "Oder mit brew:"
    echo "  brew install python3"
    echo "  pip3 install pynput pyobjc-framework-Quartz"
    exit 1
fi

# Starte den Autoclicker
echo "🚀 Starte Autoinput..."
echo ""
python3 debug_autoclicker.py
