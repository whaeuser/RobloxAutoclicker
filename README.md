# 🎮 Roblox Autoclicker

Ein konfigurierbarer Autoclicker für macOS mit GUI, Web-Interface und Terminal-Unterstützung.

## 📋 Inhaltsverzeichnis

- [Features](#features)
- [Installation](#installation)
- [Verwendung](#verwendung)
- [Konfiguration](#konfiguration)
- [Architektur](#architektur)
- [Aktueller Status](#aktueller-status)
- [Bekannte Issues](#bekannte-issues)
- [Nächste Session](#nächste-session-wo-weitermachen)

## ✨ Features

### Drei Bedienungsmöglichkeiten

1. **🖥️ GUI Desktop-App** (Empfohlen)
   - Grafische Oberfläche mit Tabs
   - Live-Log-Anzeige
   - Konfigurationseditor
   - Klick-Test-Bereich mit CPS-Messung
   - Farbige Buttons (Grün/Rot/Blau)

2. **🌐 Web-Interface**
   - Browser-basierte Steuerung auf Port 8080
   - Remote-Kontrolle möglich
   - Automatisches Neu-Laden bei Config-Änderungen

3. **⌨️ Terminal**
   - Direkter Aufruf der Python-Scripts
   - Für Scripting und Automation

### Klick-Modi

- **Fast Mode** (Empfohlen): Optimiert für hohe CPS
- **Standard Mode**: Normale Click-Events
- **Separate Events**: Separate Down/Up Events
- **Rechtsklick**: Statt Linksklick

### Aktivierungsmodi

- **Hold-Modus**: Klickt nur während Hotkey gedrückt ist
- **Toggle-Modus**: Ein/Aus-Schalter per Hotkey

### Debug-Features

- **Verbose Mode**: Zeigt jeden einzelnen Klick mit:
  - Millisekunden-Timestamp
  - Position (X, Y)
  - Gedrückte Taste
  - Click-Counter
- **Live Logs**: Echtzeit-Ausgabe in GUI und Terminal

## 🔧 Installation

### Voraussetzungen

```bash
# Python 3.x mit tkinter
brew install python-tk@3.11  # oder deine Python-Version

# Python-Abhängigkeiten
pip3 install pyautogui pynput pyyaml flask
```

### macOS Accessibility Permissions

**Wichtig**: Python/Terminal benötigt Accessibility-Rechte!

1. Öffne **System Settings** → **Privacy & Security** → **Accessibility**
2. Klicke auf **+** und füge hinzu:
   - `/usr/bin/python3`
   - Terminal.app (falls du vom Terminal startest)
3. Aktiviere die Checkboxen

## 🚀 Verwendung

### GUI starten (Empfohlen)

```bash
./start_gui.sh
```

Die GUI bietet drei Tabs:
- **⚡ Steuerung & Logs**: Start/Stop, Live-Logs
- **⚙️  Konfiguration**: Alle Einstellungen bearbeiten
- **🎯 Klick-Test**: CPS testen und messen

### Web-Interface starten

```bash
./start_web_controller.sh
```

Dann im Browser: `http://localhost:8080`

### Terminal-Nutzung

```bash
# Hold-Modus (klickt während Taste gedrückt)
python3 debug_autoclicker.py

# Toggle-Modus (ein/aus per Tastendruck)
python3 roblox_autoclicker_toggle.py
```

### Steuerung

- **Hotkey drücken**: Autoclicker aktivieren (Standard: Shift)
- **ESC**: Autoclicker beenden
- **Strg+C**: Autoclicker beenden

## ⚙️ Konfiguration

Alle Einstellungen in `config.yaml`:

```yaml
clicks_per_second: 12        # CPS (1-1000)
hotkey: shift                # Aktivierungs-Taste
activation_mode: hold        # 'hold' oder 'toggle'
click_mode: fast             # 'fast', 'standard', 'separate', 'right'
target_position: null        # [x, y] oder null für Maus-Position
enable_logging: true         # Logging aktivieren
verbose_mode: false          # Debug-Logs mit jedem Klick
```

### Verfügbare Hotkeys

`shift`, `shift_r`, `ctrl`, `ctrl_r`, `alt`, `alt_r`, `space`, `tab`, `f6`, `f7`, `f8`, `f9`

### Empfohlene Einstellungen

- **CPS**: 8-20 (Roblox-kompatibel)
- **Klick-Modus**: `fast`
- **Aktivierung**: `hold` (sicherer, sofortiger Stop)

## 🏗️ Architektur

### Projekt-Struktur

```
RobloxAutoclicker/
├── autoclicker_gui.py              # GUI Desktop-App (tkinter)
├── debug_autoclicker.py            # Hold-Modus Script
├── roblox_autoclicker_toggle.py    # Toggle-Modus Script
├── web_controller.py               # Flask Web-Interface
├── config.yaml                     # Zentrale Konfiguration
├── start_gui.sh                    # GUI Launcher
├── start_web_controller.sh         # Web Launcher
├── create_app.sh                   # macOS .app Builder
└── README.md                       # Diese Datei
```

### Script-Funktionen

| Script | Zweck | Besonderheiten |
|--------|-------|----------------|
| `autoclicker_gui.py` | Haupt-GUI | 3 Tabs, Live-Logs, Config-Editor, Custom Buttons |
| `debug_autoclicker.py` | Hold-Modus | Auto-Cleanup alter Prozesse, Verbose-Logging |
| `roblox_autoclicker_toggle.py` | Toggle-Modus | Ein/Aus-Schalter, gleiche Features wie Hold |
| `web_controller.py` | Web-UI | Port 8080, Smart Logging, Auto-Restart |

### Technische Details

**GUI (autoclicker_gui.py)**
- **Framework**: tkinter
- **Tabs**: ttk.Notebook mit 3 Tabs
- **Custom Buttons**: Frame+Label statt tk.Button (macOS Theme-Workaround)
- **Button States**: Dynamisches `button_enabled` Attribut
- **Subprocess**: Unbuffered Output (`python3 -u`, `PYTHONUNBUFFERED=1`, `bufsize=0`)
- **Threading**: Daemon-Thread für Output-Lesen
- **Process Management**: SIGTERM → SIGKILL → direct kill() Fallbacks

**Autoclicker Scripts**
- **Auto-Cleanup**: Killt alte Prozesse beim Start (`pgrep -f`, `kill -9`)
- **Exit Handling**: ESC auf press (nicht release), Ctrl+C try/except
- **Verbose Logging**: Millisekunden-Timestamps, Position, Key
- **Config Hot-Reload**: Lädt config.yaml bei jedem Start

**Web Controller**
- **Framework**: Flask
- **Smart Logging**: Keine `/api/status` Spam-Logs
- **Auto-Restart**: Neustart bei Config-Änderung
- **Port Management**: Auto-Kill von Prozessen auf Port 8080

## ✅ Aktueller Status

### Was funktioniert

✅ GUI mit allen Features (Start/Stop/Clear Logs)
✅ Farbige Buttons (Grün für Start, Rot für Stop, Blau für Clear)
✅ Button States (disabled/enabled) funktionieren korrekt
✅ Hold- und Toggle-Modi
✅ Verbose-Logging mit Millisekunden-Timestamps
✅ Live-Log-Anzeige in GUI (Echtzeit)
✅ Klick-Test-Bereich mit CPS-Messung
✅ Config-Editor in GUI
✅ Web-Interface
✅ Auto-Cleanup von Duplikat-Prozessen
✅ ESC und Ctrl+C zum Beenden
✅ Prozess-Terminierung mit Fallbacks

### Letzte Fixes (Stand: 2025-12-25)

**Button Color Fix (Commit: 08be3f4)**
- Problem: macOS Tkinter überschreibt tk.Button Farben
- Lösung: Custom Buttons mit Frame+Label statt tk.Button
- Ergebnis: Buttons zeigen korrekte Farben (Grün/Rot/Blau)

**Button Functionality Fix (Commit: 27fed45)**
- Problem: Stop-Button war nicht klickbar (state in Closure gefangen)
- Lösung: `button_enabled` als Frame-Attribut statt Closure-Variable
- Ergebnis: Alle Buttons funktionieren korrekt

**Process Termination Fix (Commit: 27fed45)**
- Problem: Stop-Button konnte Prozesse nicht zuverlässig beenden
- Lösung: Mehrere Fallbacks (SIGTERM → SIGKILL → direct kill)
- Ergebnis: Prozesse werden zuverlässig gestoppt

**Click Test Timer Auto-Pause (Commit: be9b579)**
- Problem: Dauer-Zähler lief nach dem ersten Klick ewig weiter
- Lösung: Auto-Pause nach 3 Sekunden Inaktivität
- Ergebnis: Timer friert automatisch ein wenn nicht mehr geklickt wird

## 🐛 Bekannte Issues

### macOS .app Bundle

**Status**: Funktioniert NICHT zuverlässig

**Problem**:
- System-Python hat keine Module (yaml fehlt)
- Launcher kann Module nicht automatisch installieren

**Workaround**:
Nutze `./start_gui.sh` statt der .app

**Datei**: `create_app.sh` erstellt die .app, aber nicht empfohlen

### Mögliche zukünftige Verbesserungen

- [ ] Position-Picker in GUI (Click to set position)
- [ ] Preset-Profile (speichere/lade verschiedene Configs)
- [ ] Statistiken (Total clicks, Uptime, Average CPS)
- [ ] Hotkey-Recorder (beliebige Tasten aufnehmen)
- [ ] .app Bundle mit PyInstaller (eigenständige Binary)

## 🔐 Sicherheit

⚠️ **WICHTIG**: Dieser Autoclicker ist für persönliche/private Nutzung gedacht.

- Roblox kann Autoclicker erkennen
- Verwendung kann gegen ToS verstoßen
- Kein Anti-Cheat-Bypass eingebaut
- Nur für Testzwecke/Entwicklung verwenden

## 📝 Git Repository

```bash
# Repository klonen
git clone https://github.com/whaeuser/RobloxAutoclicker.git

# Status prüfen
git status

# Änderungen committen
git add .
git commit -m "Beschreibung"
git push
```

## 🎯 Nächste Session: Wo weitermachen?

### ✅ Zuletzt erfolgreich abgeschlossen

1. **GUI komplett funktionsfähig**
   - Start/Stop/Clear Buttons funktionieren
   - Farbige Buttons (Grün/Rot/Blau) werden korrekt angezeigt
   - Button States (enabled/disabled) funktionieren
   - Live-Logs werden in Echtzeit angezeigt

2. **Prozess-Management robust**
   - Auto-Cleanup von alten Prozessen beim Start
   - Zuverlässiges Stoppen mit Fallback-Mechanismen
   - Keine Duplikat-Prozesse mehr

3. **Alle Features implementiert**
   - Hold- und Toggle-Modi
   - Verbose-Logging
   - Config-Editor
   - Klick-Test

### 📂 Wichtige Dateien für die nächste Session

| Datei | Zweck | Wann bearbeiten |
|-------|-------|-----------------|
| `autoclicker_gui.py` | Haupt-GUI | Für GUI-Features/Fixes |
| `debug_autoclicker.py` | Hold-Modus Backend | Für Click-Logik (Hold) |
| `roblox_autoclicker_toggle.py` | Toggle-Modus Backend | Für Click-Logik (Toggle) |
| `config.yaml` | Zentrale Config | Für neue Config-Optionen |
| `README.md` | Dokumentation | Für Doku-Updates |

### 🔧 Wenn Probleme auftreten

**GUI startet nicht:**
```bash
# Prüfe tkinter
python3 -c "import tkinter"

# Install wenn fehlt
brew install python-tk@3.11
```

**Keine Klicks / "This process is not trusted":**
```
System Settings → Privacy & Security → Accessibility
→ Füge Python/Terminal hinzu
```

**Port 8080 belegt (Web-Interface):**
```bash
# Automatisch: Script killt alte Prozesse
./start_web_controller.sh

# Manuell
lsof -ti:8080 | xargs kill -9
```

**Mehrere Autoclicker laufen gleichzeitig:**
```bash
# Sollte nicht passieren (Auto-Cleanup)
# Manuell stoppen:
pkill -f autoclicker
ps aux | grep -i autoclicker
```

**Verbose Logs erscheinen nicht in GUI:**
```
Bereits gefixt! Subprocess nutzt:
- python3 -u flag
- PYTHONUNBUFFERED=1
- bufsize=0
```

### 🚀 Mögliche nächste Features

**Einfach:**
1. Position-Picker Button in GUI (klicke um Position zu setzen)
2. Preset-Profile speichern/laden
3. Statistiken-Tab (Total Clicks, Uptime, Average CPS)

**Mittel:**
4. Hotkey-Recorder für beliebige Tasten
5. Mehrere Klick-Positionen (Rotation)
6. Click-Pattern-Editor (z.B. Klick-Pause-Klick)

**Komplex:**
7. PyInstaller .app Bundle (eigenständige Binary)
8. Auto-Update-Funktion
9. Cloud-Config-Sync

### 📊 Debugging & Logs

```bash
# GUI Logs (wenn über .app gestartet)
tail -f /tmp/roblox_autoclicker_gui.log

# Laufende Prozesse prüfen
ps aux | grep -i autoclicker

# Ports prüfen
lsof -i :8080

# Git Status
git status
git log --oneline -5
```

### 💡 Tipps für die nächste Session

1. **Immer zuerst testen**: `./start_gui.sh` ausführen
2. **Config prüfen**: `cat config.yaml` für aktuelle Einstellungen
3. **Git Status**: `git status` für ungespeicherte Änderungen
4. **README lesen**: Diese Datei ist aktuell! (Stand: 2025-12-25)

### 🎓 Code-Architektur verstehen

**Custom Button System:**
```python
# autoclicker_gui.py:76-114
def create_custom_button(...):
    # Frame als Button-Container
    frame.button_enabled = True  # Dynamischer State
    frame.normal_color = bg_color
    frame.hover_color = hover_color

    # Click-Handler prüft frame.button_enabled
    def on_click(e):
        if frame.button_enabled:
            command()
```

**Button State Management:**
```python
# autoclicker_gui.py:477-485 (start)
self.start_btn_frame.button_enabled = False  # Deaktivieren
self.stop_btn_frame.button_enabled = True    # Aktivieren

# autoclicker_gui.py:509-517 (stop)
self.start_btn_frame.button_enabled = True   # Reaktivieren
self.stop_btn_frame.button_enabled = False   # Deaktivieren
```

**Prozess-Cleanup:**
```python
# debug_autoclicker.py / roblox_autoclicker_toggle.py
result = subprocess.run(['pgrep', '-f', 'autoclicker'], ...)
for pid in pids:
    if pid != current_pid:
        os.system(f"kill -9 {pid}")
```

---

**Version**: 1.5
**Letztes Update**: 2025-12-25
**Autor**: whaeuser
**Repository**: https://github.com/whaeuser/RobloxAutoclicker

**Status**: ✅ Voll funktionsfähig
