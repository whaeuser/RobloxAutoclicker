# Code-Dokumentation

Technische Dokumentation des Autoinput Codes.

## Datei-Übersicht

```
AutoinputAutoclicker/
├── debug_autoclicker.py    # Hauptprogramm (214 Zeilen)
├── config.yaml             # YAML-Konfiguration
├── setup.sh                # Setup-Skript für venv
├── run.sh                  # Start-Skript (System-Python)
└── run_autoclicker.sh      # Alternatives Start-Skript
```

---

## debug_autoclicker.py

### Architektur-Übersicht

Das Programm nutzt ein **Multi-Threading-Modell**:

```
Main Thread                 Worker Thread              Keyboard Listener
    │                            │                            │
    ├─ Config laden              │                            │
    ├─ Worker starten ──────────►│                            │
    ├─ Listener starten ─────────┼──────────────────────────►│
    │                            │                            │
    │                            │◄───── on_press() ──────────┤
    │                            │  (_clicking = True)        │
    │                            │                            │
    │                       ┌────▼────┐                       │
    │                       │ Klick!  │                       │
    │                       └────┬────┘                       │
    │                            │                            │
    │                            │◄───── on_release() ────────┤
    │                            │  (_clicking = False)       │
    │                            │                            │
    │                            │◄───── ESC ─────────────────┤
    │◄──── return False ─────────┴────────────────────────────┤
    │                                                          │
    └─ Programm beendet                                       │
```

### Imports und Abhängigkeiten

```python
import time           # Für sleep() und strftime()
import threading      # Für Worker-Thread
import sys            # Für sys.exit()
from pathlib import Path        # Für Pfad-Operationen
from pynput import keyboard     # Für Tastatur-Events
import pyautogui     # Für Maus-Klicks
import yaml          # Für Config-Datei
```

**Abhängigkeiten:**
- `pynput` - Keyboard Listener (Betriebssystem-Level)
- `pyautogui` - Maus-Steuerung und Klicks
- `pyyaml` - YAML-Parser für config.yaml

### Globale Konfiguration

```python
# PyAutoGUI Optimierungen
pyautogui.PAUSE = 0        # Keine automatische Pause
pyautogui.FAILSAFE = False # Failsafe deaktiviert

# Debug-Modus
FORCE_LOGGING = True       # Logging immer aktiviert
```

**Wichtig:**
- `PAUSE = 0` entfernt künstliche Verzögerungen
- `FAILSAFE = False` deaktiviert Ecken-Exit-Mechanismus
- `FORCE_LOGGING` überschreibt `enable_logging` aus Config

---

## Funktionen

### `log(msg, prefix="INFO")`

**Zweck:** Logging mit Zeitstempel

**Parameter:**
- `msg` (str) - Nachricht zum Loggen
- `prefix` (str) - Log-Level/Kategorie (Standard: "INFO")

**Ausgabe-Format:**
```
[HH:MM:SS] [PREFIX] Nachricht
```

**Verwendete Prefixes:**
- `INFO` - Allgemeine Informationen
- `SUCCESS` - Erfolgreiche Operationen
- `ERROR` - Fehler
- `WARNING` - Warnungen
- `KEY` - Tastatur-Events
- `STATUS` - Status-Änderungen (Clicking an/aus)
- `CLICK` - Klick-Events
- `WORKER` - Worker-Thread-Events
- `SYSTEM` - System-Events
- `EXIT` - Programm-Ende

**Code:**
```python
def log(msg, prefix="INFO"):
    """Immer loggen in Debug-Modus"""
    print(f"[{time.strftime('%H:%M:%S')}] [{prefix}] {msg}")
```

---

### `load_config()`

**Zweck:** Lädt und validiert config.yaml

**Rückgabe:** Dictionary mit Config-Werten

**Ablauf:**
1. Konstruiert Pfad zu config.yaml (im gleichen Ordner wie Script)
2. Prüft ob Datei existiert
3. Lädt YAML-Datei mit `yaml.safe_load()`
4. Loggt Config-Inhalt
5. Beendet Programm bei Fehler

