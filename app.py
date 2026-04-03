# -----------------------------
# app.py - Production-ready
# -----------------------------

import os
import pickle
import requests
import pandas as pd
import streamlit as st

# -----------------------------
# Streamlit Page Config (FIRST LINE)
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎬", layout="wide")

# -----------------------------
# Dropbox Direct Links (dl=1 for direct download)
# -----------------------------
MOVIES_URL = "https://www.dropbox.com/s/b8bkm6lrenxo69ibgqyeh/movie_list.pkl?dl=1"
SIMILARITY_URL = "https://www.dropbox.com/s/aw3tx3yn2o7tyhquy96a0/similarity.pkl?dl=1"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# -----------------------------
# Safe download function (checks for HTML)
# -----------------------------
def download_file(url, path):
    temp_path = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Download failed with status {response.status_code}")

        # Read first chunk to check for HTML
        first_chunk = next(response.iter_content(chunk_size=15))
        if b"<html" in first_chunk.lower():
            raise Exception("Downloaded content is HTML, not a pickle file. Check URL!")

        # Write the first chunk + remaining
        with open(temp_path, "wb") as f:
            f.write(first_chunk)
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        os.replace(temp_path, path)

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise Exception(f"Download error: {e}")

# -----------------------------
# Ensure models exist
# -----------------------------
def ensure_file(url, path, min_size=1000000):
    if not os.path.exists(path) or os.path.getsize(path) < min_size:
        st.warning(f"Downloading {os.path.basename(path)}...")
        try:
            download_file(url, path)
        except Exception as e:
            st.error(f"Failed to download {os.path.basename(path)}: {e}")
            st.stop()

# -----------------------------
# Download models if missing
# -----------------------------
ensure_file(MOVIES_URL, MOVIES_PATH)
ensure_file(SIMILARITY_URL, SIMILARITY_PATH)

# -----------------------------
# Load models safely
# -----------------------------
try:
    with open(MOVIES_PATH, "rb") as f:
        movies = pd.DataFrame(pickle.load(f))

    with open(SIMILARITY_PATH, "rb") as f:
        similarity = pickle.load(f)

except Exception as e:
    st.error(f"Model files corrupted: {e}")
    st.stop()

# -----------------------------
# TMDB Poster Fetch
# -----------------------------
TMDB_API_KEY = "932d141e2fbedef6027ab4ec139490ea"  # <-- Replace with your key

def fetch_poster(movie_id):
    if movie_id == 0:
        return "https://via.placeholder.com/200x300.png?text=No+Image"
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        return "https://via.placeholder.com/200x300.png?text=No+Image"
    except:
        return "https://via.placeholder.com/200x300.png?text=No+Image"

# -----------------------------
# Recommendation function
# -----------------------------
def recommend(movie_name, movies_df, similarity_matrix):
    if movie_name not in movies_df['title'].values:
        return [], []

    idx = movies_df[movies_df['title'] == movie_name].index[0]
    scores = list(enumerate(similarity_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]

    recommended_movies = []
    recommended_posters = []

    for i, _ in scores:
        recommended_movies.append(movies_df.iloc[i]['title'])
        poster = fetch_poster(movies_df.iloc[i].get('id', 0))  # safe fallback
        recommended_posters.append(poster)
    return recommended_movies, recommended_posters

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎬 Movie Recommender System")
selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button("Recommend"):
    recommended_movies, recommended_posters = recommend(selected_movie, movies, similarity)
    if recommended_movies:
        cols = st.columns(5)
        for col, movie, poster in zip(cols, recommended_movies, recommended_posters):
            col.image(poster, width=200)
            col.caption(movie)
    else:
        st.info("No recommendations found.")