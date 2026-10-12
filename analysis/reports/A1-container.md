# A1 — SXI container reconnaissance

## Scope and starting point

Starting `main`: **`9bec1434e13065886e9b00ec1641a59c180a6fbe`**, the merge
commit of PR #1. GitHub's `branches/main` response independently confirmed this
SHA and PR #1 metadata confirmed `merged=true`. Local HEAD and cached
`origin/main` also matched. Work branch: `analysis/a1-sxi-container`.

Read `AGENTS.md`, `analysis/tasks/A1-sxi-container.md`, `README.md`,
`firmware/README.md`, `research/evidence-ledger.md`, `analysis/README.md` and
`tools/README.md`. Scope is offline A1 container reconnaissance, a standard-library
read-only inspector, synthetic unit tests and evidence documentation. No hardware,
USB, firmware execution, patching, flashing or architecture analysis occurred.
The shared evidence ledger is unchanged; this report supplies additional A1
evidence without reclassifying its prior entries.

## Mandatory artifact verification and staging — PASS

**OBSERVED, high confidence:** all checks below passed before artifact analysis.

| Custody field | Value |
| --- | --- |
| Supplied source filename | `ipv3_160W_V3.5.SXI` |
| Retrieval | User attachment `sediment://file_0000000029a481fd85e5b7dbaa475783`, downloaded with the attachment download tool |
| Downloaded source path | `/workspace/attachments/fa48f1ac-6645-45c3-87a2-d4f210150438/ipv3_160W_V3.5.SXI` |
| Staged path, relative to repository root | `work/firmware/ipv3_160W_V3.5.SXI` |
| Source and staged byte count | **56,009** |
| Source and staged SHA-256 | **`ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d`** |
| Raw readability | Both files opened with `rb`; source checked before copy and staged bytes checked afterward |
| Copy operation | `shutil.copyfile`; existing destination would have caused a stop |
| Git exclusion | `git check-ignore -v` reports `.gitignore:2:work/`; `git ls-files -- work/firmware/ipv3_160W_V3.5.SXI` is empty |

The historical extracted filename in the scaffold is
`Only for IPV3 160W Upgrade Software_20141126_V3.5.SXI`. The supplied filename
differs; byte identity is independently established by the hash. The historical
RAR was not supplied or inspected in this task, so archive provenance is still
the scaffold's prior report. This sample is an upgrade package; it does not
establish the physical unit's factory firmware identity.

The executed staging gate was equivalent to this reproducible command (set
`SOURCE` to the downloaded attachment; the command refuses an existing destination):

```sh
SOURCE=/workspace/attachments/fa48f1ac-6645-45c3-87a2-d4f210150438/ipv3_160W_V3.5.SXI
python - "$SOURCE" <<'PY'
import hashlib, pathlib, shutil, subprocess, sys
src = pathlib.Path(sys.argv[1])
expected = 'ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d'
with src.open('rb') as f:
    data = f.read(56010)
if len(data) != 56009 or hashlib.sha256(data).hexdigest() != expected:
    raise SystemExit('FAIL: source acceptance criteria not met')
dst = pathlib.Path('work/firmware') / src.name
dst.parent.mkdir(parents=True, exist_ok=True)
if dst.exists():
    raise SystemExit('Refusing to replace existing staged file')
shutil.copyfile(src, dst)
with dst.open('rb') as f:
    staged = f.read(56010)
assert len(staged) == 56009
assert hashlib.sha256(staged).hexdigest() == expected
subprocess.run(['git', 'check-ignore', '-v', str(dst)], check=True)
assert not subprocess.check_output(['git', 'ls-files', '--', str(dst)]).strip()
print('PASS', dst, len(staged), hashlib.sha256(staged).hexdigest())
PY
```

The observed final line was:

```text
PASS work/firmware/ipv3_160W_V3.5.SXI 56009 ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d
```

The source and staged file were rehashed after all analysis and tests; both still
matched. Neither binary nor generated JSON/projection data is included in the PR.