**Code:**
```python
def load_config():
    """Lädt die Konfiguration aus config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"

    log(f"Lade Config von: {config_path}")

    if not config_path.exists():
        log(f"Config-Datei nicht gefunden!", "ERROR")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        log(f"Config geladen: {config}", "SUCCESS")
        return config
    except Exception as e:
        log(f"Fehler beim Laden: {e}", "ERROR")
        sys.exit(1)
```

**Error-Handling:**
- Datei nicht gefunden → Exit mit Code 1
- YAML-Syntax-Fehler → Exit mit Code 1
- Andere Exceptions → Exit mit Code 1

---

### `parse_hotkey(hotkey_str)`

**Zweck:** Konvertiert String zu pynput Key-Objekt

**Parameter:**
- `hotkey_str` (str) - Hotkey-Name aus Config (z.B. "shift")

**Rückgabe:** `keyboard.Key` Objekt

**Unterstützte Hotkeys:**

| String | Key-Objekt |
|--------|------------|
| `"shift"` | `keyboard.Key.shift` |
| `"shift_r"` | `keyboard.Key.shift_r` |
| `"ctrl"` | `keyboard.Key.ctrl` |
| `"ctrl_r"` | `keyboard.Key.ctrl_r` |
| `"alt"` | `keyboard.Key.alt` |
| `"alt_r"` | `keyboard.Key.alt_r` |
| `"space"` | `keyboard.Key.space` |
| `"tab"` | `keyboard.Key.tab` |
| `"caps_lock"` | `keyboard.Key.caps_lock` |
| `"f1"` - `"f12"` | `keyboard.Key.f1` - `keyboard.Key.f12` |

**Fallback:** Bei unbekanntem Hotkey wird `keyboard.Key.shift` zurückgegeben

**Code:**
```python
def parse_hotkey(hotkey_str):
    """Konvertiert einen String in ein pynput Key-Objekt"""
    hotkey_map = {
        'shift': keyboard.Key.shift,
        'shift_r': keyboard.Key.shift_r,
        # ... (siehe vollständige Liste im Code)
    }

    key = hotkey_map.get(hotkey_str.lower())
    if key is None:
        log(f"Unbekannter Hotkey '{hotkey_str}', verwende 'shift'", "WARNING")
        return keyboard.Key.shift

    log(f"Hotkey '{hotkey_str}' -> {key}", "SUCCESS")
    return key
```

---

### Globale State-Variablen

```python
_clicking = False       # Ist Clicking aktuell aktiv?
_stop_thread = False    # Soll Worker-Thread beendet werden?
_config = None          # Config-Dictionary
_click_counter = 0      # Anzahl der ausgeführten Klicks
```

**Wichtig:** Diese Variablen werden von mehreren Threads gelesen/geschrieben.
Python's GIL (Global Interpreter Lock) macht einfache Lese/Schreib-Operationen thread-safe.

---

### `perform_click(target_pos, click_mode)`

**Zweck:** Führt einen einzelnen Klick aus

**Parameter:**
- `target_pos` - `None` oder `[x, y]` Array
- `click_mode` - String: `"fast"`, `"standard"`, `"separate"`, oder `"right"`

**Globale Variablen:**
- Inkrementiert `_click_counter`

**Ablauf:**
1. Extrahiere x, y aus target_pos (falls vorhanden)
2. Wähle Klick-Methode basierend auf click_mode
3. Führe Klick aus
4. Logge Klick-Event
5. Inkrementiere Counter
6. Fange Exceptions ab

**Klick-Modi im Detail:**

#### `fast`
```python
if x is not None and y is not None:
    pyautogui.click(x=x, y=y, duration=0)
else:
    pyautogui.click(duration=0)
```
- Schnellster Modus
- Keine Verzögerung (`duration=0`)

#### `separate`
```python
if x is not None and y is not None:
    pyautogui.mouseDown(x=x, y=y, button='left')
    pyautogui.mouseUp(x=x, y=y, button='left')
else:
    pyautogui.mouseDown(button='left')
    pyautogui.mouseUp(button='left')
```
- Separate Events
- Maximale Kontrolle

