import requests
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request

app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

#mood = input("What's your mood? (e.g., happy, sad, adventurous): ").lower()
#language = input("Preferred language? (e.g., en, nl, fr): ").lower()
#actor_name = input("Favorite actor? (optional): ").strip()
#release_year = input("Preferred release year? (optional): ").strip()
#min_rating = input("Preferred minimum rating: ")
#movie_type = input("What type of movie do you want? (e.g., anime, documentary, sci-fi): ").lower()

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
movie_type_filters = {
    "animation": {"genre": "16"},
    "documentary": {"genre": "99"},
    "sci-fi": {"genre": "878"},
    "fantasy": {"genre": "14"},
    "tv movie": {"genre": "10770"},
    "anime": {"genre": "16", "keyword": "210024"},  # Anime is a subset of animation
    "crime": {"genre": "80"},
    "horror": {"genre": "27"},
    "romance": {"genre": "10749"}
}

def get_genre_ids():
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    genres = response.json()["genres"]
    return {genre["name"].lower(): genre["id"] for genre in genres}

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

def build_query(mood, language, actor_name, min_rating, movie_type, release_year=None):
    genre_ids_map = get_genre_ids()
    genres = mood_to_genre.get(mood, [])
    genre_ids = [str(genre_ids_map[g]) for g in genres if g in genre_ids_map] 

    type_filter = movie_type_filters.get(movie_type.lower())
    if type_filter:
        if "genre" in type_filter:
            genre_ids.append(type_filter["genre"])
        if "keyword" in type_filter:
            params["with_keywords"] = type_filter["keyword"]

    actor_id = get_actor_id(actor_name)
    lang_code = format_language_code(language)

    params = {
        "api_key": API_KEY,
        "with_genres": "|".join(genre_ids),
        "language": lang_code,
        "with_original_language": "en",
        "sort_by": "popularity.desc",
        "page": 1
    }
    if release_year:
        params["primary_release_year"] = release_year
    if actor_id:
        params["with_cast"] = actor_id
    if min_rating:
        params["vote_average.gte"] = min_rating
    
    return params

def get_movies(params):
    url = "https://api.themoviedb.org/3/discover/movie"
    response = requests.get(url, params=params)
    results = response.json().get("results", [])
    movies = []
    for movie in results[:5]:
        movies.append(f"{movie['title']} ({movie['release_date']})\nOverview: {movie['overview']}\n")
    if not results:
        return "No matches found for that combo. Want to loosen the filters or try a different mood?"
    return "\n".join(movies)

#params = build_query(mood, language, actor_name, min_rating, movie_type, release_year)
#get_movies(params)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
@app.route("/filters", methods=["POST"])
def filter():
    results = None
    if request.method == "POST":
        mood = request.form.get('mood')
        language = request.form.get('language')
        actor = request.form.get('actor')
        year = request.form.get('year')
        rating = request.form.get('rating')
        movie_type = request.form.get('type')

        params = build_query(mood, language, actor, rating, movie_type, year)
        results = get_movies(params)
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)