## Reproduction and tool behavior

Run from the repository root using Python 3.12.14 (the validation environment):

```sh
python tools/sxi_inspect.py work/firmware/ipv3_160W_V3.5.SXI > work/A1-inspection.json
python tools/sxi_inspect.py work/firmware/ipv3_160W_V3.5.SXI > work/A1-inspection-repeat.json
cmp work/A1-inspection.json work/A1-inspection-repeat.json
sha256sum work/A1-inspection.json
python -m unittest discover -s tests -v
git diff --check
git check-ignore -v work/firmware/ipv3_160W_V3.5.SXI
git ls-files -- work/firmware/
```

**OBSERVED:** both inspector runs exited 0, `cmp` exited 0 with no output;
JSON SHA-256 was
`ec317e233a9f64280a45a14c432de86c17ff15d68410192b24d6bcc66687f1bb`.
The JSON has no timestamps or local filenames, so moving an identical file does
not change the output. Float entropy is rounded to six decimal places; this exact
output hash is scoped to the tested Python version and default options.

The inspector enforces size/hash **before** any parsing, reads at most 262,145
bytes, accepts at most 262,144 bytes and rejects nonregular files. Empty, missing,
oversized or mismatching files and invalid reporting options exit 2, emit stderr
diagnostics and emit no JSON. A source metadata change during reading also fails.
Unknown headers and rejected hypothesis grammars are explicitly reported; this is
an inspection tool, not a complete SXI validator. No decompression or execution
is attempted. Histogram, string, pattern and marker reporting limits are recorded
in the JSON and `tools/README.md`. All pattern counters are bounded by the hard
input cap, not by arbitrary file size.

The tests use synthetic fixtures only. They verify known histograms/entropy,
chunk boundaries, EOF strings and truncation caps, overlapping patterns and tie
ordering, hash-before-parse failure, malformed token pairs and truncated tokens,
the standard `123456789` CRC-32 vector, deterministic CLI output, unchanged input
bytes/mtime, missing/oversized files, bad options and nonblocking FIFO rejection.

```text
Ran 20 tests
OK
```

## Byte layout and high-confidence regions

All offsets below are zero-based. Ranges use an **exclusive end**. These are
observations on this single sample; field meanings are not established.

| Range | Classification and evidence | Confidence |
| --- | --- | --- |
| `0x0000..0x0018` | **OBSERVED:** exactly 24 ASCII bytes `v20140808-SXi-YiHiEcigar` | High |
| `0x0018..0x0020` | **OBSERVED:** eight `00` bytes | High |
| `0x0020..0x0080` | **OBSERVED:** non-ASCII prefix, including repeated `c1 ce e3` at `0x20`, `0x23`, `0x40`, `0x43`, `0x46`, `0x49`, `0x60`, `0x63` | High for bytes; meaning unknown |
| `0x0080..0x00a0` | **OBSERVED:** prefix `01 00 00 60 00 8b 00 71 53 33 01 08` at `0x80`; 20 zeros at `0x8c..0xa0` | High |
| `0x00a0..0x00f7` | **OBSERVED:** 29 triplets; first `37 02 24`, repeated `37 02 31` ten times | High |
| `0x00f7..0x0100` | **OBSERVED:** nine-byte tail `00 00 63 00 8f 00 00 00 00` | High |
| `0x0100..0x0157` | **OBSERVED:** another 29 triplets; first `30 2d 44`, repeated `30 3e 1c` ten times | High |
| `0x0157..0x0160` | **OBSERVED:** nine zeros | High |
| `0x0160..0xdac9` | **OBSERVED:** 55,657 bytes entirely fit the empirical grammar below | High for grammar fit |

**INFERRED, medium confidence:** the two 96-byte regions `0xa0..0x100` and
`0x100..0x160` look like separate structured prefix blocks, followed by a different
representation. Their purpose, true field boundaries and whether `0x160` is a
payload boundary are unknown. The grammar also accepts leading zero padding,
so grammar compatibility by itself cannot establish an exact payload start.

