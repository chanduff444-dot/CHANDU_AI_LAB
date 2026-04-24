
# ============================================
# CHANDU AI LAB - HYBRID EMOTIONAL ENGINE
# Emotion + Sentiment + Conflict Resolution
# ============================================

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ==============================
# Load Emotion Model (GoEmotions)
# ==============================

EMOTION_MODEL_NAME = "SamLowe/roberta-base-go_emotions"
emotion_tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL_NAME)
emotion_model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL_NAME)
emotion_model.to(device)
emotion_model.eval()

# ==============================
# Load Sentiment Model
# ==============================

SENTIMENT_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
sentiment_tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL_NAME)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL_NAME)
sentiment_model.to(device)
sentiment_model.eval()


# ============================================
# SENTIMENT PREDICTION
# ============================================

def _predict_sentiment(text):

    inputs = sentiment_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    ).to(device)

    with torch.no_grad():
        outputs = sentiment_model(**inputs)

    probs = F.softmax(outputs.logits, dim=-1)
    confidence, pred_class = torch.max(probs, dim=1)

    label_map = sentiment_model.config.id2label
    sentiment_label = label_map[pred_class.item()]

    return sentiment_label.upper(), confidence.item()


# ============================================
# EMOTION PREDICTION
# ============================================

def _predict_emotion(text):

    inputs = emotion_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    ).to(device)

    with torch.no_grad():
        outputs = emotion_model(**inputs)

    probs = F.softmax(outputs.logits, dim=-1)
    confidence, pred_class = torch.max(probs, dim=1)

    emotion_label = emotion_model.config.id2label[pred_class.item()]

    return emotion_label, confidence.item()


# ============================================
# HYBRID PREDICTION (Production Layer)
# ============================================

def _hybrid_predict(text):

    emotion, emotion_conf = _predict_emotion(text)
    sentiment, sentiment_conf = _predict_sentiment(text)

    # -----------------------------
    # Conflict Resolution
    # -----------------------------
    positive_emotions = ["joy", "love", "admiration", "gratitude", "excitement"]
    negative_emotions = [
        "sadness", "anger", "fear", "disgust",
        "disappointment", "grief", "remorse"
    ]

    # If sentiment negative but emotion positive → downgrade confidence
    if sentiment == "NEGATIVE" and emotion in positive_emotions:
        emotion_conf *= 0.4

    # If sentiment positive but emotion negative → downgrade
    if sentiment == "POSITIVE" and emotion in negative_emotions:
        emotion_conf *= 0.4

    return {
        "emotion": emotion,
        "confidence": round(emotion_conf, 4),
        "sentiment": sentiment
    }


# ============================================
# PUBLIC FUNCTIONS (Backward Compatible)
# ============================================

def predict_emotion(text: str):
    result = _hybrid_predict(text)

    if result["confidence"] < 0.55:
        result["emotion"] = "uncertain"
        result["sentiment"] = "NEUTRAL"

    return result


def predict_emotion_raw(text: str):
    return _hybrid_predict(text)
