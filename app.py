# -----------------------------
# app.py - FINAL STABLE VERSION 🚀
# -----------------------------
import os
import pickle
import requests
import pandas as pd
import streamlit as st

# -----------------------------
# Page Config (FIRST)
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎬", layout="wide")

# -----------------------------
# Direct Download URLs (Google Drive)
# -----------------------------
MOVIES_URL = "https://drive.google.com/uc?export=download&id=1Kay7X8C98PwQxjhwyxdF-SUkBOR2ro_y"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1k3O-XxbFQYTUl2qsWxQQSdEl0roVDDTk"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# -----------------------------
# Robust Download Function (with retry + HTML check)
# -----------------------------
def download_file(url, path, retries=3):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True)

            if response.status_code != 200:
                raise Exception(f"Status code: {response.status_code}")

            first_chunk = next(response.iter_content(chunk_size=1024))

            # ❌ Detect HTML instead of pickle
            if b"<html" in first_chunk.lower():
                raise Exception("Downloaded HTML instead of file")

            temp_path = path + ".tmp"

            with open(temp_path, "wb") as f:
                f.write(first_chunk)
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            os.replace(temp_path, path)
            return

        except Exception as e:
            if attempt == retries - 1:
                raise Exception(f"Download failed after {retries} attempts: {e}")

# -----------------------------
# Ensure files exist
# -----------------------------
def ensure_file(url, path):
    if not os.path.exists(path) or os.path.getsize(path) < 1000000:
        st.warning(f"Downloading {os.path.basename(path)}...")
        try:
            download_file(url, path)
        except Exception as e:
            st.error(f"Failed to download {os.path.basename(path)}: {e}")
            st.stop()

# -----------------------------
# Download models
# -----------------------------
ensure_file(MOVIES_URL, MOVIES_PATH)
ensure_file(SIMILARITY_URL, SIMILARITY_PATH)

# -----------------------------
# Load models (cached for speed)
# -----------------------------
@st.cache_resource
def load_models():
    with open(MOVIES_PATH, "rb") as f:
        movies = pd.DataFrame(pickle.load(f))

    with open(SIMILARITY_PATH, "rb") as f:
        similarity = pickle.load(f)

    return movies, similarity

try:
    movies, similarity = load_models()
except Exception as e:
    st.error(f"Model loading failed: {e}")
    st.stop()

# -----------------------------
# TMDB API
# -----------------------------
TMDB_API_KEY = "932d141e2fbedef6027ab4ec139490ea"

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
        data = requests.get(url).json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path

    except:
        pass

    return "https://via.placeholder.com/200x300?text=No+Image"

# -----------------------------
# Recommendation function
# -----------------------------
def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []

    for i in movie_list:
        movie_row = movies.iloc[i[0]]

        names.append(movie_row['title'])

        movie_id = movie_row['id'] if 'id' in movie_row else 0
        posters.append(fetch_poster(movie_id))

    return names, posters

# -----------------------------
# UI
# -----------------------------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        col.image(poster)
        col.caption(name)