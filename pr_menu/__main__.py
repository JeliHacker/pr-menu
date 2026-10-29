"""Serve a local report or public demo without third-party dependencies."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".pr-menu" / "inventory.json"


def load_report(demo=False):
    path = ROOT / "demo.json" if demo or not LOCAL.exists() else LOCAL
    data = json.loads(path.read_text())
    data["mode"] = "demo" if path.name == "demo.json" else "local"
    return data


def handler(demo=False):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/":
                content = (ROOT / "web" / "index.html").read_bytes()
                kind = "text/html; charset=utf-8"
            elif path == "/api/report":
                try:
                    content = json.dumps(load_report(demo)).encode()
                except (ValueError, OSError):
                    self.send_error(500, "Cannot read the report snapshot")
                    return
                kind = "application/json; charset=utf-8"
            elif path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

        def do_POST(self):
            self.send_error(405, "This version only displays reports and copies commands")
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4317)
    parser.add_argument("--demo", action="store_true", help="Use demo data even if a local snapshot exists")
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler(args.demo)) as server:
        mode = load_report(args.demo)["mode"]
        print(f"pr-menu: http://localhost:{args.port} ({mode} snapshot)", flush=True)
        print("Ctrl+C to stop. Commands are copied, never executed by the server.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
