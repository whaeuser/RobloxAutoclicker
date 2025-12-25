# Autoinput - Installation

## Installation auf dem Entwicklungs-Mac

### Option 1: Python-Skript direkt ausführen

**Toga GUI (Production, Empfohlen):**
```bash
# Mit Startskript
./scripts/start_autoinput_gui.sh

# Oder direkt mit Python
python3 src/autoinput_gui_toga.py
```

**Tkinter GUI (Legacy):**
```bash
./scripts/start_autoinput_gui_tkinter.sh
```

### Option 2: Standalone macOS App verwenden

```bash
# App direkt öffnen
open "build/autoinput/macos/app/Autoinput.app"
```

---

## Installation auf einem anderen Mac

Die App verwendet eine Ad-hoc-Signatur und benötigt daher eine manuelle Freigabe beim ersten Start.

### Schritt 1: DMG übertragen

Kopiere die Datei `dist/Autoinput-1.5.0.dmg` auf den Ziel-Mac.

### Schritt 2: Installation

**Option A - Mit Terminal (Empfohlen):**

```bash
# 1. DMG öffnen
open "Autoinput-1.5.0.dmg"

# 2. App in Applications-Ordner ziehen (im Finder-Fenster das erscheint)

# 3. Sicherheitsattribute entfernen
xattr -cr "/Applications/Autoinput.app"

# 4. App starten
open "/Applications/Autoinput.app"
```

**Option B - Ohne Terminal:**

1. DMG-Datei doppelklicken
2. Im geöffneten Fenster die App "Autoinput" in den "Applications"-Ordner ziehen
3. **Rechtsklick** auf "Autoinput.app" → "Öffnen" wählen
4. Im Sicherheitsdialog auf "Öffnen" klicken
5. Ab jetzt funktioniert auch normales Doppelklicken

### Schritt 3: Erste Nutzung

Beim ersten Start:
- Die App öffnet sich mit der Standard-Konfiguration
- Unter "⚙️ Konfiguration" kannst du die Einstellungen anpassen:
  - **CPS**: Klicks pro Sekunde (Standard: 12)
  - **Hotkey**: Taste zum Aktivieren (Standard: shift)
  - **Modus**: Hold (halten) oder Toggle (ein/aus)
  - **Verbose**: Debug-Modus für detaillierte Logs

---

## Funktionen

### ⚡ Steuerung & Logs
- **Starten/Stoppen**: Autoclicker-Prozess verwalten
- **Logs aktualisieren**: Neue Log-Einträge vom Autoclicker anzeigen
- **Live-Status**: Zeigt ob der Autoclicker aktiv ist

### ⚙️ Konfiguration
- **CPS**: 1-1000 Klicks pro Sekunde
- **Hotkey**: Verschiedene Tasten zur Auswahl
- **Aktivierungsmodus**:
  - **Hold**: Autoclicker aktiv solange Taste gedrückt
  - **Toggle**: Ein/Aus beim Tastendruck
- **Verbose-Modus**: Zeigt jeden einzelnen Klick im Log

### 🎯 Klick-Test
- Teste deine eigene Clicking-Geschwindigkeit
- Zeigt aktuelle und durchschnittliche CPS
- Perfekt zum Vergleichen mit dem Autoclicker

---

## Systemanforderungen

- macOS 11.0 (Big Sur) oder neuer
- Für Python-Version: Python 3.8+
- Erforderliche Berechtigungen:
  - **Bedienungshilfen**: Für Tastatur/Maus-Steuerung
  - **Bildschirmaufnahme**: Für Position-Erkennung (optional)

### Berechtigungen einrichten

Beim ersten Start fragt macOS nach Berechtigungen:

1. **Systemeinstellungen** → **Sicherheit** → **Datenschutz**
2. **Bedienungshilfen** aktivieren für "Autoinput"
3. Falls nötig: **Bildschirmaufnahme** ebenfalls aktivieren

---

## Deinstallation

```bash
# App löschen
rm -rf "/Applications/Autoinput.app"

# Optional: Log-Dateien löschen
rm -f /tmp/autoinput_toga.log
```

---

## Troubleshooting

### "App kann nicht geöffnet werden, da sie von einem nicht verifizierten Entwickler stammt"

**Lösung:**
```bash
xattr -cr "/Applications/Autoinput.app"
```

Oder: Rechtsklick → "Öffnen" statt Doppelklick

### App startet nicht / stürzt sofort ab

**Lösung:**
1. Prüfe ob alle Berechtigungen erteilt sind (Bedienungshilfen)
2. Prüfe die Logs in der Konsole.app nach Fehlern
3. Versuche die Python-Version direkt zu starten (siehe oben)

### Autoclicker reagiert nicht auf Hotkey

**Lösung:**
1. Stelle sicher dass die App läuft (Status: "🟢 Läuft")
2. Prüfe ob die richtige Taste konfiguriert ist
3. Klicke "🔄 Logs aktualisieren" um zu sehen ob Tastendrücke erkannt werden
4. Aktiviere Verbose-Modus zum Debuggen

### Logs werden nicht angezeigt

**Lösung:**
- Klicke auf "🔄 Logs aktualisieren" Button
- Logs werden manuell aktualisiert, nicht automatisch
- Bei Verbose-Modus sollten alle Klicks sichtbar sein

---

## Entwicklung & Build

### Neue App-Version erstellen

```bash
# Dependencies installieren
pip3 install briefcase toga

# App-Struktur erstellen
briefcase create

# App bauen
briefcase build

# DMG-Installer erstellen
briefcase package --adhoc-sign

# Ergebnis: dist/Autoinput-1.5.0.dmg
```

### Projekt-Struktur

```
Autoinput/
├── src/                         # Python-Quellcode
│   ├── autoinput.py             # Haupt-Autoclicker
│   ├── autoinput_toggle.py      # Toggle-Modus
│   ├── debug_autoinput.py       # Debug/Hold-Modus
│   ├── autoinput_gui_toga.py    # Toga GUI (Production)
│   ├── autoinput_gui_tkinter.py # Tkinter GUI (Legacy)
│   └── web_controller.py        # Web-Interface
├── scripts/                     # Shell-Skripte
│   ├── start_autoinput_gui.sh       # Toga GUI (Haupt)
│   ├── start_autoinput_gui_tkinter.sh # Tkinter GUI (Legacy)
│   ├── start_web_controller.sh
│   ├── run_autoinput.sh
│   ├── run_toggle.sh
│   └── setup.sh
├── docs/                        # Dokumentation
│   ├── INSTALLATION.md
│   ├── QUICKSTART.md
│   ├── TROUBLESHOOTING.md
│   └── ...
├── autoinput/                   # Briefcase Package
│   ├── __init__.py
│   ├── __main__.py              # Toga GUI für App
│   ├── debug_autoinput.py       # Hold-Modus Script
│   ├── autoinput_toggle.py      # Toggle-Modus Script
│   └── config.yaml              # Konfiguration
├── config.yaml                  # Projekt-Konfiguration
├── pyproject.toml               # Briefcase-Konfiguration
├── README.md                    # Hauptdokumentation
├── build/                       # Build-Artifacts (nicht versioniert)
└── dist/                        # DMG-Installer (nicht versioniert)
```

---

## Lizenz

MIT License - Siehe LICENSE-Datei für Details

## Support

Bei Problemen oder Fragen öffne ein Issue auf GitHub:
https://github.com/whaeuser/Autoinput/issues
