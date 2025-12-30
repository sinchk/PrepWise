# mastery.py
import pandas as pd
import numpy as np

DEFAULT_WEIGHTS = {
    "accuracy": 0.5,
    "response_time": 0.3,
    "engagement": 0.2
}

def compute_topic_stats(logs_df):
    topic_stats = {}

    for topic, df in logs_df.groupby("topic"):
        total = len(df)
        correct = df["correct"].sum()
        skipped = df["skipped"].sum()

        topic_stats[topic] = {
            "accuracy": correct / total if total else 0,
            "engagement": 1 - (skipped / total) if total else 0,
            "avg_time": df["response_time"].mean()
        }

    return topic_stats

def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-6)

def compute_topic_mastery(topic_stats):
    mastery = {}
    for topic, s in topic_stats.items():
        mastery[topic] = round(
            0.5 * s["accuracy"]
            + 0.3 * (1 / (1 + s["avg_time"]))
            + 0.2 * s["engagement"],
            3
        )
    return mastery

def classify_mastery(score):
    if score < 0.4:
        return "Not Mastered"
    elif score < 0.7:
        return "Partially Mastered"
    return "Mastered"