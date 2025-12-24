#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug-Version des Autoclickers mit ausführlichem Logging
"""

import time
import threading
import sys
from pathlib import Path
from pynput import keyboard
import pyautogui
import yaml

# PyAutoGUI Optimierungen
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Immer Logging aktivieren für Debug
FORCE_LOGGING = True

def log(msg, prefix="INFO"):
    """Immer loggen in Debug-Modus"""
    print(f"[{time.strftime('%H:%M:%S')}] [{prefix}] {msg}")

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
        log(f"Unbekannter Hotkey '{hotkey_str}', verwende 'shift'", "WARNING")
        return keyboard.Key.shift

    log(f"Hotkey '{hotkey_str}' -> {key}", "SUCCESS")
    return key

# State
_clicking = False
_stop_thread = False
_config = None
_click_counter = 0

def perform_click(target_pos, click_mode):
    """Führt einen Klick aus"""
    global _click_counter

    x, y = None, None
    if target_pos is not None and isinstance(target_pos, list) and len(target_pos) == 2:
        x, y = target_pos[0], target_pos[1]

    try:
        if click_mode == 'fast':
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, duration=0)
                log(f"Klick #{_click_counter} an Position ({x}, {y})", "CLICK")
            else:
                current_pos = pyautogui.position()
                pyautogui.click(duration=0)
                log(f"Klick #{_click_counter} an aktueller Position {current_pos}", "CLICK")

        elif click_mode == 'separate':
            if x is not None and y is not None:
                pyautogui.mouseDown(x=x, y=y, button='left')
                pyautogui.mouseUp(x=x, y=y, button='left')
            else:
                pyautogui.mouseDown(button='left')
                pyautogui.mouseUp(button='left')
            log(f"Klick #{_click_counter} (separate events)", "CLICK")

        elif click_mode == 'right':
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, button='right', duration=0)
            else:
                pyautogui.click(button='right', duration=0)
            log(f"Rechtsklick #{_click_counter}", "CLICK")

        else:  # standard
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y)
            else:
                pyautogui.click()
            log(f"Klick #{_click_counter} (standard)", "CLICK")

        _click_counter += 1

    except Exception as e:
        log(f"FEHLER beim Klicken: {e}", "ERROR")

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

def on_press(key):
    global _clicking

    log(f"Taste gedrückt: {key}", "KEY")

    if key == _config['hotkey_obj']:
        _clicking = True
        log("🟢 CLICKING AKTIVIERT!", "STATUS")

def on_release(key):
    global _clicking, _stop_thread

    log(f"Taste losgelassen: {key}", "KEY")

    if key == _config['hotkey_obj']:
        _clicking = False
        log("🔴 CLICKING DEAKTIVIERT!", "STATUS")

    # ESC zum Beenden
    if key == keyboard.Key.esc:
        log("ESC gedrückt - beende Programm", "EXIT")
        _stop_thread = True
        return False

def main():
    global _config

    print("\n" + "=" * 70)
    print("🐛 DEBUG MODE - Roblox Autoclicker")
    print("=" * 70 + "\n")

    # Config laden
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
    time.sleep(0.1)

if __name__ == "__main__":
    main()
