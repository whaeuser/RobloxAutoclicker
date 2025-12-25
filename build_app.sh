#!/bin/bash
# Automatisches Build-Script für Autoinput.app
# Stellt sicher, dass alle Scripts aktuell sind

set -e  # Bei Fehler abbrechen

echo "=================================="
echo "🔨 Building Autoinput.app"
echo "=================================="
echo ""

# 1. Synchronisiere Scripts von src/ nach autoinput/
echo "📋 Schritt 1: Synchronisiere Scripts..."
echo "  Kopiere autoinput_toggle.py..."
cp src/autoinput_toggle.py autoinput/
echo "  Kopiere debug_autoinput.py..."
cp src/debug_autoinput.py autoinput/
echo "  ✅ Scripts synchronisiert"
echo ""

# 2. Lösche alten Build
echo "🗑️  Schritt 2: Lösche alten Build..."
rm -rf build
rm -rf Autoinput.app
echo "  ✅ Alter Build gelöscht"
echo ""

# 3. Erstelle neue App
echo "🏗️  Schritt 3: Erstelle App..."
briefcase create macOS
echo "  ✅ App erstellt"
echo ""

# 4. Baue App
echo "🔧 Schritt 4: Baue App..."
briefcase build macOS
echo "  ✅ App gebaut"
echo ""

# 5. Kopiere App ins Hauptverzeichnis
echo "📦 Schritt 5: Kopiere App..."
cp -R build/autoinput/macos/app/Autoinput.app .
echo "  ✅ App kopiert nach: $(pwd)/Autoinput.app"
echo ""

echo "=================================="
echo "✅ Build erfolgreich abgeschlossen!"
echo "=================================="
echo ""
echo "Die App ist bereit unter: Autoinput.app"
echo ""
