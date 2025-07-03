import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np

def create_time_file(sp, playlist, out_file):
    """
    Creates a time file for a Spotify playlist, allowing users to specify start times for each song.
    The function retrieves the playlist, iterates through its songs, and prompts the user to enter
    start times for each song. The results are saved to a CSV file.

    :param sp: Spotipy client instance
    :param playlist: Name of the Spotify playlist to modify
    :param out_file: Output file path where the time modifications will be saved
    """

    print('Creating time file at', out_file)

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

    # loop through playlist songs, build lists
    for i, items in enumerate(playlist_items['items']):
        tracks_uri.append(items['track']['uri'])
        tracks_name.append(items['track']['name'])
        tracks_artist.append(items['track']['artists'][0]['name'])
        tracks_time.append(0) # default to zero


    user_numbers = []
    # loop through songs and ask for user modifications to start times
    for i, uri in enumerate(tracks_uri):
        name = tracks_name[i]
        artist = tracks_artist[i]
        # print(name,' by ', artist)
        # print(uri)
        print(f"Song {i+1} of {len(tracks_uri)}")
        while True:
            try:
                user_input = input(f"Enter a time (in seconds) for when '{name}' by '{artist}' should start to play (press Enter for 0): ")
                if user_input.strip() == '':
                    user_number = 0
                else:
                    user_number = int(user_input)
                user_numbers.append(user_number)
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer for the time or press Enter for 0.")

    # After collecting user_numbers, combine all lists into a 2D array and save to CSV
    data = list(zip(tracks_name, tracks_artist, user_numbers, tracks_uri))
    arr = np.array(data, dtype=object)
    header = 'name\tartist\ttime\turi'
    np.savetxt(out_file, arr, fmt='%s', delimiter='\t', header=header, comments='')
    print(f"Saved time modifications to {out_file}")
    
    return 

