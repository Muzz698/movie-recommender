# -----------------------------
# app.py - FINAL STABLE VERSION 🚀 (gdown fix)
# -----------------------------
import os
import pickle
import pandas as pd
import streamlit as st
import requests
import gdown

# -----------------------------
# Page Config (FIRST)
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎬", layout="wide")

# -----------------------------
# Google Drive FILE IDs
# -----------------------------
MOVIE_ID = "1Kay7X8C98PwQxjhwyxdF-SUkBOR2ro_y"
SIMILARITY_ID = "1k3O-XxbFQYTUl2qsWxQQSdEl0roVDDTk"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# -----------------------------
# Download using gdown (BEST METHOD)
# -----------------------------
def download_file(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    os.makedirs(os.path.dirname(output), exist_ok=True)
    gdown.download(url, output, quiet=False)

# -----------------------------
# Ensure files exist
# -----------------------------
def ensure_file(file_id, path):
    if not os.path.exists(path):
        st.warning(f"Downloading {os.path.basename(path)}...")
        try:
            download_file(file_id, path)
        except Exception as e:
            st.error(f"Download failed: {e}")
            st.stop()

# -----------------------------
# Download models
# -----------------------------
ensure_file(MOVIE_ID, MOVIES_PATH)
ensure_file(SIMILARITY_ID, SIMILARITY_PATH)

# -----------------------------
# Load models (cached)
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

