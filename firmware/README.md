# Firmware artifact custody

Do not replace, reserialize, recompress or modify original bytes. Original artifacts are **not committed in this scaffold**.

## Source
- Google Drive file observed 2026-10-11 (user-owned historical archive; displayed date 2015-02-12).
- Archive name: `Only-for-IPV3-160W-Upgrade-Software_20141126_V3.5-1417490378.rar`
- Archive size: 32,079 bytes (previous local observation; recheck).
- Extracted: `Only for IPV3 160W Upgrade Software_20141126_V3.5.SXI`
- SXI length: 56,009 bytes
- SXI SHA-256: `ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d`

Treat this as an **upgrade package**, not proof it matches the device's factory 150 W firmware. The 150 W factory image has not been recovered.

## Verification
`python -c "import hashlib,pathlib,sys; p=pathlib.Path(sys.argv[1]); print(p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())" path/to/file.SXI`

Do not upload binary images to a public repository without confirming redistribution rights and provenance. Prefer locally supplied immutable inputs at `work/firmware/` (gitignored) initially.
