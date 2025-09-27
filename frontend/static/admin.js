// ===================================
// Assisted Registration Scanner
// ===================================
document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("start-reg-scan-btn");
  const stopBtn = document.getElementById("stop-reg-scan-btn");
  const scannerContainer = document.getElementById(
    "registration-scanner-container"
  );
  const registrationReaderId = "registration-reader";

  let regScanner;

  // --- Toast Notification Function ---
  const showToast = (message) => {
    const toast = document.createElement("div");
    toast.className = "toast-notification";
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("show");
    }, 100);

    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  };

  const onScanSuccess = (decodedText, decodedResult) => {
    console.log(`Scan result: ${decodedText}`);

    startBtn.textContent = "Analyzing...";
    startBtn.disabled = true;

    fetch("/api/parse-qr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: decodedText }),
    })
      .then((response) => response.json())
      .then((details) => {
        if (details.batch_number) {
          document.getElementById("batch-number").value = details.batch_number;
        }
        if (details.manufacturer) {
          document.getElementById("manufacturer").value = details.manufacturer;
        }

        showToast("Registration form has been pre-filled.");

        // --- NEW: Guide the user to the next step ---
        setTimeout(() => {
          const registerBtn = document.querySelector(
            '#register-form button[type="submit"]'
          );
          registerBtn.scrollIntoView({ behavior: "smooth", block: "center" });

          // Highlight the button to draw attention
          registerBtn.style.transition = "all 0.2s ease-in-out";
          registerBtn.style.transform = "scale(1.1)";
          registerBtn.style.boxShadow = "0 0 15px rgba(40, 167, 69, 0.8)";

          setTimeout(() => {
            registerBtn.style.transform = "scale(1.0)";
            registerBtn.style.boxShadow = "none";
          }, 1500); // Revert style after 1.5 seconds
        }, 500); // A brief delay for a smoother feel
      })
      .catch((error) => {
        console.error("Error parsing QR data:", error);
        document.getElementById("batch-number").value = decodedText;
        showToast(`Pre-filled batch number with: ${decodedText}`);
      })
      .finally(() => {
        startBtn.textContent = "📷 Scan to Pre-fill";
        startBtn.disabled = false;
        stopScanner();
      });
  };

  const startScanner = () => {
    scannerContainer.style.display = "block";
    if (!regScanner) {
      regScanner = new Html5Qrcode(registrationReaderId);
    }
    regScanner
      .start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        onScanSuccess,
        (errorMessage) => {
          /* ignore errors */
        }
      )
      .catch((err) => {
        console.error("Unable to start registration scanner", err);
        alert("Could not start camera. Please check permissions.");
      });
  };

  const stopScanner = () => {
    if (regScanner && regScanner.isScanning) {
      regScanner
        .stop()
        .then(() => {
          scannerContainer.style.display = "none";
        })
        .catch((err) => {
          console.error("Failed to stop scanner", err);
        });
    } else {
      scannerContainer.style.display = "none";
    }
  };

  if (startBtn) startBtn.addEventListener("click", startScanner);
  if (stopBtn) stopBtn.addEventListener("click", stopScanner);

  // --- Image Analysis Handler ---
  const handleAnalysisClick = (event) => {
    if (!event.target.classList.contains("analyze-btn")) return;

    const reportId = event.target.dataset.id;
    const container = document.getElementById(`analysis-${reportId}`);
    container.innerHTML = "<p><em>Analyzing...</em></p>";

    fetch(`/api/analyze-image/${reportId}`, {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          container.innerHTML = `<p style="color: red;">${data.error}</p>`;
        } else {
          const confidence = (data.confidence * 100).toFixed(1);
          container.innerHTML = `<p><strong>${data.label}</strong><br><em>(Confidence: ${confidence}%)</em></p>`;
        }
      })
      .catch((error) => {
        console.error("Analysis error:", error);
        container.innerHTML = `<p style="color: red;">Analysis failed.</p>`;
      });
  };

  const reportsTable = document.getElementById("reports-table");
  if (reportsTable) {
    reportsTable.addEventListener("click", handleAnalysisClick);
  }

  // --- Real-Time Report Search ---
  const handleReportSearch = () => {
    const searchInput = document.getElementById("report-search");
    if (!searchInput) return;

    searchInput.addEventListener("keyup", () => {
      const searchTerm = searchInput.value.toLowerCase();
      const tableBody = document.getElementById("reports-body");
      const rows = tableBody.getElementsByTagName("tr");

      for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const rowText = row.textContent.toLowerCase();

        if (rowText.includes(searchTerm)) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      }
    });
  };

  handleReportSearch();
});
