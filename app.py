import os
import pickle
import streamlit as st
import requests
import pandas as pd

# ---------------------------
# Streamlit page config MUST be first
# ---------------------------
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ---------------------------
# TMDB API Key
# ---------------------------
TMDB_API_KEY = "932d141e2fbedef6027ab4ec139490ea"  # Replace with your TMDB API Key

# ---------------------------
# Dropbox model URLs
# ---------------------------
MOVIES_URL = "https://www.dropbox.com/scl/fi/b8bkm6lrenxo69ibgqyeh/movie_list.pkl?rlkey=bbhk68qavhknq6lc7ny1up0mf&dl=1"
SIMILARITY_URL = "https://www.dropbox.com/scl/fi/aw3tx3yn2o7tyhquy96a0/similarity.pkl?rlkey=d48z31ze2plcjb99j1twshgif&dl=1"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# ---------------------------
# Download helper functions
# ---------------------------
def download_file(url, path):
    temp_path = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Download failed with status {response.status_code}")
    with open(temp_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    os.replace(temp_path, path)

def ensure_file(url, path):
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        st.warning(f"Downloading {os.path.basename(path)}...")
        try:
            download_file(url, path)
        except Exception as e:
            st.error(f"Failed to download {os.path.basename(path)}: {e}")
            st.stop()

# ---------------------------
# Ensure model files
# ---------------------------
ensure_file(MOVIES_URL, MOVIES_PATH)
ensure_file(SIMILARITY_URL, SIMILARITY_PATH)

# ---------------------------
# Load models safely
# ---------------------------
try:
    with open(MOVIES_PATH, "rb") as f:
        movies = pd.DataFrame(pickle.load(f))
    with open(SIMILARITY_PATH, "rb") as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Error loading model files: {e}")
    st.stop()

# ---------------------------
# TMDB Poster fetch with caching
# ---------------------------
@st.cache_data(show_spinner=False)
def fetch_poster(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    data = requests.get(url).json()
    results = data.get("results")
    if results:
        poster_path = results[0].get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

# ---------------------------
# Recommendation function
# ---------------------------
def recommend(movie_title, movies, similarity):
    if movie_title not in movies['title'].values:
        st.warning(f"Movie '{movie_title}' not found in database.")
        return [], []
    idx = movies[movies['title'] == movie_title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Top 10 recommendations
    recommended_movies = []
    recommended_posters = []
    for i, score in sim_scores:
        title = movies.iloc[i]['title']
        poster = fetch_poster(title)
        recommended_movies.append(title)
        recommended_posters.append(poster)
    return recommended_movies, recommended_posters

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("🎬 Movie Recommender System")
selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button("Recommend"):
    recommended_movies, recommended_posters = recommend(selected_movie, movies, similarity)
    if recommended_movies:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if idx < len(recommended_movies):
                with col:
                    st.text(recommended_movies[idx])
                    if recommended_posters[idx]:
                        st.image(recommended_posters[idx], use_column_width=True)
                    else:
                        st.write("No poster found")