#### `right`
```python
if x is not None and y is not None:
    pyautogui.click(x=x, y=y, button='right', duration=0)
else:
    pyautogui.click(button='right', duration=0)
```
- Rechtsklick
- Gleich schnell wie `fast`

#### `standard`
```python
if x is not None and y is not None:
    pyautogui.click(x=x, y=y)
else:
    pyautogui.click()
```
- Mit pyautogui.PAUSE
- Langsamer

---

### `click_worker()`

**Zweck:** Worker-Thread-Funktion für kontinuierliches Klicken

**Thread:** Läuft in separatem daemon Thread

**Globale Variablen:**
- Liest: `_clicking`, `_stop_thread`, `_config`
- Schreibt: `_click_counter` (via `perform_click()`)

**Ablauf:**
```
START
  │
  ├─ Berechne Intervall: 1.0 / clicks_per_second
  ├─ Extrahiere target_pos und click_mode
  ├─ Log Worker-Info
  │
  └─┬─ while not _stop_thread:
    │
    ├───┬─ if _clicking:
    │   ├──── perform_click()
    │   └──── sleep(interval)
    │
    └───┴─ else:
            sleep(0.01)  # Kurze Pause wenn inaktiv
```

**Timing:**
- **Aktiv:** `sleep(interval)` zwischen Klicks
- **Inaktiv:** `sleep(0.01)` um CPU zu schonen

**Code:**
```python
def click_worker():
    global _clicking, _stop_thread, _click_counter

    interval = 1.0 / _config['clicks_per_second']
    target_pos = _config.get('target_position')
    click_mode = _config.get('click_mode', 'fast')

    log(f"Worker gestartet: {_config['clicks_per_second']} CPS, Modus: {click_mode}", "WORKER")
    log(f"Intervall: {interval:.4f} Sekunden", "WORKER")

    while not _stop_thread:
        if _clicking:
            perform_click(target_pos, click_mode)
            time.sleep(interval)
        else:
            time.sleep(0.01)

    log(f"Worker beendet. Gesamt: {_click_counter} Klicks", "WORKER")
```

**Thread-Safety:**
- `_clicking` wird nur von Keyboard-Listener geschrieben
- `_stop_thread` wird nur von Keyboard-Listener geschrieben
- Lesen dieser Variablen ist thread-safe in Python

---

### `on_press(key)`

**Zweck:** Callback für Tastendruck-Events

**Parameter:**
- `key` - pynput Key-Objekt

**Globale Variablen:**
- Liest: `_config['hotkey_obj']`
- Schreibt: `_clicking`

**Ablauf:**
1. Logge Tastendruck
2. Prüfe ob gedrückte Taste == Hotkey
3. Falls ja und clicking noch nicht aktiv:
   - Setze `_clicking = True`
   - Logge "CLICKING AKTIVIERT!"

**Code:**
```python
def on_press(key):
    global _clicking

    log(f"Taste gedrückt: {key}", "KEY")

    if key == _config['hotkey_obj']:
        if not _clicking:
            _clicking = True
            log("🟢 CLICKING AKTIVIERT!", "STATUS")
```

**Wichtig:**
- Nur beim ersten Drücken wird aktiviert (nicht bei Auto-Repeat)
- `if not _clicking` verhindert redundante Logs bei gehalten Taste

---

### `on_release(key)`

**Zweck:** Callback für Tasten-Loslassen-Events

**Parameter:**
- `key` - pynput Key-Objekt

**Rückgabe:**
- `False` - Stoppt Listener (bei ESC)
- Sonst nichts (implizit None = weitermachen)

**Globale Variablen:**
- Liest: `_config['hotkey_obj']`
- Schreibt: `_clicking`, `_stop_thread`

**Ablauf:**
1. Logge Tasten-Loslassen
2. **Hotkey-Check:**
   - Falls Hotkey losgelassen und clicking aktiv:
     - Setze `_clicking = False`
     - Logge "CLICKING DEAKTIVIERT!"
