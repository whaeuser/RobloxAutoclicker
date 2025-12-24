# Troubleshooting Guide

Lösungen für häufige Probleme mit dem Roblox Autoclicker.

## Inhaltsverzeichnis

1. [Berechtigungsprobleme](#berechtigungsprobleme)
2. [Installation & Dependencies](#installation--dependencies)
3. [Klick-Probleme](#klick-probleme)
4. [Konfigurationsprobleme](#konfigurationsprobleme)
5. [Performance-Probleme](#performance-probleme)
6. [macOS-spezifische Probleme](#macos-spezifische-probleme)

---

## Berechtigungsprobleme

### Problem: "This process is not trusted! Input event monitoring will not be possible..."

**Ursache:** Python hat keine Accessibility-Berechtigung für Tastatur-Events.

**Lösung 1 - System-Python Berechtigung geben (EMPFOHLEN):**

1. Öffne **Systemeinstellungen**
2. Gehe zu **Datenschutz & Sicherheit**
3. Klicke auf **Bedienungshilfen** (Accessibility)
4. Klicke auf das **Schloss** unten links (Admin-Passwort eingeben)
5. Klicke auf **+** (Plus-Symbol)
6. Navigiere zu:
   - `/usr/local/bin/python3` ODER
   - `/usr/bin/python3` ODER
   - Der Pfad den `which python3` zeigt
7. Füge Python hinzu
8. Starte das Script neu

**Lösung 2 - venv-Python Berechtigung geben:**

Schritte 1-5 wie oben, dann:

6. Navigiere zu: `/Users/whaeuser/Entwicklung/RobloxAutoclicker/venv/bin/python`
7. Füge hinzu
8. Starte das Script neu

**Lösung 3 - Terminal/iTerm Berechtigung geben:**

Schritte 1-5 wie oben, dann:

6. Füge **Terminal.app** oder **iTerm.app** hinzu
7. Starte Terminal neu
8. Starte das Script

**Prüfen ob Berechtigung gesetzt ist:**

1. Öffne **Systemeinstellungen** → **Datenschutz & Sicherheit** → **Bedienungshilfen**
2. In der Liste sollte erscheinen:
   - `python3` ODER
   - `Terminal.app` / `iTerm.app`
3. Häkchen muss gesetzt sein

**Troubleshooting:**
- Neustart des Terminals nach Berechtigung setzen
- Neustart des Macs wenn nichts hilft
- Prüfe ob du Admin-Rechte hast

---

## Installation & Dependencies

### Problem: "No module named 'pynput'"

**Ursache:** pynput ist nicht installiert.

**Lösung:**

```bash
pip3 install pynput
```

Oder für alle Dependencies:

```bash
pip3 install pynput pyautogui pyyaml
```

**Falls pip3 nicht gefunden wird:**

```bash
python3 -m pip install pynput pyautogui pyyaml
```

**Prüfen ob installiert:**

```bash
python3 -c "import pynput; import pyautogui; import yaml; print('OK')"
```

Sollte ausgeben: `OK`

---

### Problem: "No module named 'yaml'"

**Ursache:** PyYAML ist nicht installiert.

**Lösung:**

```bash
pip3 install pyyaml
```

**Hinweis:** Package heißt `pyyaml`, aber importiert wird als `import yaml`.

---

### Problem: "No module named 'pyautogui'"

**Ursache:** PyAutoGUI ist nicht installiert.

**Lösung:**

```bash
pip3 install pyautogui
```

Oder auf macOS mit Quartz-Support:

```bash
pip3 install pyautogui pyobjc-framework-Quartz
```

---

### Problem: Dependencies installiert aber "No module named..."

**Ursache:** Dependencies in falschem Python/venv installiert.

**Diagnose:**

```bash
# Welches Python wird verwendet?
which python3

# Wo sind die Packages?
pip3 list | grep pynput
```

**Lösung 1 - Explizit mit Python-Modul installieren:**

```bash
python3 -m pip install pynput pyautogui pyyaml
```

**Lösung 2 - In aktivem venv installieren:**

```bash
source venv/bin/activate
pip install pynput pyautogui pyyaml
```

---

## Klick-Probleme

### Problem: Programm startet, aber es wird nicht geklickt

**Diagnose-Schritte:**

1. **Prüfe ob Clicking aktiviert wird:**
   - Starte `debug_autoclicker.py`
   - Drücke und halte Shift (oder dein Hotkey)
   - Siehst du: `[HH:MM:SS] [STATUS] 🟢 CLICKING AKTIVIERT!`?

   **Falls NEIN:**
   - Accessibility-Berechtigung fehlt (siehe oben)
   - Falscher Hotkey in config.yaml

   **Falls JA → Weiter zu Schritt 2**

2. **Prüfe ob Klicks geloggt werden:**
   - Während Shift gehalten
   - Siehst du: `[HH:MM:SS] [CLICK] Klick #1 an Position...`?

   **Falls NEIN:**
   - CPS zu niedrig? (überprüfe config.yaml)
   - Worker-Thread crashed?
   - Prüfe Terminal auf Fehler

   **Falls JA → Weiter zu Schritt 3**

3. **Klicks werden geloggt aber nicht ausgeführt:**
   - PyAutoGUI-Problem
   - App blockiert Klicks
   - Siehe [Klicks werden ignoriert](#klicks-werden-ignoriert)

---

### Problem: Klicks werden ignoriert (App reagiert nicht)

**Mögliche Ursachen:**

1. **App ist nicht im Fokus:**
   - Klicke einmal manuell in die Ziel-App
   - Halte dann Shift

2. **App blockiert synthetische Events:**
   - Manche Apps (z.B. mit Anti-Cheat) blockieren pyautogui
   - Teste mit anderem Klick-Modus:
   ```yaml
   click_mode: separate  # Statt fast
   ```

3. **Falsche Position:**
   - Bei `target_position: [x, y]` könnte Position falsch sein
   - Setze auf `target_position: null` zum Testen

4. **macOS Sandbox:**
   - Manche Apps sind sandboxed
   - Lösung: Gib der App selbst Accessibility-Berechtigung

**Test:**

Teste ob Klicks generell funktionieren:

```python
import pyautogui
import time

time.sleep(3)  # Zeit zum Fokussieren
pyautogui.click()
print("Klick ausgeführt!")
```

Speichere als `test_click.py` und führe aus:

```bash
python3 test_click.py
# Fokussiere schnell ein Textfeld
# Es sollte ein Klick erscheinen
```

---

### Problem: Zu wenig Klicks (CPS zu niedrig)

**Symptome:**
- Config sagt 20 CPS
- Real sind nur 15 CPS

**Ursachen:**

1. **Logging-Overhead:**
   ```yaml
   enable_logging: false  # Deaktiviere Logging
   ```

2. **System-Last:**
   - Schließe andere Programme
   - Überprüfe Activity Monitor

3. **Klick-Modus zu langsam:**
   ```yaml
   click_mode: fast      # Oder separate
   ```

4. **Python zu langsam:**
   - Nutze PyPy statt CPython (fortgeschritten)

**CPS messen:**

```python
# In debug_autoclicker.py temporär hinzufügen:
import time
start = time.time()
clicks = 0

# Nach 100 Klicks:
if _click_counter == 100:
    elapsed = time.time() - start
    actual_cps = 100 / elapsed
    log(f"Tatsächliche CPS: {actual_cps:.2f}", "INFO")
```

---

### Problem: Doppelklicks statt Einzelklicks

**Ursache:** Klick-Intervall zu kurz oder falscher Modus.

**Lösung:**

1. **Reduziere CPS:**
   ```yaml
   clicks_per_second: 10  # Statt 20
   ```

2. **Ändere Klick-Modus:**
   ```yaml
   click_mode: standard  # Statt separate
   ```

---

## Konfigurationsprobleme

### Problem: "Config-Datei nicht gefunden!"

**Ursache:** `config.yaml` ist nicht im richtigen Ordner.

**Lösung:**

1. **Prüfe wo Script ausgeführt wird:**
   ```bash
   pwd
   ```

2. **config.yaml muss im gleichen Ordner sein:**
   ```bash
   ls config.yaml
   ```

   Falls nicht gefunden:
   ```bash
   # Erstelle config.yaml
   cp config.yaml.example config.yaml  # Falls vorhanden
   # Oder erstelle manuell
   ```

3. **Script aus richtigem Ordner starten:**
   ```bash
   cd /Users/whaeuser/Entwicklung/RobloxAutoclicker
   python3 debug_autoclicker.py
   ```

---

### Problem: YAML-Syntax-Fehler

**Fehlermeldung:**
```
yaml.scanner.ScannerError: while scanning...
```

**Ursache:** Syntax-Fehler in config.yaml.

**Häufige Fehler:**

1. **Tabs statt Spaces:**
   ```yaml
   # FALSCH (mit Tab)
   →clicks_per_second: 12

   # RICHTIG (mit Spaces oder keine Einrückung nötig)
   clicks_per_second: 12
   ```

2. **Fehlende Leerzeichen:**
   ```yaml
   # FALSCH
   clicks_per_second:12

   # RICHTIG
   clicks_per_second: 12
   ```

3. **Falsche Array-Syntax:**
   ```yaml
   # FALSCH
   target_position: 500, 300

   # RICHTIG
   target_position: [500, 300]
   ```

4. **Falsche Boolean:**
   ```yaml
   # FALSCH
   enable_logging: True   # Großbuchstabe
   enable_logging: yes    # Nicht empfohlen

   # RICHTIG
   enable_logging: true
   enable_logging: false
   ```

**YAML validieren:**

```bash
python3 -c "import yaml; yaml.safe_load(open('config.yaml')); print('OK')"
```

Keine Ausgabe außer "OK" = Syntax korrekt.

---

### Problem: Hotkey funktioniert nicht

**Symptome:**
- Shift drücken → nichts passiert
- Keine "Taste gedrückt" Meldung

**Diagnose:**

1. **Ist Hotkey korrekt geschrieben?**
   ```yaml
   # FALSCH
   hotkey: Shift      # Großbuchstabe
   hotkey: shift_left # Falscher Name

   # RICHTIG
   hotkey: shift
   hotkey: shift_r
   ```

2. **Wird Hotkey erkannt?**
   - Schau in Log beim Start:
   ```
   [HH:MM:SS] [SUCCESS] Hotkey 'shift' -> Key.shift
   ```

   Falls:
   ```
   [HH:MM:SS] [WARNING] Unbekannter Hotkey '...', verwende 'shift'
   ```
   → Tippfehler in config.yaml

3. **Accessibility-Berechtigung?**
   - Siehe [Berechtigungsprobleme](#berechtigungsprobleme)

**Workaround - Teste mit anderem Hotkey:**

```yaml
hotkey: f6  # F6-Taste ist meist frei
```

---

### Problem: Position wird nicht erkannt

**Symptome:**
- `target_position: [500, 300]` gesetzt
- Aber es wird an anderer Stelle geklickt

**Ursache:** Koordinatensystem falsch verstanden.

**Prüfen:**

1. **Aktuelle Mausposition herausfinden:**
   ```bash
   python3 -c "import pyautogui; print(pyautogui.position())"
   ```

2. **Positioniere Maus wo du klicken willst**
3. **Führe obigen Befehl aus**
4. **Nutze die angezeigte Position:**
   ```yaml
   target_position: [x, y]  # Werte von oben
   ```

**Koordinatensystem:**
- **(0, 0)** = Oben links
- **X** wächst nach rechts
- **Y** wächst nach unten

---

## Performance-Probleme

### Problem: Programm ist langsam / verzögert

**Symptome:**
- Klicks kommen verzögert
- Hohe CPU-Last
- System ruckelt

**Lösungen:**

1. **Logging deaktivieren:**
   ```yaml
   enable_logging: false
   ```

2. **CPS reduzieren:**
   ```yaml
   clicks_per_second: 15  # Statt 100
   ```

3. **Optimalen Klick-Modus:**
   ```yaml
   click_mode: fast
   ```

4. **Andere Programme schließen:**
   - Activity Monitor öffnen
   - CPU-hungrige Apps beenden

---

### Problem: Hohe CPU-Last

**Normal:**
- **Inaktiv:** <1% CPU
- **20 CPS:** 1-3% CPU
- **100 CPS:** 5-10% CPU

**Zu hoch:**
- **20 CPS:** >10% CPU → Logging deaktivieren
- **100 CPS:** >20% CPU → CPS reduzieren

**Diagnose:**

```bash
# CPU-Usage überwachen
top -pid $(pgrep -f debug_autoclicker)
```

---

## macOS-spezifische Probleme

### Problem: "Operation not permitted"

**Ursache:** macOS Sicherheitsfeature (SIP / Gatekeeper).

**Lösung:**
- Siehe [Berechtigungsprobleme](#berechtigungsprobleme)
- Gib Terminal/Python Accessibility-Berechtigung

---

### Problem: Nach macOS-Update funktioniert nichts mehr

**Ursache:** Berechtigungen werden zurückgesetzt.

**Lösung:**

1. Öffne **Systemeinstellungen** → **Datenschutz & Sicherheit**
2. Entferne alte Einträge (Python/Terminal)
3. Füge neu hinzu
4. Neustart Terminal

---

### Problem: Script startet nicht (killed)

**Fehlermeldung:**
```
Killed: 9
```

**Ursache:** macOS Gatekeeper blockiert.

**Lösung:**

```bash
# Entferne Quarantine-Flag
xattr -r -d com.apple.quarantine debug_autoclicker.py

# Oder für ganzen Ordner
xattr -r -d com.apple.quarantine /Users/whaeuser/Entwicklung/RobloxAutoclicker
```

---

## Debugging-Tipps

### Systematisches Debugging

1. **Starte mit Debug-Modus:**
   ```bash
   python3 debug_autoclicker.py
   ```

2. **Prüfe jede Log-Meldung:**
   - `[INFO]` - Normal
   - `[SUCCESS]` - Funktioniert
   - `[WARNING]` - Vorsicht
   - `[ERROR]` - Problem!

3. **Teste einzelne Komponenten:**

   **Config laden:**
   ```bash
   python3 -c "from debug_autoclicker import load_config; print(load_config())"
   ```

   **Hotkey parsen:**
   ```bash
   python3 -c "from debug_autoclicker import parse_hotkey; print(parse_hotkey('shift'))"
   ```

   **Klick testen:**
   ```bash
   python3 -c "import pyautogui; pyautogui.click(); print('OK')"
   ```

4. **Isoliere das Problem:**
   - Config-Fehler? → Teste mit minimaler Config
   - Hotkey-Fehler? → Teste mit `f6` statt `shift`
   - Klick-Fehler? → Teste mit `click_mode: standard`

---

## Häufig gestellte Fragen (FAQ)

### Kann ich mehrere Autoclicker gleichzeitig laufen lassen?

Ja, aber mit verschiedenen Hotkeys:

1. Kopiere Ordner: `RobloxAutoclicker_2`
2. Ändere `config.yaml`:
   ```yaml
   hotkey: f6  # Statt shift
   ```
3. Starte beide Scripts in verschiedenen Terminals

---

### Funktioniert das auch unter Windows/Linux?

**Aktuell:** Nur macOS getestet.

**Anpassungen für Windows:**
- Entferne pyobjc-framework-Quartz
- Berechtigungen nicht nötig

**Anpassungen für Linux:**
- pyautogui benötigt `python3-xlib`
- Accessibility-Berechtigungen anders

---

### Wird mein Account gebannt wenn ich das benutze?

**Disclaimer:** Das hängt vom Spiel/Service ab.

- **Erlaubt:** Idle-Games, Offline-Games
- **Grauzone:** Online-Games ohne explizite Regeln
- **Verboten:** Games mit Anti-Cheat (z.B. Valorant, Fortnite)

**Empfehlung:** Prüfe die Terms of Service des jeweiligen Spiels.

---

### Kann ich die Geschwindigkeit während des Laufens ändern?

**Aktuell:** Nein, du musst das Script neu starten.

**Workaround:**
1. Drücke ESC (beendet Script)
2. Ändere `clicks_per_second` in config.yaml
3. Starte neu

---

## Logs analysieren

### Normales Startup-Log

```
======================================================================
🐛 DEBUG MODE - Roblox Autoclicker
======================================================================

[12:00:00] [INFO] Lade Config von: /Users/.../config.yaml
[12:00:00] [SUCCESS] Config geladen: {'clicks_per_second': 12, ...}
[12:00:00] [SUCCESS] Hotkey 'shift' -> Key.shift
[12:00:00] [INFO] CPS: 12
[12:00:00] [INFO] Hotkey: shift
[12:00:00] [INFO] Position: aktuelle Mausposition
[12:00:00] [INFO] Klick-Modus: fast

----------------------------------------------------------------------
[12:00:00] [INFO] Drücke und HALTE die Hotkey-Taste zum Klicken
[12:00:00] [INFO] Beende mit ESC
----------------------------------------------------------------------

[12:00:00] [SYSTEM] Worker-Thread gestartet
[12:00:00] [WORKER] Worker gestartet: 12 CPS, Modus: fast
[12:00:00] [WORKER] Intervall: 0.0833 Sekunden
[12:00:00] [SYSTEM] Starte Keyboard-Listener...
```

**Alles OK!** Script läuft.

---

### Log bei Clicking

```
[12:00:05] [KEY] Taste gedrückt: Key.shift
[12:00:05] [STATUS] 🟢 CLICKING AKTIVIERT!
[12:00:05] [CLICK] Klick #1 an aktueller Position Point(x=500, y=300)
[12:00:05] [CLICK] Klick #2 an aktueller Position Point(x=500, y=300)
[12:00:06] [CLICK] Klick #3 an aktueller Position Point(x=501, y=300)
...
[12:00:10] [KEY] Taste losgelassen: Key.shift
[12:00:10] [STATUS] 🔴 CLICKING DEAKTIVIERT!
```

**Alles OK!** Clicking funktioniert.

---

### Error-Logs

#### Config nicht gefunden

```
[12:00:00] [INFO] Lade Config von: /Users/.../config.yaml
[12:00:00] [ERROR] Config-Datei nicht gefunden!
```

→ Siehe [Config-Datei nicht gefunden](#problem-config-datei-nicht-gefunden)

#### YAML-Fehler

```
[12:00:00] [ERROR] Fehler beim Laden: ...
```

→ Siehe [YAML-Syntax-Fehler](#problem-yaml-syntax-fehler)

#### Klick-Fehler

```
[12:00:05] [CLICK] Klick #1 an ...
[12:00:05] [ERROR] FEHLER beim Klicken: ...
```

→ PyAutoGUI-Problem, teste mit anderem Klick-Modus

---

## Kontakt & Support

Bei weiteren Problemen:

1. **Lese diese Dokumentation nochmal**
2. **Prüfe die Config-Syntax**
3. **Teste mit minimal Config:**
   ```yaml
   clicks_per_second: 12
   hotkey: shift
   target_position: null
   enable_logging: true
   click_mode: fast
   ```

4. **Sammle Informationen:**
   - macOS-Version: `sw_vers`
   - Python-Version: `python3 --version`
   - Installierte Packages: `pip3 list | grep -E "(pynput|pyautogui|yaml)"`
   - Vollständiges Log vom Start bis Fehler

---

## Checkliste bei Problemen

- [ ] Python 3 installiert? (`python3 --version`)
- [ ] Dependencies installiert? (`pip3 list`)
- [ ] Berechtigungen gesetzt? (Systemeinstellungen)
- [ ] config.yaml existiert? (`ls config.yaml`)
- [ ] config.yaml Syntax korrekt? (YAML-Validator)
- [ ] Script aus richtigem Ordner gestartet? (`pwd`)
- [ ] Terminal neu gestartet nach Berechtigung?
- [ ] Debug-Modus zeigt Logs? (`python3 debug_autoclicker.py`)
- [ ] Hotkey wird erkannt? (Log prüfen)
- [ ] Klicks werden geloggt? (während Shift halten)

Wenn alle Punkte ✓ sind und es immer noch nicht funktioniert → Detailliertes Log sammeln und Support kontaktieren.
