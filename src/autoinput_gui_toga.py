#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autoinput - Toga GUI
Native macOS GUI mit Toga (BeeWare)
"""

import sys
import os

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import subprocess
import threading
import signal
import yaml
import time
from pathlib import Path
from datetime import datetime
import platform
import tempfile

# ------------------- Platform Detection ----------------------------
def is_windows():
    """Check if running on Windows"""
    return platform.system() == 'Windows'

def get_python_executable():
    """Get the correct Python executable for this platform"""
    # WICHTIG: Wir brauchen Python 3.13, weil die gebündelten Packages für 3.13 kompiliert sind!
    import shutil

    # Versuche zuerst python3.13 zu finden
    for python_cmd in ['python3.13', 'python3']:
        python_path = shutil.which(python_cmd)
        if python_path:
            # Prüfe Version
            try:
                import subprocess
                version_output = subprocess.check_output([python_path, '--version'], text=True, stderr=subprocess.STDOUT)
                if '3.13' in version_output:
                    return python_path
            except:
                pass

    # Fallback: Bekannte Python 3.13 Pfade
    known_paths = [
        '/opt/homebrew/Caskroom/miniconda/base/bin/python3',  # Miniconda
        '/opt/homebrew/bin/python3.13',
        '/usr/local/bin/python3.13',
    ]

    for path in known_paths:
        if Path(path).exists():
            return path

    # Letzter Fallback: Irgendein python3
    return shutil.which('python3') or 'python3'


class AutoinputApp(toga.App):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keine Dokument-Typen akzeptieren
        self._document_types = []

    def startup(self):
        """Wird beim App-Start aufgerufen"""

        # Variablen
        self.autoclicker_thread = None
        self.config_path = Path(__file__).parent / "config.yaml"
        self.log_file_path = Path(tempfile.gettempdir()) / "autoinput_toga.log"
        self.log_file_handle = None

        # Klick-Test Variablen
        self.click_count = 0
        self.click_start_time = None
        self.click_timestamps = []

        # Log reading (file-based, manual refresh)
        self.log_file_position = 0

        # Lösche alte Log-Datei beim Start
        if self.log_file_path.exists():
            self.log_file_path.unlink()

        # Haupt-Container
        main_box = toga.Box(style=Pack(direction=COLUMN))

        # Header
        header = toga.Box(style=Pack(
            direction=ROW,
            margin=(20, 20),
            background_color="#667eea"
        ))

        title = toga.Label(
            "🎮 Autoinput",
            style=Pack(
                margin=(10, 10),
                font_size=20,
                font_weight="bold",
                color="#ffffff"
            )
        )
        header.add(title)
        main_box.add(header)

        # Tab Container
        option_container = toga.OptionContainer(
            style=Pack(flex=1)
        )

        # Tab 1: Steuerung & Logs
        control_tab = self.create_control_tab()
        option_container.content.append("⚡ Steuerung & Logs", control_tab)

        # Tab 2: Konfiguration
        config_tab = self.create_config_tab()
        option_container.content.append("⚙️  Konfiguration", config_tab)

        # Tab 3: Klick-Test
        test_tab = self.create_test_tab()
        option_container.content.append("🎯 Klick-Test", test_tab)

        main_box.add(option_container)

        # Footer
        footer = toga.Box(style=Pack(
            direction=ROW,
            margin=(10, 10),
            background_color="#f1f5f9"
        ))

        footer_label = toga.Label(
            "Drücke die Hotkey-Taste zum Aktivieren | ESC oder Strg+C zum Beenden",
            style=Pack(margin=(5, 5), font_size=9, color="#64748b")
        )
        footer.add(footer_label)
        main_box.add(footer)

        # Haupt-Fenster
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.size = (800, 700)  # Breite x Höhe in Pixel
        self.main_window.show()

        # Config laden
        self.load_config()

    def open_document(self, fileURL):
        """Verhindert Dokument-Opening Warnung beim Start"""
        # Ignoriere .py Dateien und gib True zurück um Warnung zu unterdrücken
        return True

    def create_control_tab(self):
        """Tab für Start/Stop und Logs"""
        box = toga.Box(style=Pack(direction=COLUMN, margin=(20, 20)))

        # Status
        status_box = toga.Box(style=Pack(direction=ROW, margin=(10, 10)))
        self.status_label = toga.Label(
            "⚫ Gestoppt",
            style=Pack(font_size=14, font_weight="bold")
        )
        status_box.add(self.status_label)

        self.config_info = toga.Label(
            "",
            style=Pack(font_size=10, margin=(0, 10))
        )
        status_box.add(self.config_info)

        box.add(status_box)

        # Buttons
        button_box = toga.Box(style=Pack(direction=ROW, margin=(10, 10)))

        self.start_btn = toga.Button(
            "▶️  Starten",
            on_press=self.start_autoclicker,
            style=Pack(margin=(5, 5))
        )
        button_box.add(self.start_btn)

        self.stop_btn = toga.Button(
            "⏹️  Stoppen",
            on_press=self.stop_autoclicker,
            style=Pack(margin=(5, 5)),
            enabled=False
        )
        button_box.add(self.stop_btn)

        refresh_btn = toga.Button(
            "🔄 Logs aktualisieren",
            on_press=self.refresh_logs,
            style=Pack(margin=(5, 5))
        )
        button_box.add(refresh_btn)

        clear_btn = toga.Button(
            "🗑️  Logs löschen",
            on_press=self.clear_logs,
            style=Pack(margin=(5, 5))
        )
        button_box.add(clear_btn)

        box.add(button_box)

        # Log Area
        log_label = toga.Label(
            "📋 Live Logs:",
            style=Pack(margin=(10, 10), font_weight="bold")
        )
        box.add(log_label)

        self.log_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, margin=(10, 10))
        )
        box.add(self.log_text)

        return box

    def create_config_tab(self):
        """Tab für Konfiguration"""
        box = toga.Box(style=Pack(direction=COLUMN, margin=(20, 20)))

        # Hotkey (VOR CPS wie gewünscht!)
        hotkey_label = toga.Label("Aktivierungs-Hotkey:", style=Pack(margin=(5, 5)))
        box.add(hotkey_label)

        self.hotkey_selection = toga.Selection(
            items=['shift', 'shift_r', 'ctrl', 'ctrl_r', 'alt', 'alt_r',
                   'space', 'tab', 'f6', 'f7', 'f8', 'f9'],
            style=Pack(margin=(5, 5))
        )
        box.add(self.hotkey_selection)

        # CPS
        cps_label = toga.Label("Klicks pro Sekunde (CPS):", style=Pack(margin=(5, 5)))
        box.add(cps_label)

        self.cps_input = toga.NumberInput(
            min=1,
            max=1000,
            style=Pack(margin=(5, 5))
        )
        self.cps_input.value = 12
        box.add(self.cps_input)

        # Aktivierungsmodus
        mode_label = toga.Label("Aktivierungs-Modus:", style=Pack(margin=(5, 5)))
        box.add(mode_label)

        self.activation_mode_selection = toga.Selection(
            items=['hold', 'toggle'],
            style=Pack(margin=(5, 5))
        )
        box.add(self.activation_mode_selection)

        # Input Type Selection
        input_type_label = toga.Label("Input-Typ:", style=Pack(margin=(5, 5)))
        box.add(input_type_label)

        self.input_type_selection = toga.Selection(
            items=['mouse', 'keyboard'],
            on_change=self.on_input_type_changed,
            style=Pack(margin=(5, 5))
        )
        box.add(self.input_type_selection)

        # Keyboard Key Selection (conditional)
        self.keyboard_key_label = toga.Label("Tastatur-Taste:", style=Pack(margin=(5, 5)))
        box.add(self.keyboard_key_label)

        self.keyboard_key_selection = toga.Selection(
            items=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                   'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                   '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                   'space', 'enter', 'tab', 'backspace', 'delete',
                   'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'],
            style=Pack(margin=(5, 5))
        )
        box.add(self.keyboard_key_selection)

        # Keyboard Mode Selection (conditional)
        self.keyboard_mode_label = toga.Label("Tastatur-Modus:", style=Pack(margin=(5, 5)))
        box.add(self.keyboard_mode_label)

        self.keyboard_mode_selection = toga.Selection(
            items=['repeat', 'hold'],
            style=Pack(margin=(5, 5))
        )
        box.add(self.keyboard_mode_selection)

        # Verbose Mode
        self.verbose_switch = toga.Switch(
            "Verbose-Modus (zeigt jeden Klick)",
            style=Pack(margin=(10, 10))
        )
        box.add(self.verbose_switch)

        # Debug Mode
        self.debug_switch = toga.Switch(
            "Debug-Modus (Event Tap Details)",
            style=Pack(margin=(10, 10))
        )
        box.add(self.debug_switch)

        # Save Button
        save_btn = toga.Button(
            "💾 Konfiguration speichern",
            on_press=self.save_config,
            style=Pack(margin=(20, 20))
        )
        box.add(save_btn)

        return box

    def create_test_tab(self):
        """Tab für Klick-Test"""
        box = toga.Box(style=Pack(direction=COLUMN, margin=(20, 20)))

        title = toga.Label(
            "🎯 Klick-Test Bereich",
            style=Pack(margin=(10, 10), font_size=16, font_weight="bold")
        )
        box.add(title)

        info = toga.Label(
            "Klicke auf den Button unten, um deine Clicking-Geschwindigkeit zu testen",
            style=Pack(margin=(5, 5), font_size=10)
        )
        box.add(info)

        # Test Button
        self.test_btn = toga.Button(
            "Klick mich! (0)",
            on_press=self.register_test_click,
            style=Pack(margin=(20, 20))
        )
        box.add(self.test_btn)

        # Reset Button
        reset_btn = toga.Button(
            "🔄 Test zurücksetzen",
            on_press=self.reset_click_test,
            style=Pack(margin=(10, 10))
        )
        box.add(reset_btn)

        # Stats
        stats_box = toga.Box(style=Pack(direction=ROW, margin=(10, 10)))

        self.current_cps_label = toga.Label("Aktuelle CPS: 0", style=Pack(margin=(5, 5)))
        stats_box.add(self.current_cps_label)

        self.avg_cps_label = toga.Label("Durchschnitt: 0", style=Pack(margin=(5, 5)))
        stats_box.add(self.avg_cps_label)

        box.add(stats_box)

        stats_box2 = toga.Box(style=Pack(direction=ROW, margin=(10, 10)))

        self.total_clicks_label = toga.Label("Gesamt: 0", style=Pack(margin=(5, 5)))
        stats_box2.add(self.total_clicks_label)

        self.duration_label = toga.Label("Dauer: 0s", style=Pack(margin=(5, 5)))
        stats_box2.add(self.duration_label)

        box.add(stats_box2)

        return box

    def on_input_type_changed(self, widget):
        """Zeigt/versteckt Keyboard-Controls basierend auf Auswahl"""
        try:
            input_type = self.input_type_selection.value

            # Keyboard-Controls nur bei keyboard aktivieren
            is_keyboard = (input_type == 'keyboard')

            self.keyboard_key_label.enabled = is_keyboard
            self.keyboard_key_selection.enabled = is_keyboard
            self.keyboard_mode_label.enabled = is_keyboard
            self.keyboard_mode_selection.enabled = is_keyboard
        except:
            pass  # Ignoriere Fehler beim Initialisieren

    def load_config(self):
        """Lädt die Konfiguration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            self.cps_input.value = config.get('clicks_per_second', 12)
            self.hotkey_selection.value = config.get('hotkey', 'shift')
            self.activation_mode_selection.value = config.get('activation_mode', 'hold')
            self.verbose_switch.value = config.get('verbose_mode', False)
            self.debug_switch.value = config.get('debug_mode', False)

            # NEU: Keyboard-Einstellungen laden
            self.input_type_selection.value = config.get('input_type', 'mouse')
            self.keyboard_key_selection.value = config.get('keyboard_key', 'a')
            self.keyboard_mode_selection.value = config.get('keyboard_mode', 'repeat')

            # UI aktualisieren
            self.on_input_type_changed(None)

            self.update_config_display(config)
        except Exception as e:
            self.log(f"❌ Fehler beim Laden der Config: {e}")

    def update_config_display(self, config):
        """Aktualisiert die Config-Anzeige"""
        hotkey = config.get('hotkey', 'shift').upper()
        cps = config.get('clicks_per_second', '?')
        mode = config.get('activation_mode', 'hold')
        mode_text = "Toggle" if mode == 'toggle' else "Hold"

        # NEU: Input-Typ Info
        input_type = config.get('input_type', 'mouse')
        input_type_text = "Tastatur" if input_type == 'keyboard' else "Maus"

        if input_type == 'keyboard':
            keyboard_key = config.get('keyboard_key', 'a').upper()
            keyboard_mode = config.get('keyboard_mode', 'repeat')
            kb_mode_text = "Halten" if keyboard_mode == 'hold' else "Wiederholen"
            self.config_info.text = f"{input_type_text}: {keyboard_key} ({kb_mode_text}) | Hotkey: {hotkey} | CPS: {cps} | Modus: {mode_text}"
        else:
            self.config_info.text = f"{input_type_text} | Hotkey: {hotkey} | CPS: {cps} | Modus: {mode_text}"

    def save_config(self, widget):
        """Speichert die Konfiguration"""
        try:
            config = {
                'clicks_per_second': int(self.cps_input.value),
                'hotkey': self.hotkey_selection.value,
                'activation_mode': self.activation_mode_selection.value,
                'click_mode': 'fast',
                'target_position': None,
                'enable_logging': True,
                'verbose_mode': self.verbose_switch.value,
                'debug_mode': self.debug_switch.value,

                # NEU: Keyboard-Einstellungen
                'input_type': self.input_type_selection.value,
                'keyboard_key': self.keyboard_key_selection.value,
                'keyboard_mode': self.keyboard_mode_selection.value
            }

            # Autoclicker stoppen falls er läuft
            was_running = self.autoclicker_thread and self.autoclicker_thread.is_alive()
            if was_running:
                self.stop_autoclicker(None)

            # Config speichern
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            self.update_config_display(config)
            self.log("💾 Konfiguration gespeichert!")
            self.log("✅ Konfiguration erfolgreich gespeichert!")

            # Autoclicker wieder starten falls er vorher lief
            if was_running:
                self.log("🔄 Autoclicker wird neu gestartet...")
                import threading
                t = threading.Timer(0.5, self.start_autoclicker, args=[None])
                t.daemon = True
                t.start()

        except Exception as e:
            self.log(f"❌ Fehler beim Speichern: {e}")

    def start_autoclicker(self, widget):
        """Startet den Autoclicker"""
        # Prevent double-clicks
        if not self.start_btn.enabled:
            self.log("⚠️  Start bereits in Bearbeitung...")
            return

        if self.autoclicker_thread and self.autoclicker_thread.is_alive():
            self.log("⚠️  Autoclicker läuft bereits!")
            return

        # Sofort Button deaktivieren um Doppel-Klicks zu verhindern
        self.start_btn.enabled = False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            activation_mode = config.get('activation_mode', 'hold')

            # Importiere das neue Quartz-basierte Modul (OHNE pynput!)
            from autoinput import autoclicker_quartz as autoclicker_module
            mode_name = "Toggle" if activation_mode == 'toggle' else "Hold"

            self.log(f"▶️  Starte Autoclicker ({mode_name}-Modus)...")

            # Öffne Log-Datei zum Schreiben
            self.log_file_handle = open(self.log_file_path, 'w', buffering=1)
            self.log_file_position = 0
            self.stop_autoclicker_flag = False

            # Starte Script in einem Thread - IMPORTIERT statt exec()
            def run_autoclicker():
                # Redirect stdout/stderr
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = self.log_file_handle
                sys.stderr = self.log_file_handle

                try:
                    # Rufe main() Funktion auf (kein exec!)
                    autoclicker_module.main()
                except Exception as e:
                    import traceback
                    print(f"[ERROR] {traceback.format_exc()}")
                finally:
                    # Restore stdout/stderr
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

            self.autoclicker_thread = threading.Thread(target=run_autoclicker, daemon=True)
            self.autoclicker_thread.start()

            # Buttons aktualisieren
            self.stop_btn.enabled = True
            self.status_label.text = "🟢 Läuft"

            self.log("✅ Autoclicker gestartet!")
            self.log("💡 Klicke auf '🔄 Logs aktualisieren' um die Autoclicker-Logs zu sehen")

        except Exception as e:
            self.log(f"❌ Fehler beim Starten: {e}")
            import traceback
            self.log(traceback.format_exc())
            # Bei Fehler: Button wieder aktivieren
            self.start_btn.enabled = True
            self.stop_btn.enabled = False
            self.status_label.text = "⚫ Gestoppt"

    def stop_autoclicker(self, widget):
        """Stoppt den Autoclicker"""
        if not self.autoclicker_thread or not self.autoclicker_thread.is_alive():
            self.log("⚠️  Autoclicker läuft nicht!")
            return

        try:
            self.log("⏹️  Stoppe Autoclicker...")
            self.log("💡 Sende ESC-Signal an Autoclicker...")

            # Simuliere ESC-Taste um Autoclicker zu stoppen
            try:
                from pynput import keyboard
                controller = keyboard.Controller()
                controller.press(keyboard.Key.esc)
                controller.release(keyboard.Key.esc)
                self.log("✅ ESC gesendet - Autoclicker wird beendet...")
            except Exception as e:
                self.log(f"⚠️  Konnte ESC nicht senden: {e}")

            # Warte kurz auf Thread-Ende
            self.autoclicker_thread.join(timeout=2)

            # Schließe Log-Datei
            if self.log_file_handle:
                try:
                    self.log_file_handle.close()
                except:
                    pass
                self.log_file_handle = None

            # Buttons aktualisieren
            self.start_btn.enabled = True
            self.stop_btn.enabled = False
            self.status_label.text = "⚫ Gestoppt"

            self.log("✅ Autoclicker gestoppt!")

        except Exception as e:
            self.log(f"❌ Fehler beim Stoppen: {e}")


    def refresh_logs(self, widget):
        """Aktualisiert die Logs manuell aus der Log-Datei"""
        try:
            if self.log_file_path.exists():
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    # Springe zur letzten Position
                    f.seek(self.log_file_position)

                    # Lese neue Zeilen
                    new_lines = f.readlines()

                    # Aktualisiere Position
                    self.log_file_position = f.tell()

                    # Zeige neue Zeilen im GUI
                    if new_lines:
                        for line in new_lines:
                            stripped = line.strip()
                            if stripped:
                                self.log(stripped)
                    else:
                        # Keine neuen Logs
                        pass
        except Exception as e:
            self.log(f"❌ Fehler beim Aktualisieren: {e}")

    def clear_logs(self, widget):
        """Löscht alle Logs"""
        self.log_text.value = ""

    def register_test_click(self, widget):
        """Registriert einen Klick im Test-Bereich"""
        self.click_count += 1
        now = time.time()

        if self.click_start_time is None:
            self.click_start_time = now

        self.click_timestamps.append(now)
        # Nur letzte Sekunde behalten
        self.click_timestamps = [t for t in self.click_timestamps if now - t < 1.0]

        # Update Display
        self.test_btn.text = f"Klick mich! ({self.click_count})"
        self.total_clicks_label.text = f"Gesamt: {self.click_count}"

        # CPS berechnen
        current_cps = len(self.click_timestamps)
        self.current_cps_label.text = f"Aktuelle CPS: {current_cps}"

        # Durchschnitt und Dauer
        duration = now - self.click_start_time
        avg_cps = self.click_count / duration if duration > 0 else 0
        self.avg_cps_label.text = f"Durchschnitt: {avg_cps:.1f}"
        self.duration_label.text = f"Dauer: {duration:.1f}s"

    def reset_click_test(self, widget):
        """Setzt den Klick-Test zurück"""
        self.click_count = 0
        self.click_start_time = None
        self.click_timestamps = []

        self.test_btn.text = "Klick mich! (0)"
        self.current_cps_label.text = "Aktuelle CPS: 0"
        self.avg_cps_label.text = "Durchschnitt: 0"
        self.total_clicks_label.text = "Gesamt: 0"
        self.duration_label.text = "Dauer: 0s"

    def log(self, message):
        """Fügt eine Log-Nachricht hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        current = self.log_text.value or ""
        self.log_text.value = f"{current}[{timestamp}] {message}\n"

        # Scroll to end
        # Note: Toga doesn't have built-in scroll_to_end, but text is added at bottom


def main():
    return AutoinputApp(
        "Autoinput",
        "com.autoinput"
    )


if __name__ == "__main__":
    # Filtere "Don't know how to open documents" stderr Warnung
    import io
    import contextlib

    class StderrFilter(io.TextIOWrapper):
        def write(self, message):
            if "Don't know how to open documents with extension" not in message:
                return super().write(message)
            return len(message)

    # Ersetze stderr mit Filter
    original_stderr = sys.stderr
    sys.stderr = StderrFilter(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

    try:
        main().main_loop()
    finally:
        sys.stderr = original_stderr
