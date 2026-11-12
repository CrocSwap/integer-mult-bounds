"""Exact source and coupled price census for one finished-helper promotion."""
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
CASE_CAP,SECONDS=119,20


def stop(*_):
    raise TimeoutError('20-second finished-helper price cap')


def unique(pairs):
    out=dict(pairs)
    assert len(out)==len(pairs),'duplicate JSON key'
    return out


def load_pins():
    raw,pins={},{}
    for line in (ROOT/'PINS').read_text().splitlines():
        expected,path=line.split()
        assert path not in pins
        data=(ROOT/path).read_bytes()
        assert sha256(data).hexdigest()==expected,path
        raw[path]=data
        pins[path]=expected
    return raw,pins


def exact_cases(raw):
    data={p:loads(raw['inputs/'+p+'.json'],object_pairs_hook=unique)
          for p in ('R200','R201','R203','R204','R204-FIRST12','R204-REST38')}
    assert all((data[p]['head'],data[p]['caller'])==(HEAD,CALLER)
               for p in ('R200','R201','R203','R204-FIRST12','R204-REST38'))
    case=data['R200']
    assert case['state']=='absent_exterior_coordinate' and not case['capped']
    a,m,b,r,s=case['key']
    value=case['decision']['target_coefficient']
    cases=[('R200',[a,m,b],r,s,case['bank_chart'],{str(case['decision']['coordinate']):'1'},value)]
    for p,n in (('R201',6),('R203',62)):
        assert len(data[p]['checked'])==n and not data[p]['capped']
        for case in data[p]['checked']:
            d=case['decision']
            assert d['status']=='exact_rank_exclusion' and Q(d['separated_target'])
            cases.append((p,case['clocks'],case['role'],case['peer'],case['chart'],d['separating_covector'],d['separated_target']))
    old=data['R204']
    assert not old['survivors'] and len(old['records'])==50
    first=data['R204-FIRST12']['checked']; rest=data['R204-REST38']['checked']
    assert len(first)==12 and len(rest)==38
    independent={tuple(x['clocks']):x for x in [*first,*rest]}
    assert len(independent)==50
    for case in old['records']:
        x=independent[tuple(case['clocks'])]
        d=case['separator']
        assert (case['role'],case['peer'],d['input'],d['source_value'])==(x['role'],x['peer'],x['input'],x['source_value'])
        assert Q(d['source_value'])
        cases.append(('R204',case['clocks'],case['role'],case['peer'],x['chart'],d['input'],d['source_value']))
    assert len(cases)==CASE_CAP and len({tuple(c[1]) for c in cases})==CASE_CAP
    return cases


def reduced(x,basis):
    while x:
        high=x.bit_length()-1
        if high not in basis:
            break
        x^=basis[high]
    return x


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    raw,pins=load_pins()
    body=decompress(raw['inputs/7334-WORD.json.gz'])
    assert sha256(body).hexdigest()==PAYLOAD
    w=loads(body,object_pairs_hook=unique)
    p=loads(raw['inputs/R92-PRICE.json'],object_pairs_hook=unique)
    assert (p['head'],p['caller_head'],p['word_sha256'])==(HEAD,CALLER,pins['inputs/7334-WORD.json.gz'])
    tape,frames=w['program'],w['frames']
    n=w['public']
    assert (n,w['owned_fields'],len(tape))==(1501,68,76466)
    mains=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
    assert len(mains)==400 and all(0<=r<n for r in mains)
    last={}
    for i,e in enumerate(tape):
        op,d,*args=e
        last[d]=i
        if op in ('ADD','COPY'):
            last[args[0]]=i
    @cache
    def basis(chart):
        out={}
        for v in frames[chart]:
            y=reduced(v,out)
            assert y
            out[y.bit_length()-1]=y
        return out
    def subset(a,b):
        return all(not reduced(v,basis(b)) for v in basis(a).values())
    cases=exact_cases(raw)
    cost=run_path(str(ROOT/'inputs/pricing.py'))['cost']
    k=Q(p['old_crossing_upper'])
    reports=[]
    checks=Counter()
    for group,key,owner,peer,C,dual,value in cases:
        a,m,b=key
        first,add,second=(tape[i] for i in key)
        assert first[:2]==second[:2]==['MOVE',owner] and add[:3]==['ADD',owner,peer]
        assert first[3]==add[-1]==second[2] and second[3]==C
        u,v=abs(len(basis(first[3]))-len(basis(first[2]))),abs(len(basis(C))-len(basis(second[2])))
        assert u and v and abs(len(basis(C))-len(basis(first[2])))==u+v
        options=[]
        for r_text,coefficient in sorted(dual.items(),key=lambda it:int(it[0])):
            r=int(r_text)
            assert Q(coefficient) and 0<=r<n
            checks['dual_nonzero_coordinates']+=1
            if r in mains or r==owner:
                checks['main_or_target']+=1
                continue
            A,D=w['initial'][r],w['final'][r]
            if last[r]>b:
                checks['unfinished']+=1
                continue
            d=len(basis(C))-len(basis(D))
            if d<=0 or not subset(D,C):
                checks['outside_strict_final_nesting']+=1
                continue
            t=len(basis(D))-len(basis(A))
            if t<=0 or not subset(A,D):
                checks['outside_old_proper_helper']+=1
                continue
            checks['structurally_eligible']+=1
            h=Counter((u,v,t+d));h.subtract((u+v,d,t))
            hist={j:17*z for j,z in h.items() if z}
            assert sum(hist.values())==0 and sum(j*z for j,z in hist.items())==0
            quote=cost(hist,k)
            status='positive' if quote[0]>0 else 'nonpositive' if quote[1]<=0 else 'interval_ambiguous'
            checks[status]+=1
            dominated=(max(t,d)>=max(u,v) and min(t,d)>=min(u,v))
            if dominated:
                assert status=='nonpositive'
            options.append({'donor':r,'separator_value_on_e_r':coefficient,'initial_final_promoted':[A,D,C],
                            'last_contact':last[r],'last_event':tape[last[r]],'cut':b+1,
                            'fusion_ranks':[u,v,u+v],'promotion_ranks':[t,d,t+d],
                            'signed_histogram':hist,'gross_interval':list(map(str,quote)),
                            'status':status,'uniform_deficit_dominated':dominated})
        reports.append({'group':group,'clocks':key,'owner':owner,'peer':peer,'chart':C,
                        'target_value':value,'promotion_options':options})
    ranked=sorted(((Q(o['gross_interval'][0]),x['clocks'],o['donor']) for x in reports
                   for o in x['promotion_options'] if o['status']=='positive'),key=lambda x:(-x[0],x[1],x[2]))
    assert len(ranked)==checks['positive']
    alarm(0)
    print(dumps({'head':HEAD,'caller':CALLER,'pins':pins,'payload':PAYLOAD,'case_cap':CASE_CAP,
                 'seconds_cap':SECONDS,'case_count':len(reports),'checks':checks,'reports':reports,
                 'first_positive_for_one_exact_span':ranked[0] if ranked else None,
                 'scope':'price gate grants source-row unit endpoint and all ancillary work free'},
                sort_keys=True,indent=2,default=str))


if __name__=='__main__':
    main()
