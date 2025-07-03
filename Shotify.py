# Shotify
# Coauthored by Dr. Aaron Huxford and Dr. Noah Waller

# Instructions:
# 1. Ensure you have the necessary permissions and Spotify API credentials set up for your account.
# 2. First create the time file by running this script with `time_file = "create"` and `save_file` set to the desired output path.
# 3. Run the script again with the `time_file` set to the path of the created time file.
# 4. Optionally, set `restart = True` and `restart_song_number` to the desired song number to resume playback from a specific point.
# 5. Adjust `playlist` to the desired collaborative playlist name.
# 6. Set `shuffle_seed` to a desired integer for shuffling the playlist.
# 7. Run the script to start playback of the playlist.
# 8. Enjoy the music and the fun of Shotify!

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import numpy as np
import sys
import os
from Shotify_functions import *

# initialize some variables, DONT TOUCH
save_file = None
restart = False
restart_song_number = 1
shuffle_seed = int(time.time()) # use current time as seed

# USER: collaborative playlist to play
playlist = "Naaron’s PH Hot" # apostrophe needs to be an actual apostrophe, due to naming playlist using iPhone (or Mac)

# USER: shuffle playlist based on a seed
# shuffle_seed = 123

# USER: restart playlist from a specific song number (if script crashed for any reason)
# restart = True
# restart_song_number = 20

# USER:tsv file for song start times
time_file = "/home/aaron/Shotify/PH_times/PH_July42025.tsv"
# time_file = "create" # used to create a new user modification file, will prompt for start times of each song
# save_file = "/home/aaron/Shotify/PH_times/PH_July42025.tsv" # output file for user modifications, if creating new file

###############################################################################
###############################################################################
###############################################################################
# setup spotify access
scope = "user-read-playback-state,user-modify-playback-state,playlist-read-collaborative"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

# create time file
if time_file == "create":

    if save_file is not None:
        out_file = save_file
    else:
        out_file = os.path.abspath("PH_times.csv")

    create_time_file(sp=sp, playlist=playlist, out_file=out_file)
    sys.exit() # Exits the script

# read time file
print('Using time file at:', time_file)
time_data = np.genfromtxt(time_file, delimiter='\t', names=True, dtype=None)
N_songs = len(time_data)
names   = time_data['name'].tolist()
artists = time_data['artist'].tolist()
times   = time_data['time'].tolist()
uris    = time_data['uri'].tolist()

# shuffle order of songs
np.random.seed(shuffle_seed)
print('Random seed used for shuffle:', np.random.get_state()[1][0])

random_order = np.arange(N_songs)
np.random.shuffle(random_order)

random_names   = []
random_artists = []
random_times   = []
random_uris    = []

for i in random_order:
    random_names.append(names[i])
    random_artists.append(artists[i])
    random_times.append(times[i])
    random_uris.append(uris[i])

# restarting playback if crashed for some reason
if restart:
    random_names   = random_names[(restart_song_number-1):]
    random_artists = random_artists[(restart_song_number-1):]
    random_times   = random_times[(restart_song_number-1):]
    random_uris    = random_uris[(restart_song_number-1):]

# redistribute Afroman songs (thank you github copilot)
afroman_count = random_artists.count("Afroman")
afroman_indices = [i for i, artist in enumerate(random_artists) if artist == "Afroman"]
print(f"Number of 'Afroman' songs being redistributed: {afroman_count}")

if afroman_count > 0:
    # Calculate new evenly spaced indices, then subtract 1 to shift (e.g., 30 -> 29)
    new_indices = [int(round((N_songs * (k + 0.5)) / afroman_count - 0.5)) - 1 for k in range(afroman_count)]
    # Clamp indices to valid range
    new_indices = [min(max(idx, 0), N_songs - 1) for idx in new_indices]

    # Remove Afroman songs from current positions
    afroman_songs = [(random_names[i], random_artists[i], random_times[i], random_uris[i]) for i in afroman_indices]
    for i in sorted(afroman_indices, reverse=True):
        del random_names[i]
        del random_artists[i]
        del random_times[i]
        del random_uris[i]

    # Insert Afroman songs at new indices
    for insert_idx, song in sorted(zip(new_indices, afroman_songs)):
        random_names.insert(insert_idx, song[0])
        random_artists.insert(insert_idx, song[1])
        random_times.insert(insert_idx, song[2])
        random_uris.insert(insert_idx, song[3])

    print(f"Redistributed 'Afroman' songs to indices: {new_indices}")

# playback songs
random_times_ms= [value * 1000 for value in random_times]
time_per_song = 60 # time to play each song, in seconds

for i, song_uri in enumerate(random_uris):
    if i in [14, 29, 44]: # play airhorn sound at specific song indices
        print(f"Alert: at song {i+restart_song_number} of {N_songs}!\n")
        sp.start_playback(uris=["spotify:track:4aT8Ly8q4V1ZS1x7Mu0PHw"])
        time.sleep(5)

    # play song
    sp.start_playback(uris=[song_uri], position_ms=random_times_ms[i])

    print(f"Playing song {i+restart_song_number} of {N_songs}")
    print(f"{random_names[i]} by {random_artists[i]}\n")

    time.sleep(time_per_song)

print(f"Alert: you're done!\n")
sp.start_playback(uris=["spotify:track:4aT8Ly8q4V1ZS1x7Mu0PHw"])
time.sleep(5)

# play "Friday by Riton et al" to finish
sp.start_playback(uris=["spotify:track:4cG7HUWYHBV6R6tHn1gxrl"])
print("Playing 'Friday' by Riton et al to finish.\n")
