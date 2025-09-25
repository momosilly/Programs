import requests, os
from dotenv import load_dotenv
from flask import Flask, redirect, request

load_dotenv()
app = Flask(__name__)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.route("/")
def login():
    scopes = "user-read-private user-top-read"
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scopes}"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    global access_token
    code = request.args.get("code")

    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(token_url, data=data)
    token_info = response.json()
    access_token = token_info.get("access_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    test = requests.get("https://api.spotify.com/v1/me", headers=headers)

    return f"<pre>{test.json()}</pre>"

@app.route("/top-tracks")
def top_tracks():
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": 10,
        "time_range": "short_term"
    }

    response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers, params=params)
    data = response.json()

    #Display track names and artists

    output = ""
    print("Top tracks response:", data)
    for track in data.get("items", []):
        name = track["name"]
        artist = track["artists"][0]["name"]
        output += f"{name} by {artist}\n"
    return f"<pre>{output}</pre>"

if __name__ == "__main__":
    app.run(port=5000)