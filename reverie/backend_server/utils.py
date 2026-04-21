"""
utils.py — runtime configuration.

Two ways to supply your OpenAI API key:
  1. (recommended) Export it in your shell before launching:
       export OPENAI_API_KEY=sk-...
  2. Paste it into the string below, replacing <Your OpenAI API Key>.
     If you do this, be careful NOT to commit the change.
"""
import os

# === Fill in your key here, OR set OPENAI_API_KEY in the environment ===
openai_api_key = os.environ.get("OPENAI_API_KEY", "<Your OpenAI API Key>")
key_owner = os.environ.get("OPENAI_KEY_OWNER", "<Your Name>")
# =======================================================================

maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"

collision_block_id = "32125"

# Verbose
debug = True

if not openai_api_key or openai_api_key.startswith("<"):
  print("[utils] WARNING: OPENAI_API_KEY is not set. Either export it in "
        "your shell or edit reverie/backend_server/utils.py.")
