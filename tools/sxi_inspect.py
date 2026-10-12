#!/usr/bin/env python3
"""Bounded, offline SXI diagnostics. This is not a validated firmware decoder."""

import argparse
import binascii
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import zlib


SAMPLE_SHA256 = "ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d"
SAMPLE_SIZE = 56009
HEADER = b"v20140808-SXi-YiHiEcigar"
MAX_INPUT_SIZE = 262144
MAX_STRINGS = 128
MAX_STRING_TEXT = 96
MAX_PATTERNS = 8
MAX_OFFSETS = 8
MARKERS = (b"\xf0\xa0", b"\xf0\xc0")


class InspectionError(ValueError):
    """Invalid input or an unmet verification gate."""


def validate_options(expected_sha256, expected_size, chunk_size, min_string):
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise InspectionError("expected SHA-256 must contain exactly 64 hex digits")
    if not 1 <= expected_size <= MAX_INPUT_SIZE:
        raise InspectionError(f"expected size must be 1..{MAX_INPUT_SIZE} bytes")
    if not 256 <= chunk_size <= 65536:
        raise InspectionError("chunk size must be 256..65536 bytes")
    if not 1 <= min_string <= MAX_STRING_TEXT:
        raise InspectionError(f"minimum string length must be 1..{MAX_STRING_TEXT}")


def verify_data(data, expected_sha256, expected_size):
    if not 1 <= len(data) <= MAX_INPUT_SIZE:
        raise InspectionError(f"input size must be 1..{MAX_INPUT_SIZE} bytes")
    if len(data) != expected_size:
        raise InspectionError(f"size mismatch: expected {expected_size}, got {len(data)}")
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_sha256.lower():
        raise InspectionError(f"SHA-256 mismatch: expected {expected_sha256.lower()}, got {digest}")
    return digest


def read_verified(path, expected_sha256, expected_size):
    """Read at most cap+1 bytes; reject devices, directories and FIFOs."""
    validate_options(expected_sha256, expected_size, 4096, 6)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise InspectionError("input must be a regular binary file")
        if before.st_size != expected_size:
            raise InspectionError(f"size mismatch: expected {expected_size}, got {before.st_size}")
        data = source.read(MAX_INPUT_SIZE + 1)
        after = os.fstat(source.fileno())
    if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
        after.st_size, after.st_mtime_ns, after.st_ctime_ns
    ):
        raise InspectionError("input changed while being read")
    verify_data(data, expected_sha256, expected_size)
    return data


def statistics(data):
    counts = [0] * 256
    for value in data:
        counts[value] += 1
    entropy = -sum((n / len(data)) * math.log2(n / len(data)) for n in counts if n)
    return {"size": len(data), "entropy_bits_per_byte": round(entropy, 6),
            "histogram": counts}


def printable_strings(data, minimum):
    results = []
    total = 0
    start = None
    for offset in range(len(data) + 1):
        printable = offset < len(data) and 0x20 <= data[offset] <= 0x7E
        if printable and start is None:
            start = offset
        elif not printable and start is not None:
            length = offset - start
            if length >= minimum:
                total += 1
                if len(results) < MAX_STRINGS:
                    results.append({"offset": start, "length": length,
                                    "text": data[start:start + min(length, MAX_STRING_TEXT)].decode("ascii"),
                                    "text_truncated": length > MAX_STRING_TEXT})
            start = None
    return {"minimum_length": minimum, "total": total, "reported": results,
            "omitted": total - len(results), "max_reported": MAX_STRINGS}


def repeated_patterns(data):
    """Count overlapping n-grams; cap input, widths, output and stored offsets."""
    results = []
    for width in (4, 8, 16):
        counts = Counter(data[i:i + width] for i in range(max(0, len(data) - width + 1)))
        candidates = sorted(((p, n) for p, n in counts.items() if n > 1),
                            key=lambda entry: (-entry[1], entry[0]))[:MAX_PATTERNS]
        reported = []
        for pattern, count in candidates:
            offsets = []
            position = data.find(pattern)
            while position >= 0 and len(offsets) < MAX_OFFSETS:
                offsets.append(position)
                position = data.find(pattern, position + 1)
            reported.append({"hex": pattern.hex(), "count": count, "offsets": offsets,
                             "offsets_omitted": count - len(offsets)})
        results.append({"width": width, "overlapping": True, "reported": reported,
                        "unique_repeated": sum(n > 1 for n in counts.values())})
    return results


def token_probe(data, start):
    """Test an empirical grammar strictly, with no resynchronization or repair.

    The projection drops marker tokens and redundant decimal digits. Its hash is
    a diagnostic calculation, not evidence that it is a usable firmware image.
    """
    if not 0 <= start < len(data):
        return {"start": start, "status": "unavailable", "reason": "start outside input"}
    offset = start
    counts = Counter()
    values = Counter()
    marker_counts = Counter()
    marker_offsets = {marker.hex(): [] for marker in MARKERS}
    projection = bytearray()
    first_invalid = None
    while offset < len(data):
        value = data[offset]
        pair = data[offset:offset + 2]
        if value in (0, 255):
            counts[f"literal_{value:02x}"] += 1
            projection.append(value)
            offset += 1
        elif pair in MARKERS:
            counts["markers"] += 1
            marker_counts[pair.hex()] += 1
            if len(marker_offsets[pair.hex()]) < MAX_OFFSETS:
                marker_offsets[pair.hex()].append(offset)
            offset += 2
        elif len(pair) == 2 and pair[1] == 0x30 + value % 10:
            counts["digit_pairs"] += 1
            values[value] += 1
            projection.append(value)
            offset += 2
        else:
            first_invalid = {"offset": offset, "hex": data[offset:offset + 4].hex()}
            break
    return {"start": start, "end": offset, "status": "complete" if first_invalid is None else "rejected",
            "consumed_bytes": offset - start, "first_invalid": first_invalid,
            "counts": dict(sorted(counts.items())), "unique_pair_values": len(values),
            "missing_pair_values_1_to_254": [n for n in range(1, 255) if n not in values],
            "markers": [{"hex": m.hex(), "count": marker_counts[m.hex()],
                         "offsets": marker_offsets[m.hex()],
                         "offsets_omitted": marker_counts[m.hex()] - len(marker_offsets[m.hex()])}
                        for m in MARKERS],
            "projection_policy": "retain literals and first byte of digit pairs; omit markers",
            "projection_size": len(projection),
            "projection_sha256": hashlib.sha256(projection).hexdigest(),
            "qualification": "empirical token grammar; projection is not validated firmware"}


