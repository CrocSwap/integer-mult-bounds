"""Exact phase-aware checks for an all-width three-call sector completion."""
import hashlib,importlib.util,json
from pathlib import Path


def main():
    root=Path(__file__).resolve().parent
    src=root/'pr4710'/'verify_residual.py'
    pins=json.loads((root/'SOURCE-PINS.json').read_text(encoding='utf-8'))
    expected=next(x['sha256'] for x in pins if x['file']=='pr4710/verify_residual.py')
    if hashlib.sha256(src.read_bytes()).hexdigest()!=expected:raise ValueError('frozen residual source drift')
    spec=importlib.util.spec_from_file_location('frozen_residual',src);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    I=v.ident(); C=[v.c_letter(i) for i in range(3)]
    T=v.monomial([((x&1)<<2)|(x&2)|((x&4)>>2) for x in range(8)])
    U=v.monomial([0,5,2,7,4,1,6,3]); V=v.monomial([0,2,1,3,4,6,5,7]); S=v.s_letter(7)
    P=v.word(S,U,S);Q=v.word(S,V,S)
    A=v.word(C[0],P,C[0]);B=v.word(C[0],Q,C[0]);F=v.plus(A,v.scale(v.q(2),B))
    K=v.word(*C);a=v.pauli(1,3);W=v.pauli(0,5);J=v.word(v.pauli(0,2),V,C[2])
    M=v.monomial([2,0,3,1,4,6,5,7],[0,0,2,2,1,3,3,1])
    def req(x,label):
        if not x:raise ValueError(label)
    req(v.word(T,T)==I,'T inverse')
    req(v.word(T,C[0],T)==C[2],'actual swap conjugation')
    req(v.word(J,W,A)==v.word(M,C[2]),'P word residual')
    req(v.word(J,W,B)==v.word(K,a),'Q word target')
    out_pauli=v.word(K,a,v.adjoint(K));desc=v.describe_pauli(out_pauli)
    req(v.word(v.adjoint(out_pauli),K,a)==K,'free output ABI correction')
    rejected=0
    for sign in [1,-1]:
        E=v.scale(v.q(1,0),v.plus(I,v.scale(v.q(sign),T)))
        E=v.scale(v.q(v.F(1,2)),E)
        req(v.word(E,E)==E,'projector idempotence')
        req(v.word(C[2],E)==v.scale(v.q(sign),v.word(T,C[0],E)),'sector residual closure')
        left=v.plus(v.word(J,W,F,E),v.scale(v.q(-sign),v.word(M,T,C[0],E)))
        req(left==v.scale(v.q(2),v.word(K,a,E)),'full completed sector')
        got=v.scale(v.q(v.F(1,2)),v.word(v.adjoint(out_pauli),left))
        req(got==v.word(K,E),'canonical target on sector')
        bad=v.plus(v.word(J,W,F,E),v.scale(v.q(sign),v.word(M,T,C[0],E)))
        req(bad!=v.scale(v.q(2),v.word(K,a,E)),'wrong residual sign control');rejected+=1
    print(json.dumps({'status':'PASS_THREE_CALL_SECTOR_COMPLETION','paid_calls':3,'sectors':[1,-1],'output_abi_pauli':desc,'wrong_sign_rejections':rejected,'proof_scope':'base word identities tensorized separately; scalar coefficients outside tensor powers','new_kappa':False},sort_keys=True))

if __name__=='__main__':main()
