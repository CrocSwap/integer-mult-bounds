#!/usr/bin/env python3
"""Generic dirty-cache identities plus separately interpreted matrix controls.

Apache-2.0. conorholds with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
import cache_family as c
import families as f
import verify_signed as s


def require(ok,message):
    if not ok:raise ValueError(message)


def independent_dense(word,incoming,maps,modulus=None):
    """No polynomial interpreter, shared port decoder, or cache constructor logic."""
    state={key:list(value) for key,value in incoming.items()}
    def image(matrix,value):
        return [sum(a*b for a,b in zip(row,value)) for row in matrix]
    for op in word:
        require(isinstance(op,list) and len(op)==4 and type(op[-1]) is int
                and op[-1] in (-1,1),'bad dense instruction')
        if op[0] in ('A','B'):
            require(op[2]==0,'operator used a cache port')
            if op[0]=='A':source='z0';target=f'y{op[1]}'
            else:source=f'x{op[1]}';target='z0'
            add=image(maps[f'{op[0]}{op[1]}'],state[source])
        elif op[0]=='T':
            require(op[1]!=op[2] and 0 in op[1:3],'non-star dense transfer')
            source=f'z{op[2]}';target=f'z{op[1]}';add=state[source]
        else:raise ValueError('unknown dense opcode')
        out=[a+op[-1]*b for a,b in zip(state[target],add)]
        state[target]=out if modulus is None else [a%modulus for a in out]
    return state


def dense_controls():
    cases=0
    for n in (1,3,6):
        word=c.construct(n);inverse=[op[:-1]+[-op[-1]] for op in reversed(word)]
        names=[f'x{j}' for j in range(n)]+[f'y{m}' for m in range(1,1<<n)]+[f'z{j}' for j in range(n+1)]
        for width in (1,2,3):
            for modulus in (None,2):
                rng=random.Random(6011+100*n+10*width+(modulus or 0))
                maps={f'{kind}{i}':[[rng.randrange(-2,3) for _ in range(width)] for _ in range(width)]
                      for kind,indices in (('A',range(1,1<<n)),('B',range(n))) for i in indices}
                if width>1:
                    maps['B0']=[[int(i==0 and j==1) for j in range(width)] for i in range(width)]
                    maps['A1']=[[int(i==1 and j==0) for j in range(width)] for i in range(width)]
                inputs=[]
                for name in names:
                    for column in range(width):
                        incoming={role:[0]*width for role in names};incoming[name][column]=1;inputs.append(incoming)
                for _ in range(8):
                    inputs.append({role:[rng.randrange(2) if modulus else rng.randrange(-3,4)
                                         for _ in range(width)] for role in names})
                for incoming in inputs:
                    expected={key:list(value) for key,value in incoming.items()}
                    for mask in range(1,1<<n):
                        for j in range(n):
                            if mask&(1<<j):
                                b=[sum(a*x for a,x in zip(row,incoming[f'x{j}'])) for row in maps[f'B{j}']]
                                ab=[sum(a*x for a,x in zip(row,b)) for row in maps[f'A{mask}']]
                                expected[f'y{mask}']=[a+x for a,x in zip(expected[f'y{mask}'],ab)]
                        if modulus:expected[f'y{mask}']=[a%modulus for a in expected[f'y{mask}']]
                    out=independent_dense(word,incoming,maps,modulus)
                    require(out==expected,'independent dirty-cache endpoint')
                    require(independent_dense(inverse,out,maps,modulus)==incoming,'independent dirty-cache inverse')
                    cases+=1
    return cases


def path_controls():
    cases=0
    for n in range(1,6):
        for a in range(1<<n):
            for b in range(1<<n):
                if (a^b).bit_count()&1:
                    vertices=c.path(range(n),a,b)
                    require(vertices[0]==a and vertices[-1]==b and
                            set(vertices)==set(range(1<<n)) and len(vertices)==1<<n and
                            all((x^y).bit_count()==1 for x,y in zip(vertices,vertices[1:])),
                            'Hamiltonian path control')
                    cases+=1
    vertices=c.path((0,2,5),128,128+1+4+32)
    require(set(vertices)=={128+a+4*b+32*d for a in (0,1) for b in (0,1) for d in (0,1)},
            'sparse cube coordinate control')
    for args in (((),0,1),((0,1),0,3),((0,0),0,1),((0,),0,3),((-1,),0,1),
                 ((True,),0,1),((0,),True,1),((0,),-1,0)):
        try:c.path(*args)
        except ValueError:pass
        else:raise ValueError('invalid path accepted')
    return cases+1


def prefix_bounds(word,n):
    maximum={'coefficient_absolute_max':0,'parent_dirty_l1_max':0,'output_dirty_l1_max':0}
    def observe(target,poly):
        height=max(map(abs,poly.values()),default=0)
        require(height<=1,'cache coefficient height exceeded one')
        maximum['coefficient_absolute_max']=max(maximum['coefficient_absolute_max'],height)
        if target.startswith('z'):
            dirt=sum(abs(poly.get((f'z{j}',),0)) for j in range(n+1));key='parent_dirty_l1_max'
        else:
            dirt=sum(abs(poly.get((f'A{target[1:]}',f'z{j}'),0)) for j in range(n+1));key='output_dirty_l1_max'
        require(dirt<=n+1,'cache dirty norm exceeded row count')
        maximum[key]=max(maximum[key],dirt)
    s.polynomial(word,n,n+1,observe)
    return maximum


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-receipt',action='store_true');args=parser.parse_args()
    records=[]
    for n in range(1,13):
        word=c.construct(n);s.check(word,n,n+1)
        require(all(op[2]==0 for op in word if op[0] in ('A','B')),'physical child port changed')
        records.append({'sources':n,'counts':c.counts(n),'prefix_bounds':prefix_bounds(word,n),
                        'word_sha256':sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest()})
    word=c.construct(3)
    for i in range(len(word)):
        try:s.check(word[:i]+word[i+1:],3,4)
        except ValueError:pass
        else:raise ValueError('cache omission accepted')
    for kind in ('A','B','T'):
        altered=[list(op) for op in word];i=next(j for j,op in enumerate(altered) if op[0]==kind);altered[i][-1]*=-1
        try:s.check(altered,3,4)
        except ValueError:pass
        else:raise ValueError('cache sign mutation accepted')
    for kind in ('A','B'):
        altered=[list(op) for op in word];i=next(j for j,op in enumerate(altered) if op[0]==kind);altered[i][2]=1
        try:s.check(altered,3,4)
        except ValueError:pass
        else:raise ValueError('cache child-port mutation accepted')
    for op in (['T',1,1,1],['T',1,2,1],['T',0,4,1],['T',0,True,1],['T',0,1,0],['T',0,1,1,1]):
        try:s.polynomial([op],3,4)
        except ValueError:pass
        else:raise ValueError('invalid star transfer accepted')
    for n in (0,-1,True,2.5):
        try:c.construct(n)
        except ValueError:pass
        else:raise ValueError('invalid source count accepted')
    for prices in ((0,1,1),(1,0,1),(1,1,-1)):
        try:c.screen(3,*prices)
        except ValueError:pass
        else:raise ValueError('invalid cache tariff accepted')
    require(c.screen(3,1,1,0)['relative_gap_to_any_root_lower_bound']=='0','zero-transfer limit')
    result={'schema':'paid-dirty-star-cache-v1','records':records,'path_cases':path_controls(),
            'independent_dense_cases':dense_controls(),'fields':['integers','F2'],
            'omission_controls':len(word),'sign_controls':3,'child_port_controls':2,'invalid_transfer_controls':6,
            'cost_examples':[c.screen(n,f.critical_tariff(n),1,Fraction(1,n*n)) for n in (9,12,15,18,30,60)],
            'fixed_quarter_transfer_examples':[c.screen(n,f.critical_tariff(n),1,Fraction(1,4))
                                              for n in (12,15,18,30,60)],
            'scope':'n+1 arbitrary dirty parent rows; paid full-row star transfers. Query tariffs only; no physical hosting, roundoff or kappa claim.'}
    target=Path(__file__).resolve().parent/'CACHE-RECEIPT.json'
    if args.write_receipt:target.write_text(json.dumps(result,indent=2)+'\n')
    else:require(json.loads(target.read_text())==result,'cache receipt mismatch')
    print(f"PASS_PAID_DIRTY_CACHE generic_n=1..12 paths={result['path_cases']} integer_F2_dense={result['independent_dense_cases']} inverse=checked omissions={len(word)} roots=n+1 no_new_kappa")


if __name__=='__main__':main()
