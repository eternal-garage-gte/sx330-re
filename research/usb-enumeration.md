# A3 — Passive USB reconnaissance

**Goal:** discover whether the original iPV3 enumerates over USB and what its updater can do. A firmware update interface is not evidence of a readback endpoint.

1. Remove the atomizer; do not initiate a flash/update/repair operation.
2. Inspect Windows Device Manager and USB Device Tree Viewer before/after connection using a known data-capable micro-USB cable.
3. Record whether the host sees an event, VID/PID, USB class, interface/endpoint descriptors, driver name, and any error code; redact serial numbers.
4. If it does not enumerate, document cable/port/host observations without assuming the hardware is broken.
5. Analyze any acquired legacy YiHi SXi desktop updater **offline** in an isolated environment before installing old drivers. Verify source and hash.
6. Treat USBPcap/Wireshark as observational tools. Do not send undocumented control transfers or commands to the device.

**Unknown:** if MCU debug/readout protection, external flash, or a reversible readback path exists. Do not claim a dump is possible until corroborated.
