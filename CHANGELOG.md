# Changelog
All notable changes to **GOAM Admin** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to **Semantic Versioning**.

---

## [1.3.0] - 2026-05-16
### Added
- Full GOAM UI theme (deep blue sidebar, modern buttons, metric cards).
- Sidebar logo support (`assets/goam_logo.png`).
- README banner with centered logo and badges.
- CHANGELOG.md for version tracking.

### Changed
- Moved `st.set_page_config()` to the top of `app.py` (required by Streamlit).
- Improved theme injection placement for consistent rendering.

---

## [1.2.0] - 2026-05-15
### Added
- Complete admin user management page:
  - Create users
  - Edit roles
  - Verify accounts
  - Reset passwords
  - Delete users
- Updated profile page with:
  - Editable name & phone
  - Secure password change
  - Updated timestamps

### Changed
- Unified authentication system across all pages.
- Cleaned up session state handling.

---

## [1.1.0] - 2026-05-14
### Added
- Login throttling and lockout system.
- Email verification token flow.
- Password reset token flow.
- Session timeout (30 minutes).
- JSON user store (`auth/users.json`).

### Changed
- Rewrote login page to use new auth utilities.
- Improved error handling and messaging.

---

## [1.0.0] - 2026-05-10
### Added
- Initial GOAM Admin application structure.
- Pairing Matrix tool.
- Handicap Scraper tool.
- Scores & Rounds viewer.
- Basic navigation and session handling.

---

## [Unreleased]
### Planned
- Dark mode toggle.
- Exportable pairing matrix PDF.
- Player statistics dashboard.
- Automated backups for `users.json`.
