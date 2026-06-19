"""GUI module for the Emotion-Based Music Recommendation System.
Provides a modern Tkinter-based graphical user interface with enhanced styling.
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from deepface import DeepFace
except ImportError:
    DeepFace = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

from .engine import (
    ensure_dataset,
    detect_emotion_from_frame,
    analyze_text_sentiment,
    recommend_songs,
)
from .config import get_emotion_mood_map, get_supported_emotions


class EmotionMusicApp(tk.Tk):
    """Main GUI application for emotion-based music recommendation with modern styling."""

    # Color scheme
    BG_COLOR = "#0f1419"
    FG_COLOR = "#ffffff"
    ACCENT_COLOR = "#00d9ff"
    BUTTON_COLOR = "#1a2332"
    BUTTON_HOVER = "#2d3e50"
    SUCCESS_COLOR = "#00ff88"
    ERROR_COLOR = "#ff6b6b"

    def __init__(self):
        super().__init__()
        self.title("🎵 Emotion-Based Music Recommender 🎵")
        self.geometry("1000x800")
        self.resizable(False, False)
        self.configure(bg=self.BG_COLOR)

        # Configure styles
        self._setup_styles()

        # State variables
        self.cap = None  # cv2.VideoCapture
        self.video_thread = None
        self.stop_event = threading.Event()
        self.current_frame = None  # Latest OpenCV frame (BGR)
        self.is_webcam_active = False

        # Configuration
        self.emotion_mood_map = get_emotion_mood_map()
        self.supported_emotions = get_supported_emotions()

        # UI Elements
        self.create_widgets()
        ensure_dataset()

    def _setup_styles(self):
        """Configure custom styles for a modern look."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure colors
        style.configure("TFrame", background=self.BG_COLOR)
        style.configure("TLabel", background=self.BG_COLOR, foreground=self.FG_COLOR)
        style.configure(
            "Title.TLabel",
            background=self.BG_COLOR,
            foreground=self.ACCENT_COLOR,
            font=("Helvetica", 18, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BG_COLOR,
            foreground=self.ACCENT_COLOR,
            font=("Helvetica", 12, "bold"),
        )
        style.configure(
            "TButton",
            background=self.BUTTON_COLOR,
            foreground=self.FG_COLOR,
            borderwidth=0,
            focuscolor="none",
            padding=10,
            font=("Helvetica", 10, "bold"),
        )
        style.map(
            "TButton",
            background=[("active", self.BUTTON_HOVER)],
        )

        style.configure(
            "Primary.TButton",
            background=self.ACCENT_COLOR,
            foreground=self.BG_COLOR,
            font=("Helvetica", 10, "bold"),
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#00b8cc")],
        )

        style.configure("TEntry", fieldbackground=self.BUTTON_COLOR, foreground=self.FG_COLOR)
        style.configure("TText", background=self.BUTTON_COLOR, foreground=self.FG_COLOR)

    def create_widgets(self):
        """Create and layout all GUI elements with modern design."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = ttk.Label(main_container, text="🎵 Emotion-Based Music Recommender 🎵", style="Title.TLabel")
        title_label.pack(pady=(0, 20))

        # Webcam Section
        webcam_frame = ttk.LabelFrame(main_container, text="📹 Webcam Emotion Detection", padding=15)
        webcam_frame.pack(fill=tk.BOTH, expand=False, pady=10)

        # Video display with better styling
        video_container = ttk.Frame(webcam_frame)
        video_container.pack(fill=tk.BOTH, expand=True, pady=10)

        self.video_label = tk.Label(
            video_container,
            text="🎥 Webcam not started\n\nClick 'Start Webcam' to begin",
            background=self.BUTTON_COLOR,
            foreground=self.ACCENT_COLOR,
            font=("Helvetica", 14),
            height=12,
            width=70,
        )
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Webcam button controls
        webcam_btn_frame = ttk.Frame(webcam_frame)
        webcam_btn_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(
            webcam_btn_frame, text="▶️ Start Webcam", command=self.start_webcam, style="Primary.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.stop_btn = ttk.Button(
            webcam_btn_frame, text="⏹️ Stop Webcam", command=self.stop_webcam, state="disabled"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.detect_btn = ttk.Button(
            webcam_btn_frame,
            text="🎯 Detect & Recommend",
            command=self.detect_and_recommend,
            state="disabled",
            style="Primary.TButton",
        )
        self.detect_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.manage_btn = ttk.Button(
            webcam_btn_frame, text="⚙️ Manage Songs", command=self.open_song_manager
        )
        self.manage_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Status label
        self.status_label = ttk.Label(
            webcam_frame,
            text="Status: Ready",
            foreground=self.SUCCESS_COLOR,
            font=("Helvetica", 9),
        )
        self.status_label.pack(pady=5)

        # Text Analysis Section
        text_frame = ttk.LabelFrame(main_container, text="📝 Text Sentiment Analysis", padding=15)
        text_frame.pack(fill=tk.BOTH, expand=False, pady=10)

        text_label = ttk.Label(text_frame, text="Type a sentence or emotion description:")
        text_label.pack(anchor=tk.W, pady=(0, 5))

        self.text_entry = ttk.Entry(text_frame, width=70)
        self.text_entry.pack(fill=tk.X, pady=5)
        self.text_entry.insert(0, "e.g., 'I feel happy and excited today!'")

        self.text_btn = ttk.Button(
            text_frame, text="💭 Analyze Text & Recommend", command=self.analyze_text, style="Primary.TButton"
        )
        self.text_btn.pack(fill=tk.X, pady=5)

        # Results Section
        results_frame = ttk.LabelFrame(main_container, text="🎼 Recommendations & Results", padding=15)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.result_text = tk.Text(
            results_frame,
            height=12,
            width=95,
            state="disabled",
            bg=self.BUTTON_COLOR,
            fg=self.FG_COLOR,
            insertbackground=self.ACCENT_COLOR,
            font=("Helvetica", 10),
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollbar for results
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

        # Disable webcam buttons if OpenCV/DeepFace is missing
        if cv2 is None or DeepFace is None:
            self.start_btn.configure(state="disabled")
            self.detect_btn.configure(state="disabled")
            self.video_label.configure(text="⚠️ Webcam unavailable\n(Missing OpenCV/DeepFace)")
            self.update_status("Missing dependencies: OpenCV/DeepFace", is_error=True)

        # Disable text button if TextBlob is missing
        if TextBlob is None:
            self.text_btn.configure(state="disabled")
            self.text_entry.configure(state="disabled")
            self.update_status("TextBlob not installed", is_error=True)

    def update_status(self, message, is_error=False):
        """Update status label with color coding."""
        color = self.ERROR_COLOR if is_error else self.SUCCESS_COLOR
        self.status_label.configure(
            text=f"Status: {message}",
            foreground=color,
        )

    # ---------- Webcam handling ----------
    def start_webcam(self):
        """Start the webcam video stream."""
        if cv2 is None:
            messagebox.showerror("Error", "OpenCV is not installed.")
            self.update_status("OpenCV not installed", is_error=True)
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam.")
            self.update_status("Webcam access denied", is_error=True)
            return
        self.stop_event.clear()
        self.is_webcam_active = True
        self.video_thread = threading.Thread(target=self.update_video, daemon=True)
        self.video_thread.start()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.detect_btn.configure(state="normal")
        self.video_label.configure(text="🎥 Webcam is running...")
        self.update_status("Webcam started")

    def stop_webcam(self):
        """Stop the webcam video stream."""
        self.stop_event.set()
        self.is_webcam_active = False
        if self.cap:
            self.cap.release()
        self.video_label.configure(text="⏹️ Webcam stopped\n\nClick 'Start Webcam' to begin again")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.detect_btn.configure(state="disabled")
        self.update_status("Webcam stopped")

    def update_video(self):
        """Continuously capture and display video frames."""
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                continue
            self.current_frame = frame.copy()
            # Convert BGR to RGB for Tkinter
            if Image is None or ImageTk is None:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img = img.resize((800, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            # Keep a reference to avoid garbage collection
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk, text="")

    # ---------- Emotion detection & recommendation ----------
    def detect_and_recommend(self):
        """Detect emotion from the current frame and recommend songs."""
        if self.current_frame is None:
            messagebox.showwarning("Warning", "No frame captured yet.")
            self.update_status("No frame available", is_error=True)
            return

        try:
            self.update_status("Analyzing emotion...")
            emotion = detect_emotion_from_frame(self.current_frame)
            self.update_status(f"Emotion detected: {emotion}")
        except Exception as e:
            messagebox.showerror("Error", f"Emotion analysis failed: {e}")
            self.update_status(f"Analysis failed: {str(e)[:30]}", is_error=True)
            emotion = "neutral"

        # Map to supported emotion list (fallback to neutral)
        if emotion not in self.supported_emotions:
            emotion = "neutral"

        mood = self.emotion_mood_map.get(emotion, "soft")
        songs = recommend_songs(mood)

        # Build result string with better formatting
        result = f"{'=' * 60}\n"
        result += f"🎭 EMOTION DETECTION RESULTS\n"
        result += f"{'=' * 60}\n\n"
        result += f"📊 Detected Emotion:  {emotion.upper()}\n"
        result += f"🎵 Mapped Mood:       {mood.upper()}\n"
        result += f"\n{'=' * 60}\n"
        result += f"🎼 RECOMMENDED SONGS ({len(songs)} found)\n"
        result += f"{'=' * 60}\n\n"

        if not songs:
            result += "❌ No songs found for this mood.\n"
        else:
            for idx, s in enumerate(songs, 1):
                result += f"{idx}. 🎵 {s['song_name']}\n"
                result += f"   Artist: {s['artist']} | Genre: {s['genre']}\n\n"

        self.display_result(result)
        self.update_status(f"✓ Results ready: {emotion} mood", is_error=False)

    def analyze_text(self):
        """Analyze text sentiment and recommend songs."""
        text = self.text_entry.get().strip()
        if not text or text == "e.g., 'I feel happy and excited today!'":
            messagebox.showinfo("Info", "Please enter some text.")
            self.update_status("Please enter text", is_error=True)
            return

        try:
            self.update_status("Analyzing text sentiment...")
            emotion = analyze_text_sentiment(text)
        except Exception as e:
            messagebox.showerror("Error", f"Text sentiment analysis failed: {e}")
            self.update_status(f"Analysis failed: {str(e)[:30]}", is_error=True)
            return

        if emotion is None:
            messagebox.showerror("Error", "Text sentiment analysis unavailable.")
            self.update_status("TextBlob unavailable", is_error=True)
            return

        mood = self.emotion_mood_map.get(emotion, "soft")
        songs = recommend_songs(mood)

        # Build result string with better formatting
        result = f"{'=' * 60}\n"
        result += f"💬 TEXT SENTIMENT ANALYSIS RESULTS\n"
        result += f"{'=' * 60}\n\n"
        result += f"📝 Your Text:        \"{text}\"\n"
        result += f"🎭 Detected Emotion: {emotion.upper()}\n"
        result += f"🎵 Mapped Mood:      {mood.upper()}\n"
        result += f"\n{'=' * 60}\n"
        result += f"🎼 RECOMMENDED SONGS ({len(songs)} found)\n"
        result += f"{'=' * 60}\n\n"

        if not songs:
            result += "❌ No songs found for this mood.\n"
        else:
            for idx, s in enumerate(songs, 1):
                result += f"{idx}. 🎵 {s['song_name']}\n"
                result += f"   Artist: {s['artist']} | Genre: {s['genre']}\n\n"

        self.display_result(result)
        self.update_status(f"✓ Results ready: {emotion} mood", is_error=False)

    def display_result(self, text):
        """Display results in the result text widget with formatting."""
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state="disabled")

    def on_closing(self):
        """Handle window closing event."""
        if self.is_webcam_active:
            self.stop_webcam()
        self.destroy()

    def open_song_manager(self):
        """Open a new window to manage songs."""
        manager_window = tk.Toplevel(self)
        manager_window.title("⚙️ Manage Songs")
        manager_window.geometry("600x400")
        manager_window.configure(bg=self.BG_COLOR)
        
        from .song_manager import list_songs, add_song, delete_song
        
        # Frame for list
        list_frame = ttk.Frame(manager_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("name", "artist", "genre", "mood")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        tree.heading("name", text="Song Name")
        tree.heading("artist", text="Artist")
        tree.heading("genre", text="Genre")
        tree.heading("mood", text="Mood")
        tree.pack(fill=tk.BOTH, expand=True)
        
        def refresh_list():
            for item in tree.get_children():
                tree.delete(item)
            for song in list_songs():
                tree.insert("", tk.END, values=(song["song_name"], song["artist"], song["genre"], song["mood"]), iid=song["_index"])
                
        refresh_list()
        
        # Frame for controls
        control_frame = ttk.Frame(manager_window)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def del_song():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Select a song to delete.")
                return
            idx = int(selected[0])
            delete_song(idx)
            refresh_list()
            
        ttk.Button(control_frame, text="Delete Selected", command=del_song).pack(side=tk.LEFT, padx=5)
        
        # Simple Add inputs
        add_frame = ttk.Frame(manager_window)
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(add_frame, text="Name:", bg=self.BG_COLOR, fg=self.FG_COLOR).grid(row=0, column=0, padx=2)
        entry_name = ttk.Entry(add_frame, width=15)
        entry_name.grid(row=0, column=1, padx=2)
        
        tk.Label(add_frame, text="Artist:", bg=self.BG_COLOR, fg=self.FG_COLOR).grid(row=0, column=2, padx=2)
        entry_artist = ttk.Entry(add_frame, width=15)
        entry_artist.grid(row=0, column=3, padx=2)
        
        tk.Label(add_frame, text="Genre:", bg=self.BG_COLOR, fg=self.FG_COLOR).grid(row=0, column=4, padx=2)
        entry_genre = ttk.Entry(add_frame, width=10)
        entry_genre.grid(row=0, column=5, padx=2)
        
        tk.Label(add_frame, text="Mood:", bg=self.BG_COLOR, fg=self.FG_COLOR).grid(row=1, column=0, padx=2, pady=5)
        entry_mood = ttk.Entry(add_frame, width=15)
        entry_mood.grid(row=1, column=1, padx=2, pady=5)
        
        def do_add():
            if not entry_name.get() or not entry_mood.get():
                messagebox.showerror("Error", "Name and Mood are required.")
                return
            add_song(entry_name.get(), entry_artist.get(), entry_genre.get(), entry_mood.get())
            refresh_list()
            entry_name.delete(0, tk.END)
            entry_artist.delete(0, tk.END)
            entry_genre.delete(0, tk.END)
            entry_mood.delete(0, tk.END)
            
        ttk.Button(add_frame, text="Add Song", command=do_add).grid(row=1, column=2, columnspan=2, padx=5, pady=5)
