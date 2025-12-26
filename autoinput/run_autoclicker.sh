#!/bin/bash
# Wrapper-Script für Autoclicker - kann zu Accessibility hinzugefügt werden

# Finde Python 3.13
PYTHON=""
for py in python3.13 python3; do
    if command -v $py &> /dev/null; then
        version=$($py --version 2>&1)
        if [[ $version == *"3.13"* ]]; then
            PYTHON=$py
            break
        fi
    fi
done

# Fallback
if [ -z "$PYTHON" ]; then
    PYTHON="/opt/homebrew/Caskroom/miniconda/base/bin/python3"
fi

# Führe das Script aus
exec $PYTHON "$@"
