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


class AutoinputApp(toga.App):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keine Dokument-Typen akzeptieren
        self._document_types = []

    def startup(self):
        """Wird beim App-Start aufgerufen"""

        # Variablen
        self.process = None
        self.config_path = Path(__file__).parent / "config.yaml"
        self.log_file_path = Path("/tmp/autoinput_toga.log")
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

        # Hotkey
        hotkey_label = toga.Label("Aktivierungs-Hotkey:", style=Pack(margin=(5, 5)))
        box.add(hotkey_label)

        self.hotkey_selection = toga.Selection(
            items=['shift', 'shift_r', 'ctrl', 'ctrl_r', 'alt', 'alt_r',
                   'space', 'tab', 'f6', 'f7', 'f8', 'f9'],
            style=Pack(margin=(5, 5))
        )
        box.add(self.hotkey_selection)

        # Aktivierungsmodus
        mode_label = toga.Label("Aktivierungs-Modus:", style=Pack(margin=(5, 5)))
        box.add(mode_label)

        self.activation_mode_selection = toga.Selection(
            items=['hold', 'toggle'],
            style=Pack(margin=(5, 5))
        )
        box.add(self.activation_mode_selection)

        # Verbose Mode
        self.verbose_switch = toga.Switch(
            "Debug/Verbose-Modus (zeigt jeden Klick)",
            style=Pack(margin=(10, 10))
        )
        box.add(self.verbose_switch)

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

    def load_config(self):
        """Lädt die Konfiguration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            self.cps_input.value = config.get('clicks_per_second', 12)
            self.hotkey_selection.value = config.get('hotkey', 'shift')
            self.activation_mode_selection.value = config.get('activation_mode', 'hold')
            self.verbose_switch.value = config.get('verbose_mode', False)

            self.update_config_display(config)
        except Exception as e:
            self.log(f"❌ Fehler beim Laden der Config: {e}")

    def update_config_display(self, config):
        """Aktualisiert die Config-Anzeige"""
        cps = config.get('clicks_per_second', '?')
        mode = config.get('activation_mode', 'hold')
        mode_text = "Toggle" if mode == 'toggle' else "Hold"

        self.config_info.text = f"CPS: {cps} | Modus: {mode_text}"

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
                'verbose_mode': self.verbose_switch.value
            }

            # Autoclicker stoppen falls er läuft
            was_running = self.process and self.process.poll() is None
            if was_running:
                self.stop_autoclicker(None)

            # Config speichern
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            self.update_config_display(config)
            self.log("💾 Konfiguration gespeichert!")
            self.main_window.dialog(toga.InfoDialog("Erfolg", "✅ Konfiguration erfolgreich gespeichert!"))

            # Autoclicker wieder starten falls er vorher lief
            if was_running:
                self.log("🔄 Autoclicker wird neu gestartet...")
                import threading
                t = threading.Timer(0.5, self.start_autoclicker, args=[None])
                t.daemon = True
                t.start()

        except Exception as e:
            self.log(f"❌ Fehler beim Speichern: {e}")
            self.main_window.dialog(toga.ErrorDialog("Fehler", f"Fehler beim Speichern:\n{e}"))

    def start_autoclicker(self, widget):
        """Startet den Autoclicker"""
        if self.process and self.process.poll() is None:
            self.log("⚠️  Autoclicker läuft bereits!")
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            activation_mode = config.get('activation_mode', 'hold')

            if activation_mode == 'toggle':
                script_path = Path(__file__).parent / "autoinput_toggle.py"
                mode_name = "Toggle"
            else:
                script_path = Path(__file__).parent / "debug_autoinput.py"
                mode_name = "Hold"

            self.log(f"▶️  Starte Autoclicker ({mode_name}-Modus)...")

            # Umgebungsvariablen für unbuffered output
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'

            # Öffne Log-Datei zum Schreiben
            self.log_file_handle = open(self.log_file_path, 'w', buffering=1)
            self.log_file_position = 0

            # Starte Subprocess mit Output in Log-Datei
            self.process = subprocess.Popen(
                ['python3', '-u', str(script_path)],
                stdout=self.log_file_handle,
                stderr=subprocess.STDOUT,
                env=env,
                preexec_fn=os.setsid
            )

            # Buttons aktualisieren
            self.start_btn.enabled = False
            self.stop_btn.enabled = True
            self.status_label.text = "🟢 Läuft"

            self.log("✅ Autoclicker gestartet!")
            self.log("💡 Klicke auf '🔄 Logs aktualisieren' um die Autoclicker-Logs zu sehen")

        except Exception as e:
            self.log(f"❌ Fehler beim Starten: {e}")
            self.main_window.dialog(toga.ErrorDialog("Fehler", f"Fehler beim Starten:\n{e}"))

    def stop_autoclicker(self, widget):
        """Stoppt den Autoclicker"""
        if not self.process or self.process.poll() is not None:
            self.log("⚠️  Autoclicker läuft nicht!")
            return

        try:
            self.log("⏹️  Stoppe Autoclicker...")

            # Versuche zuerst SIGTERM
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=2)
            except:
                # Falls SIGTERM nicht funktioniert, versuche SIGKILL
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    self.process.wait(timeout=2)
                except:
                    # Letzter Versuch: direkt kill
                    self.process.kill()
                    self.process.wait(timeout=2)

            self.process = None

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
