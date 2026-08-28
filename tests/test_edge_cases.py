from compressx.compressor import compress_file
from compressx.decompressor import decompress_file


def roundtrip(tmp_path, data: bytes):
    input_file = tmp_path / "input.bin"
    compressed_file = tmp_path / "compressed.cx"
    restored_file = tmp_path / "restored.bin"

    input_file.write_bytes(data)

    compress_file(input_file, compressed_file)
    decompress_file(compressed_file, restored_file)

    assert restored_file.read_bytes() == data


def test_empty_file(tmp_path):
    roundtrip(tmp_path, b"")


def test_one_byte(tmp_path):
    roundtrip(tmp_path, b"A")


def test_repeated_byte(tmp_path):
    roundtrip(tmp_path, b"A" * 10_000)


def test_all_byte_values(tmp_path):
    roundtrip(tmp_path, bytes(range(256)))


def test_all_byte_values_repeated(tmp_path):
    roundtrip(tmp_path, bytes(range(256)) * 100)


def test_binary_data(tmp_path):
    data = bytes(range(256)) * 1_000
    roundtrip(tmp_path, data)


def test_unicode_text(tmp_path):
    data = "CompressX — Huffman compression 🚀\n" * 1_000
    roundtrip(tmp_path, data.encode("utf-8"))
    