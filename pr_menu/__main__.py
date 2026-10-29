"""Serve a local report or public demo without third-party dependencies."""
import argparse
import json
import secrets
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .codex import prepare_chat

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".pr-menu" / "inventory.json"


def load_report(demo=False):
    path = ROOT / "demo.json" if demo or not LOCAL.exists() else LOCAL
    data = json.loads(path.read_text())
    data["mode"] = "demo" if path.name == "demo.json" else "local"
    return data


def handler(demo=False):
    token = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/":
                content = (ROOT / "web" / "index.html").read_bytes()
                kind = "text/html; charset=utf-8"
            elif path == "/api/report":
                try:
                    report = load_report(demo)
                    report['actionToken'] = token
                    content = json.dumps(report).encode()
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
            if self.path != '/api/codex':
                self.send_error(404)
                return
            origin = self.headers.get('Origin', '')
            allowed = {f'http://localhost:{self.server.server_port}',
                       f'http://127.0.0.1:{self.server.server_port}'}
            if (origin not in allowed or
                    not secrets.compare_digest(self.headers.get('X-Pr-Menu-Token', ''), token)):
                self.send_error(403, 'Open this action from the local pr-menu page')
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 4096:
                    raise ValueError('Invalid request size')
                if self.headers.get('Content-Type') != 'application/json':
                    raise ValueError('Expected a JSON request')
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict) or not isinstance(body.get('branch'), str):
                    raise ValueError('Choose a branch from the current report')
                result = prepare_chat(load_report(demo), body['branch'], ROOT / '.pr-menu' / 'workspaces')
                status = 200
            except (ValueError, OSError, subprocess.TimeoutExpired) as error:
                result = {'error': str(error) if isinstance(error, ValueError) else 'Could not prepare the local workspace'}
                status = 400
            content = json.dumps(result).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(content)
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4317)
    parser.add_argument("--demo", action="store_true", help="Use demo data even if a local snapshot exists")
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler(args.demo)) as server:
        mode = load_report(args.demo)["mode"]
        print(f"pr-menu: http://localhost:{args.port} ({mode} snapshot)", flush=True)
        print("Ctrl+C to stop. Shell commands are copied. Open in Codex can prepare a branch worktree.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
