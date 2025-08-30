# post_quote.py
import os, json, requests, pathlib, unicodedata, time

API_BASE = "https://api.x.com/2"
TOKEN_URL = f"{API_BASE}/oauth2/token"
POST_URL = f"{API_BASE}/tweets"

CLIENT_ID = os.environ["X_CLIENT_ID"]
REFRESH_TOKEN = os.environ["X_REFRESH_TOKEN"]  # from auth_pkce.py output
QUOTES_FILE = os.environ.get("QUOTES_FILE", "quotes.txt")
STATE_FILE = os.environ.get("STATE_FILE", "state.json")

def nfc_len(s: str) -> int:
    return len(unicodedata.normalize("NFC", s))

def trim_to_280(s: str) -> str:
    s = unicodedata.normalize("NFC", s).strip()
    if nfc_len(s) <= 280:
        return s
    return s[:277] + "..."

def refresh_access_token():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def load_quotes():
    p = pathlib.Path(QUOTES_FILE)
    if not p.exists():
        raise SystemExit("quotes.txt not found.")
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        raise SystemExit("quotes file empty.")
    return lines

def next_index(n):
    i = 0
    if pathlib.Path(STATE_FILE).exists():
        try:
            j = json.loads(pathlib.Path(STATE_FILE).read_text())
            i = j.get("i", 0) % n
        except:
            i = 0
    pathlib.Path(STATE_FILE).write_text(json.dumps({"i": i+1}))
    return i

def post_text(access_token: str, text: str):
    payload = {"text": trim_to_280(text)}
    r = requests.post(POST_URL, json=payload, headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    quotes = load_quotes()
    idx = next_index(len(quotes))
    text = quotes[idx]
    token = refresh_access_token()
    resp = post_text(token, text)
    print("Posted:", resp)
