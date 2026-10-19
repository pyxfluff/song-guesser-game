# pyxfluff 2026

from random import randint, shuffle
from time import sleep

import httpx
from mpv import MPV
from rich.live import Live

from . import authenticated_request, config, console, spinner
from .ui import add_box_thingy

player = MPV()

player.volume = 85

# x = authenticated_request("rest/download?id=eNuejPOf1n48ntgUj7zkpJ&u=admin&v=0.1.0&c=song-guesser", "get")
# print(x.status_code)
# print(x.text)


spinner.update(text="Downloading songs...")
song_names = []

with Live(spinner, console=console, refresh_per_second=20, transient=True):
    songs = authenticated_request(
        "api/song?_order=ASC&_sort=name&_start=0", "get"
    ).json()
    #shuffle(songs)

    for song in songs:
        #song_names.append(song["title"])
        song_names.append(f"{song["title"]} - {song["albumArtist"]}")

    print(len(songs))
    # console.print_json(data=songs[1])

while True:
    selected_song = songs[randint(1, len(songs))]
    song_data = {"name": selected_song["title"], "artist": selected_song["albumArtist"]}

    # print(selected_song)

    player.play(
        f"{config['nd_url']}/rest/stream?id={selected_song['id']}&u=admin&t={config['ss_token']}&s={config['ss_salt']}&v=0.1.0&c=song-guesser&format=mpe&bitrate=256"
    )


    player.wait_until_playing()
    player.pause = True
    print("is playing now")
    player.seek(2)
    sleep(1) # for some reason, wait_until_playing doesn't actually wait until it's playing..
    add_box_thingy(song_names, song_data, player)