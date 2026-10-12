# Offline tools

The first worker owns `sxi_inspect.py` and tests (see `analysis/tasks/A1-sxi-container.md`). Any tool must be deterministic, bounded, read-only, and must never communicate with physical hardware. Store generated data in ignored `work/`.

## SXI inspection

From the repository root, after verifying and staging the supplied firmware:

```sh
python tools/sxi_inspect.py work/firmware/ipv3_160W_V3.5.SXI > work/A1-inspection.json
python -m unittest discover -s tests -v
```

The CLI checks the expected size and SHA-256 before parsing. Defaults are the
56,009-byte A1 sample and its recorded hash. It opens only regular files for
reading and emits deterministic JSON on stdout. Errors produce a diagnostic on
stderr, no JSON, and exit status 2. Input bytes are never written or executed.

Output includes first/last 64 bytes, ASCII strings with offsets, global and
per-chunk 256-entry histograms and Shannon entropy, overlapping repeated patterns,
limited encoding/checksum probes, and an empirical suffix token grammar. Offsets
are zero-based decimal integers; ranges end exclusively. Histogram index is the
byte value. Candidate projections are summarized by size/hash only; marker
semantics and firmware decoding remain unverified. See the
[A1 evidence report](../analysis/reports/A1-container.md).

Input is capped at 262,144 bytes, chunks at 256..65,536 bytes (default 4,096),
strings at 128 results and 96 characters each (minimum length default 6), and
patterns at eight results per width (4, 8, 16 bytes), each with eight offsets.
Full-file string/pattern counts and omitted-result counts are reported. Pattern
counts include overlapping occurrences. Counter sizes, reads and output are
bounded by these hard limits; no decompression is attempted.

For another research input, explicitly supply both `--expected-size N` and
`--expected-sha256 HASH`. `--chunk-size` and `--min-string` only change reporting.
Unknown headers and incomplete candidate grammars are diagnostic results, not a
claim of a valid SXI container. This inspector establishes no ISA or device-write
path.

## Lossless SXI tokens

```sh
python tools/sxi_tokens.py work/firmware/ipv3_160W_V3.5.SXI > work/A1b-tokens.json
python -m unittest discover -s tests -v
```

The size/hash verification gate and 262,144-byte input cap are shared with the
A1 inspector. The independent parser strictly tokenizes from `0x160` (override
with `--start`, decimal or `0x` notation), retaining the entire opaque prefix.
`decode(bytes, start)` returns immutable tokens with absolute source offsets,
classes and raw bytes. `encode(document)` verifies contiguous offsets, valid
classes and exact coverage and reconstructs the original SXI. It writes no files.
Use these APIs only for representation recovery; no firmware modification or
executable image is implied. Direct API calls accept synthetic bytes without a
hash gate; the CLI always verifies first.

JSON contains all tokens, all marker positions and four-token contexts, spacing
and residue distributions in four diagnostic coordinates, both projection
size/hashes, and a plain integer scan of the first 352 prefix bytes. Error status
is 2 with no JSON. Output is deterministic and bounded by the byte cap; prefix
scan widths and residue moduli are fixed. Generated reports belong in `work/`.
Neither projection is validated firmware. See the [A1b report](../analysis/reports/A1b-encoding.md).

The original-sample integration test checks the ignored staged artifact when
present; absent artifacts cause an explicit skip, while a present wrong artifact
fails. Full acceptance requires that test to run and pass.
