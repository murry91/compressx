from dataclasses import dataclass


MAGIC = b"CX02"

HUFFMAN = 0
STORED = 1

CHECKSUM_SIZE = 4

HEADER_FIXED_SIZE = 4 + 1 + 8 + 2 + CHECKSUM_SIZE

FREQUENCY_ENTRY_SIZE = 1 + 8
MAX_FREQUENCY_ENTRIES = 256


@dataclass
class CompressionHeader:
    original_size: int
    frequencies: dict[int, int]
    checksum: int = 0
    method: int = HUFFMAN


def write_header(
    file,
    original_size: int,
    frequencies: dict[int, int],
    checksum: int = 0,
    method: int = HUFFMAN,
) -> None:
    if method not in (HUFFMAN, STORED):
        raise ValueError("Invalid compression method")

    if original_size < 0:
        raise ValueError("original_size cannot be negative")

    if len(frequencies) > MAX_FREQUENCY_ENTRIES:
        raise ValueError("Too many frequency entries")

    if not 0 <= checksum <= 0xFFFFFFFF:
        raise ValueError(
            "checksum must be a 32-bit unsigned integer"
        )

    file.write(MAGIC)

    # Compression method:
    # 0 = Huffman
    # 1 = Stored/uncompressed
    file.write(bytes([method]))

    file.write(
        original_size.to_bytes(8, "big")
    )

    file.write(
        len(frequencies).to_bytes(2, "big")
    )

    file.write(
        checksum.to_bytes(4, "big")
    )

    for byte_value, frequency in sorted(frequencies.items()):
        if not 0 <= byte_value <= 255:
            raise ValueError(
                "byte value must be between 0 and 255"
            )

        if frequency <= 0:
            raise ValueError(
                "frequency must be positive"
            )

        if frequency > 0xFFFFFFFFFFFFFFFF:
            raise ValueError(
                "frequency is too large"
            )

        file.write(bytes([byte_value]))

        file.write(
            frequency.to_bytes(8, "big")
        )


def read_header(file) -> CompressionHeader:
    magic = file.read(4)

    if magic != MAGIC:
        raise ValueError("Invalid CompressX file")

    # Read compression method.
    method_bytes = file.read(1)

    if len(method_bytes) != 1:
        raise ValueError("Truncated header")

    method = method_bytes[0]

    if method not in (HUFFMAN, STORED):
        raise ValueError("Unknown compression method")

    # Read original file size.
    original_size_bytes = file.read(8)

    if len(original_size_bytes) != 8:
        raise ValueError("Truncated header")

    original_size = int.from_bytes(
        original_size_bytes,
        "big",
    )

    # Read frequency-table entry count.
    entry_count_bytes = file.read(2)

    if len(entry_count_bytes) != 2:
        raise ValueError("Truncated header")

    entry_count = int.from_bytes(
        entry_count_bytes,
        "big",
    )

    if entry_count > MAX_FREQUENCY_ENTRIES:
        raise ValueError(
            "Invalid frequency entry count"
        )

    # Read checksum.
    checksum_bytes = file.read(CHECKSUM_SIZE)

    if len(checksum_bytes) != CHECKSUM_SIZE:
        raise ValueError("Truncated checksum")

    checksum = int.from_bytes(
        checksum_bytes,
        "big",
    )

    # Read frequency table.
    frequencies: dict[int, int] = {}

    for _ in range(entry_count):
        byte_value_bytes = file.read(1)

        if len(byte_value_bytes) != 1:
            raise ValueError(
                "Truncated frequency table"
            )

        byte_value = byte_value_bytes[0]

        frequency_bytes = file.read(8)

        if len(frequency_bytes) != 8:
            raise ValueError(
                "Truncated frequency table"
            )

        frequency = int.from_bytes(
            frequency_bytes,
            "big",
        )

        if frequency == 0:
            raise ValueError(
                "Frequency cannot be zero"
            )

        if byte_value in frequencies:
            raise ValueError(
                "Duplicate byte value"
            )

        frequencies[byte_value] = frequency

    return CompressionHeader(
        original_size=original_size,
        frequencies=frequencies,
        checksum=checksum,
        method=method,
    )