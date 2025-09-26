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
// QR & Barcode Scanner
// =========================
let html5QrCode;
const qrRegionId = "qr-reader";

// NEW: Define all the code formats we want to support
const supportedFormats = [
  Html5QrcodeSupportedFormats.QR_CODE,
  Html5QrcodeSupportedFormats.UPC_A,
  Html5QrcodeSupportedFormats.UPC_E,
  Html5QrcodeSupportedFormats.EAN_13,
  Html5QrcodeSupportedFormats.EAN_8,
];

function startScanner() {
  if (!html5QrCode) {
    // MODIFIED: Pass a config object to enable verbose logging for debugging
    html5QrCode = new Html5Qrcode(qrRegionId, { verbose: false });
  }

  // MODIFIED: Update the scanner configuration
  const scannerConfig = {
    fps: 10,
    qrbox: { width: 250, height: 150 }, // Rectangular box is better for barcodes
    // Tell the scanner to only look for the formats we've defined
    formatsToSupport: supportedFormats,
  };

  html5QrCode
    .start(
      { facingMode: "environment" },
      scannerConfig,
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
  if (html5QrCode && html5QrCode.isScanning) {
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
    showMessage("Batch number is required to report.", "error");
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
      showMessage(data.message || "Report submitted successfully", "success");
    })
    .catch((err) => {
      console.error(err);
      showMessage("Error submitting report", "error");
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
  if (startBtn) startBtn.addEventListener("click", startScanner);
  if (stopBtn) stopBtn.addEventListener("click", stopScanner);

  const verifyForm = document.getElementById("verify-form");
  if (verifyForm) {
    verifyForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const batchInput = document.getElementById("verify-batch");
      if (batchInput && batchInput.value) {
        openVerificationPage(batchInput.value.trim());
      } else {
        alert("Please enter a batch number.");
      }
    });
  }

  const reportBtn = document.getElementById("report-btn");
  if (reportBtn) {
    reportBtn.addEventListener("click", reportCounterfeit);
  }
});
