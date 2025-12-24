#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web-Controller für Roblox Autoclicker
Ermöglicht Start/Stop und Config-Verwaltung über Web-Interface
"""

from flask import Flask, render_template_string, request, jsonify
import yaml
import subprocess
import os
import signal
from pathlib import Path

app = Flask(__name__)

# Globale Variablen
autoclicker_process = None
config_path = Path(__file__).parent / "config.yaml"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Autoclicker Controller</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
        }

        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }

        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .card h2 {
            font-size: 1.8em;
            margin-bottom: 20px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 10px;
        }

        .status-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }

        .status-running {
            background: #4ade80;
            box-shadow: 0 0 20px #4ade80;
        }

        .status-stopped {
            background: #f87171;
            box-shadow: 0 0 20px #f87171;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .control-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            font-size: 1.1em;
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid white;
            color: white;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
        }

        button:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .btn-start {
            background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
            border-color: #4ade80;
        }

        .btn-stop {
            background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
            border-color: #f87171;
        }

        .btn-save {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            border-color: #3b82f6;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            font-size: 1.1em;
        }

        input, select {
            width: 100%;
            padding: 12px;
            font-size: 1em;
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: white;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        input:focus, select:focus {
            outline: none;
            border-color: white;
            background: rgba(255, 255, 255, 0.3);
        }

        input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }

        select option {
            background: #667eea;
            color: white;
        }

        .click-test-area {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            width: 200px;
            height: 200px;
            margin: 20px auto;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: all 0.1s ease;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
            user-select: none;
        }

        .click-test-area:hover {
            transform: scale(1.05);
        }

        .click-test-area:active {
            transform: scale(0.95);
        }

        .click-count {
            font-size: 3em;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }

        .stat-box {
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
        }

        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .alert-success {
            background: rgba(74, 222, 128, 0.3);
            border: 2px solid #4ade80;
        }

        .alert-error {
            background: rgba(248, 113, 113, 0.3);
            border: 2px solid #f87171;
        }

        .help-text {
            font-size: 0.9em;
            opacity: 0.7;
            margin-top: 5px;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        code {
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 Roblox Autoclicker</h1>
            <div class="subtitle">Web Controller</div>
        </header>

        <div id="alertContainer"></div>

        <div class="grid">
            <!-- Status & Steuerung -->
            <div class="card">
                <h2>
                    <span class="status-indicator" id="statusIndicator"></span>
                    Status & Steuerung
                </h2>

                <div style="font-size: 1.2em; margin-bottom: 20px;">
                    Status: <strong id="statusText">Gestoppt</strong>
                </div>

                <div class="control-buttons">
                    <button class="btn-start" onclick="startAutoclicker()" id="btnStart">
                        ▶️ Starten
                    </button>
                    <button class="btn-stop" onclick="stopAutoclicker()" id="btnStop" disabled>
                        ⏹️ Stoppen
                    </button>
                </div>

                <div style="margin-top: 30px; padding: 20px; background: rgba(0, 0, 0, 0.2); border-radius: 10px;">
                    <strong>ℹ️ Hinweise:</strong><br>
                    • <strong>Hold-Modus:</strong> Taste halten = Clicking aktiv<br>
                    • <strong>Toggle-Modus:</strong> Taste drücken = Ein/Aus umschalten<br>
                    • <strong>ESC</strong> = Autoclicker beenden<br>
                    • Stelle sicher dass Python <strong>Accessibility-Berechtigung</strong> hat!
                </div>
            </div>

            <!-- Konfiguration -->
            <div class="card">
                <h2>⚙️ Konfiguration</h2>

                <form id="configForm" onsubmit="saveConfig(event)">
                    <div class="form-group">
                        <label for="cps">Klicks pro Sekunde (CPS)</label>
                        <input type="number" id="cps" name="cps" min="1" max="1000" value="12" required>
                        <div class="help-text">Empfohlen: 8-20 für normale Nutzung</div>
                    </div>

                    <div class="form-group">
                        <label for="hotkey">Aktivierungs-Hotkey</label>
                        <select id="hotkey" name="hotkey" required>
                            <option value="shift">Shift (Links)</option>
                            <option value="shift_r">Shift (Rechts)</option>
                            <option value="ctrl">Strg (Links)</option>
                            <option value="ctrl_r">Strg (Rechts)</option>
                            <option value="alt">Alt (Links)</option>
                            <option value="alt_r">Alt (Rechts)</option>
                            <option value="space">Leertaste</option>
                            <option value="tab">Tab</option>
                            <option value="f6">F6</option>
                            <option value="f7">F7</option>
                            <option value="f8">F8</option>
                            <option value="f9">F9</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="activationMode">Aktivierungs-Modus</label>
                        <select id="activationMode" name="activationMode" required>
                            <option value="hold">Hold (Halten)</option>
                            <option value="toggle">Toggle (Umschalten)</option>
                        </select>
                        <div class="help-text">Hold = Klickt beim Halten | Toggle = Ein/Aus bei jedem Druck</div>
                    </div>

                    <div class="form-group">
                        <label for="clickMode">Klick-Modus</label>
                        <select id="clickMode" name="clickMode" required>
                            <option value="fast">Fast (Empfohlen)</option>
                            <option value="standard">Standard</option>
                            <option value="separate">Separate Events</option>
                            <option value="right">Rechtsklick</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="targetX">Position X (leer = Mausposition)</label>
                        <input type="number" id="targetX" name="targetX" placeholder="z.B. 500">
                        <div class="help-text">Optional: Feste X-Koordinate</div>
                    </div>

                    <div class="form-group">
                        <label for="targetY">Position Y (leer = Mausposition)</label>
                        <input type="number" id="targetY" name="targetY" placeholder="z.B. 300">
                        <div class="help-text">Optional: Feste Y-Koordinate</div>
                    </div>

                    <button type="submit" class="btn-save" style="width: 100%;">
                        💾 Konfiguration speichern
                    </button>
                </form>
            </div>

            <!-- Klick-Test -->
            <div class="card full-width">
                <h2>🎯 Klick-Test</h2>

                <div class="click-test-area" id="clickArea" onmousedown="registerClick()">
                    <div class="click-count" id="clickCount">0</div>
                </div>

                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-label">Aktuelle CPS</div>
                        <div class="stat-value" id="currentCPS">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Durchschnitt CPS</div>
                        <div class="stat-value" id="avgCPS">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Gesamt Klicks</div>
                        <div class="stat-value" id="totalClicks">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Dauer (s)</div>
                        <div class="stat-value" id="duration">0</div>
                    </div>
                </div>

                <button onclick="resetClickTest()" style="width: 100%; margin-top: 15px;">
                    🔄 Test zurücksetzen
                </button>
            </div>
        </div>
    </div>

    <script>
        // Klick-Test Variablen
        let clickCount = 0;
        let startTime = null;
        let clickTimestamps = [];

        // Config beim Laden holen
        window.onload = function() {
            loadConfig();
            updateStatus();
            setInterval(updateStatus, 2000);
            setInterval(updateCPS, 100);
        };

        function loadConfig() {
            fetch('/api/config')
                .then(r => r.json())
                .then(config => {
                    document.getElementById('cps').value = config.clicks_per_second;
                    document.getElementById('hotkey').value = config.hotkey;
                    document.getElementById('clickMode').value = config.click_mode;
                    document.getElementById('activationMode').value = config.activation_mode || 'hold';

                    if (config.target_position && config.target_position.length === 2) {
                        document.getElementById('targetX').value = config.target_position[0];
                        document.getElementById('targetY').value = config.target_position[1];
                    }
                })
                .catch(err => showAlert('Fehler beim Laden der Config', 'error'));
        }

        function saveConfig(event) {
            event.preventDefault();

            const targetX = document.getElementById('targetX').value;
            const targetY = document.getElementById('targetY').value;

            let targetPosition = null;
            if (targetX && targetY) {
                targetPosition = [parseInt(targetX), parseInt(targetY)];
            }

            const config = {
                clicks_per_second: parseInt(document.getElementById('cps').value),
                hotkey: document.getElementById('hotkey').value,
                click_mode: document.getElementById('clickMode').value,
                activation_mode: document.getElementById('activationMode').value,
                target_position: targetPosition,
                enable_logging: true
            };

            fetch('/api/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(r => r.json())
            .then(result => {
                showAlert('✅ Konfiguration erfolgreich gespeichert!', 'success');
            })
            .catch(err => showAlert('❌ Fehler beim Speichern', 'error'));
        }

        function startAutoclicker() {
            fetch('/api/start', {method: 'POST'})
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        showAlert('✅ Autoclicker gestartet!', 'success');
                        updateStatus();
                    } else {
                        showAlert('❌ ' + result.error, 'error');
                    }
                })
                .catch(err => showAlert('❌ Fehler beim Starten', 'error'));
        }

        function stopAutoclicker() {
            fetch('/api/stop', {method: 'POST'})
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        showAlert('✅ Autoclicker gestoppt!', 'success');
                        updateStatus();
                    } else {
                        showAlert('❌ ' + result.error, 'error');
                    }
                })
                .catch(err => showAlert('❌ Fehler beim Stoppen', 'error'));
        }

        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(status => {
                    const indicator = document.getElementById('statusIndicator');
                    const text = document.getElementById('statusText');
                    const btnStart = document.getElementById('btnStart');
                    const btnStop = document.getElementById('btnStop');

                    if (status.running) {
                        indicator.className = 'status-indicator status-running';
                        text.textContent = 'Läuft';
                        btnStart.disabled = true;
                        btnStop.disabled = false;
                    } else {
                        indicator.className = 'status-indicator status-stopped';
                        text.textContent = 'Gestoppt';
                        btnStart.disabled = false;
                        btnStop.disabled = true;
                    }
                });
        }

        function showAlert(message, type) {
            const container = document.getElementById('alertContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            container.appendChild(alert);

            setTimeout(() => alert.remove(), 5000);
        }

        // Klick-Test Funktionen
        function registerClick() {
            clickCount++;
            const now = Date.now();

            if (startTime === null) {
                startTime = now;
            }

            clickTimestamps.push(now);
            clickTimestamps = clickTimestamps.filter(t => now - t < 1000);

            document.getElementById('clickCount').textContent = clickCount;
            document.getElementById('totalClicks').textContent = clickCount;
            document.getElementById('currentCPS').textContent = clickTimestamps.length;

            if (startTime !== null) {
                const totalSeconds = (now - startTime) / 1000;
                const avgCPS = totalSeconds > 0 ? (clickCount / totalSeconds).toFixed(1) : 0;
                document.getElementById('avgCPS').textContent = avgCPS;
                document.getElementById('duration').textContent = totalSeconds.toFixed(1);
            }
        }

        function updateCPS() {
            const now = Date.now();
            clickTimestamps = clickTimestamps.filter(t => now - t < 1000);
            document.getElementById('currentCPS').textContent = clickTimestamps.length;
        }

        function resetClickTest() {
            clickCount = 0;
            startTime = null;
            clickTimestamps = [];
            document.getElementById('clickCount').textContent = '0';
            document.getElementById('totalClicks').textContent = '0';
            document.getElementById('currentCPS').textContent = '0';
            document.getElementById('avgCPS').textContent = '0';
            document.getElementById('duration').textContent = '0';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config', methods=['GET'])
def get_config():
    """Lädt die aktuelle Konfiguration"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def save_config():
    """Speichert die Konfiguration"""
    try:
        config = request.json
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def start_autoclicker():
    """Startet den Autoclicker"""
    global autoclicker_process

    try:
        if autoclicker_process and autoclicker_process.poll() is None:
            return jsonify({'success': False, 'error': 'Autoclicker läuft bereits'})

        # Config laden um activation_mode zu lesen
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        activation_mode = config.get('activation_mode', 'hold')

        # Wähle das richtige Skript basierend auf dem Modus
        if activation_mode == 'toggle':
            script_path = Path(__file__).parent / "roblox_autoclicker_toggle.py"
        else:
            script_path = Path(__file__).parent / "debug_autoclicker.py"

        autoclicker_process = subprocess.Popen(
            ['python3', str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_autoclicker():
    """Stoppt den Autoclicker"""
    global autoclicker_process

    try:
        if autoclicker_process and autoclicker_process.poll() is None:
            os.killpg(os.getpgid(autoclicker_process.pid), signal.SIGTERM)
            autoclicker_process.wait(timeout=5)
            autoclicker_process = None
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Autoclicker läuft nicht'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Gibt den Status des Autoclickers zurück"""
    global autoclicker_process

    running = autoclicker_process is not None and autoclicker_process.poll() is None
    return jsonify({'running': running})

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🌐 Roblox Autoclicker Web Controller")
    print("=" * 70)
    print("\n📍 Öffne im Browser: http://localhost:8080")
    print("🛑 Beenden mit: Strg+C\n")

    app.run(host='0.0.0.0', port=8080, debug=False)
