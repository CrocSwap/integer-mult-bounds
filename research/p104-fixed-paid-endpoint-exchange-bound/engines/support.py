"""Exact signed two-sided support for a fixed-paid endpoint exchange."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    'lead/PRICE.json':'7b0ccc8fd85240568aeddfc1e2c036ac05ab0ec6e8473522bd902a4adcc1e9eb',
    'lead/GEOMETRY.json':'f2aa238ed8c49f0633c3837c6961bfba19482385851a5606578fa6368db79542',
    'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'inputs/reverse_span.py':'f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff',
}
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
EVENTS=76466


def checked(root,name,expected=None):
    b=(root/name).read_bytes()
    assert sha256(b).hexdigest()==(expected or PINS[name]),('changed input',name)
    return b


def scaled(row,q):
    return {j:v*q for j,v in row.items() if v*q}


def add(dst,src,q):
    for j,v in src.items():
        x=dst.get(j,0)+q*v
        if x:
            dst[j]=x
        else:
            dst.pop(j,None)


def difference(left,right):
    result=left.copy()
    add(result,right,Q(-1))
    return result


def compact(row):
    return {j:str(v) for j,v in sorted(row.items())}


def parallel(value,target):
    if not value:
        return None
    first=next(iter(target))
    factor=value.get(first,0)/target[first]
    return factor if factor and scaled(target,factor)==value else None


def as_int(row):
    from math import lcm
    den=lcm(*(x.denominator for x in row.values()))
    return {j:x.numerator*(den//x.denominator) for j,x in row.items()},den


def prefix(word,keys,engine,deadline):
    req=defaultdict(list)
    for k,(i,j,_,t) in enumerate(keys):
        req[t].extend([(i,2*k),(j,2*k+1)])
    raw=engine['transpose_prefix'](word,req,2*len(keys),deadline)
    return [{j:Q(v,d) for j,v in row.items()} for row,d in raw]


def suffix(word,keys,deadline):
    n,m=word['public'],word['owned_fields']
    values=[{} for _ in range(n+m)]
    start=defaultdict(list)
    for k,(i,j,_,t) in enumerate(keys):
        start[t].extend([(i,2*k),(j,2*k+1)])
    guards=[{} for _ in range(2*len(keys))]
    begin=min(start)
    for t in range(begin,EVENTS):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError('suffix sweep cap')
        for r,k in start.get(t,()):
            values[r][k]=Q(1)
        op,d,*a=word['program'][t]
        if op=='ADD':
            add(values[d],values[a[0]],Q(a[1]))
        elif op=='COPY':
            for k,v in values[d].items():
                guards[k][n+t]=v
            values[d]=scaled(values[a[0]],Q(a[1]))
        elif op=='SCALE':
            values[d]=scaled(values[d],Q(a[0]))
        elif op in ('INIT','CLEAR'):
            values[d]={}
        else:
            assert op=='MOVE'
    for r,row in enumerate(values[:n]):
        for k,v in row.items():
            guards[k][r]=v
    return guards


def controls(engine):
    d={0:Q(1),1:Q(-1)}
    assert parallel(scaled(d,Q(-2,3)),d)==Q(-2,3)
    assert parallel({0:Q(1),1:Q(-1),2:Q(1)},d) is None
    assert engine['exact_span']([(0,({0:1},1)),(1,({1:1},1))],as_int(d))['coefficients']=={0:'1',1:'-1'}
    assert engine['exact_span']([(0,({0:1,2:1},1)),(1,({1:1},1))],as_int(d))['status']!='exact_span'
    return ['negative exact transposition scale','extra guard/output rejects','two-row basis witness','exterior axis blocks basis']


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('mode',choices=('bare','basis','controls'))
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--bare-sha')
    args=cli.parse_args()
    checked(args.root,'inputs/reverse_span.py')
    engine=run_path(str(args.root/'inputs/reverse_span.py'))
    tests=controls(engine)
    if args.mode=='controls':
        print(dumps(tests));return
    g=loads(checked(args.root,'lead/GEOMETRY.json'),object_pairs_hook=engine['unique'])
    assert g['price_sha256']==PINS['lead/PRICE.json']
    checked(args.root,'lead/PRICE.json')
    if args.mode=='bare':
        keys=g['selected']
        limit,seconds=16,25
    else:
        if args.bare_sha is None:
            cli.error('--bare-sha is required for basis mode')
        bare=loads(checked(args.root,'lead/BARE.json',args.bare_sha),object_pairs_hook=engine['unique'])
        assert bare['pins']==PINS and bare['mode']=='bare'
        keys=[r['key'] for r in sorted(bare['rows'],key=lambda r:(r['missing_own_input'],r['prefix_exterior_count'],-r['key'][3]))[:8]]
        limit,seconds=8,35
    assert 0<len(keys)<=limit
    def stop(*_):
        raise TimeoutError('hard signed support cap')
    signal(SIGALRM,stop)
    alarm(seconds)
    deadline=monotonic()+seconds-1
    results=[]
    error=None
    try:
        raw=decompress(checked(args.root,'inputs/7334-WORD.json.gz'))
        assert sha256(raw).hexdigest()==PAYLOAD
        word=loads(raw,object_pairs_hook=engine['unique'])
        assert len(word['program'])==EVENTS
        rows=prefix(word,keys,engine,deadline)
        needed=[]
        for k,(i,j,_,t) in enumerate(keys):
            a,b=rows[2*k:2*k+2]
            d={i:Q(1),j:Q(-1)}
            df=difference(a,b)
            item={'key':keys[k],'prefix_exterior_count':len(set(df)-{i,j}),
                  'missing_own_input':sum(not (r in a or r in b) for r in (i,j))}
            if args.mode=='bare':
                factor=parallel(df,d)
                item|={'prefix_factor':None if factor is None else str(factor),
                       'first_exterior':next(([x,str(df[x])] for x in sorted(df) if x not in d),None),
                       'decision':'prefix excluded' if factor is None else 'suffix pending'}
                if factor is not None:
                    needed.append((k,d,factor))
            else:
                proof=engine['exact_span']([(i,as_int(a)),(j,as_int(b))],as_int(d))
                item|={'prefix':proof,'decision':'prefix excluded' if proof['status']!='exact_span' else 'suffix pending'}
                if proof['status']=='exact_span':
                    needed.append((k,d,proof['coefficients']))
            results.append(item)
        if needed:
            columns=suffix(word,[keys[k] for k,_,_ in needed],deadline)
            for z,(k,d,witness) in enumerate(needed):
                a,b=columns[2*z:2*z+2]
                if args.mode=='bare':
                    out=difference(a,b)
                    value=parallel(out,d)
                    results[k]|={'suffix_factor':None if value is None else str(value),
                                 'decision':'bare exact support' if value==1/witness else 'suffix excluded'}
                else:
                    i,j,_,_=keys[k]
                    proof=engine['exact_span']([(i,as_int(a)),(j,as_int(b))],as_int(d))
                    results[k]['suffix']=proof
                    if proof['status']!='exact_span':
                        results[k]['decision']='suffix excluded'
                    else:
                        coefficients=proof['coefficients']
                        av=[Q(witness.get(r,'0')) for r in (i,j)]
                        bv=[Q(coefficients.get(r,'0')) for r in (i,j)]
                        det=1-sum(x*y for x,y in zip(av,bv,strict=True))
                        L=[[Q(1) if row==column else Q(0) for column in range(2)] for row in range(2)]
                        for row in range(2):
                            for column in range(2):
                                L[row][column]-=bv[row]*av[column]
                        results[k]|={'rank_one_det':str(det),'L':[[str(x) for x in row] for row in L[::-1]],
                                     'decision':'basis exact support' if det else 'singular proposed basis'}
    except TimeoutError as e:
        error=str(e)
    finally:
        alarm(0)
    out={'mode':args.mode,'pins':PINS,'caps':{'keys':limit,'seconds':seconds,'events_per_pass':EVENTS},
         'controls':tests,'rows':results,'unvisited':keys[len(results):]+[r['key'] for r in results if r['decision']=='suffix pending'],
         'timeout':error}
    if args.bare_sha:
        out['bare_sha256']=args.bare_sha
    print(dumps(out,indent=2,sort_keys=True))
    if error:
        raise SystemExit(2)


if __name__=='__main__':
    main()
