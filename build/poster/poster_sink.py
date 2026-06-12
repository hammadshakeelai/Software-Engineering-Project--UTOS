import base64, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))

class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n).decode("utf-8")
        name = self.path.strip("/") or "banner_html"
        b64 = data.split(",", 1)[1] if "," in data else data
        with open(os.path.join(HERE, name + ".png"), "wb") as f:
            f.write(base64.b64decode(b64))
        self.send_response(200); self._cors(); self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, *a): pass

ThreadingHTTPServer(("127.0.0.1", 8912), H).serve_forever()
