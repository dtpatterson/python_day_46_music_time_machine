import os

from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# CONST VARIABLES
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
USERNAME = os.environ["USERNAME"]
SPOTIPY_SCOPE = "playlist-modify-private"
REDIRECT_URL="http://example.com"

# ASK FOR TIME INPUT
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

# SCRAPING BILLBOARD FOR THE SONG LIST AND ARTIST OF TIME INPUT
response = requests.get("https://www.billboard.com/charts/hot-100/" + date)

soup = BeautifulSoup(response.text, 'html.parser')
song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]

# GET TOKEN FOR AUTH SPOTIFY
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=SPOTIPY_SCOPE,
        redirect_uri=REDIRECT_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
        username=USERNAME,
    )
)
user_id = sp.current_user()["id"]

# REQUEST SPOTIFY FOR SONG URIs
song_uris = []
year = date.split("-")[0]
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# CREATE NEW PLAYLIST / ADD SONGS TO PLAYLIST
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)