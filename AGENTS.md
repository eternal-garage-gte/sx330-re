# Agent instructions — SX330-RE

## Operating rules
1. Record starting commit SHA and scope before work. Prefer small, bounded tasks and **unmerged** PRs.
2. Label assertions as **OBSERVED**, **INFERRED**, or **HYPOTHESIS**; cite offsets, bytes, hashes, documents and reproduction commands. Unknown is an acceptable outcome.
3. Never alter source firmware in place. Retain original name, SHA-256 and retrieval details. Generated/decoded outputs go to ignored `work/`.
4. Do not assume an SXI file contains plaintext machine code, that 7 W is a mere UI clamp, or that USB update support implies readback.
5. Tools are **read-only/offline** unless a separate documented approval and review authorizes something else. Do not add flashing, USB writes, protection bypass, firmware patch generation, or live-heater tests.
6. Use standard-library Python where practicable; include unit tests and explicit failure behavior for malformed input.
7. Provide reproducible commands, test results, changed-file list, limitations and next hypothesis in each PR.
8. Coordinate changes to common parsers and evidence ledger; do not overwrite other workers' results.

## Stage gates
A1 encoding recovery precedes architecture claims (A2). A3 USB enumeration and updater disassembly may proceed independently. A4 requires identified target code/data. A5 requires hardware safety and recovery analysis before any write proposal.
