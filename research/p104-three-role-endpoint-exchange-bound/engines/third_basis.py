"""Exact three-role prefix and guarded suffix checks on frozen R148 segments."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from math import lcm
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
 'lead/PRICE.json':'8b71d05eddb3aee641ffa41a57a3922292bc4d45c5eb8aae8f2e4514388f6524',
 'lead/IMPULSE.json':'d7b30091bd881711f4de7339216368ef8de1649e35cddb00d4dd29be2185b3af',
 'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
 'inputs/reverse_span.py':'f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff',
}
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
EVENTS=76466


def checked(root,name,pin=None):
    b=(root/name).read_bytes()
    assert sha256(b).hexdigest()==(pin or PINS[name]),('changed dependency',name)
    return b


def key(row):
    i,j,c,_,_=row['range']
    return [i,j,1454,c,row['segment']['last']]


def selection(prior):
    assert prior['price_sha256']==PINS['lead/PRICE.json']
    assert prior['counts']=={'no coframe':3961,'prefix pending':16494}
    all_keys=[key(r) for r in prior['unresolved']]
    assert len(set(map(tuple,all_keys)))==15
    return sorted(all_keys,key=lambda r:(r[0]!=232,-r[-1],r[0],r[3]))


def direction(roles):
    return {roles[0]:1,roles[1]:-1},1


def to_int(row):
    d=lcm(*(v.denominator for v in row.values()))
    return {i:v.numerator*(d//v.denominator) for i,v in row.items()},d


def prefix(word,keys,engine,deadline):
    demands=defaultdict(list)
    for k,row in enumerate(keys):
        for j,r in enumerate(row[:3]):
            demands[row[-1]].append((r,3*k+j))
    rows=engine['transpose_prefix'](word,demands,3*len(keys),deadline)
    return [(r,engine['exact_span'](list(zip(r[:3],rows[3*k:3*k+3],strict=True)),direction(r[:3])))
            for k,r in enumerate(keys)]


def add(row,source,q):
    for j,v in source.items():
        x=row.get(j,0)+q*v
        if x:
            row[j]=x
        else:
            row.pop(j,None)


def suffix(word,keys,deadline):
    n,m=word['public'],word['owned_fields']
    values=[{} for _ in range(n+m)]
    starts=defaultdict(list)
    columns=[{} for _ in range(3*len(keys))]
    for k,row in enumerate(keys):
        for j,r in enumerate(row[:3]):
            starts[row[-1]].append((r,3*k+j))
    for t in range(min(starts),EVENTS):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError('guarded suffix cap')
        for r,i in starts.get(t,()):
            values[r][i]=Q(1)
        op,d,*a=word['program'][t]
        if op=='ADD':
            add(values[d],values[a[0]],Q(a[1]))
        elif op=='COPY':
            for j,v in values[d].items():
                columns[j][n+t]=v
            values[d]={j:Q(a[1])*v for j,v in values[a[0]].items()}
        elif op=='SCALE':
            values[d]={j:Q(a[0])*v for j,v in values[d].items()}
        elif op in ('INIT','CLEAR'):
            values[d]={}
        else:
            assert op=='MOVE'
    for r,row in enumerate(values[:n]):
        for j,v in row.items():
            columns[j][r]=v
    return columns


def local_basis(roles,a,b):
    a=[Q(a.get(r,'0')) for r in roles]
    b=[Q(b.get(r,'0')) for r in roles]
    d=1-sum(x*y for x,y in zip(a,b,strict=True))
    rows=[[Q(i==j)-b[i]*a[j] for j in range(3)] for i in range(3)]
    rows[0],rows[1]=rows[1],rows[0]
    return d,[[str(q) for q in row] for row in rows]


def controls(engine):
    roles=(2,3,7)
    a,b={2:'1',3:'-1'},{2:'1',3:'-1'}
    assert local_basis(roles,a,b)==(Q(-1),[['1','0','0'],['0','1','0'],['0','0','1']])
    assert local_basis(roles,{2:'1'},{2:'1'})[0]==0
    assert engine['exact_span']([(2,({2:1},1)),(3,({3:1},1)),(7,({7:1},1))],direction(roles))['status']=='exact_span'
    return ['three-role bare exchange control','rank-one determinant zero control','exact three-row membership']


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('mode',choices=('prefix','suffix','controls'))
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--prefix-sha')
    args=cli.parse_args()
    checked(args.root,'inputs/reverse_span.py')
    engine=run_path(str(args.root/'inputs/reverse_span.py'))
    tests=controls(engine)
    if args.mode=='controls':
        print(dumps(tests));return
    prior=loads(checked(args.root,'lead/IMPULSE.json'),object_pairs_hook=engine['unique'])
    checked(args.root,'lead/PRICE.json')
    all_keys=selection(prior)
    chosen=all_keys[:8]
    pending=all_keys[8:]
    limit=25
    if args.mode=='suffix':
        assert args.prefix_sha is not None
        pre=loads(checked(args.root,'lead/PREFIX.json',args.prefix_sha),object_pairs_hook=engine['unique'])
        assert pre['mode']=='prefix' and pre['pins']==PINS
        positive=[r for r in pre['rows'] if r['proof']['status']=='exact_span']
        chosen=[r['key'] for r in positive[:4]]
        pending=[r['key'] for r in positive[4:]]
        assert chosen
        limit=35
    def stop(*_):
        raise TimeoutError('hard exact support cap')
    signal(SIGALRM,stop)
    alarm(limit)
    deadline=monotonic()+limit-1
    result={'mode':args.mode,'pins':PINS,'controls':tests,'selected':chosen,'unvisited':pending,'runner_cap':limit}
    rows=[]
    try:
        raw=decompress(checked(args.root,'inputs/7334-WORD.json.gz'))
        assert sha256(raw).hexdigest()==PAYLOAD
        word=loads(raw,object_pairs_hook=engine['unique'])
        assert len(word['program'])==EVENTS
        if args.mode=='prefix':
            rows=[{'key':r,'proof':proof} for r,proof in prefix(word,chosen,engine,deadline)]
        else:
            cols=suffix(word,chosen,deadline)
            for k,r in enumerate(chosen):
                bank=[(role,to_int(cols[3*k+j])) for j,role in enumerate(r[:3])]
                proof=engine['exact_span'](bank,direction(r[:3]))
                row={'key':r,'proof':proof}
                if proof['status']=='exact_span':
                    a=positive[k]['proof']['coefficients']
                    b=proof['coefficients']
                    det,L=local_basis(r[:3],a,b)
                    row|={'det':str(det),'L':L,'basis_status':'exact normalized support' if det else 'singular chosen witness'}
                rows.append(row)
    except TimeoutError as e:
        result|={'timeout':str(e),'unvisited':pending+chosen[len(rows):]}
    finally:
        alarm(0)
    result|={'rows':rows,'counts':Counter(r['proof']['status'] for r in rows)}
    if args.prefix_sha:
        result['prefix_sha256']=args.prefix_sha
    print(dumps(result,indent=2,sort_keys=True))
    if 'timeout' in result:
        raise SystemExit(2)


if __name__=='__main__':
    main()
