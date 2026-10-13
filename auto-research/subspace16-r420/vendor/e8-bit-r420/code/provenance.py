"""Provenance of everything this package runs that it did not write.
usage: provenance.py PACKAGE_DIR
  1. every vendored file listed in SOURCE-pr*.json has the recorded blob id (sha1 of "blob <size>\\0" + bytes), i.e. it is
     byte-identical to the file at source_path in the cited PR's commit; the vendored set equals the listed set;
  2. the files of main this package uses are pinned in DEPENDS.json by sha256; PR #493's package
     (research/e8-bit-carrier-skeleton) is pinned through its own MANIFEST.sha256: every file of that directory must
     match it and no file may be unlisted;
  3. seven of the files PR #510 vendors are also byte-identical to PR #493's copies on main.
Adapted from PR #493's code/provenance.py (itself adapted from PR #381's, DaysSky).
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.abspath(sys.argv[1])
PARENT = os.path.join(HERE, "..", "e8-bit-carrier-skeleton")


def read(rel, base=HERE):
    return open(os.path.join(base, rel), "rb").read()


def blob(b):
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


listed = set()
for name in sorted(glob.glob(os.path.join(HERE, "SOURCE-pr*.json"))):
    src = json.load(open(name))
    bad = [rel for rel, x in src["identical"].items() if blob(read(rel)) != x["blob"]]
    if bad:
        sys.exit("files differ from %s at %s: %s" % (src["source"], src["commit"][:7], bad))
    listed |= set(src["identical"])
    print("   %2d files byte-identical to PR #%s at %s (%s)" % (len(src["identical"]), src["source"].rsplit("/", 1)[-1],
                                                              src["commit"][:7], src["head_repository"]))
vendored = {os.path.relpath(os.path.join(r, f), HERE) for r, _, fs in os.walk(os.path.join(HERE, "vendor")) for f in fs
            if "__pycache__" not in r}
vendored |= {os.path.relpath(p, HERE) for p in glob.glob(os.path.join(HERE, "data/complex/*/*"))}
assert vendored == listed, ("vendored set differs from the SOURCE pins", sorted(vendored ^ listed))
dep = json.load(open(os.path.join(HERE, "DEPENDS.json")))
for rel, x in dep["files"].items():
    b = read(rel)
    assert hashlib.sha256(b).hexdigest() == x["sha256"] and blob(b) == x["blob"], ("main file changed", rel)
bad, seen = [], set()
for line in read("MANIFEST.sha256", PARENT).decode().splitlines():
    h, p = line.split("  ", 1)
    seen.add(p)
    if hashlib.sha256(read(p, PARENT)).hexdigest() != h:
        bad.append(p)
files = {os.path.relpath(os.path.join(r, f), PARENT) for r, _, fs in os.walk(PARENT) for f in fs
         if "__pycache__" not in r} - {"MANIFEST.sha256"}
assert not bad and files == seen, ("PR #493 package differs from its MANIFEST.sha256", bad, sorted(files ^ seen))
print("   main (commit %s): %d pinned files unchanged; PR #493's package matches its MANIFEST.sha256 (%d files)"
      % (dep["commit"][:7], len(dep["files"]), len(seen)))
V = "vendor/pr510/e8-r480-nine-stage/vendor/"
same = [(V + "e8-r740-replica32/code/" + n, "code/hub/e8-r740-replica32/code/" + n)
        for n in ("bank_routes.py", "tile_m.py", "e8core.py", "engines/moment.py", "engines/base_two_moment.py",
                  "engines/outer.py")] + [(V + "idle-axis-hosting/hosting_core.py", "code/hub/idle-axis-hosting/hosting_core.py")]
for a, b in same:
    assert read(a) == read(b, PARENT), (a, b)
print("   %d of PR #510's vendored files are also byte-identical to PR #493's copies on main" % len(same))
