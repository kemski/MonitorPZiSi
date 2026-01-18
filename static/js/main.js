/**
 * Główny plik JavaScript
 *
 * Funkcjonalności:
 * - Timer Pomodoro z przyciskami
 * - Wyświetlanie ćwiczeń
 * - Przesyłanie i analiza zdjęć postawy
 * - Wyświetlanie sugestii ergonomicznych
 */

// Zmienne globalne
let timerInterval = null;
let selectedFile = null;
let isTimerRunning = false;
let isTimerPaused = false;
let lastTimerType = null;
let lastRemainingSeconds = -1;
let audioContext = null;

// Inicjalizacja po załadowaniu strony
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

/**
 * Inicjalizacja aplikacji
 */
function initializeApp() {
  // Załadowanie ćwiczeń
  loadExercises();

  // Załadowanie sugestii ergonomicznych
  loadErgonomicSuggestions();

  // Ustawienie event listenerów
  setupEventListeners();

  // Aktualizacja timera
  updateTimer();
}

/**
 * Ustawienie event listenerów dla przycisków i interakcji
 */
function setupEventListeners() {
  // Przyciski timera
  document
    .getElementById("pomodoro-btn")
    .addEventListener("click", startPomodoro);
  document.getElementById("break-btn").addEventListener("click", startBreak);
  document.getElementById("play-btn").addEventListener("click", resumeTimer);
  document.getElementById("pause-btn").addEventListener("click", pauseTimer);

  // Przyciski analizy postawy
  document.getElementById("upload-btn").addEventListener("click", () => {
    document.getElementById("posture-image-input").click();
  });

  document
    .getElementById("posture-image-input")
    .addEventListener("change", handleFileSelect);
  document
    .getElementById("analyze-btn")
    .addEventListener("click", analyzePosture);

  // Modal ćwiczeń
  const modal = document.getElementById("exercise-modal");
  const closeBtn = document.querySelector(".close");

  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
}

/**
 * Rozpoczęcie timera Pomodoro (25 minut)
 */
async function startPomodoro() {
  try {
    const response = await fetch("/api/timer/pomodoro", {
      method: "POST",
    });

    const data = await response.json();

    if (data.status === "success") {
      isTimerRunning = true;
      isTimerPaused = false;
      lastRemainingSeconds = -1; // Reset dla wykrywania końca
      startTimerUpdate();
      updateButtonStates();
    }
  } catch (error) {
    console.error("Błąd podczas rozpoczynania Pomodoro:", error);
  }
}

/**
 * Rozpoczęcie timera przerwy (5 minut)
 */
async function startBreak() {
  try {
    const response = await fetch("/api/timer/break", {
      method: "POST",
    });

    const data = await response.json();

    if (data.status === "success") {
      isTimerRunning = true;
      isTimerPaused = false;
      lastRemainingSeconds = -1; // Reset dla wykrywania końca
      startTimerUpdate();
      updateButtonStates();
    }
  } catch (error) {
    console.error("Błąd podczas rozpoczynania przerwy:", error);
  }
}

/**
 * Pauzowanie timera
 */
async function pauseTimer() {
  try {
    const response = await fetch("/api/timer/pause", {
      method: "POST",
    });

    const data = await response.json();

    if (data.status === "success") {
      isTimerPaused = true;
      stopTimerUpdate();
      updateButtonStates();
    }
  } catch (error) {
    console.error("Błąd podczas pauzowania timera:", error);
  }
}

/**
 * Wznowienie timera
 */
async function resumeTimer() {
  try {
    const response = await fetch("/api/timer/resume", {
      method: "POST",
    });

    const data = await response.json();

    if (data.status === "success") {
      isTimerPaused = false;
      startTimerUpdate();
      updateButtonStates();
    }
  } catch (error) {
    console.error("Błąd podczas wznawiania timera:", error);
  }
}

/**
 * Rozpoczęcie aktualizacji timera
 */
function startTimerUpdate() {
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  timerInterval = setInterval(updateTimer, 100);
}

/**
 * Zatrzymanie aktualizacji timera
 */
function stopTimerUpdate() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

/**
 * Aktualizacja wyświetlanego timera
 */
