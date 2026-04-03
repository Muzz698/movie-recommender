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
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

        # check size
        if total_size != 0 and downloaded < total_size:
            raise Exception("Download incomplete")

        os.rename(temp_path, path)

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

# ---------------------------
# Ensure models exist
# ---------------------------
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

def ensure_file(url, path):
    if not os.path.exists(path) or os.path.getsize(path) < 1000000:  # <1MB = broken
        st.warning(f"Downloading {os.path.basename(path)}...")
        download_file(url, path)

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
    st.stop()