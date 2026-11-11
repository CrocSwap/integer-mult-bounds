"""Independent reverse-chart and signed scalar audit of R60 ADD contractions."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
from itertools import pairwise
import json
from pathlib import Path
import runpy
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD='9d0119eb12fbd9fa534b48cd37b68e7099757b91'
WORD='7314/WORD.json.gz'
CALLER='7113/CALLER.json'
BASE='BASE-PRICE.json'
TARIFF='7298/pricing.py'
PINS={
    WORD:'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
    CALLER:'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    BASE:'8d70669e720faabc932366dafbc1bd1fdaef6f088c4eb02b0ea3707ba309ab53',
    TARIFF:'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}
EXCLUDE={863,1355,1568}


def decode(raw):
    def unique(pairs):
        obj=dict(pairs)
        assert len(obj)==len(pairs),'duplicate JSON key'
        return obj
    return json.loads(raw,object_pairs_hook=unique)


def save(out,name,record):
    tmp=out/(name+'.tmp')
    tmp.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    tmp.replace(out/name)


def frames(word):
    @cache
    def span(f):
        result={0}
        for bit in word['frames'][f]:
            assert bit not in result
            result|={x^bit for x in result}
        return result

    @cache
    def directed(a,b,owned):
        if a==b:
            return 0
        x,y=span(a),span(b)
        if x<y or owned and y<x:
            return abs(len(word['frames'][a])-len(word['frames'][b]))
        return None
    return directed


def structure(program,public,deadline):
    previous=[]
    stock,public_diagnostics=[],[]
    inspected=Counter()
    for i,e in enumerate(program):
        if monotonic()>=deadline:
            return stock,public_diagnostics,inspected,i
        if e[0]=='MOVE':
            continue
        previous=(previous+[i])[-3:]
        if len(previous)!=3:
            continue
        inspected['normalized_windows']+=1
        events=[program[t] for t in previous]
        if any(x[0]!='ADD' for x in events):
            continue
        inspected['all_add_triples']+=1
        if len({x[-1] for x in events})<2:
            continue
        inspected['cross_chart']+=1
        roles=set(x for row in events for x in row[1:3])
        if len(roles)!=3:
            continue
        inspected['exactly_three_roles']+=1
        if roles&EXCLUDE:
            continue
        edge={tuple(row[1:3]):t for t,row in zip(previous,events,strict=True)}
        if len(edge)!=3:
            continue
        chains=[]
        for (i_role,j),x in edge.items():
            for (k_role,l),y in edge.items():
                if k_role==j and (i_role,l) in edge and len({i_role,j,l})==3:
                    chains.append((i_role,j,l,x,y,edge[i_role,l]))
        if not chains:
            continue
        assert len(chains)==1
        inspected['directed_triangles']+=1
        i_role,j,k,x,y,z=chains[0]
        old_first,old_last=previous[0],previous[-1]
        surviving=sorted((x,y),reverse=True)
        slots=sorted((x,y))
        destination = stock if j>=public else public_diagnostics
        destination.append(dict(clocks=previous,roles=sorted(roles),middle=j,chain_roles=[i_role,j,k],
                                x=x,y=y,correction=z,new_order=surviving,new_scalar_slots=slots,
                                first=old_first,last=old_last))
    return stock,public_diagnostics,inspected,None


def reverse_charts(word,stock,directed,deadline):
    tape=word['program']
    charts=word['final']+[None]*word['owned_fields']
    public=word['public']
    enter,leave=defaultdict(list),defaultdict(list)
    for n,row in enumerate(stock):
        enter[row['first']].append(n)
        leave[row['last']].append(n)
    entries,exits={},{}
    paid=Counter()
    for i in range(len(tape)-1,-1,-1):
        if monotonic()>=deadline:
            return entries,exits,paid,i
        for n in leave.get(i,()):
            exits[n]={r:charts[r] for r in stock[n]['roles']}
        op,d,*args=tape[i]
        if op=='MOVE':
            a,b,owned=args
            assert owned==(d>=public) and charts[d]==b
            size=directed(a,b,owned)
            assert size
            paid[size]+=1
            charts[d]=a
        elif op in ('INIT','CLEAR'):
            f,=args
            assert d>=public and charts[d]==(f if op=='INIT' else None)
            charts[d]=None if op=='INIT' else f
        else:
            assert op in ('ADD','COPY','SCALE') and Q(args[-2])
            assert charts[d]==args[-1]
            if op in ('ADD','COPY'):
                s=args[0]
                assert s!=d and charts[s]==args[-1]
                if op=='COPY':
                    assert d>=public
        for n in enter.get(i,()):
            entries[n]={r:charts[r] for r in stock[n]['roles']}
    assert charts==word['initial']+[None]*word['owned_fields']
    return entries,exits,paid,None


def window_geometry(program,case,entry,exit_,public,directed):
    touched=set(case['roles'])
    assert set(entry)==set(exit_)==touched and None not in (*entry.values(),*exit_.values())
    old,retained=Counter(),[]
    for t in range(case['first'],case['last']+1):
        op,r,*rest=program[t]
        if op!='MOVE':
            assert t in case['clocks'] and op=='ADD'
            continue
        if r in touched:
            size=directed(*rest)
            assert size
            old[size]+=1
        else:
            retained.append(t)

    requests=defaultdict(list)
    for source,slot in zip(case['new_order'],case['new_scalar_slots'],strict=True):
        _,d,s,_,f=program[source]
        requests[d].append((slot,'before_add',f))
        requests[s].append((slot,'before_add',f))
    new=Counter()
    moves=[]
    invalid=[]
    for r in sorted(touched):
        route=[(case['first'],'entry',entry[r]),*requests[r],(case['last'],'exit',exit_[r])]
        for (_,_,a),(clock,at,b) in pairwise(route):
            owned=r>=public
            size=directed(a,b,owned)
            if size is None:
                invalid.append(dict(role=r,from_chart=a,to_chart=b,clock=clock,anchor=at))
            elif size:
                new[size]+=1
                moves.append(dict(clock=clock,anchor=at,event=['MOVE',r,a,b,owned],rank=size))
    delta=new.copy()
    delta.subtract(old)
    return dict(old_paid=dict(old),new_paid=dict(new),paid_delta_per_copy={r:n for r,n in delta.items() if n},
                retained_unrelated_move_clocks=retained,proposed_touched_moves=moves,
                invalid_edges=invalid,legal=not invalid)


def product(program,clocks,roles):
    location={r:i for i,r in enumerate(roles)}
    rows=[[Q(i==j) for j in range(3)] for i in range(3)]
    for t in clocks:
        op,d,s,q,_=program[t]
        assert op=='ADD' and d!=s
        a,b=location[d],location[s]
        value=Q(q)
        rows[a]=[u+value*v for u,v in zip(rows[a],rows[b],strict=True)]
    return rows


def identity(program,row):
    old=product(program,row['clocks'],row['roles'])
    new=product(program,row['new_order'],row['roles'])
    for i,(a,b) in enumerate(zip(old,new,strict=True)):
        for j,(x,y) in enumerate(zip(a,b,strict=True)):
            if x!=y:
                return dict(equal=False,first_defect=[i,j,str(x),str(y)])
    return dict(equal=True,matrix=[[str(v) for v in r] for r in old])


def controls():
    word=dict(public=2,owned_fields=1,frames=[[],[1]],initial=[0,1],final=[1,1],program=[
        ['INIT',2,0],['ADD',0,2,'2',0],['MOVE',2,0,1,True],
        ['ADD',2,1,'-3/2',1],['MOVE',0,0,1,False],['ADD',0,1,'-3',1],['CLEAR',2,1]])
    d=frames(word)
    tape=word['program']
    stock,outside,_,cap=structure(tape,2,float('inf'))
    assert len(stock)==1 and not outside and cap is None
    entries,exits,paid,cap=reverse_charts(word,stock,d,float('inf'))
    assert cap is None and paid=={1:2}
    g=window_geometry(tape,stock[0],entries[0],exits[0],2,d)
    assert g['legal'] and g['old_paid']=={1:2} and g['new_paid']=={1:4}
    assert identity(tape,stock[0])['equal']
    bad=tape.copy()
    bad[5]=['ADD',0,1,'3',1]
    assert not identity(bad,stock[0])['equal']
    blocked=entries[0] | {0:1}
    assert not window_geometry(tape,stock[0],blocked,exits[0],2,d)['legal']
    return ['exact_signed_correction_and_two_old_four_new_moves','wrong_correction_sign_rejected',
            'public_descent_rejected','reverse_entry_exit_and_ownership']


def load(root):
    raw={}
    for rel,h in PINS.items():
        raw[rel]=(root/rel).read_bytes()
        assert sha256(raw[rel]).hexdigest()==h,('changed input',rel)
    return raw


def run(root,out,primary,primary_sha,cap,seconds,start):
    # The completed lead price must already exist. The independent engine
    # authenticates it but never reads its decisions or geometry.
    lead=primary.read_bytes()
    assert sha256(lead).hexdigest()==primary_sha,'changed primary price'
    assert decode(lead)['head']==HEAD,'primary price uses wrong comparator'
    controls_result=controls()
    raw=load(root)
    word=decode(gzip.decompress(raw[WORD]))
    c=decode(raw[CALLER])
    old=decode(raw[BASE])
    assert [e[1] for e in c['events'] if e[0]=='J']==list(range(1,18))
    assert old['head']==HEAD and old['copies']==17
    tape=word['program']
    cost=runpy.run_path(str(root/TARIFF))['cost']
    k=Q(old['crossing_upper'])
    paid,targets=(Counter({int(r):v for r,v in old[name].items()}) for name in ('paid','targets'))
    assert (sum(paid.values()),sum(targets.values()))==(110536,22461)
    net=targets.copy()
    net.subtract(paid)
    baseline=cost(net,k)
    assert list(map(str,baseline))==old['old_margin']
    deadline=start+min(28,seconds-1)
    structural,public_diagnostics,visited,unknown=structure(tape,word['public'],deadline)
    d=frames(word)
    bounded=structural[:cap]
    entries,exits,old_native,chart_cap=reverse_charts(word,bounded+public_diagnostics,d,deadline)
    if chart_cap is None:
        assert sum(old_native.values())==6280 and len(tape)==76461

    @cache
    def quote(key):
        delta=dict(key)
        signed=net.copy()
        signed.subtract({r:n*17 for r,n in delta.items()})
        return list(map(str,cost(signed,k)))

    rows=[]
    for n,row in enumerate(bounded):
        if monotonic()>=deadline or n not in entries or n not in exits:
            break
        geom=window_geometry(tape,row,entries[n],exits[n],word['public'],d)
        row=dict(row,entry=entries[n],exit=exits[n],geometry=geom)
        if geom['legal']:
            row['complete_margin_interval']=quote(tuple(sorted(geom['paid_delta_per_copy'].items())))
        rows.append(row)

    remaining=structural[len(rows):]
    unresolved=[]
    for row in remaining:
        removed=sum(abs(len(word['frames'][e[3]])-len(word['frames'][e[2]]))
                    for e in tape[row['first']:row['last']+1] if e[0]=='MOVE' and e[1] in row['roles'])
        unresolved.append(dict(clocks=row['clocks'],complete_margin_upper=str(baseline[1]+17*removed)))
    diagnostics=[]
    for n,row in enumerate(public_diagnostics,len(bounded)):
        datum=dict(row,literal_adds=[tape[t] for t in row['clocks']],
                   owned_roles=[r for r in row['roles'] if r>=word['public']])
        if n in entries and n in exits:
            datum.update(entry=entries[n],exit=exits[n],
                         geometry=window_geometry(tape,row,entries[n],exits[n],word['public'],d))
        diagnostics.append(datum)
    save(out,'GEOMETRY.json',dict(head=HEAD,pins=PINS,primary_price_sha256=primary_sha,
        baseline_interval=list(map(str,baseline)),structural_filter_counts=dict(visited),
        excluded_public_middle_diagnostics=diagnostics,
        structural_count=len(structural),geometry_checked=len(rows),unknown_inventory_clock=unknown,
        reverse_unvisited_clock=chart_cap,old_native_paid_histogram=dict(old_native),
        rows=rows,unresolved_geometry=unresolved,seconds_cap=seconds,typed_cap=cap))

    decisions=[]
    for row in rows:
        if monotonic()>=deadline:
            break
        equal=identity(tape,row)
        positive=row['geometry']['legal'] and Q(row['complete_margin_interval'][0])>0
        decisions.append(dict(clocks=row['clocks'],identity=equal,legal_geometry=row['geometry']['legal'],
                              paid_delta_per_copy=row['geometry']['paid_delta_per_copy'],
                              positive_directed_lower=positive,
                              status='support_only' if equal['equal'] and positive else
                                     'wrong_product' if not equal['equal'] else
                                     'illegal_geometry' if not row['geometry']['legal'] else 'no_positive_lower'))
    save(out,'RESULT.json',dict(head=HEAD,pins=PINS,controls=controls_result,
        geometry_sha256=sha256((out/'GEOMETRY.json').read_bytes()).hexdigest(),
        counts=dict(Counter(r['status'] for r in decisions)),rows=decisions,
        unresolved=[r['clocks'] for r in rows[len(decisions):]]+[r['clocks'] for r in unresolved],
        unknown_inventory_clock=unknown,reverse_unvisited_clock=chart_cap,
        scope_exhausted=unknown is None and chart_cap is None and len(decisions)==len(structural),
        surviving=[r['clocks'] for r in decisions if r['status']=='support_only']))


def main():
    p=ArgumentParser()
    p.add_argument('inputs',type=Path,nargs='?',default=Path(__file__).resolve().parent/'inputs')
    p.add_argument('out',type=Path,nargs='?')
    p.add_argument('--primary-price',type=Path)
    p.add_argument('--primary-price-sha')
    p.add_argument('--cap',type=int,default=128,choices=range(1,129),metavar='1..128')
    p.add_argument('--seconds',type=int,default=30,choices=range(3,31),metavar='3..30')
    p.add_argument('--controls-only',action='store_true')
    a=p.parse_args()
    if a.controls_only:
        print(json.dumps(controls()))
        return
    if a.out is None or a.primary_price is None or a.primary_price_sha is None:
        p.error('fresh output and exact saved primary price required')
    a.out.mkdir()

    def timeout(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,timeout)
    alarm(a.seconds)
    try:
        run(a.inputs,a.out,a.primary_price,a.primary_price_sha,a.cap,a.seconds,monotonic())
    except TimeoutError:
        save(a.out,'TIMEOUT.json',dict(head=HEAD,pins=PINS,status='hard_timeout',seconds_cap=a.seconds))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__=='__main__':
    assert __debug__
    main()
