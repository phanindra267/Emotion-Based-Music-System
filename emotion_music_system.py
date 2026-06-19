# emotion_music_system.py
"""
Emotion-Based Music Recommendation System

This script provides a Tkinter GUI that can:
- Capture webcam video and detect the dominant facial emotion using DeepFace.
- Optionally analyse typed text sentiment (TextBlob) to infer emotion.
- Map the detected emotion to a music mood.
- Recommend 3‑5 songs from a local CSV dataset (songs.csv).

All processing is offline – no external APIs are used.
"""

import os
import random
import threading
import sys

# Additional imports for styling
import tkinter.font as tkfont

# ---------- Optional imports with graceful fallback ----------
try:
    import cv2
except ImportError:
    cv2 = None
    print("OpenCV (cv2) not installed - webcam functionality will be disabled.")

try:
    from deepface import DeepFace
except ImportError:
    DeepFace = None
    print("DeepFace not installed - emotion detection from webcam will be disabled.")

try:
    import pandas as pd
except ImportError:
    pd = None
    print("pandas not installed - recommendation engine cannot run.")

try:
    import numpy as np
except ImportError:
    np = None
    print("numpy not installed - some internal calculations may be affected.")

# Text sentiment analysis is optional
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None
    print("TextBlob not installed - text-based emotion analysis will be disabled.")

# Tkinter is part of the standard library (Python 3)
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# ---------- Configuration ----------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, "songs.csv")

# Emotion → Mood mapping (easy to modify)
EMOTION_MOOD_MAP = {
    "happy": "energetic",
    "sad": "calm",
    "angry": "motivational",
    "neutral": "soft",
    "surprise": "upbeat",
    # fallback for other emotions
    "fear": "motivational",
    "disgust": "motivational",
}

SUPPORTED_EMOTIONS = ["happy", "sad", "angry", "neutral", "surprise"]

# ---------- Helper Functions ----------
def ensure_csv_exists():
    """Create a default songs.csv if it does not exist.
    The CSV contains columns: song_name, artist, genre, mood, tempo.
    """
    if os.path.isfile(CSV_PATH):
        return
    # Sample dataset covering all moods
    sample_data = [
        {"song_name": "Happy Tune", "artist": "Artist A", "genre": "Pop", "mood": "energetic", "tempo": 120},
        {"song_name": "Joyful Beats", "artist": "Artist B", "genre": "Electronic", "mood": "energetic", "tempo": 130},
        {"song_name": "Sunrise", "artist": "Artist C", "genre": "Acoustic", "mood": "soft", "tempo": 80},
        {"song_name": "Calm Waters", "artist": "Artist D", "genre": "Ambient", "mood": "soft", "tempo": 70},
        {"song_name": "Mellow Breeze", "artist": "Artist E", "genre": "Jazz", "mood": "soft", "tempo": 85},
        {"song_name": "Sad Strings", "artist": "Artist F", "genre": "Classical", "mood": "calm", "tempo": 60},
        {"song_name": "Rainy Day", "artist": "Artist G", "genre": "Indie", "mood": "calm", "tempo": 75},
        {"song_name": "Lonely Road", "artist": "Artist H", "genre": "Folk", "mood": "calm", "tempo": 68},
        {"song_name": "Rage", "artist": "Artist I", "genre": "Rock", "mood": "motivational", "tempo": 140},
        {"song_name": "Power Up", "artist": "Artist J", "genre": "Electronic", "mood": "motivational", "tempo": 150},
        {"song_name": "Fire Within", "artist": "Artist K", "genre": "Metal", "mood": "motivational", "tempo": 155},
        {"song_name": "Surprise Party", "artist": "Artist L", "genre": "Pop", "mood": "upbeat", "tempo": 125},
        {"song_name": "Jump Start", "artist": "Artist M", "genre": "Dance", "mood": "upbeat", "tempo": 128},
        {"song_name": "Spark", "artist": "Artist N", "genre": "EDM", "mood": "upbeat", "tempo": 132},
        # Additional songs to ensure at least 20 entries
        {"song_name": "Morning Light", "artist": "Artist O", "genre": "Pop", "mood": "energetic", "tempo": 115},
        {"song_name": "Evening Calm", "artist": "Artist P", "genre": "Ambient", "mood": "soft", "tempo": 72},
        {"song_name": "Deep Thought", "artist": "Artist Q", "genre": "Instrumental", "mood": "calm", "tempo": 65},
        {"song_name": "Storm", "artist": "Artist R", "genre": "Rock", "mood": "motivational", "tempo": 145},
        {"song_name": "Heartbeat", "artist": "Artist S", "genre": "Pop", "mood": "upbeat", "tempo": 122},
        {"song_name": "Peaceful Moment", "artist": "Artist T", "genre": "Classical", "mood": "soft", "tempo": 78},
    ]
    df = pd.DataFrame(sample_data)
    df.to_csv(CSV_PATH, index=False)
    print(f"Created default dataset at {CSV_PATH}")

