import os
import subprocess

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

DOWNLOAD_DIR = "/downloads"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Music Downloader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 24px;
            font-size: 24px;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        input:focus {
            outline: none;
            border-color: #007bff;
        }
        button {
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover:not(:disabled) {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .status {
            padding: 12px 16px;
            border-radius: 8px;
            margin-top: 16px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.loading {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>BlackCandy Music Downloader</h1>
        <div class="input-group">
            <input type="text" id="urlInput" placeholder="Paste YouTube URL here...">
            <button onclick="download()">Download</button>
        </div>
        <div id="status" class="status"></div>
    </div>

    <script>
        const urlInput = document.getElementById('urlInput');
        const status = document.getElementById('status');

        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') download();
        });

        async function download() {
            const url = urlInput.value.trim();

            if (!url) {
                showStatus('Please enter a URL', 'error');
                return;
            }

            const button = document.querySelector('button');
            button.disabled = true;
            showStatus('Downloading...', 'loading');

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                const data = await response.json();

                if (response.ok) {
                    showStatus('✓ Download completed!', 'success');
                    urlInput.value = '';
                } else {
                    showStatus('✗ ' + (data.error || 'Download failed'), 'error');
                }
            } catch (error) {
                showStatus('✗ Network error: ' + error.message, 'error');
            } finally {
                button.disabled = false;
            }
        }

        function showStatus(message, type) {
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        subprocess.run(
            [
                "yt-dlp",
                "-x",
                "--audio-format",
                "opus",
                "--audio-quality",
                "0",
                "--embed-thumbnail",
                "--add-metadata",
                "-o",
                os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
                url,
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=300,
        )

        return jsonify({"success": True, "message": "Download completed"})

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Download timed out"}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Download failed", "details": e.stderr}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