**OBSERVED:** first 64 bytes, exactly as the inspector reports:

```text
7632303134303830382d5358692d596948694563696761720000000000000000c1cee3c1cee3b6bffed7ddd3c1cee3c8cffdc6cddfc3caae007d032a00000000
```

Last 64 bytes start at decimal 55,945 (`0xda89`):

```text
c0329034ce36b531e236dc30c931e933ce36ab31c4361632bf311f31a636000000783000000012381d393230000000000000ae345e3465317a324c3642360000
```

**OBSERVED:** the global Shannon entropy is **5.970902 bits/byte**, with 8,881
zero bytes and 24,912 ASCII decimal digit bytes. This is a distribution calculation,
not evidence of encryption or executable code. There are 541 printable ASCII
runs of length at least six; the JSON shows 128 and records 413 omitted. The first
run is the header at offset 0, length 24. Other runs can arise from encoded data
and are not automatically firmware strings.

| Chunk start | Bytes | Shannon bits/byte |
| --- | --- | --- |
| `0x0000` | 4096 | 5.749778 |
| `0x1000` | 4096 | 5.917917 |
| `0x2000` | 4096 | 5.887929 |
| `0x3000` | 4096 | 6.140544 |
| `0x4000` | 4096 | 5.614674 |
| `0x5000` | 4096 | 6.008779 |
| `0x6000` | 4096 | 4.853702 |
| `0x7000` | 4096 | 5.830761 |
| `0x8000` | 4096 | 5.852407 |
| `0x9000` | 4096 | 5.959724 |
| `0xa000` | 4096 | 6.046091 |
| `0xb000` | 4096 | 5.924313 |
| `0xc000` | 4096 | 5.437680 |
| `0xd000` | 2761 | 4.961455 |

**OBSERVED:** overlapping repeated-pattern examples (full counts, first offset):

| Pattern hex | Occurrences | First offset |
| --- | --- | --- |
| `00000000` | 1885 | `0x18` (24) |
| `00002234` | 81 | 2428 |
| `16327234` | 65 | 999 |
| `0000223400001733` | 26 | 5387 |
| `00f23200cf3700c93100f23200cf3700` | 10 | 19543 |

Pattern counts overlap; shifted versions can describe the same repeating area.
Zero runs occur at `0x1a3..0x277` (212 bytes) and decimal 29130..29342 (212 bytes).
Repeated values identify structured/padded regions, without assigning code/data
or flash addresses.

## Empirical encoding model and rejected hypotheses

**OBSERVED, high confidence:** starting at `0x160`, strict left-to-right
tokenization consumes the entire suffix with zero errors:

```text
literal: 00 or ff                               (one source byte)
pair:    n, 0x30 + (n modulo 10), 1 <= n <= 254 (two source bytes)
marker:  f0 a0 or f0 c0                        (two source bytes)
```

The literal, pair and marker forms are unambiguous. For example, `73 35` at
`0x160` has `0x73 = 115`, whose decimal units digit is 5; `77 39` at `0x162`
has `0x77 = 119`, whose units digit is 9. `f0 30` is an ordinary pair for 240,
distinct from both markers.

```text
start=352 end=56009 consumed_bytes=55657 status=complete
digit_pairs=22946 literal_00=8815 literal_ff=636 markers=157
unique_pair_values=254 missing_pair_values_1_to_254=[]
f0a0 count=113 first_offset=393 (0x189)
f0c0 count=44  first_offset=1172 (0x494)
```

The arithmetic reconciles the suffix exactly:
`2*22946 + 8815 + 636 + 2*157 = 55657`. Every possible pair value 1..254
occurs. The next `f0 a0` positions are 639, 7643, 7814 and 7826; the next
`f0 c0` positions are 2923, 4808 and 5350. Offsets are source positions, not
decoded addresses.

