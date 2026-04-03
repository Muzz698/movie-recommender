# -----------------------------
# app.py - OPTIMIZED VERSION 🚀
# -----------------------------
import os
import pickle
import pandas as pd
import streamlit as st
import requests
import gdown

# -----------------------------
# PAGE CONFIG (FIRST)
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎬", layout="wide")

# -----------------------------
# GOOGLE DRIVE LINKS
# -----------------------------
MOVIES_URL = "https://drive.google.com/uc?id=1Kay7X8C98PwQxjhwyxdF-SUkBOR2ro_y"
RECOMMEND_URL = "https://drive.google.com/uc?id=1sFzHHBwEFnw7ZoE3VMFYNSgt5AE1PxAo"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
RECOMMEND_PATH = os.path.join(MODEL_DIR, "recommendations.pkl")

# -----------------------------
# DOWNLOAD FUNCTION
# -----------------------------
def download_file(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        gdown.download(url, path, quiet=False)
    except Exception as e:
        raise Exception(f"Download failed: {e}")

def ensure_file(url, path):
    if not os.path.exists(path):
        st.warning(f"Downloading {os.path.basename(path)}...")
        try:
            download_file(url, path)
        except Exception as e:
            st.error(e)
            st.stop()

# -----------------------------
# DOWNLOAD MODELS
# -----------------------------
ensure_file(MOVIES_URL, MOVIES_PATH)
ensure_file(RECOMMEND_URL, RECOMMEND_PATH)

# -----------------------------
# LOAD MODELS (CACHED)
# -----------------------------
@st.cache_resource
def load_models():
    with open(MOVIES_PATH, "rb") as f:
        movies = pd.DataFrame(pickle.load(f))

    with open(RECOMMEND_PATH, "rb") as f:
        recommendations = pickle.load(f)

    return movies, recommendations

with st.spinner("Loading models... ⏳"):
    movies, recommendations = load_models()

# -----------------------------
# TMDB API
# -----------------------------
TMDB_API_KEY = "932d141e2fbedef6027ab4ec139490ea"  # ⚠️ Replace this

@st.cache_data(show_spinner=False)
def fetch_poster(movie_name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        data = requests.get(url).json()

        results = data.get("results")
        if results and len(results) > 0:
            poster_path = results[0].get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
    except:
        pass

    return "https://via.placeholder.com/200x300.png?text=No+Poster"

# -----------------------------
# RECOMMEND FUNCTION (NEW)
# -----------------------------
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    idx = movies[movies['title'] == movie].index[0]

    recommended_indices = recommendations[idx]

    names = []
    posters = []

    for i in recommended_indices:
        movie_row = movies.iloc[i]
        names.append(movie_row['title'])
        posters.append(fetch_poster(movie_row['title']))

    return names, posters

# -----------------------------
# UI
# -----------------------------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    if not names:
        st.info("No recommendations found.")
    else:
        cols = st.columns(5)
        for col, name, poster in zip(cols, names, posters):
            col.image(poster)
            col.caption(name)