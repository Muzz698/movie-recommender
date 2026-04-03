import os
import pickle
import requests
import pandas as pd
import streamlit as st

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# Replace with your TMDB API key
TMDB_API_KEY = "YOUR_API_KEY_HERE"

# Dropbox direct links for models
MOVIES_URL = "https://www.dropbox.com/scl/fi/b8bkm6lrenxo69ibgqyeh/movie_list.pkl?rlkey=bbhk68qavhknq6lc7ny1up0mf&dl=1"
SIMILARITY_URL = "https://www.dropbox.com/scl/fi/aw3tx3yn2o7tyhquy96a0/similarity.pkl?rlkey=d48z31ze2plcjb99j1twshgif&dl=1"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def download_file(url, path):
    """Download a file from a URL safely."""
    temp_path = path + ".tmp"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(8192):
                if chunk:
                    f.write(chunk)
        os.replace(temp_path, path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise Exception(f"Download error: {e}")

def ensure_file(url, path):
    """Ensure the file exists, else download it."""
    if not os.path.exists(path) or os.path.getsize(path) < 1000000:
        download_file(url, path)

@st.cache_resource
def load_models():
    """Load movie list and similarity matrix safely."""
    ensure_file(MOVIES_URL, MOVIES_PATH)
    ensure_file(SIMILARITY_URL, SIMILARITY_PATH)
    with open(MOVIES_PATH, "rb") as f:
        movies = pd.DataFrame(pickle.load(f))
    with open(SIMILARITY_PATH, "rb") as f:
        similarity = pickle.load(f)
    return movies, similarity

def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get("poster_path")
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

def recommend(movie_name, movies, similarity, top_n=5):
    """Return top_n recommended movies with posters."""
    if movie_name not in movies['title'].values:
        return [], []
    idx = movies[movies['title'] == movie_name].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recommended_movies = []
    recommended_posters = []
    for i, _ in sim_scores:
        recommended_movies.append(movies.iloc[i]['title'])
        poster = fetch_poster(movies.iloc[i]['id'])
        recommended_posters.append(poster)
    return recommended_movies, recommended_posters

# ---------------------------
# MAIN APP
# ---------------------------
with st.spinner("Loading recommendation system... ⏳"):
    try:
        movies, similarity = load_models()
    except Exception as e:
        st.error(f"Error loading model files: {e}")
        st.stop()

st.title("🎬 Movie Recommender System")

movie_list = movies['title'].values
selected_movie = st.selectbox("Select a movie:", movie_list)

if st.button("Show Recommendations"):
    recommended_movies, recommended_posters = recommend(selected_movie, movies, similarity)

    if recommended_movies:
        cols = st.columns(len(recommended_movies))
        for col, movie, poster in zip(cols, recommended_movies, recommended_posters):
            with col:
                st.image(poster if poster else "https://via.placeholder.com/150", width=150)
                st.caption(movie)
    else:
        st.info("No recommendations found.")