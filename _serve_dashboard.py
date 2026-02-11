"""Temp script to launch dashboard server."""
import sys, os
os.chdir(r"C:\Users\david\jean\mrhyde-pkg\iconic-whale")
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from mrhyde import db

def get_all_data():
    db.ensure_db()
    identity = db.get_identity()
    stats = db.get_stats()
    memories = [dict(r) for r in db.get_all_memories()]
    journal = [dict(r) for r in db.get_all_journal()]
    history = [dict(r) for r in db.get_field_history()]
    bonds = [dict(r) for r in db.get_bonds()]
    encounters = [dict(r) for r in db.get_encounters()]
    dreams = [dict(r) for r in db.get_dreams(limit=50)]
    for d in dreams:
        if d.get("themes") and isinstance(d["themes"], str):
            try: d["themes"] = json.loads(d["themes"])
            except: d["themes"] = []
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

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html_path = Path(r"C:\Users\david\jean\mrhyde-pkg\iconic-whale\src\mrhyde\dashboard.html")
            content = html_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/api/all":
            body = json.dumps(get_all_data(), default=str).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

server = HTTPServer(("127.0.0.1", 8432), Handler)
print(f"Dashboard: http://127.0.0.1:8432", flush=True)
server.serve_forever()
