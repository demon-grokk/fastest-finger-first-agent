import json
import os
import sys
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.ipc_solver import listen_and_solve

class WebhookHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        # Enable CORS for requests from Gmail/Tampermonkey
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        if self.path in ['/solve', '/']:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                url = data.get('url')
                if not url:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing 'url' field in payload"}).encode('utf-8'))
                    return

                print(f"\n[WEBHOOK] ⚡ Received Form URL from Gmail extension: {url}")
                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "received", "url": url}).encode('utf-8'))

                # Trigger the solver asynchronously
                asyncio.run(listen_and_solve(url))
            except Exception as e:
                print(f"[ERROR] Failed to process webhook payload: {e}")
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)

    def log_message(self, format, *args):
        # Suppress standard HTTP access logs to keep terminal output clean
        return

def start_webhook_server(port: int = 5000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    print(f"\n" + "="*75)
    print(f"⚡ FASTEST FINGER FIRST - GMAIL LIVE WEBHOOK SERVER ⚡")
    print(f"Listening on: http://localhost:{port}/solve")
    print(f"Status: Waiting for automated link payloads from Tampermonkey...")
    print(f"="*75 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[WEBHOOK] Server stopped.")

if __name__ == '__main__':
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    start_webhook_server(port_arg)
