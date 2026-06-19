# Emotion‑Music Web Interface

## Overview
This lightweight **static web UI** provides a modern, premium‑looking interface for the Emotion‑Based Music Recommender. Users can select an emotion, click **Recommend Songs**, and see a list of matching tracks from the `songs.csv` dataset.

## Folder Layout
```
emotion_music_system/
│   emotion_music_system.py   # Original Tkinter app (unchanged)
│   songs.csv                # Data source (used by both apps)
│   ...
└── web/                    # <-- web UI files
    │   index.html
    │   style.css
    │   script.js
    │   README.md   <-- (this file)
```

## Running the Web UI
1. Open a command prompt and **navigate** to the `web` directory:
   ```
   cd "C:\Users\phani\OneDrive\Apps\emotion_music_system\web"
   ```
2. Start a simple HTTP server (Python 3 includes it out‑of‑the‑box):
   ```
   python -m http.server 8000
   ```
   This serves the files on `http://localhost:8000`.
3. Open a browser and go to:
   ```
   http://localhost:8000
   ```
4. Choose an emotion from the dropdown and click **Recommend Songs**. The results appear instantly, styled with a dark‑mode glassmorphism aesthetic.

## How It Works
- `script.js` fetches `../songs.csv` (the CSV located one level above the `web` folder).
- It parses the CSV, maps the selected emotion to a mood using the same dictionary as the Python backend, and randomly selects up to 5 matching songs.
- The UI is built with **vanilla HTML/CSS/JS**, no external libraries needed beyond the Google Fonts import.

## Customisation
- **Add more emotions/moods**: edit the `EMOTION_MOOD_MAP` object in `script.js`.
- **Change colours or layout**: modify `style.css`. The design follows modern dark‑mode principles with subtle micro‑animations.
- **Extend dataset**: add rows to `songs.csv` (same columns: `song_name,artist,genre,mood,tempo`).

Enjoy the new premium web experience!
