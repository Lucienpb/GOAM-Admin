# GOAM Admin Dashboard

Admin dashboard for GOAM (Golf Once A Month) with two main features:

## Features

### 1. ⛳ Pairing Matrix & Fourball Generator
- Upload golf pairings and build a pairing matrix
- Track player history with visual heatmap
- Player pairing lookup
- Automatic fourball generation with conflict detection
- Team balancing across fourballs

### 2. 🏌️ Handicap Scraper & Calculator
- Login to Handicaps.co.za (requires credentials)
- Single player handicap lookup
- Batch processing for multiple players
- Course handicap calculator
- CAP (Calculated Allowance Parameter) application

## Project Structure

```
goam-admin/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── apps/
│   ├── __init__.py
│   ├── pairing_app.py    # Pairing Matrix & Fourball UI
│   └── handicap_app.py   # Handicap Scraper & Calculator UI
├── utils/
│   ├── __init__.py
│   ├── pairing_matrix.py        # Pairing matrix logic
│   ├── handicap_scraper.py      # Playwright scraping
│   ├── handicap_calculator.py   # Handicap calculations
│   └── fourball_generator.py    # Fourball generation logic
└── data/
    └── (data files go here)
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download Playwright browsers:
   ```bash
   python -m playwright install
   ```

## Usage

Run the application:
```bash
streamlit run app.py
```

Then navigate to `http://localhost:8501` in your browser.

### Login (for Handicap Scraper)
You'll need a membership number and password for Handicaps.co.za

### Upload Files
- **Pairings CSV**: Format should have month headers and player names
- **Player List CSV**: Must contain "Name" and "Team" columns
- **Course Information XLSX**: Excel file with course and tee information

## Features

- Responsive sidebar for login and configuration
- Session state management for data persistence
- Caching for handicap scrapes to avoid repeated requests
- Strict mode for fourball generation (prevents 1-2 person groups)
- WhatsApp-ready output format
- Download matrix as CSV or results as Excel

## License

Private project
