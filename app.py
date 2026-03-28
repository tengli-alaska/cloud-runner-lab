from flask import Flask, jsonify, render_template_string
import datetime
import platform
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alaska's Cloud Runner</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 600px;
            width: 90%;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { color: #aaa; margin-bottom: 30px; font-size: 1.1rem; }
        .info-card {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            text-align: left;
        }
        .info-card h3 { color: #00d2ff; margin-bottom: 8px; }
        .info-card p { color: #ccc; line-height: 1.6; }
        .endpoints { margin-top: 25px; text-align: left; }
        .endpoint {
            background: rgba(0, 210, 255, 0.1);
            border-left: 3px solid #00d2ff;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 0 8px 8px 0;
            font-family: monospace;
            font-size: 0.95rem;
        }
        .badge {
            display: inline-block;
            background: #3a7bd5;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-left: 8px;
            vertical-align: middle;
        }
        footer { margin-top: 30px; color: #666; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>☁️ Alaska's Cloud Runner</h1>
        <p class="subtitle">A containerized Flask app running on Google Cloud Run</p>
        <div class="info-card">
            <h3>📊 Server Info</h3>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            <p><strong>Python:</strong> {{ python_version }}</p>
            <p><strong>Host:</strong> {{ hostname }}</p>
        </div>
        <div class="info-card">
            <h3>🔗 Available Endpoints</h3>
            <div class="endpoints">
                <div class="endpoint">GET / <span class="badge">Home</span></div>
                <div class="endpoint">GET /api/info <span class="badge">JSON</span></div>
                <div class="endpoint">GET /health <span class="badge">Health Check</span></div>
                <div class="endpoint">GET /greet/&lt;name&gt; <span class="badge">Dynamic</span></div>
            </div>
        </div>
        <footer>
            <p>MLOps Lab 5 | Alaska Tengli | Northeastern University</p>
        </footer>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    """Home page with styled HTML dashboard."""
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        python_version=platform.python_version(),
        hostname=platform.node(),
    )


@app.route("/api/info")
def api_info():
    """JSON endpoint returning server and app metadata."""
    return jsonify({
        "app": "Alaska's Cloud Runner",
        "author": "Alaska Tengli",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "environment": os.getenv("ENV", "development"),
    })


@app.route("/health")
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return jsonify({
        "status": "healthy",
        "uptime": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
    }), 200


@app.route("/greet/<name>")
def greet(name):
    """Dynamic greeting endpoint."""
    return jsonify({
        "message": f"Hello, {name}! Welcome to Alaska's Cloud Runner!",
        "timestamp": datetime.datetime.now().isoformat(),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)