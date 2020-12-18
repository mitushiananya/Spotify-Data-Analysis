import spotipy
import time
import numpy as np
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials

client_id = 'Enter the client id that you just got'
client_secret = 'Enter the client secret key you just got'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)  # Object to access API
name = "J. Cole"  # You can choose any artist of your choice
result = sp.search(name)
print("Search Query: \n")
print(result['tracks']['items'][0]['artists'])

# Extract Artist's URI (basically unique ID for the artist)
artist_uri = result['tracks']['items'][0]['artists'][0]['uri']

# Pull all of the artist's albums
sp_albums = sp.artist_albums(artist_uri, album_type='album')

# Store artist's albums' names and URIs in separate lists
album_names = []
album_uris = []
for i in range(len(sp_albums['items'])):
    album_names.append(sp_albums['items'][i]['name'])
    album_uris.append(sp_albums['items'][i]['uri'])

print("Album Names: \n", pd.DataFrame(album_names, columns=['Album Names']))
print("\n")
print("Album URIs: \n", pd.DataFrame(album_uris, columns=['Album URIs']))

# Extract track data from albums
def album_songs(uri):
    album = uri
    spotify_albums[album] = {}  # Create keys-values of empty lists inside nested dictionary for album
    spotify_albums[album]['album'] = []
    spotify_albums[album]['track_number'] = []
    spotify_albums[album]['id'] = []
    spotify_albums[album]['name'] = []
    spotify_albums[album]['uri'] = []
    # Extract track data
    tracks = sp.album_tracks(album)
    for n in range(len(tracks['items'])):
        spotify_albums[album]['album'].append(album_names[album_count])
        spotify_albums[album]['track_number'].append(tracks['items'][n]['track_number'])
        spotify_albums[album]['id'].append(tracks['items'][n]['id'])
        spotify_albums[album]['name'].append(tracks['items'][n]['name'])
        spotify_albums[album]['uri'].append(tracks['items'][n]['uri'])

# store the album data in an empty dictionary
spotify_albums = {}
album_count = 0
for i in album_uris:  # Each album
    album_songs(i)
    print(str(album_names[album_count]) + " album songs have been added to spotify_albums dictionary.")
    album_count += 1  # Updates album count once all tracks have been added


def audio_features(album):
    # Key-values to store audio features
    spotify_albums[album]['acousticness'] = []
    spotify_albums[album]['danceability'] = []
    spotify_albums[album]['energy'] = []
    spotify_albums[album]['instrumentalness'] = []
    spotify_albums[album]['liveness'] = []
    spotify_albums[album]['loudness'] = []
    spotify_albums[album]['speechiness'] = []
    spotify_albums[album]['tempo'] = []
    spotify_albums[album]['valence'] = []
    spotify_albums[album]['popularity'] = []

    track_count = 0
    for track in spotify_albums[album]['uri']:
        # Extract audio features per track
        features = sp.audio_features(track)
        # Append relevant key-value
        spotify_albums[album]['acousticness'].append(features[0]['acousticness'])
        spotify_albums[album]['danceability'].append(features[0]['danceability'])
        spotify_albums[album]['energy'].append(features[0]['energy'])
        spotify_albums[album]['instrumentalness'].append(features[0]['instrumentalness'])
        spotify_albums[album]['liveness'].append(features[0]['liveness'])
        spotify_albums[album]['loudness'].append(features[0]['loudness'])
        spotify_albums[album]['speechiness'].append(features[0]['speechiness'])
        spotify_albums[album]['tempo'].append(features[0]['tempo'])
        spotify_albums[album]['valence'].append(features[0]['valence'])
        # Popularity is stored differently
        pop = sp.track(track)
        spotify_albums[album]['popularity'].append(pop['popularity'])
        track_count += 1

# Avoiding sending many requests at Spotify’s API at once
sleep_min = 2
sleep_max = 5
start_time = time.time()
request_count = 0
for i in spotify_albums:
    audio_features(i)
    request_count+=1
    if request_count % 5 == 0:
        print(str(request_count) + " playlists completed")
        time.sleep(np.random.uniform(sleep_min, sleep_max))
        print('Loop #: {}'.format(request_count))
        print('Elapsed Time: {} seconds'.format(time.time() - start_time))

# Organise the data data into a dictionary which can be converted into a dataframe.
dic_df = {}
dic_df['album'] = []
dic_df['track_number'] = []
dic_df['id'] = []
dic_df['name'] = []
dic_df['uri'] = []
dic_df['acousticness'] = []
dic_df['danceability'] = []
dic_df['energy'] = []
dic_df['instrumentalness'] = []
dic_df['liveness'] = []
dic_df['loudness'] = []
dic_df['speechiness'] = []
dic_df['tempo'] = []
dic_df['valence'] = []
dic_df['popularity'] = []
for album in spotify_albums:
    for feature in spotify_albums[album]:
        dic_df[feature].extend(spotify_albums[album][feature])

print("Total number of Songs: ",len(dic_df['album']))

dataframe = pd.DataFrame.from_dict(dic_df)
print("All songs details: \n",dataframe)

# Remove duplicate songs
print("Total number of songs (with duplicate values: ",len(dataframe))
final_df = dataframe.sort_values('popularity', ascending=False).drop_duplicates('name').sort_index()
print("Total number of songs (without duplicate values: ",len(final_df))

print("Song details after removal of duplicate songs: \n")
print(final_df.head())

# saving the file to a CSV file in the project directory
final_df.to_csv("spotifycoleanalysis.csv")
