# -----------------------------
# app.py - Robust version
# -----------------------------
import os
import pickle
import requests
import pandas as pd
import streamlit as st
from time import sleep

# -----------------------------
# Streamlit Page Config (FIRST LINE)
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎬", layout="wide")

# -----------------------------
# Direct download URLs
# -----------------------------
MOVIES_URL = "https://drive.google.com/uc?export=download&id=1Kay7X8C98PwQxjhwyxdF-SUkBOR2ro_y"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1k3O-XxbFQYTUl2qsWxQQSdEl0roVDDTk"
MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# -----------------------------
# Safe download function with retries
# -----------------------------
def download_file(url, path, retries=3, delay=2):
    temp_path = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Status {response.status_code}")

            # Peek first 1024 bytes to check for HTML (Dropbox page)
            first_chunk = next(response.iter_content(chunk_size=1024))
            if b"<html" in first_chunk.lower():
                raise Exception("Downloaded content is HTML, not a pickle file!")

            with open(temp_path, "wb") as f:
                f.write(first_chunk)
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            os.replace(temp_path, path)
            return

        except Exception as e:
            if attempt < retries:
                sleep(delay)
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise Exception(f"Download failed after {retries} attempts: {e}")

# -----------------------------
# Ensure files exist
# -----------------------------
def ensure_file(url, path, min_size=1000):
    if not os.path.exists(path) or os.path.getsize(path) < min_size:
        st.warning(f"Downloading {os.path.basename(path)}...")
        try:
            download_file(url, path)
        except Exception as e:
            st.error(f"Failed to download {os.path.basename(path)}: {e}")
            st.stop()

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
# TMDB poster fetch with caching and retries
# -----------------------------
TMDB_API_KEY = "932d141e2fbedef6027ab4ec139490ea"

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    if not movie_id:
        return "https://via.placeholder.com/200x300.png?text=No+Image"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    retries = 3
    for attempt in range(retries):
        try:
            data = requests.get(url, timeout=5).json()
            poster_path = data.get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
            return "https://via.placeholder.com/200x300.png?text=No+Image"
        except:
            sleep(1)
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
        recommended_posters.append(fetch_poster(movies_df.iloc[i].get('id', 0)))

    return recommended_movies, recommended_posters

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button("Recommend"):
    try:
        recommended_movies, recommended_posters = recommend(selected_movie, movies, similarity)
        if recommended_movies:
            cols = st.columns(5)
            for col, movie, poster in zip(cols, recommended_movies, recommended_posters):
                col.image(poster, width=200)
                col.caption(movie)
        else:
            st.info("No recommendations found.")
    except Exception as e:
        st.error(f"Failed to generate recommendations: {e}")