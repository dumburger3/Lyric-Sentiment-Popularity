import billboard
import lyricsgenius
import pandas as pd
import numpy as np
import time
import os
import re
from dotenv import load_dotenv

load_dotenv()

GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

# Creates a Genius object to interact wppyith the Genius API
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, timeout=10, retries=3, skip_non_songs=True, remove_section_headers=True)

# Fetches the current Billboard Hot 100 chart
chart = billboard.ChartData('hot-100')

songs_data = []

# Since Billboard artist names can be inconsistent, we change them to the format used by Genius (X and With and And becomes &)
def clean_artist(artist):
    artist = re.sub(r"\s+x\s+|\s+with\s+", " & ", artist, flags=re.IGNORECASE)
    artist = re.sub(r"\s+and\s+", " & ", artist)
    artist = artist.strip()
    return artist


for song in chart:    
    title = song.title
    artist = song.artist

    print(f"Fetching lyrics for: {title} by {artist}") # Technically don't need this since search_song prints
    
    # Attempts to fetch lyrics from Genius API using the song title and artist from Billboard
    try:
        genius_song = genius.search_song(title, clean_artist(artist))
        
        if genius_song:
            if genius_song.lyrics:
                lyrics = genius_song.lyrics
            else: 
                lyrics = None
            if 'release_date_components' in genius_song.to_dict() and genius_song.to_dict()['release_date_components']:
                release_year = genius_song.to_dict()['release_date_components']['year']
            else:
                release_year = None
        else:
            lyrics = None       
            release_year = None
    
    except Exception as e:
        print(f"Error fetching lyrics for {title} by {artist}: {e}")
        lyrics = None
        release_year = None
        
    # Adds song info to the songs_data list
    songs_data.append({
        'title': title,
        'artist': artist,
        'lyrics': lyrics,
        'rank': song.rank,
        'last_week': song.lastPos,
        'peak_rank': song.peakPos,
        'weeks_on_chart': song.weeks,
        'release_year': release_year,
        'lyric_length' : len(lyrics.split()) if lyrics else 0,
    })
    
    time.sleep(1)  # To respect API rate limits


df = pd.DataFrame(songs_data)
df.to_csv('billboard_hot_100_with_lyrics.csv', index=False)

print("Data collection complete. Saved to 'billboard_hot_100_with_lyrics.csv'.")
