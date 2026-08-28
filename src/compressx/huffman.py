import heapq
from itertools import count

from compressx.huffman_node import HuffmanNode
from compressx.bitstream import BitStreamWriter, BitStreamReader


def build_huffman_tree(
    frequencies: dict[int, int],
) -> HuffmanNode | None:
    if not frequencies:
        return None

    counter = count()

    heap = [
        (
            frequency,
            next(counter),
            HuffmanNode(frequency, byte_value),
        )
        for byte_value, frequency in sorted(frequencies.items())
    ]

    heapq.heapify(heap)

    while len(heap) > 1:
        frequency1, _, node1 = heapq.heappop(heap)
        frequency2, _, node2 = heapq.heappop(heap)

        parent = HuffmanNode(
            frequency=frequency1 + frequency2,
            left=node1,
            right=node2,
        )

        heapq.heappush(
            heap,
            (
                parent.frequency,
                next(counter),
                parent,
            ),
        )

    return heap[0][2]


def generate_codes(root: HuffmanNode | None) -> dict[int, str]:
    if root is None:
        return {}

    codes: dict[int, str] = {}

    def walk(node: HuffmanNode, code: str) -> None:
        if node.is_leaf:
            codes[node.byte_value] = code or "0"
            return

        if node.left is not None:
            walk(node.left, code + "0")

        if node.right is not None:
            walk(node.right, code + "1")

    walk(root, "")

    return codes


def encode_data(data, codes, writer):
    for byte_value in data:
        code = codes[byte_value]

        if isinstance(code, tuple):
            code_value, code_length = code

            writer.write_code_value(
                code_value,
                code_length,
            )
        else:
            writer.write_code(code)


def encode_data_fast(data, codes, writer):
    for byte_value in data:
        code_value, code_length = codes[byte_value]

        writer.write_code_value(
            code_value,
            code_length,
        )


def encode_file(
    path,
    codes,
    writer,
    chunk_size=1024 * 1024,
):
    with open(path, "rb") as file:
        while chunk := file.read(chunk_size):
            for byte_value in chunk:
                code_value, code_length = codes[byte_value]

                writer.buffer = (
                    writer.buffer << code_length
                ) | code_value

                writer.bit_count += code_length

                while writer.bit_count >= 8:
                    writer.bit_count -= 8

                    writer.data.append(
                        (writer.buffer >> writer.bit_count) & 0xFF
                    )

                if writer.bit_count:
                    writer.buffer &= (
                        (1 << writer.bit_count) - 1
                    )
                else:
                    writer.buffer = 0

def decode_data(
    reader: BitStreamReader,
    root: HuffmanNode | None,
    original_size: int,
) -> bytes:
    if original_size == 0:
        return b""

    if root is None:
        raise ValueError(
            "Huffman tree is required for non-empty data"
        )

    # Special case: only one unique byte exists.
    if root.is_leaf:
        if root.byte_value is None:
            raise ValueError("Leaf node has no byte value")

        return bytes([root.byte_value]) * original_size

    result = bytearray()
    decoded = 0

    while decoded < original_size:
        node = root

        while node.left is not None or node.right is not None:
            bit = reader.read_bit()

            if bit == 0:
                if node.left is None:
                    raise ValueError("Invalid Huffman tree")

                node = node.left

            else:
                if node.right is None:
                    raise ValueError("Invalid Huffman tree")

                node = node.right

        if node.byte_value is None:
            raise ValueError("Leaf node has no byte value")

        result.append(node.byte_value)
        decoded += 1

    return bytes(result)

def decode_data_fast(
    reader: BitStreamReader,
    root: HuffmanNode | None,
    expected_size: int,
) -> bytes:
    if expected_size == 0:
        return b""

    if root is None:
        raise ValueError(
            "Huffman tree is required for non-empty data"
        )

    # Special case: only one unique byte exists.
    if root.is_leaf:
        if root.byte_value is None:
            raise ValueError("Leaf node has no byte value")

        return bytes([root.byte_value]) * expected_size

    output = bytearray()
    node = root
    decoded = 0

    while decoded < expected_size:
        current_byte = reader.read_byte()

        for shift in range(7, -1, -1):
            bit = (current_byte >> shift) & 1

            if bit == 0:
                if node.left is None:
                    raise ValueError("Invalid Huffman tree")

                node = node.left
            else:
                if node.right is None:
                    raise ValueError("Invalid Huffman tree")

                node = node.right

            if node.is_leaf:
                if node.byte_value is None:
                    raise ValueError("Leaf node has no byte value")

                output.append(node.byte_value)
                decoded += 1
                node = root

                if decoded == expected_size:
                    break

    return bytes(output)

def generate_code_values(root):
    codes = {}

    def walk(node, code_value, code_length):

        if node is None:
            return

        if node.is_leaf:
            if node.byte_value is None:
                raise ValueError("Leaf node has no byte value")

            # A single-symbol tree needs at least one bit.
            if code_length == 0:
                codes[node.byte_value] = (0, 1)
            else:
                codes[node.byte_value] = (
                    code_value,
                    code_length,
                )

            return

        walk(
            node.left,
            code_value << 1,
            code_length + 1,
        )

        walk(
            node.right,
            (code_value << 1) | 1,
            code_length + 1,
        )

    walk(root, 0, 0)

    return codes