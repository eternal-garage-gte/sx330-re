# A1b — Lossless SXI representation and marker investigation

## Scope, custody and stage gate

Starting current `main`: **`4bf93f23919905bac9dab90bd92e7ae9461fa1c5`**.
GitHub `branches/main` confirmed this SHA and tree
`77faa64e6f212a2c6334d0828dd14eda6621fde4`; PR #2 reports `merged=true`,
merge commit equal to this starting SHA. Local HEAD matched. The cached
`origin/main` was stale; it was not used as the authority. Dedicated branch:
`analysis/a1b-sxi-encoding`. Ending publication SHA is recorded in the PR handoff
(the report cannot contain its own enclosing commit's SHA).

Read `AGENTS.md`, `README.md`, `analysis/README.md`,
`analysis/reports/A1-container.md`, `tools/sxi_inspect.py`, `tools/README.md`,
`research/evidence-ledger.md`, `.gitignore`, and existing inspector tests.
Scope: offline representation recovery and bounded structural experiments.
No USB/device communication, hardware changes, flashing, driver installation,
updater execution, modified firmware, ISA identification or disassembly occurred.
This PR remains unmerged for coordinator review; A2 has not begun.

**OBSERVED, high confidence:** mandatory verification passed before analysis:

| Custody item | Result |
| --- | --- |
| Filename | `ipv3_160W_V3.5.SXI` |
| Retrieval | Attachment ID `file_0000000029a481fd85e5b7dbaa475783`, recovered from A1's custody record using `download_file`; accessible in this session |
| Source path | `/workspace/attachments/f506e3b7-d5d4-4300-b97a-98d6beb5baec/ipv3_160W_V3.5.SXI` |
| Retrieval date | 2026-10-11, America/Los_Angeles (2026-10-12 UTC) |
| Staged path | `work/firmware/ipv3_160W_V3.5.SXI` |
| Size, source and staged | **56,009 bytes** |
| SHA-256, source and staged | **`ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d`** |
| Verification | `read_verified`, regular binary file, size/hash before parsing; `shutil.copyfile` to a previously nonexistent destination; independent reread/hash and direct byte comparison |
| Git exclusion | `git check-ignore -v` → `.gitignore:2:work/`; `git ls-files -- work/firmware/` → empty |

The historical RAR was not supplied. Its provenance remains as qualified in A1;
this sample does not establish the physical unit's factory firmware identity.
The source and staged file were reverified at the end of work.

**Result:** lossless recovery of the *container representation* is established.
Marker semantics, payload address mapping, and even the correct marker output
width remain unresolved. Evidence is **insufficient to begin A2 as validated
firmware disassembly**. Byte-pattern architecture guesses are not made.

## Token grammar and complete round trip

`tools/sxi_tokens.py` implements an independent strict parser; it does not call
A1's `token_probe`. The only reuse is A1's bounded verification reader/constants.
`decode(bytes, start=0x160)` returns an immutable `Document` containing an opaque
prefix and immutable `Token(offset, kind, raw)` entries. `encode(document)` checks
contiguity, classes, exact source coverage and byte limits before reconstructing
the source. Neither API infers executable boundaries or modifies source files.

**OBSERVED:** all body bytes fit these mutually exclusive forms:

| Token class | Raw source form | Count | Source bytes |
| --- | --- | ---: | ---: |
| `digit_pair` | `XX (0x30 + XX % 10)`, `1 <= XX <= 254` | 22,946 | 45,892 |
| `literal_00` | `00` | 8,815 | 8,815 |
| `literal_ff` | `ff` | 636 | 636 |
| `marker_a0` | `f0 a0` | 113 | 226 |
| `marker_c0` | `f0 c0` | 44 | 88 |
| Total | `[0x160, 0xdac9)` | 32,554 tokens | **55,657** |

The remaining 352 prefix bytes plus 55,657 body bytes give 56,009.
All 254 ordinary pair values occur. `f0 30` is an ordinary digit pair, distinct
from `f0 a0` and `f0 c0`. No resynchronization, guessed replacement or omission is
permitted. A malformed or truncated token fails at its absolute source offset.

**OBSERVED:** `encode(decode(original)) == original` by direct comparison, and
SHA-256 equals the verified original hash above. Every individual token's raw
bytes also equal the original slice at its recorded offset. JSON retains the
entire prefix, all token offsets/classes/raw values, and every marker; reconstructing
`prefix_hex` plus the ordered token `raw_hex` values is likewise byte-identical.

Input is capped at 262,144 bytes; decode/encode storage is O(n), with at most one
token per input byte. The CLI uses the size/hash gate before decoding, rejects
nonregular/missing/oversized files through the shared reader, writes only JSON to
stdout, and exits 2 with stderr and no JSON on verification/grammar failures.
JSON has no date or path fields. Context is four tokens on each side, prefix
integer scanning is capped at 352 bytes, and residue moduli are fixed. All arrays
and counters are bounded by the input cap. This is not a general SXI validator.

## Marker distributions, context and zero regions

The generated report preserves four separate coordinates:

- `source_offset`: original SXI byte offset.
- `token_index`: number of preceding body tokens, counting each marker once.
- `omit_offset`: diagnostic output position with markers omitted.
- `retain_offset`: diagnostic output position with both raw marker bytes retained.

None is an established memory address. For the j-th marker of either type,
`retain_offset = omit_offset + 2*j` and `token_index = omit_offset + j`.
This difference is cumulative, not one global alignment adjustment.

**OBSERVED:** the two marker types have the following independent distributions.
Gaps below are between successive markers *of the same type*, not successive
markers of either type.

| Measurement | `f0 a0` | `f0 c0` |
| --- | ---: | ---: |
| Count | 113 | 44 |
| First / last source offset | `0x189` / `0xd67c` | `0x494` / `0xc392` |
| First / last omitted-marker coordinate | 25 / 31,674 | 564 / 28,539 |
| Source gap min / max / GCD | 4 / 7,004 / 1 | 12 / 5,044 / 1 |
| Token-index gap min / max / GCD | 2 / 3,849 / 1 | 6 / 2,874 / 1 |
| Omitted-coordinate gap min / max / GCD | 1 / 3,844 / 1 | 5 / 2,858 / 1 |
| Retained-coordinate gap min / max / GCD | 3 / 3,854 / 1 | 7 / 2,890 / 1 |
| Adjacent to at least one zero literal | 53 / 113 | 7 / 44 |
| Neither immediate neighbor is zero | 60 / 113 | 37 / 44 |
| Immediately adjacent to another marker | 0 | 0 |

For comparison, 14,023 / 32,397 ordinary tokens have at least one zero-literal
neighbor. This baseline includes tokens inside zero runs and is descriptive;
these are not independent samples or a significance test. A0 zero proximity is
not specific enough to assign a padding command, and C0 rarely adjoins zeros.

In *all four coordinates*, each marker type has more than one residue modulo
16, 32, 64, 128, 256, 512 and 1,024. For example, source offsets cover all 16
modulo-16 residues for A0 and 15 for C0; retained offsets cover 16 and 14.
Gap GCD 1 rules out a common phase for any exact fixed region width >1 in these
coordinates, including an arbitrary constant address base. Variable records,
multiple memory regions and unknown address transforms remain untested.
Full positions, gap histograms and residue histograms are in the generated JSON.

**OBSERVED local examples** (ordinary pairs shown as their first byte for compact
context; bracketed marker bytes remain literal):

| Marker source offset | Preceding four tokens | Marker | Following four tokens |
| --- | --- | --- | --- |
| `0x189` | `76 51 00 5a` | `[f0 a0]` | `1a 2f 03 00` |
| `0x494` | `68 f9 3c c7` | `[f0 c0]` | `c9 3e 23 b0` |
| `0xc9a8` | part of 28-zero run | `[f0 a0]` | four zero literals |
| `0xc392` | `c3 50 7f b7` | `[f0 c0]` | `04 38 23 7c` |

A0's most frequent preceding token is `00` (23); following is `00` (36).
C0's most frequent preceding token is ordinary `c0 32` (10), followed in frequency
by `38 36` (5); its most frequent following token is `00` (5). These local biases
are observations; they do not identify instructions or command operands.

Ordinary pairs for values `f0`, `a0` and `c0` occur 71, 33 and 194 times,
respectively. Thus a claim that one of these byte values *always* requires the
special form contradicts the sample. Context-dependent escaping remains possible.
No two markers are adjacent; at `0x9d9d`, two A0 markers surround one ordinary
`4e 38` token. An obligatory alternating A0/C0 opening/closing model is rejected.

There are seven markers between immediate zero runs:

| Source offset / marker | Zeros before | Zeros after |
| --- | ---: | ---: |
| `0x27f` / A0 | 6 | 1 |
| `0x72b0` / A0 | 1 | 1 |
| `0x8396` / C0 | 2 | 2 |
| `0x9881` / A0 | 4 | 1 |
| `0xbaee` / A0 | 2 | 1 |
| `0xc9a8` / A0 | 28 | 4 |
| `0xd65c` / A0 | 2 | 1 |

Dropping markers merges these runs: zero-run count changes from 5,047 retained
to 5,040 omitted, with the 28+4 example becoming 32 zeros. The longest zero runs
remain 212 bytes under either projection, at omitted positions `0x26` and
`0x413e`, retained positions `0x28` and `0x41ae`. Their surroundings differ.
Repeated long zero-run lengths (41, 50, 53, 48, etc.) also occur in both halves,
but do not share a single distance: omitted examples `0x3bcc`→`0x794c` and
`0x3cfc`→`0x7a7a` differ by `0x3d80` and `0x3d7e`. Repeated padding lengths alone
do not establish duplicated records or fixed banks.

## Competing semantic hypotheses

Confidence refers to the proposed meaning, separate from the high-confidence
measurements above. Rejection is limited to the exact prediction tested.

| Hypothesis | Predicted observations | Supporting observations | Contradictions / limits | Assessment |
| --- | --- | --- | --- | --- |
| Fixed-size record or memory-page delimiters, with one common phase | Same-type positions align in source or one simple projection; spacing is a multiple of record width | Tokens are distinguishable and scattered through the body | Gap GCD is 1 in all four coordinates; broad residues; A0 source gaps 4..7,004, C0 12..5,044 | Reject exact fixed-phase model, high confidence; variable records still possible |
| A0 opens and C0 closes each framed record | Marker types alternate and counts balance, possibly allowing one unmatched end | Two marker types could encode different roles | 113 versus 44; two A0 markers separated by one ordinary token at `0x9d9d`; multiple A0 events before first C0 | Reject obligatory alternating model, high confidence; optional controls remain possible |
| Zero/padding run controls | Markers occur consistently at zero-run starts/ends, perhaps with a stable length | 53 A0 and 7 C0 occurrences touch zeros; A0 can split zero runs | Most C0 and 60 A0 touch no zeros; many ordinary tokens touch zeros; lengths vary; 212-zero runs need no internal marker | Low confidence; reject universal zero-boundary interpretation |
| Unconditional escaping of literal F0, A0 or C0 | Ordinary corresponding values are absent or always special | Marker prefix F0 resembles an escape introducer | All three ordinary values occur; all 1..254 ordinary values are represented | Reject unconditional per-value escape rule; selective multi-byte escape has low, unresolved confidence |
| Address-change commands with immediate ordinary 2/4-byte operands in a monotonically increasing traversal | Following values are monotone, aligned and fit a consistent address domain | Distinct controls could change output location without emitting data | Tested following values decrease many times and are often unaligned; one A0 context includes another marker among the next two/four tokens | Low confidence; reject only immediate monotone/aligned operand model; segmented/nonmonotone addresses untested |
| Markers are data expansions rather than removable controls | Retaining or mapping them changes layout; occurrences can be embedded among arbitrary values and zeros | Embedded contexts and variable positions fit; retaining keeps distinctions lost by deletion | No mapping/width independently known; ordinary F0/A0/C0 also exist | Plausible but low confidence; neither two-byte nor one-byte output validated |
| Both markers are discardable no-output framing | Ordinary-token projection has meaningful record layout and consistent lengths/metadata | Projection is deterministic, yields 32,397 bytes | Deletion merges zero runs and changes every subsequent position; no updater or length-field validation | Low confidence; syntactic ability to omit is not semantic validation |

For the immediate-operand test, use the first bytes of the next 2 or 4 ordinary
*tokens*, rejecting a context if a marker appears within that fixed window.
A0 has 112 usable contexts; C0 has 44. Counts of decreasing successive values:

| Type | 16-bit LE / BE | 32-bit LE / BE |
| --- | --- | --- |
| A0 | 53 / 52 | 56 / 52 |
| C0 | 19 / 23 | 21 / 23 |

Only 40/112 A0 and 9/44 C0 immediate values have a low-order LE nibble of zero;
these do not form a universally 16-byte-aligned traversal. These are diagnostic
integers, not discovered addresses. The test does not rule out command operands
with another representation, updater-side state, or intentional nonmonotone writes.

## Payload projections and prefix consistency

**OBSERVED:**

| Representation policy | Body bytes | SHA-256 |
| --- | ---: | --- |
| Collapse digit pairs, retain both raw bytes of each marker | **32,711** | `e2c2adb0c9d99140278ac8637f0109035d00454da39a802dcc822f1a472d026d` |
| Collapse digit pairs, omit both marker types | **32,397** | `320fdd602eb7567f65fae0523617fdf523362a5545d35666eb55e335df5d50e2` |
| Count one byte per marker (no mapping specified) | 32,554 | No candidate image generated |

The first two differ by exactly `2 * 157 = 314` bytes. Retaining yields a
57-byte deficit relative to 32,768; one byte per marker would give a 214-byte
deficit, and omitting gives 371. This arithmetic does not select a policy.
Adding the entire 352-byte prefix would instead give 33,063 retained or 32,749
omitted (19 short of 32 KiB). Nearness to a power of two is sensitive to an
unvalidated boundary/output choice.

**HYPOTHESIS, low confidence:** the 57-byte deficit could represent missing
metadata, omitted address ranges, a variable-length image, or coincidence. A
specific 32 KiB flash capacity, a 57-byte missing region, and an address origin
cannot be inferred. No padding or candidate executable image was generated.

The exact prefix `[0,0x160)` is retained in JSON; A1's layout remains observed:
24-byte ASCII header, eight zeros, three 32-byte regions at `0x20..0x80`, a
32-byte region at `0x80..0xa0`, then two 96-byte regions at `0xa0..0x100` and
`0x100..0x160`, each with 29 triplets and a nine-byte tail. Interpreting any as
records, encoded labels, address metadata or lengths remains hypothetical.
A1 already rejected uniform XOR and position-independent triplet substitution
between the two 87-byte triplet arrays; this work does not reinterpret those as
firmware payload. No semantic prefix decoder has been established.

**OBSERVED, bounded negative test:** scan every possible byte alignment in the
352-byte prefix for plain unsigned 2-, 3- and 4-byte LE/BE integers equal to
56,009; 55,657; 32,711; 32,397; 32,554; 32,768; or 57. **No matches.** This
contradicts a direct integer field of those widths/orders for those exact sizes.
It does not exclude encoded lengths, units other than bytes, different field
widths, sums, checksums, addresses or records whose lengths differ from these.
No address field is established; alignment appearance alone is insufficient.

**OBSERVED:** starting at `0x157` also tokenizes completely, adding nine zero
literals and producing 32,720 retained bytes. Starting at `0x158` gives 32,719.
Moving the presumed start 57 source bytes earlier to `0x127` fails immediately
on `30 3e`. Thus appending preceding prefix bytes does not simply explain the
57-byte deficit under the same grammar. The accepted `0x157` start shows why
`0x160` is a reproducible A1 probe boundary, not a proven firmware-code boundary.

## Independent validation search and provenance limits

A bounded web search on 2026-10-11 America/Los_Angeles looked for historical
SX330/iPV3 and SX350 SXI downloads and the original YiHi updater. No second
binary or updater was acquired. Download URLs/hashes cannot be invented:
**additional downloaded artifacts: none; additional artifact hashes: none**.

| Primary-source URL checked | Observed retrieval result | Relevance / limit |
| --- | --- | --- |
| `https://www.yihisxmini.com/download-center.html` | Readable current manufacturer page; browser rendition supplied no archive download links | Search index listed current resources, but indexed descriptions are not binary provenance |
| `https://www.yihisxmini.com/firmware-download.html` | Readable manufacturer page; rendered table said zero available files, possibly dynamic-loading failure | No usable historical link; this does not establish absence from the actual catalogue |
| `http://www.yihiecigar.com/download.html` | Browser followed HTTPS; 502 Bad Gateway | Historical manufacturer download endpoint unavailable through this tool |
| `https://yihiecigar.com/download.html` and `https://yihiecigar.com/download_en.html` | Browser tool reported inaccessible | No file retrieval |

Queries also returned forum reports naming 2015 updates, but those were not used
as validation of a grammar, binary identity or marker meaning. No legacy software
or driver was executed/installed. The executor's configured HTTPS proxy could
not be reached even for `git fetch origin main`; no proxy bypass was attempted.
Browser search and the authorized GitHub connector worked. This leaves all
cross-sample and updater-behavior predictions untested, rather than failed.

## Reproduction and observed validation

From the repository root with Python **3.12.14**, after verified staging:

```sh
python -m unittest discover -s tests -v
python tools/sxi_tokens.py work/firmware/ipv3_160W_V3.5.SXI > work/A1b-tokens.json
python tools/sxi_tokens.py work/firmware/ipv3_160W_V3.5.SXI > work/A1b-tokens-repeat.json
cmp work/A1b-tokens.json work/A1b-tokens-repeat.json
sha256sum work/A1b-tokens.json
python tools/sxi_inspect.py work/firmware/ipv3_160W_V3.5.SXI > work/A1-inspection.json
git diff --check
git check-ignore -v work/firmware/ipv3_160W_V3.5.SXI
git ls-files -- work/
```

**OBSERVED:** all **30 tests pass**: the 20 existing A1 tests and 10 new tests,
including the complete original-artifact verification/round trip (not skipped).
New fixtures cover every ordinary pair value, literals, both markers, adjacent
markers, raw/offset preservation, malformed/truncated input, forged serializer
metadata, byte cap, deterministic/read-only CLI output, and verification before
parse. In a clean checkout without the ignored artifact, only the original-sample
test skips explicitly; a present but mismatching artifact fails.

Both tokenizer runs exit 0; `cmp` exits 0. JSON is **3,122,309 bytes**, SHA-256
**`6f236c25740d678097977694b6997cf1b2110c7fb3166b78bdbe48e1296fe5c0`**.
A1 inspector still exits 0 with its previous output hash. `git diff --check` is
clean. Firmware and generated JSON remain ignored and untracked.
A full-cap 262,144-byte synthetic all-zero input (`--start 0`, explicitly supplied
size/hash) also completed successfully; measured peak child RSS was 149,356 KiB.
The CLI streams JSON rather than building an additional complete output string.
This measurement is environment-specific; the hard input cap establishes the
structural memory bound.

Additional measurements above can be reproduced with this bounded command:

```sh
python - <<'PY'
from collections import Counter
from pathlib import Path
from tools.sxi_tokens import decode, projection, read_verified, SAMPLE_SHA256, SAMPLE_SIZE
b = read_verified(Path('work/firmware/ipv3_160W_V3.5.SXI'), SAMPLE_SHA256, SAMPLE_SIZE)
d = decode(b)
ts = d.tokens
print('ordinary f0/a0/c0', {v: sum(t.kind == 'digit_pair' and t.raw[0] == v for t in ts)
                              for v in (240, 160, 192)})
for kind in ('marker_a0', 'marker_c0'):
    group = [(i, t) for i, t in enumerate(ts) if t.kind == kind]
    print(kind, 'zero adjacent', sum(bool((i and ts[i-1].kind == 'literal_00') or
          (i+1 < len(ts) and ts[i+1].kind == 'literal_00')) for i, t in group))
    for width in (2, 4):
        for order in ('little', 'big'):
            values = []
            for i, t in group:
                window = ts[i+1:i+1+width]
                if len(window) == width and all(not x.kind.startswith('marker') for x in window):
                    values.append(int.from_bytes(bytes(x.raw[0] for x in window), order))
            print(kind, width, order, len(values), 'decreases',
                  sum(a > c for a, c in zip(values, values[1:])))
for keep in (False, True):
    p = projection(d, keep)
    runs, start = [], None
    for i in range(len(p)+1):
        if i < len(p) and p[i] == 0:
            if start is None:
                start = i
        elif start is not None:
            runs.append((start, i-start))
            start = None
    print('retain', keep, 'runs', len(runs), 'long runs', [(hex(s), n) for s, n in runs if n >= 16])
PY
```

## Handoff

Changed files:

- `tools/sxi_tokens.py`: deterministic lossless tokenizer/serializer and marker diagnostics.
- `tests/test_sxi_tokens.py`: synthetic/malformed fixtures, bounded behavior, original-sample integration.
- `analysis/reports/A1b-encoding.md`: findings, competing predictions, rejects and limits.
- `tools/README.md`, `analysis/README.md`, `README.md`: usage and current encoding gate.
- `research/evidence-ledger.md`: append supported A1b observations and qualified hypotheses; preserve existing entries.

**Confirmed:** complete empirical grammar, exact counts, original byte recovery,
full marker preservation, diagnostic sizes/hashes, heterogeneous positions and
zero contexts, no tested plain prefix size field. **Unresolved:** what markers
emit or control, address transitions, prefix interpretation, true payload size,
checksums and whether any projection represents original executable bytes.

**One bounded follow-up experiment:** obtain the historical YiHi updater archive
from a verifiable source, hash it, extract it without installation, and trace its
file-loading routine statically from the `v20140808-SXi-YiHiEcigar` header to
handling of `f0 a0` and `f0 c0`. Record whether each branch emits 0, 1, 2 or a
variable number of bytes, changes a destination address, or consumes operands.
Limit scope to these file-parser branches; stop before USB I/O routines and do
not execute the program. This distinguishes data expansion from no-output
framing/address control and directly resolves which projection policy, if any,
is justified. Until coordinator review and that evidence, A2 stays gated.
