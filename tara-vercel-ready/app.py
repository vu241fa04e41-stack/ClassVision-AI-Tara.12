from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from services.analytics import build_analytics
from services.camera_registry import camera_registry
from services.database import db

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["JSON_SORT_KEYS"] = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
def dashboard():
    return render_template("dashboard.html", app_name="Vignan AI Classroom")


@app.get("/analytics")
def analytics_page():
    return render_template("analytics.html", app_name="Vignan AI Analytics")


@app.get("/api/health")
def health():
    return jsonify({
        "status": "online",
        "service": "Vignan AI Classroom Monitoring System",
        "time": utc_now(),
        "database": db.backend_name(),
    })


@app.get("/api/dashboard")
def dashboard_api():
    return jsonify(build_analytics())


@app.get("/api/cameras")
def cameras_api():
    return jsonify(camera_registry.list_cameras())


@app.post("/api/cameras/<int:camera_id>/heartbeat")
def camera_heartbeat(camera_id: int):
    payload = request.get_json(silent=True) or {}
    expected_key = os.getenv("WORKER_API_KEY", "")
    supplied_key = request.headers.get("X-Worker-Key", "")
    if expected_key and supplied_key != expected_key:
        return jsonify({"error": "Unauthorized"}), 401

    if not 1 <= camera_id <= 25:
        return jsonify({"error": "Camera ID must be between 1 and 25"}), 400

    camera_registry.update_camera(
        camera_id=camera_id,
        status=payload.get("status", "online"),
        students=int(payload.get("students", 0)),
        attention=float(payload.get("attention", 0)),
        activity=payload.get("activity", "Normal Activity"),
    )
    return jsonify({"ok": True, "camera_id": camera_id, "updated_at": utc_now()})


@app.get("/api/attendance")
def attendance_api():
    return jsonify(db.recent_attendance(limit=50))


@app.post("/api/attendance")
def save_attendance():
    payload = request.get_json(silent=True) or {}
    required = ["classroom", "students", "attendance"]
    missing = [key for key in required if key not in payload]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    db.save_attendance(
        str(payload["classroom"]),
        int(payload["students"]),
        float(payload["attendance"]),
    )
    return jsonify({"ok": True})


@app.get("/api/config")
def config_api():
    return jsonify({
        "camera_count": 25,
        "refresh_seconds": 5,
        "live_camera_urls_configured": camera_registry.live_urls_configured(),
        "ai_worker_enabled": bool(os.getenv("WORKER_API_KEY")),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
