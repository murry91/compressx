from collections import Counter
import zlib


def calculate_frequencies(data: bytes) -> Counter:
    return Counter(data)


def calculate_file_frequencies(
    path,
    chunk_size: int = 1024 * 1024,
) -> Counter:
    frequencies = Counter()

    with open(path, "rb") as file:
        while chunk := file.read(chunk_size):
            frequencies.update(chunk)

    return frequencies


def analyze_file(
    path,
    chunk_size: int = 1024 * 1024,
):
    frequencies = Counter()
    checksum = 0

    with open(path, "rb") as file:
        while chunk := file.read(chunk_size):
            frequencies.update(chunk)
            checksum = zlib.crc32(chunk, checksum)

    return frequencies, checksum & 0xFFFFFFFF