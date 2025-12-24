# Konfigurationsdokumentation

Die `config.yaml` Datei steuert das Verhalten des Autoclickers. Alle Einstellungen können ohne Code-Änderungen angepasst werden.

## Vollständige Beispiel-Konfiguration

```yaml
# Klicks pro Sekunde
clicks_per_second: 12

# Aktivierungs-Hotkey
hotkey: shift

# Klick-Position
target_position: null

# Logging aktivieren
enable_logging: true

# Klick-Modus
click_mode: fast
```

---

## Parameter-Referenz

### `clicks_per_second`

**Typ:** Integer (1-1000)
**Standard:** 12
**Beschreibung:** Anzahl der Klicks pro Sekunde (CPS)

**Beispiele:**
```yaml
clicks_per_second: 8    # Langsam - für Idle-Games
clicks_per_second: 12   # Mittel - Standard
clicks_per_second: 20   # Schnell - für Action-Games
clicks_per_second: 100  # Sehr schnell - kann erkannt werden
```

**Empfehlungen:**
- **1-10 CPS:** Unauffällig, sieht natürlich aus
- **11-20 CPS:** Standard für die meisten Spiele
- **21-50 CPS:** Schnell, könnte auffallen
- **50+ CPS:** Sehr schnell, hohes Risiko erkannt zu werden

**Technisch:** Der Klick-Intervall wird berechnet als `1.0 / clicks_per_second`
Bei 12 CPS: `1.0 / 12 = 0.0833` Sekunden zwischen Klicks

---

### `hotkey`

**Typ:** String
**Standard:** `shift`
**Beschreibung:** Taste zum Aktivieren/Deaktivieren des Autoclickers

**Verfügbare Werte:**

#### Modifier-Tasten
```yaml
hotkey: shift       # Linke Shift-Taste (Standard)
hotkey: shift_r     # Rechte Shift-Taste
hotkey: ctrl        # Linke Strg-Taste (Ctrl)
hotkey: ctrl_r      # Rechte Strg-Taste
hotkey: alt         # Linke Alt-Taste
hotkey: alt_r       # Rechte Alt-Taste
```

#### Andere Tasten
```yaml
hotkey: space       # Leertaste
hotkey: tab         # Tab-Taste
hotkey: caps_lock   # Caps Lock
```

#### Funktionstasten
```yaml
hotkey: f1          # F1-Taste
hotkey: f2          # F2-Taste
# ... bis f12
hotkey: f12         # F12-Taste
```

**Empfehlungen:**
- **shift** - Gut für FPS/Action-Games (oft Sprint)
- **space** - Gut wenn Shift anderweitig gebraucht wird
- **f6-f12** - Funktionstasten, meist unbelegt
- **alt** - Alternative zu Shift

**Hinweis:** Die Exit-Taste (ESC) kann nicht geändert werden.

---

### `target_position`

**Typ:** `null` oder Array `[x, y]`
**Standard:** `null`
**Beschreibung:** Position, an der geklickt werden soll

**Optionen:**

#### Dynamische Position (Standard)
```yaml
target_position: null
```
Klickt an der aktuellen Mausposition. Die Maus kann frei bewegt werden.

#### Feste Position
```yaml
target_position: [500, 300]
```
Klickt immer an Pixel-Koordinate X=500, Y=300 (von oben links).

**Position herausfinden:**

Methode 1 - Python:
```bash
python3 -c "import pyautogui; print(pyautogui.position())"
```

Methode 2 - Im Code:
```python
import pyautogui
print(pyautogui.position())
# Zeigt: Point(x=123, y=456)
```

Methode 3 - Screenshot-Tool:
Bewege die Maus zur gewünschten Position und lese Koordinaten aus macOS Screenshot-Tool.

**Verwendungszwecke:**
- **null** - Für Spiele wo du die Maus bewegst
- **Feste Position** - Für Idle-Games mit festen Buttons
- **Feste Position** - Für automatisierte Aufgaben

**Beispiele:**
```yaml
# Minecraft: Klicke in Bildschirmmitte
target_position: [960, 540]  # Bei 1920x1080

# Idle-Game: Klicke auf "Collect"-Button
target_position: [650, 400]

# Cookie Clicker: Klicke auf Cookie
target_position: [512, 384]
```

**Koordinatensystem:**
- **X-Achse:** Links (0) → Rechts (Bildschirmbreite)
- **Y-Achse:** Oben (0) → Unten (Bildschirmhöhe)
- **Ursprung:** Oben links (0, 0)

