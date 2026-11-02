#!/usr/bin/env python3
"""Independent native-Git path oracle for the source6428 search-seam contract.

Git, not a Python binary/text heuristic, classifies EVERY candidate alias.
No predecessor or peer executable is imported. Other scanner policy is retained
with credit to apoursh/6357/6428; this is not a historical154-row replay.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MANIFEST_SHA = "e4d812801ed232f58117f51343b7409b67059bd10c500acfef2a2da8f697f2b9"
PINS = {
    "predecessor.py": ("c9c0290c02a49f59cbad6b382eaae99ee2e96627b0a5d62346e4c069c3d936d5", "218dc2dff2c41653849ffa7ea7cfa93236684d09"),
    "reuse.py": ("db7eb6631216c1871f75a0818415293fb4f4f5bb5bb8a35da110491769083635", "bef96e0ad6ec057429f361cd0041cd29709317f8"),
    "README-6428.md": ("24d9eecb5a4da2da11730b50a61b6e96c811a638a5f5776c7761aa7fe9f4489d", "a382b97bcf5b1d74f7c0882af85e62aa913de496"),
    "research_package.py": ("e1256016e7f51827d04fa2179255989f639ae1d97afaa9c16265f85a0c6abd70", "091b4c8f58bac9a9580d76025b887dc5c873d05f"),
}
CHUNK = 4096


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def decode(raw):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON member")
            result[key] = value
        return result
    def bad(value):
        raise ValueError("Nonfinite JSON value " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def authenticate():
    require(hashlib.sha256((ROOT / "SOURCE-PINS.json").read_bytes()).hexdigest() == MANIFEST_SHA,
            "Source manifest sha256 mismatch")
    for name, (sha, blob) in PINS.items():
        raw = (ROOT / "sources" / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "Source sha256 mismatch: " + name)
        require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "Source Git blob mismatch: " + name)


class GitFixture:
    def __init__(self, directory):
        require(os.name == "posix", "This LF/CR/colon filename fixture has a POSIX Git scope, not a Windows claim")
        executable = shutil.which("git")
        require(executable is not None, "Git executable is a declared runtime dependency")
        self.executable = executable
        self.directory = Path(directory)
        self.repo = self.directory / "repo"
        self.repo.mkdir()
        # Local temporary configuration only. Parent Git selection/config
        # injection cannot redirect these fixture subprocesses.
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                         "GIT_AUTHOR_NAME": "Pinned Digest Oracle", "GIT_AUTHOR_EMAIL": "oracle@example.invalid",
                         "GIT_COMMITTER_NAME": "Pinned Digest Oracle", "GIT_COMMITTER_EMAIL": "oracle@example.invalid",
                         "GIT_AUTHOR_DATE": "2001-01-01T00:00:00+0000", "GIT_COMMITTER_DATE": "2001-01-01T00:00:00+0000"})
        self.run("init", "-q")
        self.run("symbolic-ref", "HEAD", "refs/heads/main")
        empty = self.directory / "empty.attributes"
        empty.write_bytes(b"")
        hooks = self.directory / "empty-hooks"
        hooks.mkdir()
        for key, value in (("core.attributesFile", str(empty)), ("core.excludesFile", str(empty)), ("core.autocrlf", "false"),
                           ("core.hooksPath", str(hooks)), ("commit.gpgsign", "false"),
                           ("diff.fixturebinary.binary", "true")):
            self.run("config", "--local", key, value)
        (self.repo / ".git" / "info").mkdir(parents=True, exist_ok=True)
        (self.repo / ".git" / "info" / "attributes").write_bytes(b"")
        (self.repo / ".git" / "info" / "exclude").write_bytes(b"")

    def run(self, *args, check=True, data=None):
        result = subprocess.run([self.executable, "--no-replace-objects", *args], cwd=self.repo,
                                env=self.env, input=data, capture_output=True, timeout=20)
        if check:
            require(result.returncode == 0, "Native Git command failed: " + repr(args[:3]) + ": " + result.stderr.decode(errors="replace"))
        return result

    def write(self, name, content):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.chmod(0o644)

    def commit(self, message):
        self.run("add", "--all")
        self.run("commit", "-q", "-m", message)
        return self.run("rev-parse", "HEAD^{commit}").stdout.decode("ascii").strip()

    def tree(self, revision):
        raw = self.run("ls-tree", "-r", "-z", "--full-tree", revision).stdout
        result = {}
        for record in raw.split(b"\0"):
            if not record:
                continue
            metadata, path = record.split(b"\t", 1)
            mode, kind, oid = metadata.split()
            require(len(oid) in (40, 64) and all(c in b"0123456789abcdef" for c in oid), "Git object identifier framing")
            result[path.decode("utf-8")] = (mode.decode("ascii"), kind.decode("ascii"), oid.decode("ascii"))
        return result

    def blob(self, oid):
        return self.run("cat-file", "blob", oid).stdout

    def literal_bytes(self, revision, name):
        raw = self.run("--literal-pathspecs", "ls-tree", "-z", "--full-tree", revision, "--", name).stdout
        if not raw:
            return None
        entries = raw.split(b"\0")
        require(len(entries) == 2 and entries[-1] == b"", "Literal tree single-entry framing")
        metadata, path = entries[0].split(b"\t", 1)
        require(path == name.encode("utf-8"), "Literal tree exact UTF8 path")
        _mode, kind, oid = metadata.split()
        return self.blob(oid.decode("ascii")) if kind == b"blob" else None

    def grep_path(self, revision, name, digests):
        patterns = [arg for digest in sorted(digests) for arg in ("-e", digest)]
        result = self.run("--literal-pathspecs", "grep", "-I", "-l", "-z", "-F",
                          *patterns, revision, "--", name, check=False)
        require(result.returncode in (0, 1), "Native per-path Git grep error: " + result.stderr.decode(errors="replace"))
        prefix = revision.encode("ascii") + b":"
        names = []
        for record in result.stdout.split(b"\0"):
            if record:
                require(record.startswith(prefix), "Native grep revision prefix framing")
                names.append(record[len(prefix):].decode("utf-8"))
        require(names in ([], [name]) and (result.returncode == 0) == bool(names), "Native grep exact literal alias output")
        return bool(names)


def raw_matches(payload, patterns, carry=True):
    found, tail = set(), b""
    encoded = [(digest, digest.encode("ascii")) for digest in patterns]
    for offset in range(0, len(payload), CHUNK):
        block = (tail if carry else b"") + payload[offset:offset+CHUNK]
        found.update(digest for digest, needle in encoded if needle in block)
        tail = block[-63:]
    return found


def changed_targets(git, base, head):
    fields = git.run("diff", "--name-status", "-z", "--no-renames", base, head).stdout.split(b"\0")
    require(fields[-1] == b"", "NUL-terminated changed path stream")
    fields.pop()
    require(len(fields) % 2 == 0, "Changed path status/name pairs")
    changed, targets = {}, defaultdict(list)
    for i in range(0, len(fields), 2):
        status, name = fields[i].decode("ascii"), fields[i+1].decode("utf-8")
        if status[:1] not in "MDT":
            continue
        changed[name] = "deleted" if status[:1] == "D" else "modified"
        before = git.literal_bytes(base, name)
        if before is not None:
            targets[hashlib.sha256(before).hexdigest()].append(name)
    return changed, dict(targets)


def report(git, base, head, changed, targets, pinners):
    rows = []
    for pinner in sorted(pinners):
        before = git.literal_bytes(base, pinner)
        require(before is not None, "Every base pinner has stored blob bytes")
        # Same retained6428 read-reuse contract; classification policy is not
        # changed by the search prefilter.
        after = git.literal_bytes(head, pinner) if pinner in changed else before
        for digest, names in sorted(targets.items()):
            if digest.encode("ascii") not in before:
                continue
            state = "pinner_removed" if after is None else "stale" if digest.encode("ascii") in after else "repinned"
            for name in sorted(names):
                rows.append({"pinned": name, "change": changed[name], "pinner": pinner, "sha256": digest,
                             "state": state, "frozen": name.startswith(("research/", "upstream/"))})
    rows.sort(key=lambda row: (not row["frozen"], row["state"] != "stale", row["pinned"], row["pinner"]))
    return {"pins": rows, "changed_files": len(changed), "pinned_changed_files": len({r["pinned"] for r in rows}),
            "stale": sum(r["state"] == "stale" for r in rows),
            "frozen_stale": sum(r["state"] == "stale" and r["frozen"] for r in rows)}


def fixture(git):
    oldA, oldB = b"old shared target\n", b"\0old binary target\r\n"
    digestA, digestB = hashlib.sha256(oldA).hexdigest(), hashlib.sha256(oldB).hexdigest()
    a = digestA.encode("ascii"); b = digestB.encode("ascii")
    shared = b"aa"+a+b"bb\n"  # Deliberately inside a longer lowercase-hex token.
    nul = b"prefix\0"+a+b"\n"
    aliases = ["00-binary.opaque", "10-text.force", "20-driver.custom", "pinners/line\nbreak.pin",
               "pinners/carriage\rreturn.pin", "colon:pin.txt", "pinners/bracket[1]*?.pin",
               ":(exclude)hide.pin", ":(glob)magic?.pin", "pinners/µ-unicode.pin", "--dash.pin"]
    data = {name: shared for name in aliases}
    data.update({".gitattributes": b"*.opaque -diff\n*.force diff\n*.custom diff=fixturebinary\n",
                 "research/target-a.dat": oldA, "docs/target-b.dat": oldA, "research/target-c.bin": oldB,
                 "docs/unchanged-target": b"unchanged\n", "forced-nul.force": nul, "ordinary-nul.bin": nul,
                 "custom-nul.custom": nul, "both-1.txt": a+b"\n"+b+b"\n", "both-2.txt": a+b"\n"+b+b"\n",
                 "chunk-boundary.txt": b"p"*(65536-9)+a+b"tail\n", "uppercase-only.txt": a.upper()+b"\n",
                 "truncated-only.txt": a[:-1]+b"\n", "pinners/bracket1DECOYz.pin": b"unrelated\n",
                 "pinners/"+digestA+".name-only": b"no digest in these bytes\n"})
    for name, content in data.items():
        git.write(name, content)
    base = git.commit("deterministic merge-base fixture")
    git.write("research/target-a.dat", b"new target A\n")
    (git.repo / "docs/target-b.dat").unlink()
    git.write("research/target-c.bin", b"\0new binary target\n")
    git.write("10-text.force", b"repinned "+hashlib.sha256(b"new target A\n").hexdigest().encode()+b"\n")
    (git.repo / "pinners/line\nbreak.pin").unlink()
    git.write("both-1.txt", a+b"\nchanged but still pins A\n")
    git.write("added-pinner.txt", a+b"\n")
    head = git.commit("deterministic changed head fixture")
    return base, head, data, digestA, digestB, aliases


def run_fixture():
    with tempfile.TemporaryDirectory(prefix="pinned-digest-oracle-") as directory:
        git = GitFixture(directory)
        base, head, initial, digestA, digestB, aliases = fixture(git)
        require(git.run("merge-base", base, head).stdout.decode("ascii").strip() == base, "Actual merge-base relation")
        changed, targets = changed_targets(git, base, head)
        require(sorted(targets[digestA]) == ["docs/target-b.dat", "research/target-a.dat"], "Duplicate target digest multiplicity")
        tree = git.tree(base)
        blobs = {name: oid for name, (_mode, kind, oid) in tree.items() if kind == "blob"}
        # Independent reference: nativeGit inspects EVERY literal tracked path.
        native = {name for name in sorted(blobs) if git.grep_path(base, name, targets)}
        groups = defaultdict(list)
        for name, oid in sorted(blobs.items()):
            groups[oid].append(name)
        candidates, matches, raw_bytes = set(), {}, 0
        for oid, names in sorted(groups.items()):
            # One explicit raw-payload request per unique OID;
            # internal caching/decompression is unmeasured.
            content = git.blob(oid)
            require(all(initial[name] == content for name in names), "Stored raw Git blob equals every fixture alias's original bytes")
            raw_bytes += len(content)
            digests = raw_matches(content, targets)
            matches[oid] = digests
            if digests:
                candidates.update(names)
        # Crucial seam: every candidate ALIAS, not one representative perOID.
        selected = {name for name in sorted(candidates) if git.grep_path(base, name, targets)}
        require(selected == native, "Prefilter must preserve the native per-path Git result exactly")
        native_report = report(git, base, head, changed, targets, native)
        selected_report = report(git, base, head, changed, targets, selected)
        require(canonical(native_report) == canonical(selected_report), "Full per-target/pinner report preservation")
        require({r["sha256"] for r in native_report["pins"]} == {digestA, digestB}, "Only intended changed-target digests have pins")
        for name in aliases:
            require(blobs[name] == blobs["10-text.force"], "Same rawOID for aliases with different policy")
        require("10-text.force" in native and "00-binary.opaque" not in native and "20-driver.custom" not in native,
                "Actual Git per-path diff/-diff/custom-binary classification")
        require(blobs["forced-nul.force"] == blobs["ordinary-nul.bin"] == blobs["custom-nul.custom"]
                and "forced-nul.force" in native and "ordinary-nul.bin" not in native and "custom-nul.custom" not in native,
                "Actual Git forced-text NUL alias classification")
        special = ["pinners/line\nbreak.pin", "pinners/carriage\rreturn.pin", "colon:pin.txt", "pinners/bracket[1]*?.pin",
                   ":(exclude)hide.pin", ":(glob)magic?.pin", "pinners/µ-unicode.pin", "--dash.pin"]
        require(all(name in native for name in special), "Every UTF8/LF/CR/colon/glob/magic alias remains literal")
        require("uppercase-only.txt" not in native and "truncated-only.txt" not in native
                and "pinners/"+digestA+".name-only" not in native, "Exact lowercase64byte literal content domain")
        require(digestA in raw_matches(initial["chunk-boundary.txt"], targets)
                and digestA not in raw_matches(initial["chunk-boundary.txt"], targets, carry=False)
                and "chunk-boundary.txt" in native, "Cross-chunk digest needs overlap and native match agrees")
        require(initial["10-text.force"].startswith(b"aa"+digestA.encode()+b"bb") and "10-text.force" in native,
                "Digest literal substring inside longer lowercase-hex text")
        require("added-pinner.txt" not in blobs and "added-pinner.txt" not in native, "Added head-only pinner is outside merge-base search")
        false_positive, false_negative = set(), set()
        for oid, names in groups.items():
            if not matches[oid]:
                continue
            good = [name for name in names if name in native]
            rejected = [name for name in names if name not in native]
            positive_rep = good[0] if good else names[0]
            negative_rep = rejected[0] if rejected else names[0]
            if positive_rep in native:
                false_positive.update(set(names)-native)
            if negative_rep not in native:
                false_negative.update(set(names) & native)
        require(false_positive and false_negative, "Representative classification cache must exhibit both error directions")
        pins = native_report["pins"]
        require(all(r["state"] == "repinned" for r in pins if r["pinner"] == "10-text.force"), "Changed pinner repin state")
        require(all(r["state"] == "pinner_removed" for r in pins if r["pinner"] == "pinners/line\nbreak.pin"), "LF pinner removal state")
        require({r["state"] for r in pins if r["pinner"] == "both-1.txt"} == {"stale", "repinned"}, "One pinner has per-digest stale/repinned states")
        require(set(r["state"] for r in pins) == {"stale", "repinned", "pinner_removed"}, "All retained classification states covered")
        return {"fixture_scope": "Actual native Git in a disposable POSIX UTF8 repository with local fixed configuration; valid stable objects only",
                "tracked_blob_aliases": len(blobs), "unique_blob_OIDs": len(groups), "raw_blob_requests": len(groups),
                "raw_blob_payload_bytes": raw_bytes, "candidate_aliases": sorted(candidates), "native_matched_aliases": sorted(native),
                "candidate_native_Git_checks": len(candidates), "independent_all_path_Git_checks": len(blobs),
                "every_candidate_alias_delegated_to_Git": True,
                "sameOID_policy_classes": [{"raw_sha256": hashlib.sha256(initial[names[0]]).hexdigest(),
                    "aliases": [{"path": name, "native_Git_match": name in native} for name in sorted(names)]}
                    for _oid, names in sorted(groups.items(), key=lambda item: hashlib.sha256(initial[item[1][0]]).hexdigest())
                    if len(names) > 1 and any(name in native for name in names)],
                "representative_cache_negative_controls": {"text_representative_false_positive_paths": sorted(false_positive),
                    "binary_representative_false_negative_paths": sorted(false_negative)},
                "substring_and_chunk_controls": {"lowercase64bytes_inside_longer_hex_text": True, "chunk_bytes": CHUNK,
                    "digest_offset": 65536-9, "missing_overlap_loses_actual_match": True,
                    "uppercase_truncated_and_name_only_are_not_matches": True},
                "complete_normalized_report": native_report,
                "default_exit": int(native_report["frozen_stale"] > 0), "strict_exit": int(native_report["stale"] > 0),
                "report_sha256": hashlib.sha256((canonical(native_report)+"\n").encode()).hexdigest()}


def compute():
    authenticate()
    return {"schema_version": 1, "status": "PASS_INDEPENDENT_PATH_CLASSIFICATION_PREFILTER_ORACLE",
            "source_manifest_sha256": MANIFEST_SHA, "source_sha256": {name: pin[0] for name, pin in PINS.items()},
            "source_git_blobs": {name: pin[1] for name, pin in PINS.items()},
            "method": "Independent per-literal-path nativeGit oracle versus one-raw-read-perOID byte-substring prefilter, followed by nativeGit on EVERY surviving alias",
            "fixture": run_fixture(),
            "limits": ["Git is a declared runtime dependency; this is not a Git-free check.",
                       "All path text/binary/custom-driver policy is delegated to Git, never cached by blobID or replicated as a Python heuristic.",
                       "The fixture isolates only local temporary configuration and preserves the parent environment/configuration; no global driver changes occur.",
                       "This fixture covers successful searches with no submodules. Production recursive-submodule/config-error fallbacks and exact error transcripts are not independently exercised here.",
                       "Other source6428/6357 read/classification policies retain their scope and credit. This is not the historical154-row comparison, a universal failure-preservation proof, a Windows claim or a runtime speedup claim.",
                       "No scientific supplier replay, kappa, framework-assumption or selected-frontier change is involved."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        receipt = ROOT / "ORACLE.json"
        require(receipt.is_file(), "Retained oracle receipt ORACLE.json required")
        require(canonical(decode(receipt.read_bytes())) == canonical(result), "Retained oracle receipt mismatch")
        print("PASS independent nativeGit alias-prefilter receipt")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
