"""Tiny dev-only sink: receives {name, dataurl} POSTs and writes PNGs to
screenshots/. CORS-open so the app page (different origin/port) can POST.
Run: python sink.py   (listens on 127.0.0.1:8799)
"""
import base64, json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(OUT, exist_ok=True)


class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        try:
            data = json.loads(body)
            name = "".join(c for c in data["name"] if c.isalnum() or c in "._-")
            durl = data["dataurl"]
            b64 = durl.split(",", 1)[1]
            raw = base64.b64decode(b64)
            path = os.path.join(OUT, name + ".png")
            with open(path, "wb") as f:
                f.write(raw)
            print("saved", path, len(raw), "bytes")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "bytes": len(raw)}).encode())
        except Exception as e:
            print("ERR", e)
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("sink on http://127.0.0.1:8799 ->", OUT)
    ThreadingHTTPServer(("127.0.0.1", 8799), H).serve_forever()
