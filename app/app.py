"""Stretch feature: deployed interface. Paste a post, get a label + confidence.

Setup: train first (writes ./model, which is gitignored because of size):
    python scripts/train.py --epochs 8 --lr 3e-5 --class-weights --final
Then:

    pip install -r requirements.txt
    python app/app.py
"""
import os

import gradio as gr
from transformers import pipeline

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
clf = pipeline("text-classification", model=MODEL_DIR, top_k=None)


def classify(text):
    out = clf(text)
    scores = out[0] if isinstance(out[0], list) else out  # output nesting differs across transformers versions
    return {s["label"]: s["score"] for s in scores}


gr.Interface(
    fn=classify,
    inputs=gr.Textbox(lines=6, label="Post or comment"),
    outputs=gr.Label(num_top_classes=4, label="TakeMeter says"),
    title="TakeMeter",
    description="Fine-tuned DistilBERT that labels r/nba comments as analysis, hot_take, reaction, or banter.",
    examples=[["If it's the Spurs maybe. Not for OKC though. SGA is the only player on their team who's played more than 30 mpg in the last 2 games. They're stupid deep"],
              ["Wemby is already the best defender in the league and it isn't close."],
              ["Grudge avenged!! CHAMPS BABY!"],
              ["That man is married with 3 kids. He gone gone."]],
).launch()
