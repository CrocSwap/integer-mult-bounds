"""New pure finite controls only; no compiler/diagnostics/original imports."""
import io
import json
import tarfile
import unittest
from pathlib import Path
import configured_data_v1 as data
import generated_config_v1 as generated


def control(checksum="a"*64,size=3,filename="plugin.deb"):
    return ("Format: 1.0\nSource: gcc-13\nVersion: exact\nArchitecture: amd64\n"
            "Checksums-Sha256:\n "+checksum+" "+str(size)+" "+filename+"\n").encode()


def ar_part(name,payload):
    # Independent fixture writer: no ar/dpkg/package process is invoked.
    header=(name+"/").ljust(16)+"0".ljust(12)+"0".ljust(6)+"0".ljust(6)+"100644".ljust(8)+str(len(payload)).ljust(10)+"`\n"
    return header.encode()+payload+(b"\n" if len(payload)%2 else b"")


def ar_fixture(parts=None):
    parts=parts or [("debian-binary",b"2.0\n"),("control.tar",b"control"),("data.tar",b"data")]
    return b"!<arch>\n"+b"".join(ar_part(name,payload) for name,payload in parts)


def tar_fixture(rows):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode="w",format=tarfile.USTAR_FORMAT) as archive:
        for name,kind,body in rows:
            info=tarfile.TarInfo(name);info.mode=0o644
            if kind=="file":
                info.size=len(body);archive.addfile(info,io.BytesIO(body))
            elif kind=="symlink":
                info.type=tarfile.SYMTYPE;info.linkname=body;archive.addfile(info)
            else:raise AssertionError("fixture kind")
    return stream.getvalue()


class AssociationControls(unittest.TestCase):
    def test_same_build_rows_agree(self):
        record=data.same_build_package(control(),control(),"plugin.deb","gcc-13","exact")
        self.assertEqual((record["bytes"],record["sha256"]),(3,"a"*64))
        self.assertFalse(record["signature_verified"])

    def test_same_version_different_package_row_refused(self):
        with self.assertRaisesRegex(data.DataRefusal,"disagrees"):
            data.same_build_package(control(),control("b"*64),"plugin.deb","gcc-13","exact")

    def test_duplicate_fields_case_insensitive_refused(self):
        with self.assertRaisesRegex(data.DataRefusal,"duplicate control field"):
            data.debian_control(control()+b"sOuRcE: duplicate\n")

    def test_duplicate_checksum_filenames_refused(self):
        raw=control()+b" "+b"b"*64+b" 3 plugin.deb\n"
        with self.assertRaisesRegex(data.DataRefusal,"duplicate checksum filename"):
            data.sha256_rows(data.debian_control(raw))

    def test_missing_exact_filename_refused(self):
        with self.assertRaisesRegex(data.DataRefusal,"filename absent"):
            data.same_build_package(control(),control(),"another.deb","gcc-13","exact")

    def test_control_paragraph_and_unsafe_row_refused(self):
        for raw in (control()+b"\nSource: second\n", b" continuation\n",b"-----BEGIN PGP SIGNED MESSAGE-----\n"):
            with self.subTest(raw=raw[:20]):
                with self.assertRaises(data.DataRefusal):data.debian_control(raw)
        with self.assertRaises(data.DataRefusal):data.sha256_rows(data.debian_control(control(filename="../bad")))


class ArchiveControls(unittest.TestCase):
    def test_ar_layout_metadata_and_payloads_preserved(self):
        rows=data.strict_ar(ar_fixture())
        self.assertEqual([row["name"] for row in rows],["debian-binary","control.tar","data.tar"])
        self.assertEqual(rows[-1]["data"],b"data")
        self.assertEqual(rows[-1]["mode"],0o100644)

    def test_duplicate_ar_and_truncation_refused(self):
        original=[("debian-binary",b"2.0\n"),("control.tar",b"control"),("data.tar",b"data")]
        with self.assertRaisesRegex(data.DataRefusal,"duplicate ar member"):
            data.strict_ar(ar_fixture(original+[("data.tar",b"same")]))
        with self.assertRaises(data.DataRefusal):data.strict_ar(ar_fixture()[:-1])
        changed=bytearray(ar_fixture());changed[8+40]=ord("9")
        with self.assertRaisesRegex(data.DataRefusal,"numeric metadata"):
            data.strict_ar(bytes(changed))

    def test_normalized_duplicate_tar_path_refused(self):
        archive=tar_fixture([("./one","file",b"x"),("one","file",b"y")])
        with self.assertRaisesRegex(data.DataRefusal,"duplicate tar member"):
            data.strict_tar(archive)

    def test_tar_symlink_kind_and_alias_retained(self):
        archive=tar_fixture([("ordinary","file",b"bytes"),("alias","symlink","../outside")])
        rows=data.strict_tar(archive)
        self.assertEqual(rows[0]["data"],b"bytes")
        self.assertEqual((rows[1]["kind"],rows[1]["linkname"]),("symlink","../outside"))
        self.assertNotIn("data",rows[1])

    def test_tar_traversal_and_hidden_tail_refused(self):
        with self.assertRaisesRegex(data.DataRefusal,"unsafe"):
            data.strict_tar(tar_fixture([("../bad","file",b"x")]))
        archive=tar_fixture([("good","file",b"x")])
        with self.assertRaisesRegex(data.DataRefusal,"termination/padding"):
            data.strict_tar(archive+b"hidden"+b"\0"*506)