---

### `enable_logging`

**Typ:** Boolean (`true` oder `false`)
**Standard:** `true` (im Debug-Modus)
**Beschreibung:** Aktiviert/Deaktiviert Konsolen-Ausgaben

**Optionen:**

```yaml
enable_logging: true   # Zeigt jeden Klick in der Konsole
enable_logging: false  # Keine Ausgabe (bessere Performance)
```

**Hinweis:** Im `debug_autoclicker.py` ist Logging immer aktiv (`FORCE_LOGGING = True`).

**Was wird geloggt:**
- Jeder Tastendruck/Loslassen
- Aktivierung/Deaktivierung des Clickings
- Jeder einzelne Klick mit Position und Nummer
- Fehler und Warnungen
- System-Events (Worker-Start/Stop)

**Beispiel-Output:**
```
[12:34:56] [KEY] Taste gedrückt: Key.shift
[12:34:56] [STATUS] 🟢 CLICKING AKTIVIERT!
[12:34:56] [CLICK] Klick #1 an aktueller Position Point(x=500, y=300)
[12:34:56] [CLICK] Klick #2 an aktueller Position Point(x=501, y=300)
[12:34:57] [KEY] Taste losgelassen: Key.shift
[12:34:57] [STATUS] 🔴 CLICKING DEAKTIVIERT!
```

---

### `click_mode`

**Typ:** String
**Standard:** `fast`
**Beschreibung:** Definiert wie Klicks ausgeführt werden

#### Modi im Detail:

##### `fast` (Empfohlen)
```yaml
click_mode: fast
```

**Funktionsweise:** `pyautogui.click(duration=0)`
**Eigenschaften:**
- Keine künstliche Verzögerung
- Schnellste PyAutoGUI-Methode
- Am besten für die meisten Anwendungsfälle
- Stabil und zuverlässig

**Verwendung:** Standard für alle Spiele

---

##### `standard`
```yaml
click_mode: standard
```

**Funktionsweise:** `pyautogui.click()` (mit Standard-Pause)
**Eigenschaften:**
- Kleine Pause zwischen Events (pyautogui.PAUSE)
- Langsamer als `fast`
- Kompatibilitätsmodus

**Verwendung:** Wenn `fast` Probleme macht

---

##### `separate`
```yaml
click_mode: separate
```

**Funktionsweise:** Separate `mouseDown()` und `mouseUp()` Aufrufe
**Eigenschaften:**
- Simuliert echte Maus-Events genauer
- Theoretisch schneller als `fast`
- Kann von manchen Apps besser erkannt werden

**Verwendung:**
- Maximale Geschwindigkeit gewünscht
- Apps die separate Events benötigen

**Technisch:**
```python
pyautogui.mouseDown(button='left')
pyautogui.mouseUp(button='left')
```

---

##### `right`
```yaml
click_mode: right
```

**Funktionsweise:** `pyautogui.click(button='right', duration=0)`
**Eigenschaften:**
- Rechtsklick statt Linksklick
- Gleiche Geschwindigkeit wie `fast`

**Verwendung:**
- Spiele die Rechtsklick-Spam benötigen
- Kontextmenü-Automatisierung
- Spezielle Anwendungsfälle

---

## Erweiterte Konfigurationen

### High-Speed Gaming (FPS/Action)

```yaml
clicks_per_second: 20
hotkey: shift
target_position: null
enable_logging: false
click_mode: fast
```

**Grund:** 20 CPS, dynamische Position, kein Logging-Overhead

---

### Idle/Clicker Games

```yaml
clicks_per_second: 15
hotkey: space
target_position: [640, 360]
enable_logging: true
click_mode: fast
```

**Grund:** Mittelschnell, feste Position auf Button, Logging zum Debuggen

---

### Unauffälliges Clicking

```yaml
clicks_per_second: 8
hotkey: f6
target_position: null
enable_logging: false
click_mode: standard
```

**Grund:** Niedrige CPS sieht natürlich aus, F6 fällt nicht auf

---

### Maximale Geschwindigkeit

```yaml
clicks_per_second: 100
hotkey: shift
target_position: [500, 300]
enable_logging: false
click_mode: separate
```

**Grund:** 100 CPS mit separate Events, feste Position, kein Logging

**Warnung:** Sehr hohe CPS können von Anti-Cheat-Systemen erkannt werden!

---

## Position herausfinden - Schritt für Schritt

### Methode 1: Python One-Liner

