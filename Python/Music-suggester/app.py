import csv
import librosa
import os
import numpy as np
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import ast

app = Flask(__name__)
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'tracks.csv')
#uploaded_file = os.path.join(base_dir, 'uploaded.mp3')
upload_folder = 'uploads'
app.config['upload_folder'] = upload_folder
min_max = {
    'tempo': [float('inf'), float('-inf')],
    'energy': [float('inf'), float('-inf')],
    'valence': [float('inf'), float('-inf')],
    'danceability': [float('inf'), float('-inf')],
    'instrumentalness': [float('inf'), float('-inf')]
}

with open(csv_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    track_pool = []
    for row in reader:
        for feature in min_max:
            try:
                value = float(row[feature])
                if value > 0:  
                    if value < min_max[feature][0]:
                        min_max[feature][0] = value
                    if value > min_max[feature][1]:
                        min_max[feature][1] = value
            except:
                pass


for feature, (min_val, max_val) in min_max.items():

        feature_ranges = {
        'tempo': (30.51, 246.38),
        'energy': (0.0, 1.0),
        'valence': (0.0, 1.0),
        'danceability': (0.05, 0.99),
        'instrumentalness': (0.0, 1.0)
        }

        def normalize(value, min_val, max_val):
            return (value - min_val) / (max_val - min_val)
        
        artists_raw = row['artists']
        try:
            artists_list = ast.literal_eval(artists_raw)
            artists = ', '.join(artists_list)
        except:
            artists = artists_raw

        track_pool.append({
            'name': row['name'],
            'artist': artists,
            'tempo': float(row['tempo']),
            'energy': float(row['energy']),
            'valence': float(row['valence']),
            'danceability': float(row['danceability']),
            'key': row['key'],
            'instrumentalness': float(row['instrumentalness'])
        })

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)
    tempo = librosa.beat.tempo(y=y, sr=sr)[0]
    energy = librosa.feature.rms(y=y).mean()
    valence = librosa.feature.spectral_centroid(y=y, sr=sr).mean() / sr # proxy for brightness
    danceability = librosa.feature.zero_crossing_rate(y).mean() # rough proxy
    harmonic = librosa.effects.harmonic(y)
    percussive = librosa.effects.percussive(y)
    harmonic_energy = np.mean(np.abs(harmonic))
    percussive_energy = np.mean(np.abs(percussive))

    # Instrumentalness proxy: more harmonic, less percussive = more instrumental
    instrumentalness = harmonic_energy / (harmonic_energy + percussive_energy)

    return {
        'tempo': round(tempo),
        'energy': round(float(energy), 2),
        'valence': round(float(valence), 2),
        'danceability': round(float(danceability), 2),
        'instrumentalness': round(float(instrumentalness), 2),
        'harmonic_energy': round(float(harmonic_energy), 2),
        'percussive_energy': round(float(percussive_energy), 2)
    }

def match_score(user, candidate):

    diffs = []
    for feature in ['tempo', 'energy', 'valence', 'danceability', 'instrumentalness']:
        diffs.append(abs(user[feature] - candidate[feature]))
    score = 1 - (sum(diffs) / len(diffs))  # average similarity
    return round(score * 100, 2)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['track']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['upload_folder'], filename)
        file.save(filepath)

        user_features = extract_features(filepath)
        user_norm = {}
        for feature in feature_ranges:
            user_norm[feature] = normalize(user_features[feature], *feature_ranges[feature])

        # Score all tracks

        scored_tracks = []
        for track in track_pool:
            candidate_norm = {}
            for feature in feature_ranges:
                candidate_norm[feature] = normalize(track[feature], *feature_ranges[feature])
            score = match_score(user_norm, candidate_norm)
            scored_tracks.append((track['name'], round(score, 2), track['artist']))

            # Sort by score descending
        scored_tracks.sort(key=lambda x: x[1], reverse=True)
        top_matches = scored_tracks[:5]

        return render_template('index.html', matches=top_matches)
    return render_template('index.html', matches=None)

if __name__ == '__main__':
    os.makedirs(upload_folder, exist_ok=True)
    app.run(debug=True)