"""Actual canonical-chart active-Pauli gauge recipes and finite controls.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
No profitable profile is asserted; use these complete operators in a census.
"""
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CE=ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
WORD=ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'


def load_ce():
    spec=importlib.util.spec_from_file_location('active_palette_exact_clifford',CE)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def canonical_chart(ce,basis,n=9):
    r=len(basis)
    if r in (0,n):return ce.ident(n)
    G=ce.transpose(ce.basis_extend(tuple(basis),n),n)
    inverse=ce.inv(G,n);columns=ce.transpose(inverse,n)
    quadratic=tuple((1<<i)^sum(ce.parity(a&b)<<j for j,b in enumerate(columns))
                    for i,a in enumerate(columns))
    return ce.perm(n,G).then(ce.diag(n,quadratic))


def active_frame(ce,basis,mask,n=9):
    """Chronological circuit K^-1 -> C_active -> C_mask -> K.

    In ordinary left action this is K C_mask C_active K^-1. The mask is
    in the canonical active chart, never guessed from raw physical vectors.
    """
    r=len(basis)
    if not 0<=mask<1<<r:raise ValueError('mask supported in actual active chart')
    K=canonical_chart(ce,basis,n)
    return K.adjoint().then(ce.fourier(n,range(r))).then(ce.cgate(n,mask)).then(K)


def small_palette(r):
    return list(dict.fromkeys([0]+([1,1<<(r-1),(1<<r)-1] if r else [])))


def action(columns,value):
    out=0
    while value:
        bit=value&-value;out^=columns[bit.bit_length()-1];value^=bit
    return out


def main():
    began=time.monotonic();ce=load_ce();rankcases=0
    for r in range(10):
        for mask in range(1<<r):
            columns=[(1<<j)^(mask if mask>>j&1 else 0) for j in range(r)]
            odd=mask.bit_count()%2
            assert ce.rank(columns)==r-odd
            if odd:
                assert {x for x in range(1<<r) if action(columns,x)==0}=={0,mask}
            else:
                assert all(action(columns,action(columns,1<<j))==1<<j for j in range(r))
            rankcases+=1
    raw=gzip.decompress(WORD.read_bytes());c=json.loads(raw)['canonical']
    # Bound the actual-operator control: first and last registered frames of
    # each available rank. This is not an all-frame paid-profile admission.
    chosen=[]
    for rank in range(10):
        ids=[i for i,basis in enumerate(c['frames']) if len(basis)==rank]
        chosen+=list(dict.fromkeys([ids[0],ids[-1]])) if ids else []
    rows=[];unit_checks=0
    for frame in chosen:
        basis=c['frames'][frame];r=len(basis);K=canonical_chart(ce,basis);old=ce.canonical_frame(9,basis)
        baseline=active_frame(ce,basis,0)
        assert baseline.tab==old.tab and baseline.zero_state()==old.zero_state()
        recipes=[]
        for mask in small_palette(r):
            actual=active_frame(ce,basis,mask)
            fourier_rank=ce.rank([x for x,z,p in actual.tab[9:]])
            assert fourier_rank==r-mask.bit_count()%2
            square=actual.then(actual)
            expected=K.adjoint().then(ce.xgate(9,((1<<r)-1)^mask)).then(K)
            assert square.tab==expected.tab and square.zero_state()==expected.zero_state()
            if mask and mask.bit_count()==1:
                index=mask.bit_length()-1
                cancelled=K.adjoint().then(ce.fourier(9,[j for j in range(r) if j!=index])).then(ce.xgate(9,mask)).then(K)
                assert actual.tab==cancelled.tab and actual.zero_state()==cancelled.zero_state()
                unit_checks+=1
            recipes.append(dict(mask=mask,active_weight=mask.bit_count(),fourier_rank=fourier_rank,
                literal_circuit=actual.circuit,actual_tableau_sha256=sha256(json.dumps(actual.tab).encode()).hexdigest()))
        rows.append(dict(frame=frame,registered_basis=basis,rank=r,recipes=recipes))
    result=dict(status='PASS_SCOPED_ACTIVE_PAULI_PALETTE',author='Cao Yifan',new_kappa=False,
        rank_and_kernel_cases=rankcases,actual_registered_frames=len(chosen),actual_unit_cancellations=unit_checks,
        palette='deduplicated old/first-active-unit/last-active-unit/all-active mask',frames=rows,
        exact_square='A_v^2=K X_(ones_active xor v) K^-1; including actual Pauli phase',
        input_sha256={str(CE.relative_to(ROOT)):sha256(CE.read_bytes()).hexdigest(),str(WORD.relative_to(ROOT)):sha256(WORD.read_bytes()).hexdigest()},
        actual_word_canonical_sha256=sha256(raw).hexdigest(),script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Finite canonical operator controls and universal written/Lean kernel algebra; no all-frame invoice, scalar-contact optimization, complete helper endpoint proof, or new kappa.',
        seconds=time.monotonic()-began)
    (HERE/'ACTIVE-PALETTE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],rankcases,len(chosen),unit_checks,round(result['seconds'],3),flush=True)


if __name__=='__main__':main()
