"""Complete mixed-port invoice and ordinary cost, adapted from #6917.

DreamingOfClouds' root/caller accounting; composition by @CubeJerry with
substantial OpenAI assistance. No unchanged scalar or precision cap is reused.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from linear import main_roles, need


def census(word):
    d = list(map(len, word['frames']))
    main = main_roles(word)
    return (Counter(d[b]-d[a] for r,(a,b) in enumerate(zip(word['initial'],word['final'])) if r not in main),
            Counter(abs(d[e[3]]-d[e[2]]) for e in word['program'] if e[0]=='MOVE'))


def caller_invoice(word, caller):
    h, p = census(word)
    t, paid = Counter(), Counter()
    counts = {ty:len(meta['ports']) for ty,meta in caller['types'].items()}
    hosts = 0
    for e in caller['events']:
        if e[0]=='J':
            hosts += 1; t.update(h); paid.update(p)
        elif e[1]=='QUERY': paid[1] += counts[e[0]]
        elif e[1]=='IDLE_ONE': paid[8*len(e[3])] += counts[e[0]]
        else: need(e[1] in ('ADD','SCALE','SWAP','LAMBDA'), 'Known caller operation')
    for ty,meta in caller['types'].items():
        for exponent,zero,*mask in meta['diagonal']:
            t[int(exponent%2)+8*sum(mask)] += counts[ty]
    need(hosts==18, 'Eighteen joint calls')
    return t, paid


def root_invoice(word, roots):
    t, p = Counter(), Counter()
    for root,ports in roots:
        hosted = Counter()
        for role in range(root['n']):
            stages=[k for k,s in enumerate(root['stages']) if role in s['mask']]
            active=[k for k in stages if any(Q(root['Y'][u][role]) for u in root['stages'][k]['units'])]
            t[8*len(stages)+1] += ports
            hosted.update(active)
            run,prev=0,None
            for k in stages:
                if k in active:
                    if run: p[8*run] += ports
                    run,prev=0,None; continue
                if prev is not None and k==prev+1: run+=1
                else:
                    if run: p[8*run] += ports
                    run=1
                prev=k
            if run: p[8*run] += ports
        for k,s in enumerate(root['stages']):
            u,v=s['units']
            dot=lambda a,b:sum(Q(x)*Q(y) for x,y in zip(a,b))
            planes=2 if dot(root['Y'][u],root['X'][v])==dot(root['Y'][v],root['X'][u])==0 else 1
            p[8] += ports*max(0,hosted[k]-2*planes)
        p[1] += ports*(root['N']-sum(len(s['units']) for s in root['stages']))
    h,local=census(word)
    t.update({r:18*n for r,n in h.items()}); p.update({r:18*n for r,n in local.items()})
    return +t,+p


def crossing(t,p):
    with localcontext() as ctx:
        ctx.prec=60
        ranks=sorted(set(t)|set(p)); logs={r:Decimal(r).ln() for r in ranks}
        def moment(k): return sum(Decimal(t[r]-p[r])*(logs[r]*(1-k)).exp() for r in ranks)
        lo,hi=Decimal('.003'),Decimal('.005')
        need(moment(lo)>0 and moment(hi)<0, 'Root bracket')
        for _ in range(180):
            mid=(lo+hi)/2
            if moment(mid)>0: lo=mid
            else: hi=mid
        return str(lo)


def ordinary_bound(word,caller,ledger):
    counts={ty:len(meta['ports']) for ty,meta in caller['types'].items()}
    need(set(caller['types']['A']['ports'])==set(word['hosted']['Dports']), 'Caller/native port binding')
    need(set(caller['types']['B']['ports'])==set(range(len(word['ports'])))-set(word['hosted']['Dports']), 'Hosted complement binding')
    swap=lambda axes:len(set(axes)-set(range(len(axes))))
    rest=0; lambdas=0
    for ty,meta in caller['types'].items():
        ports=counts[ty]; events=[e for e in caller['events'] if e[0] in ('J',ty)]
        main_maps=idle_maps=query_maps=queries=0
        for exponent,zero,*mask in meta['diagonal']:
            axes=([0] if exponent else [])+[a for st,on in enumerate(mask,1) if on for a in range(9+8*(st-1),9+8*st)]
            main_maps+=ports*(2*swap(axes)+2*bool(exponent)+int(exponent==-1))
        for e in events:
            if e[0]=='J': continue
            if e[1]=='IDLE_ONE':
                axes=[a for st in e[3] for a in range(9+8*(st-1),9+8*st)]
                idle_maps+=ports*2*swap(axes)
            elif e[1]=='QUERY': queries+=1; query_maps+=ports*(2+int(e[4]==-1))
            elif e[1]=='LAMBDA': lambdas+=ports
        rest+=32*meta['roles']*ports*len(events)+16*queries*ports+26*meta['roles']*ports+1000*(main_maps+idle_maps+query_maps)
    nA=counts['A']; total=sum(counts.values())
    routes=(sum(ledger['paid'].values())+2*sum(ledger['helpers'].values())+6*total+6*nA+4*ledger['owned_lifetimes'])*1000
    raw=18*(ledger['scalar_upper']+routes)+rest
    return dict(caller_rest=rest,routes_per_call=routes,raw_reviewed_upper=raw,
                lambda_extra=1000*lambdas,full_ordinary_upper=raw+1000*lambdas,
                margin_under_billion=10**9-raw-1000*lambdas)
