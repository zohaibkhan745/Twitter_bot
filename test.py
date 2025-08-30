import requests

# Replace with the access token you got
ACCESS_TOKEN = "QU82NHdQbURHZ0hkZGFrYTR3enRFdndGMWVtdlZYQ09hakRoY2h2VE94SWU3OjE3NTY1NDY4ODkzMTU6MTowOmF0OjE"

# The tweet text you want to post
tweet_text = "Hello world! 🚀 This is my second automated post."

# Endpoint for posting tweets
url = "https://api.x.com/2/tweets"

# Headers with authorization
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Data to send
payload = {
    "text": tweet_text
}

# Make POST request
response = requests.post(url, headers=headers, json=payload)

# Print result
print("Status code:", response.status_code)
print("Response:", response.json())
