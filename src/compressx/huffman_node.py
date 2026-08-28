class HuffmanNode:
    def __init__(
        self,
        frequency: int,
        byte_value: int | None = None,
        left: "HuffmanNode | None" = None,
        right: "HuffmanNode | None" = None,
    ):
        self.frequency = frequency
        self.byte_value = byte_value
        self.left = left
        self.right = right

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None