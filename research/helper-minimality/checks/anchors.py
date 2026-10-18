"""File:line anchors quoted in the README: each quoted line must contain the quoted text in the vendored file."""
import os, sys
HM = os.environ['HM_ROOT']; bad = 0
def rd(p): return open(os.path.join(HM, p), encoding='utf-8').read().split('\n')
A = [
 ('inputs/pr799/independent/audit_local.py', 31, "def registers(e):return e[1:3] if e[0]=='add' else e[1:2]", 'AL:31 registers() of an op'),
 ('inputs/pr799/independent/audit_local.py', 82, "main=w['A']+w['cut']+w['B']", 'AL:82 one cut section'),
 ('inputs/pr799/independent/audit_local.py', 88, "non-target reads target", 'AL:88 covers A,B only'),
 ('inputs/pr799/independent/audit_local.py', 115, "end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R", 'AL:115 end caps perp(port)'),
 ('inputs/pr799/independent/audit_local.py', 117, "start=[(p,) for p in w['ports']]+[()]*(v+R)", 'AL:117 start frames'),
 ('inputs/pr799/independent/audit_local.py', 122, "require(contained(cur[q],U),'frame not monotone '", 'AL:122 monotone frames'),
 ('inputs/pr799/independent/audit_local.py', 125, "cur[q]=U", 'AL:125 cur assigned in climb'),
 ('inputs/pr799/independent/audit_local.py', 132, "served={lev.get(e[1]-v,()) for e in w['cut'] if e[2]==q}", 'AL:132 cut ops only supply the served set'),
 ('inputs/pr799/independent/audit_local.py', 138, "for q in registers(e):climb(q,e[-1])", 'AL:138 A/B op frames'),
 ('inputs/pr799/independent/audit_local.py', 142, "for q,U in enumerate(end):climb(q,U)", 'AL:142 end caps'),
 ('inputs/pr635/hpe_emit_local.py', 94, "terms=[e for e in c['cut'] if e[2]==r]", 'emitter:94 keeps only centre-sourced cut ops'),
 ('inputs/pr799/code/audit_allcold.py', 75, "==8", 'audit_allcold:75 8 centres'),
 ('inputs/pr799/code/emit_allcold.py', 41, "==8", 'emit_allcold:41 8 centres'),
 ('inputs/pr799/construction/construct_gauge_xcentre.py', 344, "cut=[['add',v+t,centers[i]", 'generator:344 cut = add target<-centre'),
 ('inputs/pr799/construction/construct_gauge_xcentre.py', 360, "assert is_cut and e[0]=='add' and e[1]-120==e[2] and e[2]<8", 'generator:360 assert on cut ops'),
 ('inputs/main/03-motifs.tex', 78, "subtract scatter", 'spec:78 step 1 subtract scatter'),
 ('inputs/main/03-motifs.tex', 79, "copy", 'spec:79 step 2 copy'),
 ('inputs/main/03-motifs.tex', 80, "gather", 'spec:80 step 3 gather'),
 ('inputs/main/03-motifs.tex', 81, "targets and center", 'spec:81 step 4 scatter on targets and center'),
 ('inputs/main/03-motifs.tex', 83, "undo gather", 'spec:83 step 6 undo gather'),
]
for f, ln, sub, name in A:
    L = rd(f)
    ok = ln <= len(L) and sub.replace(' ', '') in L[ln - 1].replace(' ', '')
    print('%s anchor %s' % ('PASS' if ok else 'FAIL', name)); bad += (not ok)
sys.exit(1 if bad else 0)