class HeaderDataControls(unittest.TestCase):
    def test_comments_and_splicing_control_file_operations(self):
        source=(b'/* #include "fake.h" */\n'
                b'#define TEXT "/* literal */"\n'
                b'#inc\\\nlude "real.h" // trailing\n')
        operations=generated.header_operations(source,"fixture.h")
        self.assertEqual([row["include_name"] for row in operations if row["kind"]=="include"],["real.h"])
        self.assertEqual(operations[-1]["line"],3)
        self.assertEqual(operations[0]["body"],'"/* literal */"')

    def test_formfeed_is_not_a_fabricated_directive_line(self):
        operations=generated.header_operations(b'code\f#include "fake.h"\n#include "real.h"\n',"fixture.h")
        self.assertEqual([row["include_name"] for row in operations if row["kind"]=="include"],["real.h"])

    def test_tm_reordering_preserves_changed_macro_precedence(self):
        leaves={"a.h":b"#define VALUE 1\n","b.h":b"#undef VALUE\n#define VALUE 2\n"}
        def trace(source):
            result=[]
            for row in generated.header_operations(source,"tm.h"):
                if row["kind"]=="include":
                    result.extend((event["kind"],event.get("body"))
                                  for event in generated.header_operations(leaves[row["include_name"]],row["include_name"]))
            return result
        first=trace(b'#include "a.h"\n#include "b.h"\n')
        second=trace(b'#include "b.h"\n#include "a.h"\n')
        self.assertEqual(first,[("define","1"),("undef",None),("define","2")])
        self.assertEqual(second,[("undef",None),("define","2"),("define","1")])
        self.assertNotEqual(first[-1],second[-1])

    def test_branches_stay_explicit_and_malformed_is_refused(self):
        rows=generated.header_operations(b'#if FEATURE\n#define V 1\n#else\n#define V 2\n#endif\n',"fixture.h")
        definitions=[row for row in rows if row["kind"]=="define"]
        self.assertEqual([row["conditions"][-1]["branch"] for row in definitions],["initial","else"])
        for raw in (b"#else\n",b"#if X\n",b"/* unclosed",b'??=include "hidden.h"\n'):
            with self.subTest(raw=raw):
                with self.assertRaises(data.DataRefusal):generated.header_operations(raw,"fixture.h")

    def test_c_string_grammar_does_not_execute_or_guess(self):
        self.assertEqual(generated.c_string_sequence(r'"a\\b" "\x63\141\n"'),"a\\bca\n")
        for raw in ('function()',r'"\q"',r'"\777"','"unterminated'):
            with self.subTest(raw=raw):
                with self.assertRaises(data.DataRefusal):generated.c_string_sequence(raw)

    def test_header_vars_preserves_repeats_and_rejects_make(self):
        self.assertEqual(generated.header_vars(b"TM_H=a.h b.h a.h\n")["TM_H"],["a.h","b.h","a.h"])
        for raw in (b"A=one\nA=two\n",b"A=$(shell false)\n"):
            with self.assertRaises(data.DataRefusal):generated.header_vars(raw)


class ActualPublishedDataControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unit=Path(__file__).resolve().parents[1];cls.frozen=cls.unit.parent
        cls.headers=generated.load_headers(cls.unit/"source-artifacts/plugin-members")
        cls.changes=(cls.frozen/"source-artifacts/gcc-13_13.3.0-6ubuntu2~24.04.1_amd64.changes").read_bytes()
        cls.buildinfo=(cls.frozen/"source-artifacts/gcc-13_13.3.0-6ubuntu2~24.04.1_amd64.buildinfo").read_bytes()
        cls.embedded=(cls.frozen/"evidence/EMBEDDED-CONFIGURATION-v1.json").read_bytes()
        cls.view=generated.construct_generated_config_view(cls.headers,cls.changes,cls.buildinfo,cls.embedded)

    def test_generated_change_rejected_despite_identical_configure_text(self):
        headers=dict(self.headers)
        headers["distro-defaults.h"]=headers["distro-defaults.h"].replace(b"DIST_DEFAULT_FORTIFY_SOURCE 3",b"DIST_DEFAULT_FORTIFY_SOURCE 4")
        self.assertEqual(headers["configargs.h"],self.headers["configargs.h"])
        with self.assertRaisesRegex(data.DataRefusal,"header identity"):
            generated.construct_generated_config_view(headers,self.changes,self.buildinfo,self.embedded)

    def test_same_version_another_record_body_rejected(self):
        changed=self.buildinfo.replace(b"Build-Date:",b"Other-Date:",1)
        self.assertNotEqual(changed,self.buildinfo)
        self.assertEqual(data.debian_control(changed)["version"],data.debian_control(self.buildinfo)["version"])
        with self.assertRaisesRegex(data.DataRefusal,"pinned retained build"):
            generated.construct_generated_config_view(self.headers,self.changes,changed,self.embedded)

    def test_actual_archive_reparse_uses_strict_boundaries(self):
        package=(self.unit/"source-artifacts"/generated.PACKAGE).read_bytes()
        self.assertEqual(data.digest(package),generated.PACKAGE_SHA256)
        rows=data.strict_ar(package)
        self.assertEqual([row["name"] for row in rows],["debian-binary","control.tar.zst","data.tar.zst"])

    def test_configargs_corroborates_driver_and_retains_ordered_defaults(self):
        self.assertTrue(self.view["configure_text_matches_pinned_driver"])
        pairs=self.view["configuration_arguments"]["configure_default_options"]
        self.assertEqual([row["name"] for row in pairs],["abi","cpu","arch_32","arch_64","tune"])
        self.assertEqual(pairs[0]["value"],"m64")

    def test_published_tm_order_and_conditions(self):
        rows=self.view["ordered_tm_header_operations"]
        names=[row["include_name"] for row in rows]
        self.assertLess(names.index("config/i386/biarch64.h"),names.index("config/i386/i386.h"))
        self.assertLess(names.index("config/gnu-user.h"),names.index("config/i386/gnu-user64.h"))
        self.assertEqual(names[-1],"defaults.h")
        self.assertTrue(next(row for row in rows if row["include_name"]=="insn-flags.h")["conditions"])

    def test_actual_distro_defines_and_declarations_do_not_mint_initialisers(self):
        values={row["name"]:row["body"] for row in self.view["observed_distro_macro_operations"]}
        self.assertEqual(values["DIST_DEFAULT_FORTIFY_SOURCE"],"3")
        self.assertEqual(values["DIST_DEFAULT_SSP_STRONG"],"1")
        self.assertTrue(all(row["conditions"][0]["opening"]=="ACCEL_COMPILER"
                            for row in self.view["observed_distro_macro_operations"]))
        self.assertIn("option initialisation",[row["cell"] for row in self.view["residual_configuration_cells"]])

    def test_missing_driver_defines_are_empty_observations_not_guessed_values(self):
        for name in ("STANDARD_EXEC_PREFIX","STANDARD_LIBEXEC_PREFIX","GCC_INCLUDE_DIR"):
            self.assertEqual(self.view["observed_host_macro_cells"][name],[])
        self.assertTrue(any("DRIVER_DEFINES" in row["cell"] for row in self.view["residual_configuration_cells"]))

    def test_earlier_stage_cannot_satisfy_missing_final_stage_cell(self):
        # No API accepts a caller's stage1 command as final-stage proof. The
        # actual503 gap remains explicit even though package metadata exists.
        cells=self.view["residual_configuration_cells"]
        self.assertTrue(all(row["status"]=="UNAVAILABLE_BUILDLOG_HTTP503"
                            for row in cells if row["cell"].startswith("final-installed")))
        with self.assertRaisesRegex(data.DataRefusal,"effective GCC configuration remains unproved"):
            generated.require_effective_configuration(self.headers,self.changes,self.buildinfo,self.embedded)
        self.assertFalse(self.view["effective_configuration"])
        self.assertFalse(self.view["full_C05"])
        self.assertFalse(self.view["full_V03"])


if __name__=="__main__":unittest.main(verbosity=2)
