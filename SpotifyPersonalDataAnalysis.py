import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import spotipy
import spotipy.util as util

from spotipy.oauth2 import SpotifyClientCredentials

# AUTHORIZATION FLOW
# Declare the credentials
client_id = 'Enter your client ID'
client_secret = 'Enter your client secret'
redirect_uri='http://localhost:7777/callback'
username = 'Enter your username'

# Authorization flow
scope = 'user-top-read'
token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)
# You have to first run the above code i.e code till line 27. You will be redirected to spotify weebsite. Click on Agree and then a message with "Authorisation: Sucessful" will be displayed

# Extract your top-50 songs
if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_top_tracks(limit=50,offset=0,time_range='medium_term')
    for song in range(50):
        list = []
        list.append(results)
        with open('top50_data.json', 'w', encoding='utf-8') as f:
            json.dump(list, f, ensure_ascii=False, indent=4)
else:
    print("Can't get token for", username)

# Open the JSON file to Python objects
with open('top50_data.json') as f:
  data = json.load(f)

print("Total number of songs: ",len(data[0]['items']))

list_of_results = data[0]["items"]
list_of_artist_names = []
list_of_artist_uri = []
list_of_song_names = []
list_of_song_uri = []
list_of_durations_ms = []
list_of_explicit = []
list_of_albums = []
list_of_popularity = []

for result in list_of_results:
    result["album"]
    this_artists_name = result["artists"][0]["name"]
    list_of_artist_names.append(this_artists_name)
    this_artists_uri = result["artists"][0]["uri"]
    list_of_artist_uri.append(this_artists_uri)
    list_of_songs = result["name"]
    list_of_song_names.append(list_of_songs)
    song_uri = result["uri"]
    list_of_song_uri.append(song_uri)
    list_of_duration = result["duration_ms"]
    list_of_durations_ms.append(list_of_duration)
    song_explicit = result["explicit"]
    list_of_explicit.append(song_explicit)
    this_album = result["album"]["name"]
    list_of_albums.append(this_album)
    song_popularity = result["popularity"]
    list_of_popularity.append(song_popularity)

# Convert the extracted data to a pandas dataframe
all_songs = pd.DataFrame(
    {'artist': list_of_artist_names,
     'artist_uri': list_of_artist_uri,
     'song': list_of_song_names,
     'song_uri': list_of_song_uri,
     'duration_ms': list_of_durations_ms,
     'explicit': list_of_explicit,
     'album': list_of_albums,
     'popularity': list_of_popularity

     })

allsongsdisplay = all_songs.sort_values('popularity', ascending=False)
print(allsongsdisplay)
allsongsdisplay.to_csv("Top50Songs.csv")  # Save in a CSV file in the project directory

descending_order = all_songs['artist'].value_counts().sort_values(ascending=False).index
ax = sns.countplot(y=all_songs['artist'], order=descending_order, palette='Pastel2')

sns.despine(fig=None, ax=None, top=True, right=True, left=False, trim=False)
sns.set(rc={'figure.figsize': (14, 17)})

ax.set_ylabel('')
ax.set_xlabel('')
ax.set_title('Number of Songs per Artist in the Top 50', fontsize=16, fontweight='heavy')
sns.set(font_scale=1.4)
ax.axes.get_xaxis().set_visible(False)
ax.set_frame_on(False)

y = all_songs['artist'].value_counts()
for i, v in enumerate(y):
    ax.text(v + 0.2, i + .16, str(v), color='black', fontweight='light', fontsize=14)

plt.show()

# Extracting all my playlists
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlists = sp.user_playlists(username)
def fetch_playlists(sp, username):
    id = []
    name = []
    num_tracks = []

    # Make the API request
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        id.append(playlist['id'])
        name.append(playlist['name'])
        num_tracks.append(playlist['tracks']['total'])

    # Create the final df
    df_playlists = pd.DataFrame({"id":id, "name": name, "#tracks": num_tracks})
    return df_playlists


print("My Playlists: \n",fetch_playlists(sp,username))

# Pull tracks for the given playlist
def fetch_playlist_tracks(sp, username, playlist_id):

    offset = 0
    tracks = []

    # API request
    while True:
        content = sp.user_playlist_tracks(username, playlist_id, fields=None, limit=100, offset=offset, market=None)
        tracks += content['items']

        if content['next'] is not None:
            offset += 100
        else:
            break
    
    track_id = []
    track_name = []

    for track in tracks:
        track_id.append(track['track']['id'])
        track_name.append(track['track']['name'])

    # Create the final dataframe
    df_playlists_tracks = pd.DataFrame({"track_id":track_id, "track_name": track_name})
    return df_playlists_tracks


print("Playlist Tracks: \n")      # After Username add the Playlist_id of any playlist of your choice (that we saw from the previous table)
print(fetch_playlist_tracks(sp, username, 'Enter the playlist_id')) 

# Extract songs' audio characteristics/features
def fetch_audio_features(sp, username, playlist_id):
    playlist = fetch_playlist_tracks(sp, username, playlist_id)
    index = 0
    audio_features = []

    while index < playlist.shape[0]:
        audio_features += sp.audio_features(playlist.iloc[index:index + 50, 0])
        index += 50

    # features list
    features_list = []
    for features in audio_features:
        features_list.append([features['danceability'],
                              features['energy'], features['tempo'],
                              features['loudness'], features['valence'],
                              features['speechiness'], features['instrumentalness'],
                              features['liveness'], features['acousticness']])

    df_audio_features = pd.DataFrame(features_list, columns=['danceability', 'energy',
                                                             'tempo', 'loudness', 'valence',
                                                             'speechiness', 'instrumentalness',
                                                             'liveness', 'acousticness'])

    df_playlist_audio_features = pd.concat([playlist, df_audio_features], axis=1)
    df_playlist_audio_features.set_index('track_id', inplace=True, drop=True)

    return df_playlist_audio_features


