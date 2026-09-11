# TourPlan Provider Onboarding Web Portal

A lightweight, production-ready web application designed for external tourism providers to submit their data for onboarding into **TourPlan**.

## Key Features
- **Bilingual Interface**: Separate, dedicated pages for **English** (`/` or `/index.html`) and **Spanish** (`/es.html`).
- **TourPlan Fidelity**: Captures all 32 parameters across the 7 creditor screens with mandatory indicators matching TourPlan requirements.
- **Smart Form Automation**:
  - `📋 Copy From Invoicing Address` and `📋 Copy From Physical Address` buttons.
  - Virtual Credit Card (VCC) conditional parameters toggle.
- **Zero-Dependency Backend**: Built entirely with Python's standard library (`http.server` + `sqlite3` + `json` + `csv` + `smtplib`).
- **Database Persistence**: Automatic SQLite storage (`submissions.db`) with configurable path (`DB_PATH`).
- **Email Notifications**: Asynchronous email alerts sent to the operations team upon each new provider registration.
- **Password-Protected Backoffice**:
  - Live backoffice dashboard at `/admin.html` secured with HTTP Basic Authentication.
  - One-click CSV export at `/api/export/csv` (Excel-compatible with UTF-8 BOM).

---

## Quick Start (Local)

### 1. Launch the Server
```bash
python3 server.py
```

By default, the server runs on port **`8080`** (or configurable via `PORT=8000 python3 server.py`).

### 2. Available Routes

| Route / URL | Role | Description |
|---|---|---|
| `http://localhost:8080/` | English | Main English provider onboarding form |
| `http://localhost:8080/es.html` | Español | Formulario oficial de registro en español |
| `http://localhost:8080/admin.html` | Internal | Password-protected dashboard for incoming submissions |
| `http://localhost:8080/api/submit` | REST API | `POST` endpoint receiving and validating JSON submissions |
| `http://localhost:8080/api/submissions` | REST API | `GET` endpoint returning JSON array of all registrations |
| `http://localhost:8080/api/export/csv` | Export | `GET` endpoint downloading all records as `.csv` for Excel/TourPlan |

---

## Deploying to Render (Option B)

### Step 1: Create a Web Service on Render
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your GitHub repository: `msendracr87/samaraexplorers`.
4. Configure service settings:
   - **Name**: `samaraexplorers-onboarding`
   - **Runtime**: `Python 3`
   - **Build Command**: *(leave empty)*
   - **Start Command**: `python3 server.py`
   - **Plan**: Free

### Step 2: Environment Variables
Add the following in the **Environment** tab on Render:

| Variable | Description | Example / Default |
|---|---|---|
| `ADMIN_PASSWORD` | Password for `/admin.html` and export | `YourSecretPassword123` |
| `ADMIN_USER` | Admin username | `admin` (default) |
| `ADMIN_URL` | Live URL linked in email alerts | `https://samaraexplorers.onrender.com/admin.html` |
| `SMTP_HOST` | *(Optional)* SMTP mail server host | `smtp.gmail.com` or `smtp.sendgrid.net` |
| `SMTP_PORT` | *(Optional)* SMTP port | `587` |
| `SMTP_USER` | *(Optional)* SMTP account email/username | `notifications@samaraexplorers.com` |
| `SMTP_PASSWORD` | *(Optional)* SMTP app password | `xxxx-xxxx-xxxx-xxxx` |
| `NOTIFICATION_TO`| *(Optional)* Email address receiving alerts | `info@samaraexplorers.com` |
| `DB_PATH` | *(Optional)* Custom database path | `/data/submissions.db` (if using disk) |

> [!NOTE]
> **Data Persistence across Free-tier sleep/rebuilds**: 
> On Render's Free tier, container restarts reset local storage unless a **Persistent Disk** (Starter tier) is attached and `DB_PATH` is set to `/data/submissions.db`. Alternatively, export the CSV periodically or view submissions instantly upon receipt.

---

## Directory Structure
```
samaraexplorers/
├── server.py              # Zero-dependency Python server & SQLite backend
├── submissions.db         # SQLite database (auto-generated, gitignored)
├── render.yaml            # Render Blueprint deployment definition
├── README.md              # Documentation & deployment guide
└── public/
    ├── index.html         # English onboarding form
    ├── es.html            # Spanish onboarding form
    ├── admin.html         # Backoffice review dashboard (password-protected)
    ├── css/
    │   └── style.css      # Modern responsive styling
    └── js/
        └── form.js        # Client validation, address copy, and AJAX submission
```
