import os
import base64
import hashlib
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json
# -----------------------------
# 1. Fill in your app credentials
# -----------------------------
CLIENT_ID = "LUVUeE9hejhVNUV5dmk2dFhUZVI6MTpjaQ"   # From Twitter/X developer portal
CLIENT_SECRET = "sNkPmHWP3s9HEAEHQI11iUJqT0AkOdK3ZCc6uL_kj5cXEoqWUK"  # If available (not always needed for PKCE apps)
REDIRECT_URI = "http://localhost:8000/callback"
AUTHORIZE_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
SCOPES = "tweet.read tweet.write users.read offline.access"

# -----------------------------
# 2. Generate Code Verifier + Challenge (PKCE)
# -----------------------------
def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")

def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)

# -----------------------------
# 3. Build authorization URL
# -----------------------------
params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPES,
    "state": "state123",
    "code_challenge": code_challenge,
    "code_challenge_method": "S256"
}
auth_url = AUTHORIZE_URL + "?" + urllib.parse.urlencode(params)

print("Opening browser for authorization...")
print(auth_url)
webbrowser.open(auth_url)

# -----------------------------
# 4. HTTP server to capture callback
# -----------------------------
auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Authorization successful. You can close this window.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

# Start server
httpd = HTTPServer(("localhost", 8000), CallbackHandler)
print("Waiting for authorization...")
httpd.handle_request()  # waits until redirected

print("Auth code received:", auth_code)

# -----------------------------
# 5. Exchange code for access token
# -----------------------------
data = {
    "grant_type": "authorization_code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "code_verifier": code_verifier,
    "code": auth_code
}

response = requests.post(TOKEN_URL, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
tokens = response.json()
print("Access token response:", tokens)

# Save tokens
with open("refresh_token.json", "w") as f:
    json.dump(tokens, f, indent=2)

print("Tokens saved to refresh_token.json ✅")


access_token = tokens.get("access_token")

# -----------------------------
# 6. Make a test tweet
# -----------------------------
if access_token:
    headers = {"Authorization": f"Bearer {access_token}",
               "Content-Type": "application/json"}
    payload = {"text": "Hello world from my Twitter bot 🚀"}
    tweet_response = requests.post("https://api.twitter.com/2/tweets",
                                   headers=headers,
                                   json=payload)
    print("Tweet response:", tweet_response.json())
else:
    print("Failed to get access token.")
