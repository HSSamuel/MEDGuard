# 🛡️ MedGuard – Counterfeit Drug Reporting & Verification System

**MedGuard** is a full-stack web application designed to detect, report, and manage counterfeit drugs in Nigeria.  
It provides a comprehensive public health platform with a user-friendly interface for citizens and a powerful admin dashboard for regulators to ensure a resilient and transparent pharmaceutical supply chain.

## ✨ Key Features

### Multi-Platform Verification

- 📷 **QR Code / Barcode Scanning** – Use your device's camera for real-time validation.
- 🔢 **Batch Number Lookup** – Manually enter a batch number for verification.
- 📱 **Offline SMS Verification** – Works without internet, ensuring accessibility for all citizens.

### Citizen Reporting

- 🚨 **Counterfeit Reporting** – Anonymously submit reports of suspicious drugs with geo-location, notes, and image uploads.
- 💊 **Adverse Drug Reaction (ADR) Reporting** – Users can report side effects of legitimate medications, contributing to national pharmacovigilance.

### Regulator Admin Dashboard

- 📊 **Centralized Report Management** – View, filter, and manage all counterfeit and ADR reports in one place.
- 🗺️ **Live Hotspot Map** – Visualize the geographic distribution of counterfeit reports to identify clusters and target investigations.
- 📦 **Drug Batch Registration** – Securely register new drug batches and instantly generate verifiable QR codes.
- 📤 **Data Exporting** – Export filtered reports to Word and PDF for documentation and analysis.

### AI & Intelligence

- 🤖 **AI Assistant** – An integrated chatbot to guide users on how to verify drugs and report counterfeits.
- 🔮 **Predictive Hotspot Analysis** – A (simulated) machine learning model to predict future counterfeit hotspots based on existing data.

### Multi-Language Support

- 🌍 Full internationalization for **English, Hausa, Igbo, and Yoruba**.

---

## 🏗️ Tech Stack

- **Backend:** Python with Flask
- **Frontend:** HTML, CSS, and Vanilla JavaScript
- **Database:** SQLite3
- **Real-time Communication:** Flask-SocketIO (live admin notifications)
- **Internationalization:** Flask-Babel (multi-language support)
- **SMS Integration:** Twilio (offline verification)
- **Deployment:** Gunicorn + Eventlet

---

## 🗄️ Database Schema

| Table         | Description                                                                 |
| ------------- | --------------------------------------------------------------------------- |
| `drugs`       | Stores all registered drug batches, including name, manufacturer, expiry.   |
| `users`       | Manages public user accounts for personalized features like report history. |
| `admin_users` | Securely stores regulator accounts with role-based access control.          |
| `reports`     | Contains all counterfeit drug reports (geo-location, images, metadata).     |
| `adr_reports` | Stores reports of adverse drug reactions for pharmacovigilance.             |
| `scan_logs`   | Records every scan attempt to detect anomalies or potential code cloning.   |

---

## ⚙️ Installation & Setup

### Clone the Repository

````bash
git clone https://github.com/hssamuel/medguard.git
cd medguard


2. **Create a virtual environment & install dependencies**

   ```bash
  python -m venv venv
# On Windows
venv\Scripts\activate
pip install -r requirements.txt

3. **Initialize the database**

   ```bash
   python -m backend.database
````

4. **Run the Flask app**

   ```bash
   python run.py
   ```

5. **Access the App**

User Interface: http://127.0.0.1:5000/
Admin Dashboard: http://127.0.0.1:5000/admin
Default Login: admin@nafdac.gov.ng / StrongPass123

---

## 🚀 Future Enhancements

- **Live Blockchain Integration** – Immutable, transparent ledger for drug supply chain.
- **Advanced AI/ML Model** – Production-grade prediction of counterfeit hotspots.
- **EMDEX API Integration** – Automatic access to over 15,000 NAFDAC-registered drugs.
- **Cloud Database Migration** – Transition from SQLite to PostgreSQL/MySQL for scalability.

## 🎨 UI & Design

- **Primary Accents**: Soft Teal `#00B8A9`, Muted Cyan `#4ECDC4`, Medical Green `#1ABC9C`
- **Warnings**: Warm Amber `#F39C12`, Coral Orange `#E67E22`
- **Buttons**: Dark Teal `#008080`, Navy Blue `#2C3E50`, Soft Emerald `#2ECC71`
- **Backgrounds**: Light Grey-Blue `#ECF0F1`, Pale Aqua `#E8F8F5`

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a pull request with detailed notes.

## 🧑‍💻 Author

This project was collaboratively developed by **Victor, Samuel, and Desmond** as a solution to protect communities from counterfeit drugs and safeguard public health in Nigeria.