async function updateTimer() {
  try {
    const response = await fetch("/api/timer");
    const data = await response.json();

    const timerDisplay = document.getElementById("timer-display");
    timerDisplay.textContent = data.remaining_formatted;

    // Ostrzeżenie, gdy czas się kończy (mniej niż 1 minuta)
    if (data.remaining_seconds < 60 && data.remaining_seconds > 0) {
      timerDisplay.classList.add("warning");
    } else {
      timerDisplay.classList.remove("warning");
    }

    // Wykrycie końca timera i odtworzenie odpowiedniego dźwięku
    // Sprawdzamy, czy timer właśnie się skończył (był > 0, teraz jest 0)
    if (
      data.remaining_seconds === 0 &&
      lastRemainingSeconds > 0 &&
      data.running &&
      !data.paused
    ) {
      // Timer się właśnie skończył
      stopTimerUpdate();
      isTimerRunning = false;
      updateButtonStates();

      // Odtworzenie odpowiedniego dźwięku w zależności od typu timera
      if (data.timer_type === "pomodoro") {
        // Czas na przerwę - dźwięk Y (wyższy, melodyjny)
        playAlarmSound("pomodoro");
        if (
          typeof Notification !== "undefined" &&
          Notification.permission === "granted"
        ) {
          new Notification("Czas na przerwę! 🍅");
        }
      } else if (data.timer_type === "break") {
        // Wracamy do pracy - dźwięk X (niższy, rytmiczny)
        playAlarmSound("break");
        if (
          typeof Notification !== "undefined" &&
          Notification.permission === "granted"
        ) {
          new Notification("Wracamy do pracy! 💼");
        }
      }
    }

    // Aktualizacja ostatniego stanu
    lastRemainingSeconds = data.remaining_seconds;

    // Śledzenie zmiany typu timera
    if (data.timer_type !== lastTimerType) {
      lastTimerType = data.timer_type;
    }

    isTimerRunning = data.running;
    isTimerPaused = data.paused;
    updateButtonStates();
  } catch (error) {
    console.error("Błąd podczas aktualizacji timera:", error);
  }
}

/**
 * Aktualizacja stanu przycisków
 */
function updateButtonStates() {
  const playBtn = document.getElementById("play-btn");
  const pauseBtn = document.getElementById("pause-btn");

  if (isTimerRunning && !isTimerPaused) {
    playBtn.disabled = true;
    pauseBtn.disabled = false;
  } else if (isTimerPaused) {
    playBtn.disabled = false;
    pauseBtn.disabled = true;
  } else {
    playBtn.disabled = true;
    pauseBtn.disabled = true;
  }
}

/**
 * Załadowanie listy ćwiczeń
 */
async function loadExercises() {
  try {
    const response = await fetch("/api/exercises");
    const data = await response.json();

    const exercisesGrid = document.getElementById("exercises-grid");
    exercisesGrid.innerHTML = "";

    data.exercises.forEach((exercise) => {
      const exerciseCard = createExerciseCard(exercise);
      exercisesGrid.appendChild(exerciseCard);
    });
  } catch (error) {
    console.error("Błąd podczas ładowania ćwiczeń:", error);
  }
}

/**
 * Utworzenie karty ćwiczenia
 */
function createExerciseCard(exercise) {
  const card = document.createElement("div");
  card.className = "exercise-card";
  card.addEventListener("click", () => showExerciseDetails(exercise.id));

  card.innerHTML = `
        <h3>${exercise.name}</h3>
        <p><strong>Kategoria:</strong> ${exercise.category}</p>
        <p><strong>Czas trwania:</strong> ${exercise.duration}</p>
        <span class="exercise-badge">${exercise.difficulty}</span>
    `;

  return card;
}

/**
 * Wyświetlenie szczegółów ćwiczenia w modalu
 */
async function showExerciseDetails(exerciseId) {
  try {
    const response = await fetch(`/api/exercise/${exerciseId}`);
    const exercise = await response.json();

    const modal = document.getElementById("exercise-modal");
    const detailsDiv = document.getElementById("exercise-details");

    detailsDiv.innerHTML = `
            <h2>${exercise.name}</h2>
            <p><strong>Kategoria:</strong> ${exercise.category}</p>
            <p><strong>Czas trwania:</strong> ${exercise.duration}</p>
            <p><strong>Poziom trudności:</strong> ${exercise.difficulty}</p>
            <p>${exercise.description}</p>

            <h3>Instrukcje wykonania:</h3>
            <ol>
                ${exercise.instructions
                  .map((instruction) => `<li>${instruction}</li>`)
                  .join("")}
            </ol>

            <h3>Korzyści:</h3>
            <ul>
                ${exercise.benefits
                  .map((benefit) => `<li>${benefit}</li>`)
                  .join("")}
            </ul>
        `;

    modal.style.display = "block";
  } catch (error) {
    console.error("Błąd podczas ładowania szczegółów ćwiczenia:", error);
  }
}

/**
 * Obsługa wyboru pliku zdjęcia
 */
function handleFileSelect(event) {
  const file = event.target.files[0];

  if (file) {
    selectedFile = file;
    document.getElementById("file-name").textContent = `Wybrano: ${file.name}`;

    // Wyświetlenie podglądu
    const reader = new FileReader();
    reader.onload = function (e) {
      const preview = document.getElementById("upload-preview");
      const previewImg = document.getElementById("preview-image");

      previewImg.src = e.target.result;
      preview.style.display = "block";
    };
    reader.readAsDataURL(file);
  }
}

