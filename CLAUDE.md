# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Autoinput is a configurable macOS autoclicker with a native Toga GUI, featuring both mouse and keyboard automation. The project uses Event Tap (macOS Quartz framework) instead of pynput for keyboard/mouse monitoring, and PyAutoGUI for click execution.

## Build Commands

### Build the macOS App
```bash
./build_app.sh
```
This is the primary build command. It:
1. Syncs `src/*.py` → `autoinput/*.py`
2. Deletes old build
3. Creates app with Briefcase
4. Copies dependencies (pynput, pyautogui, pyobjc modules)
5. Outputs `Autoinput.app` in root directory

### Test the App
```bash
open Autoinput.app
```

### Test Scripts Directly (without GUI)
```bash
python3 src/autoclicker_quartz.py
```

## Critical: Source of Truth Pattern

**ALWAYS edit in `src/`, NEVER in `autoinput/`** (except for `__main__.py`)

```
src/                              ← Edit here (Source of Truth)
├── autoclicker_quartz.py         ← Core autoclicker logic
├── autoinput_toggle.py           ← Toggle mode variant
└── debug_autoinput.py            ← Debug mode variant

autoinput/                        ← Auto-synced by build_app.sh
├── __main__.py                   ← EXCEPTION: Edit here for GUI
├── autoclicker_quartz.py         ← Copied from src/
├── autoinput_toggle.py           ← Copied from src/
└── config.yaml                   ← Configuration file
```

The build script copies from `src/` to `autoinput/` because Briefcase only packages the `autoinput/` directory into the app bundle.

## Architecture

### Threading Model (autoclicker_quartz.py)

The core autoclicker uses **3 parallel threads**:

1. **Main Thread**: Waits for stop signal, coordinates shutdown
2. **Event Tap Thread**: Runs CFRunLoop to monitor keyboard events via macOS Event Tap
3. **Click Worker Thread**: Performs actual clicking/keyboard actions

**Why Event Tap instead of pynput:**
- Event Tap runs in separate thread with own CFRunLoop
- Can run parallel to Toga's main event loop
- Native macOS API, more reliable for monitoring
- pynput conflicted with Toga's event loop

**Key Threading Pattern:**
```python
# Event Tap runs in dedicated thread
def _event_tap_thread():
    event_tap = CGEventTapCreate(...)
    runloop_source = CFMachPortCreateRunLoopSource(...)
    CFRunLoopAddSource(CFRunLoopGetCurrent(), runloop_source, kCFRunLoopCommonModes)
    CFRunLoopRun()  # Blocks until CFRunLoopStop()

# Click Worker in separate thread
def _click_worker():
    while not _stop_thread:
        if _clicking:
            _perform_click(...)
            time.sleep(interval)
```

### Global State Management

All state is managed via global variables with explicit resets in `main()`:
- `_clicking`: Whether clicking is active
- `_stop_thread`: Shutdown signal
- `_last_activity_time`: For idle prevention feature
- `_held_key`: Tracks held keyboard key
- `_event_tap_runloop`: RunLoop reference for shutdown

**Reset pattern in main():**
```python
def main():
    global _clicking, _stop_thread, _last_activity_time, ...
    _clicking = False
    _stop_thread = False
    _last_activity_time = None
    # ... rest of initialization
```

### New Features: Idle Prevention & Randomization

**Idle Prevention** (added 2025-12-26):
- Performs small mouse movements (±1-2px) to prevent system idle detection
- Only active when autoclicker is running (`_clicking = True`)
- Uses `pyautogui.moveRel()` to move and immediately returns to original position
- Tracked via `_last_activity_time` global variable

**Click Rhythm Randomization** (added 2025-12-26):
- Varies click intervals by configurable percentage (default ±20%)
- Calculated per-click using `random.uniform()`
- Enforces minimum interval of 0.001s (max 1000 CPS) for safety
- Applied to both mouse clicks and keyboard actions

Both features are:
- Disabled by default in `config.yaml`
- Configured via GUI switches and number inputs
- Independent and can be enabled separately

