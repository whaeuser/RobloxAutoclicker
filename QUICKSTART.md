# Kurzanleitung - Roblox Autoclicker

## In 3 Schritten loslegen

### 1. Dependencies installieren

```bash
pip3 install pynput pyautogui pyyaml
```

### 2. Berechtigungen setzen

1. **Systemeinstellungen** → **Datenschutz & Sicherheit** → **Bedienungshilfen**
2. Klick auf **Schloss** (Passwort eingeben)
3. Klick auf **+**
4. Füge hinzu: `/usr/local/bin/python3` (oder Pfad von `which python3`)

### 3. Starten

```bash
cd /Users/whaeuser/Entwicklung/RobloxAutoclicker
python3 debug_autoclicker.py
```

## Bedienung

| Aktion | Taste |
|--------|-------|
| Clicking starten | **Shift drücken und halten** |
| Clicking stoppen | **Shift loslassen** |
| Programm beenden | **ESC** |

## Einstellungen anpassen

Bearbeite `config.yaml`:

```yaml
clicks_per_second: 12    # Anzahl Klicks pro Sekunde (1-1000)
hotkey: shift            # Aktivierungs-Taste
target_position: null    # null = Mausposition, [x,y] = feste Position
click_mode: fast         # fast, standard, separate, right
```

**Speichern und Programm neu starten!**

## Häufige Hotkeys

```yaml
hotkey: shift      # Shift-Taste (Standard)
hotkey: space      # Leertaste
hotkey: f6         # F6-Taste
hotkey: alt        # Alt-Taste
```

## Häufige Probleme

### "This process is not trusted!"
→ Schritt 2 (Berechtigungen) nochmal machen

### "No module named 'pynput'"
→ Schritt 1 (Dependencies) nochmal machen

### Keine Klicks
→ In der Konsole sichtbar ob "🟢 CLICKING AKTIVIERT!" erscheint beim Shift-Drücken

### ESC funktioniert nicht
→ Nur ESC drücken (nicht Strg+ESC)

## Position herausfinden

Für feste Klick-Position:

```bash
python3 -c "import pyautogui; import time; time.sleep(3); print(pyautogui.position())"
```

1. Befehl ausführen
2. Innerhalb 3 Sekunden Maus zur gewünschten Stelle bewegen
3. Position wird ausgegeben: `Point(x=500, y=300)`
4. In config.yaml eintragen: `target_position: [500, 300]`

## Fertig!

**Mehr Details:**
- Vollständige Anleitung: [README.md](README.md)
- Alle Einstellungen: [CONFIG.md](CONFIG.md)
- Probleme lösen: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
