"""Committed Git-path regressions for the pinned-edit report.

Fixtures are bare Git trees, so control bytes in a tracked name do not require
an operating system to create or check out that name. Expected pins are literal
fixture declarations, independently of the reporter's object-reading protocol.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_pinned_edits.py"
SCOPE = ("Full lowercase SHA-256 hex digests in merge-base text files only; "
         "not a replay, and an empty report does not prove frozen evidence is unchanged.")


def digest(data):
    return sha256(data).hexdigest()


class CommittedPathReport(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="pinned-edit-paths-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.sequence = 0
        self.git_executable = shutil.which("git")
        if self.git_executable is None:
            self.fail("Git is required for committed-path report tests")
        # Admit Git explicitly in the child PATH. This is not an empty-PATH test.
        self.environment = {key: value for key, value in os.environ.items()
                            if not key.startswith("GIT_")}
        self.environment.update({
            "PATH": str(Path(self.git_executable).resolve().parent),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_AUTHOR_NAME": "Pinned report fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Pinned report fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2001-01-01T00:00:00+0000",
            "GIT_COMMITTER_DATE": "2001-01-01T00:00:00+0000",
        })

    def git(self, root, *arguments, data=None):
        result = subprocess.run([self.git_executable, "--no-replace-objects", *arguments],
                                cwd=root, env=self.environment, input=data,
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout

    def tree(self, root, files):
        entries = {}
        for path, data in files.items():
            self.assertIs(type(data), bytes)
            parts = path.split("/")
            self.assertTrue(all(parts))
            current = entries
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            oid = self.git(root, "hash-object", "-w", "--stdin", data=data).strip()
            # Query the immutable object by its ASCII OID, never by a path line.
            self.assertEqual(self.git(root, "cat-file", "blob", oid.decode()), data)
            current[parts[-1]] = oid

        def emit(node):
            rows = []
            for name, value in node.items():
                if isinstance(value, dict):
                    oid, mode, kind = emit(value), b"040000", b"tree"
                else:
                    oid, mode, kind = value, b"100644", b"blob"
                rows.append(mode + b" " + kind + b" " + oid + b"\t" +
                            name.encode("utf-8") + b"\0")
            return self.git(root, "mktree", "-z", data=b"".join(rows)).strip()

        return emit(entries).decode()

    def repository(self, before, after):
        self.sequence += 1
        root = self.directory / str(self.sequence)
        root.mkdir()
        self.git(root, "init", "--bare", "--quiet")
        base_tree, head_tree = self.tree(root, before), self.tree(root, after)
        base = self.git(root, "commit-tree", base_tree, "-m", "base").decode().strip()
        head = self.git(root, "commit-tree", head_tree, "-p", base, "-m", "head").decode().strip()
        self.git(root, "update-ref", "refs/heads/main", base)
        self.git(root, "update-ref", "refs/heads/branch", head)
        self.git(root, "symbolic-ref", "HEAD", "refs/heads/branch")
        return root, base, head

    def pin(self, target, pinner, old_bytes, change="modified", state="stale", frozen=True):
        return {"pinned": target, "change": change, "pinner": pinner,
                "sha256": digest(old_bytes), "state": state, "frozen": frozen}

    def expected(self, repository, changed, pins):
        _, base, head = repository
        return {
            "merge_base": base, "head": head, "changed_files": changed,
            "pinned_changed_files": len({row["pinned"] for row in pins}),
            "stale": sum(row["state"] == "stale" for row in pins),
            "frozen_stale": sum(row["state"] == "stale" and row["frozen"] for row in pins),
            "pins": pins, "scope": SCOPE,
        }

    def report(self, repository, expected, pollution=None):
        root, _, _ = repository
        environment = dict(self.environment)
        if pollution:
            environment.update(pollution)
        python = [sys.executable, "-I", "-B"]
        if sys.flags.optimize:
            python.append("-O")
        for strict in (False, True):
            with self.subTest(strict=strict):
                command = python + [str(SCRIPT), "--root", str(root), "--base", "main",
                                    "--head", "HEAD", "--json"]
                if strict:
                    command.append("--strict")
                result = subprocess.run(command, env=environment, capture_output=True, check=False)
                try:
                    actual = json.loads(result.stdout)
                except (ValueError, UnicodeDecodeError):
                    self.fail("report is not JSON: " + result.stderr.decode(errors="replace"))
                self.assertEqual(actual, expected)
                failing = expected["stale"] if strict else expected["frozen_stale"]
                self.assertEqual(result.returncode, int(bool(failing)),
                                 result.stderr.decode(errors="replace"))

    def simple_target(self, target, decoy=None):
        old, new = b"old retained payload\n", b"new retained payload\n"
        pinner = "notes/PINS.txt"
        before = {target: old, pinner: digest(old).encode() + b"\n"}
        if decoy is not None:
            before[decoy] = b"unrelated sibling bytes\n"
        repository = self.repository(before, {**before, target: new})
        self.report(repository, self.expected(repository, 1, [self.pin(target, pinner, old)]))
        return repository

    def test_lf_target_is_stale(self):
        repository = self.simple_target("research/pkg/line[1]*?\nbreak.json",
                                        decoy="research/pkg/line1decoyX\nbreak.json")
        # An existing tree entry whose object is unreadable is not an absent path.
        root, _, _ = repository
        oid = self.git(root, "hash-object", "--stdin", data=b"old retained payload\n").decode().strip()
        (root / "objects" / oid[:2] / oid[2:]).unlink()
        python = [sys.executable, "-I", "-B"] + (["-O"] if sys.flags.optimize else [])
        command = python + [str(SCRIPT), "--root", str(root), "--base", "main", "--head", "HEAD", "--json"]
        result = subprocess.run(command, env=self.environment, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(("git cat-file blob " + oid + " failed:").encode(), result.stderr)

    def test_crlf_target_is_stale(self):
        self.simple_target("research/pkg/line\r\nbreak.json")

    def test_lf_pinner_stale_removed_and_repinned(self):
        target, pinner = "research/pkg/data.json", "notes/line\npins.txt"
        old, new = b"old payload\n", b"new payload\n"
        before = {target: old, pinner: digest(old).encode() + b"\n"}
        for transition in ("stale", "pinner_removed", "repinned", "replaced_by_tree"):
            with self.subTest(transition=transition):
                state = "pinner_removed" if transition == "replaced_by_tree" else transition
                after = {**before, target: new}
                if state == "pinner_removed":
                    del after[pinner]
                    if transition == "replaced_by_tree":
                        after[pinner + "/child.txt"] = b"a tree is not a pinning text blob"
                elif state == "repinned":
                    after[pinner] = digest(new).encode() + b"\n"
                repository = self.repository(before, after)
                changed = 1 if state == "stale" else 2
                pins = [self.pin(target, pinner, old, state=state)]
                self.report(repository, self.expected(repository, changed, pins))

    def test_deleted_lf_target_keeps_its_stale_pin(self):
        target, pinner, old = "upstream/pkg/deleted\nsource.bin", "notes/PINS.txt", b"deleted source"
        before = {target: old, pinner: digest(old).encode()}
        repository = self.repository(before, {pinner: before[pinner]})
        pins = [self.pin(target, pinner, old, change="deleted")]
        self.report(repository, self.expected(repository, 1, pins))

    def test_lf_request_does_not_desynchronize_ordinary_targets(self):
        targets = ("research/pkg/a.txt", "research/pkg/m\nline.txt", "research/pkg/z.txt")
        pinner = "notes/PINS.txt"
        before = {target: ("old-" + str(index)).encode() for index, target in enumerate(targets)}
        before[pinner] = b"\n".join(digest(before[target]).encode() for target in targets)
        after = {**before, **{target: ("new-" + str(index)).encode()
                             for index, target in enumerate(targets)}}
        repository = self.repository(before, after)
        pins = [self.pin(target, pinner, before[target]) for target in targets]
        self.report(repository, self.expected(repository, 3, pins))

    def test_tree_response_does_not_hide_later_stale_pinner(self):
        target, old = "research/target", b"old payload"
        pin = digest(old).encode()
        before = {target: old, "a-pin": pin, "z-pin": pin}
        after = {target: b"new payload", "a-pin/child": b"tree entry", "z-pin": pin}
        repository = self.repository(before, after)
        pins = [self.pin(target, "z-pin", old),
                self.pin(target, "a-pin", old, state="pinner_removed")]
        self.report(repository, self.expected(repository, 2, pins))

    def test_unicode_and_carriage_return_names(self):
        target, pinner, old = "research/測試/δ\rdata.json", "notes/測試:δ\npins.txt", b"unicode case"
        before = {target: old, pinner: digest(old).encode()}
        repository = self.repository(before, {**before, target: b"changed unicode case"})
        self.report(repository, self.expected(repository, 1, [self.pin(target, pinner, old)]))

    def test_binary_target_is_pinned_but_binary_pinner_is_excluded(self):
        target, text, binary = "research/pkg/binary\ninput.bin", "notes/PINS.txt", "notes/PINS.bin"
        old = b"\0old binary\xff\0"
        pin = digest(old).encode()
        before = {target: old, text: pin, binary: b"\0" + pin + b"\0"}
        repository = self.repository(before, {**before, target: b"\0new binary\xfe\0"})
        self.report(repository, self.expected(repository, 1, [self.pin(target, text, old)]))

    def test_living_lf_target_is_advisory_unless_strict(self):
        target, pinner, old = "docs/living\nrecord.json", "notes/PINS.txt", b"old living record"
        before = {target: old, pinner: digest(old).encode()}
        repository = self.repository(before, {**before, target: b"new living record"})
        self.report(repository, self.expected(repository, 1, [self.pin(target, pinner, old, frozen=False)]))

    def test_unpinned_lf_edit_remains_clean(self):
        target = "research/pkg/unpinned\nnotes.txt"
        repository = self.repository({target: b"before"}, {target: b"after"})
        self.report(repository, self.expected(repository, 1, []))

    def test_ambient_git_redirect_and_config_cannot_select_another_repository(self):
        target, pinner, old = "research/pkg/source.txt", "notes/PINS.txt", b"requested root old"
        before = {target: old, pinner: digest(old).encode()}
        requested = self.repository(before, {**before, target: b"requested root new"})
        wrong = self.repository({"notes/unpinned.txt": b"old"}, {"notes/unpinned.txt": b"new"})
        expected = self.expected(requested, 1, [self.pin(target, pinner, old)])
        for pollution in ({"GIT_DIR": str(wrong[0])},
                          {"GIT_CONFIG_COUNT": "not-a-count"},
                          {"GIT_DIR": str(wrong[0]), "GIT_CONFIG_COUNT": "not-a-count"}):
            with self.subTest(pollution=tuple(sorted(pollution))):
                self.report(requested, expected, pollution=pollution)


if __name__ == "__main__":
    unittest.main()
