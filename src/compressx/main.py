import argparse
import sys
from pathlib import Path

from compressx.compressor import compress_file
from compressx.decompressor import decompress_file
from compressx.utils import compression_ratio, space_saving

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compressx",
        description="Compress and decompress files using Huffman coding.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    compress_parser = subparsers.add_parser(
        "compress",
        help="Compress a file.",
    )

    compress_parser.add_argument(
        "input",
        help="Input file.",
    )

    compress_parser.add_argument(
        "output",
        help="Output .cx file.",
    )

    decompress_parser = subparsers.add_parser(
        "decompress",
        help="Decompress a .cx file.",
    )

    decompress_parser.add_argument(
        "input",
        help="Input .cx file.",
    )

    decompress_parser.add_argument(
        "output",
        help="Output file.",
    )

    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(
            f"Error: input file does not exist: {input_path}",
            file=sys.stderr,
        )
        return 1

    if not input_path.is_file():
        print(
            f"Error: input path is not a file: {input_path}",
            file=sys.stderr,
        )
        return 1

    if input_path.resolve() == output_path.resolve():
        print(
            "Error: input and output files must be different.",
            file=sys.stderr,
        )
        return 1

    if output_path.exists():
        print(
            f"Error: output file already exists: {output_path}",
            file=sys.stderr,
        )
        return 1

    try:
        if args.command == "compress":
            compress_file(input_path, output_path)

            original_size = input_path.stat().st_size
            compressed_size = output_path.stat().st_size

            ratio = compression_ratio(original_size, compressed_size)
            saving = space_saving(original_size, compressed_size)

            print(f"Compressed successfully: {output_path}")
            print(f"Original size:   {original_size:,} bytes")
            print(f"Compressed size: {compressed_size:,} bytes")
            print(f"Compression ratio: {ratio:.2%}")
            print(f"Space saved:       {saving:.2f}%")

        elif args.command == "decompress":
            decompress_file(input_path, output_path)

    except (OSError, ValueError, EOFError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Success: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())