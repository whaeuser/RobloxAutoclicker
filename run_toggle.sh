#!/bin/bash
# Startet den Autoinput im Toggle-Modus

cd "$(dirname "$0")"

echo "🎮 Starte Autoinput (Toggle-Modus)..."

# Python mit venv oder system python
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 autoinput_toggle.py
