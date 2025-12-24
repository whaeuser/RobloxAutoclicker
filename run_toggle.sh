#!/bin/bash
# Startet den Roblox Autoclicker im Toggle-Modus

cd "$(dirname "$0")"

echo "🎮 Starte Roblox Autoclicker (Toggle-Modus)..."

# Python mit venv oder system python
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 roblox_autoclicker_toggle.py
