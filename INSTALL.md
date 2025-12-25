# Installation auf einem anderen Mac

## ⚠️ Wichtiger Hinweis

Die **Autoinput.app ist NICHT vollständig standalone**!

**Grund:** `pyautogui` und `pynput` haben keine ARM64-Wheels für macOS und können daher nicht in die App gebündelt werden. Die App verwendet **System-Python** mit den systemweit installierten Paketen.

---

## 📋 Voraussetzungen auf dem Ziel-Mac

### 1. Python 3.8+ muss installiert sein

```bash
# Prüfe Python-Version
python3 --version
```

Falls Python fehlt:
```bash
# Homebrew installieren (falls nicht vorhanden)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python installieren
brew install python@3.13
```

### 2. Dependencies installieren

**Wichtig:** Diese Pakete müssen auf **jedem** Mac installiert sein, auf dem die App laufen soll!

```bash
pip3 install pyautogui pynput pyyaml
```

### 3. Berechtigungen erteilen

Autoinput benötigt **Accessibility-Zugriff**:

1. Öffne **Systemeinstellungen** → **Datenschutz & Sicherheit**
2. Wähle **Bedienungshilfen**
3. Füge **Autoinput.app** oder **Terminal** hinzu (je nachdem, wo du die App startest)
4. Aktiviere das Häkchen

---

## 🚀 Installation

### Option 1: Nur die .app kopieren (Empfohlen)

```bash
# 1. Kopiere Autoinput.app auf den anderen Mac
# (z.B. via AirDrop, USB-Stick, Cloud)

# 2. Verschiebe die App nach /Applications
mv Autoinput.app /Applications/

# 3. Installiere Dependencies
pip3 install pyautogui pynput pyyaml

# 4. config.yaml kopieren (optional)
# Falls du deine Einstellungen behalten willst:
mkdir -p ~/Library/Application\ Support/Autoinput/
cp config.yaml ~/Library/Application\ Support/Autoinput/
```

### Option 2: Ganzes Projekt klonen

```bash
# 1. Repository klonen
git clone https://github.com/whaeuser/RobloxAutoclicker.git
cd RobloxAutoclicker

# 2. Dependencies installieren
pip3 install pyautogui pynput pyyaml toga briefcase

# 3. App öffnen
open Autoinput.app
```

---

## ✅ Testen

Nach der Installation:

```bash
# 1. App öffnen
open /Applications/Autoinput.app

# 2. Im GUI: Config-Tab öffnen
# 3. Einstellungen vornehmen
# 4. Autoclicker starten
```

Falls Fehler auftreten:
```bash
# Prüfe ob Dependencies installiert sind
python3 -c "import pyautogui; import pynput; print('✅ Dependencies OK')"
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pyautogui'"

```bash
pip3 install pyautogui pynput
```

### "Operation not permitted" oder "Accessibility Error"

1. Öffne **Systemeinstellungen** → **Datenschutz & Sicherheit** → **Bedienungshilfen**
2. Füge **Autoinput.app** oder **Terminal** hinzu
3. App neu starten

### App startet nicht / "Beschädigte App"

```bash
# macOS Gatekeeper umgehen
xattr -cr /Applications/Autoinput.app
```

### Scripts starten nicht

```bash
# Prüfe welches Python die App verwendet
which python3

# Prüfe ob pyautogui dort installiert ist
python3 -m pip list | grep pyautogui
```

---

## 📦 Was wird kopiert?

### Minimal (nur .app):
```
Autoinput.app          ← Die App selbst (ca. 50-100 MB)
```

**Vorteile:**
- ✅ Schnell (nur eine Datei)
- ✅ Sauber (/Applications)

**Nachteile:**
- ❌ Dependencies müssen separat installiert werden
- ❌ config.yaml muss separat kopiert werden

### Vollständig (ganzes Projekt):
```
RobloxAutoclicker/
├── Autoinput.app           ← Die App
├── config.yaml             ← Deine Einstellungen
├── src/                    ← Source-Code
└── README.md               ← Dokumentation
```

**Vorteile:**
- ✅ config.yaml ist dabei
- ✅ Kann App selbst neu bauen
- ✅ Hat Source-Code für Anpassungen

**Nachteile:**
- ❌ Größer (~100-200 MB mit Build-Dateien)

---

## 🔄 Updates

Wenn du die App updatest:

```bash
# 1. Neue .app kopieren
cp -R Autoinput.app /Applications/

# 2. Alte App-Prozesse beenden
killall -9 Autoinput 2>/dev/null

# 3. Neue App starten
open /Applications/Autoinput.app
```

---

## 📝 Zusammenfassung

**JA, du kannst die .app kopieren**, ABER:

1. ✅ **Autoinput.app** kopieren nach `/Applications`
2. ⚠️ **Python 3.8+** muss installiert sein
3. ⚠️ **Dependencies installieren:** `pip3 install pyautogui pynput pyyaml`
4. ⚠️ **Berechtigungen:** Accessibility-Zugriff erteilen
5. ✅ **config.yaml** optional kopieren
6. ✅ **App starten:** `open /Applications/Autoinput.app`

**Die App ist portabel, aber benötigt System-Python + Dependencies!**
