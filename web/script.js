// script.js – handles emotion detection via API

const API_BASE_URL = "http://localhost:8000/api";

document.addEventListener("DOMContentLoaded", () => {
  const btnTextTab = document.getElementById("btnTextTab");
  const btnImageTab = document.getElementById("btnImageTab");
  const textInputArea = document.getElementById("textInputArea");
  const imageInputArea = document.getElementById("imageInputArea");

  const analyzeTextBtn = document.getElementById("analyzeTextBtn");
  const textInput = document.getElementById("textInput");

  const analyzeImageBtn = document.getElementById("analyzeImageBtn");
  const imageInput = document.getElementById("imageInput");

  const loadingIndicator = document.getElementById("loadingIndicator");

  // Tab Switching
  btnTextTab.addEventListener("click", () => {
    btnTextTab.classList.add("active");
    btnImageTab.classList.remove("active");
    textInputArea.style.display = "block";
    imageInputArea.style.display = "none";
  });

  btnImageTab.addEventListener("click", () => {
    btnImageTab.classList.add("active");
    btnTextTab.classList.remove("active");
    imageInputArea.style.display = "block";
    textInputArea.style.display = "none";
  });

  // Analyze Text
  analyzeTextBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) {
      alert("Please enter some text!");
      return;
    }
    
    showLoading();
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data = await handleResponse(response);
      renderResults(data);
    } catch (e) {
      showError(e.message);
    }
  });

  // Analyze Image
  analyzeImageBtn.addEventListener("click", async () => {
    const file = imageInput.files[0];
    if (!file) {
      alert("Please select an image file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    showLoading();
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/image`, {
        method: "POST",
        body: formData
      });
      const data = await handleResponse(response);
      renderResults(data);
    } catch (e) {
      showError(e.message);
    }
  });
});

function showLoading() {
  document.getElementById("loadingIndicator").style.display = "block";
  document.getElementById("results").innerHTML = "";
}

function hideLoading() {
  document.getElementById("loadingIndicator").style.display = "none";
}

async function handleResponse(response) {
  hideLoading();
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error: ${response.status}`);
  }
  return await response.json();
}

function showError(msg) {
  hideLoading();
  document.getElementById("results").innerHTML = `<p style="color:#ff8c42;">⚠️ ${msg}</p>`;
}

function renderResults(data) {
  const resultsDiv = document.getElementById("results");
  const { emotion, mood, songs } = data;

  if (!songs || songs.length === 0) {
    resultsDiv.innerHTML = `<p>Detected Emotion: <strong>${emotion}</strong> → Mood: <strong>${mood}</strong></p><p>No songs found for this mood.</p>`;
    return;
  }

  const cards = songs
    .map(
      song => `<div class="result-card">
          <h3>${song.song_name}</h3>
          <p><strong>Artist:</strong> ${song.artist}</p>
          <p><strong>Genre:</strong> ${song.genre}</p>
        </div>`
    )
    .join("");
    
  resultsDiv.innerHTML = `<p>Detected Emotion: <strong>${emotion}</strong> → Mood: <strong>${mood}</strong></p>` + cards;
}
