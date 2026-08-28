from compressx.frequency import calculate_frequencies
from compressx.huffman_node import HuffmanNode
from compressx.huffman import build_huffman_tree, generate_codes, encode_data, decode_data, decode_data_fast
from compressx.bitstream import BitStreamWriter, BitStreamReader

def test_empty_data():
    assert calculate_frequencies(b"") == {}


def test_single_byte():
    assert calculate_frequencies(b"A") == {
        65: 1,
    }


def test_repeated_bytes():
    assert calculate_frequencies(b"BANANA") == {
        66: 1,
        65: 3,
        78: 2,
    }


def test_all_bytes():
    data = bytes(range(256))

    frequencies = calculate_frequencies(data)

    assert len(frequencies) == 256

    for byte_value in range(256):
        assert frequencies[byte_value] == 1


def test_leaf_node():
    node = HuffmanNode(frequency=5, byte_value=65)

    assert node.frequency == 5
    assert node.byte_value == 65
    assert node.left is None
    assert node.right is None
    assert node.is_leaf


def test_internal_node():
    left = HuffmanNode(frequency=3, byte_value=65)
    right = HuffmanNode(frequency=2, byte_value=66)

    parent = HuffmanNode(
        frequency=5,
        left=left,
        right=right,
    )

    assert parent.frequency == 5
    assert parent.byte_value is None
    assert parent.left is left
    assert parent.right is right
    assert not parent.is_leaf

def test_empty_huffman_tree():
    assert build_huffman_tree({}) is None


def test_single_symbol_tree():
    frequencies = {
        65: 5,
    }

    root = build_huffman_tree(frequencies)

    assert root is not None
    assert root.is_leaf
    assert root.byte_value == 65
    assert root.frequency == 5


def test_huffman_tree():
    frequencies = {
        65: 3,  # A
        78: 2,  # N
        66: 1,  # B
    }

    root = build_huffman_tree(frequencies)

    assert root is not None
    assert not root.is_leaf
    assert root.frequency == 6

    assert root.left is not None
    assert root.right is not None

def test_generate_codes():
    frequencies = {
        65: 3,  # A
        78: 2,  # N
        66: 1,  # B
    }

    root = build_huffman_tree(frequencies)
    codes = generate_codes(root)

    assert set(codes.keys()) == {65, 78, 66}

    # Every symbol must have a non-empty code.
    assert all(code for code in codes.values())

    # Huffman codes must be prefix-free.
    for byte_a, code_a in codes.items():
        for byte_b, code_b in codes.items():
            if byte_a != byte_b:
                assert not code_b.startswith(code_a)


def test_generate_code_for_single_symbol():
    frequencies = {
        65: 10,
    }

    root = build_huffman_tree(frequencies)
    codes = generate_codes(root)

    assert codes == {
        65: "0",
    }


def test_generate_codes_for_empty_tree():
    assert generate_codes(None) == {}


def test_encode_data():
    data = b"BANANA"

    frequencies = calculate_frequencies(data)
    root = build_huffman_tree(frequencies)
    codes = generate_codes(root)

    writer = BitStreamWriter()

    encode_data(data, codes, writer)

    encoded = writer.get_bytes()

    assert len(encoded) > 0

def test_huffman_roundtrip():
    data = b"BANANA"

    frequencies = calculate_frequencies(data)
    root = build_huffman_tree(frequencies)
    codes = generate_codes(root)

    writer = BitStreamWriter()
    encode_data(data, codes, writer)

    encoded = writer.get_bytes()

    reader = BitStreamReader(encoded)
    decoded = decode_data(reader, root, len(data))

    assert decoded == data

def test_huffman_roundtrip_empty():
    data = b""

    frequencies = calculate_frequencies(data)
    root = build_huffman_tree(frequencies)
    codes = generate_codes(root)

    writer = BitStreamWriter()
    encode_data(data, codes, writer)

    encoded = writer.get_bytes()

    reader = BitStreamReader(encoded)
    decoded = decode_data(reader, root, len(data))

    assert decoded == data

def test_huffman_fast_roundtrip():
    data = b"BANANA HUFFMAN " * 100

    frequencies = calculate_frequencies(data)
    root = build_huffman_tree(frequencies)
    codes = generate_codes(root)

    writer = BitStreamWriter()
    encode_data(data, codes, writer)

    compressed = writer.get_bytes()

    reader = BitStreamReader(compressed)

    restored = decode_data_fast(
        reader,
        root,
        len(data),
    )

    assert restored == data