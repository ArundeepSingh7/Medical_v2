import gradio as gr
import time
from medical_v2.models.classifier import predict
from medical_v2.models.medical_advice import DISEASE_INFO


def normalize(name):
    return name.strip().lower().replace(" ", "")


def predict_image(image, lang):
    with open(image, "rb") as f:
        image_bytes = f.read()

    result = predict(image_bytes)

    condition = result.get("condition", "Unknown")
    confidence = result.get("confidence", 0)
    status = result.get("status", "unknown")

    advice_text = "No advice found. Please consult a doctor."
    condition_display = condition

    for key in DISEASE_INFO.keys():
        if normalize(key) == normalize(condition):
            data = DISEASE_INFO[key][lang][0]
            advice_text = data["advice"]
            condition_display = data["disease"]
            break

    output = ""

    output += f"Condition: {condition_display}\n"
    yield output
    time.sleep(0.3)

    output += f"Confidence: {confidence}%\n"
    yield output
    time.sleep(0.3)

    output += f"Status: {status}\n\n"
    yield output
    time.sleep(0.3)

    output += "Advice:\n"
    yield output

    for word in advice_text.split():
        output += word + " "
        yield output
        time.sleep(0.05)


demo = gr.Interface(
    fn=predict_image,
    inputs=[
        gr.Image(type="filepath", label="Upload Skin Image"),
        gr.Radio(["english", "hindi"], value="english", label="Select Language")
    ],
    outputs=gr.Textbox(label="Result", lines=15),
    title="🩺 Skin Disease Detector"
)

demo.launch(server_name="0.0.0.0", server_port=7860)