# -----------------------------
# app.py - FINAL STABLE 🚀
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
# GOOGLE DRIVE DIRECT LINKS
# -----------------------------
MOVIES_URL = "https://drive.google.com/uc?id=1Kay7X8C98PwQxjhwyxdF-SUkBOR2ro_y"
SIMILARITY_URL = "https://drive.google.com/uc?id=1k3O-XxbFQYTUl2qsWxQQSdEl0roVDDTk"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# -----------------------------
# DOWNLOAD FUNCTION (gdown)
# -----------------------------
def download_file(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        gdown.download(url, path, quiet=False)
    except Exception as e:
        raise Exception(f"Download failed: {e}")

# -----------------------------
# ENSURE FILE EXISTS
# -----------------------------
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
ensure_file(SIMILARITY_URL, SIMILARITY_PATH)

# -----------------------------
# LOAD MODELS
# -----------------------------
try:
    with open(MOVIES_PATH, "rb") as f:
        movies = pd.DataFrame(pickle.load(f))

    with open(SIMILARITY_PATH, "rb") as f:
        similarity = pickle.load(f)

except Exception as e:
    st.error(f"Model loading failed: {e}")
    st.stop()

# -----------------------------
# TMDB API
# -----------------------------
TMDB_API_KEY = "YOUR_API_KEY_HERE"

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
# RECOMMEND FUNCTION
# -----------------------------
def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]

    movie_list = sorted(list(enumerate(distances)),
                        reverse=True,
                        key=lambda x: x[1])[1:6]

    names = []
    posters = []

    for i in movie_list:
        movie_row = movies.iloc[i[0]]
        names.append(movie_row['title'])

        movie_id = movie_row.get('id', 0)
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