# CompressX

A lossless file compression tool written in Python using Huffman coding.

CompressX operates on raw bytes, allowing it to compress text and binary files while preserving the original data exactly.

## Features

* Lossless Huffman compression
* Bit-level encoding and decoding
* Automatic selection between Huffman and stored mode
* CRC32 integrity verification
* Support for arbitrary binary data
* Empty-file handling
* Single-symbol optimization
* Command-line interface
* Automated test suite
* Benchmarking and profiling

## Installation

Clone the repository and install the package in editable mode:

```bash
pip install -e .
```

Verify the CLI:

```bash
compressx --help
```

## Usage

### Compress a file

```bash
compressx compress input.txt output.cx
```

### Decompress a file

```bash
compressx decompress output.cx restored.txt
```

CompressX preserves the original bytes exactly during decompression.

## How It Works

The compression pipeline is:

1. Read the input file and analyze byte frequencies.
2. Build a Huffman tree from the frequency table.
3. Generate Huffman codes.
4. Convert codes into integer values and bit lengths.
5. Encode the input into a bitstream.
6. Store the required metadata and integrity information in the `.cx` format.
7. Compare the Huffman result with stored mode and select the smaller representation.

During decompression, CompressX reads the `.cx` header, reconstructs the required Huffman information, decodes the bitstream, and verifies the resulting data using CRC32.

## File Types

CompressX works with files as byte streams rather than relying on a particular file format.

It can therefore process:

* `.txt`
* `.pdf`
* `.jpg`
* `.png`
* `.csv`
* `.bin`
* and other binary or text files

Files that are already compressed, such as many JPEG, PNG, ZIP, and similar formats, generally provide little opportunity for Huffman compression. CompressX can use stored mode when Huffman compression would not reduce the file size.

## Example

```text
Input:
maju challan.pdf

        ↓

CompressX

        ↓

maju challan.cx

        ↓

Decompress

        ↓

maju challan_restored.pdf
```

The original and restored files can be verified using SHA-256:

```powershell
Get-FileHash "maju challan.pdf"
Get-FileHash "maju challan_restored.pdf"
```

Identical hashes confirm that the decompression reproduced the original bytes exactly.

## Performance

Benchmark results on 1 MB-scale test data:

| Input              |    Original |  Compressed |  Ratio | Space Saved |
| ------------------ | ----------: | ----------: | -----: | ----------: |
| Highly repetitive  | 1,000,000 B |   125,028 B | 12.50% |      87.50% |
| English-like text  |   900,000 B |   484,003 B | 53.78% |      46.22% |
| All byte values    | 1,024,000 B | 1,024,019 B |  ~100% |         ~0% |
| Random data        | 1,000,000 B | 1,000,019 B |  ~100% |         ~0% |
| Single-symbol data | 1,000,000 B |   125,028 B | 12.50% |      87.50% |

For incompressible data, the stored representation avoids wasting space on Huffman encoding.

## Optimization

The encoder uses integer Huffman code values and code lengths instead of repeatedly converting codes to strings during encoding.

Profiling showed compression time decreasing from approximately 1.3 seconds to approximately 0.62 seconds on the profiling workload after this optimization.

The main remaining compression cost is Huffman encoding, followed by byte-frequency analysis.

## Testing

The project includes automated tests covering:

* Bitstream reading and writing
* Huffman tree construction
* Code generation
* Encoding and decoding
* Compression and decompression
* Corrupted data handling
* Empty files
* Repeated-byte data
* Unicode text
* Binary data
* Huffman/stored method selection
* Round-trip correctness

Current test result:

```text
52 passed
```

## Project Structure

```text
compressx/
├── benchmarks/
│   └── benchmark.py
├── src/
│   └── compressx/
│       ├── bitstream.py
│       ├── compressor.py
│       ├── decompressor.py
│       ├── file_io.py
│       ├── format.py
│       ├── frequency.py
│       ├── huffman.py
│       ├── huffman_node.py
│       ├── main.py
│       └── utils.py
├── tests/
├── profile_compression.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Limitations

CompressX is designed as a learning and engineering project rather than as a replacement for production compression formats such as ZIP, gzip, or modern archival formats.

Compression effectiveness depends heavily on the input data. Files that are already compressed may not become smaller.

## Future Improvements

Possible future improvements include:

* Additional performance optimization
* More extensive benchmarking across file types
* Improved command-line inspection and reporting
* Additional robustness testing
* Further optimization of bitstream operations

## License

See `LICENSE` for licensing information.
