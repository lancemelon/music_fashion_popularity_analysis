import os
from dotenv import load_dotenv
import requests
from collections import Counter
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = os.getenv("LASTFM_BASE_URL")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

def get_album_info(track_id: str):
    """
    Fetch album information for a track from the Spotify API.
    
    Args:
        track_id (str): The Spotify track ID.
        
    Returns:
        dict: Track info with a list of genres/tags.
        'track_name': track['name'],
        'album_type': album_type,
        'album_name': album_name,
        'release_date': release_date
    """
    if not track_id:
        raise ValueError("A valid Spotify track ID must be provided.")

    track = sp.track(track_id) 
    
    album = track['album']
    album_type = album['album_type'] 
    album_name = album['name']
    release_date = album['release_date']
    
    return {
        'track_name': track['name'],
        'album_type': album_type,
        'album_name': album_name,
        'release_date': release_date
    }

def get_track_genres(track_name: str, *artists: str, limit: int = 5):
    """
    Fetch genres (tags) for a track from the Last.fm API.
    
    Args:
        track_name (str): The name of the track.
        *artists (str): One or more artist names.
        limit (int): How many genre tags to return (default = 5).
        
    Returns:
        dict: Track info with a list of genres/tags.
        "track": data["track"]["name"],
        "artist": artist_name,
        "genres": genres        
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
        dict: Merged artist info with a list of top genres/tags.
        "artists": artist_names,
        "genres": top_genres
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