3. **ESC-Check:**
   - Falls ESC gedrückt:
     - Setze `_stop_thread = True`
     - Return `False` (stoppt Listener)

**Code:**
```python
def on_release(key):
    global _clicking, _stop_thread

    log(f"Taste losgelassen: {key}", "KEY")

    # Hotkey losgelassen
    if key == _config['hotkey_obj']:
        if _clicking:
            _clicking = False
            log("🔴 CLICKING DEAKTIVIERT!", "STATUS")

    # ESC zum Beenden
    if isinstance(key, keyboard.KeyCode) and key.char == '\x1b':
        log("ESC gedrückt - beende Programm", "EXIT")
        _stop_thread = True
        return False  # Stoppt Listener
```

**ESC-Detection:**
- `isinstance(key, keyboard.KeyCode)` - Ist es ein reguläres Zeichen?
- `key.char == '\x1b'` - Ist es das ESC-Zeichen (Hex 0x1B)?

**Alternative ESC-Detection:**
```python
if key == keyboard.Key.esc:  # Funktioniert auch
```

---

### `main()`

**Zweck:** Hauptfunktion - Orchestriert das Programm

**Ablauf:**

```
START
  │
  ├─ Banner ausgeben
  │
  ├─ Config laden (load_config)
  ├─ Hotkey parsen (parse_hotkey)
  │
  ├─ Info ausgeben (CPS, Hotkey, Position, etc.)
  │
  ├─ Worker-Thread starten
  │   └─ threading.Thread(target=click_worker, daemon=True)
  │
  ├─ Keyboard-Listener starten
  │   └─ keyboard.Listener(on_press, on_release)
  │
  ├─ listener.join()  # Wartet bis Listener stoppt (ESC)
  │
  └─ Programm beendet
```

**Code:**
```python
def main():
    global _config

    # Banner
    print("\n" + "=" * 70)
    print("🐛 DEBUG MODE - Autoinput")
    print("=" * 70 + "\n")

    # Config
    _config = load_config()
    _config['hotkey_obj'] = parse_hotkey(_config.get('hotkey', 'shift'))

    # Info
    log(f"CPS: {_config['clicks_per_second']}")
    log(f"Hotkey: {_config.get('hotkey', 'shift')}")
    log(f"Position: {_config.get('target_position', 'aktuelle Mausposition')}")
    log(f"Klick-Modus: {_config.get('click_mode', 'fast')}")

    print("\n" + "-" * 70)
    log("Drücke und HALTE die Hotkey-Taste zum Klicken", "INFO")
    log("Beende mit ESC", "INFO")
    print("-" * 70 + "\n")

    # Worker starten
    worker = threading.Thread(target=click_worker, daemon=True)
    worker.start()
    log("Worker-Thread gestartet", "SYSTEM")

    # Keyboard Listener
    log("Starte Keyboard-Listener...", "SYSTEM")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    log("Programm beendet", "EXIT")
    time.sleep(0.1)  # Kurze Pause damit letzte Logs ausgegeben werden
```

**Threading:**
- Worker-Thread ist `daemon=True` → wird beendet wenn Main-Thread endet
- Keyboard-Listener läuft in Main-Thread (via `listener.join()`)

**Context Manager:**
```python
with keyboard.Listener(...) as listener:
    listener.join()
```
Startet Listener automatisch und räumt auf beim Verlassen.

---

## Programmfluss - Detailliert

### 1. Start

```bash
python3 debug_autoclicker.py
```

```
main()
  │
  ├─ Banner ausgeben
  ├─ Config laden
  └─ Hotkey parsen
```

### 2. Worker-Thread starten

```
threading.Thread(target=click_worker, daemon=True).start()
```

Worker läuft jetzt parallel:
```
while not _stop_thread:
    if _clicking:
        perform_click()
        sleep(interval)
    else:
        sleep(0.01)
```

### 3. Keyboard-Listener starten

```
keyboard.Listener(on_press, on_release).join()
```

Main-Thread wartet jetzt auf Keyboard-Events.

