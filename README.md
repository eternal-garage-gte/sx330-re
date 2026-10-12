# SX330-RE — YiHi SX330 firmware archaeology

Reverse engineering of the original Pioneer4You iPV3 (150 W) / YiHi SX330-V3S ecosystem, beginning with a recovered 2014 iPV3 160 W upgrade package.

## Research question
Can this hardware regulate an output of **1.8–3.0 V** across **1.3–1.8 Ω** resistive loads (about **1.8–6.9 W**), and how are the UI limits, regulation limits and protection mechanisms implemented?

**Status:** No MCU architecture, payload decoding or firmware readback method established yet. No modified images are approved for flashing.

## Project phases
- **A0 — Provenance:** preserve original bytes, hashes, filename, provenance and uncertainties.
- **A1 — Container:** establish SXI layout, header, encoding, payload, checksums and read-only parser.
- **A2 — CPU:** identify code regions and MCU architecture; develop reproducible disassembly.
- **A3 — USB:** characterize enumerated interfaces and updater protocol; investigate *non-destructive* readback.
- **A4 — Control:** locate user wattage clamps, voltage/power calculations and protections.
- **A5 — Validation:** compare builds if another image is obtained; bench-test hypotheses off-device.

## Repository conventions
See [AGENTS.md](AGENTS.md) and [analysis/README.md](analysis/README.md). Evidence, inference and speculation must not be conflated. Keep worker PRs small and unmerged for coordinator review.

## Recovered artifact
Original file: `Only-for-IPV3-160W-Upgrade-Software_20141126_V3.5-1417490378.rar`
Extracted filename reported: `Only for IPV3 160W Upgrade Software_20141126_V3.5.SXI`.
The recovered SXI is 56,009 bytes; SHA-256 **ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d**. Validate this against your own copy before analysis. The original RAR and SXI binaries are **not yet committed**. See [firmware/README.md](firmware/README.md).

## Safety boundary
Analysis and enumerating a disconnected heating controller are in scope. No device write, flash, unlocking, bypass of thermal/current/battery protections, or use on a live atomizer is part of the scaffold.

## Encoding investigation

[A1b](analysis/reports/A1b-encoding.md) verifies lossless SXI representation recovery
and reproduces A1's full token counts. Marker semantics and payload address mapping
remain unknown; the 32,711-byte and 32,397-byte projections are diagnostic only.
A2 has not begun. See [offline tool usage](tools/README.md).
