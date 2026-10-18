"""The eleven-stage emitter, independent audit and local projector audit used for this word are PR #472's files
(chafreaky, with OpenAI Codex assistance; vendored byte-identical under code/hub/e8-r715-whole-hosted/code/) with the
exact edits listed below and nothing else: package paths, R = 489 in place of the hard-coded R715 counts, a
--hosting argument for the frozen selection, and one helper entrance frame (frame zero) in place of eleven.
usage: adapt.py --write   (regenerate code/eleven/{emit,audit,local_audit}.py from the pinned originals)
       adapt.py --check   (fail unless the shipped adapted files equal the pinned originals with these edits)
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "hub" / "e8-r715-whole-hosted" / "code"
HEAD = "# Adapted from PR #472's code/%s (chafreaky, with OpenAI Codex assistance) by code/eleven/adapt.py: R = 489,\n" \
       "# package paths, frozen hosting selection argument, frame-zero helper entrances. Apache-2.0.\n"
EDITS = {
    "emit.py": [
        ('sys.path.insert(0,str(HERE.parents[1]/"e8-r740-replica32/code"))\n',
         'sys.path.insert(0,str(HERE.parent/"hub/e8-r740-replica32/code"))\n'),
        ('sys.path.insert(0,str(HERE.parents[1]/"idle-axis-hosting"))\n',
         'sys.path.insert(0,str(HERE.parent/"hub/idle-axis-hosting"))\n'),
        ("    ap.add_argument('--isometries',type=Path,required=True)\n",
         "    ap.add_argument('--isometries',type=Path,required=True); ap.add_argument('--hosting',type=Path,required=True)\n"),
        ("    ys,zs,proxy=HC.load_selection(HERE.parent/'data/hosting.json','bit')\n",
         "    ys,zs,proxy=HC.load_selection(a.hosting,'bit')\n"),
    ],
    "audit.py": [
        ("K,L,M,T,V,R=5,11,78,8,120,715\n", "K,L,M,T,V,R=5,11,78,8,120,489\n"),
        ("    widths=[8-fs[str(state['initial'][str(h)])]['dim'] for h in range(240,955)]\n",
         "    widths=[8-fs[str(state['initial'][str(h)])]['dim'] for h in range(240,240+R)]\n"),
        ("    assert (g['live'],g['physical'],g['hosted_residuals'],g['bank_assignments'],g['deficit'])==(9600,9609,62920,0,3264)\n",
         "    assert (g['live'],g['physical'],g['hosted_residuals'],g['bank_assignments'],g['deficit'])==(9600,9609,L*T*R,0,3264)\n"),
        ("    assert g['independent_unbanked_scalar_columns']==9065 and len(g['scalar_stages'])==11 and g['all_scalar_columns_restored']\n",
         "    assert g['independent_unbanked_scalar_columns']==2*K*V+L*R and len(g['scalar_stages'])==11 and g['all_scalar_columns_restored']\n"),
        ("profile={str(r):n for r,n in sorted(P.items())},live=9600,physical=9609,hosted_residuals=62920,\n",
         "profile={str(r):n for r,n in sorted(P.items())},live=9600,physical=9609,hosted_residuals=L*T*R,\n"),
    ],
    "local_audit.py": [
        ('"""Exact frame projectors and independent decoding of fresh R715 rank120 records.\n',
         '"""Exact frame projectors and independent decoding of fresh R489 records (all helpers enter at frame zero).\n'),
        ("ROOT=Path(__file__).resolve().parents[1]\n", "ROOT=Path(__file__).resolve().parents[2]\n"),
        ("sys.path.insert(0,str(ROOT.parent/'e8-r740-replica32/code'))\n",
         "sys.path.insert(0,str(ROOT/'code/hub/e8-r740-replica32/code'))\n"),
        (" assert lg['copies']==lg['erasures']==9 and cc['formal_columns_checked']==1195\n",
         " assert lg['copies']==lg['erasures']==9 and cc['formal_columns_checked']==969\n"),
        (" word=json.loads(gzip.decompress((ROOT/'data/word.json.gz').read_bytes()))\n",
         " word=json.loads(gzip.decompress((ROOT/'data/bit/bitE8mut-r489.json.gz').read_bytes()))\n"),
        (" initial=[state['initial'][str(i)] for i in range(955)];assert initial==word['start']\n",
         " initial=[state['initial'][str(i)] for i in range(729)];assert initial==word['start']\n"),
        (" iso=read(ROOT/'data/residual-isometries.json')\n", " iso=read(ROOT/'data/eleven/residual-isometries.json')\n"),
        (" assert validate_isometries(iso,word['frames'],word['lines'],dims)==set(initial[240:]) and len(iso)==11\n",
         " assert validate_isometries(iso,word['frames'],word['lines'],dims)==set(initial[240:]) and len(iso)==1\n"),
        (" rank=sum(dims[f] for f in initial[240:]);assert rank==120\n",
         " rank=sum(dims[f] for f in initial[240:]);assert rank==0\n"),
        (" result=dict(status='PASS_EXACT_R715_RANK120_LOCAL_PROJECTORS',",
         " result=dict(status='PASS_EXACT_R489_LOCAL_PROJECTORS',"),
    ],
}


def adapted(name):
    text = (SRC / name).read_text()
    for old, new in EDITS[name]:
        assert text.count(old) == 1, (name, old)
        text = text.replace(old, new)
    return HEAD % name + text


mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
for name in EDITS:
    want = adapted(name)
    if mode == "--write":
        (HERE / name).write_text(want)
    else:
        assert (HERE / name).read_text() == want, "code/eleven/%s differs from PR #472's file plus the listed edits" % name
print("   code/eleven/{emit,audit,local_audit}.py = PR #472's files + %d listed edits (%s)" %
      (sum(len(e) for e in EDITS.values()), "written" if mode == "--write" else "checked"))
