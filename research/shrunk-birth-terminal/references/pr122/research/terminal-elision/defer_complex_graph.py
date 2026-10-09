#!/usr/bin/env python3
"""Adapt pinned PR110's explicit deferred-role compiler to a frozen graph.

Exports the full finite word/frames, exact integer adjoint numerators, and
conservative scalar-work/height counts. PR110's additional two-stage/gauge
proof obligations are not discharged by this producer alone.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def once(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--compiler-repo', type=Path, required=True)
    ap.add_argument('--case', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--order', choices=('ascending', 'reversed'), required=True)
    a = ap.parse_args()
    assert not sys.flags.optimize
    repo, case, out = a.compiler_repo.resolve(), a.case.resolve(), a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = repo / 'research/deferred-stopped/complex_deferred.py'
    original = source.read_text()
    new = once(original, 'ROOT = HERE.parents[1]', 'ROOT = Path(' + repr(str(repo)) + ')')
    start = new.index('from stopped_product.complex import build')
    end = new.index('\n', start)
    replacement = '''import shutil
import gzip
CASE = Path(CASE_LITERAL)
def build(h, prefix, central_disjoint):
    require(h==24 and central_disjoint==24, 'frozen all-disjoint case')
    for suffix in ('.bin','.labels'):
        shutil.copyfile(CASE/('graph'+suffix), Path(str(prefix)+suffix))
'''.replace('CASE_LITERAL', repr(str(case)))
    new = new[:start] + replacement + new[end:]
    old = "require(len(links) == 8966 and R == 44918, 'matching size %d, roles %d' % (len(links), R))"
    new = once(new, old, "expected = json.loads((CASE/'matched.json').read_text())\n"
               "    require(len(links)==expected['matched'] and R==expected['R'], 'maximum cardinality and roles against frozen matcher')")
    if a.order == 'reversed':
        new = once(new, 'key=lambda i: ((i ^ 1) in (a, b), i)',
                   'key=lambda i: ((i ^ 1) in (a, b), -i)')
    # Use exact integer adjoint coordinates with common denominator42.
    new = once(new, 'HALF = inv(2); I21 = inv(21)', 'HALF = inv(2); I21 = inv(21); I42=inv(42)')
    new = once(new, '(P - HALF) if j >= v else HALF', '-21 if j >= v else 21')
    new = once(new, '(p + q_) % P for p, q_ in zip(cvec[dst], cvec[src])',
               '(p + q_) for p, q_ in zip(cvec[dst], cvec[src])')
    new = once(new, '(dpart[dst].get(t, 0) + c) % P', '(dpart[dst].get(t, 0) + c)')
    new = once(new, '(I21 - (HALF if i in trip[t] else 0)) % P', '(2 - 21*(i in trip[t]))')
    new = once(new, 'f = sign * ci * value % P', 'f = sign * ci * value * I42 % P')
    new = once(new, 'y[t] + sign * c * value) % P', 'y[t] + sign * c * value * I42) % P')
    marker = "    (HERE / 'complex-profile.json').write_text"
    extra = '''    # Exact clean support replay, separate from modular dirty-state tests.
    clean=[0]*Rr
    for o in ops:
        if o[0]=='src':
            require(clean[o[1]]==0,'fresh input role')
            clean[o[1]]=1<<(o[2]-1)
        elif o[0]=='add':
            require(not(clean[o[1]]&clean[o[2]]),'clean support overlap')
            clean[o[1]] |= clean[o[2]]
        else:
            require(o[0]=='copy' and clean[o[2]]==0,'fresh scalar copy role')
            clean[o[2]]=clean[o[1]]
    dag=[0]*n
    for x in order:
        if not args[x][0]:dag[x]=1<<(x-1)
        else:
            aa,bb=args[x]
            require(not(dag[aa]&dag[bb]),'input DAG disjoint support')
            dag[x]=dag[aa]|dag[bb]
    require(all(clean[s]==dag[roots[j]] for s,j in role_root.items()),'exact all-input clean root supports')
    # These conservative finite constants charge the literal centre/dpart
    # readout loops, or dominate offline-combined coefficient evaluation.
    read_terms=sum(v*sum(c!=0 for c in (cv or []))+len(dp)
                   for cv,dp in zip(cvec,dpart))
    direct_ops=2*sum(o[0] in ('add','copy') for o in ops)+2*len(leaf_of)
    numerator_bound=max((19*sum(abs(c) for c in (cv or []))+
                         max((abs(c) for c in dp.values()),default=0))
                        for cv,dp in zip(cvec,dpart))
    max_bits=max(1,numerator_bound.bit_length())
    literal_scalar_terms=read_terms+direct_ops+q+h*v+4*h*h+8*h+8
    # Expanding each fixed coefficient into unit/dyadic operations followed
    # by at most one21-division gives this deliberately generous count.
    safe_scalar_groups=(4*max_bits+16)*literal_scalar_terms
    out.update(exact_clean_roots=True,adjoint_denominator=42,
        adjoint_numerator_bound=numerator_bound,max_coefficient_bits=max_bits,
        literal_readout_terms=read_terms,literal_scalar_terms=literal_scalar_terms,
        safe_one_axis_scalar_groups=safe_scalar_groups,
        second_stage_scope='Written complement-inverse and translated-gauge lemma required; this producer replays stage1.')
    witness=dict(h=h,v=v,n=n,q=q,R=R,args=args,active=list(active),
        roots=list(roots),kind=list(kind),target=target,centre_of=centre_of,
        links={x:list(r) for x,r in links.items()},ops=ops,holds=holds,
        first_node=first_node,role_root=role_root,frames=U,sigma=placed,
        phase_one=phase1,deferred=deferred,reach=[sorted(t) for t in reach],
        leaf_of=leaf_of,root_frames=root_frame,chain_dims=chain_dims,
        adjoint_centre=cvec,adjoint_ordinary=dpart)
    data=json.dumps(witness,separators=(',',':')).encode()
    (HERE/'word.json.gz').write_bytes(gzip.compress(data,mtime=0))
'''
    new = once(new, marker, extra + marker)
    derived = out / 'producer.py'
    derived.write_text(new)
    (out / 'producer.patch').write_text(''.join(difflib.unified_diff(
        original.splitlines(True), new.splitlines(True),
        fromfile='PR110/complex_deferred.py', tofile='adapted/producer.py')))
    (out / 'adapter-source.py').write_bytes(Path(__file__).read_bytes())
    paths = [source, case/'graph.bin', case/'graph.labels', case/'matched.json', Path(__file__)]
    (out / 'SOURCE.json').write_text(json.dumps(dict(
        compiler_pin='09775e9f3fbf1900175010bcd0c3d6d1dbf65ffe',
        order=a.order, input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        derived_sha256=hashlib.sha256(new.encode()).hexdigest()),indent=2)+'\n')
    print('Running explicit deferred compile; log', out/'run.log', flush=True)
    with (out/'run.log').open('w') as log:
        subprocess.run([sys.executable,str(derived)],stdout=log,stderr=subprocess.STDOUT,check=True)
    print((out/'run.log').read_text(), flush=True)


if __name__ == '__main__':
    main()
