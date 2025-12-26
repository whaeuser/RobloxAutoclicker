#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Autoclicker mit Event Tap in separatem Thread (OHNE pynput)
Event Tap läuft in eigenem Thread mit eigenem RunLoop parallel zu Toga
"""

import time
import threading
import os
import sys
import atexit
from pathlib import Path
import yaml
import random

# macOS Frameworks (gebündelt mit pyobjc)
from Quartz import (
    CGEventSourceCreate,
    kCGEventSourceStateHIDSystemState,
    CGEventCreateKeyboardEvent,
    CGEventPost,
    kCGHIDEventTap,
    CGEventTapCreate,
    kCGSessionEventTap,
    kCGEventKeyDown,
    kCGEventKeyUp,
    kCGEventFlagsChanged,
    CGEventGetIntegerValueField,
    kCGKeyboardEventKeycode,
    CGEventGetFlags,
    CGEventSetFlags,
    kCGEventFlagMaskShift,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskAlternate,
    CFRunLoopGetCurrent,
    CFRunLoopAddSource,
    kCFRunLoopCommonModes,
    CFMachPortCreateRunLoopSource,
    CFRunLoopRun,
    CFRunLoopStop,
    kCGEventTapOptionDefault,
    kCGHeadInsertEventTap,
)
import pyautogui

# PyAutoGUI für Maus-Klicks (schnell und stabil)
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

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

# ------------------- Keycodes --------------------------------------

# macOS Keycodes
KEYCODE_MAP = {
    'shift': 56,
    'shift_r': 60,
    'ctrl': 59,
    'ctrl_r': 62,
    'alt': 58,
    'alt_r': 61,
    'space': 49,
    'tab': 48,
    'caps_lock': 57,
    'f1': 122, 'f2': 120, 'f3': 99, 'f4': 118,
    'f5': 96, 'f6': 97, 'f7': 98, 'f8': 100,
    'f9': 101, 'f10': 109, 'f11': 103, 'f12': 111,
    'esc': 53,
}

def parse_hotkey(hotkey_str):
    """Konvertiert einen Hotkey-String in einen macOS Keycode"""
    keycode = KEYCODE_MAP.get(hotkey_str.lower())
    if keycode is None:
        print(f"⚠️  Unbekannter Hotkey '{hotkey_str}', verwende 'shift' als Standard")
        return KEYCODE_MAP['shift']
    return keycode

def parse_keyboard_key(key_str):
    """Konvertiert einen String in einen macOS Keycode für Tastatur-Eingaben"""
    special_keys = {
        'space': 49, 'enter': 36, 'tab': 48, 'backspace': 51,
        'delete': 117, 'esc': 53, 'up': 126, 'down': 125,
        'left': 123, 'right': 124, 'home': 115, 'end': 119,
        'page_up': 116, 'page_down': 121,
        'f1': 122, 'f2': 120, 'f3': 99, 'f4': 118,
        'f5': 96, 'f6': 97, 'f7': 98, 'f8': 100,
        'f9': 101, 'f10': 109, 'f11': 103, 'f12': 111,
    }

    key_lower = key_str.lower().strip()

    if key_lower in special_keys:
        return special_keys[key_lower]

    if len(key_str) == 1:
        char = key_str.lower()
        char_map = {
            'a': 0, 'b': 11, 'c': 8, 'd': 2, 'e': 14, 'f': 3, 'g': 5, 'h': 4,
            'i': 34, 'j': 38, 'k': 40, 'l': 37, 'm': 46, 'n': 45, 'o': 31,
            'p': 35, 'q': 12, 'r': 15, 's': 1, 't': 17, 'u': 32, 'v': 9,
            'w': 13, 'x': 7, 'y': 16, 'z': 6,
            '0': 29, '1': 18, '2': 19, '3': 20, '4': 21,
            '5': 23, '6': 22, '7': 26, '8': 28, '9': 25,
        }
        return char_map.get(char, 0)

    print(f"⚠️  Unbekannter Key '{key_str}', verwende 'a' als Standard")
    return 0

# ------------------- Global State ----------------------------------

_clicking = False
_stop_thread = False
_config = None
_click_counter = 0
_held_key = None
_hotkey_keycode = None
_hotkey_was_pressed = False
_event_tap_runloop = None
_last_activity_time = None

def _log(msg):
    if _config and _config.get('enable_logging', False):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def _verbose_log(msg):
    """Zeigt detaillierte Logs nur im Verbose-Modus"""
    if _config and _config.get('verbose_mode', False):
        timestamp = time.strftime('%H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] {msg}")

def _debug_log(msg):
    """Zeigt Debug-Logs nur im Debug-Modus"""
    if _config and _config.get('debug_mode', False):
        timestamp = time.strftime('%H:%M:%S.%f')[:-3]
        print(f"[DEBUG {timestamp}] {msg}")

# ------------------- Click & Keyboard Actions ----------------------

def _perform_click(target_pos, click_mode):
    """Führt einen Maus-Klick aus"""
    global _click_counter

    x, y = None, None
    if target_pos is not None and isinstance(target_pos, list) and len(target_pos) == 2:
        x, y = target_pos[0], target_pos[1]

    if click_mode == 'fast' or click_mode == 'separate':
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, duration=0)
        else:
            pyautogui.click(duration=0)
    elif click_mode == 'right':
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, button='right', duration=0)
        else:
            pyautogui.click(button='right', duration=0)
    else:  # standard
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y)
        else:
            pyautogui.click()

    _click_counter += 1
    _verbose_log(f"🖱️  CLICK #{_click_counter}")

def _perform_keyboard_action(keycode, keyboard_mode):
    """Führt Tastatur-Aktion aus mit CGEvent"""
    global _held_key, _click_counter

    source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

    if keyboard_mode == 'hold':
        if _held_key is None:
            key_down = CGEventCreateKeyboardEvent(source, keycode, True)
            # WICHTIG: Modifier-Flags löschen (Shift/Ctrl/Alt) damit keine großen Buchstaben entstehen
            CGEventSetFlags(key_down, 0)
            CGEventPost(kCGHIDEventTap, key_down)
            _held_key = keycode
            _verbose_log(f"⌨️  KEY #{_click_counter} | HELD")
    elif keyboard_mode == 'repeat':
        key_down = CGEventCreateKeyboardEvent(source, keycode, True)
        key_up = CGEventCreateKeyboardEvent(source, keycode, False)
        # WICHTIG: Modifier-Flags löschen (Shift/Ctrl/Alt) damit keine großen Buchstaben entstehen
        CGEventSetFlags(key_down, 0)
        CGEventSetFlags(key_up, 0)
        CGEventPost(kCGHIDEventTap, key_down)
        CGEventPost(kCGHIDEventTap, key_up)
        _verbose_log(f"⌨️  KEY #{_click_counter} | PRESS+RELEASE")

    _click_counter += 1

def _release_held_key():
    """Lässt eine gehaltene Taste los"""
    global _held_key

    if _held_key is not None:
        try:
            source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
            key_up = CGEventCreateKeyboardEvent(source, _held_key, False)
            # Modifier-Flags löschen
            CGEventSetFlags(key_up, 0)
            CGEventPost(kCGHIDEventTap, key_up)
            _log(f"Taste (keycode={_held_key}) losgelassen")
        except Exception as e:
            print(f"⚠️  Fehler beim Loslassen der Taste: {e}")
        finally:
            _held_key = None

def _perform_idle_prevention():
    """Führt kleine Mausbewegung aus um Idle-Erkennung zu verhindern"""
    global _last_activity_time

    try:
        # Aktuelle Position merken
        current_pos = pyautogui.position()

        # 1-2 Pixel nach rechts bewegen
        offset = random.choice([1, 2])
        pyautogui.moveRel(offset, 0, duration=0.1)
        _verbose_log(f"🐭 IDLE PREVENTION: Bewegt {offset}px nach rechts")

        # Kurz warten
        time.sleep(0.05)

        # Zurück zur Originalposition
        pyautogui.moveRel(-offset, 0, duration=0.1)
        _verbose_log(f"🐭 IDLE PREVENTION: Zurück zur Originalposition")

        _last_activity_time = time.time()
    except Exception as e:
        print(f"⚠️  Fehler bei Idle Prevention: {e}")

def _calculate_randomized_interval(base_interval, randomness_percent):
    """Berechnet randomisiertes Intervall mit ±randomness_percent Variation"""
    if randomness_percent <= 0:
        return base_interval

    # Variations-Range berechnen
    variation = base_interval * (randomness_percent / 100.0)

    # Zufällige Variation anwenden
    randomized = base_interval + random.uniform(-variation, variation)

    # Minimum-Intervall sicherstellen (0.001s = max 1000 CPS)
    min_interval = 0.001
    final_interval = max(min_interval, randomized)

    return final_interval

# ------------------- Event Tap Callback ----------------------------

_last_shift_state = False  # Track Shift state für FlagsChanged

def event_tap_callback(proxy, event_type, event, refcon):
    """Callback für Event Tap - läuft im Event-Tap Thread"""
    global _clicking, _stop_thread, _hotkey_was_pressed, _event_tap_runloop, _last_shift_state

    try:
        _debug_log(f"EVENT TAP CALLBACK! Type: {event_type}")

        # Modifier-Keys (Shift, Ctrl, Alt) erzeugen FlagsChanged Events
        if event_type == kCGEventFlagsChanged:
            flags = CGEventGetFlags(event)

            # Prüfe ob Shift gedrückt ist (left oder right)
            shift_pressed = bool(flags & kCGEventFlagMaskShift)

            _debug_log(f"FlagsChanged: shift={shift_pressed}, was={_last_shift_state}")

            # Nur bei State-Änderung reagieren
            if shift_pressed != _last_shift_state:
                _last_shift_state = shift_pressed

                # Prüfe ob Shift unser Hotkey ist
                if _hotkey_keycode in [56, 60]:  # Left/Right Shift
                    _debug_log(f"SHIFT ERKANNT! pressed={shift_pressed}")
                    activation_mode = _config.get('activation_mode', 'hold')

                    if activation_mode == 'toggle':
                        if shift_pressed and not _hotkey_was_pressed:
                            _clicking = not _clicking
                            status = "▶️  GESTARTET" if _clicking else "⏸️  GESTOPPT"
                            print(f"\n{status}")
                        _hotkey_was_pressed = shift_pressed
                    else:  # hold
                        if shift_pressed and not _clicking:
                            _clicking = True
                            print("▶️  CLICKING AKTIVIERT (Hold)")
                        elif not shift_pressed and _clicking:
                            _clicking = False
                            print("⏸️  CLICKING DEAKTIVIERT (Hold)")

        # Normale Keys (A-Z, F1-F12, ESC, etc.)
        elif event_type == kCGEventKeyDown or event_type == kCGEventKeyUp:
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            is_down = (event_type == kCGEventKeyDown)

            _debug_log(f"Key Event: keycode={keycode}, down={is_down}, hotkey={_hotkey_keycode}")

            # Hotkey-Logik (für nicht-Modifier Keys)
            if keycode == _hotkey_keycode and _hotkey_keycode not in [56, 60, 59, 62, 58, 61]:  # Nicht Modifier
                _debug_log(f"HOTKEY ERKANNT!")
                activation_mode = _config.get('activation_mode', 'hold')

                if activation_mode == 'toggle':
                    if is_down and not _hotkey_was_pressed:
                        _clicking = not _clicking
                        status = "▶️  GESTARTET" if _clicking else "⏸️  GESTOPPT"
                        print(f"\n{status}")
                    _hotkey_was_pressed = is_down
                else:  # hold
                    if is_down and not _clicking:
                        _clicking = True
                        print("▶️  CLICKING AKTIVIERT (Hold)")
                    elif not is_down and _clicking:
                        _clicking = False
                        print("⏸️  CLICKING DEAKTIVIERT (Hold)")

            # ESC zum Beenden
            if keycode == KEYCODE_MAP['esc'] and is_down:
                print("\n🛑 ESC gedrückt - beende Programm...")
                _stop_thread = True
                if _event_tap_runloop:
                    CFRunLoopStop(_event_tap_runloop)

    except Exception as e:
        print(f"❌ Event Tap Callback Fehler: {e}")
        import traceback
        print(traceback.format_exc())

    return event

# ------------------- Event Tap Thread ------------------------------

def _event_tap_thread():
    """Event Tap Thread mit eigenem RunLoop"""
    global _event_tap_runloop

    _debug_log("Event Tap Thread gestartet")

    # Event Tap erstellen - WICHTIG: Auch kCGEventFlagsChanged für Modifier-Keys!
    event_mask = (1 << kCGEventKeyDown) | (1 << kCGEventKeyUp) | (1 << kCGEventFlagsChanged)

    event_tap = CGEventTapCreate(
        kCGSessionEventTap,
        kCGHeadInsertEventTap,
        kCGEventTapOptionDefault,
        event_mask,
        event_tap_callback,
        None
    )

    if not event_tap:
        print("❌ FEHLER: Konnte Event Tap nicht erstellen!")
        print("⚠️  Stelle sicher, dass die App Accessibility-Berechtigung hat:")
        print("   Systemeinstellungen → Datenschutz & Sicherheit → Bedienungshilfen → Autoinput.app")
        return

    # RunLoop Source erstellen
    runloop_source = CFMachPortCreateRunLoopSource(None, event_tap, 0)
    _event_tap_runloop = CFRunLoopGetCurrent()
    CFRunLoopAddSource(_event_tap_runloop, runloop_source, kCFRunLoopCommonModes)

    _debug_log("Event Tap erstellt - RunLoop startet...")

    # RunLoop starten (blockiert bis CFRunLoopStop)
    CFRunLoopRun()

    _debug_log("Event Tap Thread beendet")

# ------------------- Click Worker Thread --------------------------

def _click_worker():
    """Worker-Thread für automatisches Klicken"""
    global _clicking, _stop_thread, _last_activity_time

    # Basis-Konfiguration laden
    interval = 1.0 / _config['clicks_per_second']
    target_pos = _config.get('target_position')
    click_mode = _config.get('click_mode', 'fast')

    input_type = _config.get('input_type', 'mouse')
    keyboard_keycode = _config.get('keyboard_keycode')
    keyboard_mode = _config.get('keyboard_mode', 'repeat')

    # NEU: Idle Prevention Einstellungen
    prevent_idle = _config.get('prevent_idle', False)
    idle_interval = _config.get('idle_prevention_interval', 30)

    # NEU: Randomisierungs-Einstellungen
    randomize_timing = _config.get('randomize_timing', False)
    randomness_percent = _config.get('randomness_percent', 20.0)

    _debug_log(f"Click-Worker gestartet - Input: {input_type}, CPS: {_config['clicks_per_second']}")
    _debug_log(f"Idle Prevention: {prevent_idle}, Randomization: {randomize_timing}")

    key_is_held = False

    while not _stop_thread:
        if _clicking:
            # NEU: Idle Prevention Only Mode
            if prevent_idle:
                # Nur Mausbewegungen, KEIN Clicking
                _perform_idle_prevention()
                time.sleep(idle_interval)
            else:
                # Normaler Clicking-Modus
                if input_type == 'keyboard':
                    if keyboard_mode == 'hold':
                        if not key_is_held:
                            _perform_keyboard_action(keyboard_keycode, keyboard_mode)
                            key_is_held = True
                        time.sleep(0.1)
                    else:
                        _perform_keyboard_action(keyboard_keycode, keyboard_mode)

                        # NEU: Randomisierung für Keyboard-Intervalle
                        if randomize_timing:
                            sleep_time = _calculate_randomized_interval(interval, randomness_percent)
                        else:
                            sleep_time = interval

                        time.sleep(sleep_time)
                else:
                    _perform_click(target_pos, click_mode)

                    # NEU: Randomisierung für Maus-Intervalle
                    if randomize_timing:
                        sleep_time = _calculate_randomized_interval(interval, randomness_percent)
                    else:
                        sleep_time = interval

                    time.sleep(sleep_time)
        else:
            if key_is_held:
                _release_held_key()
                key_is_held = False
            time.sleep(0.01)

    _debug_log("Click-Worker beendet")

# ------------------- Main Function --------------------------------

def cleanup_handler():
    """Emergency cleanup bei Exit"""
    _release_held_key()

def main():
    global _config, _hotkey_keycode, _stop_thread, _clicking, _hotkey_was_pressed, _click_counter, _held_key, _event_tap_runloop, _last_shift_state, _last_activity_time

    # WICHTIG: State zurücksetzen für neuen Run!
    _stop_thread = False
    _clicking = False
    _hotkey_was_pressed = False
    _click_counter = 0
    _held_key = None
    _event_tap_runloop = None
    _last_shift_state = False
    _last_activity_time = None

    # Cleanup-Handler registrieren
    atexit.register(cleanup_handler)

    # Konfiguration laden
    _config = load_config()
    _hotkey_keycode = parse_hotkey(_config.get('hotkey', 'shift'))

    # Keyboard-Key parsen falls nötig
    input_type = _config.get('input_type', 'mouse')
    if input_type == 'keyboard':
        _config['keyboard_keycode'] = parse_keyboard_key(_config.get('keyboard_key', 'a'))

    # Info ausgeben
    activation_mode = _config.get('activation_mode', 'hold')
    click_mode_names = {
        'fast': 'Schnell (optimiert)',
        'standard': 'Standard',
        'separate': 'Separate Events',
        'right': 'Rechtsklick'
    }
    click_mode = _config.get('click_mode', 'fast')

    print("=" * 50)
    print(f"🎮 Autoinput ({activation_mode.upper()}-MODUS) gestartet")
    print("=" * 50)
    print(f"Input-Typ: {'Tastatur' if input_type == 'keyboard' else 'Maus'}")
    if input_type == 'keyboard':
        keyboard_mode = _config.get('keyboard_mode', 'repeat')
        keyboard_key = _config.get('keyboard_key', 'a')
        mode_name = 'Halten' if keyboard_mode == 'hold' else 'Wiederholen'
        print(f"Tastatur-Taste: {keyboard_key}")
        print(f"Tastatur-Modus: {mode_name}")
    print(f"CPS: {_config['clicks_per_second']}")
    print(f"Hotkey: {_config.get('hotkey', 'shift')}")
    if input_type == 'mouse':
        print(f"Position: {_config.get('target_position', 'aktuelle Mausposition')}")
        print(f"Klick-Modus: {click_mode_names.get(click_mode, click_mode)}")
    print(f"Logging: {'AN' if _config.get('enable_logging') else 'AUS'}")
    print("=" * 50)

    if activation_mode == 'toggle':
        print("💡 Drücke die Hotkey-Taste zum Starten/Stoppen")
    else:
        print("💡 Drücke und HALTE die Hotkey-Taste zum Klicken")

    print("🛑 Beenden mit ESC")
    print("=" * 50)

    # Event Tap Thread starten (mit eigenem RunLoop)
    event_tap_thread = threading.Thread(target=_event_tap_thread, daemon=True)
    event_tap_thread.start()

    # Click-Worker Thread starten
    worker = threading.Thread(target=_click_worker, daemon=True)
    worker.start()

    print("✅ Autoclicker läuft - warte auf Hotkey...")

    try:
        # Hauptthread wartet auf Stop-Signal
        while not _stop_thread:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Strg+C erkannt - beende Programm...")
        _stop_thread = True
    finally:
        _release_held_key()
        if _event_tap_runloop:
            CFRunLoopStop(_event_tap_runloop)

    print("\n✅ Autoclicker beendet")
    time.sleep(0.1)

if __name__ == "__main__":
    main()
