# Shotify
# By Aaron Huxford and Noah Waller

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import numpy as np
import sys
import os

# collaborative playlist to play
playlist = "Naaron’s PH Dance-y Club" # apostrophe needs to be an actual apostrophe, due to naming playlist using iPhone (or Mac)

# file for modifying start times, MUST BE TAB DELIMITED (TSV) file
usr_file = '/home/aaron/Downloads/UserModList - July282023.tsv'

# shuffle playlist
shuffle = True
shuffle_seed = 69

# resume playlist (if script crashed for any reason)
restart = False
restart_song_number = 1

###############################################################################
###############################################################################
###############################################################################
# read input user file
if len(usr_file) == 0:
    print('No user modifications required for playlist...')
    usr_mod_names    = [] # song name
    usr_mod_artists  = [] # song artist
    usr_mod_times    = [] # start time
    usr_mod_position = [] # desired position in playlist
else:
    print('Performing user modifications to playlist...')
    usr_array = np.genfromtxt(fname=usr_file,delimiter='\t',skip_header=1,usecols=(0,1),dtype=str)
    usr_times = np.genfromtxt(fname=usr_file,delimiter='\t',skip_header=1,usecols=(2),dtype=int)
    usr_position = np.genfromtxt(fname=usr_file,delimiter='\t',skip_header=1,usecols=(3),dtype=int)

    usr_mod_names    = usr_array[:,0].tolist()
    usr_mod_artists  = usr_array[:,1].tolist()
    usr_mod_times    = usr_times.tolist()
    usr_mod_position = usr_position.tolist()

# force restart number to atleast 1
if restart_song_number  < 1:
    restart_song_number  = 1

# setup spotify access
scope = "user-read-playback-state,user-modify-playback-state,playlist-read-collaborative"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

# loop through seen playlists and find input playlist
results = sp.current_user_playlists(limit=50)
for i, item in enumerate(results['items']):
    if item['name'] == playlist:
        break

playlist_items = sp.playlist_items(item['id'])

# initial lists for tracks
tracks_uri    = []
tracks_time   = []
tracks_name   = []
tracks_artist = []

mod_name   = []
mod_artist = []

# loop through playlist songs, build lists
for i, items in enumerate(playlist_items['items']):
    tracks_uri.append(items['track']['uri'])
    tracks_name.append(items['track']['name'])
    tracks_artist.append(items['track']['artists'][0]['name'])
    tracks_time.append(0) # default to zero


# loop through modifications for playlist
i_mod = 0
for i, name in enumerate(usr_mod_names):    \

    mod_name.append(name)
    mod_artist.append(usr_mod_artists[i])

    for j, items in enumerate(playlist_items['items']):   # loop through playlist again

        if (items['track']['name'] == mod_name[-1]) and (items['track']['artists'][0]['name'] == mod_artist[-1]):

            tracks_time[j] = usr_mod_times[i]
            i_mod += 1

# check if typo in supplied modification lists
if i_mod != len(usr_mod_names):

    print('')
    print('Typo in user provided modification file in song name or artist')
    print('')

    sys.exit('Error in supplied modification file')


N_songs = len(tracks_uri)

###############################################################################
###############################################################################
# if playlist is shuffled

if shuffle:
    np.random.seed(shuffle_seed)

    # in case playlist stops/crashes
    print('Random seed used for shuffle =', np.random.get_state()[1][0])

    random_order = np.arange(N_songs)
    np.random.shuffle(random_order)

    random_tracks_uri  = []
    random_tracks_time = []
    random_tracks_name = []
    random_tracks_artist = []

    for i in random_order:
        random_tracks_uri.append(tracks_uri[i])
        random_tracks_time.append(tracks_time[i])
        random_tracks_name.append(tracks_name[i])
        random_tracks_artist.append(tracks_artist[i])

    tracks_uri    = random_tracks_uri
    tracks_name   = random_tracks_name
    tracks_time   = random_tracks_time
    tracks_artist = random_tracks_artist


###############################################################################
###############################################################################
# if restarting modify list of songs

if restart:
    tracks_uri  = tracks_uri[(restart_song_number-1):]
    tracks_time = tracks_time[(restart_song_number-1):]
    tracks_name = tracks_name[(restart_song_number-1):]
else:
    restart_song_number = 1

###############################################################################
###############################################################################
# modify position of song supplied by user's modification list

# hurt my head making this
for i, uri in enumerate(tracks_uri):

    name = tracks_name[i]

    if name in mod_name:
        i_mod = mod_name.index(name)

        if usr_mod_position[i_mod] != -1: # -1 is an empty cell

            i_moveto = usr_mod_position[i_mod]-1

            # swap songs, in theory this will work unless probability gets us
            tracks_uri[i_moveto] ,tracks_uri[i]  = tracks_uri[i] ,tracks_uri[i_moveto]
            tracks_time[i_moveto],tracks_time[i] = tracks_time[i],tracks_time[i_moveto]
###############################################################################
###############################################################################

# convert s to ms for position
tracks_time_ms= [value * 1000 for value in tracks_time]

time_per_song = 60 # time to play each song, in seconds

# play songs (:
for i, song_uri in enumerate(tracks_uri):

    # play song
    sp.start_playback(uris=[song_uri], position_ms=tracks_time_ms[i])

    print("Playing song number", i+restart_song_number, "of", N_songs)

    time.sleep(time_per_song)
