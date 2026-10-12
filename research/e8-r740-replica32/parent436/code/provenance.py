"""Check that every vendored file listed in a SOURCE-pr*.json has the git blob id recorded there, i.e. that it is
byte-identical to the file at source_path in the cited PR's commit (compare with git ls-tree -r <commit>).
Adapted from PR #381's code/provenance.py (DaysSky). Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def blob(rel):
    b = open(os.path.join(HERE, rel), "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


seen = set()
for name in sorted(glob.glob(os.path.join(HERE, "SOURCE-pr*.json"))):
    src = json.load(open(name))
    bad = [rel for rel, x in src["identical"].items() if blob(rel) != x["blob"]]
    if bad:
        sys.exit("files differ from %s at %s: %s" % (src["source"], src["commit"][:7], bad))
    seen |= set(src["identical"])
    print("   %2d files byte-identical to %s at %s (git blob ids)"
          % (len(src["identical"]), src["source"].replace("https://github.com/CrocSwap/integer-mult-bounds/pull/", "PR #"),
             src["commit"][:7]))
print("   %d vendored files in all (some pinned to two PRs); every other file is new in this package" % len(seen))
