"""Write R-specific copies of PR #493's eleven-stage audit files (code/eleven/audit.py and local_audit.py, which are
PR #472's files adapted to R = 489) for another word: the same exact string edits PR #503's adapt.py makes for R = 480,
for any R.  Every anchor must occur exactly once.  emit.py and assemble.py take the word and R as arguments and are
used unchanged.
usage: adapt11.py SKELETON_PACKAGE_DIR WORD.json.gz R OUTDIR
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import sys
from pathlib import Path

pkg, word, R, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), int(sys.argv[3]), Path(sys.argv[4])
EDITS = {
    "audit.py": [("K,L,M,T,V,R=5,11,78,8,120,489\n", "K,L,M,T,V,R=5,11,78,8,120,%d\n" % R)],
    "local_audit.py": [
        ("ROOT=Path(__file__).resolve().parents[2]\n", "ROOT=Path(%r)\n" % str(pkg)),
        (" assert lg['copies']==lg['erasures']==9 and cc['formal_columns_checked']==969\n",
         " assert lg['copies']==lg['erasures']==9 and cc['formal_columns_checked']==%d\n" % (4 * 120 + R)),
        (" word=json.loads(gzip.decompress((ROOT/'data/bit/bitE8mut-r489.json.gz').read_bytes()))\n",
         " word=json.loads(gzip.decompress((Path(%r)).read_bytes()))\n" % str(word)),
        (" initial=[state['initial'][str(i)] for i in range(729)];assert initial==word['start']\n",
         " initial=[state['initial'][str(i)] for i in range(%d)];assert initial==word['start']\n" % (240 + R)),
        (" result=dict(status='PASS_EXACT_R489_LOCAL_PROJECTORS',",
         " result=dict(status='PASS_EXACT_R%d_LOCAL_PROJECTORS'," % R),
    ],
}
out.mkdir(parents=True, exist_ok=True)
n = 0
for name, edits in EDITS.items():
    text = (pkg / "code" / "eleven" / name).read_text()
    for old, new in edits:
        assert text.count(old) == 1, (name, old)
        text = text.replace(old, new)
        n += 1
    (out / name).write_text(text)
print("   adapted code/eleven/audit.py and local_audit.py to R = %d with %d listed edits (each anchor found once)" % (R, n))
