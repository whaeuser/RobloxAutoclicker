#!/bin/bash
# Setup-Script für Roblox Autoclicker
# Erstellt virtual environment und installiert Dependencies

set -e  # Bei Fehler abbrechen

echo "🚀 Roblox Autoclicker Setup"
echo "=========================="
echo ""

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Prüfe ob Python 3 installiert ist
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 ist nicht installiert!${NC}"
    echo "Bitte installiere Python 3 über: https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 gefunden:${NC} $(python3 --version)"
echo ""

# Entferne altes venv falls vorhanden
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Altes virtual environment gefunden - wird entfernt${NC}"
    rm -rf venv
fi

# Erstelle virtual environment
echo "📦 Erstelle virtual environment..."
python3 -m venv venv

# Aktiviere venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Update pip..."
pip install --upgrade pip --quiet

# Installiere Dependencies
echo "📥 Installiere Dependencies..."
pip install pynput pyobjc-framework-Quartz --quiet

echo ""
echo -e "${GREEN}✅ Setup erfolgreich abgeschlossen!${NC}"
echo ""
echo "⚠️  WICHTIG - Berechtigungen:"
echo "================================"
echo ""
echo "Das Python im venv benötigt Accessibility-Berechtigung!"
echo ""
echo "Option 1 (EMPFOHLEN): Verwende System-Python direkt"
echo "  → Führe aus: python3 debug_autoclicker.py"
echo "  → NICHT: source venv/bin/activate"
echo ""
echo "Option 2: Gib dem venv-Python Berechtigung"
echo "  1. Gehe zu: Systemeinstellungen → Datenschutz & Sicherheit → Bedienungshilfen"
echo "  2. Klicke auf '+' und füge hinzu:"
echo "     $(pwd)/venv/bin/python"
echo "  3. Dann kannst du ausführen:"
echo "     source venv/bin/activate"
echo "     python debug_autoclicker.py"
echo ""
echo -e "${YELLOW}💡 Tipp: Option 1 ist einfacher und funktioniert sofort!${NC}"
