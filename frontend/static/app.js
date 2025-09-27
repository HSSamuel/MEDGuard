// =========================
// Rotating tagline
// =========================
const taglines = window.translations.taglines || [
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
// QR & Barcode Scanner
// =========================
let html5QrCode;
const qrRegionId = "qr-reader";

const supportedFormats = [
  Html5QrcodeSupportedFormats.QR_CODE,
  Html5QrcodeSupportedFormats.UPC_A,
  Html5QrcodeSupportedFormats.UPC_E,
  Html5QrcodeSupportedFormats.EAN_13,
  Html5QrcodeSupportedFormats.EAN_8,
];

// Function to manage button enabled/disabled states
function updateButtonStates(isScanning) {
  const startBtn = document.getElementById("start-scan");
  const stopBtn = document.getElementById("stop-scan");
  const scanFromFileBtn = document.getElementById("scan-from-file-btn");

  if (startBtn) startBtn.disabled = isScanning;
  if (scanFromFileBtn) scanFromFileBtn.disabled = isScanning;
  if (stopBtn) stopBtn.disabled = !isScanning;
}

function startScanner() {
  if (!html5QrCode) {
    html5QrCode = new Html5Qrcode(qrRegionId, { verbose: false });
  }

  updateButtonStates(true);

  const scannerConfig = {
    fps: 10,
    qrbox: { width: 300, height: 200 },
    formatsToSupport: supportedFormats,
  };

  html5QrCode
    .start(
      { facingMode: "environment" },
      scannerConfig,
      (decodedText) => {
        // --- VISUAL FEEDBACK LOGIC START ---
        const qrReaderElement = document.getElementById(qrRegionId);
        if (qrReaderElement) {
          qrReaderElement.classList.add("scan-success");
          setTimeout(() => {
            qrReaderElement.classList.remove("scan-success");
          }, 700); // Remove class after 0.7s animation
        }
        // --- VISUAL FEEDBACK LOGIC END ---

        stopScanner();

        // Open the page after a brief delay to allow the user to see the flash
        setTimeout(() => {
          openVerificationPage(decodedText);
        }, 200);
      },
      () => {} // ignore scan errors
    )
    .catch((err) => {
      console.error("Unable to start scanning:", err);
      showMessage(
        window.translations.cameraAccessFailed ||
          "Camera access failed. Please check permissions.",
        "error"
      );
      updateButtonStates(false);
    });
}

function stopScanner() {
  if (html5QrCode && html5QrCode.isScanning) {
    html5QrCode.stop().catch((err) => console.error("Stop failed:", err));
  }
  updateButtonStates(false);
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) {
    return;
  }
  if (!html5QrCode) {
    html5QrCode = new Html5Qrcode(qrRegionId, { verbose: false });
  }

  html5QrCode
    .scanFile(file, true)
    .then((decodedText) => {
      openVerificationPage(decodedText);
    })
    .catch((err) => {
      showMessage(`Error scanning file: ${err}`, "error");
    });
}

// =========================
// Open verification page in new tab
// =========================
function openVerificationPage(batchNumber) {
  if (!batchNumber) {
    showMessage(
      window.translations.enterBatchNumber || "Please enter a batch number.",
      "error"
    );
    return;
  }
  window.open(`/verify/${encodeURIComponent(batchNumber)}`, "_blank");
}

// =========================
// Report counterfeit with Geolocation
// =========================
function reportCounterfeit() {
  const reportBtn = document.getElementById("report-btn");
  const drug = document.getElementById("report-drug").value.trim();
  const batch = document.getElementById("report-batch").value.trim();
  const location = document.getElementById("report-location").value.trim();
  const note = document.getElementById("report-note").value.trim();
  const image = document.getElementById("report-image").files[0];

  if (!batch) {
    showMessage(
      window.translations.batchRequired ||
        "Batch number is required to report.",
      "error"
    );
    return;
  }

  reportBtn.textContent = "Getting location...";
  reportBtn.disabled = true;

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        sendReportData(drug, batch, location, note, image, lat, lon);
      },
      () => {
        alert("Could not get location. Submitting report without it.");
        sendReportData(drug, batch, location, note, image, null, null);
      }
    );
  } else {
    alert(
      "Geolocation is not supported by your browser. Submitting report without it."
    );
    sendReportData(drug, batch, location, note, image, null, null);
  }
}

function sendReportData(
  drug,
  batch,
  location,
  note,
  image,
  latitude,
  longitude
) {
  const reportBtn = document.getElementById("report-btn");
  const formData = new FormData();
  formData.append("drug_name", drug);
  formData.append("batch_number", batch);
  formData.append("location", location);
  formData.append("note", note);
  if (image) {
    formData.append("image", image);
  }
  if (latitude && longitude) {
    formData.append("latitude", latitude);
    formData.append("longitude", longitude);
  }

  reportBtn.textContent = "Submitting...";

  fetch("/api/report", {
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      showMessage(
        data.message ||
          window.translations.reportSuccess ||
          "Report submitted successfully",
        "success"
      );
    })
    .catch((err) => {
      console.error(err);
      showMessage(
        window.translations.errorSubmitting || "Error submitting report",
        "error"
      );
    })
    .finally(() => {
      reportBtn.textContent = "Report";
      reportBtn.disabled = false;
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
  const startBtn = document.getElementById("start-scan");
  const stopBtn = document.getElementById("stop-scan");
  const scanFromFileBtn = document.getElementById("scan-from-file-btn");
  const fileInput = document.getElementById("qr-input-file");

  if (startBtn) startBtn.addEventListener("click", () => startScanner());
  if (stopBtn) stopBtn.addEventListener("click", stopScanner);
  if (scanFromFileBtn)
    scanFromFileBtn.addEventListener("click", () => fileInput.click());
  if (fileInput) fileInput.addEventListener("change", handleFileSelect);

  const verifyForm = document.getElementById("verify-form");
  if (verifyForm) {
    verifyForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const batchInput = document.getElementById("verify-batch");
      if (batchInput && batchInput.value) {
        openVerificationPage(batchInput.value.trim());
      } else {
        alert(
          window.translations.enterBatchNumber || "Please enter a batch number."
        );
      }
    });
  }

  const reportBtn = document.getElementById("report-btn");
  if (reportBtn) {
    reportBtn.addEventListener("click", reportCounterfeit);
  }

  // Set initial button states on page load
  updateButtonStates(false);
});
