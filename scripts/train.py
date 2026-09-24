"""Fine-tune distilbert-base-uncased on data/takemeter_final.csv (local; uses Apple MPS / CUDA if present).

Mirrors the CodePath starter notebook: stratified 70/15/15 split, DistilBERT, defaults 3 epochs /
lr 2e-5 / batch 16. Hyperparameters are compared on the VALIDATION set only; the test set is scored
once, with --final.

    python scripts/train.py --tag default                           # val-only run, logged to outputs/hparam_runs.json
    python scripts/train.py --epochs 8 --lr 3e-5 --class-weights --tag weighted
    python scripts/train.py --epochs 8 --lr 3e-5 --class-weights --final   # test eval + save model/
"""
import argparse
import json
import os
import random

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, Trainer,
                          TrainingArguments)

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data", "takemeter_final.csv")
SPLITS = os.path.join(ROOT, "data", "splits")
OUTPUTS = os.path.join(ROOT, "outputs")
MODEL_DIR = os.path.join(ROOT, "model")
BASE = "distilbert-base-uncased"
SEED = 42

LABELS = list(json.load(open(os.path.join(ROOT, "labels.json")))["labels"])
L2I = {l: i for i, l in enumerate(LABELS)}


def make_splits():
    """70/15/15 stratified split, written once so the baseline uses the exact same test set."""
    if os.path.exists(os.path.join(SPLITS, "test.csv")):
        return [pd.read_csv(os.path.join(SPLITS, f"{s}.csv"), keep_default_na=False)
                for s in ("train", "val", "test")]
    df = pd.read_csv(DATA, keep_default_na=False)
    train, rest = train_test_split(df, test_size=0.30, stratify=df.label, random_state=SEED)
    val, test = train_test_split(rest, test_size=0.50, stratify=rest.label, random_state=SEED)
    os.makedirs(SPLITS, exist_ok=True)
    for name, d in (("train", train), ("val", val), ("test", test)):
        d.to_csv(os.path.join(SPLITS, f"{name}.csv"), index=False)
    return train, val, test


class DS(torch.utils.data.Dataset):
    def __init__(self, df, tok, max_len):
        self.enc = tok(list(df.text), truncation=True, max_length=max_len)
        self.y = [L2I[l] for l in df.label]

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        item = {k: torch.tensor(v[i]) for k, v in self.enc.items()}
        item["labels"] = torch.tensor(self.y[i])
        return item


class WeightedTrainer(Trainer):
    def __init__(self, *a, class_weights=None, **kw):
        super().__init__(*a, **kw)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        w = self.class_weights.to(outputs.logits.device) if self.class_weights is not None else None
        loss = torch.nn.functional.cross_entropy(outputs.logits, labels, weight=w)
        return (loss, outputs) if return_outputs else loss


def metrics(p):
    preds = p.predictions.argmax(-1)
    return {"accuracy": accuracy_score(p.label_ids, preds),
            "macro_f1": f1_score(p.label_ids, preds, average="macro")}