/**
 * Analiza przesłanego zdjęcia postawy
 */
async function analyzePosture() {
  if (!selectedFile) {
    alert("Najpierw wybierz zdjęcie");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("image", selectedFile);

    const analyzeBtn = document.getElementById("analyze-btn");
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analizowanie...";

    const response = await fetch("/api/posture/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Przeanalizuj Postawę";

    if (data.status === "success") {
      displayAnalysisResults(data.analysis);
    } else {
      alert(data.message || "Błąd podczas analizy");
    }
  } catch (error) {
    console.error("Błąd podczas analizy postawy:", error);
    alert("Błąd podczas analizy postawy");
    document.getElementById("analyze-btn").disabled = false;
    document.getElementById("analyze-btn").textContent = "Przeanalizuj Postawę";
  }
}

/**
 * Wyświetlenie wyników analizy postawy
 */
function displayAnalysisResults(analysis) {
  const resultsDiv = document.getElementById("analysis-results");

  let html = `
        <h3>Wyniki analizy postawy</h3>
        <div class="alert ${
          analysis.is_correct_posture ? "alert-success" : "alert-warning"
        }">
            <strong>${analysis.message}</strong>
        </div>
    `;

  if (analysis.suggestions && analysis.suggestions.length > 0) {
    html += "<h4>Sugestie poprawy:</h4>";

    analysis.suggestions.forEach((suggestion) => {
      const priorityClass = `priority-${suggestion.priority}`;
      html += `
                <div class="suggestion-item ${priorityClass}">
                    <h4>${suggestion.title} (${suggestion.category})</h4>
                    <p>${suggestion.description}</p>
                    ${
                      suggestion.detected_issue
                        ? `<p class="detected-issue"><em>Wykryty problem: ${suggestion.detected_issue}</em></p>`
                        : ""
                    }
                </div>
            `;
    });
  }

  resultsDiv.innerHTML = html;
  resultsDiv.style.display = "block";

  // Przewinięcie do wyników
  resultsDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Załadowanie sugestii ergonomicznych
 */
async function loadErgonomicSuggestions() {
  try {
    const response = await fetch("/api/posture/suggestions");
    const data = await response.json();

    const suggestionsList = document.getElementById("suggestions-list");
    suggestionsList.innerHTML = "";

    data.suggestions.forEach((suggestion) => {
      const categoryDiv = document.createElement("div");
      categoryDiv.className = "suggestion-category";

      categoryDiv.innerHTML = `
                <h3>${suggestion.title}</h3>
                <ul>
                    ${suggestion.points
                      .map((point) => `<li>${point}</li>`)
                      .join("")}
                </ul>
            `;

      suggestionsList.appendChild(categoryDiv);
    });
  } catch (error) {
    console.error("Błąd podczas ładowania sugestii ergonomicznych:", error);
  }
}

/**
 * Inicjalizacja AudioContext dla dźwięków
 */
function initAudioContext() {
  if (!audioContext) {
    try {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    } catch (e) {
      console.error("Nie można utworzyć AudioContext:", e);
    }
  }
  return audioContext;
}

/**
 * Odtwarzanie dźwięku alarmu
 * @param {string} type - 'pomodoro' (czas na przerwę) lub 'break' (wracamy do pracy)
 */
function playAlarmSound(type) {
  const ctx = initAudioContext();
  if (!ctx) {
    console.error("AudioContext nie jest dostępny");
    return;
  }

  try {
    if (type === "pomodoro") {
      // Dźwięk Y - czas na przerwę (wyższy, bardziej melodyjny)
      // Sekwencja rosnących dźwięków
      playToneSequence(ctx, [800, 1000, 1200, 1400], 0.25, 0.4);
    } else if (type === "break") {
      // Dźwięk X - wracamy do pracy (niższy, bardziej rytmiczny)
      // Sekwencja rytmicznych dźwięków
      playToneSequence(ctx, [400, 500, 400, 600], 0.2, 0.4);
    }
  } catch (e) {
    console.error("Błąd podczas odtwarzania dźwięku:", e);
  }
}

/**
 * Odtwarzanie sekwencji dźwięków
 */
function playToneSequence(ctx, frequencies, duration, volume) {
  frequencies.forEach((freq, index) => {
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);

    oscillator.frequency.value = freq;
    oscillator.type = "sine";

    const startTime = ctx.currentTime + index * duration * 1.3;
    gainNode.gain.setValueAtTime(0, startTime);
    gainNode.gain.linearRampToValueAtTime(volume, startTime + 0.05);
    gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + duration);

    oscillator.start(startTime);
    oscillator.stop(startTime + duration);
  });
}

// Prośba o pozwolenie na powiadomienia
if ("Notification" in window && Notification.permission === "default") {
  Notification.requestPermission();
}
