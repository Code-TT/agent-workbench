"""Leichtgewichtiger Dummy-HTTP-Server fuer Integrationstests (loopback only).

Port via TESTSLOT_PORT (Default 31201). Endpunkte: /health -> 200 "ok",
/ -> 200 "dummy". Reiner Test-Prozess, schreibt nichts, startet nichts.
"""
import http.server
import os
import socketserver


class Server(socketserver.TCPServer):
    allow_reuse_address = True  # schnelles Port-Recycling nach Neustart


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"ok" if self.path == "/health" else b"dummy"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # Log bleibt klein
        pass


if __name__ == "__main__":
    port = int(os.environ.get("TESTSLOT_PORT", "31201"))
    with Server(("127.0.0.1", port), Handler) as httpd:
        httpd.serve_forever()
