# main.py
"""Entry point for the Emotion‑Based Music Recommendation System.

Usage:
    python main.py                  # launches the Tkinter GUI
    python main.py --headless --image <path>  # processes a static image and prints results
"""

import argparse
import sys
from pathlib import Path

# Import the engine functions
from app.engine import process_image_file

def run_gui():
    """Launch the graphical user interface."""
    # The GUI implementation lives in app.gui
    from app.gui import EmotionMusicApp
    app = EmotionMusicApp()
    app.mainloop()

def run_headless(image_path: str):
    """Run in head‑less mode: analyse a single image and print the results."""
    if not Path(image_path).is_file():
        print(f"[ERROR] Image file not found: {image_path}")
        sys.exit(1)
    result = process_image_file(image_path)
    print("--- Emotion Detection Result ---")
    print(f"Detected emotion : {result['emotion']}")
    print(f"Mapped mood      : {result['mood']}")
    print("Recommended songs:")
    if not result["songs"]:
        print("  No songs found for this mood.")
    else:
        for i, song in enumerate(result["songs"], 1):
            print(f"  {i}. {song['song_name']} – {song['artist']} ({song['genre']})")

def run_server():
    """Run the FastAPI backend server."""
    import uvicorn
    print("Starting Emotion Music API server on http://localhost:8000")
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Emotion‑Based Music Recommendation System")
    parser.add_argument("--headless", action="store_true", help="Run without GUI (process a single image)")
    parser.add_argument("--image", type=str, help="Path to an image file (required with --headless)")
    parser.add_argument("--serve", action="store_true", help="Start the FastAPI backend server for the web UI")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.serve:
        run_server()
    elif args.headless:
        if not args.image:
            print("[ERROR] --image is required when using --headless")
            sys.exit(1)
        run_headless(args.image)
    else:
        run_gui()
