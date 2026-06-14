# ============================================================
#  server.py  —  Smart Path Suggestor Modular App Wrapper
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.server import start_server

if __name__ == "__main__":
    start_server()
