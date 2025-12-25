# Autoinput - Installation

## Problem: Virtual Environment Berechtigungen

Das Python im `venv` benötigt spezielle Accessibility-Berechtigungen auf macOS. Die **einfachste Lösung** ist, das System-Python direkt zu verwenden.

## ✅ Empfohlene Installation (ohne venv)

### 1. Installiere Dependencies mit System-Python

```bash
pip3 install pynput pyobjc-framework-Quartz
```

Falls `pip3` nicht gefunden wird:
```bash
python3 -m pip install pynput pyobjc-framework-Quartz
```

### 2. Gib dem System-Python Berechtigung

1. Öffne **Systemeinstellungen** → **Datenschutz & Sicherheit** → **Bedienungshilfen**
2. Klicke auf das **Schloss** unten links (Passwort eingeben)
3. Klicke auf **+** und füge hinzu:
   - `/usr/local/bin/python3` ODER
   - `/usr/bin/python3` ODER
   - Den Pfad, den dieser Befehl zeigt: `which python3`

### 3. Starte den Autoclicker

```bash
cd /Users/whaeuser/Entwicklung/AutoinputAutoclicker
python3 debug_autoclicker.py
```

Oder einfach:
```bash
./run.sh
```

---

## Alternative: Mit Virtual Environment

Falls du unbedingt ein venv verwenden möchtest:

### 1. Setup ausführen
```bash
./setup.sh
```

### 2. venv-Python Berechtigung geben

1. **Systemeinstellungen** → **Datenschutz & Sicherheit** → **Bedienungshilfen**
2. Klicke auf **+** und füge hinzu:
   ```
   /Users/whaeuser/Entwicklung/AutoinputAutoclicker/venv/bin/python
   ```

### 3. Autoclicker starten
```bash
source venv/bin/activate
python debug_autoclicker.py
```

---

## 🐛 Problemlösung

### Fehlermeldung: "This process is not trusted!"
→ Python hat keine Accessibility-Berechtigung (siehe Schritt 2 oben)

### Fehlermeldung: "No module named 'pynput'"
→ Dependencies fehlen (siehe Schritt 1 oben)

### Terminal-App selbst Berechtigung geben
Falls nichts funktioniert, gib dem Terminal selbst die Berechtigung:
- **Systemeinstellungen** → **Datenschutz & Sicherheit** → **Bedienungshilfen**
- Füge hinzu: **Terminal.app** oder **iTerm.app**

---

## 🎮 Verwendung

1. Starte den Autoclicker
2. **Halte Shift** gedrückt → Clicking startet
3. **Lasse Shift los** → Clicking stoppt
4. **Drücke ESC** → Programm beenden

**Standard-Konfiguration:**
- **Klicks pro Sekunde:** 20 CPS
- **Aktivierungstaste:** Shift
- **Stop-Taste:** ESC
- **Modus:** Gehalten (clicking nur während Shift gedrückt)
