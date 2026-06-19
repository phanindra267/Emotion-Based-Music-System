# app/engine.py
"""Core engine for the Emotion‑Based Music Recommendation System.
Provides:
- Model loading and caching for DeepFace.
- Webcam frame emotion detection.
- Text sentiment analysis (TextBlob primary, VADER fallback).
- CSV loading/validation and song recommendation.
- Simple logging.
All operations are offline.
"""

import os
import logging
import random
from pathlib import Path

# Optional imports – handled lazily
try:
    import cv2
except ImportError:
    cv2 = None
    logging.debug("opencv-python not available – webcam features disabled.")

try:
    from deepface import DeepFace
except ImportError:
    DeepFace = None
    logging.debug("deepface not available – facial emotion detection disabled.")

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None
    logging.debug("textblob not available – text sentiment disabled.")

# VADER fallback – imported only if needed
def _load_vader():
    try:
        import nltk
        nltk.download("vader_lexicon", quiet=True)
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        return SentimentIntensityAnalyzer()
    except Exception as e:
        logging.error(f"Failed to load VADER: {e}")
        return None

# Logging setup – writes to app.log in the project root
LOG_FILE = Path(__file__).resolve().parents[1] / "app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

# ------------------------------------------------------------
# Configuration handling (delegates to app.config)
# ------------------------------------------------------------
from .config import load_config, get_csv_path

CONFIG = load_config()

# ------------------------------------------------------------
# CSV handling
# ------------------------------------------------------------
import pandas as pd

def ensure_dataset(csv_path: str = None) -> pd.DataFrame:
    """Load the songs CSV, creating a default one if missing or empty.
    Returns a pandas DataFrame.
    """
    if csv_path is None:
        csv_path = get_csv_path()
    if not os.path.isfile(csv_path) or os.path.getsize(csv_path) == 0:
        logging.info("Songs CSV not found – creating default dataset.")
        _create_default_dataset(csv_path)
    df = pd.read_csv(csv_path)
    # Normalise mood column for safe matching
    df["mood_norm"] = df["mood"].astype(str).str.strip().str.lower()
    return df

def _create_default_dataset(csv_path: str) -> None:
    """Write a minimal default songs.csv covering all moods."""
    default_data = [
        {"song_name": "Happy Tune", "artist": "Artist A", "genre": "Pop", "mood": "energetic", "tempo": 120},
        {"song_name": "Calm Waves", "artist": "Artist B", "genre": "Ambient", "mood": "calm", "tempo": 70},
        {"song_name": "Motivation", "artist": "Artist C", "genre": "Rock", "mood": "motivational", "tempo": 140},
        {"song_name": "Soft Piano", "artist": "Artist D", "genre": "Classical", "mood": "soft", "tempo": 60},
        {"song_name": "Upbeat Beat", "artist": "Artist E", "genre": "EDM", "mood": "upbeat", "tempo": 130},
    ]
    df = pd.DataFrame(default_data)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    logging.info(f"Default dataset written to {csv_path}")

# ------------------------------------------------------------
# Emotion detection (webcam)
# ------------------------------------------------------------
def detect_emotion_from_frame(frame) -> str:
    """Detect the dominant emotion from an OpenCV BGR frame.
    Returns one of the supported emotions; falls back to "neutral" on any error.
    """
    if DeepFace is None:
        logging.warning("DeepFace unavailable – returning neutral emotion.")
        return "neutral"
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        analysis = DeepFace.analyze(rgb, actions=["emotion"], enforce_detection=False)
        dominant = analysis.get("dominant_emotion", "neutral").lower()
        if dominant not in CONFIG.get("supported_emotions", []):
            # map unknown emotions (fear, disgust, etc.) to neutral/motivational as per config
            return "neutral"
        return dominant
    except Exception as e:
        logging.error(f"Emotion detection failed: {e}")
        return "neutral"

# ------------------------------------------------------------
# Text sentiment analysis
# ------------------------------------------------------------
def analyse_sentiment(text: str) -> str:
    """Return an emotion string derived from the sentiment of *text*.
    Primary method: TextBlob polarity. Fallback: VADER polarity.
    """
    if not text:
        return "neutral"
    # TextBlob path
    if TextBlob is not None:
        try:
            polarity = TextBlob(text).sentiment.polarity
            if polarity > 0.2:
                return "happy"
            if polarity < -0.2:
                return "sad"
            return "neutral"
        except Exception as e:
            logging.error(f"TextBlob analysis error: {e}")
    # VADER fallback
    vader = _load_vader()
    if vader:
        try:
            scores = vader.polarity_scores(text)
            compound = scores["compound"]
            if compound > 0.2:
                return "happy"
            if compound < -0.2:
                return "sad"
            return "neutral"
        except Exception as e:
            logging.error(f"VADER analysis error: {e}")
    # If everything fails
    return "neutral"

# ------------------------------------------------------------
# Mood mapping
# ------------------------------------------------------------
def map_emotion_to_mood(emotion: str) -> str:
    """Map a detected emotion to the music mood using the config mapping.
    Defaults to "soft" if the emotion is not in the map.
    """
    return CONFIG.get("emotion_mood_map", {}).get(emotion.lower(), "soft")

# ------------------------------------------------------------
# Recommendation engine
# ------------------------------------------------------------
def recommend_songs(mood: str, n: int = None) -> list:
    """Return up to *n* random songs matching *mood*.
    *n* defaults to the value from config (default_song_count).
    """
    if n is None:
        n = CONFIG.get("default_song_count", 5)
    df = ensure_dataset()
    matches = df[df["mood_norm"] == mood.strip().lower()]
    if matches.empty:
        return []
    count = min(len(matches), n)
    sample = matches.sample(n=count)
    # Return list of dicts with key info
    return sample[["song_name", "artist", "genre"]].to_dict(orient="records")

# ------------------------------------------------------------
# Helper for headless image processing
# ------------------------------------------------------------
def process_image_file(image_path: str) -> dict:
    """Load an image file, detect emotion, map to mood, and recommend songs.
    Returns a dict with keys: emotion, mood, songs (list).
    """
    if cv2 is None:
        raise RuntimeError("OpenCV is required for image processing but is not installed.")
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Unable to read image at {image_path}")
    emotion = detect_emotion_from_frame(img)
    mood = map_emotion_to_mood(emotion)
    songs = recommend_songs(mood)
    return {"emotion": emotion, "mood": mood, "songs": songs}


# Alias for GUI compatibility
def analyze_text_sentiment(text: str) -> str:
    """Alias for analyse_sentiment for backward compatibility."""
    return analyse_sentiment(text)
