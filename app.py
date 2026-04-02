import os
import pickle
import streamlit as st
import requests
import pandas as pd

# ===============================
# CONFIG
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# Google Drive Direct Download Links
MOVIES_URL = "https://drive.google.com/uc?id=1Kay7X8C98PwQxjhwyxdF-SUkBOR2ro_y"
SIMILARITY_URL = "https://drive.google.com/uc?id=1k3O-XxbFQYTUl2qsWxQQSdEl0roVDDTk"


# ===============================
# DOWNLOAD FUNCTION
# ===============================
def download_file(url, path):
    try:
        r = requests.get(url, stream=True)
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        st.error(f"Download failed: {e}")
        st.stop()


# ===============================
# ENSURE MODEL FILES
# ===============================
os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.exists(MOVIES_PATH):
    with st.spinner("Downloading movie data..."):
        download_file(MOVIES_URL, MOVIES_PATH)

if not os.path.exists(SIMILARITY_PATH):
    with st.spinner("Downloading similarity matrix (first run only)..."):
        download_file(SIMILARITY_URL, SIMILARITY_PATH)


# ===============================
# LOAD DATA
# ===============================
try:
    movies = pd.DataFrame(pickle.load(open(MOVIES_PATH, "rb")))
    similarity = pickle.load(open(SIMILARITY_PATH, "rb"))
except Exception as e:
    st.error(f"Error loading model files: {e}")
    st.stop()


# ===============================
# POSTER FUNCTION
# ===============================
def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        return "https://via.placeholder.com/500x750?text=No+API+Key"

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        data = requests.get(url).json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path

        return "https://via.placeholder.com/500x750?text=No+Image"

    except:
        return "https://via.placeholder.com/500x750?text=Error"


# ===============================
# RECOMMEND FUNCTION
# ===============================
def recommend(movie):
    try:
        index = movies[movies["title"] == movie].index[0]
        distances = sorted(
            list(enumerate(similarity[index])),
            reverse=True,
            key=lambda x: x[1]
        )

        names = []
        posters = []

        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            names.append(movies.iloc[i[0]].title)
            posters.append(fetch_poster(movie_id))

        return names, posters

    except:
        return [], []


# ===============================
# UI
# ===============================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬")

st.title("🎬 Movie Recommender System")

movie_list = movies["title"].values
selected_movie = st.selectbox("Select a movie", movie_list)

if st.button("Recommend"):

    names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(5)

        for i in range(5):
            with cols[i]:
                st.image(posters[i])
                st.caption(names[i])
    else:
        st.warning("No recommendations found.")