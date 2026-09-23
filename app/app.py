"""Stretch feature: deployed interface. Paste a post, get a label + confidence.

Setup: after training in Colab, save the model and download it:
    trainer.save_model("model"); tokenizer.save_pretrained("model")
    !zip -r model.zip model
Unzip it into this repo's root as ./model (gitignored), then:

    pip install -r requirements.txt
    python app/app.py
"""
import os

import gradio as gr
from transformers import pipeline

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
clf = pipeline("text-classification", model=MODEL_DIR, top_k=None)


def classify(text):
    scores = clf(text)[0]
    return {s["label"]: s["score"] for s in scores}


gr.Interface(
    fn=classify,
    inputs=gr.Textbox(lines=6, label="Post or comment"),
    outputs=gr.Label(num_top_classes=4, label="TakeMeter says"),
    title="TakeMeter",
    description="Fine-tuned DistilBERT classifier for discourse quality.",
).launch()