def softmax(x):
    e = np.exp(x - x.max(-1, keepdims=True))
    return e / e.sum(-1, keepdims=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--class-weights", action="store_true", help="inverse-frequency weighted loss")
    ap.add_argument("--tag", default="run")
    ap.add_argument("--final", action="store_true", help="evaluate on test and save the model")
    args = ap.parse_args()

    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
    train, val, test = make_splits()
    print(f"split sizes: train {len(train)}  val {len(val)}  test {len(test)}")

    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE, num_labels=len(LABELS), id2label=dict(enumerate(LABELS)), label2id=L2I)

    weights = None
    if args.class_weights:
        counts = train.label.value_counts()
        weights = torch.tensor([len(train) / (len(LABELS) * counts[l]) for l in LABELS], dtype=torch.float)
        print("class weights:", dict(zip(LABELS, weights.round(decimals=2).tolist())))

    targs = TrainingArguments(
        output_dir=os.path.join(MODEL_DIR, "_runs", args.tag), num_train_epochs=args.epochs,
        learning_rate=args.lr, per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=32, weight_decay=0.01, warmup_steps=0.1,
        eval_strategy="epoch", save_strategy="epoch", save_total_limit=1,
        load_best_model_at_end=True, metric_for_best_model="macro_f1",
        logging_strategy="epoch", report_to="none", seed=SEED)
    trainer = WeightedTrainer(model=model, args=targs, train_dataset=DS(train, tok, args.max_len),
                              eval_dataset=DS(val, tok, args.max_len), processing_class=tok,
                              compute_metrics=metrics, class_weights=weights)
    trainer.train()

    history = [{"epoch": h["epoch"], "val_loss": round(h["eval_loss"], 4),
                "val_accuracy": round(h["eval_accuracy"], 4), "val_macro_f1": round(h["eval_macro_f1"], 4)}
               for h in trainer.state.log_history if "eval_loss" in h]
    train_loss = [{"epoch": h["epoch"], "train_loss": round(h["loss"], 4)}
                  for h in trainer.state.log_history if "loss" in h and "eval_loss" not in h]
    best = trainer.evaluate()
    run = {"tag": args.tag, "epochs": args.epochs, "lr": args.lr, "batch_size": args.batch_size,
           "class_weights": args.class_weights, "best_val_macro_f1": round(best["eval_macro_f1"], 4),
           "best_val_accuracy": round(best["eval_accuracy"], 4), "history": history, "train_loss": train_loss}
    os.makedirs(OUTPUTS, exist_ok=True)
    log_path = os.path.join(OUTPUTS, "hparam_runs.json")
    runs = json.load(open(log_path)) if os.path.exists(log_path) else []
    runs = [r for r in runs if r["tag"] != args.tag] + [run]
    json.dump(runs, open(log_path, "w"), indent=2)
    print(json.dumps({k: v for k, v in run.items() if k not in ("history", "train_loss")}))
    for h in history:
        print(h)

    if not args.final:
        return

    # ---- one-time test evaluation ----
    out = trainer.predict(DS(test, tok, args.max_len))
    probs = softmax(out.predictions)
    preds = probs.argmax(-1)
    y = np.array([L2I[l] for l in test.label])
    report = classification_report(y, preds, labels=range(len(LABELS)), target_names=LABELS,
                                   output_dict=True, zero_division=0)
    cm = confusion_matrix(y, preds, labels=range(len(LABELS)))
    print(classification_report(y, preds, labels=range(len(LABELS)), target_names=LABELS, zero_division=0))
    print("confusion (rows=true, cols=pred):", LABELS)
    print(cm)

    pred_df = test[["text", "label"]].rename(columns={"label": "true"}).copy()
    pred_df["pred"] = [LABELS[i] for i in preds]
    pred_df["confidence"] = probs.max(-1).round(4)
    for i, l in enumerate(LABELS):
        pred_df[f"p_{l}"] = probs[:, i].round(4)
    pred_df.to_csv(os.path.join(OUTPUTS, "finetuned_test_predictions.csv"), index=False)

    json.dump({"model": BASE, "config": {k: v for k, v in run.items() if k not in ("history", "train_loss")},
               "labels": LABELS, "test_size": len(test), "accuracy": report["accuracy"],
               "macro_f1": report["macro avg"]["f1-score"], "per_class": {l: report[l] for l in LABELS},
               "confusion_matrix": cm.tolist()},
              open(os.path.join(OUTPUTS, "finetuned_metrics.json"), "w"), indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(LABELS)), LABELS, rotation=30)
    ax.set_yticks(range(len(LABELS)), LABELS)
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    ax.set_title("TakeMeter — fine-tuned DistilBERT (test set)")
    for i in range(len(LABELS)):
        for j in range(len(LABELS)):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUTS, "confusion_matrix.png"), dpi=150)

    trainer.save_model(MODEL_DIR)
    tok.save_pretrained(MODEL_DIR)
    print(f"saved model -> {MODEL_DIR}")


if __name__ == "__main__":
    main()
