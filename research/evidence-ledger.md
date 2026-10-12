# Evidence ledger

| ID | Type | Claim | Evidence | Confidence / qualification |
| --- | --- | --- | --- | --- |
| E001 | OBSERVED (user) | Device shows a 150 W maximum | User observation in project discussion, 2026-10-08 | High for this physical unit; not independently probed |
| E002 | OBSERVED (user) | Coils are 1.3–1.8 Ω; target 1.8–3.0 V | User stated operating requirement | High |
| E003 | OBSERVED (artifact) | Archive is named `Only-for-IPV3-160W-Upgrade-Software_20141126_V3.5-1417490378.rar` | Google Drive discovery; local copy previously inspected | High; preserve original |
| E004 | OBSERVED (artifact) | Extracted SXI has 56,009 bytes and SHA-256 `ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d` | Previous local extraction analysis; reverify after transfer | High pending independent hash check |
| E005 | OBSERVED (artifact) | Header appears to contain `v20140808-SXi-YiHiEcigar` | Prior inspection; exact offset/encoding to reconfirm | Medium |
| E006 | INFERRED | 7 W UI floor may be firmware-enforced | Published user-interface limit and user experience | Unproven; could have regulator constraints |
| E007 | UNKNOWN | SXI decoding, CPU architecture, USB readback, safe lower regulation | No validated evidence yet | Open |

Add rows; do not silently reclassify hypotheses as facts.

A1b additions; prior entries above remain unchanged.

| ID | Type | Claim | Evidence | Confidence / qualification |
| --- | --- | --- | --- | --- |
| E008 | OBSERVED (artifact, A1b) | Source and staged SXI independently reverified: 56,009 bytes, SHA-256 as E004; direct copy comparison passes | [A1b custody and reproduction](../analysis/reports/A1b-encoding.md); staged file Git-ignored | High for this sample; no factory identity/readback claim |
| E009 | OBSERVED (artifact, A1b) | Full suffix `[0x160,0xdac9)` tokenized: 22,946 digit pairs, 8,815 zero literals, 636 ff literals, 113 A0 and 44 C0 markers; consumes 55,657 bytes | Independent `tools/sxi_tokens.py`, original-artifact integration test | High for empirical grammar; meaning unestablished |
| E010 | OBSERVED (artifact, A1b) | Prefix and all offset/class/raw token values yield byte-identical full-source round trip and original SHA-256 | `encode(decode(original)) == original`, original-artifact test | High for lossless container representation, not executable payload recovery |
| E011 | OBSERVED (artifact, A1b) | Marker gaps have GCD 1 in source, token and both projection coordinates; zero proximity differs by type; dropping markers merges seven zero-run pairs | [A1b marker experiments](../analysis/reports/A1b-encoding.md) and generated deterministic JSON | High; excludes exact fixed-phase delimiter model, not arbitrary address control |
| E012 | OBSERVED (artifact, A1b) | Diagnostic projections have 32,711 bytes retained and 32,397 omitted; prefix scan finds no plain 2/3/4-byte LE/BE field equal to tested sizes | [A1b prefix/size tests](../analysis/reports/A1b-encoding.md) | High for tested quantities/widths; no validated output policy |
| E013 | HYPOTHESIS (A1b) | Markers could expand data, delimit variable records or change output addressing | [A1b competing hypotheses](../analysis/reports/A1b-encoding.md); no updater/second image acquired | Low; semantics and A2 gate unresolved |
| E014 | HYPOTHESIS (A1b) | Retained projection's 57-byte deficit to 32 KiB may have structural significance | Size arithmetic only; no matching tested prefix field or validated marker width | Low; no flash-capacity or missing-region claim |
