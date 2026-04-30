import io
import logging
import time
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import BaseModel
from models.medical_advice import DISEASE_INFO
import sys
import os



def normalize_condition_name(name: str) -> str:
    return name.strip()


logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("skin-api")

MAX_FILE_SIZE = 10 * 1024 * 1024


app = FastAPI(
    title="Skin Disease Screening API",
    description="ViT + RAG + LLM Skin Disease Detection System — for informational use only",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_classifier = None




def get_classifier():
    global _classifier
    if _classifier is None:
        from models.classifier import load_vit
        load_model()
        from models import classifier
        _classifier = classifier
        logger.info("Classifier loaded")
    return _classifier


@app.on_event("startup")
async def startup():
    logger.info("Starting up — skipping heavy model load")




class PredictResponse(BaseModel):
    condition: str
    confidence: float
    is_urgent: bool
    status: str
    subtypes: str
    definition: str
    advice: str
    ai_generated: bool
    inference_ms: float
    device: str
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    ollama_available: bool
    ollama_model: str
    classes: int




@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    from models.classifier import TRAINED_CLASSES
    return {
        "status":           "ok",
        "model_loaded":     _classifier is not None,
        "ollama_available": False,
        "ollama_model": "disabled",
        "classes":          len(TRAINED_CLASSES),
    }

@app.get("/classes", tags=["System"])
async def list_classes():
    from models.classifier import TRAINED_CLASSES, URGENT_CONDITIONS
    return {
        "total":   len(TRAINED_CLASSES),
        "classes": TRAINED_CLASSES,
        "urgent":  list(URGENT_CONDITIONS),
    }

@app.post("/predict", tags=["Screening"])
async def predict(
    file: UploadFile = File(..., description="Skin image (JPG/PNG/WEBP, max 10MB)"),
    language: str = Form("English")
):


    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    image_bytes = await file.read()

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Image too large. Max 10 MB.")

    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid or corrupted image file.")

    t0 = time.perf_counter()
    try:
        clf    = get_classifier()
        result = {
        "condition": "test",
        "confidence": 99,
        "status": "confident",
        "top_predictions": [{"condition": "test", "confidence": 99}]
    }


        top_predictions = result.get("top_predictions", [])

        if not top_predictions:
            def generate():
                yield "__META__|Uncertain|0|Uncertain\n"
                yield "Unable to determine condition."

            return StreamingResponse(generate(), media_type="text/plain")


        top1 = top_predictions[0]

        confidence = top1["confidence"]

        if confidence < 50:
            result["condition"] = "Uncertain"
            result["status"] = "uncertain"

        elif 50 <= confidence < 85:
            result["condition"] = top1["condition"]
            result["status"] = "low_confidence"

        else:
            result["condition"] = top1["condition"]
            result["status"] = "confident"

        result["confidence"] = confidence

    except Exception as e:
        logger.error("Classification error: %s", e)
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

    result.setdefault("status", "ok")

    total_ms = round((time.perf_counter() - t0) * 1000, 1)

    condition = result.get("condition", "Uncertain")

    lang = "english" if language.lower() != "hindi" else "hindi"

    normalized_condition = normalize_condition_name(condition)

    medical_data = None

    for key in DISEASE_INFO.keys():
        if key.lower().replace(" ", "") == normalized_condition.lower().replace(" ", ""):
            medical_data = DISEASE_INFO[key]
            break

    if medical_data:
        advice_list = medical_data.get(lang) or medical_data.get("english")
        advice_data = advice_list[0]

        final_advice = advice_data.get("advice", "No advice available.")
        disease_name = advice_data.get("disease", condition)
    else:
        final_advice = "डॉक्टर से सलाह लें." if lang == "hindi" else "No advice found. Please consult a doctor."
        disease_name = condition



    def generate():
        meta = f"__META__|{disease_name}|{result['confidence']}|{result['status']}\n"
        yield meta

        for word in final_advice.split():
            yield word + " "
            time.sleep(0.1)

    result["advice"] = final_advice
    result["display_name"] = disease_name
    result["inference_ms"] = total_ms
    result["device"] = "cpu"

    return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
    )
