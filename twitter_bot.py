import subprocess
import time
import requests
import os
import json
import sys

def run_node_quote():
    try:
        subprocess.run(["node", "quote.js"], check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to run quote.js:", e, file=sys.stderr)
        # continue, maybe quotes.txt already present

def read_quotes(path="quotes.txt"):
    if not os.path.exists(path):
        print(f"{path} not found.", file=sys.stderr)
        return []
    with open(path, "r", encoding="utf-8") as f:
        # strip lines and ignore empty ones
        return [line.strip() for line in f if line.strip()]

# Run quote.js to (re)generate quotes.txt
run_node_quote()

# Read quotes.txt
quotes = read_quotes("quotes.txt")

# pick last 2 quotes (or fewer if not available)
quotes_to_post = quotes[-2:] if quotes else []

# Read secrets from environment
CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TWITTER_CLIENT_SECRET")  # optional for PKCE clients
REFRESH_TOKEN = os.environ.get("TWITTER_REFRESH_TOKEN")
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

if not CLIENT_ID or not REFRESH_TOKEN:
    print("Missing TWITTER_CLIENT_ID or TWITTER_REFRESH_TOKEN in environment.", file=sys.stderr)
    sys.exit(1)

# Refresh access token
def refresh_access_token():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # If you have a client secret and the token endpoint requires HTTP Basic auth,
    # requests will send it when auth is provided. If not needed, auth can be None.
    auth = (CLIENT_ID, CLIENT_SECRET) if CLIENT_SECRET else None

    resp = requests.post(TOKEN_URL, data=data, headers=headers, auth=auth)
    resp.raise_for_status()
    new_tokens = resp.json()

    # Save new refresh token if provided
    if "refresh_token" in new_tokens:
        with open("new_refresh_token.json", "w", encoding="utf-8") as f:
            json.dump({"refresh_token": new_tokens["refresh_token"]}, f, indent=2)

    if "access_token" not in new_tokens:
        raise RuntimeError(f"No access_token returned: {new_tokens}")

    return new_tokens["access_token"]

try:
    ACCESS_TOKEN = refresh_access_token()
except Exception as e:
    print("Failed to refresh access token:", e, file=sys.stderr)
    sys.exit(1)

# Post to Twitter
def post_tweet(text):
    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    r = requests.post(url, headers=headers, json=payload)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        print("Failed to post tweet:", r.status_code, r.text, file=sys.stderr)
        return None
    print("Posted tweet:", r.json())
    return r

# Post two quotes
if not quotes_to_post:
    print("No quotes to post.", file=sys.stderr)
    sys.exit(0)

for quote in quotes_to_post:
    post_tweet(quote)
    time.sleep(5)  # wait 5 sec between posts
