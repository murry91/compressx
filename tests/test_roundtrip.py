from compressx.compressor import compress_file
from compressx.decompressor import decompress_file


def test_compress_decompress_roundtrip(tmp_path):
    input_file = tmp_path / "input.txt"
    compressed_file = tmp_path / "compressed.cx"
    restored_file = tmp_path / "restored.txt"

    original_data = (
        b"BANANA BANANA BANANA "
        b"HUFFMAN HUFFMAN HUFFMAN"
    )

    input_file.write_bytes(original_data)

    compress_file(input_file, compressed_file)
    decompress_file(compressed_file, restored_file)

    restored_data = restored_file.read_bytes()

    assert restored_data == original_data
def test_empty_file_roundtrip(tmp_path):
    input_file = tmp_path / "empty.txt"
    compressed_file = tmp_path / "empty.cx"
    restored_file = tmp_path / "restored.txt"

    original_data = b""

    input_file.write_bytes(original_data)

    compress_file(input_file, compressed_file)
    decompress_file(compressed_file, restored_file)

    assert restored_file.read_bytes() == original_data

def test_empty_file_roundtrip(tmp_path):
    input_file = tmp_path / "empty.txt"
    compressed_file = tmp_path / "empty.cx"
    restored_file = tmp_path / "restored.txt"

    original_data = b""

    input_file.write_bytes(original_data)

    compress_file(input_file, compressed_file)
    decompress_file(compressed_file, restored_file)

    assert restored_file.read_bytes() == original_data

def test_binary_roundtrip(tmp_path):
    input_file = tmp_path / "binary.bin"
    compressed_file = tmp_path / "binary.cx"
    restored_file = tmp_path / "restored.bin"

    original_data = bytes(range(256)) * 10

    input_file.write_bytes(original_data)

    compress_file(input_file, compressed_file)
    decompress_file(compressed_file, restored_file)

    assert restored_file.read_bytes() == original_data