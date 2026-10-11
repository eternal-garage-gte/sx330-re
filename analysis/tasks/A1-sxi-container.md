# A1 — SXI container reconnaissance (bounded worker handoff)

## Starting point
Read `AGENTS.md`, `README.md`, `firmware/README.md` and `research/evidence-ledger.md`. Record initial `main` SHA. Work on a branch; deliver an **unmerged PR**.

## Goal
Determine the on-disk structure of the recovered **56,009-byte** SXI sample without executing it or touching any hardware.

## Inputs
Locate the SXI matching SHA-256 `ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d`. Binary is not currently in repo; pause and report missing input rather than fabricate analysis.

## Concrete tasks
1. Implement a stdlib-only read-only CLI (`tools/sxi_inspect.py`) that reports size, SHA-256, first/last 64 bytes as hex, printable strings with offsets, byte histogram/entropy per bounded chunk, and repeated patterns.
2. Add unit tests with synthetic fixtures. Never decode or modify the original in place.
3. Investigate the apparent header `v20140808-SXi-YiHiEcigar`; test hypotheses for framing/encoding against actual byte offsets, documenting rejects.
4. Inventory any potential checksums and high-confidence regions; **do not** announce an MCU ISA without evidence.
5. Write `analysis/reports/A1-container.md` with exact commands, outputs, confidence ratings and candidate next steps.

## Acceptance criteria
- Deterministic output; malformed files handled; no unbounded allocations.
- Every claim is tied to a byte offset or reproducible calculation.
- Original file hash checked before parsing.
- Tests pass; no USB write, flashing, or patching functionality.
- PR remains open for coordinator review.
