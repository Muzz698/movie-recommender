import os
import pickle
import streamlit as st
import requests
import pandas as pd

# ---------------------------
# Dropbox Direct Links
# ---------------------------
MOVIES_URL = "https://www.dropbox.com/scl/fi/b8bkm6lrenxo69ibgqyeh/movie_list.pkl?rlkey=bbhk68qavhknq6lc7ny1up0mf&dl=1"
SIMILARITY_URL = "https://www.dropbox.com/scl/fi/aw3tx3yn2o7tyhquy96a0/similarity.pkl?rlkey=d48z31ze2plcjb99j1twshgif&dl=1"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# ---------------------------
# Safe download function
# ---------------------------
def download_file(url, path):
    temp_path = path + ".tmp"

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        response = requests.get(url, stream=True)

        if response.status_code != 200:
            raise Exception(f"Download failed with status {response.status_code}")

        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Check file exists before rename
        if not os.path.exists(temp_path):
            raise Exception("Temporary file not created")

        # Rename safely
        os.replace(temp_path, path)

    except Exception as e:
        # Cleanup temp file if exists
        if os.path.exists(temp_path):
            os.remove(temp_path)

        raise Exception(f"Download error: {e}")

# ---------------------------
# Ensure models exist
# ---------------------------
def ensure_file(url, path):
    if not os.path.exists(path) or os.path.getsize(path) < 1000000:
        st.warning(f"Downloading {os.path.basename(path)}...")

        try:
            download_file(url, path)
        except Exception as e:
            st.error(f"Failed to download {os.path.basename(path)}: {e}")
            st.stop()
# Download if needed
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
    st.error("Model files corrupted. Please refresh.")
    st.stop()import os
import pickle
import streamlit as st
import requests
import pandas as pd

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬")

MOVIES_URL = "https://www.dropbox.com/scl/fi/b8bkm6lrenxo69ibgqyeh/movie_list.pkl?rlkey=bbhk68qavhknq6lc7ny1up0mf&dl=1"
SIMILARITY_URL = "https://www.dropbox.com/scl/fi/aw3tx3yn2o7tyhquy96a0/similarity.pkl?rlkey=d48z31ze2plcjb99j1twshgif&dl=1"

MODEL_DIR = "models"
MOVIES_PATH = os.path.join(MODEL_DIR, "movie_list.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity.pkl")

# ---------------------------
# SAFE DOWNLOAD
# ---------------------------
def download_file(url, path):
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

        if not os.path.exists(temp_path):
            raise Exception("Temp file not created")

        os.replace(temp_path, path)

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise Exception(e)

# ---------------------------
# ENSURE FILE
# ---------------------------
def ensure_file(url, path):
    if not os.path.exists(path) or os.path.getsize(path) < 1000000:
        download_file(url, path)

# ---------------------------
# LOAD MODELS (CACHED)
# ---------------------------
@st.cache_resource
def load_models():
    ensure_file(MOVIES_URL, MOVIES_PATH)
    ensure_file(SIMILARITY_URL, SIMILARITY_PATH)

    with open(MOVIES_PATH, "rb") as f:
        movies = pd.DataFrame(pickle.load(f))

    with open(SIMILARITY_PATH, "rb") as f:
        similarity = pickle.load(f)

    return movies, similarity

# ---------------------------
# LOAD WITH SPINNER
# ---------------------------
with st.spinner("Loading recommendation system... ⏳"):
    try:
        movies, similarity = load_models()
    except Exception as e:
        st.error(f"Error loading model files: {e}")
        st.stop()