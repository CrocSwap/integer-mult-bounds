#!/usr/bin/env python3
"""Positive fixture and semantic/parser/source-pin controls, Apache-2.0."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("independent_pr540_audit", PACKAGE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class AuditControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.manifest_sha = v.snapshot()
        cls.word = v.decode_records(gzip.decompress(cls.files["inputs/records.bin.gz"]))
        cls.template = json.loads(gzip.decompress(cls.files["inputs/hosted-template.json.gz"]))
        cls.states = json.loads(gzip.decompress(cls.files["inputs/states.json.gz"]))
        cls.frames = json.loads(gzip.decompress(cls.files["inputs/frames.json.gz"]))["frames"]
        cls.matrix = v.definitions(cls.files["MatrixData.lean"].decode())
        cls.frame_defs = v.definitions(cls.files["FrameTraceLiterals.lean"].decode())
        cls.scalar = v.checkpoints(cls.matrix, v.nodes(cls.files, "MatrixNodes", 22))
        cls.framed = v.checkpoints(cls.frame_defs, v.nodes(cls.files, "FrameTraceNodes", 17), framed=True)
        cls.first_copy = next(i for i, e in enumerate(cls.word) if e[0] == 2)
        cls.first_erase = next(i for i, e in enumerate(cls.word) if e[0] == 3)
        cls.first_move = next(i for i, e in enumerate(cls.word) if e[0] == 0)

    def replay(self, word=None, scalar=None, framed=None, dirty=False):
        return v.replay(self.word if word is None else word, self.states, self.frames,
                        self.scalar if scalar is None else scalar,
                        self.framed if framed is None else framed, dirty_private=dirty)

    def table_mutation(self, filename, name, old, new):
        files = self.files.copy()
        lines = files[filename].decode().splitlines()
        matches = [i for i, line in enumerate(lines) if line.startswith("def " + name + " :")]
        self.assertEqual(len(matches), 1)
        i = matches[0]
        self.assertIn(old, lines[i])
        lines[i] = lines[i].replace(old, new, 1)
        files[filename] = ("\n".join(lines) + "\n").encode()
        return files

    def owners(self, template=None, files=None):
        return v.ownership(self.template if template is None else template, self.states, self.frames,
                           self.files if files is None else files)

    def test_positive_complete_receipt(self):
        actual = v.audit(self.files)
        actual.update(status="PASS_PR540_LITERAL_SOURCE_AUDIT", audited_pr540=v.HEAD,
                      source_pr442=v.SOURCE, snapshot_files=len(self.files),
                      source_manifest_sha256=self.manifest_sha,
                      source_binary_sha256=v.sha(gzip.decompress(self.files["inputs/records.bin.gz"])))
        self.assertEqual(actual, json.loads((PACKAGE / "EXPECTED.json").read_text()))

    def test_omitted_add_changes_checkpoint(self):
        word = copy.deepcopy(self.word)
        word.pop(76)  # OS assignment seed selects a fixed first-chunk ADD.
        self.assertEqual(self.word[76][0], 1)
        with self.assertRaisesRegex(v.Rejected, "scalar checkpoint 1"):
            self.replay(word=word)

    def test_changed_add_source_changes_checkpoint(self):
        word = copy.deepcopy(self.word)
        word[0][2] = 252 if word[0][2] != 252 else 253
        with self.assertRaisesRegex(v.Rejected, "scalar checkpoint 1"):
            self.replay(word=word)

    def test_target_invisible_helper_checkpoint_fault(self):
        scalar = copy.deepcopy(self.scalar)
        scalar[1][0][240 + 76] ^= 1
        self.assertEqual(scalar[1][0][:240], self.scalar[1][0][:240])
        with self.assertRaisesRegex(v.Rejected, "scalar checkpoint 1"):
            self.replay(scalar=scalar)

    def test_frame_checkpoint_fault(self):
        framed = copy.deepcopy(self.framed)
        framed[1][0][240 + 76] += 1
        with self.assertRaisesRegex(v.Rejected, "frame checkpoint 1"):
            self.replay(framed=framed)

    def test_dirty_private_copy_guard(self):
        with self.assertRaisesRegex(v.Rejected, f"COPY clean guard at event {self.first_copy}"):
            self.replay(dirty=True)

    def test_wrong_erase_center(self):
        word = copy.deepcopy(self.word)
        word[self.first_erase][1] = (word[self.first_erase][1] + 1) % v.LIVE
        with self.assertRaisesRegex(v.Rejected, "ERASE guard"):
            self.replay(word=word)

    def test_write_to_retained_center(self):
        word = copy.deepcopy(self.word)
        word[self.first_copy + 1] = [1, word[self.first_copy][1], 0, 1, 0, 0]
        with self.assertRaisesRegex(v.Rejected, "write to retained center"):
            self.replay(word=word)

    def test_closed_private_read(self):
        word = copy.deepcopy(self.word)
        word[0][2] = v.PRIVATE
        with self.assertRaisesRegex(v.Rejected, "closed private read at event 0"):
            self.replay(word=word)

    def test_out_of_range_low_bit_alias(self):
        word = copy.deepcopy(self.word)
        word[0][1] += v.SIZE
        with self.assertRaisesRegex(v.Rejected, "register bound at event 0"):
            self.replay(word=word)

    def test_copy_rank_fault(self):
        word = copy.deepcopy(self.word)
        word[self.first_copy][5] = 7
        with self.assertRaisesRegex(v.Rejected, "COPY frame/rank"):
            self.replay(word=word)

    def test_move_old_frame_fault(self):
        word = copy.deepcopy(self.word)
        word[self.first_move][2] = 1 if word[self.first_move][2] != 1 else 0
        with self.assertRaisesRegex(v.Rejected, "MOVE frame"):
            self.replay(word=word)

    def test_nonbinary_add_coefficient(self):
        word = copy.deepcopy(self.word)
        word[0][3] = 3
        with self.assertRaisesRegex(v.Rejected, "ADD operands"):
            self.replay(word=word)

    def test_chunk_order_fault(self):
        defs = self.matrix.copy()
        kind, body = defs["forwardChunks"]
        defs["forwardChunks"] = (kind, body.replace("chunk0,chunk1,", "chunk1,chunk0,", 1))
        with self.assertRaisesRegex(v.Rejected, "chunk order"):
            v.chunks(defs, "List Event", "forwardChunks", "forwardWord")

    def test_cyclic_chunk_suffix(self):
        defs = self.matrix.copy()
        name = "chunk0_tail12"
        defs[name] = ("List Event", name)
        with self.assertRaisesRegex(v.Rejected, "missing/cyclic chunk suffix"):
            v.chunks(defs, "List Event", "forwardChunks", "forwardWord")

    def test_scalar_literal_operand_fault(self):
        files = self.files.copy()
        old = "⟨1,125,516,true⟩"
        self.assertIn(old.encode(), files["MatrixData.lean"])
        files["MatrixData.lean"] = files["MatrixData.lean"].replace(old.encode(), "⟨1,125,517,true⟩".encode(), 1)
        with self.assertRaisesRegex(v.Rejected, "scalar literal word"):
            v.audit(files)

    def test_false_checkpoint_flag(self):
        defs = self.matrix.copy()
        kind, body = defs["state1"]
        defs["state1"] = (kind, body.replace("true", "false"))
        with self.assertRaisesRegex(v.Rejected, "false scalar checkpoint flag"):
            v.checkpoints(defs, v.nodes(self.files, "MatrixNodes", 22))

    def test_duplicate_declaration(self):
        with self.assertRaisesRegex(v.Rejected, "duplicate declaration"):
            v.definitions("def n : Tree Nat := .leaf 1\ndef n : Tree Nat := .leaf 2\n")

    def test_unsupported_literal_tail(self):
        with self.assertRaisesRegex(v.Rejected, "unconsumed literal syntax"):
            v.atom("(.leaf 1) garbage")

    def test_cyclic_tree_reference(self):
        with self.assertRaisesRegex(v.Rejected, "missing/cyclic tree reference"):
            v.Trees({"n": ("n", 0)}).get("n", 0)

    def test_compressed_checkpoint_tree(self):
        with self.assertRaisesRegex(v.Rejected, "wrong checkpoint tree depth"):
            v.Trees({"n": 0}).table("n", v.SIZE, depth=10)

    def test_owner_collision(self):
        template = copy.deepcopy(self.template)
        owners = next(c for c in template["calls"] if c["stage"] == 2 and c["replica"] == 0)["owners"]
        first = 240
        key = tuple(owners[first][1]) + (self.states["initial"][str(first)],)
        other = next(i for i in range(first + 1, v.LIVE)
                     if tuple(owners[i][1]) + (self.states["initial"][str(i)],) == key)
        owners[other][0] = owners[first][0]
        with self.assertRaisesRegex(v.Rejected, "owner injectivity"):
            self.owners(template=template)

    def test_family_literal_fault(self):
        files = self.table_mutation("OwnershipDatumCore.lean", "familyTable", ".leaf 0", ".leaf 1")
        with self.assertRaisesRegex(v.Rejected, "ownership table: familyTable"):
            self.owners(files=files)

    def test_permutation_literal_fault(self):
        files = self.table_mutation("OwnershipDatumCore.lean", "permTable", ".leaf 0", ".leaf 1")
        with self.assertRaisesRegex(v.Rejected, "ownership table: permTable"):
            self.owners(files=files)

    def test_inverse_permutation_fault(self):
        files = self.table_mutation("OwnershipDatumCore.lean", "invPermTable", ".leaf 0", ".leaf 1")
        with self.assertRaisesRegex(v.Rejected, "ownership table: invPermTable"):
            self.owners(files=files)

    def test_inverse_owner_unused_slot_fault(self):
        files = self.table_mutation("OwnershipInverseTable.lean", "inverseOwnerTable_part0",
                                    ".leaf 987", ".leaf 0")
        with self.assertRaisesRegex(v.Rejected, "ownership table: inverseOwnerTable"):
            self.owners(files=files)

    def test_source_kernel_mask_fault(self):
        files = self.table_mutation("OwnershipDatumCore.lean", "sourceBits", ".leaf 254", ".leaf 255")
        with self.assertRaisesRegex(v.Rejected, "ownership table: sourceBits"):
            self.owners(files=files)

    def test_wrong_selected_call(self):
        template = copy.deepcopy(self.template)
        call = next(c for c in template["calls"] if c["stage"] == 2 and c["replica"] == 0)
        call["orientation"] = "backward"
        with self.assertRaisesRegex(v.Rejected, "selected invocation"):
            self.owners(template=template)

    def test_binary_phase_annotation(self):
        raw = bytearray(gzip.decompress(self.files["inputs/records.bin.gz"]))
        struct.pack_into("<i", raw, 20, 0)
        with self.assertRaisesRegex(v.Rejected, "raw phase annotation"):
            v.decode_records(raw)

    def test_binary_truncation(self):
        with self.assertRaisesRegex(v.Rejected, "raw record length"):
            v.decode_records(gzip.decompress(self.files["inputs/records.bin.gz"])[:-1])

    def test_snapshot_hash_fault(self):
        with tempfile.TemporaryDirectory(prefix="pr540-negative-") as tmp:
            root = Path(tmp)
            (root / "SOURCE-SNAPSHOT.json").write_bytes((PACKAGE / "SOURCE-SNAPSHOT.json").read_bytes())
            payload = bytearray((PACKAGE / "PR540-SOURCES.tar.gz").read_bytes())
            payload[76] ^= 1
            (root / "PR540-SOURCES.tar.gz").write_bytes(payload)
            with self.assertRaisesRegex(v.Rejected, "snapshot archive digest"):
                v.snapshot(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
