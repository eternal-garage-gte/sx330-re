import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import sxi_inspect as sxi


class InspectorTests(unittest.TestCase):
    def inspect(self, data, **options):
        return sxi.inspect_data(data, hashlib.sha256(data).hexdigest(), len(data), **options)

    def test_statistics_known_distribution(self):
        result = self.inspect(b"\x00\x01" * 128)
        self.assertEqual(result["whole_file"]["entropy_bits_per_byte"], 1.0)
        self.assertEqual(result["whole_file"]["histogram"][:3], [128, 128, 0])
        self.assertEqual(sum(result["whole_file"]["histogram"]), 256)

    def test_chunks_and_last_short_chunk(self):
        result = self.inspect(b"\x00" * 256 + b"\xff" * 44, chunk_size=256)
        self.assertEqual([(c["offset"], c["size"]) for c in result["chunks"]], [(0, 256), (256, 44)])
        self.assertEqual(result["chunks"][1]["histogram"][255], 44)
        self.assertEqual(result["last_64_offset"], 236)
        self.assertEqual(bytes.fromhex(result["last_64_hex"]), b"\0" * 20 + b"\xff" * 44)

    def test_short_file_edges_and_unknown_header(self):
        result = self.inspect(b"ABC")
        self.assertEqual(result["first_64_hex"], "414243")
        self.assertEqual(result["last_64_hex"], "414243")
        self.assertFalse(result["sxi_header"]["matches"])
        self.assertEqual(result["token_probes"][0]["status"], "unavailable")

    def test_header_and_padding(self):
        result = self.inspect(sxi.HEADER + b"\0" * 8)
        self.assertTrue(result["sxi_header"]["matches"])
        self.assertTrue(result["sxi_header"]["zero_padding_24_to_31"])

    def test_strings_offsets_and_eof(self):
        strings = self.inspect(b"\0ABCDEF\xffuvwxyz")["strings"]
        self.assertEqual([(s["offset"], s["text"]) for s in strings["reported"]], [(1, "ABCDEF"), (8, "uvwxyz")])
        self.assertEqual(strings["total"], 2)

    def test_string_output_caps(self):
        result = self.inspect(b"A" * 200 + b"\0" + (b"abcdef\0" * 200))["strings"]
        self.assertEqual(result["total"], 201)
        self.assertEqual(len(result["reported"]), 128)
        self.assertEqual(result["omitted"], 73)
        self.assertEqual(result["reported"][0]["length"], 200)
        self.assertEqual(len(result["reported"][0]["text"]), 96)
        self.assertTrue(result["reported"][0]["text_truncated"])

    def test_overlapping_patterns(self):
        pattern = self.inspect(b"A" * 20)["repeated_patterns"][0]["reported"][0]
        self.assertEqual(pattern["hex"], "41414141")
        self.assertEqual(pattern["count"], 17)
        self.assertEqual(pattern["offsets"], list(range(8)))
        self.assertEqual(pattern["offsets_omitted"], 9)

    def test_pattern_ties_have_byte_order(self):
        result = self.inspect(b"BBBB\0BBBB\0AAAA\0AAAA")["repeated_patterns"][0]["reported"]
        tied = [entry["hex"] for entry in result if entry["count"] == 2]
        self.assertEqual(tied, sorted(tied))

    def test_hash_gate_before_parsing(self):
        with mock.patch.object(sxi, "statistics") as parse:
            with self.assertRaisesRegex(sxi.InspectionError, "SHA-256 mismatch"):
                sxi.inspect_data(b"abc", "0" * 64, 3)
            parse.assert_not_called()

    def test_size_gate(self):
        with self.assertRaisesRegex(sxi.InspectionError, "size mismatch"):
            sxi.inspect_data(b"abc", hashlib.sha256(b"abc").hexdigest(), 4)

    def test_empty_and_oversized_bytes(self):
        for data in (b"", b"A" * (sxi.MAX_INPUT_SIZE + 1)):
            with self.subTest(length=len(data)), self.assertRaises(sxi.InspectionError):
                sxi.verify_data(data, "0" * 64, 1)

    def test_invalid_options(self):
        for options in (("bad", 1, 4096, 6), ("0" * 64, 0, 4096, 6),
                        ("0" * 64, sxi.MAX_INPUT_SIZE + 1, 4096, 6),
                        ("0" * 64, 1, 0, 6), ("0" * 64, 1, 65537, 6),
                        ("0" * 64, 1, 4096, 0), ("0" * 64, 1, 4096, 97)):
            with self.subTest(options=options), self.assertRaises(sxi.InspectionError):
                sxi.validate_options(*options)

    def test_token_grammar_literals_pairs_and_markers(self):
        result = sxi.token_probe(b"\0\xff\x011\xf00\xf0\xa0\xf0\xc0\xfe4", 0)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["counts"], {"digit_pairs": 3, "literal_00": 1, "literal_ff": 1, "markers": 2})
        self.assertEqual(result["projection_size"], 5)
        self.assertEqual(result["projection_sha256"], hashlib.sha256(b"\0\xff\x01\xf0\xfe").hexdigest())
        self.assertEqual(result["markers"][0]["offsets"], [6])
        self.assertEqual(result["markers"][1]["offsets"], [8])

    def test_token_mismatch_and_truncation_stop_without_repair(self):
        for data, offset in ((b"\x011\x022\x033", None), (b"\x011\x023\0", 2),
                             (b"\x011\x02", 2), (b"\xf0\xb0", 0)):
            result = sxi.token_probe(data, 0)
            with self.subTest(data=data):
                if offset is None:
                    self.assertEqual(result["status"], "complete")
                else:
                    self.assertEqual(result["status"], "rejected")
                    self.assertEqual(result["first_invalid"]["offset"], offset)
                    self.assertEqual(result["end"], offset)

    def test_known_crc32_trailer(self):
        candidates = sxi.checksum_candidates(b"123456789\x26\x39\xf4\xcb")
        entry = next(e for e in candidates if e["start"] == 0 and len(e["trailer_hex"]) == 8)
        self.assertEqual(entry["calculated"]["crc32_ieee_zlib"], 0xCBF43926)
        self.assertIn({"algorithm": "crc32_ieee_zlib", "byte_order": "little"}, entry["matches"])

    def test_encoding_probes_record_exact_invalid_offset(self):
        probes = sxi.encoding_probes(b"deadbeef\0")
        entry = next(e for e in probes if e["start"] == 0 and e["hypothesis"] == "ascii_hex")
        self.assertFalse(entry["alphabet_compatible"])
        self.assertEqual(entry["first_invalid_offset"], 8)
        self.assertEqual(entry["first_invalid_hex"], "00")

    def test_cli_is_deterministic_and_input_unchanged(self):
        data = b"ABCDEF\0\xff" * 40
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.sxi"
            path.write_bytes(data)
            before = path.stat()
            args = [str(path), "--expected-size", str(len(data)), "--expected-sha256", hashlib.sha256(data).hexdigest()]
            outputs = []
            for _ in range(2):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(sxi.main(args), 0)
                outputs.append(output.getvalue())
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(json.loads(outputs[0])["size"], len(data))
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)

    def test_cli_errors_have_no_json_and_exit_two(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.sxi"
            path.write_bytes(b"abc")
            for args, message in (([str(path)], "size mismatch"),
                                  ([str(path), "--expected-size", "3"], "SHA-256 mismatch"),
                                  ([str(path) + ".missing"], "No such file")):
                output, errors = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    self.assertEqual(sxi.main(args), 2)
                self.assertEqual(output.getvalue(), "")
                self.assertIn(message, errors.getvalue())

    def test_oversized_regular_file_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.sxi"
            with path.open("wb") as output:
                output.truncate(sxi.MAX_INPUT_SIZE + 1)
            with self.assertRaisesRegex(sxi.InspectionError, "size mismatch"):
                sxi.read_verified(path, "0" * 64, 1)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO test")
    def test_fifo_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.fifo"
            os.mkfifo(path)
            with self.assertRaisesRegex(sxi.InspectionError, "regular binary file"):
                sxi.read_verified(path, "0" * 64, 1)


if __name__ == "__main__":
    unittest.main()
