#!/usr/bin/env python3
"""Exact rational controls of gauged exits, tensor connectors and copied correction.
Zhihao Chen / Codex audit; symbolic identities in companion report cover all h.
"""
import json,time,signal
from pathlib import Path
import sympy as s
HERE=Path(__file__).resolve().parent
def main():
    st=time.monotonic()
    def stop(*_):raise TimeoutError('120 seconds')
    signal.signal(signal.SIGALRM,stop);signal.alarm(120)
    def D(P):
        I=s.eye(P.rows);return (I-P).row_join(P).col_join(P.row_join(I-P))
    rows=[];bad_controls=0
    for h in (4,5):
        I=s.eye(h);G=I-s.ones(h)/9
        def proj(B):return B*(B.T*G*B).inv()*B.T*G if B.cols else s.zeros(h)
        P=proj(s.Matrix([int(i<3) for i in range(h)]))
        Q=proj(s.Matrix([int(i>=h-3) for i in range(h)]))
        K=s.kronecker_product;m=h*h;J=s.eye(m);U=K(P,Q);B=K(I-P,I);T=K(I,Q)
        C=K(I-P,I-Q)
        X1=T;Y1=K(I-P,Q);X2=B+U;Y2=B
        assert X2-X1==Y2-Y1==C and C*C==C and C.rank()==(h-1)**2
        assert D(X2)*D(X1)==D(C) and D(Y2)*D(Y1)==D(C)
        assert D(U)*D(J)==D(J-U)
        for f in range(h+1):
            sigma=proj(I[:,:f]);A=K(sigma,Q)
            exit1=J-T+A;end1=J-A
            live2=J-K(P,sigma);end2=J-B;exit2=B+K(P,sigma)
            assert exit1*exit1==exit1 and exit2*exit2==exit2
            assert exit1.rank()==exit2.rank()==m-h+f
            assert D(end1)*D(T)==D(exit1)
            assert D(end2)*D(live2)==D(exit2)
            assert D(end1)*D(A)==D(J) and D(end2)*D(B)==D(J)
            if f:
                assert D(end1)*D(T)!=D(J-T);bad_controls+=1
            rows.append(dict(h=h,sigma_rank=f,exterior_rank=m-h+f,all_identities=True))
    out=dict(rows=rows,negative_omitted_sigma_rejected=bad_controls,
        data_connectors_per_pair=2,connector_rank_formula='(h-1)^2',correction_rank=1,
        elapsed=time.monotonic()-st,limit_seconds=120,
        scope='Exact rational finite controls of general tensor identities; not a full all-size compiler, complex phase/precision or final multiplication theorem.',new_multiplication_bound=False)
    (HERE/'round7-tensor-endpoint-controls.json').write_text(json.dumps(out,indent=2)+'\n')
    signal.alarm(0);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