def load_dataset():
    """Load songs.csv into a pandas DataFrame."""
    if pd is None:
        raise RuntimeError("pandas is required to load the song dataset.")
    return pd.read_csv(CSV_PATH)

def map_emotion_to_mood(emotion):
    """Map detected emotion to music mood, case‑insensitive."""
    emotion_key = emotion.lower()
    return EMOTION_MOOD_MAP.get(emotion_key, "soft")  # default fallback

def recommend_songs(mood, n=5):
    """Return up to n random songs matching the given mood.
    The mood comparison is case‑insensitive and ignores surrounding spaces.
    """
    df = load_dataset()
    # Normalise mood column
    df["mood_norm"] = df["mood"].str.strip().str.lower()
    filtered = df[df["mood_norm"] == mood.strip().lower()]
    if filtered.empty:
        return []
    count = min(len(filtered), n)
    # Random sample without replacement
    sample = filtered.sample(n=count, random_state=random.randint(0, 100000))
    # Return list of dicts with required fields
    return sample[["song_name", "artist", "genre"]].to_dict(orient="records")

def analyse_text_sentiment(text):
    """Use TextBlob to compute polarity and map to an emotion.
    Returns one of the supported emotions (happy, sad, neutral).
    """
    if TextBlob is None:
        return None
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        return "happy"
    elif polarity < -0.2:
        return "sad"
    else:
        return "neutral"

