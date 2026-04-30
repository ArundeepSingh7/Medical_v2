from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torch
import io

model = None
processor = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_vit():
    global model, processor
    if model is None:
        model = ViTForImageClassification.from_pretrained(
            "LaurianeMD/vit-skin-disease"
        ).to(device)

        if device.type == "cuda":
            model = model.half()

        model.eval()
        processor = ViTImageProcessor.from_pretrained(
            "LaurianeMD/vit-skin-disease"
        )

# def print_all_classes():
#     load_vit()
#     for idx in sorted(model.config.id2label.keys()):
#         print(f"{idx}: {model.config.id2label[idx]}")

def predict_vit(image_bytes):
    load_vit()



    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    if device.type == "cuda":
        inputs = {k: v.to(device).half() for k, v in inputs.items()}
    else:
        inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]

    topk = torch.topk(probs, 3)

    results = []
    for i in range(3):
        idx = topk.indices[i].item()
        conf = topk.values[i].item() * 100
        label = model.config.id2label[idx]

        results.append({
            "condition": label,
            "confidence": round(conf, 1)
        })

    return results

# print_all_classes()