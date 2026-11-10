"""Fresh synthetic fixtures only; imports only the adjacent newly written module."""
import hashlib
import unittest
from c05_header_edges_v1 import (
    ConfiguredSearchPremise, EdgeError, SearchPosition, SourceOccurrence,
    extract_header_edges, plan_literal_candidates, validate_plain,
)


def source(data, origin=None, name="/fixture/source.c", occurrence="fixture"):
    return SourceOccurrence(occurrence, name, hashlib.sha256(data).hexdigest(),
                            len(data), "fresh synthetic fixture bytes", origin)


def scan(text, origin=None):
    data = text.encode("ascii")
    return extract_header_edges(data, source(data, origin))


class LiteralEdges(unittest.TestCase):
    def test_multitoken_argument_splits_paste_chain(self):
        out = scan('#define P(a) 0 ## a ## include\n#if P(0 || __has_)("hidden.h")\n#endif\n')
        self.assertFalse(out['supported_language_scan'])
        self.assertIn('potential_synthesized_file_operator',self.codes(out))

    def names(self, result):
        return [(x["kind"], x["filename"]) for x in result["edges"]]

    def codes(self, result):
        return {x["code"] for x in result["unsupported_frontier"]}

    def test_all_branches_includes(self):
        out = scan('#if 0\n#include <inactive.h>\n#else\n#include "active.h"\n#endif\n')
        self.assertEqual(self.names(out), [("include", "inactive.h"), ("include", "active.h")])
        self.assertTrue(out["supported_language_scan"])
        self.assertFalse(out["full_C05"])

    def test_comments_strings_chars_are_not_directives(self):
        out = scan('/* #include <bad1.h> */\n// #include <bad2.h>\nchar *s = "#include <bad3.h>";\nchar q = \'"\';\n#include /*x*/ <good.h>\n')
        self.assertEqual(self.names(out), [("include", "good.h")])
        self.assertTrue(out["supported_language_scan"])

    def test_spliced_line_comment(self):
        out = scan('// masked\\\n#include <bad.h>\n#include <good.h>\n')
        self.assertEqual(self.names(out), [("include", "good.h")])

    def test_phase1_before_phase2_and_comment(self):
        out = scan('??=inc??/\nlude <yes.h>\n// hidden??/\n#include <no.h>\n')
        self.assertEqual(self.names(out), [("include", "yes.h")])
        self.assertEqual(out["edges"][0]["physical_line"], 2)
        self.assertEqual(out["edges"][0]["directive_physical_line"], 1)

    def test_literal_probes_and_presence_tests(self):
        out = scan('#if defined(__has_include) && __has_include /*c*/ (<x.h>)\n#endif\n#ifdef __has_include\n#endif\n#if __has_include_next("y.h")\n#endif\n')
        self.assertEqual(self.names(out), [("__has_include", "x.h"), ("__has_include_next", "y.h")])
        self.assertTrue(out["supported_language_scan"])

    def test_computed_includes_and_probes_stop(self):
        out = scan('#define HEADER "x.h"\n#include HEADER\n#if __has_include(HEADER)\n#endif\n')
        self.assertEqual(self.names(out), [])
        self.assertEqual(self.codes(out), {"macro_computed_or_malformed_include", "macro_computed_or_nonliteral_has_include"})
        self.assertFalse(out["supported_language_scan"])

    def test_probe_macro_alias_and_paste_stop(self):
        out = scan('#define H __has_include\n#define C(a,b) a ## b\n#define D(a,b) a %:%: b\n')
        self.assertIn("macro_computed_or_nonliteral_has_include", self.codes(out))
        self.assertEqual(sum(x["code"] == "potential_synthesized_file_operator" for x in out["unsupported_frontier"]), 2)

    def test_fixed_prefix_paste_is_diagnostic(self):
        out = scan('#define __GLIBC_USE(F) __GLIBC_USE_ ## F\n#include <x.h>\n')
        self.assertTrue(out["supported_language_scan"])
        self.assertEqual(out["lexical_diagnostics"][0]["code"], "non_file_operator_token_paste")

    def test_paste_can_hide_has_include(self):
        out = scan('#define CAT(a,b) a##b\n#if CAT(__has_,include)("hidden.h")\n#endif\n')
        self.assertFalse(out["supported_language_scan"])
        self.assertIn("potential_synthesized_file_operator", self.codes(out))

    def test_failed_later_paste_does_not_hide_operator(self):
        out = scan('#define X(a,b) a ## b ## +\n')
        self.assertIn("potential_synthesized_file_operator", self.codes(out))

    def test_va_opt_is_explicit_frontier(self):
        out = scan('#define X(...) __VA_OPT__(__has_) ## include\n')
        self.assertIn("unsupported_macro_va_opt", self.codes(out))

    def test_paste_fixed_suffix_blocks_target(self):
        self.assertTrue(scan('#define F(a,b) a ## _suffix ## b\n')["supported_language_scan"])

    def test_safe_pragmas_and_dollar_are_diagnostics(self):
        out = scan('#pragma once\n#pragma GCC system_header\nint name$;\n')
        self.assertTrue(out["supported_language_scan"])
        self.assertEqual(len(out["lexical_diagnostics"]), 3)

    def test_digraph_directive(self):
        self.assertEqual(self.names(scan('%:include <yes.h>\n')), [("include", "yes.h")])

    def test_multiline_comment_inside_directive(self):
        out = scan('# /*x\ny*/ include /*a\nb*/ <yes.h>\n')
        self.assertEqual(self.names(out), [("include", "yes.h")])
        self.assertTrue(out["supported_language_scan"])
        self.assertEqual(out["edges"][0]["physical_line"], 3)

    def test_header_comment_text_is_not_removed(self):
        out = scan('#include <a/*b*/c.h>\n')
        self.assertEqual(out["edges"], [])
        self.assertIn("unsupported_header_spelling", self.codes(out))

    def test_extensions_pragmas_and_asm_stop(self):
        out = scan('#include \\ \t\n <x.h>\n#pragma GCC dependency "other.h"\n_Pragma("once")\n__asm__(".incbin file");\n')
        self.assertEqual(self.names(out), [("include", "x.h")])
        self.assertTrue({"gcc_whitespace_splice_extension", "unsupported_pragma", "unsupported_Pragma", "unsupported_assembler_construct"} <= self.codes(out))

    def test_crlf_and_bare_cr(self):
        out = scan('#include <a.h>\r\n#include <b.h>\r')
        self.assertEqual(self.names(out), [("include", "a.h"), ("include", "b.h")])
        self.assertTrue(out["supported_language_scan"])

    def test_quote_filename_backslash_not_unescaped(self):
        self.assertIn("unsupported_header_spelling", self.codes(scan('#include "a\\b.h"\n')))

    def test_unterminated_frontiers(self):
        for text, code in [('"\n', "unterminated_string_or_char"), ('"x\\"\n', "unterminated_string_or_char"), ('/*x\n', "unterminated_block_comment"), ('#if 1\n', "unterminated_conditional"), ('#endif\n', "malformed_conditional_nesting"), ('#include <x\n', "unterminated_header")]:
            with self.subTest(text=text):
                self.assertIn(code, self.codes(scan(text)))

    def test_equal_byte_occurrences_remain_distinct(self):
        data = b'#include <x.h>\n'
        a = extract_header_edges(data, source(data, occurrence="first"))
        b = extract_header_edges(data, source(data, occurrence="second"))
        self.assertNotEqual(a["source"]["occurrence_id"], b["source"]["occurrence_id"])
        self.assertEqual(a["source"]["sha256"], b["source"]["sha256"])

    def test_authentication_rejects(self):
        data = b'#include <x.h>\n'
        with self.assertRaises(EdgeError):
            extract_header_edges(data + b' ', source(data))
        with self.assertRaises(EdgeError):
            extract_header_edges(data, SourceOccurrence("x", "/x", "0" * 64, len(data), "fixture"))

    def test_row_cap_is_explicit(self):
        out = scan('#include <x.h>\n' * 600)
        self.assertLessEqual(len(out["edges"]) + len(out["unsupported_frontier"]), 512)
        self.assertIn("representation_row_cap", self.codes(out))
        self.assertFalse(out["supported_language_scan"])

    def test_plain_caps(self):
        for item in ([0] * 1025, "x" * 8193, {1: "x"}):
            with self.subTest(kind=type(item).__name__), self.assertRaises(EdgeError):
                validate_plain(item)


