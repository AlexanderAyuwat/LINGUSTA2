"""
Linguista – FastAPI backend
Run: uvicorn server:app --reload --port 8000
"""
import asyncio
import base64
import json
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sign_predictor import SignLanguagePredictor

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Linguista")


# ── Helpers ────────────────────────────────────────────────────────────────────
def _convert(obj):
    """Recursively convert numpy types to native Python for JSON."""
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _convert(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert(i) for i in obj]
    return obj


def safe_json(result: dict) -> str:
    return json.dumps(_convert(result))


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    # Each connection gets its own predictor so the internal frame-buffer
    # is independent per-client (mirrors the old VideoProcessor pattern).
    predictor = SignLanguagePredictor(confidence_threshold=0.2)
    loop = asyncio.get_event_loop()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                encoded = data.split(",", 1)[1] if "," in data else data
                img_bytes = base64.b64decode(encoded)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is None:
                    continue

                # process_frame only accepts the frame argument (no kwargs).
                # The predictor already does cv2.flip internally, so we pass raw.
                _, raw = await loop.run_in_executor(None, predictor.process_frame, img)

                conf      = float(raw.get("confidence", 0.0))
                pred_str  = str(raw.get("prediction", "Collecting..."))

                # Build a normalised result the frontend understands
                result = {
                    "prediction":     pred_str,
                    "display_label":  pred_str,          # already English from predictor
                    "confidence":     conf,
                    "is_confident":   conf >= 0.70 and not pred_str.startswith(("Collecting", "Uncertain", "ERROR")),
                    "frames_collected": int(raw.get("frames_collected", 0)),
                    "frames_needed":    int(raw.get("frames_needed", 45)),
                    "top3": [
                        {"label": str(t["label"]), "confidence": float(t["confidence"])}
                        for t in raw.get("top3", [])
                    ],
                }
                await websocket.send_text(json.dumps(result))

            except Exception as exc:
                await websocket.send_text(json.dumps({
                    "prediction": "Error",
                    "display_label": "Error",
                    "confidence": 0.0,
                    "is_confident": False,
                    "frames_collected": 0,
                    "frames_needed": 45,
                    "top3": [],
                    "error": str(exc),
                }))

    except WebSocketDisconnect:
        pass


# ── Static files ───────────────────────────────────────────────────────────────
_assets_dir = BASE_DIR / "assets"
if _assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
