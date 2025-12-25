#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roblox Autoclicker - Toga GUI
Native macOS GUI mit Toga (BeeWare)
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class RobloxAutoclickerApp(toga.App):
    def startup(self):
        """Wird beim App-Start aufgerufen"""

        # Haupt-Container
        main_box = toga.Box(style=Pack(direction=COLUMN))

        # Header
        header = toga.Box(style=Pack(
            direction=ROW,
            padding=20,
            background_color="#667eea"
        ))

        title = toga.Label(
            "🎮 Roblox Autoclicker",
            style=Pack(
                padding=10,
                font_size=20,
                font_weight="bold",
                color="#ffffff"
            )
        )
        header.add(title)
        main_box.add(header)

        # Tab Container
        option_container = toga.OptionContainer(
            style=Pack(flex=1, padding=10)
        )

        # Tab 1: Steuerung & Logs
        control_tab = self.create_control_tab()
        option_container.add("⚡ Steuerung & Logs", control_tab)

        # Tab 2: Konfiguration
        config_tab = self.create_config_tab()
        option_container.add("⚙️  Konfiguration", config_tab)

        # Tab 3: Klick-Test
        test_tab = self.create_test_tab()
        option_container.add("🎯 Klick-Test", test_tab)

        main_box.add(option_container)

        # Footer
        footer = toga.Box(style=Pack(
            direction=ROW,
            padding=10,
            background_color="#f1f5f9"
        ))

        footer_label = toga.Label(
            "Drücke die Hotkey-Taste zum Aktivieren | ESC oder Strg+C zum Beenden",
            style=Pack(padding=5, font_size=9, color="#64748b")
        )
        footer.add(footer_label)
        main_box.add(footer)

        # Haupt-Fenster
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def create_control_tab(self):
        """Tab für Start/Stop und Logs"""
        box = toga.Box(style=Pack(direction=COLUMN, padding=20))

        # Status
        status_box = toga.Box(style=Pack(direction=ROW, padding=10))
        self.status_label = toga.Label(
            "⚫ Gestoppt",
            style=Pack(font_size=14, font_weight="bold")
        )
        status_box.add(self.status_label)
        box.add(status_box)

        # Buttons
        button_box = toga.Box(style=Pack(direction=ROW, padding=10))

        start_btn = toga.Button(
            "▶️  Starten",
            on_press=self.start_autoclicker,
            style=Pack(padding=5)
        )
        button_box.add(start_btn)

        stop_btn = toga.Button(
            "⏹️  Stoppen",
            on_press=self.stop_autoclicker,
            style=Pack(padding=5)
        )
        button_box.add(stop_btn)

        clear_btn = toga.Button(
            "🗑️  Logs löschen",
            on_press=self.clear_logs,
            style=Pack(padding=5)
        )
        button_box.add(clear_btn)

        box.add(button_box)

        # Log Area
        log_label = toga.Label(
            "📋 Live Logs:",
            style=Pack(padding=10, font_weight="bold")
        )
        box.add(log_label)

        self.log_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, padding=10)
        )
        box.add(self.log_text)

        return box

    def create_config_tab(self):
        """Tab für Konfiguration"""
        box = toga.Box(style=Pack(direction=COLUMN, padding=20))

        # CPS
        cps_label = toga.Label("Klicks pro Sekunde (CPS):", style=Pack(padding=5))
        box.add(cps_label)

        self.cps_input = toga.NumberInput(
            min_value=1,
            max_value=1000,
            value=12,
            style=Pack(padding=5)
        )
        box.add(self.cps_input)

        # Hotkey
        hotkey_label = toga.Label("Aktivierungs-Hotkey:", style=Pack(padding=5))
        box.add(hotkey_label)

        self.hotkey_selection = toga.Selection(
            items=['shift', 'shift_r', 'ctrl', 'ctrl_r', 'alt', 'alt_r',
                   'space', 'tab', 'f6', 'f7', 'f8', 'f9'],
            style=Pack(padding=5)
        )
        box.add(self.hotkey_selection)

        # Save Button
        save_btn = toga.Button(
            "💾 Konfiguration speichern",
            on_press=self.save_config,
            style=Pack(padding=20)
        )
        box.add(save_btn)

        return box

    def create_test_tab(self):
        """Tab für Klick-Test"""
        box = toga.Box(style=Pack(direction=COLUMN, padding=20))

        title = toga.Label(
            "🎯 Klick-Test Bereich",
            style=Pack(padding=10, font_size=16, font_weight="bold")
        )
        box.add(title)

        info = toga.Label(
            "Klicke auf den Button unten, um deine Clicking-Geschwindigkeit zu testen",
            style=Pack(padding=5, font_size=10)
        )
        box.add(info)

        # Test Button
        self.test_btn = toga.Button(
            "Klick mich! (0)",
            on_press=self.register_test_click,
            style=Pack(padding=20)
        )
        box.add(self.test_btn)

        # Reset Button
        reset_btn = toga.Button(
            "🔄 Test zurücksetzen",
            on_press=self.reset_click_test,
            style=Pack(padding=10)
        )
        box.add(reset_btn)

        # Stats
        self.stats_label = toga.Label(
            "Klicks: 0 | CPS: 0",
            style=Pack(padding=10)
        )
        box.add(self.stats_label)

        return box

    # Event Handlers
    def start_autoclicker(self, widget):
        self.status_label.text = "🟢 Läuft"
        self.log("▶️  Autoclicker gestartet!")

    def stop_autoclicker(self, widget):
        self.status_label.text = "⚫ Gestoppt"
        self.log("⏹️  Autoclicker gestoppt!")

    def clear_logs(self, widget):
        self.log_text.value = ""

    def save_config(self, widget):
        self.main_window.info_dialog("Erfolg", "Konfiguration gespeichert!")

    def register_test_click(self, widget):
        # TODO: Implementiere CPS-Zählung
        self.test_btn.text = "Klick mich! (1)"

    def reset_click_test(self, widget):
        self.test_btn.text = "Klick mich! (0)"
        self.stats_label.text = "Klicks: 0 | CPS: 0"

    def log(self, message):
        """Fügt eine Log-Nachricht hinzu"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        current = self.log_text.value or ""
        self.log_text.value = f"{current}[{timestamp}] {message}\n"


def main():
    return RobloxAutoclickerApp(
        "Roblox Autoclicker",
        "com.roblox.autoclicker"
    )


if __name__ == "__main__":
    main().main_loop()
