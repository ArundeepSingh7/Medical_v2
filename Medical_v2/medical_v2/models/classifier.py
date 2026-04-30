import time
import torch
from medical_v2.models.vit_model import predict_vit



ALL_CLASSES = set()


TRAINED_CLASSES = []


URGENT_CONDITIONS = {
    "melanoma",
    "basal cell carcinoma",
    "squamous cell carcinoma"
}


def load_model():
    return True


def predict(image_bytes: bytes) -> dict:
    global ALL_CLASSES

    t0 = time.perf_counter()

    try:
        raw_predictions = predict_vit(image_bytes)
    except Exception:
        raw_predictions = []

    top_predictions = []
    for item in raw_predictions:
        label = item["condition"].strip()
        top_predictions.append({
            "condition": label,
            "confidence": item["confidence"]
        })

    if not top_predictions:
        return {
            "condition": "Uncertain",
            "confidence": 0,
            "status": "uncertain",
            "is_urgent": False,
            "top_predictions": [],
            "inference_ms": 0,
            "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu")),
        }

    print("\n🔥 ALL PREDICTIONS:\n")

    for p in top_predictions:
        name = p["condition"]
        ALL_CLASSES.add(name)
        print(f"{name} : {p['confidence']:.2f}%")

    print("\n🔥 ALL CLASSES DISCOVERED:\n")
    for c in sorted(ALL_CLASSES):
        print(c)

    top1 = top_predictions[0]
    condition = top1["condition"].strip()
    condition_lower = condition.lower()
    confidence = top1["confidence"]

    status = "confident" if confidence >= 70 else "uncertain"

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    return {
        "condition": condition,
        "confidence": confidence,
        "status": status,
        "is_urgent": condition_lower in URGENT_CONDITIONS,
        "top_predictions": top_predictions,
        "inference_ms": elapsed_ms,
        "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu")),
    }