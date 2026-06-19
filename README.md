# 🎵 Emotion-Based Music System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)
![DeepFace](https://img.shields.io/badge/DeepFace-Latest-orange.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

## 📖 Project Overview
The **Emotion-Based Music System** is a dynamic application that detects a user's current emotion—either via facial expression analysis or text sentiment analysis—and recommends tailored music tracks to match their mood. 

Whether you are feeling happy, sad, or motivated, this system seamlessly maps your emotion to an appropriate musical vibe and provides instant recommendations from a customizable local dataset.

---

## ✨ Features
- **Text Emotion Detection**: Type a sentence and let the AI analyze your sentiment (powered by `TextBlob` & `NLTK VADER`).
- **Image Emotion Detection**: Upload a photo or use your webcam to detect facial emotions (powered by `DeepFace` & `OpenCV`).
- **Smart Recommendation Engine**: Maps detected emotions to specific moods (e.g., Happy ➡️ Energetic) and shuffles recommendations.
- **Desktop GUI**: A polished, dark-themed Tkinter application for seamless desktop usage.
- **Web API**: A robust FastAPI backend serving a modern, glassmorphism-styled web interface.
- **Built-in Song Management**: Add, edit, or delete songs from your dataset directly through the desktop UI.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Core application logic and backend |
| **FastAPI** | REST API and Web Server |
| **DeepFace** | Facial emotion recognition |
| **TextBlob** | Text sentiment analysis |
| **Tkinter** | Native Desktop GUI |
| **HTML/CSS/JS**| Modern Web Interface |

---

## 🚀 Installation Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/phanindra267/Emotion-Based-Music-System.git
   cd Emotion-Based-Music-System
   ```

2. **Run the setup script (Windows):**
   This script will automatically create a virtual environment and install all dependencies.
   ```powershell
   .\setup.ps1
   ```
   *Alternatively, manually create a virtual environment and run `pip install -r requirements.txt`.*

3. **Activate the environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

---

## 🎮 Running the Project

### 1. Desktop Application (Tkinter GUI)
To launch the native desktop application with webcam support:
```bash
python main.py
```

### 2. Web Server (FastAPI + Web UI)
To launch the local web server and access the browser interface:
```bash
python main.py --serve
```
Then, open your browser and navigate to: **http://localhost:8000**

### 3. Headless CLI Mode
To analyze a static image directly from the terminal without any UI:
```bash
python main.py --headless --image path/to/your/photo.jpg
```

---

## 🌐 API Endpoints

The FastAPI backend exposes the following REST endpoints for seamless integration:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze/text` | **POST** | Detect emotion from provided text and return song recommendations. |
| `/api/analyze/image` | **POST** | Detect emotion from an uploaded image file and return song recommendations. |
| `/api/songs` | **GET** | Retrieve the entire music dataset. |

---

## 📂 Project Structure

```text
Emotion-Based-Music-System/
├── app/                  # Core Python modules (engine, api, gui, song_manager)
├── config/               
│   └── config.json       # Theme settings and emotion-to-mood mappings
├── data/                 
│   └── songs.csv         # Local music dataset
├── tests/                # Unit tests
├── web/                  # Frontend HTML/CSS/JS files
├── .venv/                # Virtual environment (ignored by git)
├── .gitignore            # Git ignore rules
├── main.py               # Main entrypoint
├── README.md             # Project documentation (this file)
├── requirements.txt      # Python dependencies
└── setup.ps1             # Windows setup script
```

---

## 🔮 Future Improvements
- [ ] Upgrade ML models for deeper contextual sentiment analysis.
- [ ] Implement `.env` support for dynamic configuration flexibility.
- [ ] Integrate a cloud database (e.g., Firebase or PostgreSQL) for shared datasets.
- [ ] Add an authentication system for user-specific playlists and history.
- [ ] Direct audio playback integration (Spotify API or local MP3s).
