#!/usr/bin/env python3
"""
TourPlan Provider Onboarding - Lightweight Standard Library Web Server & Backend
Features:
- Serves English & Spanish onboarding pages and Admin Dashboard
- Validates and stores submissions in SQLite database (submissions.db)
- Asynchronous email notifications upon provider submission (SMTP)
- HTTP Basic Authentication protection for admin endpoints
- REST API for form submission, submission querying, and CSV/JSON export
- Zero external dependencies (Python 3 standard library only)
"""

import http.server
import socketserver
import json
import sqlite3
import os
import mimetypes
import urllib.parse
import csv
import io
import base64
import threading
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "submissions.db"))

# Admin Authentication credentials
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")  # If set, enforces auth

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS creditor_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        language_page TEXT,
        creditor_code TEXT,
        creditor_name TEXT NOT NULL,
        local_creditor_name TEXT,
        default_currency TEXT NOT NULL,
        physical_name TEXT,
        physical_address TEXT,
        physical_city TEXT,
        physical_country TEXT,
        physical_razon_social TEXT,
        physical_cedula_juridica TEXT,
        physical_post_code TEXT,
        mailing_name TEXT,
        mailing_address TEXT,
        mailing_city TEXT,
        mailing_country TEXT,
        mailing_razon_social TEXT NOT NULL,
        mailing_cedula_juridica TEXT NOT NULL,
        mailing_post_code TEXT,
        general_email TEXT NOT NULL,
        general_phone TEXT NOT NULL,
        whatsapp_sales TEXT,
        whatsapp_operations TEXT,
        website TEXT,
        notes TEXT,
        supplier_type TEXT NOT NULL,
        payment_policy TEXT NOT NULL,
        vcc_active INTEGER DEFAULT 0,
        vcc_activation_type TEXT,
        vcc_days_prior TEXT,
        vcc_duration TEXT,
        vcc_currency TEXT,
        language TEXT,
        raw_json TEXT
    )
    """)
    conn.commit()
    conn.close()

def _send_email_task(data, submission_id):
    smtp_host = os.environ.get("SMTP_HOST")
    if not smtp_host:
        print("[Notification] SMTP_HOST not set. Notification email skipped.")
        return

    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    to_email = os.environ.get("NOTIFICATION_TO") or os.environ.get("NOTIFICATION_EMAIL")
    if not to_email:
        print("[Notification] NOTIFICATION_TO email not set. Notification email skipped.")
        return

    from_email = os.environ.get("NOTIFICATION_FROM") or smtp_user or "notifications@samaraexplorers.com"
    admin_url = os.environ.get("ADMIN_URL", "https://samaraexplorers.onrender.com/admin.html")

    try:
        creditor_name = data.get("creditor_name", "Unknown")
        tax_id = data.get("mailing_cedula_juridica", "N/A")
        email = data.get("general_email", "N/A")
        phone = data.get("general_phone", "N/A")
        supplier_type = data.get("supplier_type", "N/A")
        currency = data.get("default_currency", "N/A")
        legal_name = data.get("mailing_razon_social", "N/A")
        lang = data.get("language_page", "en").upper()

        subject = f"🔔 New Provider Onboarding: {creditor_name} (#{submission_id})"
        body = f"""Hello Samara Explorers Team,

A new provider has submitted their onboarding details via the web portal:

- Submission ID: #{submission_id}
- Creditor / Trading Name: {creditor_name}
- Legal Name (Razón Social): {legal_name}
- Tax ID (Cédula): {tax_id}
- Supplier Type: {supplier_type}
- Currency: {currency}
- Email: {email}
- Phone: {phone}
- Form Language: {lang}

View all submissions in the Admin Dashboard:
{admin_url}

