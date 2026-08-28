import zlib

def compression_ratio(original_size: int, compressed_size: int) -> float:
    if original_size == 0:
        return 0.0

    return compressed_size / original_size


def space_saving(original_size: int, compressed_size: int) -> float:
    if original_size == 0:
        return 0.0

    return (1 - compressed_size / original_size) * 100

def calculate_checksum(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF

def calculate_file_checksum(
    path,
    chunk_size: int = 1024 * 1024,
) -> int:
    checksum = 0

    with open(path, "rb") as file:
        while chunk := file.read(chunk_size):
            checksum = zlib.crc32(chunk, checksum)

    return checksum & 0xFFFFFFFF