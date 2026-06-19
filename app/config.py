"""Configuration module for the Emotion-Based Music Recommendation System.
Handles loading config.json and providing paths to resources.
"""

import os
import json
from pathlib import Path

# Project root is the parent of the app directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config.json"
CSV_PATH = PROJECT_ROOT / "songs.csv"


def load_config():
    """Load configuration from config.json.
    Returns a dict with UI theme, emotion-mood mapping, and supported emotions.
    Falls back to defaults if config.json is missing or invalid.
    """
    default_config = {
        "ui_theme": {
            "bg_color": "#1e1e2f",
            "accent_color": "#a78bfa",
            "font": "Helvetica",
            "font_size": 12,
            "dark_mode": True,
        },
        "emotion_mood_map": {
            "happy": "energetic",
            "sad": "calm",
            "angry": "motivational",
            "neutral": "soft",
            "surprise": "upbeat",
            "fear": "motivational",
            "disgust": "motivational",
        },
        "supported_emotions": ["happy", "sad", "angry", "neutral", "surprise"],
    }

    if not CONFIG_PATH.exists():
        return default_config

    try:
        with open(CONFIG_PATH, "r") as f:
            user_config = json.load(f)
            # Merge with defaults (user config overrides defaults)
            config = default_config.copy()
            config.update(user_config)
            return config
    except Exception as e:
        print(f"[WARNING] Failed to load config.json: {e}. Using defaults.")
        return default_config


def get_csv_path():
    """Return the path to the songs.csv file."""
    return str(CSV_PATH)


def get_project_root():
    """Return the project root directory."""
    return str(PROJECT_ROOT)


def get_emotion_mood_map():
    """Return the emotion-to-mood mapping from config."""
    config = load_config()
    return config.get("emotion_mood_map", {})


def get_supported_emotions():
    """Return the list of supported emotions from config."""
    config = load_config()
    return config.get("supported_emotions", ["happy", "sad", "angry", "neutral", "surprise"])
