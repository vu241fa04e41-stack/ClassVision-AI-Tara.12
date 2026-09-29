from __future__ import annotations

from .camera_registry import camera_registry


def build_analytics():
    cameras = camera_registry.list_cameras()
    online = [c for c in cameras if c["status"] == "online"]
    total_students = sum(c["students"] for c in cameras)
    attention_values = [c["attention"] for c in online if c["attention"] > 0]
    attention = round(sum(attention_values) / len(attention_values), 1) if attention_values else 0

    return {
        "total_classes": 25,
        "total_students": total_students,
        "present_today": total_students,
        "attendance": 92 if total_students else 0,
        "total_cameras": 25,
        "online_cameras": len(online),
        "offline_cameras": 25 - len(online),
        "attention": attention,
        "cameras": cameras,
    }