def checksum_candidates(data):
    """Limited, explicit trailer checks; a match alone would not prove semantics."""
    results = []
    for start in (0, 32, 128, 160, 352):
        for width in (1, 2, 4):
            end = len(data) - width
            if start >= end:
                continue
            region = data[start:end]
            trailer = data[end:]
            xor = 0
            for value in region:
                xor ^= value
            candidates = {"sum_mod_width": sum(region) & ((1 << (8 * width)) - 1), "xor8": xor}
            if width == 4:
                candidates["crc32_ieee_zlib"] = zlib.crc32(region)
            elif width == 2:
                candidates["crc16_ccitt_hqx_init_0000"] = binascii.crc_hqx(region, 0)
                candidates["crc16_ccitt_hqx_init_ffff"] = binascii.crc_hqx(region, 65535)
            stored = {order: int.from_bytes(trailer, order) for order in ("little", "big")}
            results.append({"start": start, "end_exclusive": end, "trailer_offset": end,
                            "trailer_hex": trailer.hex(), "stored": stored, "calculated": candidates,
                            "matches": [{"algorithm": name, "byte_order": order}
                                        for name, value in sorted(candidates.items())
                                        for order in ("little", "big") if value == stored[order]]})
    return results


def encoding_probes(data):
    results = []
    alphabets = {"ascii_hex": set(b"0123456789abcdefABCDEF \t\r\n"),
                 "base64_text": set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/= \t\r\n")}
    signatures = {"gzip": b"\x1f\x8b", "bzip2": b"BZh", "xz": b"\xfd7zXZ\x00", "zip": b"PK\x03\x04"}
    for start in (0, 32, 128, 160, 352):
        if start >= len(data):
            continue
        for name, alphabet in sorted(alphabets.items()):
            invalid = next((i for i in range(start, len(data)) if data[i] not in alphabet), None)
            results.append({"start": start, "hypothesis": name, "alphabet_compatible": invalid is None,
                            "first_invalid_offset": invalid,
                            "first_invalid_hex": None if invalid is None else f"{data[invalid]:02x}"})
        prefix = data[start:start + 6]
        zlib_header = (len(prefix) >= 2 and prefix[0] & 0x0F == 8 and prefix[0] >> 4 <= 7
                       and int.from_bytes(prefix[:2], "big") % 31 == 0)
        results.append({"start": start, "hypothesis": "standard_compression_prefix",
                        "prefix_hex": prefix.hex(), "zlib_header_compatible": zlib_header,
                        "matching_signatures": [name for name, sig in sorted(signatures.items())
                                                if prefix.startswith(sig)]})
    return results


def inspect_data(data, expected_sha256, expected_size, chunk_size=4096, min_string=6):
    validate_options(expected_sha256, expected_size, chunk_size, min_string)
    digest = verify_data(data, expected_sha256, expected_size)  # Gate before parsing.
    chunks = []
    for offset in range(0, len(data), chunk_size):
        chunks.append({"offset": offset, **statistics(data[offset:offset + chunk_size])})
    return {"schema_version": 1, "size": len(data), "sha256": digest,
            "first_64_hex": data[:64].hex(), "last_64_hex": data[-64:].hex(),
            "last_64_offset": max(0, len(data) - 64),
            "sxi_header": {"expected_ascii": HEADER.decode("ascii"), "offset": 0,
                           "matches": data.startswith(HEADER),
                           "zero_padding_24_to_31": data[24:32] == b"\0" * 8},
            "whole_file": statistics(data), "chunk_size": chunk_size, "chunks": chunks,
            "strings": printable_strings(data, min_string), "repeated_patterns": repeated_patterns(data),
            "encoding_probes": encoding_probes(data),
            "token_probes": [token_probe(data, start) for start in (128, 160, 256, 352)],
            "checksum_candidates": checksum_candidates(data),
            "limits": {"max_input_bytes": MAX_INPUT_SIZE, "max_strings": MAX_STRINGS,
                       "max_string_text": MAX_STRING_TEXT, "pattern_widths": [4, 8, 16],
                       "max_patterns_per_width": MAX_PATTERNS, "max_offsets": MAX_OFFSETS}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--expected-sha256", default=SAMPLE_SHA256,
                        help="verification hash; defaults to the recovered A1 sample")
    parser.add_argument("--expected-size", type=int, default=SAMPLE_SIZE)
    parser.add_argument("--chunk-size", type=int, default=4096)
    parser.add_argument("--min-string", type=int, default=6)
    args = parser.parse_args(argv)
    try:
        validate_options(args.expected_sha256, args.expected_size, args.chunk_size, args.min_string)
        data = read_verified(args.path, args.expected_sha256, args.expected_size)
        report = inspect_data(data, args.expected_sha256, args.expected_size, args.chunk_size, args.min_string)
    except (OSError, InspectionError) as error:
        print(f"sxi_inspect: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
