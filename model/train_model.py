"""
train_model.py
Trains and evaluates multiple ML classifiers on Jenkins build failure logs.
Saves the best-performing model for use by the web dashboard.
"""
import os, sys, json, pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

DATA_PATH  = os.path.join(os.path.dirname(__file__), "../data/build_failures.csv")
MODEL_DIR  = os.path.dirname(__file__)


def train():
    print("[INFO] Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    X  = df["log_snippet"]
    y  = df["failure_type"]
    print(f"[INFO] Dataset: {len(df)} samples, {y.nunique()} classes")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    models = {
        "Random Forest": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
            ("clf",   RandomForestClassifier(n_estimators=100, random_state=42)),
        ]),
        "Decision Tree": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
            ("clf",   DecisionTreeClassifier(max_depth=20, random_state=42)),
        ]),
        "SVM": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
            ("clf",   LinearSVC(random_state=42, max_iter=3000)),
        ]),
    }

    results = {}
    best_name, best_model, best_acc = None, None, 0.0

    for name, pipeline in models.items():
        print(f"\n[TRAINING] {name}...")
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        acc   = accuracy_score(y_test, preds)
        f1    = f1_score(y_test, preds, average="weighted")
        cv    = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")

        try:
            classes = list(pipeline["clf"].classes_)
        except Exception:
            classes = sorted(y.unique().tolist())

        results[name] = {
            "accuracy": round(acc * 100, 2),
            "f1_score": round(f1, 4),
            "cv_mean":  round(cv.mean() * 100, 2),
            "cv_std":   round(cv.std() * 100, 2),
            "report":   classification_report(y_test, preds, output_dict=True),
            "confusion": confusion_matrix(y_test, preds).tolist(),
            "classes":  classes,
        }

        print(f"  Accuracy : {acc*100:.2f}%  |  F1: {f1:.4f}  |  CV: {cv.mean()*100:.2f}% ± {cv.std()*100:.2f}%")
        print(classification_report(y_test, preds))

        if acc > best_acc:
            best_acc, best_name, best_model = acc, name, pipeline

    print(f"\n[RESULT] Best Model: {best_name} — Accuracy: {best_acc*100:.2f}%")

    with open(os.path.join(MODEL_DIR, "best_model.pkl"), "wb") as f:
        pickle.dump(best_model, f)

    def convert(o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, np.ndarray):    return o.tolist()
        raise TypeError

    with open(os.path.join(MODEL_DIR, "model_results.json"), "w") as f:
        json.dump({"results": results, "best_model": best_name}, f, default=convert, indent=2)

    print("[INFO] Model saved → model/best_model.pkl")
    print("[INFO] Results saved → model/model_results.json")
    return results, best_name


if __name__ == "__main__":
    train()
