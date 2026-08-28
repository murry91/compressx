from pathlib import Path


def read_file(path: str | Path) -> bytes:
    with open(path, "rb") as file:
        return file.read()