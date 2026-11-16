#!/usr/bin/env python3
"""Local dev server for P2P Chat: serves this folder without caching and prints the URLs."""

import functools
import http.server
import socket
import sys
from pathlib import Path


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def local_ip():
    """IP of the interface used for outgoing traffic (no packets are actually sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
        except OSError:
            return None


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(NoCacheHandler, directory=str(Path(__file__).parent))
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    ip = local_ip()
    print(f"P2P Chat running at:\n  http://localhost:{port}/")
    if ip:
        print(f"  http://{ip}:{port}/   (other devices on your network)")
        print(f"\nYour local IP: {ip}  (enter it under 'Network settings' if a LAN connection fails)")
    print("\nPress Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
