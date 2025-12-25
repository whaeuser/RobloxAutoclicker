# Web Controller - Anleitung

Der Web Controller ermöglicht die Steuerung des Autoclickers über ein Browser-Interface.

## Installation

### 1. Flask installieren

```bash
pip3 install flask pyyaml
```

Oder alle Dependencies auf einmal:

```bash
pip3 install flask pynput pyautogui pyyaml
```

### 2. Web Controller starten

```bash
./scripts/start_web_controller.sh
```

Oder manuell:

```bash
python3 web_controller.py
```

### 3. Browser öffnen

Öffne im Browser:

```
http://localhost:8080
```

## Features

### 🎮 Status & Steuerung

- **Start-Button** - Startet den Autoclicker im Hintergrund
- **Stop-Button** - Stoppt den laufenden Autoclicker
- **Status-Anzeige** - Zeigt ob Autoclicker läuft (grün) oder gestoppt (rot)
- **Hinweise** - Bedienungsanleitung direkt im Interface

### ⚙️ Konfiguration

Alle Config-Parameter können direkt im Browser bearbeitet werden:

- **CPS (Clicks per Second)** - 1-1000, Slider mit Empfehlung
- **Hotkey** - Dropdown mit allen verfügbaren Tasten
- **Klick-Modus** - Fast, Standard, Separate, Right
- **Position X/Y** - Optional für feste Klick-Position

**Speichern** - Schreibt direkt in `config.yaml`

### 🎯 Klick-Test

Integrierter Klick-Test zum Testen:

- **Großer Kreis** - Klick-Bereich zum Testen
- **Aktuelle CPS** - Zeigt CPS der letzten Sekunde
- **Durchschnitt CPS** - Durchschnitt seit Start
- **Gesamt Klicks** - Zähler aller Klicks
- **Dauer** - Zeit seit erstem Klick

## Verwendung

### Workflow

1. **Browser öffnen** - Gehe zu `http://localhost:8080`
2. **Config anpassen** - Stelle CPS, Hotkey, etc. ein
3. **Speichern** - Klicke "Konfiguration speichern"
4. **Starten** - Klicke "Starten"
5. **In Spiel wechseln** - Wechsle zu deinem Spiel
6. **Shift halten** - (oder dein konfigurierter Hotkey)
7. **Stoppen** - Zurück zum Browser, klicke "Stoppen"

### Klick-Test verwenden

1. **Maus über Kreis** - Bewege Maus über den großen Kreis
2. **Shift halten** - Halte Hotkey gedrückt (während Autoclicker läuft)
3. **CPS beobachten** - Schau wie viele CPS du erreichst
4. **Reset** - Klicke "Test zurücksetzen" für neuen Test

## API-Endpunkte

Der Web Controller bietet folgende REST-API:

### GET /api/config
Lädt die aktuelle Konfiguration

**Response:**
```json
{
  "clicks_per_second": 12,
  "hotkey": "shift",
  "click_mode": "fast",
  "target_position": null,
  "enable_logging": true
}
```

### POST /api/config
Speichert eine neue Konfiguration

**Request Body:**
```json
{
  "clicks_per_second": 20,
  "hotkey": "f6",
  "click_mode": "fast",
  "target_position": [500, 300],
  "enable_logging": true
}
```

**Response:**
```json
{
  "success": true
}
```

### POST /api/start
Startet den Autoclicker

**Response:**
```json
{
  "success": true
}
```

### POST /api/stop
Stoppt den Autoclicker

**Response:**
```json
{
  "success": true
}
```

### GET /api/status
Gibt Status zurück

**Response:**
```json
{
  "running": true
}
```

## Netzwerk-Zugriff

### Lokal (Standard)
```
http://localhost:8080
```

### Von anderem Gerät im Netzwerk

1. **IP-Adresse herausfinden:**
```bash
ipconfig getifaddr en0  # macOS
```

2. **Im Browser des anderen Geräts:**
```
http://192.168.x.x:8080
```

**Hinweis:** Firewall muss Port 8080 freigeben!

## Troubleshooting

### "Address already in use"

**Problem:** Port 8080 wird bereits verwendet

**Lösung 1 - Anderen Port:**

Ändere in `web_controller.py` Zeile 675:
```python
app.run(host='0.0.0.0', port=9090, debug=False)  # Statt 8080
```

**Lösung 2 - Prozess beenden:**
```bash
lsof -ti:8080 | xargs kill -9
```

### "Module 'flask' not found"

**Problem:** Flask nicht installiert

**Lösung:**
```bash
pip3 install flask
```

### Autoclicker startet nicht über Web-Interface

**Mögliche Ursachen:**

1. **Berechtigungen fehlen** - Python braucht Accessibility
2. **debug_autoclicker.py nicht gefunden** - Muss im gleichen Ordner sein
3. **Dependencies fehlen** - pynput, pyautogui nicht installiert

**Diagnose:**
Schaue in Terminal wo `web_controller.py` läuft - dort erscheinen Fehler.

### Config-Änderungen werden nicht übernommen

**Problem:** Autoclicker muss neu gestartet werden nach Config-Änderung

**Lösung:**
1. Klicke "Stoppen"
2. Ändere Config
3. Klicke "Speichern"
4. Klicke "Starten"

## Sicherheit

### Wichtig!

- **Nur im lokalen Netzwerk verwenden**
- Keine Authentifizierung implementiert
- Jeder mit Zugriff auf Port 8080 kann Autoclicker steuern

### Für Production

Füge Authentifizierung hinzu (nicht im Scope dieses Projekts):
- Basic Auth
- Token-basiert
- OAuth

## Erweiterte Nutzung

### Custom Port

```bash
python3 web_controller.py --port 8080
```

Oder ändere direkt in `web_controller.py`.

### Als Service

Erstelle macOS Launch Agent (fortgeschritten):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.autoclicker.webcontroller</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/whaeuser/Entwicklung/AutoinputAutoclicker/web_controller.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Speichere in `~/Library/LaunchAgents/com.autoclicker.webcontroller.plist`

## Vorteile gegenüber CLI

| Feature | CLI | Web Controller |
|---------|-----|----------------|
| **Config bearbeiten** | Texteditor, Neustart | Browser, live |
| **Starten/Stoppen** | Terminal-Befehle | Button-Klick |
| **Status sehen** | Terminal-Output | Visueller Indikator |
| **Klick-Test** | Separates HTML | Integriert |
| **Fernsteuerung** | Nicht möglich | Über Netzwerk |
| **Multi-User** | Schwierig | Browser von jedem Gerät |

## Deinstallation

Einfach löschen:

```bash
rm web_controller.py
rm start_web_controller.sh
```

Flask behalten oder deinstallieren:

```bash
pip3 uninstall flask
```

## Support

Bei Problemen:
- Prüfe Terminal-Output von `web_controller.py`
- Schaue Browser-Konsole (F12) für Frontend-Fehler
- Lese [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
