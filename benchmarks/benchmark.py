import random
import tempfile
import time
from pathlib import Path
import cProfile
import pstats

from compressx.compressor import compress_file
from compressx.decompressor import decompress_file
from compressx.utils import compression_ratio, space_saving


def run_benchmark(name: str, data: bytes):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)

        input_file = temp / "input.bin"
        compressed_file = temp / "compressed.cx"
        restored_file = temp / "restored.bin"

        input_file.write_bytes(data)

        start = time.perf_counter()
        compress_file(input_file, compressed_file)
        compression_time = time.perf_counter() - start

        start = time.perf_counter()
        decompress_file(compressed_file, restored_file)
        decompression_time = time.perf_counter() - start

        original_size = len(data)
        compressed_size = compressed_file.stat().st_size

        # Verify correctness.
        assert restored_file.read_bytes() == data

        return {
            "name": name,
            "original": original_size,
            "compressed": compressed_size,
            "ratio": compression_ratio(
                original_size,
                compressed_size,
            ),
            "saving": space_saving(
                original_size,
                compressed_size,
            ),
            "compression_time": compression_time,
            "decompression_time": decompression_time,
        }


def print_results(results):
    print()
    print(
        f"{'Type':<25}"
        f"{'Original':>12}"
        f"{'Compressed':>12}"
        f"{'Ratio':>10}"
        f"{'Saved':>10}"
        f"{'Comp(s)':>10}"
        f"{'Decomp(s)':>10}"
    )

    print("-" * 99)

    for result in results:
        print(
            f"{result['name']:<25}"
            f"{result['original']:>12,}"
            f"{result['compressed']:>12,}"
            f"{result['ratio']:>9.2%}"
            f"{result['saving']:>9.2f}%"
            f"{result['compression_time']:>10.4f}"
            f"{result['decompression_time']:>10.4f}"
        )


def main():
    random_data = random.Random(42).randbytes(1_000_000)

    test_cases = [
        (
            "Highly repetitive",
            b"A" * 1_000_000,
        ),
        (
            "English-like text",
            (
                b"CompressX is a Huffman compression tool. "
                b"It compresses files using variable-length codes. "
            )
            * 10_000,
        ),
        (
            "All byte values",
            bytes(range(256)) * 4_000,
        ),
        (
            "Random data",
            random_data,
        ),
        (
            "Single-symbol data",
            b"X" * 1_000_000,
        ),
    ]

    results = []
    

    for name, data in test_cases:
        results.append(
            run_benchmark(name, data)
        )

    print_results(results)
    profile_decompression(
    random.Random(42).randbytes(1_000_000)
    )

def profile_decompression(data: bytes):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)

        input_file = temp / "input.bin"
        compressed_file = temp / "compressed.cx"
        restored_file = temp / "restored.bin"

        input_file.write_bytes(data)

        compress_file(
            input_file,
            compressed_file,
        )

        profiler = cProfile.Profile()

        profiler.enable()

        decompress_file(
            compressed_file,
            restored_file,
        )

        profiler.disable()

        print()
        print("========== DECOMPRESSION PROFILING ==========")

        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative")
        stats.print_stats(15)

if __name__ == "__main__":
    main()