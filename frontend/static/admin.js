document.addEventListener("DOMContentLoaded", () => {
  // =========================
  // Drug Registration + QR
  // =========================
  const registerBtn = document.getElementById("register-btn");
  const qrResult = document.getElementById("qr-result");
  const qrImage = document.getElementById("qr-image");

  if (registerBtn) {
    registerBtn.addEventListener("click", () => {
      const name = document.getElementById("drug-name").value.trim();
      const batch = document.getElementById("batch-number").value.trim();
      const mfg = document.getElementById("mfg-date").value.trim();
      const expiry = document.getElementById("expiry-date").value.trim();
      const manufacturer = document.getElementById("manufacturer").value.trim();

      if (!name || !batch || !mfg || !expiry || !manufacturer) {
        alert("Please fill in all fields.");
        return;
      }

      qrImage.src = "";
      qrResult.style.display = "none";

      fetch("/api/admin/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          batch_number: batch,
          mfg_date: mfg,
          expiry_date: expiry,
          manufacturer
        })
      })
        .then(res => {
          const contentType = res.headers.get("content-type") || "";
          if (!res.ok) {
            if (contentType.includes("application/json")) {
              return res.json().then(err => {
                throw new Error(err.error || "Unknown error");
              });
            }
            return res.text().then(text => {
              throw new Error("Server error: " + text.slice(0, 100));
            });
          }
          if (contentType.includes("image/png")) {
            return res.blob();
          } else {
            throw new Error("Unexpected response type: " + contentType);
          }
        })
        .then(blob => {
          const url = URL.createObjectURL(blob);
          qrImage.src = url;
          qrResult.style.display = "block";
        })
        .catch(err => {
          console.error(err);
          alert(`Error registering batch: ${err.message}`);
        });
    });
  }

  // =========================
  // Counterfeit Reports Click-to-Check
  // =========================
  document.querySelectorAll(".report-row").forEach(row => {
    row.addEventListener("click", () => {
      const reportId = row.dataset.id;
      fetch(`/admin/reports/mark_checked/${reportId}`, {
        method: "POST"
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            row.classList.remove("new");
            const badge = row.querySelector(".badge");
            if (badge) {
              badge.textContent = "Checked";
              badge.classList.remove("badge-warning");
              badge.classList.add("badge-success");
            }
          }
        })
        .catch(err => {
          console.error("Failed to mark report as checked:", err);
        });
    });
  });
});
