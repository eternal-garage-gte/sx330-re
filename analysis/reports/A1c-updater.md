# A1c — YiHi updater archaeology and SXI parser recovery

## Result and scope

**OBSERVED:** the bounded search recovered references and exact links to
contemporary updater and firmware candidates, but **no updater binary or second
SXI sample**. Only the existing verified iPV3 SXI was obtained. The
[acquisition ledger](../../research/updater-artifacts.md) distinguishes source
claims, attempted retrievals and actual bytes, including unsuccessful leads.

**INFERRED:** there is insufficient evidence to reconstruct the updater's file
parser or select a firmware representation. **A2 is not ready**: marker output
semantics, payload boundaries and address mapping remain unestablished. No
semantic interpreter, modified image or flashable projection was created.

Scope: offline acquisition research and read-only checks of the original SXI.
No updater/installer launch, driver installation, USB or other device
communication, hardware modification, patch generation or A2 investigation
occurred. Third-party software instructions encountered in sources were treated
as historical documentation and were not executed.

## Initialization and exact baseline

Starting current `main`: **`c3cb29018a85be959560edf2be6c570b4197c1d9`**.
[PR #3](https://github.com/eternal-garage-gte/sx330-re/pull/3) was independently
checked through the GitHub connector: `merged=true`, merge SHA equal to this
starting SHA. GitHub `branches/main` returned the same commit and tree
`84100c8273228973058744597ed1859f235cff3c`. Dedicated local branch:
`analysis/a1c-updater`, created **from that merge commit**, not PR #3's branch.
Ending commit is recorded in the unmerged PR handoff, avoiding a self-referential
commit hash in this report.

The supplied checkout initially ended at A1's merged commit
`4bf93f23919905bac9dab90bd92e7ae9461fa1c5`. `git fetch origin main` failed before
origin contact because the configured proxy was unreachable. The authorized
GitHub connector supplied current-main blobs, the recursive tree and both missing
commit records. All blob/tree Git object IDs were verified locally; the original
A1b commit and signed merge commit were reconstructed and their exact IDs matched.
Local HEAD and `HEAD^{tree}` then matched the current-main SHA/tree above.
The baseline retrieval cache is ignored `work/A1c-baseline.json`. Cached remote
refs were not used as the authority and no proxy bypass was attempted.

Read `AGENTS.md`, `README.md`, `analysis/README.md`,
`analysis/reports/A1-container.md`, `analysis/reports/A1b-encoding.md`,
`research/evidence-ledger.md`, `firmware/README.md`, `.gitignore`,
`tools/README.md`, `tools/sxi_inspect.py` and `tools/sxi_tokens.py`.
Existing parser behavior remains empirical lossless tokenization, not updater
semantics. Claims below retain OBSERVED / INFERRED / HYPOTHESIS distinctions.

Investigation/retrieval date: **2026-10-12, America/Los_Angeles**.

## Acquisition findings and limits

See the ledger's U01–U05 and F02–F11 for original links, distribution sources,
reported versions/devices, attempted retrieval results and compatibility limits.
The updater stage used 25 web queries plus targeted manufacturer/archive/catalogue
checks; fallback used seven web queries and targeted second-sample links. Six
GitHub repository/code searches are recorded. Search stopped after fallback
retailer Drive objects returned 401, rather than repeatedly probing the same
unavailable endpoints.

**OBSERVED (documentation):** a firsthand February 2015 SX350 tutorial names a
20140808 MSI (U01); May/June 2015 instructions name a 20150522 RAR/MSI (U02).
The associated manufacturer pages were 404 or inaccessible through the tools.
A retailer supplied exact Drive links for an unversioned SX350 installer (U03)
and two firmware candidates (F06/F07), all returning 401. Those are useful
reacquisition leads, not acquired artifacts. Catalogue labels 2.3.0/1.9 (U05)
cannot be tied to a dated package. iPV3 Li leads (U04/F10) concern a different
reported target from the original iPV3.

The mission's original V3.5 RAR and historical 165W ZIP names were searched;
no independently usable archive location was recovered. Their original public
URLs remain unknown. No SHA-256 or measured size was invented for missing files.
Wayback CDX and timestamp requests were inaccessible; **no capture inventory was
obtained**. The requested timestamp is not an observed capture date. Current
manufacturer download pages rendered no historical candidates, but dynamic or
access limitations prevent an absence claim.

**HYPOTHESIS:** U01/U02 may implement a parser relevant to F01 because of their
era and SXi family context. Neither the repeated `20140808` substring nor the
`.SXI` extension proves that. There is no supported-model list or executable
comparison here. A reported third-party logo editor and `.data` files (F11) also
do not establish an independently stored firmware dependency in the YiHi updater.

## Updater architecture — unavailable

No candidate passed the actual-binary acquisition/hash gate. Consequently there
are **no observed** PE headers, architecture, CLR metadata, imports, resources,
dependency graph, configuration, header-string cross-references, function/RVA
locations or disassembly to report. `.msi`/`.rar` descriptions remain documented
distribution claims. In particular, a runtime DLL near an updater filename in
a public system log is not proof that the updater imports that DLL.

No static analyzer was run on a missing or unrelated executable. Installing
Ghidra/PE tooling would not resolve the absent input. When an authentic package
is acquired, extracted application components must be hashed independently and
its target/header checks traced before interpreting this sample.

## Parser questions and semantic evidence

Each unknown below means **not recovered**, not a negative finding about the
updater. There are no updater code locations to cite. The existing tokenizer's
source locations can reproduce sample syntax only; they are not YiHi code.

| Question | Concrete available evidence | Updater behavior established? |
| --- | --- | --- |
| Header recognition | F01 bytes `[0,24)` equal `v20140808-SXi-YiHiEcigar`; inspector `sxi_header.matches=true` | **Unknown**: comparison length, accepted versions, failure branch and model checks |
| Prefix fields | A1/A1b preserve `[0,0x160)` and report its exact bytes; A1b's bounded plain-integer scan has no tested size matches | **Unknown**: decoded addresses, lengths, checksum/version metadata and compatibility rules |
| Ordinary tokens | Entire suffix from `0x160` obeys literal `00`/`ff` or value/ASCII-decimal-units pairing, with two special forms | **Unknown**: whether YiHi removes digits, validates them, transforms values or processes another representation |
| `f0 a0` | 113 exact source occurrences; first at `0x189`; lossless token width is two **source** bytes | **Unknown**: branch, subsequent bytes/tokens consumed, output width, destination changes, arithmetic/state/context |
| `f0 c0` | 44 exact source occurrences; first at `0x494`; same two-source-byte syntactic width | **Unknown**: all semantic questions above |
| Marker relationship | A1b rejects an obligatory alternating opening/closing model and exact fixed-phase delimiters in four tested coordinates | **Unknown**: independence, complementary optional operations, operands or prefix-dependent state |
| Prepared transport/programming representation | Diagnostic projections can be computed reproducibly | **Unknown**: actual prepared buffer, record structure, address mapping and subsequent USB interpretation |

The empirical `decode` consumes two bytes for a marker and retains them in its
representation. That does **not** demonstrate that YiHi consumes only two bytes,
emits two bytes, or consumes no following operands. Similarly, lossless
round-trip serialization is evidence about the source container, not evidence
about firmware programming.

The central hypotheses remain open:

| HYPOTHESIS | Evidence needed to discriminate it | A1c assessment |
| --- | --- | --- |
| Complete firmware image | Validated decoding, emitted extent and a demonstrated relationship between bytes and destination regions | Neither diagnostic size establishes completeness or flash capacity |
| Addressed regions / partial replacements | Parser or programming-layer address/length records and destination transitions; coverage of writes | No address/length interpretation or page boundary established |
| Differential patch | Concrete use of existing firmware bytes, a base-image checksum/version, or patch operations that depend on a base | No updater available to establish or exclude such dependencies |
| Other encoding/transport representation | Concrete state transitions, value mapping, framing/decompression and the buffer handed to transport | Still plausible; empirical digit redundancy alone does not select it |

None can be promoted to a confirmed interpretation. A parser producing bytes
could still hand an addressed or patch representation to another layer. Even
proof that the file parser never reads existing firmware would not alone exclude
a device-side differential operation. Conversely, accepting an upgrade filename,
reporting a current version, or displaying a repair option would not demonstrate
firmware readback. **No readback path is established.**

## Reconcile with the verified sample

**OBSERVED:** F01 was recovered from A1's attachment identifier and staged via the
existing verification procedure. Original source and staged copy were opened
with the bounded regular-file reader, checked for exact size/hash before parsing,
compared directly, and reverified after inspection. Both are **56,009 bytes**,
SHA-256 **`ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d`**.
Full source path and custody details are in the ledger. `work/` remains ignored
and untracked; the source file was not modified.

The existing tools reproduce A1/A1b exactly:

| Observation | A1c reproduced value |
| --- | --- |
| Probe body range | `[0x160,0xdac9)`, 55,657 source bytes |
| Digit-pair / zero / FF tokens | 22,946 / 8,815 / 636 |
| A0 / C0 marker tokens | 113 / 44 |
| Representation round trip | Byte-identical, original SHA-256 |
| Retained / omitted diagnostic projection sizes | 32,711 / 32,397 |
| Token report | 3,122,309 bytes; SHA-256 `6f236c25740d678097977694b6997cf1b2110c7fb3166b78bdbe48e1296fe5c0` |
| Inspector report SHA-256 | `ec317e233a9f64280a45a14c432de86c17ff15d68410192b24d6bcc66687f1bb` |

The token report preserves all source offsets and all 157 marker positions,
including raw bytes and context. Its hash matches A1b's complete report; no
marker-policy change is introduced. There is no recovered updater behavior to
compare against those positions. `0x160` remains a reproducible probe boundary,
not a demonstrated executable/payload boundary. Neither projection is a
validated firmware image. No projected binary was saved.

Fallback comparison is **not performed**, because no second candidate passed
retrieval, size/hash and generation verification. Its header, prefix, grammar,
marker distribution and candidate-size relationships remain unmeasured.
Documentation about another filename is not a comparison dataset.

## Reproduction and observed validation

After staging F01 by the existing [A1 procedure](A1-container.md), run from the
repository root with Python **3.12.14**:

```sh
python -m unittest discover -s tests -v
python tools/sxi_tokens.py work/firmware/ipv3_160W_V3.5.SXI > work/A1c-token-regression.json
python tools/sxi_inspect.py work/firmware/ipv3_160W_V3.5.SXI > work/A1c-inspection-regression.json
sha256sum work/A1c-token-regression.json work/A1c-inspection-regression.json
git diff --check
git check-ignore -v work/firmware/ipv3_160W_V3.5.SXI work/updater/A1c-retrieval-log.json
git ls-files -- work/
```

**OBSERVED:** all **30 existing tests passed**, including
`test_original_artifact_when_available` without skipping. Both CLIs exited 0;
their hashes match the table. No new interpreter/tests were added because no
demonstrated semantic behavior was recovered; this is a documentation-only
change. Diff/exclusion checks pass and no `work/` files are tracked.

## Coordinator handoff and A2 gate

Changed files:

- `analysis/reports/A1c-updater.md`: result, unknown parser semantics, competing
  interpretations, sample regression and explicit A2 gate.
- `research/updater-artifacts.md`: reproducible source/attempt ledger, candidate
  distinction, exact unavailable links and second-sample fallback.
- `research/evidence-ledger.md`: appended supported A1c observations and qualified
  inference; earlier evidence preserved.
- `analysis/README.md`: link to A1c's acquisition result and continuing gate.

**Confirmed:** merged starting revision, unchanged verified original SXI,
unchanged empirical token stream and output hashes, named contemporary leads
with explicit retrieval failures. **Unresolved:** updater architecture and parser
code; marker output/operand/state semantics; decoded prefix; true payload extent;
address mapping; checksums; full-image versus partial/differential/transport
meaning; readback feasibility. **A2 architecture identification cannot begin as
validated payload analysis.** Coordinator review is still required.

**Single most discriminating next experiment:** acquire a legitimately shared
original 2014-era YiHi/Pioneer4You updater package supporting original iPV3 /
SX330-V3S, hash it and its extracted application components, then statically trace
file selection/header validation through the two marker branches to the prepared
buffer. U01 is a dated candidate, not confirmed support; demonstrate its model
and header compatibility before using it. Stop before USB interaction and never
launch the application. The exact missing evidence is the authentic file parser
and any called decoder: instruction/RVA or IL locations showing digit handling,
A0/C0 input advancement, output writes, destination changes, state and dependence
on prefix/base data, tied to hashed bytes. These would distinguish expansion
from no-output framing/address control and determine whether any projection is
justified. Legitimate access to the ledger's installer link or a coordinator
attachment supplies the currently absent input; another round of equivalent
dead-URL searches does not.
