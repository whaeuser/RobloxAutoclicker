#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roblox‑Autoclicker für macOS

Features:
  • Klickt, solange die linke Shift‑Taste (oder ein beliebiger Hotkey) gehalten wird.
  • Einstellbare Klick‑Pro‑Sekunde (CPS).
  • Optionales Klicken an einer fest definierten Position (z. B. im Spiel‑Fenster).
  • Sauberes Beenden mit STRG+ESC.
  • Konfiguration über config.yaml

Benötigte Pakete:
    pip install pyautogui pynput pyyaml
"""

import time
import threading
import os
import sys
from pathlib import Path
from pynput import keyboard, mouse
import pyautogui
import yaml

# PyAutoGUI Optimierungen für schnellere Klicks
pyautogui.PAUSE = 0  # Keine Pause zwischen Befehlen
pyautogui.FAILSAFE = False  # Failsafe deaktivieren für bessere Performance

# ------------------- Config Loader ---------------------------------
def load_config():
    """Lädt die Konfiguration aus config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        print(f"❌ Konfigurationsdatei nicht gefunden: {config_path}")
        print("Bitte erstelle eine config.yaml Datei im gleichen Verzeichnis.")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"❌ Fehler beim Laden der Konfiguration: {e}")
        sys.exit(1)

def parse_hotkey(hotkey_str):
    """Konvertiert einen String in ein pynput Key-Objekt"""
    hotkey_map = {
        'shift': keyboard.Key.shift,
        'shift_r': keyboard.Key.shift_r,
        'ctrl': keyboard.Key.ctrl,
        'ctrl_r': keyboard.Key.ctrl_r,
        'alt': keyboard.Key.alt,
        'alt_r': keyboard.Key.alt_r,
        'space': keyboard.Key.space,
        'tab': keyboard.Key.tab,
        'caps_lock': keyboard.Key.caps_lock,
        'f1': keyboard.Key.f1,
        'f2': keyboard.Key.f2,
        'f3': keyboard.Key.f3,
        'f4': keyboard.Key.f4,
        'f5': keyboard.Key.f5,
        'f6': keyboard.Key.f6,
        'f7': keyboard.Key.f7,
        'f8': keyboard.Key.f8,
        'f9': keyboard.Key.f9,
        'f10': keyboard.Key.f10,
        'f11': keyboard.Key.f11,
        'f12': keyboard.Key.f12,
    }

    key = hotkey_map.get(hotkey_str.lower())
    if key is None:
        print(f"⚠️  Unbekannter Hotkey '{hotkey_str}', verwende 'shift' als Standard")
        return keyboard.Key.shift
    return key

# ------------------- Internes State --------------------------------
_clicking = False
_stop_thread = False
_config = None

def _log(msg):
    if _config and _config.get('enable_logging', False):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def _perform_click(target_pos, click_mode):
    """Führt einen Klick basierend auf dem konfigurierten Modus aus"""
    x, y = None, None
    if target_pos is not None and isinstance(target_pos, list) and len(target_pos) == 2:
        x, y = target_pos[0], target_pos[1]

    if click_mode == 'fast':
        # Schneller Klick ohne Verzögerung
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, duration=0)
        else:
            pyautogui.click(duration=0)

    elif click_mode == 'separate':
        # Separate Down/Up Events - maximale Geschwindigkeit
        if x is not None and y is not None:
            pyautogui.mouseDown(x=x, y=y, button='left')
            pyautogui.mouseUp(x=x, y=y, button='left')
        else:
            pyautogui.mouseDown(button='left')
            pyautogui.mouseUp(button='left')

    elif click_mode == 'right':
        # Rechtsklick
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, button='right', duration=0)
        else:
            pyautogui.click(button='right', duration=0)

    else:  # standard
        # Standard PyAutoGUI Klick
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y)
        else:
            pyautogui.click()

def _click_worker():
    global _clicking, _stop_thread
    interval = 1.0 / _config['clicks_per_second']
    target_pos = _config.get('target_position')
    click_mode = _config.get('click_mode', 'fast')

    while not _stop_thread:
        if _clicking:
            _perform_click(target_pos, click_mode)
            _log("Klick")
            time.sleep(interval)
        else:
            time.sleep(0.01)

def on_press(key):
    global _clicking
    if key == _config['hotkey_obj']:
        _clicking = True

def on_release(key):
    global _clicking, _stop_thread
    if key == _config['hotkey_obj']:
        _clicking = False
    # STRG + ESC zum Beenden
    if isinstance(key, keyboard.KeyCode) and key.char == '\x1b':
        _stop_thread = True
        return False

def main():
    global _config

    # Konfiguration laden
    _config = load_config()
    _config['hotkey_obj'] = parse_hotkey(_config.get('hotkey', 'shift'))

    # Info ausgeben
    click_mode_names = {
        'fast': 'Schnell (optimiert)',
        'standard': 'Standard',
        'separate': 'Separate Events',
        'right': 'Rechtsklick'
    }
    click_mode = _config.get('click_mode', 'fast')

    print("=" * 50)
    print("🎮 Roblox Autoclicker gestartet")
    print("=" * 50)
    print(f"CPS: {_config['clicks_per_second']}")
    print(f"Hotkey: {_config.get('hotkey', 'shift')}")
    print(f"Position: {_config.get('target_position', 'aktuelle Mausposition')}")
    print(f"Klick-Modus: {click_mode_names.get(click_mode, click_mode)}")
    print(f"Logging: {'AN' if _config.get('enable_logging') else 'AUS'}")
    print("=" * 50)
    print("💡 Halte die Hotkey-Taste zum Klicken")
    print("🛑 Beenden mit STRG+ESC")
    print("=" * 50)

    # Worker-Thread starten
    worker = threading.Thread(target=_click_worker, daemon=True)
    worker.start()

    # Keyboard Listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    print("\n✅ Autoclicker beendet")
    time.sleep(0.1)

if __name__ == "__main__":
    main()
