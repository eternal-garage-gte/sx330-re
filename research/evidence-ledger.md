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
