# TourPlan Provider Onboarding Web Portal

A lightweight, production-ready web application designed for external tourism providers to submit their data for onboarding into **TourPlan**.

## Key Features
- **Bilingual Interface**: Separate, dedicated pages for **English** (`/` or `/index.html`) and **Spanish** (`/es.html`).
- **TourPlan Fidelity**: Captures all 32 parameters across the 7 creditor screens with mandatory indicators (red border + alert color) matching TourPlan requirements.
- **Smart Form Automation**:
  - `📋 Copy From Invoicing Address` and `📋 Copy From Physical Address` buttons.
  - Virtual Credit Card (VCC) conditional parameters toggle.
- **Zero-Dependency Backend**: Built entirely with Python's standard library (`http.server` + `sqlite3` + `json` + `csv`).
- **Database Persistence**: Automatic SQLite storage (`submissions.db`) with full transactional integrity.
- **Backoffice Admin & Export**:
  - Live backoffice dashboard at `/admin.html`.
  - One-click CSV export at `/api/export/csv` (Excel-compatible with UTF-8 BOM).

---

## Quick Start

### 1. Launch the Server
From the root of the project:
```bash
python3 DataEntry/Creditors-Data-Entry/webform/server.py
```
Or navigate to the directory:
```bash
cd DataEntry/Creditors-Data-Entry/webform
python3 server.py
```

By default, the server runs on port **`8080`** (or configurable via `PORT=8000 python3 server.py`).

### 2. Available Routes

| Route / URL | Language / Role | Description |
|---|---|---|
| `http://localhost:8080/` | English | Main English provider onboarding form |
| `http://localhost:8080/es.html` | Español | Formulario oficial de registro en español |
| `http://localhost:8080/admin.html` | Internal | Backoffice dashboard to view all received provider submissions |
| `http://localhost:8080/api/submit` | REST API | `POST` endpoint receiving and validating JSON submissions |
| `http://localhost:8080/api/submissions` | REST API | `GET` endpoint returning JSON array of all registrations |
| `http://localhost:8080/api/export/csv` | Export | `GET` endpoint downloading all records as `.csv` for Excel/TourPlan |

---

## Directory Structure
```
webform/
├── server.py              # Zero-dependency Python server & SQLite backend
├── submissions.db         # SQLite database (created automatically on first launch)
├── README.md              # This documentation
└── public/
    ├── index.html         # English onboarding form
    ├── es.html            # Spanish onboarding form
    ├── admin.html         # Backoffice review dashboard
    ├── css/
    │   └── style.css      # Modern responsive styling
    └── js/
        └── form.js        # Client validation, address copy, and AJAX submission
```
