from __future__ import annotations

from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "yolo11n.pt"

_model = None


def get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO
        _model = YOLO(str(MODEL_PATH))
    return _model


def detect_persons(frame):
    model = get_model()
    results = model(frame, verbose=False)
    persons = 0
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 0:
                persons += 1
    return persons, results[0].plot()
