---
# 🛡️ MedGuard – Counterfeit Drug Reporting & Verification System

MedGuard is a full‑stack web application designed to **detect, report, and manage counterfeit drugs**.
It provides a **user interface** for scanning and reporting, and an **admin dashboard** for reviewing, filtering, and verifying reports.
---

## ✨ Features

- **QR Code Verification** – Scan and validate drug packaging.
- **Counterfeit Reporting** – Submit reports with drug name, batch number, location, and notes.
- **Admin Dashboard** – View all reports, filter by date, and mark reports as checked.
- **Real-Time Notifications** – Blinking badge for new reports.
- **Status Tracking** – Reports flagged as `New` (amber) or `Checked` (green).
- **Session Management** – Auto timeout with warning modal.
- **Modern UI** – Clean, medical‑grade color palette (teal, emerald, amber).

---

## 🏗️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with medical‑friendly palette
- **QR Utilities**: Python QR code generation & verification

---

## 📂 Project Structure

### Root

```
MEDGUARD/
│
├── backend/               # Flask backend
├── frontend/              # Frontend templates & static files
├── .logs/                 # Log files
├── .venv/ / venv/         # Virtual environment
│
├── medguard.db            # SQLite database
├── run.py                 # Entry point for running the app
├── requirements.txt       # Python dependencies
│
├── create_admin_user.py   # Script to seed an admin user
├── create_drugs_table.py  # Script to create drugs table
├── create_reporttable.py  # Script to create reports table
├── migrate_add_mfg_date.py# Migration script
├── migrate_reports_table.py
├── view_admins.py         # Utility to view admin users
└── README.md              # Documentation
```

### Backend

```
backend/
├── app.py                 # Flask app factory
├── config.py              # Config settings
├── database.py            # SQLite connection
├── models.py              # ORM models
├── qr_utils.py            # QR code utilities
├── seed_demo.py           # Demo data seeding
│
└── routes/                # Modular route handlers
    ├── __init__.py
    ├── admin.py           # Admin dashboard routes
    ├── register.py        # User registration
    ├── report.py          # Report endpoints
    ├── verify.py          # Verification endpoints
```

### Frontend

```
frontend/
├── static/
│   ├── images/            # Assets
│   ├── styles.css         # Global styles
│   ├── app.js             # User-side logic
│   ├── admin.js           # Admin dashboard logic
│   └── admin_timer.js     # Session timeout handling
│
├── templates/
│   ├── base.html          # Shared layout
│   ├── index.html         # User scanning/reporting
│   ├── verify.html        # Verification page
│   ├── sms_check.html     # SMS verification
│   ├── admin.html         # Admin dashboard
│   ├── admin_login.html   # Admin login
│   └── admin_drugs.html   # Manage drugs
│
└── app_ui.py              # UI integration with backend
```

---

## 🗄️ Database Schema

**Table: `reports`**

| Column       | Type      | Description                  |
| ------------ | --------- | ---------------------------- |
| id           | INTEGER   | Primary key                  |
| drug_name    | TEXT      | Name of the drug             |
| batch_number | TEXT      | Batch number (required)      |
| location     | TEXT      | Location of report           |
| note         | TEXT      | Additional notes             |
| reported_on  | TIMESTAMP | Auto-set to current datetime |
| status       | INTEGER   | `0 = New`, `1 = Checked`     |

---

## ⚙️ Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/MEDGuard.git
   cd MEDGuard
   ```

2. **Create a virtual environment & install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Initialize the database**

   ```bash
   sqlite3 medguard.db < create_reporttable.py
   python create_admin_user.py
   ```

4. **Run the Flask app**

   ```bash
   python run.py
   ```

5. **Access the app**
   - User interface → `http://localhost:5000/`
   - Admin dashboard → `http://localhost:5000/admin`

---

## 🎨 UI & Design

- **Primary Accents**: Soft Teal `#00B8A9`, Muted Cyan `#4ECDC4`, Medical Green `#1ABC9C`
- **Warnings**: Warm Amber `#F39C12`, Coral Orange `#E67E22`
- **Buttons**: Dark Teal `#008080`, Navy Blue `#2C3E50`, Soft Emerald `#2ECC71`
- **Backgrounds**: Light Grey-Blue `#ECF0F1`, Pale Aqua `#E8F8F5`

Badges:

- 🟠 **New** → Amber (`badge-new`)
- 🟢 **Checked** → Emerald (`badge-checked`)

---

## 🚀 Future Enhancements

- Role-based authentication (Admin vs User).
- Analytics dashboard for counterfeit trends.
- Email/SMS alerts for new reports.
- Multi-language support.
- Cloud database integration (PostgreSQL/MySQL).

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a pull request with detailed notes.

---

## 📜 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## 🧑‍💻 Author

Collaboratively developed by **Victor, Samuel, and Desmond**
Designed to protect communities from counterfeit drugs and safeguard public health.

---
