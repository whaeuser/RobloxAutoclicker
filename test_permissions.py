#!/usr/bin/env python3
"""
Testet ob die benötigten Berechtigungen auf macOS vorhanden sind
"""

import sys

print("=" * 60)
print("🔍 Autoclicker Berechtigungs-Test für macOS")
print("=" * 60)

# Test 1: Imports
print("\n1️⃣ Teste Python-Pakete...")
try:
    import pyautogui
    print("   ✅ pyautogui importiert")
except ImportError as e:
    print(f"   ❌ pyautogui fehlt: {e}")
    sys.exit(1)

try:
    from pynput import keyboard, mouse
    print("   ✅ pynput importiert")
except ImportError as e:
    print(f"   ❌ pynput fehlt: {e}")
    sys.exit(1)

try:
    import yaml
    print("   ✅ yaml importiert")
except ImportError as e:
    print(f"   ❌ yaml fehlt: {e}")
    sys.exit(1)

# Test 2: Mausposition lesen
print("\n2️⃣ Teste Mausposition lesen...")
try:
    pos = pyautogui.position()
    print(f"   ✅ Mausposition: {pos}")
except Exception as e:
    print(f"   ❌ Fehler: {e}")
    print("   ⚠️  Wahrscheinlich fehlen Berechtigungen!")

# Test 3: Keyboard Listener
print("\n3️⃣ Teste Keyboard-Zugriff...")
print("   Drücke irgendeine Taste innerhalb von 3 Sekunden...")

key_pressed = False

def on_press(key):
    global key_pressed
    key_pressed = True
    print(f"   ✅ Taste erkannt: {key}")
    return False  # Stop listener

try:
    from pynput import keyboard
    import threading
    import time

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Warte 3 Sekunden
    time.sleep(3)

    if not key_pressed:
        listener.stop()
        print("   ⚠️  Keine Taste erkannt - möglicherweise fehlen Berechtigungen")

except Exception as e:
    print(f"   ❌ Fehler beim Keyboard-Test: {e}")
    print("   ⚠️  Berechtigungen fehlen wahrscheinlich!")

# Test 4: Klick-Test
print("\n4️⃣ Teste Mausklick...")
print("   Versuche einen Klick an aktueller Position...")
try:
    current_pos = pyautogui.position()
    pyautogui.click()
    print(f"   ✅ Klick ausgeführt an Position {current_pos}")
except Exception as e:
    print(f"   ❌ Fehler beim Klicken: {e}")
    print("   ⚠️  Berechtigungen fehlen!")

print("\n" + "=" * 60)
print("📋 DIAGNOSE ABGESCHLOSSEN")
print("=" * 60)
print()
print("Wenn Fehler auftraten, folge diesen Schritten:")
print()
print("🔧 macOS Berechtigungen einrichten:")
print("   1. Öffne: Systemeinstellungen → Datenschutz & Sicherheit")
print("   2. Klicke auf: 'Bedienungshilfen' (Accessibility)")
print("   3. Entsperre mit dem Schloss-Symbol (unten links)")
print("   4. Füge hinzu:")
print("      - Terminal (oder iTerm2)")
print("      - Python")
print("   5. Starte das Terminal neu")
print("   6. Führe den Test erneut aus")
print()
print("Alternative: Führe aus mit sudo (nicht empfohlen)")
print()
