# Roblox Autoclicker

Ein konfigurierbarer Autoclicker für macOS mit Hotkey-Steuerung und Debug-Modus.

## Features

- **Konfigurierbare CPS** - Stelle Klicks pro Sekunde (1-1000) ein
- **Hotkey-Steuerung** - Aktiviere/Deaktiviere mit einer Taste (Standard: Shift)
- **Flexible Klick-Modi** - Fast, Standard, Separate Events, Rechtsklick
- **Feste oder dynamische Position** - Klicke an Mausposition oder fester Koordinate
- **Debug-Modus** - Ausführliches Logging für Fehlersuche
- **YAML-Konfiguration** - Einfache Anpassung ohne Code-Änderung

## Schnellstart

### Option 1: Web Controller (Empfohlen!)

```bash
# Dependencies installieren
pip3 install flask pynput pyautogui pyyaml

# Web Controller starten
./start_web_controller.sh

# Browser öffnen
open http://localhost:8080
```

**Vorteile:**
- Config im Browser anpassen
- Start/Stop per Klick
- Integrierter Klick-Test
- Keine Terminal-Befehle nötig

Siehe [WEB_CONTROLLER.md](WEB_CONTROLLER.md) für Details.

---

### Option 2: Kommandozeile (CLI)

```bash
# Dependencies installieren
pip3 install pynput pyautogui pyyaml

# Oder mit Setup-Skript
./setup.sh
```

### 2. Berechtigungen erteilen

**Wichtig:** Python benötigt Accessibility-Berechtigung!

1. Öffne **Systemeinstellungen** → **Datenschutz & Sicherheit** → **Bedienungshilfen**
2. Klicke auf das **Schloss** (Passwort eingeben)
3. Klicke auf **+** und füge hinzu:
   - Für System-Python: `/usr/local/bin/python3` (oder der Pfad von `which python3`)
   - Für venv: `/Users/whaeuser/Entwicklung/RobloxAutoclicker/venv/bin/python`
   - Oder füge **Terminal.app** / **iTerm.app** selbst hinzu

### 3. Starten

```bash
# Mit System-Python (empfohlen)
python3 debug_autoclicker.py

# Oder mit run-Skript
./run.sh

# Mit venv
source venv/bin/activate
python debug_autoclicker.py
```

## Verwendung

### Grundlegende Steuerung

1. **Starte das Programm** - Führe `python3 debug_autoclicker.py` aus
2. **Aktiviere Clicking** - Drücke und halte die **Shift-Taste** (oder deine konfigurierte Hotkey)
3. **Deaktiviere Clicking** - Lasse die **Shift-Taste** los
4. **Beende das Programm** - Drücke **ESC**

### Konfiguration anpassen

Bearbeite die `config.yaml` Datei:

```yaml
# Klicks pro Sekunde (1-1000)
clicks_per_second: 12

# Aktivierungs-Hotkey
hotkey: shift

# Klick-Position (null = aktuelle Mausposition)
target_position: null

# Oder feste Position
# target_position: [500, 300]

# Klick-Modus (fast, standard, separate, right)
click_mode: fast

# Logging aktivieren
enable_logging: true
```

Siehe [CONFIG.md](CONFIG.md) für alle Optionen.

## Klick-Modi

| Modus | Beschreibung | Verwendung |
|-------|--------------|------------|
| `fast` | PyAutoGUI Click ohne Verzögerung | Standard, empfohlen |
| `standard` | PyAutoGUI Click mit kleiner Pause | Kompatibilität |
| `separate` | Separate mouseDown/mouseUp Events | Maximale Geschwindigkeit |
| `right` | Rechtsklick statt Linksklick | Spezielle Anwendungsfälle |

## Verfügbare Hotkeys

```
shift, shift_r    - Shift-Tasten (links/rechts)
ctrl, ctrl_r      - Strg-Tasten (links/rechts)
alt, alt_r        - Alt-Tasten (links/rechts)
space             - Leertaste
tab               - Tab-Taste
caps_lock         - Caps Lock
f1 - f12          - Funktionstasten
```

## Projektstruktur

```
RobloxAutoclicker/
├── web_controller.py           # 🌐 Web-Interface (NEU!)
├── start_web_controller.sh     # Start-Skript für Web Controller
├── debug_autoclicker.py        # Hauptprogramm mit Debug-Logging
├── config.yaml                 # Konfigurationsdatei
├── setup.sh                    # Setup-Skript (erstellt venv)
├── run.sh                      # Start-Skript (System-Python)
├── click_test.html             # Einfache Klick-Test-Seite
├── README.md                   # Diese Datei
├── QUICKSTART.md               # ⚡ Kurzanleitung
├── WEB_CONTROLLER.md           # 🌐 Web Controller Dokumentation
├── INSTALL.md                  # Detaillierte Installationsanleitung
├── CONFIG.md                   # Konfigurationsdokumentation
├── CODE_DOCUMENTATION.md       # Code-Dokumentation
└── TROUBLESHOOTING.md          # Problemlösung
```

## Troubleshooting

### "This process is not trusted!"

Python hat keine Accessibility-Berechtigung. Siehe [INSTALL.md](INSTALL.md) Schritt 2.

### Keine Klicks

1. Prüfe ob Debug-Modus Klick-Meldungen zeigt
2. Stelle sicher dass die richtige Taste gedrückt wird
3. Prüfe `config.yaml` auf Syntaxfehler

### Dependencies fehlen

```bash
pip3 install pynput pyautogui pyyaml
```

Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md) für mehr Hilfe.

## Sicherheitshinweise

- **Nur für autorisierten Gebrauch** - Verwende dieses Tool nur in Spielen/Anwendungen, wo Autoclicker erlaubt sind
- **Keine Garantie** - Einige Spiele haben Anti-Cheat-Systeme
- **Eigenes Risiko** - Der Autor übernimmt keine Haftung

## Technische Details

- **Sprache:** Python 3.13+
- **Plattform:** macOS (Darwin)
- **Dependencies:** pynput, pyautogui, pyyaml
- **Threading:** Separater Worker-Thread für Klick-Events
- **Event-Handling:** pynput keyboard listener

## Lizenz

Dieses Projekt ist für Bildungs- und Testzwecke gedacht. Verwende es verantwortungsvoll.

## Support

Bei Problemen:
1. Lese [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Prüfe ob alle Dependencies installiert sind
3. Stelle sicher dass Berechtigungen korrekt gesetzt sind
4. Teste mit `python3 debug_autoclicker.py` für detailliertes Logging

## Changelog

### Version 1.0 (Debug)
- Initial Release mit Debug-Logging
- YAML-basierte Konfiguration
- Mehrere Klick-Modi
- Hotkey-Steuerung
- macOS Accessibility-Integration
