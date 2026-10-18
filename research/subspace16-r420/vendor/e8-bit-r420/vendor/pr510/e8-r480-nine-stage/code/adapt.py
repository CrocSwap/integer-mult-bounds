# Writes the one adapted file this package runs, from the vendored PR #463 audit_parent_k.py, by exact string edits
# (each anchor must occur exactly once). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
# Apache-2.0.
"""usage: adapt.py VENDORED_CODE_DIR OUTDIR  ->  OUTDIR/audit_parent_k.py
Edit 1: HERE points at the vendored code directory (the adapted copy lives outside the package).
Edit 2: the template control 'omit a residual route factor' mutates the first residual isometry that HAS a route
        factor (a non-empty gaussian_reduction). In R480 every helper enters at frame zero, so the only isometry is the
        identity with no route factor, the selector raises StopIteration and the audit cannot start. The control is
        vacuous then (there is no factor to omit) and is skipped exactly in that case; all other controls run."""
import sys
from pathlib import Path

code, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
text = (code / 'audit_parent_k.py').read_text()
EDITS = [
    ("HERE = Path(__file__).resolve().parent", "HERE = Path(%r)" % str(code)),
    ("    rejects('omit a residual route factor',lambda q:next(r for r in q['residual_isometries'] if r['gaussian_reduction'])['gaussian_reduction'].pop())",
     "    if any(r['gaussian_reduction'] for r in t['residual_isometries']):   # vacuous when no isometry has a route factor\n"
     "        rejects('omit a residual route factor',lambda q:next(r for r in q['residual_isometries'] if r['gaussian_reduction'])['gaussian_reduction'].pop())"),
]
for old, new in EDITS:
    assert text.count(old) == 1, old
    text = text.replace(old, new)
out.mkdir(parents=True, exist_ok=True); (out / 'audit_parent_k.py').write_text(text)
print('   adapted audit_parent_k.py with %d listed edits (each anchor found exactly once)' % len(EDITS))
