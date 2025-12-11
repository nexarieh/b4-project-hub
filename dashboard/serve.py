#!/usr/bin/env python3
"""Robust HTTP server with threading and auto-restart capability."""

import http.server
import socketserver
import os
import signal
import sys

PORT = 8081
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Handle requests in separate threads to prevent blocking."""
    allow_reuse_address = True
    daemon_threads = True

def signal_handler(sig, frame):
    print("\nShutting down server...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    os.chdir(DIRECTORY)

    handler = http.server.SimpleHTTPRequestHandler

    with ThreadedHTTPServer(("", PORT), handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Directory: {DIRECTORY}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