### 4. User drückt Shift

```
Betriebssystem → pynput → on_press(Key.shift)
                              │
                              ├─ key == hotkey_obj? → JA
                              ├─ _clicking = False? → JA
                              └─ _clicking = True ✓
```

### 5. Worker bemerkt Änderung

```
while not _stop_thread:        # True
    if _clicking:              # True (geändert!)
        perform_click()        # Klick!
        sleep(0.0833)          # Bei 12 CPS
```

Jetzt werden Klicks ausgeführt (12x pro Sekunde).

### 6. User lässt Shift los

```
Betriebssystem → pynput → on_release(Key.shift)
                              │
                              ├─ key == hotkey_obj? → JA
                              ├─ _clicking = True? → JA
                              └─ _clicking = False ✓
```

### 7. Worker stoppt Clicking

```
while not _stop_thread:        # True
    if _clicking:              # False (geändert!)
        ...
    else:
        sleep(0.01)            # Idle
```

### 8. User drückt ESC

```
Betriebssystem → pynput → on_release(Key mit char='\x1b')
                              │
                              ├─ _stop_thread = True
                              └─ return False
                                    │
                                    └─ Listener stoppt
```

### 9. Cleanup

```
listener.join()  # Kehrt zurück (Listener gestoppt)
  │
  └─ main() Ende
        │
        └─ Worker-Thread beendet sich (daemon)
```

---

## Threading-Details

### Thread-Kommunikation

**Shared Variables:**
```python
_clicking      # Main → Worker (über Listener)
_stop_thread   # Main → Worker (über Listener)
_click_counter # Worker → Main (nur inkrementiert)
```

**Thread-Safety in Python:**
- **GIL** (Global Interpreter Lock) macht einfache Zuweisungen atomisch
- `_clicking = True` ist thread-safe
- `_click_counter += 1` ist thread-safe
- Keine Locks/Semaphores nötig für diesen Use-Case

### Daemon Thread

```python
threading.Thread(..., daemon=True)
```

**Eigenschaften:**
- Läuft im Hintergrund
- Wird automatisch beendet wenn Main-Programm endet
- Perfekt für Worker-Threads

**Warum daemon?**
- Worker muss nicht explizit gestoppt werden
- Beim ESC-Drücken endet Main → Worker endet automatisch

---

## Performance-Überlegungen

### Timing-Präzision

**CPS-Berechnung:**
```python
interval = 1.0 / clicks_per_second
```

Bei 12 CPS: `interval = 0.0833...` Sekunden

**Tatsächliche Rate:**
```
Erwartete Zeit: 0.0833s
time.sleep():   ~0.0833s (nicht exakt!)
perform_click():~0.001s
─────────────────────────
Gesamt:         ~0.0843s
```

**Realität:**
- `time.sleep()` ist nicht perfekt präzise
- OS-Scheduler kann Threads verzögern
- `perform_click()` braucht Zeit

**Resultat:** Tatsächliche CPS ist etwas niedriger als konfiguriert.

### CPU-Nutzung

**Aktiv (clicking):**
```python
while True:
    perform_click()  # ~0.001s
    sleep(0.0833)    # ~0.083s
```
CPU-Last: ~1% (meiste Zeit in sleep)

**Inaktiv:**
```python
while True:
    sleep(0.01)      # ~0.01s
```
CPU-Last: <0.1%

**Logging:**
- Jeder `print()` kostet Zeit
- Bei 100 CPS + Logging = merkbarer Overhead
- Daher: `enable_logging: false` für max. Performance

---

## Fehlerbehebung im Code

### Config-Fehler

**Problem:** Config kann nicht geladen werden

**Stelle:** `load_config()`:171-177

**Lösung:**
```python
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    log("config.yaml nicht gefunden!", "ERROR")
    sys.exit(1)
except yaml.YAMLError as e:
    log(f"YAML-Fehler: {e}", "ERROR")
    sys.exit(1)
```

### Click-Fehler

**Problem:** pyautogui.click() schlägt fehl

