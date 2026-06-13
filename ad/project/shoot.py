"""Headless-Chrome UI capture for the UTOS ad, via the DevTools protocol.

Runs a separate --headless=new Chrome (does NOT touch the user's visible browser),
logs in as each role by seeding localStorage, and screenshots each hash-routed
view at 1920x1080 @ deviceScaleFactor 2 (=> 3840x2160 crisp PNGs).

Pure stdlib: a minimal WebSocket client speaks CDP to Chrome.
"""
import base64, glob, json, os, random, socket, struct, subprocess, sys, tempfile, time, urllib.request

BASE = "http://127.0.0.1:8000"
OUT = os.path.join(os.path.dirname(__file__), "..", "screenshots")
OUT = os.path.abspath(OUT)
PORT = 9333

# name, user_id (None => logged out / login screen), hash-view
CAPTURES = [
    ("01_login",            None, ""),
    ("02_admin_dashboard",  1,    "#dashboard"),
    ("03_admin_timetable",  1,    "#timetable"),
    ("04_admin_versions",   1,    "#versions"),
    ("05_admin_reports",    1,    "#reports"),
    ("06_teacher_timetable",41,   "#timetable"),
    ("07_student_timetable",53,   "#timetable"),
    ("08_facility_reports", 3,    "#reports"),
]


def find_chrome():
    cands = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    raise SystemExit("chrome.exe not found")


class WS:
    def __init__(self, url):
        # url: ws://host:port/devtools/page/<id>
        assert url.startswith("ws://")
        rest = url[5:]
        hostport, _, path = rest.partition("/")
        host, _, port = hostport.partition(":")
        self.sock = socket.create_connection((host, int(port)), timeout=30)
        self.sock.settimeout(30)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        if b"101" not in buf.split(b"\r\n")[0]:
            raise SystemExit("WS handshake failed: " + buf[:120].decode("latin1"))
        self._id = 0

    def _recv_exact(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise SystemExit("socket closed")
            data += chunk
        return data

    def _recv_message(self):
        payload = b""
        while True:
            b1, b2 = self._recv_exact(2)
            fin = b1 & 0x80
            opcode = b1 & 0x0F
            masked = b2 & 0x80
            ln = b2 & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._recv_exact(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._recv_exact(8))[0]
            mask = self._recv_exact(4) if masked else b""
            data = self._recv_exact(ln)
            if masked:
                data = bytes(c ^ mask[i % 4] for i, c in enumerate(data))
            if opcode == 0x9:  # ping -> pong
                self._send_frame(0xA, data)
                continue
            if opcode == 0x8:  # close
                raise SystemExit("server closed ws")
            payload += data
            if fin:
                return payload

    def _send_frame(self, opcode, data):
        b1 = 0x80 | opcode
        ln = len(data)
        header = bytes([b1])
        mask = os.urandom(4)
        if ln < 126:
            header += bytes([0x80 | ln])
        elif ln < 65536:
            header += bytes([0x80 | 126]) + struct.pack(">H", ln)
        else:
            header += bytes([0x80 | 127]) + struct.pack(">Q", ln)
        header += mask
        masked = bytes(c ^ mask[i % 4] for i, c in enumerate(data))
        self.sock.sendall(header + masked)

    def cmd(self, method, params=None):
        self._id += 1
        mid = self._id
        self._send_frame(0x1, json.dumps({"id": mid, "method": method, "params": params or {}}).encode())
        while True:
            msg = json.loads(self._recv_message().decode("utf-8"))
            if msg.get("id") == mid:
                if "error" in msg:
                    raise SystemExit(f"CDP error {method}: {msg['error']}")
                return msg.get("result", {})
            # else: event, ignore


def main():
    os.makedirs(OUT, exist_ok=True)
    users = json.load(urllib.request.urlopen(BASE + "/api/users"))
    if isinstance(users, dict):
        users = users.get("users", [])
    by_id = {u["id"]: u for u in users}

    chrome = find_chrome()
    profile = tempfile.mkdtemp(prefix="utos_shoot_")
    proc = subprocess.Popen([
        chrome, "--headless=new", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
        "--disable-extensions", "--hide-scrollbars", "--window-size=1920,1080",
        "--disable-gpu", "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        ws_url = None
        for _ in range(40):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                pages = [t for t in tabs if t.get("type") == "page" and t.get("webSocketDebuggerUrl")]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.25)
        if not ws_url:
            raise SystemExit("no devtools page target")

        ws = WS(ws_url)
        ws.cmd("Page.enable")
        ws.cmd("Runtime.enable")
        ws.cmd("Emulation.setDeviceMetricsOverride",
               {"width": 1920, "height": 1080, "deviceScaleFactor": 2, "mobile": False})

        for name, uid, view in CAPTURES:
            ws.cmd("Page.navigate", {"url": BASE + "/" + view})
            time.sleep(0.9)
            if uid is None:
                ws.cmd("Runtime.evaluate", {"expression": "localStorage.clear()"})
            else:
                u = by_id[uid]
                js = "localStorage.setItem('currentUser', " + json.dumps(json.dumps(u)) + ")"
                ws.cmd("Runtime.evaluate", {"expression": js})
            ws.cmd("Page.reload", {"ignoreCache": True})   # full reload so app re-reads session
            time.sleep(2.6)
            if view:
                ws.cmd("Runtime.evaluate", {"expression": "location.hash=''; location.hash='%s'" % view})
                time.sleep(0.8)
            res = ws.cmd("Page.captureScreenshot", {"format": "png"})
            path = os.path.join(OUT, name + ".png")
            with open(path, "wb") as f:
                f.write(base64.b64decode(res["data"]))
            print(f"  saved {name}.png  ({os.path.getsize(path)//1024} KB)")
    finally:
        try:
            proc.terminate()
        except Exception:
            pass
    print("DONE")


if __name__ == "__main__":
    main()
