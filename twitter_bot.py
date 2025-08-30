import subprocess
import time
import requests
import os
import json

# 1. Run quote.js using Node
subprocess.run(["node", "quote.js"])

# 2. Read quotes.txt
with open("quotes.txt", "r") as f:
    quotes = f.readlines()

# pick last 2 quotes
quotes_to_post = quotes[-2:]

# 3. Load refresh token from file
with open("refresh_token.json", "r") as f:
    tokens = json.load(f)

REFRESH_TOKEN = tokens["refresh_token"]
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

# 4. Refresh access token automatically
def refresh_access_token():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
    }
    response = requests.post(TOKEN_URL, data=data)
    new_tokens = response.json()
    with open("refresh_token.json", "w") as f:
        json.dump(new_tokens, f)
    return new_tokens["access_token"]

ACCESS_TOKEN = refresh_access_token()

# 5. Post to Twitter
def post_tweet(text):
    url = "https://api.twitter.com/2/tweets"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {"text": text}
    r = requests.post(url, headers=headers, json=payload)
    print(r.json())

# Post two quotes
for quote in quotes_to_post:
    post_tweet(quote.strip())
    time.sleep(5)  # wait 5 sec between posts
