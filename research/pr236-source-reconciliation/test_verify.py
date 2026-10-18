"""Archive and source-binding rejection controls; no compiler or network calls."""
import copy
import io
from pathlib import Path
import tarfile
from types import ModuleType
import unittest

HERE = Path(__file__).resolve().parent
c = ModuleType("reconcile236_under_test")
c.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), c.__file__, "exec"), c.__dict__)


def archive(rows):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as tar:
        for name, kind, raw in rows:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.size = len(raw)
            if kind == tarfile.SYMTYPE:
                member.linkname = "outside"
            tar.addfile(member, io.BytesIO(raw))
    return output.getvalue()


class ArchiveBoundaries(unittest.TestCase):
    def test_valid_regular_file(self):
        self.assertEqual(c.read_archive(archive([("src/Example.lean", tarfile.REGTYPE, b"example")])),
                         {"src/Example.lean": b"example"})

    def test_unsafe_names(self):
        for name in ("../outside", "/absolute", "src/../outside", "src//x", "src\\x", "."):
            with self.subTest(name=name), self.assertRaises(c.ReconciliationError):
                c.read_archive(archive([(name, tarfile.REGTYPE, b"x")]))

    def test_duplicate_member(self):
        with self.assertRaisesRegex(c.ReconciliationError, "duplicate archive"):
            c.read_archive(archive([("same", tarfile.REGTYPE, b"x"), ("same", tarfile.REGTYPE, b"y")]))

    def test_nonregular_members(self):
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE):
            with self.subTest(kind=kind), self.assertRaises(c.ReconciliationError):
                c.read_archive(archive([("member", kind, b"")]))

    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(c.ReconciliationError, "Duplicate JSON key"):
            c.decode(b'{"module":"one","module":"two"}')

    def test_boolean_is_not_integer(self):
        for left, right in ((False, 0), (True, 1), ({"exit": False}, {"exit": 0})):
            with self.subTest(left=left), self.assertRaises(c.ReconciliationError):
                c.same(left, right, "typed comparison")


class SourceBindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins = c.decode((HERE / "SOURCE-PINS.json").read_bytes())
        cls.files = c.pinned_files(cls.pins)
        cls.parser = c.load_parser(cls.files)
        cls.plan = c.decode(cls.files[c.PACKAGE + "/INPUT_MAP.json"])
        cls.sources = c.read_archive(cls.files[c.PACKAGE + "/scientific_sources.tar.gz"])

    def check(self, *, plan=None, sources=None, files=None):
        return c.check_sources(plan if plan is not None else self.plan,
                               sources if sources is not None else self.sources,
                               self.pins, files if files is not None else self.files, self.parser)

    def test_missing_or_extra_source(self):
        for extra in (False, True):
            data = dict(self.sources)
            if extra:
                data["src/Unaccepted.lean"] = b""
            else:
                data.pop(self.plan["modules"][0]["source"])
            with self.subTest(extra=extra), self.assertRaisesRegex(c.ReconciliationError, "coverage differs"):
                self.check(sources=data)

    def test_changed_lean_or_scientific_input(self):
        for name in (self.plan["modules"][0]["source"], self.plan["scientific_inputs"][0]["path"]):
            data = dict(self.sources)
            data[name] += b"\n"
            with self.subTest(name=name), self.assertRaisesRegex(c.ReconciliationError, "archive bytes differ"):
                self.check(sources=data)

    def test_rehashed_import_mismatch(self):
        # A repaired source digest must not hide disagreement with the declared imports.
        plan = copy.deepcopy(self.plan)
        module = plan["modules"][0]
        data = dict(self.sources)
        data[module["source"]] = b"import Init\n" + data[module["source"]]
        module["source_sha256"] = c.digest(data[module["source"]])
        with self.assertRaisesRegex(c.ReconciliationError, "Source imports differ"):
            self.check(plan=plan, sources=data)

    def test_rehashed_audit_mismatch(self):
        plan = copy.deepcopy(self.plan)
        module = plan["modules"][0]
        data = dict(self.sources)
        data[module["source"]] += b"\n#print axioms Unaccepted.theorem\n"
        module["source_sha256"] = c.digest(data[module["source"]])
        with self.assertRaisesRegex(c.ReconciliationError, "Source audit commands differ"):
            self.check(plan=plan, sources=data)

    def test_changed_theorem_mirror(self):
        files = dict(self.files)
        files[c.PACKAGE + "/key_theorems/FullActualIdentity.lean"] += b"\n"
        with self.assertRaisesRegex(c.ReconciliationError, "Theorem mirror differs"):
            self.check(files=files)

    def test_parser_import_creates_no_bytecode(self):
        before = sorted(p.relative_to(c.ROOT).as_posix() for p in (c.ROOT / c.PACKAGE).rglob("*"))
        c.load_parser(self.files)
        after = sorted(p.relative_to(c.ROOT).as_posix() for p in (c.ROOT / c.PACKAGE).rglob("*"))
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
