document.addEventListener("DOMContentLoaded", () => {
  let remainingSeconds = 900;

  const timeLeftEl = document.getElementById("time-left");
  const timerPanel = document.getElementById("session-timer");
  const modal = document.getElementById("timeout-modal");
  const modalTimeLeft = document.getElementById("modal-time-left");
  const stayBtn = document.getElementById("stay-logged-in");

  function updateTimerDisplay() {
    const minutes = String(Math.floor(remainingSeconds / 60)).padStart(2, "0");
    const seconds = String(remainingSeconds % 60).padStart(2, "0");
    timeLeftEl.textContent = `${minutes}:${seconds}`;

    if (remainingSeconds <= 60) {
      // Urgent red style
      timerPanel.style.background = "#f8d7da";
      timerPanel.style.borderLeft = "5px solid #dc3545";
      timerPanel.style.color = "#721c24";
      timerPanel.style.fontWeight = "bold";
    } else {
      // Normal yellow style
      timerPanel.style.background = "#ffeb3b";
      timerPanel.style.borderLeft = "5px solid #f57c00";
      timerPanel.style.color = "#000";
      timerPanel.style.fontWeight = "bold";
    }
  }

  function tick() {
    remainingSeconds--;
    updateTimerDisplay();

    // Show modal at 30 seconds
    if (remainingSeconds === 30) {
      modal.style.display = "flex";
      modalTimeLeft.textContent = "30";
    }

    // Update modal countdown if visible
    if (modal.style.display === "flex") {
      modalTimeLeft.textContent = remainingSeconds;
    }

    // Session expired
    if (remainingSeconds <= 0) {
      // Let admin.html know session expired so it can hide logout button
      document.dispatchEvent(new Event("sessionExpired"));
      window.location.href = "/admin/login";
    }
  }

  function resetTimer() {
    remainingSeconds = 300;
    updateTimerDisplay();
    modal.style.display = "none";
  }

  // Reset timer on activity
  ["click", "keypress", "mousemove", "scroll"].forEach((evt) => {
    document.addEventListener(evt, resetTimer);
  });

  // Stay Logged In button
  stayBtn.addEventListener("click", () => {
    fetch("/api/admin/ping", { method: "POST" })
      .then(() => {
        resetTimer();
      })
      .catch(() => {
        resetTimer();
      });
  });

  updateTimerDisplay();
  setInterval(tick, 1000);
});
