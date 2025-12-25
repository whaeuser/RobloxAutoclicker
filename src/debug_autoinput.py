#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug-Version des Autoclickers mit ausführlichem Logging
"""

import time
import threading
import sys
import os
import atexit
import signal
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
    config_path = Path(__file__).parent.parent / "config.yaml"

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

def parse_keyboard_key(key_str):
    """Konvertiert einen String in ein pynput Key-Objekt für Tastatur-Eingaben"""
    special_key_map = {
        'space': keyboard.Key.space,
        'enter': keyboard.Key.enter,
        'tab': keyboard.Key.tab,
        'backspace': keyboard.Key.backspace,
        'delete': keyboard.Key.delete,
        'esc': keyboard.Key.esc,
        'up': keyboard.Key.up,
        'down': keyboard.Key.down,
        'left': keyboard.Key.left,
        'right': keyboard.Key.right,
        'home': keyboard.Key.home,
        'end': keyboard.Key.end,
        'page_up': keyboard.Key.page_up,
        'page_down': keyboard.Key.page_down,
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

    key_lower = key_str.lower().strip()

    # Check if it's a special key
    if key_lower in special_key_map:
        return special_key_map[key_lower]

    # Single character keys (a-z, 0-9, etc.)
    if len(key_str) == 1:
        return keyboard.KeyCode.from_char(key_str.lower())

    # Default to 'a' if unknown
    log(f"Unbekannter Key '{key_str}', verwende 'a' als Standard", "WARNING")
    return keyboard.KeyCode.from_char('a')

# State
_clicking = False
_stop_thread = False
_config = None
_click_counter = 0
_current_key = None
_held_key = None               # Track gehaltene Taste für Keyboard-Modus
_keyboard_controller = None    # pynput keyboard.Controller() Instanz

def verbose_log(msg):
    """Zeigt detaillierte Logs nur im Verbose-Modus"""
    if _config and _config.get('verbose_mode', False):
        timestamp = time.strftime('%H:%M:%S.%f')[:-3]  # Mit Millisekunden
        print(f"[{timestamp}] {msg}")

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
                verbose_log(f"🖱️  CLICK #{_click_counter} | Pos=({x},{y}) | Key={_current_key} | Mode=fast")
            else:
                current_pos = pyautogui.position()
                pyautogui.click(duration=0)
                verbose_log(f"🖱️  CLICK #{_click_counter} | Pos=({current_pos.x},{current_pos.y}) | Key={_current_key} | Mode=fast")

        elif click_mode == 'separate':
            if x is not None and y is not None:
                pyautogui.mouseDown(x=x, y=y, button='left')
                pyautogui.mouseUp(x=x, y=y, button='left')
                verbose_log(f"🖱️  CLICK #{_click_counter} | Pos=({x},{y}) | Key={_current_key} | Mode=separate")
            else:
                current_pos = pyautogui.position()
                pyautogui.mouseDown(button='left')
                pyautogui.mouseUp(button='left')
                verbose_log(f"🖱️  CLICK #{_click_counter} | Pos=({current_pos.x},{current_pos.y}) | Key={_current_key} | Mode=separate")

        elif click_mode == 'right':
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, button='right', duration=0)
                verbose_log(f"🖱️  CLICK #{_click_counter} | Pos=({x},{y}) | Key={_current_key} | Mode=right")
            else:
                current_pos = pyautogui.position()
                pyautogui.click(button='right', duration=0)
                verbose_log(f"🖱️  CLICK #{_click_counter} | Pos=({current_pos.x},{current_pos.y}) | Key={_current_key} | Mode=right")

        else:  # standard
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y)
                verbose_log(f"🖱️  CLICK #{_click_counter} | Pos=({x},{y}) | Key={_current_key} | Mode=standard")
            else:
                current_pos = pyautogui.position()
                pyautogui.click()
                verbose_log(f"🖱️  CLICK #{_click_counter} | Pos=({current_pos.x},{current_pos.y}) | Key={_current_key} | Mode=standard")

        _click_counter += 1

    except Exception as e:
        log(f"FEHLER beim Klicken: {e}", "ERROR")

def perform_keyboard_action(key_obj, keyboard_mode):
    """Führt Tastatur-Aktion aus mit ausführlichem Logging"""
    global _held_key, _keyboard_controller, _click_counter

    if _keyboard_controller is None:
        _keyboard_controller = keyboard.Controller()

    try:
        if keyboard_mode == 'hold':
            # Hold: einmal drücken und halten
            if _held_key is None:
                _keyboard_controller.press(key_obj)
                _held_key = key_obj
                verbose_log(f"⌨️  KEY #{_click_counter} | Key={key_obj} | Mode=hold | Action=PRESS")

        elif keyboard_mode == 'repeat':
            # Repeat: drücken und loslassen
            _keyboard_controller.press(key_obj)
            _keyboard_controller.release(key_obj)
            verbose_log(f"⌨️  KEY #{_click_counter} | Key={key_obj} | Mode=repeat | Action=PRESS+RELEASE")

        _click_counter += 1

    except Exception as e:
        log(f"FEHLER beim Tastendruck: {e}", "ERROR")

def release_held_key():
    """Lässt eine gehaltene Taste los"""
    global _held_key, _keyboard_controller

    if _held_key is not None and _keyboard_controller is not None:
        try:
            _keyboard_controller.release(_held_key)
            log(f"Taste {_held_key} losgelassen", "INFO")
        except Exception as e:
            log(f"Fehler beim Loslassen der Taste: {e}", "ERROR")
        finally:
            _held_key = None

def click_worker():
    global _clicking, _stop_thread, _click_counter

    interval = 1.0 / _config['clicks_per_second']
    target_pos = _config.get('target_position')
    click_mode = _config.get('click_mode', 'fast')

    # NEU: Lade Keyboard-Konfiguration
    input_type = _config.get('input_type', 'mouse')
    keyboard_key = _config.get('keyboard_key_obj')
    keyboard_mode = _config.get('keyboard_mode', 'repeat')

    if input_type == 'keyboard':
        log(f"Worker gestartet: {_config['clicks_per_second']} CPS, Tastatur-Modus: {keyboard_mode}", "WORKER")
    else:
        log(f"Worker gestartet: {_config['clicks_per_second']} CPS, Maus-Modus: {click_mode}", "WORKER")
    log(f"Intervall: {interval:.4f} Sekunden", "WORKER")

    while not _stop_thread:
        if _clicking:
            if input_type == 'keyboard':
                perform_keyboard_action(keyboard_key, keyboard_mode)

                # Hold: nur einmal drücken, dann warten
                if keyboard_mode == 'hold':
                    time.sleep(0.1)
                else:
                    time.sleep(interval)  # Repeat: CPS respektieren
            else:
                # Bestehende Mausklick-Logik UNVERÄNDERT
                perform_click(target_pos, click_mode)
                time.sleep(interval)
        else:
            # NEU: Taste loslassen wenn Clicking stoppt
            if input_type == 'keyboard' and keyboard_mode == 'hold':
                release_held_key()

            time.sleep(0.01)

    if input_type == 'keyboard':
        log(f"Worker beendet. Gesamt: {_click_counter} Tasten", "WORKER")
    else:
        log(f"Worker beendet. Gesamt: {_click_counter} Klicks", "WORKER")

def on_press(key):
    global _clicking, _current_key, _stop_thread

    _current_key = str(key)

    if key == _config['hotkey_obj']:
        _clicking = True
        log("🟢 CLICKING AKTIVIERT!", "STATUS")
        verbose_log(f"⌨️  KEY PRESSED: {key} → Clicking AKTIVIERT")

    # ESC zum Beenden (auf Press UND Release reagieren)
    if key == keyboard.Key.esc:
        log("ESC gedrückt - beende Programm...", "EXIT")
        _stop_thread = True
        return False

def on_release(key):
    global _clicking, _stop_thread, _current_key

    _current_key = None

    if key == _config['hotkey_obj']:
        _clicking = False
        log("🔴 CLICKING DEAKTIVIERT!", "STATUS")
        verbose_log(f"⌨️  KEY RELEASED: {key} → Clicking DEAKTIVIERT")

        # NEU: Taste loslassen bei Hotkey-Release
        input_type = _config.get('input_type', 'mouse')
        keyboard_mode = _config.get('keyboard_mode', 'repeat')
        if input_type == 'keyboard' and keyboard_mode == 'hold':
            release_held_key()

    # ESC zum Beenden
    if key == keyboard.Key.esc:
        log("ESC gedrückt - beende Programm", "EXIT")
        release_held_key()  # NEU: Cleanup
        _stop_thread = True
        return False

def cleanup_handler():
    """Emergency cleanup bei Exit"""
    release_held_key()

def main():
    global _config

    # Cleanup-Handler registrieren
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGTERM, lambda sig, frame: (cleanup_handler(), sys.exit(0)))
    signal.signal(signal.SIGINT, lambda sig, frame: (cleanup_handler(), sys.exit(0)))

    print("\n" + "=" * 70)
    print("🐛 DEBUG MODE - Autoinput")
    print("=" * 70 + "\n")

    # Prüfe ob bereits ein Autoclicker läuft und beende ihn
    try:
        import subprocess
        result = subprocess.run(
            ['pgrep', '-f', 'autoinput|debug_autoclicker'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            current_pid = str(os.getpid())
            for pid in pids:
                if pid and pid != current_pid:
                    print(f"⚠️  Anderer Autoclicker läuft bereits (PID: {pid}), beende...")
                    os.system(f"kill -9 {pid} 2>/dev/null")
                    time.sleep(0.5)
            print("✅ Alte Prozesse beendet\n")
    except Exception as e:
        pass  # Fehler ignorieren, Script trotzdem starten

    # Config laden
    _config = load_config()
    _config['hotkey_obj'] = parse_hotkey(_config.get('hotkey', 'shift'))

    # NEU: Parse Keyboard-Key
    input_type = _config.get('input_type', 'mouse')
    if input_type == 'keyboard':
        _config['keyboard_key_obj'] = parse_keyboard_key(_config.get('keyboard_key', 'a'))

    # Info
    log(f"Input-Typ: {'Tastatur' if input_type == 'keyboard' else 'Maus'}")
    if input_type == 'keyboard':
        keyboard_mode = _config.get('keyboard_mode', 'repeat')
        keyboard_key = _config.get('keyboard_key', 'a')
        mode_name = 'Halten' if keyboard_mode == 'hold' else 'Wiederholen'
        log(f"Tastatur-Taste: {keyboard_key}")
        log(f"Tastatur-Modus: {mode_name}")
    log(f"CPS: {_config['clicks_per_second']}")
    log(f"Hotkey: {_config.get('hotkey', 'shift')}")
    if input_type == 'mouse':
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

    # Keyboard Listener mit Cleanup
    log("Starte Keyboard-Listener...", "SYSTEM")
    try:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        log("Strg+C erkannt - beende Programm...", "EXIT")
        _stop_thread = True
    finally:
        release_held_key()

    log("Programm beendet", "EXIT")
    time.sleep(0.1)

if __name__ == "__main__":
    main()
