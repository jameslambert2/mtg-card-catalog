import os, time, hmac, base64, hashlib, secrets, sqlite3, stat
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# ---------- Security / Storage ----------
APP_DIR = Path.home() / ".myapp_auth_demo"
APP_DIR.mkdir(mode=0o700, exist_ok=True)
DB_PATH = APP_DIR / "auth.db"

# Keep this secret outside code in real apps (env/KMS). For demo, fallback is fine.
APP_SECRET = os.environ.get("APP_SECRET", secrets.token_hex(32)).encode()
APP_PEPPER = os.environ.get("APP_PEPPER", "")

SESSION_IDLE_TTL = 30 * 60          # 30 min idle timeout
SESSION_ABSOLUTE_TTL = 8 * 3600     # 8 hours absolute lifetime

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3, memory_cost=64 * 1024, parallelism=2, hash_len=32, salt_len=16
)

def _db():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        pw_hash TEXT NOT NULL,
        created_at INTEGER NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS sessions(
        sid TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        iat INTEGER NOT NULL,
        last_seen INTEGER NOT NULL,
        abs_exp INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")
    return con

def _sign(value: str) -> str:
    mac = hmac.new(APP_SECRET, value.encode(), hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(mac).decode().rstrip("=")
    return f"{value}.{sig}"

def _unsign(token: str) -> Optional[str]:
    try:
        value, sig = token.rsplit(".", 1)
        got = base64.urlsafe_b64decode(sig + "==")
    except Exception:
        return None
    exp = hmac.new(APP_SECRET, value.encode(), hashlib.sha256).digest()
    return value if hmac.compare_digest(exp, got) else None

@dataclass
class AuthUser:
    id: int
    email: str

class AuthService:
    """Password hashing + session management; GUI calls into this."""
    def signup(self, email: str, password: str):
        email = email.strip().lower()
        if not email or not password:
            raise ValueError("Email and password are required.")
        pw_hash = ph.hash(password + APP_PEPPER)
        with _db() as con:
            try:
                con.execute(
                    "INSERT INTO users(email, pw_hash, created_at) VALUES(?,?,?)",
                    (email, pw_hash, int(time.time())),
                )
            except sqlite3.IntegrityError:
                raise ValueError("Email already exists.")

    def login(self, email: str, password: str) -> str:
        """Returns a signed session token (opaque)."""
        email = email.strip().lower()
        with _db() as con:
            row = con.execute("SELECT id, pw_hash FROM users WHERE email=?", (email,)).fetchone()
            if not row:
                raise ValueError("Invalid credentials.")
            uid, pw_hash = row
            try:
                ph.verify(pw_hash, password + APP_PEPPER)
            except VerifyMismatchError:
                raise ValueError("Invalid credentials.")

            if ph.check_needs_rehash(pw_hash):
                con.execute("UPDATE users SET pw_hash=? WHERE id=?", (ph.hash(password + APP_PEPPER), uid))

            now = int(time.time())
            abs_exp = now + SESSION_ABSOLUTE_TTL
            raw_sid = secrets.token_urlsafe(32)
            con.execute(
                "INSERT OR REPLACE INTO sessions(sid, user_id, iat, last_seen, abs_exp) VALUES (?,?,?,?,?)",
                (raw_sid, uid, now, now, abs_exp),
            )
            return _sign(raw_sid)

    def logout(self, token: Optional[str]):
        if not token:
            return
        raw_sid = _unsign(token)
        if raw_sid:
            with _db() as con:
                con.execute("DELETE FROM sessions WHERE sid=?", (raw_sid,))

    def current_user(self, token: Optional[str], touch: bool = True) -> Optional[AuthUser]:
        if not token:
            return None
        raw_sid = _unsign(token)
        if not raw_sid:
            return None
        now = int(time.time())
        with _db() as con:
            row = con.execute(
                "SELECT s.user_id, s.iat, s.last_seen, s.abs_exp, u.email "
                "FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.sid=?",
                (raw_sid,),
            ).fetchone()
            if not row:
                return None
            uid, iat, last_seen, abs_exp, email = row
            # absolute expiry
            if now > abs_exp:
                con.execute("DELETE FROM sessions WHERE sid=?", (raw_sid,))
                return None
            # idle expiry
            if now - last_seen > SESSION_IDLE_TTL:
                con.execute("DELETE FROM sessions WHERE sid=?", (raw_sid,))
                return None
            if touch and (now - last_seen) > (SESSION_IDLE_TTL // 2):
                con.execute("UPDATE sessions SET last_seen=? WHERE sid=?", (now, raw_sid))
            return AuthUser(id=uid, email=email)

    def rotate(self, token: Optional[str]) -> Optional[str]:
        if not token:
            return None
        raw_sid = _unsign(token)
        if not raw_sid:
            return None
        with _db() as con:
            row = con.execute("SELECT user_id, abs_exp FROM sessions WHERE sid=?", (raw_sid,)).fetchone()
            if not row:
                return None
            uid, abs_exp = row
            now = int(time.time())
            new_sid = secrets.token_urlsafe(32)
            con.execute("DELETE FROM sessions WHERE sid=?", (raw_sid,))
            con.execute(
                "INSERT INTO sessions(sid, user_id, iat, last_seen, abs_exp) VALUES (?,?,?,?,?)",
                (new_sid, uid, now, now, abs_exp),
            )
            return _sign(new_sid)

# ---------- Tkinter GUI ----------
import tkinter as tk
from tkinter import ttk, messagebox

class LoginFrame(ttk.Frame):
    def __init__(self, master, auth: AuthService, on_login):
        super().__init__(master, padding=16)
        self.auth = auth
        self.on_login = on_login

        self.email_var = tk.StringVar()
        self.pw_var = tk.StringVar()

        ttk.Label(self, text="Sign in", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,12))

        ttk.Label(self, text="Email").grid(row=1, column=0, sticky="w")
        email_entry = ttk.Entry(self, textvariable=self.email_var, width=32)
        email_entry.grid(row=1, column=1, sticky="ew", pady=4)
        email_entry.focus()

        ttk.Label(self, text="Password").grid(row=2, column=0, sticky="w")
        pw_entry = ttk.Entry(self, textvariable=self.pw_var, width=32, show="•")
        pw_entry.grid(row=2, column=1, sticky="ew", pady=4)
        pw_entry.bind("<Return>", lambda e: self.try_login())

        btn_row = ttk.Frame(self)
        btn_row.grid(row=3, column=0, columnspan=2, pady=(10,0), sticky="ew")
        ttk.Button(btn_row, text="Log in", command=self.try_login).pack(side="left")
        ttk.Button(btn_row, text="Sign up", command=self.open_signup).pack(side="left", padx=(8,0))
        ttk.Button(btn_row, text="Quit", command=self.master.quit).pack(side="right")

        self.status = ttk.Label(self, text="", foreground="#a00")
        self.status.grid(row=4, column=0, columnspan=2, pady=(8,0), sticky="w")
        self.columnconfigure(1, weight=1)

    def try_login(self):
        email = self.email_var.get().strip()
        pw = self.pw_var.get()
        try:
            token = self.auth.login(email, pw)
        except Exception as e:
            self.status.config(text=str(e))
            return
        self.email_var.set(""); self.pw_var.set("")
        self.on_login(token)

    def open_signup(self):
        SignupDialog(self.master, self.auth)

class SignupDialog(tk.Toplevel):
    def __init__(self, master, auth: AuthService):
        super().__init__(master)
        self.auth = auth
        self.title("Create account")
        self.transient(master)
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)

        self.email = tk.StringVar()
        self.pw = tk.StringVar()
        self.pw2 = tk.StringVar()

        ttk.Label(frm, text="Create account", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,12))
        ttk.Label(frm, text="Email").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.email, width=34).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Label(frm, text="Password").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.pw, show="•", width=34).grid(row=2, column=1, sticky="ew", pady=4)
        ttk.Label(frm, text="Confirm").grid(row=3, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.pw2, show="•", width=34).grid(row=3, column=1, sticky="ew", pady=4)

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=(10,0), sticky="ew")
        ttk.Button(btns, text="Create", command=self.create).pack(side="left")
        ttk.Button(btns, text="Close", command=self.destroy).pack(side="right")

        self.status = ttk.Label(frm, text="", foreground="#0a0")
        self.status.grid(row=5, column=0, columnspan=2, pady=(8,0), sticky="w")
        frm.columnconfigure(1, weight=1)

        self.grab_set()
        self.wait_visibility()
        self.focus()

    def create(self):
        email = self.email.get().strip()
        p1, p2 = self.pw.get(), self.pw2.get()
        if not email or not p1:
            messagebox.showerror("Error", "Email and password are required.")
            return
        if p1 != p2:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        try:
            self.auth.signup(email, p1)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.status.config(text="Account created. You can close this dialog.")