### GUI Architecture (autoinput/__main__.py)

**Framework**: Toga (BeeWare) - native macOS widgets

**Structure**: 3-tab interface using `toga.OptionContainer`
1. Control & Logs tab
2. Configuration tab (includes new idle prevention and randomization settings)
3. Click Test tab

**Subprocess Management:**
The GUI launches `autoclicker_quartz.py` as a subprocess and reads logs via threaded output reader. Critical pattern:
```python
self.autoclicker_process = subprocess.Popen(
    [python_cmd, script_path],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=1,
    text=True
)
# Read output in daemon thread
```

**Log System**: File-based with manual refresh
- Logs written to `/tmp/autoinput_toga.log`
- GUI reads new lines since last position
- Manual refresh button (not auto-refresh)

### Configuration System

**File**: `config.yaml` in `autoinput/` directory

**Loading**: Loaded at subprocess start by `autoclicker_quartz.py`

**GUI Editing**: Configuration tab allows editing and saving, then restarts autoclicker subprocess

**New Options** (2025-12-26):
```yaml
prevent_idle: false                 # Idle prevention feature
idle_prevention_interval: 30        # Seconds between movements
randomize_timing: false             # Click rhythm randomization
randomness_percent: 20.0            # ±% variation
```

## Development Workflow

### Making Changes to Core Autoclicker Logic

1. Edit in `src/autoclicker_quartz.py`
2. Test directly: `python3 src/autoclicker_quartz.py`
3. Build app: `./build_app.sh`
4. Test app: `open Autoinput.app`
5. Commit both `src/` and `autoinput/` files

### Making Changes to GUI

1. Edit `autoinput/__main__.py` directly (this is the exception to src/ rule)
2. Build app: `./build_app.sh`
3. Test app: `open Autoinput.app`
4. Commit `autoinput/__main__.py`

### Adding Config Options

1. Add default value to `config.yaml`
2. Add GUI controls in `autoinput/__main__.py` → `create_config_tab()`
3. Update `load_config()` to read new option
4. Update `save_config()` to write new option
5. Use option in `src/autoclicker_quartz.py` with `.get()` and default

## macOS Permissions

The app requires **Accessibility permissions** to monitor keyboard and control mouse. Users must manually add the app to:
**System Settings → Privacy & Security → Accessibility**

## Python Version Requirement

**Critical**: Requires Python 3.13 because bundled PyObjC packages are compiled for 3.13.

The GUI (`__main__.py`) has logic to find Python 3.13:
```python
def get_python_executable():
    # Try python3.13, then check version of python3
    # Falls back to known paths like /opt/homebrew/Caskroom/miniconda/base/bin/python3
```

## Briefcase App Packaging

The project uses Briefcase to create macOS app bundles. Configuration in `pyproject.toml`:
- App name: "Autoinput"
- Bundle ID: "com.autoinput"
- Sources: `autoinput/` directory only
- Requirements: toga, pyyaml (pynput and pyautogui manually copied by build script)

**Why manual dependency copying:**
The build script (`build_app.sh`) manually copies pynput, pyautogui, and all PyObjC framework modules into the app bundle because Briefcase doesn't reliably package them via requirements.

## Common Pitfalls

1. **Editing in autoinput/ instead of src/**: Changes will be overwritten by build script
2. **Forgetting to run build_app.sh**: App won't have latest changes
3. **Python version mismatch**: Must use Python 3.13 for bundled packages
4. **Missing Accessibility permissions**: App won't be able to monitor keyboard or click
5. **Modifying config while app running**: Changes won't take effect until restart (GUI handles this automatically)

## Key Files

- `src/autoclicker_quartz.py` - Core autoclicker with Event Tap threading
- `autoinput/__main__.py` - Toga GUI (3 tabs)
- `config.yaml` - User configuration
- `build_app.sh` - Build script (syncs src/ → autoinput/, runs Briefcase)
- `pyproject.toml` - Briefcase configuration
