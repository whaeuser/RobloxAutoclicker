# Build-Anleitung für Autoinput

## ⚠️ WICHTIG: Source of Truth

**ALLE Änderungen müssen in `src/` gemacht werden, NICHT in `autoinput/`!**

Die Dateien in `autoinput/` werden automatisch von `build_app.sh` synchronisiert.

### Dateien-Struktur:

```
src/                          ← Hier editieren! (Source of Truth)
├── autoinput.py              ← Hold-Modus Script
├── autoinput_toggle.py       ← Toggle-Modus Script
├── debug_autoinput.py        ← Debug-Script mit Verbose Logging
└── autoinput_gui_toga.py     ← GUI (Alternative zu autoinput/__main__.py)

autoinput/                    ← NICHT direkt editieren!
├── __main__.py               ← GUI (einzige Datei die hier editiert wird)
├── autoinput_toggle.py       ← AUTOMATISCH KOPIERT von src/
└── debug_autoinput.py        ← AUTOMATISCH KOPIERT von src/
```

---

## 🔨 macOS App bauen

### Option 1: Automatisches Build-Script (Empfohlen)

```bash
./build_app.sh
```

Das Script:
1. ✅ Synchronisiert `src/*.py` → `autoinput/*.py`
2. ✅ Löscht alten Build
3. ✅ Erstellt neue App mit Briefcase
4. ✅ Kopiert `Autoinput.app` ins Hauptverzeichnis

### Option 2: Manuell

```bash
# 1. Scripts synchronisieren
cp src/autoinput_toggle.py autoinput/
cp src/debug_autoinput.py autoinput/

# 2. App bauen
rm -rf build
briefcase create macOS
briefcase build macOS

# 3. App kopieren
rm -rf Autoinput.app
cp -R build/autoinput/macos/app/Autoinput.app .
```

---

## 🪟 Windows .exe bauen

Siehe [BUILD_WINDOWS.md](BUILD_WINDOWS.md) für die vollständige Anleitung.

**Kurz:**
```bash
# Auf Windows-PC:
python build_windows.py
```

---

## 🔄 Workflow für Entwicklung

### Änderungen an Scripts (autoinput_toggle.py, debug_autoinput.py):

```bash
# 1. Editiere in src/
vim src/autoinput_toggle.py

# 2. Teste direkt von src/
python3 src/autoinput_toggle.py

# 3. Wenn alles funktioniert: Baue neue App
./build_app.sh

# 4. Commit
git add src/autoinput_toggle.py autoinput/autoinput_toggle.py
git commit -m "Update autoclicker script"
git push
```

### Änderungen an GUI (__main__.py):

```bash
# 1. Editiere autoinput/__main__.py ODER src/autoinput_gui_toga.py
vim autoinput/__main__.py

# 2. Baue neue App
./build_app.sh

# 3. Commit
git add autoinput/__main__.py
git commit -m "Update GUI"
git push
```

---

## 📋 Checkliste vor Commit

Bevor du committest, stelle sicher:

- [ ] ✅ Änderungen wurden in `src/` gemacht (nicht direkt in `autoinput/`)
- [ ] ✅ `./build_app.sh` wurde ausgeführt
- [ ] ✅ App wurde getestet (Tastatur UND Maus Modi)
- [ ] ✅ Beide Scripts (`autoinput/autoinput_toggle.py` und `autoinput/debug_autoinput.py`) sind synchronisiert
- [ ] ✅ Git Status zeigt keine veralteten Dateien

---

## 🐛 Troubleshooting

### "App zeigt alte Version"

```bash
# Kompletter Rebuild
rm -rf build Autoinput.app
./build_app.sh
```

### "Scripts nicht synchronisiert"

```bash
# Manuell synchronisieren
cp src/autoinput_toggle.py autoinput/
cp src/debug_autoinput.py autoinput/
```

### "Tastatur funktioniert nicht"

1. Überprüfe, ob `autoinput/autoinput_toggle.py` die `parse_keyboard_key()` Funktion hat
2. Überprüfe, ob `autoinput/autoinput_toggle.py` die gleiche Version ist wie `src/autoinput_toggle.py`:
   ```bash
   diff src/autoinput_toggle.py autoinput/autoinput_toggle.py
   ```

---

## 🚀 Quick Commands

```bash
# Kompletter Rebuild der App
./build_app.sh

# Nur Scripts synchronisieren (ohne Rebuild)
cp src/autoinput_toggle.py autoinput/
cp src/debug_autoinput.py autoinput/

# App testen
open Autoinput.app

# Scripts direkt testen (ohne GUI)
python3 src/autoinput_toggle.py
python3 src/debug_autoinput.py
```

---

## 📝 Hinweis

Die Duplikation der Scripts (`src/` und `autoinput/`) ist notwendig, weil:
1. Briefcase packt nur den `autoinput/` Ordner in die App
2. Die GUI startet die Scripts aus dem `autoinput/` Ordner
3. Für Entwicklung/Testing ist es praktisch, Scripts in `src/` zu haben

Das `build_app.sh` Script stellt sicher, dass beide Versionen immer synchron sind.
