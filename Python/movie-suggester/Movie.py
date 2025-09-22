import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

#mood = input("What's your mood? (e.g., happy, sad, adventurous): ").lower()
#language = input("Preferred language? (e.g., en, nl, fr): ").lower()
#actor_name = input("Favorite actor? (optional): ").strip()
#year = input("Preferred release year? (optional): ").strip()

mood_to_genre = {
    "happy": ["comedy", "romance", "animation", "music"],
    "sad": ["drama", "history", "war"],
    "adventurous": ["action", "adventure", "thriller", "science fiction"],
    "curious": ["mystery", "documentary", "history"],
    "thoughtful": ["drama", "documentary", "mystery"],
    "nostalgic": ["family", "tv movie", "romance"],
    "energetic": ["action", "music", "adventure"],
    "romantic": ["romance", "comedy", "drama"],
    "scared": ["horror", "thriller"],
    "escapist": ["fantasy", "science fiction", "western"],
    "reflective": ["war", "history", "documentary"],
    "lighthearted": ["comedy", "animation", "family"],
    "dark": ["crime", "thriller", "horror"]
}

def get_genre_ids():
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    genres = response.json()["genres"]
    return {genre["name"].lower(): genre["id"] for genre in genres}

#genre_ids = get_genre_ids()
#print(genre_ids)

def get_actor_id(name):
    if not name: 
        return None
    url = "https://api.themoviedb.org/3/search/person"
    params = {"api_key": API_KEY, "query": name}
    response = requests.get(url, params=params)
    results = response.json().get("results", [])
    return results[0]["id"] if results else None
#actor_name = input("Enter an actor's name to test: ").strip()
#actor_id = get_actor_id(actor_name)

#if actor_id:
    #print(f"Actor ID for '{actor_name}': {actor_id}")
#else:
#    print("Actor not found")
def format_language_code(code):
    return f"{code}-US" if code else "en-US"