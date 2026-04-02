# wsgi.py
import sys
import os
from streamlit.web import cli as stcli

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8501))  # default fallback
    sys.argv = ["streamlit", "run", "app.py", f"--server.port={port}", "--server.address=0.0.0.0"]
    sys.exit(stcli.main())
    