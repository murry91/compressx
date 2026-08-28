from pathlib import Path

from compressx.bitstream import BitStreamReader
from compressx.format import HUFFMAN, STORED, read_header
from compressx.huffman import build_huffman_tree, decode_data_fast
from compressx.utils import calculate_checksum


def decompress_file(
    input_path: str | Path,
    output_path: str | Path,
) -> None:
    with open(input_path, "rb") as input_file:
        header = read_header(input_file)

        compressed_data = input_file.read()

    # STORED mode:
    # The data is already uncompressed, so there is no
    # Huffman tree to build.
    if header.method == STORED:
        if len(compressed_data) != header.original_size:
            raise ValueError(
                "Stored data size does not match original size"
            )

        data = compressed_data

    # HUFFMAN mode:
    # Rebuild the Huffman tree and decode the bitstream.
    elif header.method == HUFFMAN:
        root = build_huffman_tree(header.frequencies)

        reader = BitStreamReader(compressed_data)

        data = decode_data_fast(
            reader,
            root,
            header.original_size,
        )

    else:
        raise ValueError(
            f"Unknown compression method: {header.method}"
        )

    # Verify data integrity for both methods.
    actual_checksum = calculate_checksum(data)

    if actual_checksum != header.checksum:
        raise ValueError(
            "Checksum mismatch: compressed file may be corrupted"
        )

    with open(output_path, "wb") as output_file:
        output_file.write(data)