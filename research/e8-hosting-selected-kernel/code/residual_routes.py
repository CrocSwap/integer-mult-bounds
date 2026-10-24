"""Generate exact coordinate isometries for this kernel's residuals.
OpenAI Codex. Route witness/check conventions follow chafreaky's PR439.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'vendor/pr439'))
from bank_routes import validate_isometries

def generate(word,dimensions):
    roots=word['lines'];index={tuple(r):i for i,r in enumerate(roots)};out=[]
    for f in sorted(set(word['start'][240:])):
        e=dimensions[f];rs=[roots[j] for j in word['frames'][f]]
        axes=sorted({i for r in rs for i,x in enumerate(r) if x})
        assert len(axes)==e, 'This finite selection must have coordinate entrances'
        order=axes+[i for i in range(8) if i not in axes]
        matrix=[[2*int(i==j) for j in range(8)] for i in order]
        basis=[index[tuple(r)] for r in matrix]
        assert set(basis[:e])<=set(word['frames'][f])
        reduced=order[:];ops=[]
        for i in range(8):
            j=reduced.index(i)
            if i!=j:reduced[i],reduced[j]=reduced[j],reduced[i];ops.append(['swap',i,j,None])
        assert reduced==list(range(8)) and len(ops)<=7
        out.append(dict(frame=f,entrance_rank=e,denominator=2,entrance_basis=basis[:e],residual_basis=basis[e:],orthogonal_rows_numerator=matrix,gaussian_reduction=ops))
    assert validate_isometries(out,word['frames'],roots,dimensions)==set(word['start'][240:])
    return out
