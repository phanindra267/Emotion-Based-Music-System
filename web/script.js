// script.js – handles emotion selection, CSV loading, and song recommendation

// Mapping from emotion (lowercase) to mood (same as Python version)
const EMOTION_MOOD_MAP = {
  happy: "energetic",
  sad: "calm",
  angry: "motivational",
  neutral: "soft",
  surprise: "upbeat",
  fear: "motivational",
  disgust: "motivational"
};

// Utility: parse CSV string into array of objects
function parseCSV(csvText) {
  const lines = csvText.trim().split(/\r?\n/);
  const header = lines[0].split(',').map(h => h.trim());
  const rows = lines.slice(1).map(line => {
    const values = line.split(',').map(v => v.trim());
    const obj = {};
    header.forEach((key, i) => (obj[key] = values[i]));
    return obj;
  });
  return rows;
}

// Load the songs dataset (relative to the web folder)
async function loadSongs() {
  const response = await fetch("songs.csv");
  if (!response.ok) {
    throw new Error("Failed to load songs.csv");
  }
  const text = await response.text();
  return parseCSV(text);
}

// Recommend up to n songs for a given mood
function recommendSongs(songs, mood, n = 5) {
  const filtered = songs.filter(s => s.mood && s.mood.trim().toLowerCase() === mood);
  if (filtered.length === 0) return [];
  // Shuffle and take n
  const shuffled = filtered.sort(() => Math.random() - 0.5);
  return shuffled.slice(0, n);
}

// UI handling
document.addEventListener("DOMContentLoaded", async () => {
  const emotionSelect = document.getElementById("emotionSelect");
  const recommendBtn = document.getElementById("recommendBtn");
  const resultsDiv = document.getElementById("results");

  let songsData = [];
  try {
    songsData = await loadSongs();
  } catch (e) {
    resultsDiv.innerHTML = `<p style="color:#ff8c42;">⚠️ ${e.message}</p>`;
    console.error(e);
    return;
  }

  recommendBtn.addEventListener("click", () => {
    const emotion = emotionSelect.value.toLowerCase();
    const mood = EMOTION_MOOD_MAP[emotion] || "soft"; // fallback
    const recommendations = recommendSongs(songsData, mood);
    renderResults(recommendations, emotion, mood);
  });
});

function renderResults(recs, emotion, mood) {
  const resultsDiv = document.getElementById("results");
  if (recs.length === 0) {
    resultsDiv.innerHTML = `<p>No songs found for mood "${mood}".</p>`;
    return;
  }
  const cards = recs
    .map(
      song => `<div class="result-card" data-mood="${song.mood}">
          <h3>${song.song_name}</h3>
          <p><strong>Artist:</strong> ${song.artist}</p>
          <p><strong>Genre:</strong> ${song.genre}</p>
        </div>`
    )
    .join("");
  resultsDiv.innerHTML = `<p>Detected Emotion: <strong>${emotion}</strong> → Mood: <strong>${mood}</strong></p>` + cards;
}
