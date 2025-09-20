// =========================
// Rotating tagline
// =========================
const taglines = [
  "Because your health deserves the truth.",
  "No more guessing — just scanning.",
  "Keeping counterfeit meds off the streets.",
  "Your pocket pharmacist.",
];
let taglineIndex = 0;
function rotateTagline() {
  const taglineEl = document.getElementById("tagline");
  if (taglineEl) {
    taglineEl.textContent = taglines[taglineIndex];
    taglineIndex = (taglineIndex + 1) % taglines.length;
  }
}
setInterval(rotateTagline, 3000);
rotateTagline(); // initial load

// =========================
// QR Scanner
// =========================
let html5QrCode;
const qrRegionId = "qr-reader";

function startScanner() {
  if (!html5QrCode) {
    html5QrCode = new Html5Qrcode(qrRegionId);
  }
  html5QrCode
    .start(
      { facingMode: "environment" },
      { fps: 10, qrbox: 250 },
      (decodedText) => {
        stopScanner();
        openVerificationPage(decodedText);
      },
      () => {} // ignore scan errors
    )
    .catch((err) => {
      console.error("Unable to start scanning:", err);
      showMessage("Camera access failed. Please check permissions.", "error");
    });
}

function stopScanner() {
  if (html5QrCode) {
    html5QrCode.stop().catch((err) => console.error("Stop failed:", err));
  }
}

// =========================
// Open verification page in new tab
// =========================
function openVerificationPage(batchNumber) {
  if (!batchNumber) {
    showMessage("Please enter a batch number.", "error");
    return;
  }
  // CORRECTED URL: Opens /verify/<batch_number>
  window.open(`/verify/${encodeURIComponent(batchNumber)}`, "_blank");
}

// =========================
// Report counterfeit
// =========================
function reportCounterfeit() {
  const drug = document.getElementById("report-drug").value.trim();
  const batch = document.getElementById("report-batch").value.trim();
  const location = document.getElementById("report-location").value.trim();
  const note = document.getElementById("report-note").value.trim();
  const image = document.getElementById("report-image").files[0];

  if (!batch) {
    showMessage("Batch number is required to report.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("drug_name", drug);
  formData.append("batch_number", batch);
  formData.append("location", location);
  formData.append("note", note);
  if (image) {
    formData.append("image", image);
  }

  fetch("/api/report", {
    method: "POST",
    body: formData, // No Content-Type header needed, browser sets it
  })
    .then((res) => res.json())
    .then((data) => {
      showMessage(data.message || "Report submitted successfully", "success");
    })
    .catch((err) => {
      console.error(err);
      showMessage("Error submitting report", "error");
    });
}

// =========================
// Utility: show message
// =========================
function showMessage(msg, type) {
  const resultContainer = document.getElementById("result");
  if (!resultContainer) return;
  let colorClass = "";
  if (type === "success") colorClass = "result-valid";
  if (type === "error") colorClass = "result-counterfeit";

  resultContainer.innerHTML = `
    <div class="result-box ${colorClass}">
      <div class="msg">${msg}</div>
    </div>
  `;
}

// =========================
// Event listeners
// =========================
document.addEventListener("DOMContentLoaded", () => {
  // Start/Stop scanner
  const startBtn = document.getElementById("start-scan");
  const stopBtn = document.getElementById("stop-scan");
  if (startBtn) startBtn.addEventListener("click", startScanner);
  if (stopBtn) stopBtn.addEventListener("click", stopScanner);

  // Manual verify — CORRECTED to handle form submission
  const verifyForm = document.getElementById("verify-form");
  if (verifyForm) {
    verifyForm.addEventListener("submit", (event) => {
      event.preventDefault(); // Stop the form from submitting the old way
      const batchInput = document.getElementById("verify-batch");
      if (batchInput && batchInput.value) {
        openVerificationPage(batchInput.value.trim());
      } else {
        alert("Please enter a batch number.");
      }
    });
  }

  // Report counterfeit
  const reportBtn = document.getElementById("report-btn");
  if (reportBtn) {
    reportBtn.addEventListener("click", reportCounterfeit);
  }
});

// =========================
// AI Chatbot UI Logic
// =========================
document.addEventListener("DOMContentLoaded", () => {
  const chatToggleBtn = document.getElementById("chat-toggle-btn");
  const chatContainer = document.getElementById("chat-container");
  const chatCloseBtn = document.getElementById("chat-close-btn");
  const chatSendBtn = document.getElementById("chat-send-btn");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");

  // Function to show/hide the chat window
  const toggleChat = () => {
    chatContainer.classList.toggle("hidden");
  };

  // Function to add a message to the chat window
  const addMessage = (text, sender) => {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message", sender);
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  };

  // Function to handle sending a message
  const sendMessage = () => {
    const userText = chatInput.value.trim();
    if (userText === "") return;

    addMessage(userText, "user");
    chatInput.value = "";

    // Send user's message to the new AI backend
    fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userText }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Add the AI's response to the chat window
        addMessage(data.answer, "bot");
      })
      .catch((error) => {
        console.error("Error with AI chat:", error);
        addMessage(
          "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later.",
          "bot"
        );
      });
  };

  // Event listeners
  if (chatToggleBtn) chatToggleBtn.addEventListener("click", toggleChat);
  if (chatCloseBtn) chatCloseBtn.addEventListener("click", toggleChat);
  if (chatSendBtn) chatSendBtn.addEventListener("click", sendMessage);
  if (chatInput)
    chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendMessage();
    });
});
