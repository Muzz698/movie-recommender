import os
import pickle
import streamlit as st
import requests
import pandas as pd

# ---------------------------
# Base paths
# ---------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))

movies_path = os.path.join(base_dir, 'models', 'movie_list.pkl')  # ensure folder is 'models'
similarity_path = os.path.join(base_dir, 'models', 'similarity.pkl')

# ---------------------------
# Load pickle files
# ---------------------------
try:
    movies = pd.DataFrame(pickle.load(open(movies_path, 'rb')))
    similarity = pickle.load(open(similarity_path, 'rb'))
except Exception as e:
    st.error(f"Failed to load model files: {e}")
    st.stop()

# ---------------------------
# TMDB Poster Fetch
# ---------------------------
def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY")  # get API key from environment variable
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

# ---------------------------
# Recommendation function
# ---------------------------
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

        recommended_movie_names = []
        recommended_movie_posters = []

        for i in distances[1:6]:  # top 5 recommendations
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_names.append(movies.iloc[i[0]].title)
            recommended_movie_posters.append(fetch_poster(movie_id))

        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        st.warning("Movie not found!")
        return [], []

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title('🎬 Movie Recommender System')

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie)
    if names:
        cols = st.columns(len(names))
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.image(poster)
                st.caption(name)
    else:
        st.info("No recommendations found.")