**Stelle:** `perform_click()`:129-130

**Aktuell:**
```python
except Exception as e:
    log(f"FEHLER beim Klicken: {e}", "ERROR")
```

**Verbesserung:**
- Exception catchen aber weiterlaufen
- Zähle fehlgeschlagene Klicks

### Hotkey nicht erkannt

**Problem:** Unbekannter Hotkey in Config

**Stelle:** `parse_hotkey()`:74-75

**Aktuell:**
```python
if key is None:
    log(f"Unbekannter Hotkey '{hotkey_str}', verwende 'shift'", "WARNING")
    return keyboard.Key.shift
```

**Gut:** Fallback zu sicherer Default-Taste.

---

## Erweiterungsmöglichkeiten

### 1. Toggle-Modus

Aktuell: Clicking nur während Hotkey gedrückt
Erweiterung: Taste drücken = an, nochmal drücken = aus

```python
def on_press(key):
    global _clicking
    if key == _config['hotkey_obj']:
        _clicking = not _clicking  # Toggle statt nur True
        state = "🟢 AKTIVIERT" if _clicking else "🔴 DEAKTIVIERT"
        log(state, "STATUS")
```

### 2. Mehrere Hotkeys

```python
_config['hotkey_toggle']  # Zum An/Aus-Schalten
_config['hotkey_hold']    # Nur während gedrückt
```

### 3. Variable CPS

Erhöhe CPS während Hotkey gedrückt:

```python
def on_press(key):
    if key == some_boost_key:
        _config['clicks_per_second'] *= 2
```

### 4. GUI

Nutze `tkinter` für grafische Config:
- Slider für CPS
- Dropdown für Hotkey
- Position-Picker

### 5. Profile

Mehrere Config-Profile:
```yaml
profiles:
  gaming:
    clicks_per_second: 20
  idle:
    clicks_per_second: 5
```

---

## Testing

### Unit-Tests

```python
import unittest

class TestClickWorker(unittest.TestCase):
    def test_interval_calculation(self):
        config = {'clicks_per_second': 12}
        interval = 1.0 / config['clicks_per_second']
        self.assertAlmostEqual(interval, 0.0833, places=3)
```

### Integration-Tests

```bash
# Test 1: Config laden
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Test 2: Hotkey parsen
python3 -c "from debug_autoclicker import parse_hotkey; print(parse_hotkey('shift'))"

# Test 3: Start ohne Crash
timeout 2 python3 debug_autoclicker.py || echo "OK"
```

---

## Deployment

### Standalone-App (PyInstaller)

```bash
pip install pyinstaller

pyinstaller --onefile \
            --windowed \
            --add-data "config.yaml:." \
            --name AutoinputAutoclicker \
            debug_autoclicker.py
```

Erstellt: `dist/AutoinputAutoclicker.app`

**Problem:** Berechtigungen müssen für die App neu gesetzt werden.

---

## Sicherheit

### Code-Review-Checkliste

- [ ] Keine Hardcoded-Credentials
- [ ] Input-Validierung (config.yaml)
- [ ] Exception-Handling bei File-Operations
- [ ] Thread-Safety bei Shared Variables
- [ ] Ressourcen werden freigegeben (daemon thread)

### Potentielle Risiken

1. **Malicious Config:**
   - Extreme CPS (1000+) könnte System überlasten
   - Mitigation: Validiere `clicks_per_second` (1-1000)

2. **Resource Exhaustion:**
   - Unendlicher Thread-Loop
   - Mitigation: ESC-Taste zum Beenden

3. **Privacy:**
   - Keyboard-Listener sieht ALLE Tastatureingaben
   - Mitigation: Nur Hotkey und ESC werden verarbeitet

---

## Lizenz & Credits

**Autor:** Entwickelt für Autoinput und ähnliche Spiele
**Python-Version:** 3.13+
**Plattform:** macOS (Darwin 25.1.0)

**Dependencies:**
- pynput - © Copyright 2015-2023 Moses Palmér
- pyautogui - © Al Sweigart
- pyyaml - © Kirill Simonov
