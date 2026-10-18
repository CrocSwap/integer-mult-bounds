#!/usr/bin/env python3
"""Exact integer-polynomial and separately interpreted integer-matrix checks.

Signed identities imply the same identities for real/complex linear maps;
floating arithmetic, rounding, native hosting and precision are not certified.
Apache-2.0. conorholds with substantial Codex assistance.
"""
import random
import json
from hashlib import sha256
from pathlib import Path
import families as f
import verify as v


def need(ok,message):
    if not ok:raise ValueError(message)


def polynomial(word,n,roots=2,observe=None):
    state={role:{(role,):1} for role in v.roles(n,roots)}
    for op in word:
        sign=op[-1];need(type(sign)is int and sign in (-1,1),'invalid signed orientation')
        if op[0]=='T':
            need(len(op)==4 and all(type(p)is int and 0<=p<roots for p in op[1:3])
                 and op[1]!=op[2] and 0 in op[1:3], 'invalid star transfer')
            coefficient,source,target=None,f'z{op[2]}',f'z{op[1]}'
        else:
            coefficient,source,target=v.ports(op[:-1],n,roots)
        for term,value in list(state[source].items()):
            term=term if coefficient is None else (coefficient,)+term
            updated=state[target].get(term,0)+sign*value
            if updated:state[target][term]=updated
            else:state[target].pop(term,None)
        if observe is not None:observe(target,state[target])
    return state


def check(word,n,roots=2):
    want={role:{(role,):1} for role in v.roles(n,roots)}
    for mask in range(1,1<<n):
        want[f'y{mask}'].update({(f'A{mask}',f'B{j}',f'x{j}'):1 for j in range(n) if mask&(1<<j)})
    need(polynomial(word,n,roots)==want,'signed map or dirty restoration failed')
    inverse=[op[:-1]+[-op[-1]] for op in reversed(word)]
    # Concatenate the actual inverse; each operation negates its additive shear.
    combined=polynomial(word+inverse,n,roots)
    need(combined=={role:{(role,):1} for role in v.roles(n,roots)},'signed inverse failed')


def prefix_bounds(word,n):
    """Exact generic coefficient bounds on every forward palette prefix."""
    maximum = {"coefficient_absolute_max":0, "root_dirty_l1_max":0, "output_dirty_l1_max":0}
    def observe(target,poly):
        maximum["coefficient_absolute_max"] = max(maximum["coefficient_absolute_max"],
                                                  max(map(abs,poly.values()), default=0))
        need(all(abs(value)<=1 for value in poly.values()), 'palette coefficient-height growth')
        if target.startswith('z'):
            dirty = sum(abs(poly.get((f'z{p}',),0)) for p in (0,1))
            maximum["root_dirty_l1_max"] = max(maximum["root_dirty_l1_max"], dirty)
            if target == 'z1':
                need(not any(len(term)>1 for term in poly), 'companion acquired source data')
        else:
            dirty = sum(abs(poly.get((f'A{target[1:]}',f'z{p}'),0)) for p in (0,1))
            maximum["output_dirty_l1_max"] = max(maximum["output_dirty_l1_max"], dirty)
            need(all(value==1 for term,value in poly.items() if len(term)==3),
                 'output source contribution lost positivity')
        need(dirty<=2, 'palette dirty-height growth')
    polynomial(word,n,2,observe)
    return maximum


def dense(word,incoming,maps):
    state={role:list(value) for role,value in incoming.items()}
    def image(matrix,value):return [sum(a*b for a,b in zip(row,value)) for row in matrix]
    for op in word:
        if op[0]=='B':source=f'x{op[1]}';target='z0';add=image(maps[f'B{op[1]}'],state[source])
        elif op[0]=='A':source='z0';target=f'y{op[1]}';add=image(maps[f'A{op[1]}'],state[source])
        else:source=f'z{1-op[1]}';target=f'z{op[1]}';add=state[source]
        state[target]=[a+op[-1]*b for a,b in zip(state[target],add)]
    return state


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args()
    records=[]
    for n in range(3,13):
        sizes=f.balanced_three(n);word=f.construct_signed_palette(sizes)
        check(word,n)
        counts=f.signed_palette_screen(sizes)
        for kind,key in (('A','readout_calls'),('B','source_calls'),('C','transfers')):
            need(sum(op[0]==kind for op in word)==counts[key],'unpaid signed invoice')
        records.append({'sources':n,'counts':counts,'prefix_bounds':prefix_bounds(word,n),
                        'word_sha256':sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest()})
    check(f.construct_signed_palette((1,3,1)),5)
    for n in range(1,13):
        count=min(n,4);q,r=divmod(n,count)
        sizes=tuple(q+int(i<r) for i in range(count))
        check(f.construct_signed_single(sizes),n,1)
    check(f.construct_signed_single((1,2)),3,1)
    word=f.construct_signed_palette((1,1,1));n=3
    for index in range(len(word)):
        try:check(word[:index]+word[index+1:],n)
        except ValueError:pass
        else:raise ValueError('signed omission control accepted')
    for kind in ('A','B','C'):
        changed=[list(op) for op in word];index=next(i for i,op in enumerate(changed) if op[0]==kind)
        changed[index][-1]*=-1
        try:check(changed,n)
        except ValueError:pass
        else:raise ValueError('signed inverse-direction mutation accepted')
    cases=0
    for n in (3,6):
        word=f.construct_signed_palette(f.balanced_three(n));names=v.roles(n,2);rng=random.Random(771+n)
        maps={f'{kind}{j}':[[rng.randrange(-2,3) for _ in range(2)] for _ in range(2)]
              for kind,indices in (('B',range(n)),('A',range(1,1<<n))) for j in indices}
        maps["B0"]=[[0,1],[0,0]];maps["A1"]=[[0,0],[1,0]]
        inputs=[]
        for role in names:
            for bit in range(2):
                incoming={name:[0,0] for name in names};incoming[role][bit]=1;inputs.append(incoming)
        inputs.extend({role:[rng.randrange(-3,4),rng.randrange(-3,4)] for role in names} for _ in range(8))
        for incoming in inputs:
            expected={role:list(value) for role,value in incoming.items()}
            for mask in range(1,1<<n):
                for j in range(n):
                    if mask&(1<<j):
                        b=[sum(x*y for x,y in zip(row,incoming[f'x{j}'])) for row in maps[f'B{j}']]
                        a=[sum(x*y for x,y in zip(row,b)) for row in maps[f'A{mask}']]
                        expected[f'y{mask}']=[x+y for x,y in zip(expected[f'y{mask}'],a)]
            out=dense(word,incoming,maps);need(out==expected,'independent integer matrix endpoint')
            inv=[op[:-1]+[-op[-1]] for op in reversed(word)]
            need(dense(inv,out,maps)==incoming,'independent integer matrix inverse');cases+=1
    result={'schema':'signed-triangle-v1','records':records,'integer_dense_cases':cases,
            'omission_controls':len(f.construct_signed_palette((1,1,1))),
            'sign_mutations':3,'inverse':'literal negated shears',
            'height_scope':'Exact generic forward coefficients, no numerical roundoff or physical precision/tape invoice.'}
    path=Path(__file__).resolve().parent/'SIGNED-RECEIPT.json'
    if args.write_receipt:path.write_text(json.dumps(result,indent=2)+'\n')
    else:need(json.loads(path.read_text())==result,'signed receipt differs')
    print(f'PASS_SIGNED_PALETTE generic_n=3..12 signed_one_root=1..12 integer_dense={cases} inverse=checked omissions={31} no_new_kappa')


if __name__=='__main__':main()
