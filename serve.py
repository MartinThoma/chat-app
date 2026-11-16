#!/usr/bin/env python3
"""Local dev server for P2P Chat.

Serves this folder over HTTPS (with a self-signed certificate) and without
caching, and prints the URLs. HTTPS is needed because the app uses the
browser's cryptography, which browsers only allow on secure origins; plain
http works only on localhost.
"""

import functools
import http.server
import re
import shutil
import socket
import ssl
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CERT_DIR = ROOT / ".cert"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet


class Server(http.server.ThreadingHTTPServer):
    """Serves HTTPS, and redirects plain-HTTP requests on the same port to HTTPS."""

    daemon_threads = True
    ssl_context: ssl.SSLContext | None = None

    def finish_request(self, request, client_address):
        # Runs in the request's own thread, so a slow client can't block the others.
        if self.ssl_context is None or not isinstance(request, socket.socket):
            return super().finish_request(request, client_address)
        request.settimeout(15)
        try:
            first = request.recv(1, socket.MSG_PEEK)
        except OSError:
            return
        if not first:
            return
        if first != b"\x16":  # not a TLS handshake: someone opened http://
            return redirect_to_https(request, self.server_address[1])
        try:
            tls = self.ssl_context.wrap_socket(request, server_side=True)
        except (ssl.SSLError, OSError):
            return  # e.g. the browser rejected the self-signed certificate
        try:
            tls.settimeout(None)
            super().finish_request(tls, client_address)
        finally:
            tls.close()

    def handle_error(self, request, client_address):
        if isinstance(sys.exc_info()[1], (ssl.SSLError, ConnectionError, TimeoutError)):
            return  # clients hanging up or giving up on the certificate: not worth a traceback
        super().handle_error(request, client_address)


def redirect_to_https(sock, port):
    try:
        head = sock.recv(8192).decode("latin-1")
    except OSError:
        return
    lines = head.split("\r\n")
    parts = lines[0].split(" ")
    path = parts[1] if len(parts) >= 2 and parts[1].startswith("/") else "/"
    host = next((l.split(":", 1)[1].strip() for l in lines[1:] if l.lower().startswith("host:")), "")
    host = re.sub(r":\d+$", "", host) if re.fullmatch(r"[A-Za-z0-9.\-]+(:\d+)?|\[[0-9a-fA-F:]+\](:\d+)?", host) else "localhost"
    location = f"https://{host}:{port}{path}"
    try:
        sock.sendall(
            f"HTTP/1.1 302 Found\r\nLocation: {location}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode("latin-1")
        )
    except OSError:
        pass


def local_ip():
    """IP of the interface used for outgoing traffic (no packets are actually sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
        except OSError:
            return None


def ensure_cert(ip):
    """Create a self-signed certificate for localhost and the LAN IP, if needed."""
    cert, key, san_file = CERT_DIR / "cert.pem", CERT_DIR / "key.pem", CERT_DIR / "san.txt"
    san = "DNS:localhost,IP:127.0.0.1" + (f",IP:{ip}" if ip else "")
    if cert.exists() and key.exists() and san_file.exists() and san_file.read_text() == san:
        return cert, key
    if not shutil.which("openssl"):
        return None
    CERT_DIR.mkdir(exist_ok=True)
    result = subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "825",
         "-keyout", str(key), "-out", str(cert), "-subj", "/CN=P2P Chat (local)",
         "-addext", f"subjectAltName={san}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        return None
    san_file.write_text(san)
    return cert, key


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(NoCacheHandler, directory=str(ROOT))
    server = Server(("0.0.0.0", port), handler)
    ip = local_ip()

    files = ensure_cert(ip)
    if files:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(*files)
        server.ssl_context = ctx
        print(f"P2P Chat running at:\n  https://localhost:{port}/")
        if ip:
            print(f"  https://{ip}:{port}/   (other devices on your network)")
        print("\nThe certificate is self-signed, so browsers show a warning the first time.")
        print("Choose “Advanced” → “Proceed” (or similar) to open the app.")
    else:
        print("openssl not found: serving plain HTTP, which only works on this computer.")
        print(f"P2P Chat running at:\n  http://localhost:{port}/")
    if ip:
        print(f"\nYour local IP: {ip}  (enter it under 'Network settings' if a LAN connection fails)")
    print("\nPress Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
