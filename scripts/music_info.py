import os
from dotenv import load_dotenv
import requests
from collections import Counter

load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = os.getenv("LASTFM_BASE_URL")

def get_track_genres(track_name: str, *artists: str, limit: int = 5):
    """
    Fetch genres (tags) for a track from the Last.fm API.
    
    Args:
        track_name (str): The name of the track.
        *artists (str): One or more artist names.
        limit (int): How many genre tags to return (default = 5).
        
    Returns:
        dict: Track info with a list of genres/tags.
    """
    if not artists:
        raise ValueError("At least one artist name must be provided.")
    
    artist_name = artists[0]  
    
    params = {
        "method": "track.getInfo",
        "api_key": API_KEY,
        "artist": artist_name,
        "track": track_name,
        "format": "json"
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if "track" not in data:
        return {"error": "Track not found", "genres": []}

    tags = data["track"].get("toptags", {}).get("tag", [])
    genres = [tag["name"] for tag in tags[:limit]]
    
    return {
        "track": data["track"]["name"],
        "artist": artist_name,
        "genres": genres
    }

def get_artist_genres(*artist_names: str, limit: int = 5):
    """
    Fetch and merge top Last.fm tags (genres) for one or more artists,
    returning the most frequent tags overall.
    
    Args:
        *artist_names (str): One or more artist names.
        top_n (int): Number of top genres to return overall.
        
    Returns:
        dict: {
            "artists": tuple of artist names,
            "genres": list of top N genres overall
        }
    """
    if not artist_names:
        raise ValueError("At least one artist name must be provided.")
    
    all_tags = []

    for artist in artist_names:
        params = {
            "method": "artist.getTopTags",
            "artist": artist,
            "api_key": API_KEY,
            "format": "json"
        }

        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if "toptags" in data and "tag" in data["toptags"]:
            tags = data["toptags"]["tag"]
            all_tags.extend([tag["name"] for tag in tags])

    tag_counts = Counter(all_tags)
    top_genres = [tag for tag, _ in tag_counts.most_common(limit)]

    return {
        "artists": artist_names,
        "genres": top_genres
    }