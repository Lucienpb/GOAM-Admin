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

# ⛳ GOAM Admin  
A modern, secure, Streamlit-based administration system for managing GOAM golf events, handicaps, pairings, and player data.

GOAM Admin provides a unified dashboard for:
- Pairing Matrix generation  
- Handicap scraping & course data  
- Scores & rounds management  
- User authentication & roles  
- Admin user management  
- Profile management  
- Secure session handling  
- Email verification & password reset  

---

## 🚀 Features

### 🔐 Authentication System
- Email + password login  
- Secure SHA256 password hashing  
- Email verification tokens  
- Password reset tokens  
- Session timeout (30 minutes)  
- Role-based access (`admin` / `user`)  
- JSON-based user store (`auth/users.json`)

### 🛠 Admin Tools
- Create users  
- Edit roles  
- Verify accounts  
- Reset passwords  
- Delete users  
- View all users  

### ⛳ Golf Tools
#### **Pairing Matrix**
- Generate 4-ball pairings  
- Supports GOAM formats  
- Clean UI with exportable results  

#### **Handicap Scraper**
- Login to HNA  
- Scrape player handicaps  
- Load course data  
- Calculate CH / PH  
- Batch processing  

#### **Scores & Rounds**
- View player rounds  
- Score summaries  
- Handicap trends  

---

## 📁 Project Structure

GOAM-Admin/
│
├── app.py                     # Main application
│
├── auth/
│   ├── auth_utils.py          # Authentication backend
│   ├── login_page.py          # Login UI
│   ├── profile_page.py        # Profile UI
│   ├── admin_page.py          # Admin UI
│   └── users.json             # User database
│
├── apps/
│   ├── pairing_app.py         # Pairing Matrix
│   ├── handicap_app.py        # Handicap Scraper
│   └── scores_app.py          # Scores & Rounds
│
├── utils/
│   ├── handicap_calculator.py # Course & CH/PH logic
│   └── handicap_scraper.py    # HNA scraping
│
├── assets/
│   └── goam_logo.png          # Sidebar logo
│
└── README.md

---

## 🎨 UI Theme

GOAM Admin includes a custom theme:
- Deep blue sidebar  
- Clean white cards  
- Modern typography  
- Styled buttons  
- Consistent spacing  
- Sidebar logo support  

Theme is injected via `inject_theme()` in `app.py`.

---

## 🔧 Installation

### 1. Clone the repo
```bash
git clone https://github.com/Lucienpb/GOAM-Admin.git
cd GOAM-Admin
