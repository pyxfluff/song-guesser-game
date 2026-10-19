# pyxfluff 2026

import threading

import readchar
from rich import box
from rich.align import Align
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import console

console.clear()  # debugging stuff from earlier mostly.. plus the loading stuff is transient


def render(guess: str, index: int, songs: list, current_status: str):
    matches = [song for song in songs if guess.lower() in song.lower()]

    index = max(0, min(index, len(matches) - 1))

    results = Table.grid(padding=(0, 1))
    results.add_column(width=3)
    results.add_column()

    selected_index = index
    start_index = max(0, min(selected_index - 2, len(matches) - 8))

    for index, song in enumerate(
        matches[start_index : start_index + 8], start=start_index
    ):
        results.add_row(
            ">" if index == selected_index else " ",
            Text(song, style="bold blue" if index == selected_index else ""),
        )

    if not matches:
        results.add_row("", Text("No matches", style="dim"))

    search = Panel(
        Text.assemble(
            (">", "bold cyan"),
            (guess, "white"),
            ("|", "bold cyan"),
        ),
        title="Guess",
        box=box.ROUNDED,
        height=3,
    )

    song_list = Panel(
        results, title=f"Library ({len(matches)})", box=box.ROUNDED, height=10
    )

    controls = Panel(
        Align.center(
            "Game over" not in current_status
            and "[bold]up/down[/] to navigate | [bold]enter[/] to submit | [bold]space[/] to replay | [bold]`[/] to give up and add more time"
            or "Press enter to continue"
        ),
        box=box.ROUNDED,
    )

    instructions = Panel(
        Align.center(current_status),
        box=box.ROUNDED,
    )

    return Group(instructions, search, song_list, controls), matches


timer = None


def play_for_duration(player, duration, start_position):
    global timer

    if timer:
        timer.cancel()

    player.pause = False
    player.seek(start_position, "absolute")

    timer = threading.Timer(duration, lambda: setattr(player, "pause", True))
    timer.start()


score = 0


# COMPLEX ASS INPUT HANDLER!! I HATE MAKING GAMES IN PYTHON!!!
def add_box_thingy(songs, correct_song, player):
    with Live(console=console, refresh_per_second=15, transient=True) as live:
        guess = ""
        index = 0
        status = f"[bold]Score = {score}[/] | Type your guess"
        past_guesses = []
        current_increment = 0
        increments = [0.5, 1, 2, 6, 8, 14]
        is_game_over = False

        play_for_duration(player, increments[current_increment], 2)

        while True:
            ui, matches = render(guess, index, songs, status)
            live.update(ui, refresh=True)

            key = readchar.readkey()

            if key == "`":
                # current_increment = (current_increment * 5) + (current_increment > .5 and .5 or 0)
                current_increment += 1
                if current_increment == 6:
                    is_game_over = True

                    status = f"Game over - correct song was {correct_song['name']} - {correct_song['artist']}!"
                    play_for_duration(player, 60, 2)

                    continue

                play_for_duration(
                    player,
                    increments[current_increment],
                    2,
                )
            elif key in (readchar.key.BACKSPACE, "\x7f"):
                guess = guess[:-1]
                index = 0
            elif key == readchar.key.UP:
                index = max(0, index - 1)
            elif key == readchar.key.DOWN:
                index = min(max(0, len(matches) - 1), index + 1)
            elif key in ("\r", "\n"):
                if is_game_over:
                    break
                if matches:
                    print(
                        correct_song["name"],
                        matches[index],
                        correct_song["name"] in matches[index],
                    )
                    if correct_song["name"] in matches[index]:
                        print("you win")
                    else:
                        print("DIE")

            elif key == " ":
                play_for_duration(
                    player,
                    increments[current_increment],
                    2,
                )
            elif key.isprintable() and len(key) == 1:
                guess += key
                index = 0