df1 = fetch_audio_features(sp, username, 'Enter the playlist_id')
print("\n Three songs with their corresponding features: \n")
print(df1.head(3))

for feature in df1.columns:
    # tempo, ludness and track_name will not be mulitplied by 100.
    if feature == 'tempo' or feature == 'loudness' or feature == 'track_name':
        continue
    df1[feature] = df1[feature] * 100

print("\n Three songs with their corresponding features (values * 100): \n")
print(df1.head(3))

# Returns selected audio features of every track, for the given playlist.
def fetch_audio_features(sp, username, playlist_id):

    playlist = fetch_playlist_tracks(sp, username, playlist_id)
    index = 0
    audio_features = []

    # API request
    while index < playlist.shape[0]:
        audio_features += sp.audio_features(playlist.iloc[index:index + 50, 0])
        index += 50

    # Append the audio features in a list
    features_list = []
    for features in audio_features:
        features_list.append([features['danceability'],
                              features['energy'], features['tempo'],
                              features['loudness'], features['valence']])

    df_audio_features = pd.DataFrame(features_list, columns=['danceability', 'energy',
                                                             'tempo', 'loudness', 'valence'])

    # Set the 'tempo' & 'loudness' in the same range with the rest features, that's why multiplying it by 100
    for feature in df_audio_features.columns:
        if feature == 'tempo' or feature == 'loudness':
            continue
        df_audio_features[feature] = df_audio_features[feature] * 100

    # Create the final df, using the 'track_id' as index for future reference
    df_playlist_audio_features = pd.concat([playlist, df_audio_features], axis=1)
    df_playlist_audio_features.set_index('track_id', inplace=True, drop=True)

    return df_playlist_audio_features


df2 = fetch_audio_features(sp, username, 'Enter playlist_id')
print("\n Selected Audio Features: \n")
print(df2.head(3))

# Self-Made personal playlist
playlists = fetch_playlists(sp,username)
playlists = playlists[:4].copy()
print("\n Self-made Playlist: \n", playlists)

df_onrepeat = fetch_audio_features(sp, username, 'Enter playlist_id')
df_jacques = fetch_audio_features(sp, username, 'Enter playlist_id')
df_kirk = fetch_audio_features(sp, username, 'Enter playlist_id')
df_onika = fetch_audio_features(sp, username, 'Enter playlist_id')

print(df_kirk.head().iloc[:, 1:])

# Plotting diagrams
plt.style.use('fivethirtyeight')  # FiveThirtyEight style sheet

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(13, 13))
ax1, ax2, ax3, ax4 = axes.flatten()
fig.subplots_adjust(hspace=.2, wspace=.5)

df_kirk.mean().plot.barh(ax=ax1, colormap='ocean', fontsize=13)
ax1.set_xlim(-25,130)

df_jacques.mean().plot.barh(ax=ax2, colormap='Dark2', fontsize=13)
ax2.set_xlim(-25,130)

df_onika.mean().plot.barh(ax=ax3, colormap='brg', fontsize=13)
ax3.set_xlim(-25,130)

df_onrepeat.mean().plot.barh(ax=ax4, colormap='jet', fontsize=13)
ax4.set_xlim(-25,130)

# Create titles
ax1.set_title('Jonathon Kirk Playlist')
ax2.set_title('Jacques Webster Playlist')
ax3.set_title('Onika Maraj Playlist')
ax4.set_title('On Repeat G Playlist')

plt.show()

kirk_mean = pd.DataFrame(df_kirk.mean(), columns= ['kirk_playlist'])
jacques_mean = pd.DataFrame(df_jacques.mean(), columns= ['jacques_playlist'])
onrepeat_mean = pd.DataFrame(df_onrepeat.mean(), columns= ['onrepeat_playlist'])
onika_mean = pd.DataFrame(df_onika.mean(), columns= ['onika_playlist'])

total_mean = pd.concat([kirk_mean, jacques_mean, onika_mean, onrepeat_mean], axis=1)
print("Summary: \n", total_mean)

plt.style.use('fivethirtyeight')  # FiveThirtyEight style sheet

total_mean.plot.barh(color = ['#008080', '#800080', '#008000', '#800000'],  width = .8, rot = 0, figsize = (8,6))
plt.title('Comparing Mean Audio Features: ', y = 1.07)
plt.xlim(-20,130) # because ratings start at 0 and end at 5
plt.legend(framealpha = 0, loc = 'upper right')
plt.show()

# For now, I will be focus on only one playlist. That is the Onika Maraj playlist
print(df_onika.describe())

df_onika.boxplot(vert = False, figsize = (13,7), showfliers = False, showmeans = True,
                 patch_artist=True, boxprops=dict(linestyle='-', linewidth=1.5),
                 flierprops=dict(linestyle='-', linewidth=1.5),
                 medianprops=dict(linestyle='-', linewidth=1.5))

plt.show()
