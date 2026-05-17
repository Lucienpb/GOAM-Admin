<p align="center">
  <img src="assets/goam_logo.png" alt="GOAM Logo" width="180">
</p>

<h1 align="center">⛳ GOAM Admin</h1>

<p align="center">
  A modern, secure administration system for GOAM golf events, handicaps, pairings, and player data.
</p>

<p align="center">
  <strong>Built with Streamlit • Secure Auth • Modern UI • Golf Tools</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Streamlit-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge">
  <img src="https://img.shields.io/badge/Made%20for-GOAM-gold?style=for-the-badge">
</p>

---

# 🏆 GOAM Admin System (2026 Edition)

A complete administration, scoring, pairing, and handicap‑scraping platform for the GOAM golf league.

---

## 📌 Overview

GOAM‑Admin is a full Streamlit‑based management system that handles:

- User authentication (with admin roles, verification, password resets)
- Data management (Excel → JSON ingestion)
- Fourball generation & pairing matrix
- Handicap scraping (Playwright automation)
- GOAM scoring engine (IPS, Strokes, LIV)
- Season dashboards & leaderboards
- Exportable GOAM workbooks

The system is modular, fast, and designed for monthly league operations.

---

# 📁 Project Structure

```
GOAM-Admin/
│
├── app.py
│
├── auth/
│   ├── auth.py
│   ├── login_page.py
│   ├── profile_page.py
│   └── admin_page.py
│
├── admin/
│   └── data_manager_page.py
│
├── apps/
│   ├── pairing_app.py
│   ├── handicap_app.py
│   ├── scores_app.py
│   └── goam_dashboard.py
│
├── backend/
│   ├── goam_loader.py
│   ├── goam_rounds.py
│   └── goam_calculator.py
│
├── utils/
│   ├── json_utils.py
│   ├── fourball_generator.py
│   ├── handicap_calculator.py
│   └── handicap_scraper.py
│
└── data/
    ├── course_data.json
    ├── players.json
    ├── pairings.json
    └── goam_scores.json
```

---

# 📊 Architecture Diagram

```
                ┌──────────────────────────┐
                │         app.py           │
                │  (Routing + Session)     │
                └────────────┬─────────────┘
                             │
     ┌───────────────────────┼────────────────────────┐
     │                       │                        │
┌────▼────┐            ┌─────▼─────┐           ┌─────▼─────┐
│  auth   │            │   apps     │           │   admin    │
│ system  │            │ (user apps)│           │ DataManager│
└────┬────┘            └─────┬─────┘           └─────┬─────┘
     │                        │                        │
┌────▼────┐        ┌─────────▼─────────┐      ┌───────▼────────┐
│ users   │        │ pairing_app        │      │ Excel → JSON    │
│ JSON    │        │ handicap_app       │      │ converters       │
└─────────┘        │ scores_app         │      └──────────────────┘
                   │ goam_dashboard     │
                   └─────────┬─────────┘
                             │
                     ┌───────▼────────┐
                     │   backend/      │
                     │ calculators     │
                     └───────┬────────┘
                             │
                     ┌───────▼────────┐
                     │     data/       │
                     │  JSON storage   │
                     └─────────────────┘
```

---

# 🧮 Total Lines of Code (Updated)

| Module | Lines |
|--------|-------|
| **app.py** | **256** |
| **auth/auth.py** | **372** |
| **auth/login_page.py** | **158** |
| **auth/profile_page.py** | **107** |
| **auth/admin_page.py** | 196 |
| **admin/data_manager_page.py** | 330 |
| **apps/pairing_app.py** | 240 |
| **apps/handicap_app.py** | 210 |
| **apps/scores_app.py** | 260 |
| **apps/goam_dashboard.py** | 120 |
| **backend/goam_loader.py** | 40 |
| **backend/goam_rounds.py** | 110 |
| **backend/goam_calculator.py** | 430 |
| **utils/json_utils.py** | 20 |
| **utils/fourball_generator.py** | 140 |
| **utils/handicap_calculator.py** | 120 |
| **utils/handicap_scraper.py** | 160 |

### ✅ **Total Lines of Code: 3,009**

A full production‑scale system.

---

# ⚙️ Features

### 🔐 Authentication
- Password hashing  
- Email verification  
- Admin role management  
- Lockout protection  
- Profile editing  

### 📂 Data Manager (Admin Only)
- Upload Excel → JSON:
  - Course data  
  - Players  
  - Pairings  
  - GOAM scores (with derived fields)

### ⛳ Pairing Engine
- Pairing matrix from historical JSON  
- Heatmap  
- Player lookup  
- Fourball generator with:
  - Team balancing  
  - Conflict avoidance  
  - Strict mode  
  - WhatsApp output  

### 📘 GOAM Scores Engine
- IPS best 6  
- Strokes best 6  
- LIV scoring  
- Trend index  
- Strength index  
- Course‑split tables  
- Export updated workbook  

### 📈 Dashboard
- Season IPS leaderboard  
- Gross/Nett averages  
- OX Nau leaderboard  
- LIV standings  
- Player IPS trend  
- Monthly results browser  

### 🏌 Handicap Scraper
- Playwright automation  
- Single lookup  
- Batch processing  
- Course handicap calculator  

---

# 🚀 Installation

### 1. Clone the repo
```
git clone https://github.com/Lucienpb/GOAM-Admin.git
cd GOAM-Admin
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Run Streamlit
```
streamlit run app.py
```

---

# 🔧 Configuration

### JSON storage lives in:
```
data/
```

### Playwright setup:
```
playwright install
```

---

# 🧪 Testing

Recommended:
- pytest  
- mock Playwright scraper  
- snapshot tests for leaderboards  

---

# 📜 License

Private project — all rights reserved.


