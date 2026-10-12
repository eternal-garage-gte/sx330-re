#!/usr/bin/env python3
"""Lossless empirical SXI representation; projections are not validated firmware."""

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

try:
    from .sxi_inspect import (InspectionError, MAX_INPUT_SIZE, SAMPLE_SHA256,
                              SAMPLE_SIZE, read_verified)
except ImportError:  # Direct script invocation.
    from sxi_inspect import (InspectionError, MAX_INPUT_SIZE, SAMPLE_SHA256,
                             SAMPLE_SIZE, read_verified)

BODY_START = 0x160
MARKERS = {b"\xf0\xa0": "marker_a0", b"\xf0\xc0": "marker_c0"}


class TokenError(ValueError):
    """Invalid grammar or inconsistent lossless representation."""


@dataclass(frozen=True)
class Token:
    offset: int  # Absolute original source offset, never a memory address.
    kind: str
    raw: bytes


@dataclass(frozen=True)
class Document:
    prefix: bytes  # Opaque and preserved, including all padding.
    tokens: tuple[Token, ...]
    source_size: int


def classify(raw):
    if raw == b"\0":
        return "literal_00"
    if raw == b"\xff":
        return "literal_ff"
    if raw in MARKERS:
        return MARKERS[raw]
    if (len(raw) == 2 and 1 <= raw[0] <= 254
            and raw[1] == 0x30 + raw[0] % 10):
        return "digit_pair"
    raise TokenError(f"invalid token {raw.hex()}")


def decode(data, start=BODY_START):
    """Preserve an opaque prefix and strictly tokenize to EOF, without repair.

    API inputs must be immutable bytes, capped at 262144; start is explicit and
    is not discovered or interpreted as an executable boundary. Empty suffixes
    are allowed for synthetic representation tests. CLI verifies size/hash first.
    """
    if not isinstance(data, bytes):
        raise TokenError("input must be immutable bytes")
    if not 0 <= len(data) <= MAX_INPUT_SIZE:
        raise TokenError("input exceeds byte cap")
    if type(start) is not int or not 0 <= start <= len(data):
        raise TokenError("start outside input")
    tokens = []
    offset = start
    while offset < len(data):
        width = 1 if data[offset] in (0, 255) else 2
        raw = data[offset:offset + width]
        try:
            kind = classify(raw)
        except TokenError as error:
            raise TokenError(f"at source offset 0x{offset:x}: {error}") from error
        tokens.append(Token(offset, kind, raw))
        offset += width
    return Document(data[:start], tuple(tokens), len(data))


def encode(document):
    """Serialize original SXI bytes; reject gaps, overlaps and false classes.

    This is representation recovery, not firmware patch generation. The token
    count, claimed source size and output are checked against the hard byte cap.
    """
    if not isinstance(document, Document):
        raise TokenError("expected Document")
    if not isinstance(document.prefix, bytes) or not isinstance(document.tokens, tuple):
        raise TokenError("expected immutable prefix and token tuple")
    if (type(document.source_size) is not int
            or not len(document.prefix) <= document.source_size <= MAX_INPUT_SIZE
            or len(document.tokens) > MAX_INPUT_SIZE):
        raise TokenError("invalid source size or token count")
    output = bytearray(document.prefix)
    for token in document.tokens:
        if (not isinstance(token, Token) or type(token.offset) is not int
                or token.offset != len(output) or not isinstance(token.raw, bytes)):
            raise TokenError("invalid token or noncontiguous source offset")
        if len(token.raw) not in (1, 2):
            raise TokenError("token width must be one or two source bytes")
        if classify(token.raw) != token.kind:
            raise TokenError(f"class mismatch at 0x{token.offset:x}")
        if len(output) + len(token.raw) > document.source_size:
            raise TokenError("tokens exceed source size")
        output.extend(token.raw)
    if len(output) != document.source_size:
        raise TokenError("tokens do not cover source size")
    return bytes(output)


