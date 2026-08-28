class BitStreamWriter:
    def __init__(self):
        self.buffer = 0
        self.bit_count = 0
        self.data = bytearray()

    def write_bit(self, bit: int) -> None:
        if bit not in (0, 1):
            raise ValueError("bit must be 0 or 1")

        self.buffer = (self.buffer << 1) | bit
        self.bit_count += 1

        if self.bit_count == 8:
            self.data.append(self.buffer)
            self.buffer = 0
            self.bit_count = 0

    def flush(self) -> None:
        if self.bit_count > 0:
            self.buffer <<= 8 - self.bit_count
            self.data.append(self.buffer)
            self.buffer = 0
            self.bit_count = 0

    def get_bytes(self) -> bytes:
        self.flush()
        return bytes(self.data)

    def write_code(self, code: str) -> None:
        if not code:
            return

        value = int(code, 2)
        length = len(code)

        self.buffer = (self.buffer << length) | value
        self.bit_count += length

        while self.bit_count >= 8:
            shift = self.bit_count - 8

            byte_value = (self.buffer >> shift) & 0xFF
            self.data.append(byte_value)

            self.bit_count -= 8

            if self.bit_count == 0:
                self.buffer = 0
            else:
                self.buffer &= (1 << self.bit_count) - 1

    def write_code_value(self, value: int, length: int) -> None:
        if length < 0:
            raise ValueError("length cannot be negative")

        if length == 0:
            return

        if value < 0 or value >= (1 << length):
            raise ValueError("value does not fit in the specified length")

        self.buffer = (self.buffer << length) | value
        self.bit_count += length

        while self.bit_count >= 8:
            self.bit_count -= 8

            self.data.append(
                (self.buffer >> self.bit_count) & 0xFF
            )

        if self.bit_count:
            self.buffer &= (1 << self.bit_count) - 1
        else:
            self.buffer = 0

class BitStreamWriter:
    def __init__(self):
        self.buffer = 0
        self.bit_count = 0
        self.data = bytearray()

    def write_bit(self, bit: int) -> None:
        if bit not in (0, 1):
            raise ValueError("bit must be 0 or 1")

        self.buffer = (self.buffer << 1) | bit
        self.bit_count += 1

        if self.bit_count == 8:
            self.data.append(self.buffer)
            self.buffer = 0
            self.bit_count = 0

    def flush(self) -> None:
        if self.bit_count > 0:
            self.buffer <<= 8 - self.bit_count
            self.data.append(self.buffer)
            self.buffer = 0
            self.bit_count = 0

    def get_bytes(self) -> bytes:
        self.flush()
        return bytes(self.data)

    def write_code(self, code: str) -> None:
        if not code:
            return

        value = int(code, 2)
        length = len(code)

        self.buffer = (self.buffer << length) | value
        self.bit_count += length

        while self.bit_count >= 8:
            shift = self.bit_count - 8

            byte_value = (self.buffer >> shift) & 0xFF
            self.data.append(byte_value)

            self.bit_count -= 8

            if self.bit_count == 0:
                self.buffer = 0
            else:
                self.buffer &= (1 << self.bit_count) - 1

    def write_code_value(self, value: int, length: int) -> None:
        if length < 0:
            raise ValueError("length cannot be negative")

        if length == 0:
            return

        if value < 0 or value >= (1 << length):
            raise ValueError("value does not fit in the specified length")

        self.buffer = (self.buffer << length) | value
        self.bit_count += length

        while self.bit_count >= 8:
            self.bit_count -= 8

            self.data.append(
                (self.buffer >> self.bit_count) & 0xFF
            )

        if self.bit_count:
            self.buffer &= (1 << self.bit_count) - 1
        else:
            self.buffer = 0


class BitStreamReader:
    def __init__(self, data: bytes):
        self.data = data
        self.byte_index = 0
        self.bit_buffer = 0
        self.bits_left = 0

    def read_bit(self) -> int:
        if self.bits_left == 0:
            if self.byte_index >= len(self.data):
                raise EOFError("Unexpected end of bitstream")

            self.bit_buffer = self.data[self.byte_index]
            self.byte_index += 1
            self.bits_left = 8

        self.bits_left -= 1

        return (self.bit_buffer >> self.bits_left) & 1

    def read_byte(self) -> int:
        if self.byte_index >= len(self.data):
            raise EOFError("Unexpected end of bitstream")

        value = self.data[self.byte_index]
        self.byte_index += 1
        return value