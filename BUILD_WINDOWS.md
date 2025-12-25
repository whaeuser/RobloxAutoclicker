# Windows .exe erstellen

Dieses Projekt ist jetzt Windows-kompatibel! Es gibt zwei Möglichkeiten, eine .exe zu erstellen:

## ⚡ Schnell: PyInstaller (Empfohlen)

### 1. Voraussetzungen installieren

```bash
pip install pyinstaller pyautogui pynput pyyaml toga toga-winforms
```

### 2. Build ausführen

```bash
python build_windows.py
```

Die fertige .exe findest du dann in: `dist/Autoinput.exe`

### 3. Manuell (falls build_windows.py nicht funktioniert)

```bash
pyinstaller --name=Autoinput --onefile --windowed --add-data="config.yaml;." autoinput/__main__.py
```

---

## 🏢 Professionell: Briefcase (Native Windows App)

### 1. Briefcase installieren

```bash
pip install briefcase
```

### 2. Windows-App erstellen

```bash
briefcase create windows
briefcase build windows
briefcase package windows
```

Die App findest du dann in: `windows/Autoinput/`

---

## 📝 Hinweise

- **WICHTIG:** Die .exe muss auf einem Windows-System gebaut werden!
- Cross-Compilation von macOS nach Windows funktioniert nicht zuverlässig
- Die PyInstaller-Methode erstellt eine standalone .exe (keine Installation nötig)
- Die Briefcase-Methode erstellt einen richtigen Windows-Installer

---

## 🚀 Standalone Scripts (ohne GUI)

Du kannst auch die Python-Scripts direkt auf Windows ausführen:

```bash
# Toggle-Modus (Ein/Aus bei jedem Tastendruck)
python src/autoinput_toggle.py

# Hold-Modus (Aktiviert solange Taste gehalten wird)
python src/autoinput.py

# Debug-Modus (Mit ausführlichem Logging)
python src/debug_autoinput.py
```

Voraussetzungen:
```bash
pip install pyautogui pynput pyyaml
```

---

## ⚙️ Konfiguration

Die `config.yaml` funktioniert identisch auf Windows und macOS:

```yaml
activation_mode: toggle      # "toggle" oder "hold"
click_mode: fast            # "fast", "standard", "separate", "right"
clicks_per_second: 12       # Klicks pro Sekunde
enable_logging: true        # Logging aktivieren
hotkey: shift               # Hotkey zum Aktivieren
input_type: mouse           # "mouse" oder "keyboard"
keyboard_key: a             # Taste für Keyboard-Modus
keyboard_mode: repeat       # "repeat" oder "hold"
target_position: null       # [x, y] oder null für aktuelle Position
verbose_mode: false         # Ausführliches Logging
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pynput'"
```bash
pip install pynput
```

### "Error: Unable to find 'config.yaml'"
Stelle sicher, dass `config.yaml` im gleichen Verzeichnis wie die .exe liegt.

### "pyautogui.click() funktioniert nicht"
Führe die App als Administrator aus (Rechtsklick → "Als Administrator ausführen").

---

## 📦 Was funktioniert auf Windows?

✅ Mouse Clicking (alle Modi: fast, standard, separate, right)
✅ Keyboard Input (repeat und hold Modi)
✅ GUI (Toga-basiert, native Windows UI)
✅ Config laden/speichern
✅ Hotkey-Detection
✅ Process Start/Stop
✅ Logging
✅ Cleanup bei Exit

⚠️ Auto-Cleanup von alten Prozessen beim Start funktioniert nur auf macOS/Linux (kein Problem, nur kleiner Komfort-Feature)