def projection(document, retain_markers):
    """Diagnostic only: collapse digit pairs; keep both marker bytes or neither."""
    encode(document)  # Validate all offsets/classes before projecting.
    return b"".join(t.raw if t.kind in MARKERS.values() and retain_markers
                    else b"" if t.kind in MARKERS.values() else t.raw[:1]
                    for t in document.tokens)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def report(data, document):
    """All tokens and markers retained; deterministic statistics in source order."""
    rebuilt = encode(document)
    if rebuilt != data:
        raise TokenError("direct round trip mismatch")
    dropped = projection(document, False)
    retained = projection(document, True)
    tokens = document.tokens
    markers = []
    drop_position = keep_position = 0
    # Adjacent zero-literal counts in O(n), avoiding repeated scans of long runs.
    left = [0] * len(tokens)
    right = [0] * len(tokens)
    for i in range(1, len(tokens)):
        left[i] = left[i - 1] + 1 if tokens[i - 1].kind == "literal_00" else 0
    for i in range(len(tokens) - 2, -1, -1):
        right[i] = right[i + 1] + 1 if tokens[i + 1].kind == "literal_00" else 0
    for i, t in enumerate(tokens):
        if t.kind in MARKERS.values():
            markers.append({"kind": t.kind, "raw_hex": t.raw.hex(),
                            "source_offset": t.offset, "token_index": i,
                            "omit_offset": drop_position, "retain_offset": keep_position,
                            "zero_literals_before": left[i], "zero_literals_after": right[i],
                            "context": [{"offset": x.offset, "kind": x.kind, "raw_hex": x.raw.hex()}
                                        for x in tokens[max(0, i - 4):i + 5]]})
            keep_position += 2
        else:
            drop_position += 1
            keep_position += 1
    distributions = {}
    for kind in MARKERS.values():
        group = [m for m in markers if m["kind"] == kind]
        distributions[kind] = {}
        for coordinate in ("source_offset", "token_index", "omit_offset", "retain_offset"):
            positions = [m[coordinate] for m in group]
            gaps = [b - a for a, b in zip(positions, positions[1:])]
            distributions[kind][coordinate] = {
                "positions": positions, "spacing_histogram": dict(sorted(Counter(gaps).items())),
                "residues": {str(size): dict(sorted(Counter(p % size for p in positions).items()))
                             for size in (16, 32, 64, 128, 256, 512, 1024)}}
    sizes = {"source": len(data), "body_source": len(data) - len(document.prefix),
             "omit_markers": len(dropped), "retain_markers": len(retained),
             "one_byte_per_marker": len(tokens), "32KiB": 32768, "32KiB_gap": 32768 - len(retained)}
    matches = []
    for name, value in sizes.items():
        for width in (2, 3, 4):
            for order in ("little", "big"):
                for i in range(min(len(document.prefix), BODY_START) - width + 1):
                    if int.from_bytes(document.prefix[i:i + width], order) == value:
                        matches.append({"quantity": name, "value": value, "offset": i,
                                        "width": width, "byte_order": order})
    return {"schema_version": 1, "qualification": "lossless SXI representation; projections are diagnostic",
            "source_size": len(data), "source_sha256": digest(data),
            "body_start": len(document.prefix), "prefix_hex": document.prefix.hex(),
            "counts": dict(sorted(Counter(t.kind for t in tokens).items())),
            "consumed_body_bytes": sum(len(t.raw) for t in tokens),
            "round_trip": {"byte_identical": True, "sha256": digest(rebuilt)},
            "projections": {"omit_markers": {"size": len(dropped), "sha256": digest(dropped)},
                            "retain_markers": {"size": len(retained), "sha256": digest(retained)}},
            "prefix_integer_scan": {"scan_bytes": min(len(document.prefix), BODY_START), "quantities": sizes, "matches": matches},
            "markers": markers, "marker_distributions": distributions,
            "tokens": [{"offset": t.offset, "kind": t.kind, "raw_hex": t.raw.hex()} for t in tokens],
            "limits": {"max_input_bytes": MAX_INPUT_SIZE, "context_tokens_each_side": 4}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--expected-sha256", default=SAMPLE_SHA256)
    parser.add_argument("--expected-size", type=int, default=SAMPLE_SIZE)
    parser.add_argument("--start", type=lambda s: int(s, 0), default=BODY_START)
    args = parser.parse_args(argv)
    try:
        data = read_verified(args.path, args.expected_sha256, args.expected_size)
        result = report(data, decode(data, args.start))
    except (OSError, InspectionError, TokenError) as error:
        print(f"sxi_tokens: {error}", file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
