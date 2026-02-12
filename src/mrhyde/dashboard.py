"""
Mr. Hyde Dashboard — a window into your agent's mind.

Starts a local HTTP server serving the dashboard HTML and JSON API endpoints.
"""

import json
import socket
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from . import db


def _row_to_dict(row):
    """Convert a sqlite3.Row to a plain dict."""
    return dict(row) if row else None


def _rows_to_list(rows):
    """Convert a list of sqlite3.Row to a list of dicts."""
    return [dict(r) for r in rows]


def _get_all_data():
    """Collect all agent data in a single payload."""
    db.ensure_db()

    identity = db.get_identity()
    stats = db.get_stats()
    memories = _rows_to_list(db.get_all_memories())
    journal = _rows_to_list(db.get_all_journal())
    history = _rows_to_list(db.get_field_history())
    bonds = _rows_to_list(db.get_bonds())
    encounters = _rows_to_list(db.get_encounters())
    dreams = _rows_to_list(db.get_dreams(limit=50))

    # Parse dream themes from JSON strings
    for d in dreams:
        if d.get("themes") and isinstance(d["themes"], str):
            try:
                d["themes"] = json.loads(d["themes"])
            except (json.JSONDecodeError, TypeError):
                d["themes"] = []

    card = db.generate_card()

    return {
        "identity": identity or {},
        "stats": stats,
        "memories": memories,
        "journal": journal,
        "history": history,
        "bonds": bonds,
        "encounters": encounters,
        "dreams": dreams,
        "card": card,
        "field_labels": db.FIELD_LABELS,
        "identity_fields": db.IDENTITY_FIELDS,
        "bond_types": db.BOND_TYPES,
    }


class DashboardHandler(BaseHTTPRequestHandler):
    """Handle dashboard HTTP requests."""

    def log_message(self, format, *args):
        # Silence request logging
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_html()
        elif self.path == "/api/all":
            self._serve_json(_get_all_data())
        else:
            self.send_error(404)

    def _serve_html(self):
        html_path = Path(__file__).parent / "dashboard.html"
        try:
            content = html_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(500, "dashboard.html not found")

    def _serve_json(self, data):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _find_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(port=0):
    """Start the dashboard server and open in browser."""
    db.ensure_db()

    if port == 0:
        port = _find_free_port()

    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    url = f"http://127.0.0.1:{port}"

    identity = db.get_identity()
    name = identity.get("name", "your agent") if identity else "your agent"

    print(f"Opening {name}'s dashboard...")
    print(f"  {url}")
    print()
    print("Press Ctrl+C to stop.")

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()
