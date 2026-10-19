# pyxfluff 2026

import sys
from pathlib import Path

import httpx
import orjson
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner

console = Console()
spinner = Spinner("material", text="Testing connection...")

# fetch config
config = None

try:
    config = orjson.loads(Path("./config.json").read_text())
except FileNotFoundError:
    user = console.input("[b cyan]Navidrome Username[/]: ")
    password = console.input("[b cyan]Navidrome Password[/]: ", password=True)
    nd_url = console.input(
        "[b cyan]URL (include protocol, no trailing slash) (https://music.example.com):[/] "
    )

    resp = httpx.post(f"{nd_url}/auth/login", json={
        "username": user,
        "password": password
    }).json()

    print(resp)

    config = {
        "nd_url": nd_url,
        "nd_token": resp["token"],
        "nd_user": user,
        "ss_salt": resp["subsonicSalt"],
        "ss_token": resp["subsonicToken"]
    }

    console.clear()

    # ..write it
    Path("./config.json").write_text(orjson.dumps(config).decode())


def delete_and_exit():
    Path("./config.json").unlink()
    sys.exit(1)


def authenticated_request(endpoint, method):
    return httpx.request(
        method=method,
        url=f"{config['nd_url']}/{endpoint}",
        headers={"x-nd-authorization": f"Bearer {config["nd_token"]}"},
    )


# test connection
with Live(spinner, console=console, refresh_per_second=20, transient=True):
    try:
        httpx.get(f"{config['nd_url']}/rest/ping").raise_for_status()
        console.print(f"[green][✓] Connected to {config['nd_url']}[/]")
    except (httpx.HTTPError, KeyError):
        console.print(
            "[red][!] The input provided is not a Navidrome server, please re-run the module and input a correct URL.[/]"
        )
        delete_and_exit()

    try:
        authenticated_request(
            "api/album?_start=0&end=1&_order=DESC&_sort=name", "get"
        ).raise_for_status()
        console.print(f"[green][✓] Authenticated with {config['nd_url']}[/]")
    except (httpx.HTTPError, KeyError) as e:
        print(e)
        console.print(
            "[red][!] Your authentication cookie is invalid! Please obtain a new one and restart the program.[/]"
        )
        delete_and_exit()

console.print("[green]Server validated!")
