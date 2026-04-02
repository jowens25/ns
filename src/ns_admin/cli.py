import typer
import asyncio
from typing import Annotated, Literal

app = typer.Typer()

strings_app = typer.Typer()

from ns_socket import read_write_socket, set_status_string


@app.command()
def strings(
    status: Literal["disable", "enable"],
    start: int,
    end: int,
):

    run = 1 if status == "enable" else 0

    for i in range(start, end + 1):
        asyncio.run(read_write_socket(f"$NVS{i}={int(run)}"))


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
