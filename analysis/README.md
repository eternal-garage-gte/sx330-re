# Analysis and work packages

| Phase | Objective | Exit artifact |
| --- | --- | --- |
| A0 | Establish chain of custody | verified artifact manifest and evidence ledger |
| A1 | Reverse engineer SXI container | read-only parser, tests, documented offsets |
| A2 | Locate executable regions and ISA | repeatable decoding/disassembly candidate |
| A3 | USB/updater discovery | USB descriptors, protocol observations, readback feasibility |
| A4 | Power-control model | sourced control-flow evidence for limits and feedback |
| A5 | Cross-version and bench validation | differential report and non-device test plan |

**First worker:** [analysis/tasks/A1-sxi-container.md](tasks/A1-sxi-container.md).

Parallel work is allowed for A3 as long as it is passive: enumeration or **offline** analysis of updater files. Never conflate a reported minimum output voltage with demonstrated closed-loop regulation at that voltage.

**A1b:** [lossless SXI representation and marker investigation](reports/A1b-encoding.md).
Complete container byte recovery is verified; marker output semantics and payload
addresses remain unresolved. Neither diagnostic projection is a validated image;
A2 architecture discovery remains gated pending coordinator review and independent
marker handling evidence.
