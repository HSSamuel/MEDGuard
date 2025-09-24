document.addEventListener("DOMContentLoaded", () => {
  // These must match the backend settings
  const SESSION_TIMEOUT_MINUTES = 15;
  const WARNING_TIME_SECONDS = 120; // Show warning modal 2 minutes before timeout

  // Get all the elements we need to interact with
  const modal = document.getElementById("session-modal");
  const modalCountdownSpan = document.getElementById("session-countdown");
  const stayBtn = document.getElementById("session-stay-btn");
  const logoutBtn = document.getElementById("session-logout-btn");
  const dashboardCountdownDisplay = document.getElementById(
    "session-countdown-display"
  );

  // If the modal doesn't exist, this isn't an admin page, so we stop.
  if (!modal) {
    return;
  }

  let masterInterval;
  let remainingSeconds = SESSION_TIMEOUT_MINUTES * 60;

  const logout = () => {
    // Find the admin logout form for a clean logout
    const logoutForm = document.querySelector('form[action*="admin/logout"]');
    if (logoutForm) {
      logoutForm.submit();
    } else {
      // Fallback if form isn't on the page
      window.location.href = "/admin/login";
    }
  };

  const stayLoggedIn = () => {
    // Ping the server to refresh the session
    fetch("/admin/session/ping", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then((res) => {
        if (res.ok) {
          console.log("Session refreshed successfully.");
          resetTimers(); // Reset all timers on success
        } else {
          alert("Your session has already expired. Please log in again.");
          logout();
        }
      })
      .catch(() => {
        alert("A connection error occurred. Could not refresh the session.");
      });
  };

  const updateDisplays = () => {
    // Format the remaining time into MM:SS
    const minutes = Math.floor(remainingSeconds / 60)
      .toString()
      .padStart(2, "0");
    const seconds = (remainingSeconds % 60).toString().padStart(2, "0");

    // Update the main dashboard display
    if (dashboardCountdownDisplay) {
      dashboardCountdownDisplay.textContent = `${minutes}:${seconds}`;
    }

    // Show the modal and update its countdown if we are in the warning period
    if (remainingSeconds <= WARNING_TIME_SECONDS) {
      modal.style.display = "flex";
      modalCountdownSpan.textContent = remainingSeconds;
    } else {
      modal.style.display = "none";
    }

    // When the timer hits zero, log out
    if (remainingSeconds <= 0) {
      clearInterval(masterInterval);
      logout();
    }

    remainingSeconds--; // Decrement the timer
  };

  const resetTimers = () => {
    // Clear the main interval
    clearInterval(masterInterval);

    // Hide the warning modal
    modal.style.display = "none";

    // Reset the countdown to the full duration
    remainingSeconds = SESSION_TIMEOUT_MINUTES * 60;

    // Start a new master interval that runs every second
    masterInterval = setInterval(updateDisplays, 1000);
  };

  // --- Initialize Everything ---
  stayBtn.addEventListener("click", stayLoggedIn);
  logoutBtn.addEventListener("click", logout);

  // Any user activity will reset the countdown
  ["click", "mousemove", "keypress", "scroll"].forEach((event) => {
    window.addEventListener(event, resetTimers);
  });

  // Start the timers when the page first loads
  resetTimers();
});
