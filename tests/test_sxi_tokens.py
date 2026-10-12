import contextlib
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import sxi_tokens as sxi


class TokenTests(unittest.TestCase):
    def test_every_pair_value_and_literals(self):
        body = b"\0\xff" + b"".join(bytes((v, 0x30 + v % 10)) for v in range(1, 255))
        data = b"opaque prefix" + body + b"\xf0\xa0\xf0\xc0"
        doc = sxi.decode(data, len(b"opaque prefix"))
        self.assertEqual(sxi.encode(doc), data)
        self.assertEqual(sxi.digest(sxi.encode(doc)), sxi.digest(data))
        self.assertEqual(len(doc.tokens), 258)
        self.assertEqual([t.raw[0] for t in doc.tokens[2:-2]], list(range(1, 255)))
        self.assertEqual([t.kind for t in doc.tokens[-2:]], ["marker_a0", "marker_c0"])
        self.assertEqual(doc.tokens[0].offset, len(doc.prefix))
        self.assertEqual(doc.tokens[-1].offset, len(data) - 2)

    def test_markers_adjacent_and_f0_digit_pair(self):
        data = b"\xf0\x30\xf0\xa0\xf0\xc0\0"
        doc = sxi.decode(data, 0)
        self.assertEqual([t.offset for t in doc.tokens], [0, 2, 4, 6])
        self.assertEqual(sxi.projection(doc, False), b"\xf0\0")
        self.assertEqual(sxi.projection(doc, True), b"\xf0\xf0\xa0\xf0\xc0\0")
        self.assertEqual(sxi.encode(doc), data)

    def test_malformed_and_truncated_tokens(self):
        for body in (b"\x01", b"\xf0", b"\x01\x30", b"\xf0\xb0", b"\xff\x01\x31\x02\x31"):
            with self.subTest(body=body), self.assertRaisesRegex(sxi.TokenError, "source offset"):
                sxi.decode(b"prefix" + body, 6)

    def test_literal_followed_by_digit_is_separate_token(self):
        for data in (b"\0\x30", b"\xff\x35"):
            with self.assertRaises(sxi.TokenError):
                sxi.decode(data, 0)

    def test_start_and_input_boundaries(self):
        for start in (-1, 2, True, "0"):
            with self.subTest(start=start), self.assertRaises(sxi.TokenError):
                sxi.decode(b"\0", start)
        for data in (bytearray(b"\0"), b"\0" * (sxi.MAX_INPUT_SIZE + 1)):
            with self.assertRaises(sxi.TokenError):
                sxi.decode(data, 0)
        for data, start in ((b"", 0), (b"opaque", 6), (b"\0" * sxi.MAX_INPUT_SIZE, 0)):
            self.assertEqual(sxi.encode(sxi.decode(data, start)), data)

    def test_serializer_rejects_forged_representation(self):
        doc = sxi.decode(b"\0\x01\x31", 0)
        bad = [replace(doc, source_size=4), replace(doc, source_size=2),
               replace(doc, source_size=sxi.MAX_INPUT_SIZE + 1),
               replace(doc, prefix=bytearray()), replace(doc, tokens=list(doc.tokens)),
               replace(doc, tokens=(replace(doc.tokens[0], offset=1), doc.tokens[1])),
               replace(doc, tokens=(doc.tokens[0], replace(doc.tokens[1], offset=0))),
               replace(doc, tokens=(replace(doc.tokens[0], kind="digit_pair"), doc.tokens[1])),
               replace(doc, tokens=(replace(doc.tokens[0], raw=b"\x01\x30"),)),
               replace(doc, tokens=(replace(doc.tokens[0], raw=b"\0\0"),)),
               replace(doc, tokens=(replace(doc.tokens[0], raw=b"\0" * (sxi.MAX_INPUT_SIZE + 1)),)),
               replace(doc, tokens=(replace(doc.tokens[0], offset=False), doc.tokens[1])),
               replace(doc, tokens=doc.tokens * (sxi.MAX_INPUT_SIZE // 2 + 1))]
        for value in bad + [None]:
            with self.subTest(value=type(value)), self.assertRaises(sxi.TokenError):
                sxi.encode(value)

    def test_report_coordinates_context_and_prefix_scan(self):
        data = b"\x00\x80" + b"\0\0\xf0\xa0\0\xf0\xc0\x01\x31"
        doc = sxi.decode(data, 2)
        result = sxi.report(data, doc)
        a, c = result["markers"]
        self.assertEqual((a["source_offset"], a["token_index"], a["omit_offset"], a["retain_offset"]), (4, 2, 2, 2))
        self.assertEqual((a["zero_literals_before"], a["zero_literals_after"]), (2, 1))
        self.assertEqual((c["omit_offset"], c["retain_offset"]), (3, 5))
        self.assertIn({"quantity": "32KiB", "value": 32768, "offset": 0,
                       "width": 2, "byte_order": "little"}, result["prefix_integer_scan"]["matches"])
        rebuilt = bytes.fromhex(result["prefix_hex"]) + b"".join(bytes.fromhex(t["raw_hex"]) for t in result["tokens"])
        self.assertEqual(rebuilt, data)
        self.assertEqual(result, sxi.report(data, doc))
        with self.assertRaisesRegex(sxi.TokenError, "round trip"):
            sxi.report(data + b"\0", doc)

    def run_cli(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sxi.main(args)
        return code, out.getvalue(), err.getvalue()

    def test_cli_deterministic_read_only_and_verification_gate(self):
        data = b"prefix\0\xf0\xa0\x01\x31"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.sxi"
            path.write_bytes(data)
            before = path.stat()
            args = [str(path), "--start", "6", "--expected-size", str(len(data)),
                    "--expected-sha256", hashlib.sha256(data).hexdigest()]
            first = self.run_cli(args)
            self.assertEqual(first, self.run_cli(args))
            self.assertEqual(first[0], 0)
            self.assertTrue(json.loads(first[1])["round_trip"]["byte_identical"])
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
            with mock.patch.object(sxi, "decode") as parse:
                code, out, err = self.run_cli(args[:-1] + ["0" * 64])
                self.assertEqual((code, out), (2, ""))
                self.assertIn("SHA-256 mismatch", err)
                parse.assert_not_called()

    def test_cli_missing_and_malformed(self):
        self.assertEqual(self.run_cli(["/no/such/sxi"])[0], 2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.sxi"
            data = b"\x01\x30"
            path.write_bytes(data)
            code, out, err = self.run_cli([str(path), "--start", "0", "--expected-size", "2",
                                          "--expected-sha256", sxi.digest(data)])
            self.assertEqual((code, out), (2, ""))
            self.assertIn("source offset 0x0", err)

    def test_original_artifact_when_available(self):
        path = Path(__file__).resolve().parents[1] / "work/firmware/ipv3_160W_V3.5.SXI"
        if not path.exists():
            self.skipTest("verified original not staged in ignored work/firmware")
        data = sxi.read_verified(path, sxi.SAMPLE_SHA256, sxi.SAMPLE_SIZE)
        doc = sxi.decode(data)
        result = sxi.report(data, doc)
        self.assertEqual(result["counts"], {"digit_pair": 22946, "literal_00": 8815,
                         "literal_ff": 636, "marker_a0": 113, "marker_c0": 44})
        self.assertEqual(result["consumed_body_bytes"], 55657)
        self.assertEqual(sxi.encode(doc), data)
        self.assertEqual(sxi.digest(sxi.encode(doc)), sxi.SAMPLE_SHA256)
        self.assertEqual(result["projections"]["omit_markers"], {"size": 32397,
            "sha256": "320fdd602eb7567f65fae0523617fdf523362a5545d35666eb55e335df5d50e2"})
        self.assertEqual(result["projections"]["retain_markers"], {"size": 32711,
            "sha256": "e2c2adb0c9d99140278ac8637f0109035d00454da39a802dcc822f1a472d026d"})
        for t in doc.tokens:
            self.assertEqual(data[t.offset:t.offset + len(t.raw)], t.raw)
        json_bytes = bytes.fromhex(result["prefix_hex"]) + b"".join(
            bytes.fromhex(t["raw_hex"]) for t in result["tokens"])
        self.assertEqual(json_bytes, data)
        self.assertEqual(len(result["markers"]), 157)
        self.assertEqual(result["markers"][0]["source_offset"], 393)
        self.assertEqual(result["prefix_integer_scan"]["matches"], [])


if __name__ == "__main__":
    unittest.main()
