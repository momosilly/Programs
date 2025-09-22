import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

mood = input("What's your mood? (e.g., happy, sad, adventurous): ").lower()
language = input("Preferred language? (e.g., en, nl, fr): ").lower()
actor_name = input("Favorite actor? (optional): ").strip()
year = input("Preferred release year? (optional): ").strip()
min_rating = input("Preferred minimum rating: ")

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

def format_language_code(code):
    return f"{code}-US" if code else "en-US"

def build_query(mood, language, actor_name, min_rating):
    genre_ids_map = get_genre_ids()
    genres = mood_to_genre.get(mood, [])
    genre_ids = [str(genre_ids_map[g]) for g in genres if g in genre_ids_map] #!

    actor_id = get_actor_id(actor_name)
    lang_code = format_language_code(language)

    params = {
        "api_key": API_KEY,
        "with_genres": ",".join(genre_ids),
        "language": lang_code,
        "sort_by": "popularity.desc",
        "page": 1
    }

    if actor_id:
        params["with_cast"] = actor_id
    if min_rating:
        params["vote_average.gte"] = min_rating
    
    return params

def get_movies(params):
    url = "https://api.themoviedb.org/3/discover/movie"
    response = requests.get(url, params=params)
    results = response.json().get("results", [])
    for movie in results[:5]:
        print(f"{movie['title']} ({movie['release_date']})")
        print(f"Overview: {movie['overview']}\n")

params = build_query(mood, language, actor_name, min_rating)
get_movies(params)