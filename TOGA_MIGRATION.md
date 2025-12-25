# Toga Migration Plan

Migration von Tkinter GUI zu Toga (BeeWare) für bessere macOS-Integration und native UX.

## Warum Toga?

- **Native Widgets**: Echte macOS-Widgets statt Tkinter-Emulation
- **Keine Rendering-Bugs**: Kein 1-Pixel-Resize-Workaround nötig
- **Bessere macOS-Integration**: Menüs, Dialoge, Notifications
- **Cross-Platform**: Gleicher Code für macOS, Windows, Linux, iOS, Android
- **Moderne API**: Einfacher und pythonischer als Tkinter
- **.app Bundle**: Einfache App-Erstellung mit Briefcase

## Branch-Strategie

```
main (Tkinter)          ← Stabile Version, bleibt erhalten
  └── toga-migration    ← Neue Toga-Version
```

**Zwischen Branches wechseln:**
```bash
# Zur Tkinter-Version
git checkout main

# Zur Toga-Version
git checkout toga-migration
```

## Installationsplan

### 1. Toga installieren

```bash
pip3 install toga briefcase
```

### 2. Projektstruktur

```
AutoinputAutoclicker/
├── autoclicker_gui.py              # Tkinter (bleibt)
├── autoclicker_gui_toga.py         # Toga (NEU)
├── debug_autoclicker.py            # Backend (unverändert)
├── autoinput_toggle.py    # Backend (unverändert)
├── config.yaml                     # Config (unverändert)
├── start_gui.sh                    # Startet Tkinter
├── start_gui_toga.sh               # Startet Toga (NEU)
└── pyproject.toml                  # Briefcase Config (NEU)
```

## Migrationsschritte

### Phase 1: Basis-Setup ✅
- [x] Branch erstellen
- [ ] Toga installieren
- [ ] Minimale Toga-App erstellen
- [ ] Fenster mit Header testen

### Phase 2: Layout migrieren
- [ ] Header (Titel)
- [ ] Tab-System (3 Tabs)
- [ ] Footer
- [ ] Basis-Styling

### Phase 3: Tab 1 - Steuerung & Logs
- [ ] Status-Label
- [ ] Config-Info
- [ ] Start/Stop/Clear Buttons
- [ ] Log-Textbereich (ScrollContainer + MultilineTextInput)
- [ ] Subprocess-Integration

### Phase 4: Tab 2 - Konfiguration
- [ ] CPS Spinbox → NumberInput
- [ ] Hotkey Dropdown → Selection
- [ ] Aktivierungsmodus (Radio Buttons)
- [ ] Klick-Modus (Radio Buttons)
- [ ] Position (X/Y TextInput)
- [ ] Verbose Checkbox → Switch
- [ ] Save Button

### Phase 5: Tab 3 - Klick-Test
- [ ] Klick-Bereich (Canvas → Custom Widget)
- [ ] Statistik-Boxen
- [ ] Reset Button
- [ ] CPS-Berechnung

### Phase 6: Funktionalität
- [ ] Autoclicker starten/stoppen
- [ ] Config laden/speichern
- [ ] Live-Logs anzeigen
- [ ] Klick-Test funktioniert
- [ ] Prozess-Management

### Phase 7: .app Bundle
- [ ] pyproject.toml konfigurieren
- [ ] Briefcase build testen
- [ ] Icon hinzufügen
- [ ] DMG erstellen

## Toga vs Tkinter Mapping

| Tkinter | Toga | Notes |
|---------|------|-------|
| `tk.Tk()` | `toga.App()` | Haupt-App |
| `tk.Frame` | `toga.Box` | Container |
| `tk.Label` | `toga.Label` | Text |
| `tk.Button` | `toga.Button` | Button (native!) |
| `tk.Entry` | `toga.TextInput` | Einzeiliger Text |
| `scrolledtext.ScrolledText` | `toga.MultilineTextInput` | Mehrzeiliger Text |
| `ttk.Notebook` | `toga.OptionContainer` | Tabs |
| `ttk.Combobox` | `toga.Selection` | Dropdown |
| `tk.Spinbox` | `toga.NumberInput` | Zahlen-Input |
| `tk.Checkbutton` | `toga.Switch` | Checkbox |
| `tk.Canvas` | Custom Widget | Zeichenfläche |

## Beispiel: Einfacher Button

**Tkinter:**
```python
button = tk.Button(parent, text="Start", command=self.start)
button.pack()
```

**Toga:**
```python
button = toga.Button("Start", on_press=self.start)
box.add(button)
```

## Custom Button Problem gelöst!

In Tkinter mussten wir `Frame+Label` verwenden wegen macOS Theme-Override.
In Toga: **Native Buttons funktionieren einfach!** ✨

```python
# Kein Workaround nötig!
start_btn = toga.Button(
    "▶️  Starten",
    on_press=self.start_autoclicker,
    style=Pack(background_color="#22c55e")
)
```

## Vorteile der Migration

### Gelöste Probleme
✅ Keine Rendering-Bugs mehr (kein 1px-Resize-Trick)
✅ Buttons funktionieren nativ (keine Frame+Label-Hacks)
✅ Echte .app Bundle (mit Briefcase)
✅ Besseres macOS Look & Feel

### Neue Features möglich
- Native macOS Menüs
- System Notifications
- Dock-Icon mit Badge
- Touch Bar Support
- iOS/Android Version möglich

## Entwicklungsworkflow

```bash
# 1. In Toga-Branch arbeiten
git checkout toga-migration

# 2. Toga-Version testen
python3 autoclicker_gui_toga.py

# 3. Änderungen committen
git add .
git commit -m "Toga: Add XYZ feature"
git push origin toga-migration

# 4. Zurück zu Tkinter (falls nötig)
git checkout main
./start_gui.sh

# 5. Wieder zu Toga
git checkout toga-migration
```

## Wenn Toga fertig ist

**Option 1: Beide Versionen behalten**
```
main → Tkinter (legacy, stabil)
toga → Neue Standard-Version
```

**Option 2: Toga wird main**
```bash
git checkout main
git merge toga-migration
git push
```

## Nächste Schritte

1. **Installiere Toga:**
   ```bash
   pip3 install toga briefcase
   ```

2. **Teste minimale App:**
   ```bash
   python3 autoclicker_gui_toga.py
   ```

3. **Migriere schrittweise:**
   - Erst Layout/Struktur
   - Dann Funktionalität
   - Zuletzt Styling

## Ressourcen

- Toga Docs: https://toga.readthedocs.io/
- BeeWare Tutorial: https://docs.beeware.org/en/latest/tutorial/
- Toga Widgets: https://toga.readthedocs.io/en/latest/reference/widgets/
- Briefcase: https://briefcase.readthedocs.io/

---

**Status**: 🚧 In Entwicklung
**Branch**: `toga-migration`
**Tkinter Version**: Bleibt in `main`