1. Positioniere Maus auf gewünschter Stelle
2. Führe aus:
```bash
python3 -c "import pyautogui; import time; time.sleep(3); print(pyautogui.position())"
```
3. Du hast 3 Sekunden um die Maus zu positionieren
4. Koordinaten werden ausgegeben: `Point(x=123, y=456)`
5. Trage in config.yaml ein: `target_position: [123, 456]`

### Methode 2: Interaktives Python-Skript

Erstelle `get_position.py`:
```python
import pyautogui
import time

print("Bewege Maus zur gewünschten Position...")
print("Position wird in 5 Sekunden erfasst...")

for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)

pos = pyautogui.position()
print(f"\nPosition: {pos}")
print(f"\nKonfiguration:\ntarget_position: [{pos.x}, {pos.y}]")
```

Führe aus:
```bash
python3 get_position.py
```

---

## YAML-Syntax-Hinweise

### Gültige Formate

```yaml
# Integer/Zahlen (ohne Anführungszeichen)
clicks_per_second: 12

# Strings (mit oder ohne Anführungszeichen)
hotkey: shift
hotkey: "shift"
hotkey: 'shift'

# Boolean (ohne Anführungszeichen)
enable_logging: true
enable_logging: false

# null (ohne Anführungszeichen)
target_position: null

# Arrays (eckige Klammern)
target_position: [500, 300]

# Kommentare (mit #)
# Das ist ein Kommentar
clicks_per_second: 12  # Kommentar am Zeilenende
```

### Häufige Fehler

#### Falsch:
```yaml
clicks_per_second: "12"      # String statt Integer
target_position: 500, 300    # Fehlende Klammern
hotkey: Shift                # Großbuchstabe (muss klein sein)
enable_logging: True         # Großgeschrieben (muss klein sein)
```

#### Richtig:
```yaml
clicks_per_second: 12
target_position: [500, 300]
hotkey: shift
enable_logging: true
```

---

## Konfiguration testen

Nach Änderungen:

1. **Syntax prüfen:**
```bash
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
```
Keine Ausgabe = Syntax OK

2. **Mit Debug-Modus starten:**
```bash
python3 debug_autoclicker.py
```
Prüfe ob Config korrekt geladen wird

3. **Log-Ausgabe prüfen:**
```
[HH:MM:SS] [SUCCESS] Config geladen: {'clicks_per_second': 12, ...}
```

---

## Troubleshooting

### Config wird nicht geladen

**Fehlermeldung:** `Config-Datei nicht gefunden!`

**Lösung:**
- Prüfe ob `config.yaml` im selben Ordner wie `debug_autoclicker.py` liegt
- Dateiname muss exakt `config.yaml` sein (nicht `config.yml` oder `Config.yaml`)

### YAML Syntax-Fehler

**Fehlermeldung:** `yaml.scanner.ScannerError`

**Lösung:**
- Prüfe Einrückungen (nur Leerzeichen, keine Tabs)
- Prüfe Klammern bei Arrays
- Prüfe Anführungszeichen
- Validiere mit: `python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"`

### Hotkey funktioniert nicht

**Mögliche Ursachen:**
- Tippfehler in Hotkey-Name (muss klein geschrieben sein)
- Hotkey wird von anderem Programm abgefangen
- Accessibility-Berechtigung fehlt

**Lösung:**
- Prüfe Schreibweise in [Hotkey-Referenz](#hotkey)
- Teste mit anderem Hotkey (z.B. `f6`)
- Prüfe Berechtigungen (siehe INSTALL.md)

---

## Best Practices

1. **Starte mit Defaults** - Ändere nur was du brauchst
2. **Teste nach Änderungen** - Immer mit Debug-Modus testen
3. **Sichere Config** - Kopiere `config.yaml` vor großen Änderungen
4. **Kommentiere** - Schreibe Kommentare für komplexe Setups
5. **Niedrige CPS** - Beginne mit niedriger CPS und erhöhe schrittweise

## Beispiel-Configs für verschiedene Spiele

### Minecraft (PvP)
```yaml
clicks_per_second: 15
hotkey: shift
target_position: null
enable_logging: false
click_mode: fast
```

### Cookie Clicker
```yaml
clicks_per_second: 20
hotkey: space
target_position: [512, 384]  # Anpassen!
enable_logging: true
click_mode: fast
```

### Allgemein (Testing)
```yaml
clicks_per_second: 5
hotkey: f6
target_position: null
enable_logging: true
click_mode: fast
```
