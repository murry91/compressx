from compressx.bitstream import BitStreamWriter
from compressx.format import (
    HUFFMAN,
    STORED,
    write_header,
)
from compressx.frequency import analyze_file
from compressx.huffman import (
    build_huffman_tree,
    encode_file,
    generate_code_values,
)


def compress_file(input_path, output_path):
    original_size = input_path.stat().st_size

    frequencies, checksum = analyze_file(input_path)

    # Empty file
    if original_size == 0:
        with open(output_path, "wb") as output_file:
            write_header(
                output_file,
                original_size,
                {},
                checksum,
                STORED,
            )

        return

    # Build Huffman tree and generate codes.
    root = build_huffman_tree(frequencies)
    codes = generate_code_values(root)

    # Calculate the exact number of Huffman bits that will be
    # produced, without actually encoding the file.
    huffman_bits = sum(
        frequencies[byte_value] * code_length
        for byte_value, (_, code_length) in codes.items()
    )

    huffman_data_size = (huffman_bits + 7) // 8

    # Huffman header includes the frequency table.
    huffman_header_size = (
        4 +              # MAGIC
        1 +              # method
        8 +              # original size
        2 +              # frequency entry count
        4 +              # checksum
        len(frequencies) * (1 + 8)
    )

    huffman_total_size = (
        huffman_header_size +
        huffman_data_size
    )

    # Stored mode has no frequency table.
    stored_header_size = (
        4 +              # MAGIC
        1 +              # method
        8 +              # original size
        2 +              # frequency entry count
        4               # checksum
    )

    stored_total_size = (
        stored_header_size +
        original_size
    )

    # Use Huffman only when it actually produces a smaller file.
    if huffman_total_size < stored_total_size:
        writer = BitStreamWriter()

        encode_file(
            input_path,
            codes,
            writer,
        )

        compressed_data = writer.get_bytes()

        with open(output_path, "wb") as output_file:
            write_header(
                output_file,
                original_size,
                frequencies,
                checksum,
                HUFFMAN,
            )

            output_file.write(compressed_data)

    else:
        # Store the original data without Huffman compression.
        with open(input_path, "rb") as input_file:
            original_data = input_file.read()

        with open(output_path, "wb") as output_file:
            write_header(
                output_file,
                original_size,
                {},
                checksum,
                STORED,
            )

            output_file.write(original_data)