# ---------- GUI Application ----------
class EmotionMusicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Emotion‑Based Music Recommender")
        self.geometry("800x600")
        self.resizable(False, False)

        # Apply modern styling and menu
        self.setup_style()
        self.create_menu()

        # state variables
        self.cap = None  # cv2.VideoCapture
        self.video_thread = None
        self.stop_event = threading.Event()
        self.current_frame = None  # latest OpenCV frame (BGR)

        # UI Elements
        self.create_widgets()
        ensure_csv_exists()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 12), padding=6)
        style.configure('TLabel', font=('Helvetica', 12), background='#2b2b2b', foreground='#e0e0e0')
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TEntry', font=('Helvetica', 12))
        self.configure(background='#2b2b2b')
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, style='Status.TLabel')
        self.status_bar.pack(side='bottom', fill='x')
        style.configure('Status.TLabel', background='#1e1e1e', foreground='#a0a0a0')

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Exit', command=self.on_closing)
        menubar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        # Main container frames
        self.video_frame = ttk.Frame(self)
        self.video_frame.pack(pady=10)

        self.video_label = ttk.Label(self.video_frame, text="Webcam not started")
        self.video_label.pack()

        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(pady=5)

        self.start_btn = ttk.Button(self.control_frame, text="Start Webcam", command=self.start_webcam)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(self.control_frame, text="Stop Webcam", command=self.stop_webcam, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.detect_btn = ttk.Button(self.control_frame, text="Detect Emotion & Recommend", command=self.detect_and_recommend, state="disabled")
        self.detect_btn.grid(row=0, column=2, padx=5)

        # Text sentiment analysis
        self.text_frame = ttk.Frame(self)
        self.text_frame.pack(pady=5)

        self.text_entry = ttk.Entry(self.text_frame, width=60)
        self.text_entry.pack(side='left', padx=5)
        self.text_entry.insert(0, "Type a sentence here (optional)...")

        self.text_btn = ttk.Button(self.text_frame, text="Analyze Text", command=self.analyze_text)
        self.text_btn.pack(side='left', padx=5)

        # Result display with scrollbar
        self.result_frame = ttk.Frame(self)
        self.result_frame.pack(pady=10, fill='both', expand=True)

        self.result_text = tk.Text(self.result_frame, height=15, width=80, state="disabled", bg="#1e1e1e", fg="#e0e0e0", insertbackground="#e0e0e0")
        self.result_scroll = ttk.Scrollbar(self.result_frame, orient='vertical', command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=self.result_scroll.set)
        self.result_scroll.pack(side='right', fill='y')
        self.result_text.pack(side='left', fill='both', expand=True)

        # Disable webcam‑related buttons if OpenCV is missing
        if cv2 is None or DeepFace is None:
            self.start_btn.configure(state="disabled")
            self.detect_btn.configure(state="disabled")
            self.video_label.configure(text="Webcam unavailable (missing OpenCV/DeepFace).")

        # Disable text button if TextBlob missing
        if TextBlob is None:
            self.text_btn.configure(state="disabled")
            self.text_entry.configure(state="disabled")

    # ---------- Webcam handling ----------
    def start_webcam(self):
        if cv2 is None:
            messagebox.showerror("Error", "OpenCV is not installed.")
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam.")
            return
        self.stop_event.clear()
        self.video_thread = threading.Thread(target=self.update_video, daemon=True)
        self.video_thread.start()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.detect_btn.configure(state="normal")
        self.video_label.configure(text="Starting video...")

    def stop_webcam(self):
        self.stop_event.set()
        if self.cap:
            self.cap.release()
        self.video_label.configure(image="", text="Webcam stopped")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.detect_btn.configure(state="disabled")

    def update_video(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                continue
            self.current_frame = frame.copy()
            # Convert BGR to RGB for Tkinter
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img = img.resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            # Need to keep a reference to avoid garbage collection
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        # End of loop

    # ---------- Emotion detection & recommendation ----------
    def detect_and_recommend(self):
        if self.current_frame is None:
            messagebox.showwarning("Warning", "No frame captured yet.")
            return
        # DeepFace expects RGB image as numpy array
        rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        try:
            analysis = DeepFace.analyze(rgb, actions=["emotion"], enforce_detection=False)
            emotion = analysis["dominant_emotion"].lower()
        except Exception as e:
            messagebox.showerror("Error", f"Emotion analysis failed: {e}")
            emotion = "neutral"
        # Map to supported emotion list (fallback to neutral)
        if emotion not in SUPPORTED_EMOTIONS:
            emotion = "neutral"
        mood = map_emotion_to_mood(emotion)
        songs = recommend_songs(mood)
        # Build result string
        result = f"Detected Emotion: {emotion}\nMapped Mood: {mood}\n\n"
        if not songs:
            result += "No songs found for this mood."
        else:
            result += "Recommended Songs:\n"
            for idx, s in enumerate(songs, 1):
                result += f"{idx}. {s['song_name']} - {s['artist']} ({s['genre']})\n"
        self.display_result(result)

    def analyze_text(self):
        text = self.text_entry.get().strip()
        if not text:
            messagebox.showinfo("Info", "Please enter some text.")
            return
        emotion = analyse_text_sentiment(text)
        if emotion is None:
            messagebox.showerror("Error", "Text sentiment analysis unavailable.")
            return
        mood = map_emotion_to_mood(emotion)
        songs = recommend_songs(mood)
        result = f"Text Sentiment → Emotion: {emotion}\nMapped Mood: {mood}\n\n"
        if not songs:
            result += "No songs found for this mood."
        else:
            result += "Recommended Songs:\n"
            for idx, s in enumerate(songs, 1):
                result += f"{idx}. {s['song_name']} - {s['artist']} ({s['genre']})\n"
        self.display_result(result)

    def display_result(self, text):
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state="disabled")

    def on_closing(self):
        self.stop_webcam()
        self.destroy()

if __name__ == "__main__":
    app = EmotionMusicApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
