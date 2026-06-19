"""Song management module for Emotion-Based Music Recommendation System.
Provides thread-safe CRUD operations for the songs dataset.
"""

import threading
import pandas as pd
from .config import get_csv_path
from .engine import ensure_dataset

# A lock to ensure thread-safe read/writes to the CSV
_csv_lock = threading.Lock()

def add_song(song_name: str, artist: str, genre: str, mood: str, tempo: int = None) -> bool:
    """Add a new song to the dataset."""
    with _csv_lock:
        df = ensure_dataset()
        new_row = {
            "song_name": song_name,
            "artist": artist,
            "genre": genre,
            "mood": mood,
            "tempo": tempo if tempo is not None else ""
        }
        # Append new row
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        # We drop the helper 'mood_norm' column before saving if it exists
        if "mood_norm" in df.columns:
            df = df.drop(columns=["mood_norm"])
        df.to_csv(get_csv_path(), index=False)
    return True

def edit_song(index: int, **updates) -> bool:
    """Edit an existing song by its DataFrame index."""
    with _csv_lock:
        df = ensure_dataset()
        if index < 0 or index >= len(df):
            return False
            
        for col, val in updates.items():
            if col in df.columns:
                df.at[index, col] = val
                
        if "mood_norm" in df.columns:
            df = df.drop(columns=["mood_norm"])
        df.to_csv(get_csv_path(), index=False)
    return True

def delete_song(index: int) -> bool:
    """Delete a song by its DataFrame index."""
    with _csv_lock:
        df = ensure_dataset()
        if index < 0 or index >= len(df):
            return False
            
        df = df.drop(index).reset_index(drop=True)
        if "mood_norm" in df.columns:
            df = df.drop(columns=["mood_norm"])
        df.to_csv(get_csv_path(), index=False)
    return True

def list_songs() -> list:
    """List all songs as a list of dictionaries with their index."""
    with _csv_lock:
        df = ensure_dataset()
        # Include original index so UI knows what ID to delete/edit
        records = df.to_dict(orient="records")
        for i, record in enumerate(records):
            record["_index"] = i
        return records
