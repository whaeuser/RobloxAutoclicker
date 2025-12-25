#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roblox Autoclicker GUI
Grafische Oberfläche zum Starten/Stoppen des Autoclickers mit Live-Log-Anzeige und Konfiguration
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import signal
import yaml
from pathlib import Path
from datetime import datetime
import time

class AutoclickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Roblox Autoclicker")
        self.root.geometry("1100x850")  # Höhe erhöht für Reset-Button Sichtbarkeit

        self.process = None
        self.config_path = Path(__file__).parent / "config.yaml"

        # Klick-Test Variablen
        self.click_count = 0
        self.click_start_time = None
        self.click_timestamps = []
        self.last_click_time = None  # Für Auto-Pause
        self.frozen_duration = 0  # Gefrorene Dauer bei Pause

        self.setup_ui()
        self.load_config()
        self.update_cps_display()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#667eea", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(header, text="🎮 Roblox Autoclicker",
                        font=("SF Pro", 20, "bold"),
                        bg="#667eea", fg="white")
        title.pack(pady=15)

        # Main Container mit Notebook (Tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Steuerung & Logs
        control_tab = tk.Frame(notebook)
        notebook.add(control_tab, text="⚡ Steuerung & Logs")
        self.setup_control_tab(control_tab)

        # Tab 2: Konfiguration
        config_tab = tk.Frame(notebook)
        notebook.add(config_tab, text="⚙️  Konfiguration")
        self.setup_config_tab(config_tab)

        # Tab 3: Klick-Test
        test_tab = tk.Frame(notebook)
        notebook.add(test_tab, text="🎯 Klick-Test")
        self.setup_test_tab(test_tab)

        # Footer
        footer = tk.Frame(self.root, bg="#f1f5f9", height=35)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        footer_label = tk.Label(footer, text="Drücke die Hotkey-Taste zum Aktivieren | ESC oder Strg+C zum Beenden",
                               font=("SF Pro", 9), bg="#f1f5f9", fg="#64748b")
        footer_label.pack(pady=8)

    def create_custom_button(self, parent, text, command, bg_color, hover_color, state=tk.NORMAL):
        """Erstellt einen benutzerdefinierten Button mit Canvas für macOS"""
        frame = tk.Frame(parent, bg=bg_color, cursor="hand2" if state == tk.NORMAL else "arrow")

        label = tk.Label(frame, text=text, font=("SF Pro", 12, "bold"),
                        bg=bg_color, fg="white", padx=25, pady=12)
        label.pack()

        # State als Attribut speichern, nicht als Closure-Variable
        frame.button_enabled = (state == tk.NORMAL)
        frame.normal_color = bg_color
        frame.hover_color = hover_color

        if state == tk.DISABLED:
            frame.config(bg="#94a3b8")
            label.config(bg="#94a3b8")

        def on_enter(e):
            if frame.button_enabled:
                frame.config(bg=frame.hover_color)
                label.config(bg=frame.hover_color)

        def on_leave(e):
            if frame.button_enabled:
                frame.config(bg=frame.normal_color)
                label.config(bg=frame.normal_color)

        def on_click(e):
            if frame.button_enabled:
                command()

        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        frame.bind("<Button-1>", on_click)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        label.bind("<Button-1>", on_click)

        return frame, label

    def setup_control_tab(self, parent):
        """Tab für Start/Stop und Logs"""
        # Status Frame
        status_frame = tk.Frame(parent, padx=20, pady=15)
        status_frame.pack(fill=tk.X)

        self.status_label = tk.Label(status_frame, text="⚫ Gestoppt",
                                     font=("SF Pro", 14, "bold"))
        self.status_label.pack(side=tk.LEFT)

        self.config_info = tk.Label(status_frame, text="",
                                    font=("SF Pro", 10), fg="#64748b")
        self.config_info.pack(side=tk.LEFT, padx=20)

        # Buttons
        button_frame = tk.Frame(parent, padx=20, pady=10)
        button_frame.pack(fill=tk.X)

        # Start Button
        self.start_btn_frame, self.start_btn_label = self.create_custom_button(
            button_frame, "▶️  Starten", self.start_autoclicker,
            "#22c55e", "#16a34a", tk.NORMAL
        )
        self.start_btn_frame.pack(side=tk.LEFT, padx=5)

        # Stop Button
        self.stop_btn_frame, self.stop_btn_label = self.create_custom_button(
            button_frame, "⏹️  Stoppen", self.stop_autoclicker,
            "#dc2626", "#b91c1c", tk.DISABLED
        )
        self.stop_btn_frame.pack(side=tk.LEFT, padx=5)

        # Clear Button
        clear_btn_frame, clear_btn_label = self.create_custom_button(
            button_frame, "🗑️  Logs löschen", self.clear_logs,
            "#2563eb", "#1d4ed8", tk.NORMAL
        )
        clear_btn_frame.pack(side=tk.LEFT, padx=5)

        # Log Area
        log_frame = tk.Frame(parent, padx=20, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_label = tk.Label(log_frame, text="📋 Live Logs:",
                            font=("SF Pro", 11, "bold"))
        log_label.pack(anchor=tk.W, pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  font=("Menlo", 9),
                                                  bg="#1e293b", fg="#e2e8f0",
                                                  insertbackground="white",
                                                  relief=tk.FLAT,
                                                  padx=10, pady=10,
                                                  height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    def setup_config_tab(self, parent):
        """Tab für Konfiguration"""
        # Scrollable Frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        config_container = tk.Frame(scrollable_frame, padx=30, pady=20)
        config_container.pack(fill=tk.BOTH, expand=True)

        # CPS
        tk.Label(config_container, text="Klicks pro Sekunde (CPS):",
                font=("SF Pro", 11, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.cps_var = tk.IntVar(value=12)
        self.cps_spinbox = tk.Spinbox(config_container, from_=1, to=1000,
                                      textvariable=self.cps_var,
                                      font=("SF Pro", 11), width=10)
        self.cps_spinbox.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        tk.Label(config_container, text="Empfohlen: 8-20",
                fg="#64748b", font=("SF Pro", 9)).grid(row=0, column=2, sticky=tk.W, padx=10)

        # Hotkey
        tk.Label(config_container, text="Aktivierungs-Hotkey:",
                font=("SF Pro", 11, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(15, 5))
        self.hotkey_var = tk.StringVar(value="shift")
        hotkey_options = ['shift', 'shift_r', 'ctrl', 'ctrl_r', 'alt', 'alt_r',
                         'space', 'tab', 'f6', 'f7', 'f8', 'f9']
        self.hotkey_combo = ttk.Combobox(config_container, textvariable=self.hotkey_var,
                                        values=hotkey_options, state="readonly",
                                        font=("SF Pro", 11), width=15)
        self.hotkey_combo.grid(row=1, column=1, sticky=tk.W, pady=(15, 5))

        # Aktivierungsmodus
        tk.Label(config_container, text="Aktivierungs-Modus:",
                font=("SF Pro", 11, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        self.activation_mode_var = tk.StringVar(value="hold")
        activation_frame = tk.Frame(config_container)
        activation_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=(15, 5))
        tk.Radiobutton(activation_frame, text="Hold (Halten)", variable=self.activation_mode_var,
                      value="hold", font=("SF Pro", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(activation_frame, text="Toggle (Umschalten)", variable=self.activation_mode_var,
                      value="toggle", font=("SF Pro", 10)).pack(side=tk.LEFT, padx=5)

        # Klick-Modus
        tk.Label(config_container, text="Klick-Modus:",
                font=("SF Pro", 11, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(15, 5))
        self.click_mode_var = tk.StringVar(value="fast")
        click_mode_options = [('Fast (Empfohlen)', 'fast'), ('Standard', 'standard'),
                             ('Separate Events', 'separate'), ('Rechtsklick', 'right')]
        click_mode_frame = tk.Frame(config_container)
        click_mode_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=(15, 5))
        for text, value in click_mode_options:
            tk.Radiobutton(click_mode_frame, text=text, variable=self.click_mode_var,
                          value=value, font=("SF Pro", 10)).pack(anchor=tk.W)

        # Position
        tk.Label(config_container, text="Klick-Position:",
                font=("SF Pro", 11, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        pos_frame = tk.Frame(config_container)
        pos_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=(15, 5))

        tk.Label(pos_frame, text="X:", font=("SF Pro", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.pos_x_var = tk.StringVar()
        tk.Entry(pos_frame, textvariable=self.pos_x_var, font=("SF Pro", 10), width=8).pack(side=tk.LEFT, padx=5)

        tk.Label(pos_frame, text="Y:", font=("SF Pro", 10)).pack(side=tk.LEFT, padx=(15, 5))
        self.pos_y_var = tk.StringVar()
        tk.Entry(pos_frame, textvariable=self.pos_y_var, font=("SF Pro", 10), width=8).pack(side=tk.LEFT, padx=5)

        tk.Label(pos_frame, text="(leer = Mausposition)", fg="#64748b",
                font=("SF Pro", 9)).pack(side=tk.LEFT, padx=10)

        # Verbose Mode
        tk.Label(config_container, text="Debug/Verbose-Modus:",
                font=("SF Pro", 11, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(15, 5))
        self.verbose_var = tk.BooleanVar(value=False)
        verbose_check = tk.Checkbutton(config_container, text="Zeige jeden Klick mit Details im Log",
                                      variable=self.verbose_var, font=("SF Pro", 10))
        verbose_check.grid(row=5, column=1, columnspan=2, sticky=tk.W, pady=(15, 5))

        # Save Button
        save_btn = tk.Button(config_container, text="💾 Konfiguration speichern",
                            command=self.save_config,
                            font=("SF Pro", 12, "bold"),
                            bg="#3b82f6", fg="white",
                            padx=30, pady=15,
                            relief=tk.FLAT,
                            cursor="hand2")
        save_btn.grid(row=6, column=0, columnspan=3, pady=30)

    def setup_test_tab(self, parent):
        """Tab für Klick-Test"""
        test_frame = tk.Frame(parent, padx=30, pady=20)
        test_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(test_frame, text="🎯 Klick-Test Bereich",
                font=("SF Pro", 16, "bold")).pack(pady=10)

        tk.Label(test_frame, text="Klicke auf den Kreis unten, um deine Clicking-Geschwindigkeit zu testen",
                font=("SF Pro", 10), fg="#64748b").pack(pady=5)

        # Click Area
        self.click_area = tk.Canvas(test_frame, width=200, height=200,
                                    bg="#f093fb", highlightthickness=0,
                                    cursor="hand2")
        self.click_area.pack(pady=20)

        # Zeichne Kreis
        self.click_area.create_oval(10, 10, 190, 190, fill="#f5576c", outline="")
        self.click_count_text = self.click_area.create_text(100, 100,
                                                             text="0",
                                                             font=("SF Pro", 48, "bold"),
                                                             fill="white")

        self.click_area.bind("<Button-1>", self.register_test_click)

        # Stats
        stats_frame = tk.Frame(test_frame)
        stats_frame.pack(pady=20)

        # Grid für Stats
        stat_labels = [
            ("Aktuelle CPS:", "current_cps"),
            ("Durchschnitt CPS:", "avg_cps"),
            ("Gesamt Klicks:", "total_clicks"),
            ("Dauer (s):", "duration")
        ]

        for idx, (label, attr) in enumerate(stat_labels):
            row, col = idx // 2, (idx % 2) * 2

            stat_box = tk.Frame(stats_frame, bg="#e2e8f0", padx=20, pady=15)
            stat_box.grid(row=row, column=col, padx=10, pady=10)

            tk.Label(stat_box, text=label, font=("SF Pro", 10),
                    bg="#e2e8f0", fg="black").pack()
            label_widget = tk.Label(stat_box, text="0", font=("SF Pro", 20, "bold"),
                                   bg="#e2e8f0", fg="black")
            label_widget.pack()
            setattr(self, f"{attr}_label", label_widget)

        # Reset Button direkt unter Stats
        button_container = tk.Frame(test_frame)
        button_container.pack(pady=15)

        reset_btn_frame, reset_btn_label = self.create_custom_button(
            button_container, "🔄 Test zurücksetzen", self.reset_click_test,
            "#f97316", "#ea580c", tk.NORMAL  # Orange
        )
        reset_btn_frame.pack()

    def load_config(self):
        """Lädt die Konfiguration aus der YAML-Datei"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            self.cps_var.set(config.get('clicks_per_second', 12))
            self.hotkey_var.set(config.get('hotkey', 'shift'))
            self.activation_mode_var.set(config.get('activation_mode', 'hold'))
            self.click_mode_var.set(config.get('click_mode', 'fast'))
            self.verbose_var.set(config.get('verbose_mode', False))

            pos = config.get('target_position')
            if pos and len(pos) == 2:
                self.pos_x_var.set(str(pos[0]))
                self.pos_y_var.set(str(pos[1]))
            else:
                self.pos_x_var.set('')
                self.pos_y_var.set('')

            self.update_config_display(config)
        except Exception as e:
            self.log(f"❌ Fehler beim Laden der Config: {e}")

    def update_config_display(self, config):
        """Aktualisiert die Config-Anzeige im Control-Tab"""
        cps = config.get('clicks_per_second', '?')
        mode = config.get('activation_mode', 'hold')
        mode_text = "Toggle" if mode == 'toggle' else "Hold"
        pos = config.get('target_position')
        pos_text = f"({pos[0]},{pos[1]})" if pos and len(pos) == 2 else "Maus"

        info_text = f"CPS: {cps} | Modus: {mode_text} | Pos: {pos_text}"
        self.config_info.config(text=info_text)

    def save_config(self):
        """Speichert die Konfiguration"""
        try:
            # Position parsen
            pos_x = self.pos_x_var.get().strip()
            pos_y = self.pos_y_var.get().strip()

            if pos_x and pos_y:
                target_position = [int(pos_x), int(pos_y)]
            else:
                target_position = None

            config = {
                'clicks_per_second': self.cps_var.get(),
                'hotkey': self.hotkey_var.get(),
                'activation_mode': self.activation_mode_var.get(),
                'click_mode': self.click_mode_var.get(),
                'target_position': target_position,
                'enable_logging': True,
                'verbose_mode': self.verbose_var.get()
            }

            # Autoclicker stoppen falls er läuft
            was_running = self.process and self.process.poll() is None
            if was_running:
                self.stop_autoclicker()

            # Config speichern
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            self.update_config_display(config)
            self.log("💾 Konfiguration gespeichert!")
            messagebox.showinfo("Erfolg", "✅ Konfiguration erfolgreich gespeichert!")

            # Autoclicker wieder starten falls er vorher lief
            if was_running:
                self.log("🔄 Autoclicker wird neu gestartet...")
                self.root.after(500, self.start_autoclicker)

        except Exception as e:
            self.log(f"❌ Fehler beim Speichern: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{e}")

    def log(self, message):
        """Fügt eine Log-Nachricht hinzu"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_logs(self):
        """Löscht alle Logs"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def read_process_output(self):
        """Liest die Ausgabe des Autoclicker-Prozesses"""
        try:
            for line in iter(self.process.stdout.readline, b''):
                if line:
                    decoded = line.decode('utf-8').strip()
                    if decoded:
                        self.root.after(0, lambda msg=decoded: self.log(msg))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Fehler beim Lesen: {e}"))

    def start_autoclicker(self):
        """Startet den Autoclicker"""
        if self.process and self.process.poll() is None:
            self.log("⚠️  Autoclicker läuft bereits!")
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            activation_mode = config.get('activation_mode', 'hold')

            if activation_mode == 'toggle':
                script_path = Path(__file__).parent / "roblox_autoclicker_toggle.py"
                mode_name = "Toggle"
            else:
                script_path = Path(__file__).parent / "debug_autoclicker.py"
                mode_name = "Hold"

            self.log(f"▶️  Starte Autoclicker ({mode_name}-Modus)...")

            # Umgebungsvariablen für unbuffered output
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'

            self.process = subprocess.Popen(
                ['python3', '-u', str(script_path)],  # -u für unbuffered
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
                env=env,
                preexec_fn=os.setsid
            )

            output_thread = threading.Thread(target=self.read_process_output, daemon=True)
            output_thread.start()

            # Buttons aktualisieren
            self.start_btn_frame.button_enabled = False
            self.start_btn_frame.config(bg="#94a3b8", cursor="arrow")
            self.start_btn_label.config(bg="#94a3b8")

            self.stop_btn_frame.button_enabled = True
            self.stop_btn_frame.normal_color = "#dc2626"
            self.stop_btn_frame.hover_color = "#b91c1c"
            self.stop_btn_frame.config(bg="#dc2626", cursor="hand2")
            self.stop_btn_label.config(bg="#dc2626")

            self.status_label.config(text="🟢 Läuft", fg="#4ade80")

            self.log("✅ Autoclicker gestartet!")

        except Exception as e:
            self.log(f"❌ Fehler beim Starten: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Starten:\n{e}")

    def stop_autoclicker(self):
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

            # Buttons aktualisieren
            self.start_btn_frame.button_enabled = True
            self.start_btn_frame.normal_color = "#22c55e"
            self.start_btn_frame.hover_color = "#16a34a"
            self.start_btn_frame.config(bg="#22c55e", cursor="hand2")
            self.start_btn_label.config(bg="#22c55e")

            self.stop_btn_frame.button_enabled = False
            self.stop_btn_frame.config(bg="#94a3b8", cursor="arrow")
            self.stop_btn_label.config(bg="#94a3b8")

            self.status_label.config(text="⚫ Gestoppt", fg="#64748b")

            self.log("✅ Autoclicker gestoppt!")

        except Exception as e:
            self.log(f"❌ Fehler beim Stoppen: {e}")

    def register_test_click(self, event):
        """Registriert einen Klick im Test-Bereich"""
        self.click_count += 1
        now = time.time()

        if self.click_start_time is None:
            self.click_start_time = now

        self.last_click_time = now  # Letzten Klick-Zeitpunkt speichern
        self.click_timestamps.append(now)
        # Nur letzte Sekunde behalten
        self.click_timestamps = [t for t in self.click_timestamps if now - t < 1.0]

        # Update Display
        self.click_area.itemconfig(self.click_count_text, text=str(self.click_count))
        self.total_clicks_label.config(text=str(self.click_count))

    def update_cps_display(self):
        """Aktualisiert die CPS-Anzeige im Test-Bereich"""
        now = time.time()

        # Filter alte Timestamps
        self.click_timestamps = [t for t in self.click_timestamps if now - t < 1.0]
        current_cps = len(self.click_timestamps)

        self.current_cps_label.config(text=str(current_cps))

        if self.click_start_time and self.click_count > 0:
            # Auto-Pause: Friere Dauer ein, wenn 3 Sekunden nicht geklickt wurde
            if self.last_click_time and (now - self.last_click_time) > 3.0:
                # Pausiert - zeige gefrorene Dauer
                if self.frozen_duration == 0:
                    self.frozen_duration = self.last_click_time - self.click_start_time
                duration = self.frozen_duration
            else:
                # Aktiv - zeige laufende Dauer
                self.frozen_duration = 0
                duration = now - self.click_start_time

            avg_cps = self.click_count / duration if duration > 0 else 0
            self.avg_cps_label.config(text=f"{avg_cps:.1f}")
            self.duration_label.config(text=f"{duration:.1f}")

        self.root.after(100, self.update_cps_display)

    def reset_click_test(self):
        """Setzt den Klick-Test zurück"""
        self.click_count = 0
        self.click_start_time = None
        self.click_timestamps = []
        self.last_click_time = None
        self.frozen_duration = 0

        self.click_area.itemconfig(self.click_count_text, text="0")
        self.current_cps_label.config(text="0")
        self.avg_cps_label.config(text="0")
        self.total_clicks_label.config(text="0")
        self.duration_label.config(text="0")

    def on_closing(self):
        """Wird beim Schließen aufgerufen"""
        if self.process and self.process.poll() is None:
            self.stop_autoclicker()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AutoclickerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
