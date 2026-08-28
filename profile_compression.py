import cProfile
import pstats
from pathlib import Path

from compressx.compressor import compress_file


input_file = Path("profile_input.bin")
output_file = Path("profile_output.cx")

input_file.write_bytes(b"A" * 1_000_000)

profiler = cProfile.Profile()

profiler.enable()
compress_file(input_file, output_file)
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(20)