class MainFrame(ttk.Frame):
    def __init__(self, master, auth: AuthService, token: str, on_logout):
        super().__init__(master, padding=16)
        self.auth = auth
        self.token = token
        self.on_logout = on_logout
        self.last_user: Optional[AuthUser] = None

        ttk.Label(self, text="Demo App", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        self.user_lbl = ttk.Label(self, text="")
        self.user_lbl.grid(row=1, column=0, sticky="w", pady=(6,12))

        ttk.Button(self, text="Protected action", command=self.protected_action).grid(row=2, column=0, sticky="w")
        ttk.Button(self, text="Rotate session", command=self.rotate_session).grid(row=2, column=1, sticky="w", padx=(8,0))
        ttk.Button(self, text="Logout", command=self.logout).grid(row=2, column=2, sticky="e")

        self.status = ttk.Label(self, text="", foreground="#555")
        self.status.grid(row=3, column=0, columnspan=3, sticky="w", pady=(8,0))

        self._tick()  # start session heartbeat
        for i in range(3): self.columnconfigure(i, weight=1)

    def _tick(self):
        user = self.auth.current_user(self.token, touch=True)
        if not user:
            messagebox.showwarning("Session expired", "Your session expired. Please log in again.")
            self.on_logout()
            return
        if self.last_user is None or self.last_user.email != user.email:
            self.user_lbl.config(text=f"Logged in as: {user.email}")
        self.last_user = user

        # show time remaining (idle + absolute)
        now = int(time.time())
        with _db() as con:
            raw_sid = _unsign(self.token)
            row = con.execute("SELECT last_seen, abs_exp FROM sessions WHERE sid=?", (raw_sid,)).fetchone()
            if row:
                last_seen, abs_exp = row
                idle_left = max(0, SESSION_IDLE_TTL - (now - last_seen))
                abs_left = max(0, abs_exp - now)
                self.status.config(text=f"Idle timeout in ~{idle_left//60}m{idle_left%60:02d}s • Absolute in ~{abs_left//3600}h")
        # schedule next check
        self.after(5000, self._tick)  # every 5s

    def protected_action(self):
        # Every protected action should verify session
        user = self.auth.current_user(self.token, touch=True)
        if not user:
            messagebox.showerror("Not authenticated", "Please log in again.")
            self.on_logout()
            return
        messagebox.showinfo("OK", f"Action ran as {user.email}")

    def rotate_session(self):
        new_token = self.auth.rotate(self.token)
        if new_token:
            self.token = new_token
            messagebox.showinfo("Session", "Session rotated.")

    def logout(self):
        self.auth.logout(self.token)
        self.on_logout()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auth Demo (Tk)")
        self.geometry("520x240")
        self.resizable(False, False)
        self.auth = AuthService()
        self._frame: Optional[ttk.Frame] = None
        self._token: Optional[str] = None
        self.show_login()

    def _swap(self, frame: ttk.Frame):
        if self._frame is not None:
            self._frame.destroy()
        self._frame = frame
        self._frame.pack(fill="both", expand=True)

    def show_login(self):
        self._token = None
        self._swap(LoginFrame(self, self.auth, on_login=self.show_main))

    def show_main(self, token: str):
        self._token = token
        self._swap(MainFrame(self, self.auth, token, on_logout=self.show_login))

if __name__ == "__main__":
    App().mainloop()
