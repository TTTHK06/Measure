#!/usr/bin/env python3
"""Tiny dev server for RoomScan.

    py serve.py            -> http://<your-lan-ip>:8777   (Photo mode works)
    py serve.py --port 9000

Scan mode (live camera + tilt sensors) needs a SECURE page. Browsers treat
http://localhost as secure, but a phone reaching this machine over the LAN is
not. Options for the phone:
  * run a tunnel:   cloudflared tunnel --url http://localhost:8777
                    ngrok http 8777
  * or use the Photo tab, which needs no camera permission at all.
"""
import argparse
import http.server
import socket
import socketserver


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # never cache during development
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        print("  %s" % (fmt % args))


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8777)
    args = ap.parse_args()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", args.port), Handler) as httpd:
        print("RoomScan dev server")
        print("  this machine : http://localhost:%d" % args.port)
        print("  on the LAN   : http://%s:%d" % (lan_ip(), args.port))
        print("  Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main()
