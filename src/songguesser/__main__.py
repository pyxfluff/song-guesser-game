from rich.live import Live

from . import authenticated_request, console, spinner

spinner.update(text="Downloading songs...")

with Live(spinner, console=console, refresh_per_second=20, transient=True):
    songs = authenticated_request("api/song?_order=ASC&_sort=name&_start=0", "get").json()
    valid_songs = []

    print(len(songs))
    console.print_json(data=songs[1])
