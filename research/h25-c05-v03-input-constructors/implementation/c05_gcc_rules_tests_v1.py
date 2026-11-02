"""Independent finite controls for newly authored passive GCC source helpers.

Run only this new file with python3 -B -S. No compiler, package scripts, original
Root/provider/module, diagnostics or target subprocess is launched.
"""

import itertools
import json
import unittest
from pathlib import Path

import c05_gcc_rules_v1 as rules


class MakeDataControls(unittest.TestCase):
    def test_small_exhaustive_branch_oracle(self):
        source = """debian_patches = base
hardening_patches =
ifeq ($(a),yes)
 debian_patches += alpha
 ifneq ($(b),yes)
  debian_patches += alpha-not-beta
 else ifeq ($(c),yes)
  debian_patches += alpha-beta-gamma
 else
  debian_patches += alpha-beta-not-gamma
 endif
else ifneq ($(c),yes)
 debian_patches += not-alpha-not-gamma
else
 debian_patches += not-alpha-gamma
endif
"""
        for a, b, c in itertools.product((False, True), repeat=3):
            with self.subTest(a=a, b=b, c=c):
                expected = ["base.diff"]
                if a:
                    expected.append("alpha.diff")
                    if not b: expected.append("alpha-not-beta.diff")
                    elif c: expected.append("alpha-beta-gamma.diff")
                    else: expected.append("alpha-beta-not-gamma.diff")
                elif not c: expected.append("not-alpha-not-gamma.diff")
                else: expected.append("not-alpha-gamma.diff")
                values = dict(zip(("a", "b", "c"), ("yes" if x else "no" for x in (a,b,c))))
                values["trunk_build"] = ""
                result = rules.select_patch_data(source, values)
                self.assertEqual(result["definitely_selected"], expected)
                self.assertEqual(result["conditional"], [])

    def test_unknown_is_not_false(self):
        source = """debian_patches = base
hardening_patches =
ifeq ($(missing),yes)
 debian_patches += possible-a
else
 debian_patches += possible-b
endif
"""
        result = rules.select_patch_data(source, {"trunk_build": ""})
        self.assertEqual(result["definitely_selected"], ["base.diff"])
        self.assertEqual([x["patch"] for x in result["conditional"]],
                         ["possible-a.diff", "possible-b.diff"])

    def test_unknown_reset_refused(self):
        source = """debian_patches = base
ifeq ($(missing),yes)
 debian_patches = replacement
endif
"""
        with self.assertRaisesRegex(rules.UnsupportedConfiguration, "unresolved patch-list reset"):
            rules.select_patch_data(source, {"trunk_build": ""})

    def test_make_shell_is_data_frontier(self):
        with self.assertRaisesRegex(rules.UnknownMakeValue, "unsupported make function: shell"):
            rules.expand_make_data("$(shell printf should-never-execute)", {})
        self.assertEqual(rules.expand_make_data("$(filter x86_64-%,x86_64-linux-gnu i686-linux-gnu)", {}),
                         "x86_64-linux-gnu")
        self.assertEqual(rules.expand_make_data("$(if $(findstring gcc-13,$(pkg)),native,$(unknown))",
                                               {"pkg": "gcc-13"}), "native")

    def test_unknown_language_context_stays_frontier(self):
        with self.assertRaises(rules.UnknownMakeValue):
            rules.expand_make_data("$(target)", {})


class ExactPatchControls(unittest.TestCase):
    def test_trailing_no_newline_marker_is_refused(self):
        patch = b'--- a/src/gcc/example.cc\n+++ b/src/gcc/example.cc\n@@ -1 +1 @@\n-old\n+new\n\\ No newline at end of file\n'
        with self.assertRaisesRegex(rules.UnsupportedConfiguration,'non-LF patch'):
            rules.project_patch(b'old\n',patch,'gcc/example.cc')

    PATCH = b"--- a/src/gcc/example.cc\n+++ b/src/gcc/example.cc\n@@ -2,3 +2,4 @@\n left\n-old\n+new\n+more\n right\n"

    def test_exact_projection_and_offset_oracle(self):
        base = b"heading\nleft\nold\nright\ntrailer\n"
        expected = b"heading\nleft\nnew\nmore\nright\ntrailer\n"
        for prefix in (b"", b"unrelated\n", b"one\ntwo\n"):
            with self.subTest(prefix=prefix):
                result, receipt = rules.project_patch(prefix + base, self.PATCH, "gcc/example.cc")
                self.assertEqual(result, prefix + expected)
                self.assertEqual(receipt[0]["actual_old_line"], 2 + prefix.count(b"\n"))

    def test_changed_context_is_not_repaired(self):
        with self.assertRaisesRegex(rules.UnsupportedConfiguration, "nonunique/missing exact patch context"):
            rules.project_patch(b"heading\nleft \nold\nright\n", self.PATCH, "gcc/example.cc")

    def test_ambiguous_relocation_rejected(self):
        base = b"heading\nelsewhere\nleft\nold\nright\nleft\nold\nright\n"
        with self.assertRaisesRegex(rules.UnsupportedConfiguration, "nonunique/missing exact patch context"):
            rules.project_patch(base, self.PATCH, "gcc/example.cc")

    def test_unrelated_target_not_transformed(self):
        base = b"unchanged\n"
        self.assertEqual(rules.project_patch(base, self.PATCH, "gcc/another.cc"), (base, []))

    def test_truncated_hunk_rejected(self):
        with self.assertRaisesRegex(rules.UnsupportedConfiguration, "hunk count"):
            rules.project_patch(b"heading\nleft\nold\nright\n", self.PATCH.rsplit(b" right",1)[0],
                                "gcc/example.cc")


class SourceAndConfigurationControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = rules.load_pinned_sources(Path(__file__).parent.parent / "source-artifacts")
        cls.command = [rules.COMPILER, *rules.FIXED_OPTIONS,
                       "/finite-fixture/stage/original-role.c", "-o", "/finite-fixture/stage/fresh.so"]
        cls.cwd = "/finite-fixture/stage"
        cls.model = rules.construct_fixed_rule_model(cls.corpus, cls.command,
                                                     rules.NATIVE_ENVIRONMENT, cls.cwd)

    def test_source_identity_mutation_rejected(self):
        mutated = dict(self.corpus)
        key = rules.BASE + "gcc/incpath.cc"
        mutated[key] = mutated[key].replace(b"remove_duplicates", b"remove_duplicateX", 1)
        with self.assertRaisesRegex(rules.UnsupportedConfiguration, "source content identity"):
            rules.verify_source_bytes(mutated)

    def test_injected_source_or_chain_rejected(self):
        injected = dict(self.corpus)
        injected["authoritative-effective-chain"] = b"complete=true"
        with self.assertRaisesRegex(rules.UnsupportedConfiguration, "exact pinned key set"):
            rules.verify_source_bytes(injected)

    def test_all_source_references_locate_real_physical_lines(self):
        for reference in self.model["source_evidence"].values():
            with self.subTest(path=reference["path"], line=reference["line"]):
                data = self.corpus[reference["path"]]
                self.assertEqual(rules.sha256(data), reference["sha256"])
                # GCC source contains form-feed page separators. Physical source
                # references count LF bytes, not Python's broader splitlines().
                self.assertIn(reference["anchor"], data.decode().split("\n")[reference["line"] - 1])
        generator = self.corpus[rules.PATCH_BASE + "rules.patch"].decode().split("\n")
        for record in self.model["conditional_distro_defines"]["definite_under_build_values"].values():
            self.assertIn(record["directive"], generator[record["line"] - 1])

    def test_automatic_specs_independent_source_control(self):
        text = self.corpus[rules.BASE + "gcc/gcc.cc"].decode()
        start = text.index("driver::set_up_specs () const")
        body = text[start:text.index("/* Process any configure-time defaults", start)]
        first = body.index('find_a_file (&startfile_prefixes, "specs", R_OK, true)')
        second = body.index("if (access (specs_file, R_OK) == 0)")
        self.assertLess(first, second)
        self.assertGreaterEqual(body.count("read_specs (specs_file, true, false)"), 2)
        self.assertNotIn("-specs", self.command)
        self.assertEqual(len(self.model["automatic_specs_rules"]), 2)
        self.assertFalse(self.model["automatic_specs_rules"][0]["ordered_candidates_proven"])

    def test_pch_before_header_source_countermodel(self):
        text = self.corpus[rules.BASE + "libcpp/files.cc"].decode()
        start = text.index("find_file_in_dir (cpp_reader *pfile, _cpp_file *file, bool *invalid_pch,\n")
        body = text[start:text.index("/*", text.index("if (open_file (file))", start))]
        self.assertLess(body.index("if (pch_open_file"), body.index("if (open_file"))
        # Two namespaces with identical ordinary header bytes can differ by a
        # usable .gch. The source tries that witness first in the eligible state.
        ordinary = {"/usr/include/python3.12/Python.h": b"ordinary header"}
        changed = dict(ordinary, **{"/usr/include/python3.12/Python.h.gch": b"candidate PCH"})
        self.assertEqual(ordinary["/usr/include/python3.12/Python.h"],
                         changed["/usr/include/python3.12/Python.h"])
        self.assertNotEqual(set(ordinary), set(changed))
        self.assertTrue(self.model["pch_rule"]["before_normal_header"])
        self.assertFalse(self.model["pch_rule"]["observed"])

    def test_patched_source_independent_postimage_controls(self):
        for target, needles in {
            "gcc/gcc.cc": [b'prefix_info.name = (const char *) prefixed_name;', b'#include "distro-defaults.h"'],
            "gcc/incpath.cc": [b"char *rp = lrealpath (str);"],
            "gcc/config/i386/t-linux64": [b"m64=../lib$(call if_multiarch,:x86_64-linux-gnu)"],
        }.items():
            data = self.corpus[rules.BASE + target]
            record = next(x for x in self.model["definite_patch_projection"] if x["target"] == target)
            for patch in record["patches"]:
                data, receipt = rules.project_patch(data,
                    self.corpus[rules.PATCH_BASE + "patches/" + patch["patch"]], target)
                self.assertTrue(all(h["exact_context"] for h in receipt))
            self.assertEqual(rules.sha256(data), record["definite_patch_projection_sha256"])
            for needle in needles: self.assertIn(needle, data)

    def test_glibc_automatic_preinclude_source(self):
        source = self.corpus[rules.BASE + "gcc/config/glibc-c.cc"].decode()
        self.assertIn('#define TARGET_C_PREINCLUDE glibc_c_preinclude', source)
        self.assertIn('return "stdc-predef.h";', source)
        self.assertEqual(self.model["automatic_preinclude"]["name"], "stdc-predef.h")
        self.assertFalse(self.model["automatic_preinclude"]["effective"])

    def test_ubuntu_generator_branch_controls(self):
        text = self.corpus[rules.PATCH_BASE + "rules.patch"].decode()
        values = rules._fixed_build_values(self.corpus)
        noble = rules.derive_distro_defines(text, values)
        jammy = rules.derive_distro_defines(text, dict(values, distrelease="jammy"))
        first = noble["definite_under_build_values"]["DIST_DEFAULT_FORTIFY_SOURCE"]["directive"]
        second = jammy["definite_under_build_values"]["DIST_DEFAULT_FORTIFY_SOURCE"]["directive"]
        self.assertEqual(first.rsplit(" ", 1)[1], "3")
        self.assertEqual(second.rsplit(" ", 1)[1], "2")
        self.assertTrue(any("DIST_DEFAULT_SSP " in x["directive"] for x in noble["conditional"]))

    def test_command_environment_and_stage_mutations_rejected(self):
        for index, value in [(0, "/usr/bin/gcc"), (4, "-O2"), (5, "-std=gnu11"),
                             (9, "-I/tmp"), (10, "/outside.c"), (11, "--output")]:
            changed = list(self.command); changed[index] = value
            with self.subTest(index=index):
                with self.assertRaises(rules.UnsupportedConfiguration):
                    rules._validate_command(changed, rules.NATIVE_ENVIRONMENT, self.cwd)
        for environment in [dict(rules.NATIVE_ENVIRONMENT, CPATH="/tmp"),
                            dict(rules.NATIVE_ENVIRONMENT, PATH="/usr/local/bin:/usr/bin:/bin")]:
            with self.assertRaises(rules.UnsupportedConfiguration):
                rules._validate_command(self.command, environment, self.cwd)
        with self.assertRaises(rules.UnsupportedConfiguration):
            rules._validate_command(self.command, rules.NATIVE_ENVIRONMENT, "/finite-fixture/../stage")

    def test_native_bytes_environment_supported(self):
        environment = {key.encode(): value.encode() for key,value in rules.NATIVE_ENVIRONMENT.items()}
        rules._validate_command(self.command, environment, self.cwd)

    def test_effective_constructor_refuses_even_positive_model(self):
        claimed = dict(self.model, full_C05=True, execution_ready=True,
                       effective_include_chain_proven=True, frontier=[])
        self.assertTrue(claimed["full_C05"])
        with self.assertRaises(rules.IncompleteConfiguration) as caught:
            rules.construct_effective_configuration(self.corpus, self.command,
                                                   rules.NATIVE_ENVIRONMENT, self.cwd)
        self.assertFalse(caught.exception.model["full_C05"])
        self.assertTrue(caught.exception.model["frontier"])

    def test_no_original_credit_or_caps_changed(self):
        self.assertFalse(self.model["full_C05"])
        self.assertFalse(self.model["full_V03"])
        self.assertFalse(self.model["original_target_executed"])
        self.assertEqual(self.model["new_scientific_activity_credit"], 0)
        self.assertEqual(self.model["original_caps"]["rows"], 512)
        self.assertEqual(self.model["original_caps"]["file_bytes"], 67108864)
        self.assertEqual(self.model["original_caps"]["capture_bytes"], 268435456)
        self.assertEqual(self.model["physical_costs"], "OPEN_NOT_ZERO")


if __name__ == "__main__":
    unittest.main(verbosity=2)
