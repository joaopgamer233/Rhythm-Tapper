import json
from pathlib import Path
from config import BEATMAPS_DIR, SONGS_DIR

def list_audio_files():
    """
    Recursively find all audio files inside assets/songs,
    including subfolders (e.g., artist or project folders).
    """
    exts = (".ogg", ".wav", ".mp3", ".m4a")
    all_songs = []
    for path in SONGS_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in exts:
            all_songs.append(path)
    return sorted(all_songs)

def load_beatmap(path: Path):
    """Load a beatmap safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load beatmap: {e}")
        return {"version": 1, "notes": []}

def save_beatmap(path: Path, data):
    """Save beatmap as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
