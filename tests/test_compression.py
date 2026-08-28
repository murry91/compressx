import io
import pytest
from compressx.format import CompressionHeader, read_header, write_header, HUFFMAN, STORED
from compressx.compressor import compress_file
from compressx.utils import compression_ratio, space_saving
from compressx.decompressor import decompress_file

def test_write_and_read_header():
    frequencies = {
        65: 3,
        66: 1,
        78: 2,
    }

    buffer = io.BytesIO()

    write_header(
        buffer,
        original_size=6,
        frequencies=frequencies,
    )

    buffer.seek(0)

    header = read_header(buffer)

    assert header == CompressionHeader(
        original_size=6,
        frequencies=frequencies,
    )


def test_invalid_magic():
    buffer = io.BytesIO(b"BAD!")

    with pytest.raises(ValueError, match="Invalid CompressX file"):
        read_header(buffer)


def test_truncated_header():
    buffer = io.BytesIO(b"CX02")

    with pytest.raises(ValueError, match="Truncated header"):
        read_header(buffer)


def test_invalid_byte_value():
    buffer = io.BytesIO()

    with pytest.raises(ValueError):
        write_header(
            buffer,
            original_size=1,
            frequencies={256: 1},
        )


def test_invalid_frequency():
    buffer = io.BytesIO()

    with pytest.raises(ValueError):
        write_header(
            buffer,
            original_size=1,
            frequencies={65: 0},
        )

def test_compress_file(tmp_path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.cx"

    original_data = b"BANANA BANANA BANANA"

    input_file.write_bytes(original_data)

    compress_file(input_file, output_file)

    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_compression_ratio():
    assert compression_ratio(1000, 500) == 0.5


def test_space_saving():
    assert space_saving(1000, 500) == 50.0


def test_empty_compression_stats():
    assert compression_ratio(0, 0) == 0.0
    assert space_saving(0, 0) == 0.0

def test_decompress_invalid_file(tmp_path):
    compressed_file = tmp_path / "invalid.cx"
    output_file = tmp_path / "output.bin"

    compressed_file.write_bytes(b"THIS IS NOT A COMPRESSX FILE")

    with pytest.raises(ValueError, match="Invalid CompressX file"):
        decompress_file(compressed_file, output_file)

def test_decompress_truncated_file(tmp_path):
    compressed_file = tmp_path / "truncated.cx"
    output_file = tmp_path / "output.bin"

    compressed_file.write_bytes(b"CX02")

    with pytest.raises(ValueError, match="Truncated header"):
        decompress_file(compressed_file, output_file)

def test_decompress_corrupted_data(tmp_path):
    input_file = tmp_path / "input.txt"
    compressed_file = tmp_path / "compressed.cx"
    corrupted_file = tmp_path / "corrupted.cx"
    output_file = tmp_path / "output.txt"

    input_file.write_bytes(b"BANANA " * 100)

    compress_file(input_file, compressed_file)

    data = bytearray(compressed_file.read_bytes())

    # Corrupt the last byte of the compressed stream.
    data[-1] ^= 0xFF

    corrupted_file.write_bytes(data)

    with pytest.raises(
        ValueError,
        match="Checksum mismatch",
    ):
        decompress_file(corrupted_file, output_file)

def test_huffman_method_roundtrip():
    buffer = io.BytesIO()

    frequencies = {65: 10, 66: 5}

    write_header(
        buffer,
        original_size=15,
        frequencies=frequencies,
        checksum=123,
        method=HUFFMAN,
    )

    buffer.seek(0)

    header = read_header(buffer)

    assert header.original_size == 15
    assert header.frequencies == frequencies
    assert header.checksum == 123
    assert header.method == HUFFMAN


def test_stored_method_roundtrip():
    buffer = io.BytesIO()

    write_header(
        buffer,
        original_size=100,
        frequencies={},
        checksum=456,
        method=STORED,
    )

    buffer.seek(0)

    header = read_header(buffer)

    assert header.original_size == 100
    assert header.frequencies == {}
    assert header.checksum == 456
    assert header.method == STORED


def test_invalid_compression_method():
    buffer = io.BytesIO()

    with pytest.raises(ValueError, match="Invalid compression method"):
        write_header(
            buffer,
            original_size=100,
            frequencies={},
            checksum=0,
            method=99,
        )


def test_invalid_method_in_header():
    buffer = io.BytesIO()

    write_header(
        buffer,
        original_size=0,
        frequencies={},
        checksum=0,
        method=STORED,
    )

    data = bytearray(buffer.getvalue())

    # Method is immediately after the 4-byte MAGIC.
    data[4] = 99

    buffer = io.BytesIO(bytes(data))

    with pytest.raises(ValueError, match="Unknown compression method"):
        read_header(buffer)

def test_compressor_selects_huffman(tmp_path):
    input_file = tmp_path / "input.bin"
    compressed_file = tmp_path / "compressed.cx"

    # Highly repetitive data should benefit from Huffman coding.
    input_file.write_bytes(b"A" * 10000)

    compress_file(input_file, compressed_file)

    with open(compressed_file, "rb") as file:
        header = read_header(file)

    assert header.method == HUFFMAN


def test_compressor_selects_stored_for_random_data(tmp_path):
    input_file = tmp_path / "input.bin"
    compressed_file = tmp_path / "compressed.cx"

    # Data containing all byte values repeatedly should not
    # benefit from Huffman coding.
    data = bytes(range(256)) * 40
    input_file.write_bytes(data)

    compress_file(input_file, compressed_file)

    with open(compressed_file, "rb") as file:
        header = read_header(file)

    assert header.method == STORED


def test_compressor_selects_stored_for_empty_file(tmp_path):
    input_file = tmp_path / "empty.bin"
    compressed_file = tmp_path / "compressed.cx"

    input_file.write_bytes(b"")

    compress_file(input_file, compressed_file)

    with open(compressed_file, "rb") as file:
        header = read_header(file)

    assert header.method == STORED