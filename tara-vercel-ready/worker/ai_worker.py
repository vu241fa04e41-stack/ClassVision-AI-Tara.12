"""Local AI worker for physical USB/IP cameras.

Run this on the computer/server that can actually access the cameras.
It sends lightweight metrics to the Vercel Flask API.

Examples:
  python worker/ai_worker.py --camera 1 --source 0
  python worker/ai_worker.py --camera 2 --source 1
  python worker/ai_worker.py --camera 3 --source https://example.com/mjpeg
"""

from __future__ import annotations

import argparse
import os
import time

import cv2
import requests
from ultralytics import YOLO


def parse_source(value: str):
    try:
        return int(value)
    except ValueError:
        return value


def analyze(model, frame):
    results = model(frame, verbose=False)
    persons = 0
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 0:
                persons += 1
    attention = 90 if persons else 0
    activity = "No Activity" if persons == 0 else ("High Activity" if persons > 60 else "Normal Activity")
    return persons, attention, activity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, required=True, choices=range(1, 26))
    parser.add_argument("--source", required=True)
    parser.add_argument("--api", default=os.getenv("VERCEL_API_URL", "http://127.0.0.1:5000"))
    parser.add_argument("--key", default=os.getenv("WORKER_API_KEY", ""))
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args()

    model = YOLO("models/yolo11n.pt")
    source = parse_source(args.source)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open camera source: {source}")

    endpoint = args.api.rstrip("/") + f"/api/cameras/{args.camera}/heartbeat"
    headers = {"X-Worker-Key": args.key} if args.key else {}

    try:
        last_send = 0.0
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(1)
                continue

            persons, attention, activity = analyze(model, frame)
            now = time.time()
            if now - last_send >= args.interval:
                response = requests.post(
                    endpoint,
                    json={
                        "status": "online",
                        "students": persons,
                        "attention": attention,
                        "activity": activity,
                    },
                    headers=headers,
                    timeout=10,
                )
                response.raise_for_status()
                print(f"Camera {args.camera}: {persons} persons | {activity}")
                last_send = now
    finally:
        cap.release()


if __name__ == "__main__":
    main()
