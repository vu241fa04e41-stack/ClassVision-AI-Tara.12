from __future__ import annotations

import os
from datetime import datetime, timezone
from threading import Lock


class CameraRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._cameras = {}
        for camera_id in range(1, 26):
            self._cameras[camera_id] = {
                "id": camera_id,
                "name": f"Classroom A{100 + camera_id}",
                "status": "offline",
                "students": 0,
                "attention": 0,
                "activity": "Waiting for AI worker",
                "last_update": None,
                "stream_url": os.getenv(f"CAMERA_URL_{camera_id}", ""),
            }

    def list_cameras(self):
        with self._lock:
            return list(self._cameras.values())

    def update_camera(self, camera_id, status, students, attention, activity):
        with self._lock:
            camera = self._cameras[camera_id]
            camera.update({
                "status": status,
                "students": students,
                "attention": attention,
                "activity": activity,
                "last_update": datetime.now(timezone.utc).isoformat(),
            })

    def live_urls_configured(self) -> int:
        with self._lock:
            return sum(bool(c["stream_url"]) for c in self._cameras.values())


camera_registry = CameraRegistry()