class SearchOrder(unittest.TestCase):
    rules = ConfiguredSearchPremise(
        (SearchPosition("q", "/q", "a"), SearchPosition("a", "/a", "b"),
         SearchPosition("b", "/b", None)), "q", "a", "q", False,
        "unverified fresh synthetic configuration")

    def edge(self, kind="include_next", delimiter="angle"):
        return {"kind": kind, "filename": "x.h", "delimiter": delimiter}

    def plan(self, origin, kind="include_next", delimiter="angle"):
        data = b'fixture\n'
        return plan_literal_candidates(self.edge(kind, delimiter), source(data, origin), self.rules)

    def paths(self, result):
        return [x["pathname"] for x in result["candidates"]]

    def test_next_uses_origin_position(self):
        self.assertEqual(self.paths(self.plan("q")), ["/a/x.h", "/b/x.h"])
        self.assertEqual(self.paths(self.plan("a")), ["/b/x.h"])
        self.assertEqual(self.paths(self.plan("b")), [])

    def test_primary_include_next_uses_normal_start(self):
        data = b"fixture\n"
        occurrence = SourceOccurrence("primary", "/fixture/main.c", hashlib.sha256(data).hexdigest(), len(data), "fixture", "a", True)
        out = plan_literal_candidates(self.edge(), occurrence, self.rules)
        self.assertEqual(self.paths(out), ["/a/x.h", "/b/x.h"])

    def test_next_quote_does_not_restart_at_source_directory(self):
        self.assertEqual(self.paths(self.plan("a", delimiter="quote")), ["/b/x.h"])

    def test_absolute_origin_falls_back_to_normal(self):
        self.assertEqual(self.paths(self.plan(None)), ["/a/x.h", "/b/x.h"])
        self.assertEqual(self.paths(self.plan(None, delimiter="quote")), ["/fixture/x.h", "/q/x.h", "/a/x.h", "/b/x.h"])

    def test_duplicate_directory_strings_do_not_erase_origins(self):
        rules = ConfiguredSearchPremise((SearchPosition("one", "/same", "two"), SearchPosition("two", "/same", None)), "one", "one", "one", False, "fixture; intentionally unverified chain")
        out = plan_literal_candidates(self.edge(), source(b'x', "one"), rules)
        self.assertEqual(out["candidates"][0]["position"], "two")
        self.assertFalse(out["configured_rules_verified"])

    def test_missing_origin_rejected(self):
        with self.assertRaises(EdgeError):
            self.plan("missing")

    def test_pch_obligation_is_not_absence(self):
        out = self.plan("a")
        self.assertEqual(out["candidates"][0]["pch_pathname_obligation"], "/b/x.h.gch")
        self.assertFalse(out["pch_behaviour_resolved"])
        self.assertFalse(out["namespace_observed"])
        self.assertFalse(out["full_C05"])

    def test_absolute_spelling_preserved(self):
        edge = {"kind": "include", "filename": "/exact/../x.h", "delimiter": "quote"}
        out = plan_literal_candidates(edge, source(b'x'), self.rules)
        self.assertEqual(self.paths(out), ["/exact/../x.h"])

    def test_cycles_rejected(self):
        rules = ConfiguredSearchPremise((SearchPosition("x", "/x", "x"),), "x", "x", "x", False, "fixture")
        with self.assertRaises(EdgeError):
            plan_literal_candidates(self.edge("include"), source(b'x'), rules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
