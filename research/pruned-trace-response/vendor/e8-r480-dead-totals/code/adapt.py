# Writes the three adapted files this package runs, from PR #493's package (research/e8-bit-carrier-skeleton),
# by exact string edits; each edited string must occur exactly once in the parent file. Nothing else changes.
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""usage: adapt.py PARENT_PACKAGE R480_WORD OUTDIR
   OUTDIR/gen_r480.py           = parent code/skeleton/gen.py, totals hosted on the LAST eligible dead register
   OUTDIR/eleven/audit.py       = parent code/eleven/audit.py with R = 480
   OUTDIR/eleven/local_audit.py = parent code/eleven/local_audit.py with R = 480 (960 formal columns, 720 registers,
                                  the audited word = the R480 word); parent package root for the shared hub files"""
import sys
from pathlib import Path

PARENT, WORD, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
EDITS = {
    'code/skeleton/gen.py': ('gen_r480.py', [
        # the parent modules (e8, geom, wordkit) are imported from the parent package
        ("sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))",
         "sys.path.insert(0, %r)" % str(PARENT / 'code/skeleton')),
        # THE change: a total formed on a dead register is hosted by the last eligible register of its combination
        # (the parent takes the first one; with the first, the payload bill is 129 bits > 104)
        ("host = next((r for r in sorted(combo) if r not in used",
         "host = next((r for r in sorted(combo, reverse=True) if r not in used"),
    ]),
    'code/eleven/audit.py': ('eleven/audit.py', [
        ("K,L,M,T,V,R=5,11,78,8,120,489", "K,L,M,T,V,R=5,11,78,8,120,480"),
    ]),
    'code/eleven/local_audit.py': ('eleven/local_audit.py', [
        ("ROOT=Path(__file__).resolve().parents[2]", "ROOT=Path(%r)" % str(PARENT)),
        ("cc['formal_columns_checked']==969", "cc['formal_columns_checked']==960"),
        ("(ROOT/'data/bit/bitE8mut-r489.json.gz')", "(Path(%r))" % str(WORD)),
        ("range(729)", "range(720)"),
        ("PASS_EXACT_R489_LOCAL_PROJECTORS", "PASS_EXACT_R480_LOCAL_PROJECTORS"),
    ]),
}
n = 0
for src, (dst, edits) in EDITS.items():
    text = (PARENT / src).read_text()
    for old, new in edits:
        assert text.count(old) == 1, (src, old, text.count(old))
        text = text.replace(old, new); n += 1
    out = OUT / dst; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(text)
print('   adapted 3 parent files with %d listed edits (each anchor found exactly once)' % n)
