"""Construct the fully paid four-carrier control circuit, Apache-2.0.

Douglas R. Colkitt with substantial OpenAI Codex assistance. Applies scoped
changes to the pinned #622 constructor; preserves its scalar, frame,
rank-mass and restoration assertions. The two new copies are explicitly paid.
Run through verify.py, which checks the source pins first.
"""
from pathlib import Path
import hashlib
import json
import sys

if not __debug__:
    raise SystemExit('Constructor requires assertions enabled.')
root = Path(__file__).resolve().parents[2]
srcpath = root/'research/complex-k492-owner-repair/code/construct_k_triangle.py'
pins = json.loads((Path(__file__).parent/'SOURCE-PINS.json').read_text())
if hashlib.sha256(srcpath.read_bytes()).hexdigest() != pins['files'][str(srcpath.relative_to(root))]:
    raise ValueError('constructor source pin mismatch')
src = srcpath.read_text()


def change(before, after):
    global src
    if src.count(before) != 1:
        raise ValueError(('ambiguous constructor substitution', before[:80], src.count(before)))
    src = src.replace(before, after)


recipe = json.loads(Path(sys.argv[1]).read_text())
output = Path(sys.argv[2]).resolve()
change('NH=504-3*len(FULLT)+len(COPYL)',f'PARTIAL={recipe!r}\nPARTIAL_KEYS={{(tuple(c),tuple(PARTIAL["pair"]),PARTIAL["sign"]) for c in PARTIAL["blocks"]}}\nPARTIAL_TARGETS={{t+8 for t in PARTIAL["targets"]}}\nNH=504-3*len(FULLT)+len(COPYL)-len(PARTIAL_KEYS)+2')
change('if t in TRI_COORDS:continue','if t in TRI_COORDS or t in PARTIAL_TARGETS:continue')
change('skipev={face_info(c,p,eps)[0] for p,eps in keys if (p,eps) in FULLT}', 'skipev={face_info(c,p,eps)[0] for p,eps in keys if (p,eps) in FULLT or (c,p,eps) in PARTIAL_KEYS}')
change('if tuple(key) in FULLT:skip();continue','if tuple(key) in FULLT or (c,key[0],key[1]) in PARTIAL_KEYS:skip();continue')
change('# Both tetrahedra use the same partition.', '''# Complete partial K/M reads, including remaining packets, before forming
# the two selected-source packets required by the ordinary M consumer.
p,eps=tuple(PARTIAL['pair']),PARTIAL['sign']
sel=sorted(tuple(c) for c in PARTIAL['blocks'])
nonselected=next(c for c in blocks if set(p)<=set(c) and c not in sel)
partial_packets=[packets[nonselected,p,eps,c] for c in sel]
for _ in range(2):
    r,alpha=partial_packets[0];n=alloc();add(n,r,1,cur[r]);partial_packets.append((n,alpha))
for op in PARTIAL['ops']:
    t=op[0]+8;key,coef=reqcoef[t]
    assert key[1:]==(p,eps)
    if op[1]=='packet':
        r,alpha=partial_packets[op[2]];q=coef*alpha
    else:
        _,_,blk,loc=op;blk=tuple(blk);r=maps[blk][loc]
        if blk==key[0]:
            rr,q,F0=own_rows[t];assert rr==r
        else:
            j,alpha=face_info(blk,p,eps);assert loc in blocks[blk]['events'][j][:2]
            q=coef*alpha
    F=basis(cur[v+t]+cur[r]);assert inside(F,hyper(P[t])),('PARTIAL frame',t)
    add(v+t,r,q,F)
for c in sel:
    j,alpha=face_info(c,p,eps);a,b,num,den=blocks[c]['events'][j]
    a,b=maps[c][a],maps[c][b];F=basis(cur[a]+cur[b])
    add(a,b,Q(num,den),F)
    packets[c,p,eps,nonselected]=(a,alpha)

# Both tetrahedra use the same partition.''')
change('for j,(target,coef) in enumerate(sorted(reqs)):\n        first_source', 'for j,(target,coef) in enumerate(sorted(reqs)):\n        if target in PARTIAL_TARGETS:continue\n        first_source')
# The old allocator tracks 504 original slots; the two additional calls to
# alloc() create fresh slots 504/505. Keep them separate in the provenance map.
change('len(shadow)+len(skipped)==504','len(shadow)+len(skipped)==506')
change('for i,s_ in enumerate(shadow)}}', 'for i,s_ in enumerate(shadow) if s_<744}}')
change("'removed_504_helpers':[", "'added_helpers':[224+i for i,s_ in enumerate(shadow) if s_>=744], 'removed_504_helpers':[")
sys.argv = [str(srcpath), str(root/'research/direct-delivery504-global/inputs/hamming'),
            str(output), str(root/'research/complex-k492-owner-repair/data/TRI-SCHEDULE.json')]
exec(compile(src, 'partial_k_constructor', 'exec'), {})
