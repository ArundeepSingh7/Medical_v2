# 🧠 Skin Disease Classification with Vision Transformer (ViT)

This project uses a fine-tuned Vision Transformer model to classify skin diseases from images. It leverages a pretrained model hosted on Hugging Face for fast and accurate inference.

## 📦 Model

This project uses the model: **LaurianeMD/vit-skin-disease**

* Architecture: Vision Transformer (ViT)
* Task: Image Classification
* Framework: PyTorch + Transformers

## ⚖️ License

The model is released under the **MIT License**.

This means:

* ✅ Commercial use allowed
* ✅ Modification allowed
* ✅ Distribution allowed
* ⚠️ Must include original license and copyright notice

## ⚠️ Disclaimer

This model is intended for **research and educational purposes only**.

* ❗ Not medically certified
* ❗ Not suitable for clinical diagnosis
* ❗ Predictions may be inaccurate

Always consult a qualified medical professional for real diagnoses.

---

## 🚀 Installation

```bash
pip install torch torchvision transformers pillow
```

---

## 🧩 Usage

### Load Model and Processor

```python
from transformers import ViTForImageClassification, ViTImageProcessor
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = ViTForImageClassification.from_pretrained(
    "LaurianeMD/vit-skin-disease"
).to(device)

processor = ViTImageProcessor.from_pretrained(
    "LaurianeMD/vit-skin-disease"
)

model.eval()
```

---

### 📸 Predict from Image

```python
from PIL import Image
import io

def predict_vit(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)

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
```

---

### 🏷️ List All Classes

```python
for idx in sorted(model.config.id2label.keys()):
    print(f"{idx}: {model.config.id2label[idx]}")
```

---

## ⚡ GPU Optimization (Optional)

If using CUDA:

```python
model = model.half()
inputs = {k: v.half() for k, v in inputs.items()}
```

---

## 📂 Project Structure

```
.
├── main.py
├── README.md
└── requirements.txt
```

---

## 🛠️ Requirements

* Python 3.8+
* torch
* transformers
* pillow

---

## 📌 Notes

* Ensure images are RGB format
* Larger images will be resized automatically by the processor
* Top-3 predictions are returned with confidence scores

---

## 🤝 Contributing

Pull requests and improvements are welcome!

---

## 📜 License (Project)

This project follows the **MIT License** (same as the model unless otherwise specified).

---

## 🙏 Acknowledgements

* Hugging Face Transformers
* Vision Transformer (ViT) architecture
* Model author: LaurianeMD

---
