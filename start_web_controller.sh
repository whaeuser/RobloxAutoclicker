#!/bin/bash
# Startet den Web Controller

echo "🌐 Starte Autoinput Web Controller..."
echo ""

# Prüfe ob Port 8080 bereits belegt ist und beende den Prozess
PORT_PID=$(lsof -ti:8080 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  Port 8080 ist bereits belegt (PID: $PORT_PID)"
    echo "🔄 Beende alten Prozess..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 1
    echo "✅ Alter Prozess beendet"
    echo ""
fi

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
