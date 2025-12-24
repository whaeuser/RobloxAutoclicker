#!/bin/bash
# Erstellt eine macOS .app Bundle für die GUI

APP_NAME="Roblox Autoclicker"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

echo "🎮 Erstelle $APP_NAME.app..."

# Lösche alte App falls vorhanden
rm -rf "$APP_DIR"

# Erstelle Verzeichnisstruktur
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Erstelle Launcher-Script
cat > "$MACOS_DIR/launcher.sh" << 'EOF'
#!/bin/bash

# Logfile für Debugging
LOGFILE="/tmp/roblox_autoclicker_gui.log"

exec > "$LOGFILE" 2>&1

echo "=== Roblox Autoclicker GUI Start ==="
echo "Datum: $(date)"

# Finde das Projektverzeichnis
APP_PATH="$(cd "$(dirname "$0")/../../.." && pwd)"
echo "App Path: $APP_PATH"

cd "$APP_PATH" || exit 1
echo "Working Directory: $(pwd)"

# Prüfe ob yaml installiert ist, falls nicht installiere es
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "YAML nicht gefunden, installiere..."
    pip3 install pyyaml --user --quiet
fi

# Starte GUI
echo "Starte Python GUI..."
python3 autoclicker_gui.py

echo "GUI beendet mit Code: $?"
EOF

chmod +x "$MACOS_DIR/launcher.sh"

# Erstelle Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher.sh</string>
    <key>CFBundleIdentifier</key>
    <string>com.roblox.autoclicker</string>
    <key>CFBundleName</key>
    <string>Roblox Autoclicker</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
EOF

echo "✅ $APP_NAME.app wurde erstellt!"
echo ""
echo "📍 Du kannst jetzt die App im Finder doppelklicken:"
echo "   $(pwd)/$APP_DIR"