**HYPOTHESIS, medium confidence:** decimal digits are redundant expansion of
underlying byte values, with `00`/`ff` left unexpanded and two reserved marker
forms. Syntactic tokenization is reversible if every token and marker is retained;
the interpretation of a token as an original firmware byte is not established.
Markers might carry data or framing rather than being discardable separators.

For comparison only, dropping the digits and both markers yields a diagnostic
projection of 32,397 bytes with SHA-256
`320fdd602eb7567f65fae0523617fdf523362a5545d35666eb55e335df5d50e2`.
The CLI computes this in memory and reports size/hash; it does not save a decoded
image. This is **not** a validated payload. Retaining marker bytes would change
the projected size to 32,711; neither choice is supported by an updater trace or
second sample. Consequently the A1 encoding gate for A2 remains unresolved.

| Tested hypothesis | Exact evidence / result | Conclusion |
| --- | --- | --- |
| Entire file or suffix is ASCII hexadecimal | Starts 0, 32, 128, 160, 352 fail respectively at offsets 0 (`76`), 32 (`c1`), 128 (`01`), 161 (`02`), 352 (`73`) | **OBSERVED:** reject these exact starts/alphabet |
| Entire file or suffix is standard Base64 text | Same starts fail at 9 (`2d`), 32 (`c1`), 128 (`01`), 161 (`02`), 358 (`95`) | **OBSERVED:** reject these exact starts/alphabet |
| Standard gzip/bzip2/xz/ZIP or zlib-wrapped stream begins at those offsets | No signature matches; none of the five two-byte zlib headers satisfies its method/window/mod-31 checks | **OBSERVED:** reject these exact wrappers/starts; raw/custom compression is untested |
| Suffix token grammar also applies to the prefix blocks | Strict probes at `0x80`, `0xa0`, `0x100` fail immediately on `01 00`, `37 02`, `30 2d` respectively | **OBSERVED:** reject a single such grammar for these starts |
| Two 87-byte triplet regions differ by a uniform XOR | At relative positions 0, 1, 2, 6 their XOR differences are `07`, `2f`, `60`, `09` | **OBSERVED:** reject one constant XOR for these two regions |
| Triplet regions have a single position-independent substitution | `37 02 43` maps to both `30 4f 34` and `30 41 3a` at corresponding positions | **OBSERVED:** reject this exact substitution relation; related content remains a hypothesis |

The grammar was discovered from this sample, so full coverage is evidence of its
internal consistency, not independent validation of an encoder. The header's
`20140808` substring is observed text; interpreting it as a build date is a
**HYPOTHESIS** without additional provenance.

## Checksum inventory

**OBSERVED:** all pair tokens satisfy the decimal-units relationship above. This
is local redundancy that could detect some corruptions. Calling it a deliberate
checksum is a **HYPOTHESIS**; it is not cryptographic integrity and the digits
can be recalculated for changed values.

**OBSERVED:** no tested standalone trailer checksum matched. `checksum_candidates`
tests starts 0, 32, 128, 160 and 352, exclusive ends `size-width`, and trailers of
width 1, 2 and 4. For each it compares both little- and big-endian trailer values
with sum modulo the trailer width and XOR-8. Width 2 also tests
`binascii.crc_hqx` with seeds `0000` and `ffff` (CCITT polynomial `0x1021`);
width 4 also tests `zlib.crc32` (IEEE CRC-32). All 15 regions report `matches=[]`.

For example, the last four bytes at `0xdac5` are `42 36 00 00`: stored LE
value 13,890, BE value 1,110,835,200. CRC-32 of raw bytes `[0,56005)` is
992,280,542; sum modulo 2^32 is 4,195,253; XOR-8 is 213. The last two bytes are
`00 00`; CCITT seed-0 CRC of `[0,56007)` is 45,385 and seed-ffff is 26,383.
The grammar interprets `42 36` as a pair and trailing zeros as literals, so a
separate trailer is not independently identified.

