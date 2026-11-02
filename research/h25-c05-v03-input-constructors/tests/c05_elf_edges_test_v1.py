"""Independent small byte fixtures; no native tools or archived code imports."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import unittest

MODULE = Path(__file__).resolve().parents[1] / "implementation/c05_elf_edges_v1.py"
SPEC = importlib.util.spec_from_file_location("new_c05_elf_edges", MODULE)
elf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(elf)

BASE = 0x400000
DYNAMIC = 0x200
INTERP = 0x380
STRTAB = 0x400
ORIGIN = "/fixture/subject.so"


def fixture(tags=None, interpreter=b"/lib64/ld-linux-x86-64.so.2"):
    """Pack directly from ELF64 structure layouts, without parser helpers."""
    raw = bytearray(2048)
    parts = (b"libalpha.so", b"libbeta.so", b"$ORIGIN/lib::/opt/lib", b"/extra",
             b"subject.so", b"$PLATFORM/audit.so")
    strings, offsets = bytearray(b"\0"), {}
    for part in parts:
        offsets[part.decode("ascii")] = len(strings)
        strings += part + b"\0"
    if tags is None:
        tags = [(1, offsets["libalpha.so"]), (1, offsets["libbeta.so"]),
                (1, offsets["libalpha.so"])]
    entries = [(5, BASE + STRTAB), (10, len(strings))] + list(tags) + [(0, 0), (0, 0)]
    raw[:16] = b"\x7fELF\x02\x01\x01" + b"\0" * 9
    struct.pack_into("<HHIQQQIHHHHHH", raw, 16, 3, 62, 1, 0, 64, 0, 0,
                     64, 56, 3, 0, 0, 0)
    struct.pack_into("<IIQQQQQQ", raw, 64, 1, 5, 0, BASE, BASE,
                     len(raw), len(raw), 4096)
    struct.pack_into("<IIQQQQQQ", raw, 120, 2, 4, DYNAMIC, BASE + DYNAMIC,
                     BASE + DYNAMIC, len(entries) * 16, len(entries) * 16, 8)
    struct.pack_into("<IIQQQQQQ", raw, 176, 3, 4, INTERP, BASE + INTERP,
                     BASE + INTERP, len(interpreter) + 1, len(interpreter) + 1, 1)
    for index, row in enumerate(entries):
        struct.pack_into("<qQ", raw, DYNAMIC + index * 16, *row)
    raw[INTERP:INTERP + len(interpreter) + 1] = interpreter + b"\0"
    raw[STRTAB:STRTAB + len(strings)] = strings
    return raw, offsets


def parse(raw):
    raw = bytes(raw)
    return elf.extract_elf_input_edges(raw, hashlib.sha256(raw).hexdigest(), origin=ORIGIN)


def ph_patch(raw, index, field, value):
    # Byte field offsets from the primary Elf64_Phdr layout, not parser output.
    fields = {"type": (0, "I"), "flags": (4, "I"), "offset": (8, "Q"),
              "vaddr": (16, "Q"), "paddr": (24, "Q"), "filesz": (32, "Q"),
              "memsz": (40, "Q"), "align": (48, "Q")}
    offset, form = fields[field]
    struct.pack_into("<" + form, raw, 64 + index * 56 + offset, value)


class ELFEdgesTests(unittest.TestCase):
    def rejected(self, raw, fragment):
        with self.assertRaisesRegex(elf.ELFEdgeError, fragment):
            parse(raw)

    def test_order_and_equal_needed_occurrences_are_retained(self):
        result = parse(fixture()[0])
        self.assertEqual([x["name"] for x in result["needed"]],
                         ["libalpha.so", "libbeta.so", "libalpha.so"])
        self.assertEqual([x["occurrence"] for x in result["needed"]], [0, 1, 2])
        self.assertEqual([x["dynamic_index"] for x in result["needed"]], [2, 3, 4])
        self.assertEqual(result["interpreter"], "/lib64/ld-linux-x86-64.so.2")
        self.assertFalse(result["full_C05"])
        self.assertFalse(result["loader_search_resolved"])
        self.assertTrue(all(not x["resolved"] for x in result["edges"]))
        self.assertIn("system-preload-audit-and-launch-configuration",
                      result["unresolved_loader_frontier"])

    def test_rpath_runpath_both_preserved_with_empty_and_origin(self):
        _, offsets = fixture()
        raw, _ = fixture([(15, offsets["$ORIGIN/lib::/opt/lib"]),
                          (29, offsets["/extra"]), (14, offsets["subject.so"])])
        result = parse(raw)
        self.assertEqual([p["tag"] for p in result["search_paths"]], ["DT_RPATH", "DT_RUNPATH"])
        self.assertEqual(result["search_paths"][0]["components"], ["$ORIGIN/lib", "", "/opt/lib"])
        self.assertTrue(result["search_paths"][0]["empty_component_requires_cwd"])
        self.assertTrue(result["search_paths"][0]["token_expansion_required"])
        self.assertNotIn("DT_SONAME", [e["tag"] for e in result["edges"]])
        self.assertEqual(result["strings"][-1]["name"], "subject.so")

    def test_consequential_flags_are_explicit(self):
        raw, _ = fixture([(30, 1 | 8), (0x6ffffffb, 0x800 | 0x80 | 0x08000000), (24, 0)])
        flags = parse(raw)["dynamic_flags"]
        self.assertEqual(flags[0]["set_flags"], ["DF_ORIGIN", "DF_BIND_NOW"])
        self.assertEqual(flags[1]["set_flags"], ["DF_1_ORIGIN", "DF_1_NODEFLIB", "DF_1_PIE"])
        self.assertEqual(flags[2]["tag"], "DT_BIND_NOW")

    def test_unknown_flag_and_posflag_remain_unsupported(self):
        raw, _ = fixture([(30, 1 << 50), (0x6ffffdfd, 1), (1, 1), (0x6ffffdfd, 2)])
        result = parse(raw)
        self.assertEqual(len(result["dynamic_flags"]), 3)
        self.assertEqual(len(result["unsupported_constructs"]), 3)
        self.assertFalse(result["full_C05"])

    def test_audit_auxiliary_filter_strings_remain_edges(self):
        _, offsets = fixture()
        raw, _ = fixture([(0x6ffffefc, offsets["$PLATFORM/audit.so"]),
                          (0x7ffffffd, 1), (0x7ffffffd, 13), (0x7fffffff, 1)])
        result = parse(raw)
        self.assertEqual(len(result["edges"]), 5)
        self.assertEqual(len(result["unsupported_constructs"]), 4)
        self.assertTrue(result["edges"][1]["token_expansion_required"])

    def test_unknown_dynamic_and_program_types_are_frontier(self):
        raw, _ = fixture([(0x12345678, 99)])
        ph_patch(raw, 2, "type", 0x71234567)
        result = parse(raw)
        self.assertEqual([x["kind"] for x in result["unsupported_constructs"]],
                         ["program-header", "dynamic-tag"])

    def test_authentication_failure(self):
        raw = bytes(fixture()[0])
        with self.assertRaisesRegex(elf.ELFEdgeError, "digest mismatch"):
            elf.extract_elf_input_edges(raw, "0" * 64, origin=ORIGIN)

    def test_exact_types_block_subclass_callbacks(self):
        class HostileBytes(bytes):
            def __len__(self):
                raise RuntimeError("callback must not run")
        with self.assertRaises(elf.ELFEdgeError):
            elf.extract_elf_input_edges(HostileBytes(b"x" * 64), "0" * 64, origin=ORIGIN)

    def test_wrong_class_endian_machine_and_short_header(self):
        for offset, value in ((4, 1), (5, 2), (18, 3)):
            raw, _ = fixture()
            raw[offset] = value
            self.rejected(raw, "unsupported ELF")
        self.rejected(b"\x7fELF", "byte type/size")

    def test_header_table_truncation_and_overlap(self):
        raw, _ = fixture()
        struct.pack_into("<Q", raw, 32, 2000)
        self.rejected(raw, "out of bounds")
        raw, _ = fixture()
        struct.pack_into("<Q", raw, 32, 32)
        self.rejected(raw, "program header layout")

    def test_extended_header_counts_rejected(self):
        raw, _ = fixture()
        struct.pack_into("<H", raw, 56, 0xffff)
        self.rejected(raw, "extended ELF header counts")

    def test_segment_file_bounds_and_memory_overflow(self):
        raw, _ = fixture()
        ph_patch(raw, 0, "filesz", 2049)
        self.rejected(raw, "out of bounds")
        raw, _ = fixture()
        ph_patch(raw, 0, "vaddr", (1 << 64) - 100)
        self.rejected(raw, "overflow")

    def test_load_alignment_and_file_memory_sizes(self):
        raw, _ = fixture()
        ph_patch(raw, 0, "align", 3)
        self.rejected(raw, "alignment")
        raw, _ = fixture()
        ph_patch(raw, 0, "memsz", 1)
        self.rejected(raw, "PT_LOAD size/alignment")

    def test_ambiguous_and_duplicate_load_mapping_rejected(self):
        raw, _ = fixture()
        ph_patch(raw, 2, "type", 1)
        self.rejected(raw, "ambiguous PT_LOAD memory")

    def test_duplicate_dynamic_and_interpreter_rejected(self):
        raw, _ = fixture()
        ph_patch(raw, 2, "type", 2)
        self.rejected(raw, "duplicate PT_INTERP/PT_DYNAMIC")
        raw, _ = fixture()
        ph_patch(raw, 1, "type", 3)
        self.rejected(raw, "duplicate PT_INTERP/PT_DYNAMIC")

    def test_dynamic_virtual_file_mapping_disagreement(self):
        raw, _ = fixture()
        ph_patch(raw, 1, "vaddr", BASE + DYNAMIC + 8)
        self.rejected(raw, "PT_DYNAMIC mapping mismatch")

    def test_dynamic_table_outside_file_backed_load(self):
        raw, _ = fixture()
        ph_patch(raw, 1, "vaddr", BASE + len(raw) + 16)
        self.rejected(raw, "unmapped file-backed")

    def test_dynamic_size_and_missing_null(self):
        raw, _ = fixture()
        ph_patch(raw, 1, "filesz", 17)
        ph_patch(raw, 1, "memsz", 17)
        self.rejected(raw, "PT_DYNAMIC size/profile")
        raw, _ = fixture()
        ph_patch(raw, 1, "filesz", 5 * 16)
        ph_patch(raw, 1, "memsz", 5 * 16)
        self.rejected(raw, "missing DT_NULL")

    def test_nonzero_null_and_entries_after_null_rejected(self):
        raw, _ = fixture()
        struct.pack_into("<qQ", raw, DYNAMIC + 5 * 16, 0, 1)
        self.rejected(raw, "nonzero DT_NULL")
        raw, _ = fixture()
        struct.pack_into("<qQ", raw, DYNAMIC + 6 * 16, 1, 1)
        self.rejected(raw, "entry after DT_NULL")

    def test_duplicate_singleton_dynamic_tags_rejected(self):
        for tag in (5, 10, 15, 29, 30, 0x6ffffffb):
            raw, _ = fixture([(tag, 1), (tag, 1)])
            self.rejected(raw, "duplicate singleton")

    def test_string_table_pair_bounds_and_mapping(self):
        raw, _ = fixture()
        struct.pack_into("<qQ", raw, DYNAMIC + 16, 12, 0)
        self.rejected(raw, "incomplete DT_STRTAB/DT_STRSZ")
        raw, _ = fixture()
        struct.pack_into("<qQ", raw, DYNAMIC, 5, BASE + len(raw) - 1)
        self.rejected(raw, "unmapped file-backed")

    def test_bad_string_offset_non_ascii_and_unterminated_interp(self):
        raw, _ = fixture([(1, 99999)])
        self.rejected(raw, "dynamic string offset")
        raw, _ = fixture()
        raw[STRTAB + 1] = 255
        self.rejected(raw, "unsupported ELF edge string")
        raw, _ = fixture()
        raw[INTERP + len(b"/lib64/ld-linux-x86-64.so.2")] = 65
        self.rejected(raw, "PT_INTERP terminator")

    def test_empty_search_path_preserves_cwd_semantics(self):
        raw, _ = fixture([(29, 0)])
        path = parse(raw)["search_paths"][0]
        self.assertEqual(path["components"], [""])
        self.assertTrue(path["empty_component_requires_cwd"])

    def test_nonzero_presence_flag_payload_rejected(self):
        raw, _ = fixture([(24, 1)])
        self.rejected(raw, "nonzero presence-only")

    def test_sectionless_static_and_relocatable_do_not_gain_completeness(self):
        raw, _ = fixture()
        struct.pack_into("<H", raw, 56, 1)
        result = parse(raw)
        self.assertEqual(result["edges"], [])
        self.assertFalse(result["full_C05"])
        raw = bytearray(64)
        raw[:16] = b"\x7fELF\x02\x01\x01" + b"\0" * 9
        struct.pack_into("<HHIQQQIHHHHHH", raw, 16, 1, 62, 1, 0, 0, 0, 0,
                         64, 0, 0, 0, 0, 0)
        result = parse(raw)
        self.assertEqual(result["elf_type"], "ET_REL")
        self.assertFalse(result["full_C05"])


if __name__ == "__main__":
    unittest.main()
