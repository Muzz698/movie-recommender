import streamlit as st
import pickle
import requests
import os

# ------------------------------
# Helper functions
# ------------------------------
def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API."""
    api_key = "8265bd1679663a7ea12ac168da84d2e8"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get("poster_path")
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

def recommend(movie):
    """Return 5 recommended movies and their posters."""
    if movie not in movie_titles:
        return [], []

    index = movie_titles.index(movie)
    distances = list(enumerate(similarity[index]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in distances:
        movie_id = movies_data[i[0]]['id']
        recommended_movies.append(movies_data[i[0]]['title'])
        recommended_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_posters

# ------------------------------
# Load models safely
# ------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_path = os.path.join(BASE_DIR, "models", "movie_list.pkl")
similarity_path = os.path.join(BASE_DIR, "models", "similarity.pkl")

# Check if model files exist
if not os.path.exists(movies_path) or not os.path.exists(similarity_path):
    st.error("Model files not found. Ensure 'models/movie_list.pkl' and 'models/similarity.pkl' exist.")
    st.stop()

with open(movies_path, "rb") as f:
    movies_data = pickle.load(f)

with open(similarity_path, "rb") as f:
    similarity = pickle.load(f)

# Extract movie titles
movie_titles = [movie['title'] for movie in movies_data]

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a movie:", movie_titles)

if st.button("Show Recommendations"):
    recommended_movies, recommended_posters = recommend(selected_movie)
    
    if recommended_movies:
        cols = st.columns(5)
        for col, name, poster in zip(cols, recommended_movies, recommended_posters):
            col.text(name)
            if poster:
                col.image(poster)
            else:
                col.write("Poster not available")
    else:
        st.warning("No recommendations found for this movie.")