**HYPOTHESIS, low confidence:** checksum/length fields might reside in the prefix,
within markers, on projected data, or in updater-side framing. Some unassigned
prefix bytes can be read as integers: `03 2a 00 00` at `0x3a` is LE 10,755,
`6c 00 00 00` at `0x5a` is LE 108, and `ae 00 00 00` at `0x7b` is LE 174.
Those chosen alignments and meanings are unverified; they are not established
lengths or checksums. This limited search does not rule out other algorithms,
coverage regions, byte order conventions or transformed inputs.

## Compact reproduction of reported evidence

After creating the JSON above:

```sh
python - <<'PY'
import hashlib, json
from pathlib import Path
from tools.sxi_inspect import read_verified, SAMPLE_SHA256, SAMPLE_SIZE
r = json.loads(Path('work/A1-inspection.json').read_text())
print(r['size'], r['sha256'], r['whole_file']['entropy_bits_per_byte'])
print('strings:', r['strings']['total'], 'omitted:', r['strings']['omitted'])
t = r['token_probes'][-1]
print(t['start'], t['end'], t['status'], t['counts'], t['unique_pair_values'])
print(t['projection_size'], t['projection_sha256'])
print('checksum_matches:', sum(len(e['matches']) for e in r['checksum_candidates']))
b = read_verified(Path('work/firmware/ipv3_160W_V3.5.SXI'), SAMPLE_SHA256, SAMPLE_SIZE)
for start, end in ((0x20, 0x80), (0x80, 0xa0), (0xf7, 0x100), (0x157, 0x160)):
    print(hex(start), hex(end), b[start:end].hex())
for start in (0xa0, 0x100):
    triplets = [b[i:i+3] for i in range(start, start+87, 3)]
    print(hex(start), {v.hex(): triplets.count(v) for v in sorted(set(triplets))})
mapping = {}
for i in range(29):
    a, c = b[160+3*i:163+3*i], b[256+3*i:259+3*i]
    mapping.setdefault(a.hex(), set()).add(c.hex())
print('ambiguous_triplet_mappings:', {k: sorted(v) for k, v in mapping.items() if len(v)>1})
print('xor_differences:', [f'{b[160+i]^b[256+i]:02x}' for i in (0, 1, 2, 6)])
PY
```

The first six output lines are:

```text
56009 ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d 5.970902
strings: 541 omitted: 413
352 56009 complete {'digit_pairs': 22946, 'literal_00': 8815, 'literal_ff': 636, 'markers': 157} 254
32397 320fdd602eb7567f65fae0523617fdf523362a5545d35666eb55e335df5d50e2
checksum_matches: 0
0x20 0x80 c1cee3c1cee3b6bffed7ddd3c1cee3c8cffdc6cddfc3caae007d032a00000000c1cee3c1cee3c1cee3c1cee3c1cff9d2dffab3bff3b6bffeb2006c0000000000c1cee3c1cee3c1cee3c1cee3c1cee3c1cee3d7ddd3b3bbbd000000ae00000000
```

## Limitations, next hypothesis and changed files

There is one image and no updater implementation in the supplied input. Marker
semantics, prefix encoding, checksum placement, payload addresses and MCU ISA
remain unknown. A2 should not proceed on the marker-dropping projection.

Next bounded hypothesis: inspect the historical updater **offline** for the
header comparison and handling of digit pairs/`f0 a0`/`f0 c0`. A second independently
verified SXI would help distinguish fixed metadata from per-image fields and
validate the grammar outside this sample. Neither step requires device writes.

Changed files in this PR:

- `tools/sxi_inspect.py` — verification-gated, bounded, offline diagnostics.
- `tests/test_sxi_inspect.py` — 20 synthetic tests.
- `tools/README.md` — reproducible use and explicit limits/failure behavior.
- `analysis/reports/A1-container.md` — custody, findings, rejects and limitations.

The PR is for coordinator review and must remain unmerged. The executor's Git
HTTPS fetch failed because its configured proxy was unreachable; current-main
verification and publishing use the authorized GitHub connector instead.
