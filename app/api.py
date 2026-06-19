"""FastAPI Backend for Emotion-Based Music Recommendation System.
Provides REST APIs for text and image-based emotion detection,
and serving the static web interface.
"""

import logging
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .engine import (
    analyze_text_sentiment,
    detect_emotion_from_frame,
    map_emotion_to_mood,
    recommend_songs
)
from .song_manager import list_songs
from .config import get_project_root

import os

app = FastAPI(title="Emotion Music API", version="1.0")

# Add CORS middleware to allow the frontend to access the API if served separately
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class TextAnalysisRequest(BaseModel):
    text: str

@app.post("/api/analyze/text")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text sentiment and return emotion, mood, and songs."""
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
        
    logging.info(f"API Request: Analyze text: '{text[:30]}...'")
    try:
        emotion = analyze_text_sentiment(text)
        mood = map_emotion_to_mood(emotion)
        songs = recommend_songs(mood)
        return {"emotion": emotion, "mood": mood, "songs": songs}
    except Exception as e:
        logging.error(f"Error in text analysis API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze uploaded image for facial emotion and return recommendations."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
        
    logging.info(f"API Request: Analyze image: '{file.filename}'")
    try:
        # Read image bytes
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file.")
            
        emotion = detect_emotion_from_frame(img)
        mood = map_emotion_to_mood(emotion)
        songs = recommend_songs(mood)
        return {"emotion": emotion, "mood": mood, "songs": songs}
    except Exception as e:
        logging.error(f"Error in image analysis API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/songs")
async def get_songs():
    """Return all songs from the CSV."""
    logging.info("API Request: Get all songs")
    try:
        songs = list_songs()
        return {"songs": songs}
    except Exception as e:
        logging.error(f"Error fetching songs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files for the web interface
web_dir = os.path.join(get_project_root(), "web")
if os.path.isdir(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")
