import os
from pathlib import Path

# === BASE DIRECTORIES ===
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

SONGS_DIR = ASSETS_DIR / "songs"
SOUNDS_DIR = ASSETS_DIR / "sounds"
BEATMAPS_DIR = ASSETS_DIR / "beatmaps"
IMAGES_DIR = ASSETS_DIR / "images"

# Create directories if they don't exist
for folder in (SONGS_DIR, SOUNDS_DIR, BEATMAPS_DIR, IMAGES_DIR):
    os.makedirs(folder, exist_ok=True)

# === GAME DISPLAY ===
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# === GAMEPLAY CONFIG ===
EDITOR_NOTE_RADIUS = 10
BEATMAP_VERSION = 1
NOTE_SPEED = 200  # pixels per second

# === PATH DEBUG ===
print("[CONFIG] Asset paths loaded:")
print("  Songs:", SONGS_DIR)
print("  Beatmaps:", BEATMAPS_DIR)
print("  Sounds:", SOUNDS_DIR)
print("  Images:", IMAGES_DIR)