Best regards,
TourPlan Automated Ingestion System
"""
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            if smtp_port in (587, 25):
                server.starttls()
                server.ehlo()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"[Notification] Notification email successfully sent to {to_email} for submission #{submission_id}")
    except Exception as e:
        print(f"[Notification] Error sending email notification: {e}")

def trigger_notification_email_async(data, submission_id):
    thread = threading.Thread(target=_send_email_task, args=(data, submission_id), daemon=True)
    thread.start()

class TourPlanHandler(http.server.BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        content = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def check_auth(self):
        if not ADMIN_PASSWORD:
            return True  # If no password configured, access is allowed
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = decoded.split(":", 1)
            return username == ADMIN_USER and password == ADMIN_PASSWORD
        except Exception:
            return False

    def request_auth(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="TourPlan Admin Area"')
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>401 Unauthorized</h1><p>Access requires administrative credentials.</p>")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/api/submit":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_json({"error": "Empty payload"}, 400)
                return

            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON format"}, 400)
                return

            # Required field validation
            required_fields = [
                ("creditor_name", "Creditor / Trading Name"),
                ("default_currency", "Default Currency"),
                ("mailing_razon_social", "Legal Name (Razón Social)"),
                ("mailing_cedula_juridica", "Corporate Tax ID (Cédula Jurídica)"),
                ("general_email", "General Email"),
                ("general_phone", "General Phone"),
                ("supplier_type", "Supplier Type"),
                ("payment_policy", "Payment Policy")
            ]

            missing = [label for key, label in required_fields if not data.get(key, "").strip()]
            if missing:
                self.send_json({
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing)}"
                }, 400)
                return

            # Save to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO creditor_submissions (
                language_page, creditor_code, creditor_name, local_creditor_name, default_currency,
                physical_name, physical_address, physical_city, physical_country,
                physical_razon_social, physical_cedula_juridica, physical_post_code,
                mailing_name, mailing_address, mailing_city, mailing_country,
                mailing_razon_social, mailing_cedula_juridica, mailing_post_code,
                general_email, general_phone, whatsapp_sales, whatsapp_operations, website, notes,
                supplier_type, payment_policy,
                vcc_active, vcc_activation_type, vcc_days_prior, vcc_duration, vcc_currency,
                language, raw_json
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?
            )
            """, (
                data.get("language_page", "en"),
                data.get("creditor_code", "").strip(),
                data.get("creditor_name", "").strip(),
                data.get("local_creditor_name", "").strip(),
                data.get("default_currency", "").strip(),
                data.get("physical_name", "").strip(),
                data.get("physical_address", "").strip(),
                data.get("physical_city", "").strip(),
                data.get("physical_country", "").strip(),
                data.get("physical_razon_social", "").strip(),
                data.get("physical_cedula_juridica", "").strip(),
                data.get("physical_post_code", "").strip(),
                data.get("mailing_name", "").strip(),
                data.get("mailing_address", "").strip(),
                data.get("mailing_city", "").strip(),
                data.get("mailing_country", "").strip(),
                data.get("mailing_razon_social", "").strip(),
                data.get("mailing_cedula_juridica", "").strip(),
                data.get("mailing_post_code", "").strip(),
                data.get("general_email", "").strip(),
                data.get("general_phone", "").strip(),
                data.get("whatsapp_sales", "").strip(),
                data.get("whatsapp_operations", "").strip(),
                data.get("website", "").strip(),
                data.get("notes", "").strip(),
                data.get("supplier_type", "").strip(),
                data.get("payment_policy", "").strip(),
                1 if data.get("vcc_active") in [True, "true", "1", 1] else 0,
                data.get("vcc_activation_type", "").strip(),
                str(data.get("vcc_days_prior", "")).strip(),
                str(data.get("vcc_duration", "")).strip(),
                data.get("vcc_currency", "").strip(),
                data.get("language", "").strip(),
                json.dumps(data, ensure_ascii=False)
            ))
            submission_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Trigger email notification asynchronously
            trigger_notification_email_async(data, submission_id)

            self.send_json({
                "success": True,
                "id": submission_id,
                "message": "Submission recorded successfully. Thank you!" if data.get("language_page") == "en" else "Registro recibido correctamente. ¡Muchas gracias!"
            }, 201)
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Protect administrative endpoints
        if path in ("/admin", "/admin.html", "/api/submissions", "/api/export/csv"):
            if not self.check_auth():
                self.request_auth()
                return

        # API: List all submissions
        if path == "/api/submissions":
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM creditor_submissions ORDER BY id DESC")
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json({"count": len(rows), "submissions": rows})
            return

        # API: Export CSV
        if path == "/api/export/csv":
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM creditor_submissions ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()

            output = io.StringIO()
            if rows:
                writer = csv.DictWriter(output, fieldnames=rows[0].keys())
                writer.writeheader()
                for row in rows:
                    writer.writerow(dict(row))

            csv_data = output.getvalue().encode('utf-8-sig')  # with BOM for Excel compatibility
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=TourPlan_Creditor_Submissions.csv")
            self.send_header("Content-Length", str(len(csv_data)))
            self.end_headers()
            self.wfile.write(csv_data)
            return

        # Static routing shortcuts
        if path in ("/", "/en", "/en.html"):
            target = os.path.join(PUBLIC_DIR, "index.html")
        elif path in ("/es", "/es.html"):
            target = os.path.join(PUBLIC_DIR, "es.html")
        elif path in ("/admin", "/admin.html"):
            target = os.path.join(PUBLIC_DIR, "admin.html")
        else:
            rel_path = path.lstrip("/")
            target = os.path.join(PUBLIC_DIR, rel_path)

        # Sanitize path to prevent directory traversal
        target = os.path.abspath(target)
        if not target.startswith(os.path.abspath(PUBLIC_DIR)):
            self.send_error(403, "Forbidden")
            return

        if os.path.isfile(target):
            mime_type, _ = mimetypes.guess_type(target)
            if not mime_type:
                mime_type = "application/octet-stream"
            with open(target, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{mime_type}; charset=utf-8" if "text" in mime_type or "javascript" in mime_type or "json" in mime_type else mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "File Not Found")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

def run_server():
    init_db()
    with ThreadedTCPServer(("", PORT), TourPlanHandler) as httpd:
        auth_status = f"Protected (User: {ADMIN_USER})" if ADMIN_PASSWORD else "Unprotected (ADMIN_PASSWORD not set)"
        print(f"==================================================")
        print(f" TourPlan Provider Onboarding Portal Running:")
        print(f" - English Form:   http://localhost:{PORT}/")
        print(f" - Spanish Form:   http://localhost:{PORT}/es.html")
        print(f" - Admin View:     http://localhost:{PORT}/admin.html [{auth_status}]")
        print(f" - CSV Export API: http://localhost:{PORT}/api/export/csv")
        print(f" - Database Path:  {DB_PATH}")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    run_server()
