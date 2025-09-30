import requests, os
from dotenv import load_dotenv
from flask import Flask, redirect, request, session
import numpy as np
import math

load_dotenv()
app = Flask(__name__)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
app.secret_key = CLIENT_SECRET

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

    session["access_token"] = access_token

    headers = {"Authorization": f"Bearer {access_token}"}
    test = requests.get("https://api.spotify.com/v1/me", headers=headers)

    return f"<pre>{test.json()}</pre>"

@app.route("/top-tracks")
def top_tracks():
    access_token = session.get("access_token")
    if not access_token:
        return "Something went wrong when using access token"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": 10,
        "time_range": "short_term"
    }

    response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers, params=params)
    data = response.json()

    #Display track names and artists

    output = ""
    for track in data.get("items", []):
        name = track["name"]
        artist = track["artists"][0]["name"]
        output += f"{name} by {artist}\n"
    return f"<pre>{output}</pre>"

@app.route("/recommendations")
def recommendations():
    access_token = session.get("access_token").strip()
    if not access_token:
        return "Something went wrong when using access token"
    
    params = {"limit": 10, "time_range": "short_term"}
    user_headers = {"Authorization": f"Bearer {access_token}"}
    print("Access token:", access_token)
    
    top_response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=user_headers, params=params)
    top_data = top_response.json()

    ids = [track["id"] for track in top_data.get("items", [])]
    if not ids:
        return "<pre>No top tracks found. Cannot generate recommendations.</pre>"

    ids_str = ",".join(ids)
    audio_response = requests.get(f"https://api.spotify.com/v1/audio-features?ids={ids_str}", headers=user_headers)
    audio_data = audio_response.json()
    print("Audio features raw:", audio_data)
    print("Seed ids:", ids_str)

    features = audio_data.get("audio_features", [])
    clean_features = [f for f in features if f is not None]

    if not clean_features:
        return "<pre>No audio features found.</pre>"
    
    energy = np.mean([track["energy"] for track in clean_features])
    valence = np.mean([track["valence"] for track in clean_features])
    tempo = np.mean([track["tempo"] for track in clean_features])

    user_profile = {
        "energy": round(float(energy), 3),
        "valence": round(float(valence), 3),
        "tempo": round(float(tempo), 1)
    }

    print("User profile vector:", user_profile)

    return f"<pre>User profile: {user_profile}</pre>"

def get_feel(track):
    return {
        "energy": round(track["energy"], 1),
        "valence": round(track["valence"], 1),
        "tempo": round(track["tempo"]/10) * 10
    }

if __name__ == "__main__":
    app.run(port=5000)
    