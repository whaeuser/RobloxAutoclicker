#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build-Script für Windows .exe mit PyInstaller
Muss auf einem Windows-System ausgeführt werden!
"""

import os
import subprocess
import sys

print("=" * 70)
print("Autoinput - Windows .exe Builder")
print("=" * 70)
print()

# Prüfe ob PyInstaller installiert ist
try:
    import PyInstaller
    print("✅ PyInstaller gefunden")
except ImportError:
    print("❌ PyInstaller nicht gefunden!")
    print("Installiere mit: pip install pyinstaller")
    sys.exit(1)

# Prüfe Plattform
if sys.platform != 'win32':
    print("⚠️  WARNUNG: Dieses Script sollte auf Windows ausgeführt werden!")
    print(f"Aktuelle Plattform: {sys.platform}")
    print()

print("\nErstelle .exe für GUI-Version...")
print("-" * 70)

# PyInstaller Command für GUI
cmd = [
    'pyinstaller',
    '--name=Autoinput',
    '--onefile',  # Einzelne .exe
    '--windowed',  # Kein Konsolen-Fenster
    '--add-data=config.yaml;.',  # Config-Datei einbetten
    '--icon=NONE',  # Kein Icon (kann später hinzugefügt werden)
    'autoinput/__main__.py'
]

print(f"Führe aus: {' '.join(cmd)}\n")
result = subprocess.run(cmd)

if result.returncode == 0:
    print("\n" + "=" * 70)
    print("✅ BUILD ERFOLGREICH!")
    print("=" * 70)
    print("\nDie .exe findest du hier:")
    print("  → dist/Autoinput.exe")
    print("\nStarte mit: dist\\Autoinput.exe")
    print()
else:
    print("\n❌ Build fehlgeschlagen!")
    sys.exit(1)
