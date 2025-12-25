#!/usr/bin/env bash

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${BASE_DIR}/venv"
PYTHON_BIN="python3"   # ggf. anpassen (z. B. /opt/homebrew/bin/python3)

# --------- venv anlegen ----------
if [[ ! -d "${VENV_DIR}" ]]; then
    echo "🛠️  Erstelle venv ..."
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# --------- aktivieren ----------
source "${VENV_DIR}/bin/activate"

# --------- pip updaten & Pakete ----------
python -m pip install --upgrade pip >/dev/null
python -m pip install --quiet pyautogui pynput pyyaml

# --------- Skript starten ----------
SCRIPT="${BASE_DIR}/autoinput.py"
if [[ -f "${SCRIPT}" ]]; then
    echo "🚀 Starte Autoclicker … (STRG+ESC zum Beenden)"
    python "${SCRIPT}"
else
    echo "❌ Skript nicht gefunden: ${SCRIPT}"
fi

deactivate
