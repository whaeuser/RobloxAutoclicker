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
echo "  Kopiere Module für Import..."
cp src/autoinput_toggle.py autoinput/toggle_mode.py
cp src/debug_autoinput.py autoinput/debug_mode.py
echo "  Kopiere Quartz-Autoclicker (OHNE pynput)..."
cp src/autoclicker_quartz.py autoinput/
echo "  Stelle sicher dass run_autoclicker.sh existiert..."
chmod +x autoinput/run_autoclicker.sh 2>/dev/null || true
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

# 5. Kopiere pynput und pyautogui in die App
echo "📦 Schritt 5: Kopiere Dependencies..."
APP_PACKAGES="build/autoinput/macos/app/Autoinput.app/Contents/Resources/app_packages"

# Finde Python 3.13 site-packages (gleiche Version wie in der App!)
PYTHON_SITE=$(python3.13 -c "import site; print(site.getsitepackages()[0])")

echo "  Kopiere pynput..."
cp -R "$PYTHON_SITE/pynput" "$APP_PACKAGES/"
echo "  Kopiere pyautogui..."
cp -R "$PYTHON_SITE/pyautogui" "$APP_PACKAGES/"

# Kopiere auch alle Dependencies
echo "  Kopiere Dependencies..."

# Einzelne .py Dateien
for pyfile in six.py; do
    if [ -f "$PYTHON_SITE/$pyfile" ]; then
        cp "$PYTHON_SITE/$pyfile" "$APP_PACKAGES/" 2>/dev/null || true
    fi
done

# Kopiere ALLE verfügbaren Framework-Module (alles was mit Großbuchstaben beginnt)
echo "  Kopiere Framework-Module..."
for pkg in "$PYTHON_SITE"/[A-Z]*; do
    if [ -d "$pkg" ]; then
        pkg_name=$(basename "$pkg")
        cp -R "$pkg" "$APP_PACKAGES/" 2>/dev/null || true
        echo "    ✓ $pkg_name"
    fi
done

# Kopiere weitere Packages
for pkg in objc rubicon_objc pymsgbox pytweening pyscreeze pygetwindow mouseinfo pyperclip pyrect; do
    if [ -d "$PYTHON_SITE/$pkg" ]; then
        cp -R "$PYTHON_SITE/$pkg" "$APP_PACKAGES/" 2>/dev/null || true
        echo "    ✓ $pkg"
    fi
done

echo "  ✅ Dependencies kopiert"
echo ""

# 6. Kopiere App ins Hauptverzeichnis
echo "📦 Schritt 6: Kopiere App..."
cp -R build/autoinput/macos/app/Autoinput.app .
echo "  ✅ App kopiert nach: $(pwd)/Autoinput.app"
echo ""

echo "=================================="
echo "✅ Build erfolgreich abgeschlossen!"
echo "=================================="
echo ""
echo "Die App ist bereit unter: Autoinput.app"
echo ""
