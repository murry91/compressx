import pytest

from compressx.bitstream import BitStreamWriter, BitStreamReader


def test_write_eight_bits():
    writer = BitStreamWriter()

    for bit in [1, 0, 1, 1, 0, 0, 1, 0]:
        writer.write_bit(bit)

    assert writer.get_bytes() == b"\xb2"


def test_write_sixteen_bits():
    writer = BitStreamWriter()

    for bit in [1, 0, 1, 1, 0, 0, 1, 0,
                0, 1, 0, 1, 1, 1, 0, 0]:
        writer.write_bit(bit)

    assert writer.get_bytes() == b"\xb2\x5c"


def test_write_partial_byte():
    writer = BitStreamWriter()

    for bit in [1, 0, 1]:
        writer.write_bit(bit)

    assert writer.get_bytes() == b"\xa0"


def test_invalid_bit():
    writer = BitStreamWriter()

    with pytest.raises(ValueError):
        writer.write_bit(2)

def test_read_eight_bits():
    reader = BitStreamReader(b"\xb2")

    bits = [reader.read_bit() for _ in range(8)]

    assert bits == [1, 0, 1, 1, 0, 0, 1, 0]


def test_read_sixteen_bits():
    reader = BitStreamReader(b"\xb2\x5c")

    bits = [reader.read_bit() for _ in range(16)]

    assert bits == [
        1, 0, 1, 1, 0, 0, 1, 0,
        0, 1, 0, 1, 1, 1, 0, 0,
    ]


def test_read_past_end():
    reader = BitStreamReader(b"\xb2")

    for _ in range(8):
        reader.read_bit()

    with pytest.raises(EOFError):
        reader.read_bit()