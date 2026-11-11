"""Price and exact body-one isolation for the two Type A rank-137 roots."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import runpy
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
CALLER_HEAD = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
SOURCE = 'round30/complex/source/inputs/'
PINS = {
    SOURCE+'WORD.json.gz': '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
    SOURCE+'CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    SOURCE+'EARLY-RESULT.json': '691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7',
    '7298/RESULT.json': 'aaf594b981f37e7dbddb12fd052d9286cf5c8c95c8d5265ab6426408f6e58cc5',
    '7298/verify.py': '4a4291c9019ef23c664ae9646b076dc57054b49f5c5ffd21908aa9f0edf19902',
    '7298/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'r52/projector.py': 'acc29bb66913fd7ba0baef848805f5ab64bea5428f5225397aac5d84a1f9fadd',
    '7113/check_odd_caller_exact_grid.py': 'abd5a5fd011b71e5b382cbc058855594d4f2fe7b049f375506675c0303180f54',
    '7113/check_odd_physical_binding.py': '5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98',
}
ROOTS = (0,18)


def decode(raw):
    def unique(pairs):
        result = dict(pairs)
        assert len(result) == len(pairs), 'duplicate JSON key'
        return result
    return json.loads(raw,object_pairs_hook=unique)


def save(out,name,obj):
    tmp = out/(name+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    tmp.replace(out/name)


def authenticate(root):
    files = {}
    for name,h in PINS.items():
        raw = (root/name).read_bytes()
        assert sha256(raw).hexdigest()==h, ('changed input',name)
        files[name] = raw
    return files


def partitions(stages):
    return [(m,c,8*m+c,8*(stages-m)+1-c,comb(stages,m))
            for m in range(stages+1) for c in (0,1)
            if 8*m+c and 8*(stages-m)+1-c]


def price(root, files, out):
    word = decode(gzip.decompress(files[SOURCE+'WORD.json.gz']))
    c = decode(files[SOURCE+'CALLER.json'])
    early = decode(files[SOURCE+'EARLY-RESULT.json'])
    predecessor = runpy.run_path(str(root/'7298/verify.py'))
    replay = predecessor['complex_scan'](word,c,early)
    assert json.loads(json.dumps(replay))==decode(files['7298/RESULT.json'])['complex']
    k = Q(replay['probe'])
    assert replay['copies']==17 and k==Q(early['price']['independent_raw_bracket'][1])
    paid,productive = (Counter({int(r):v for r,v in early['invoice'][key].items()}) for key in ('P','T'))
    assert (sum(paid.values()),sum(productive.values()),productive[137])==(110536,22461,208)
    a = c['types']['A']
    assert (a['roles'],a['offset'],len(set(a['ports'])),c['stages'])==(36,0,96,17)
    assert len(a['ports'])==96 and len(a['diagonal'])==36
    assert tuple(i for i,d in enumerate(a['diagonal']) if d==[-1,0]+[1]*17)==ROOTS
    assert len(c['events'])+1==4784
    net = productive.copy()
    net.subtract(paid)
    assert sum(r*v for r,v in net.items())==1424
    cost = predecessor['PRICING']['cost']
    baseline = cost(net,k)
    assert baseline[1]<0
    rows = []
    for m,central,p,s,count in partitions(17):
        delta = Counter()
        delta[p] += 96
        delta[s] += 96
        delta[137] -= 96
        changed = net.copy()
        changed.update(delta)
        credit,margin = cost(delta,k),cost(changed,k)
        assert credit[0]>0 and margin[0]>0 and p+s==137
        rows.append(dict(prefix_stage_count=m,prefix_central_axis=bool(central),ranks=[p,s],
                         stage_subset_multiplicity=count,productive_delta=dict(delta),
                         credit_interval=list(map(str,credit)),complete_margin_interval=list(map(str,margin))))
    assert len(rows)==34 and sum(r['stage_subset_multiplicity'] for r in rows)==262142
    best = max(Q(row['credit_interval'][1]) for row in rows)
    save(out,'PRICE.json',dict(head=HEAD,caller_head=CALLER_HEAD,pins=PINS,root_roles=ROOTS,
         crossing_upper=str(k),copies=17,ports_per_root=96,baseline_interval=list(map(str,baseline)),
         original_paid=dict(paid),original_productive=dict(productive),paid_delta={},
         stage_partition_classes=rows,ordered_factorizations_per_root=262142,
         whole_compatible_optimistic_credit_upper=str(2*best),
         optimistic_complete_margin_upper=str(baseline[1]+2*best),
         whole_rule='At most one split per rank-137 root; grant compatibility and all added costs free for the upper.'))
    return c


def isolated(rows,columns,r):
    found = {}
    for p,(row,col) in enumerate(zip(rows,columns,strict=True)):
        a,b = row[r],col[r]
        if not a or not b:
            continue
        if any(x for i,x in enumerate(row) if i!=r) or any(x for i,x in enumerate(col) if i!=r):
            continue
        assert a*b==1
        found[p] = [str(a),str(b)]
    assert len(found)<=1
    return found


def step(rows,cols,event,q,alpha,mix):
    def add(d,s,value):
        rows[d] = mix(rows[d],rows[s],Q(1),value)
        cols[s] = mix(cols[s],cols[d],Q(1),-value)

    if event[0]=='J':
        _,_,(u,v,x,y),_ = event
        assert len({u,v,x,y})==4
        add(v,u,1/q)
        add(x,y,alpha*q)
    elif event[0]=='A':
        _,op,r,*args = event
        if op in ('ADD','QUERY'):
            s,value = args
            assert s!=r
            add(r,s,Q(value) if op=='ADD' else q**value)
        elif op=='SWAP':
            s, = args
            rows[r],rows[s] = rows[s],rows[r]
            cols[r],cols[s] = cols[s],cols[r]
        elif op in ('SCALE','IDLE_ODD'):
            value = Q(args[0]) if op=='SCALE' else q**args[1]
            assert value
            rows[r] = [value*x for x in rows[r]]
            cols[r] = [x/value for x in cols[r]]
        else:
            assert op in ('LAMBDA','IDLE_ONE')
            return False
    else:
        assert event[0]=='B'
        return False
    return True


def controls(basis,mix):
    rows,cols = basis(3),basis(3)
    assert isolated(rows,cols,0)=={0:['1','1']}
    step(rows,cols,['A','SWAP',0,1],Q(1),Q(-1),mix)
    assert isolated(rows,cols,0)=={1:['1','1']}
    step(rows,cols,['A','SCALE',1,'-3/2'],Q(-1),Q(-1),mix)
    assert isolated(rows,cols,0)=={1:['-3/2','-2/3']}
    step(rows,cols,['A','ADD',2,1,'-1'],Q(1),Q(-1),mix)
    assert not isolated(rows,cols,0)
    rows,cols = basis(3),basis(3)
    step(rows,cols,['A','ADD',0,2,'1'],Q(1),Q(-1),mix)
    assert not isolated(rows,cols,0)
    assert sum(x[-1] for x in partitions(17))==262142 and len(partitions(17))==34
    return ['exact_identity_and_permuted_slot','signed_reciprocal_scale',
            'column_only_and_row_only_both_insufficient','positive_partition_counts']


def scan(c,engine,out,deadline,seconds):
    n=36
    basis,mix = engine['basis'],engine['mix']
    control = controls(basis,mix)
    phases = {q:(basis(n),basis(n)) for q in (Q(1),Q(-1))}
    alpha = Q(c['types']['A']['alpha2'])
    assert alpha==-1
    events = c['events']
    classification = Counter()
    witnesses = []
    visited = 0
    state_epoch = 0
    snapshot = {}
    for boundary in range(len(events)+1):
        if monotonic()>=deadline:
            break
        if boundary:
            changes = [step(R,C,events[boundary-1],q,alpha,mix) for q,(R,C) in phases.items()]
            assert changes[0]==changes[1]
            if changes[0]:
                state_epoch += 1
        if not boundary or changes[0]:
            snapshot={r:{q:isolated(R,C,r) for q,(R,C) in phases.items()} for r in ROOTS}
        for r in ROOTS:
            plus,minus = snapshot[r][Q(1)],snapshot[r][Q(-1)]
            common = plus.keys() & minus.keys()
            if not common:
                classification['not_isolated_in_a_common_slot'] += 1
                continue
            slot, = common
            edge = boundary in (0,len(events))
            classification['endpoint_control' if edge else 'interior_support_only'] += 1
            witnesses.append(dict(boundary=boundary,root=r,slot=slot,q_plus=plus[slot],
                                  q_minus=minus[slot],body_one_state_epoch=state_epoch,endpoint=edge))
        visited += 1
    if visited==len(events)+1:
        for q,(R,C) in phases.items():
            assert R==[[q*x for x in row] for row in basis(n)]
            assert C==[[q*x for x in row] for row in basis(n)]
        assert classification['endpoint_control']==4
    assert sum(classification.values())==visited*len(ROOTS)
    save(out,'BODY1.json',dict(head=HEAD,caller_head=CALLER_HEAD,pins=PINS,seconds_cap=seconds,
         body_specialization=1,q_specializations=[1,-1],controls=control,
         boundaries_total=len(events)+1,boundaries_visited=visited,root_cases_visited=visited*2,
         unresolved_boundary_interval=None if visited==len(events)+1 else [visited,len(events)],
         unresolved_roots=ROOTS,counts=dict(classification),witnesses=witnesses,
         price_sha256=sha256((out/'PRICE.json').read_bytes()).hexdigest(),
         note='Isolation is a necessary support gate. Full signed Laurent factorization and fully charged stock still pending.'))


def main():
    p=ArgumentParser()
    p.add_argument('dependencies',type=Path,nargs='?',default=Path(__file__).resolve().parent/'dependencies')
    p.add_argument('out',type=Path,nargs='?')
    p.add_argument('--seconds',type=int,default=30,choices=range(2,31),metavar='2..30')
    p.add_argument('--controls-only',action='store_true')
    p.add_argument('--price-only',action='store_true')
    a=p.parse_args()
    if a.out is None and not a.controls_only:
        p.error('fresh output directory required')
    if a.out is not None:
        a.out.mkdir()

    def timeout(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,timeout)
    alarm(a.seconds)
    start=monotonic()
    try:
        files=authenticate(a.dependencies)
        engine=runpy.run_path(str(a.dependencies/'r52/projector.py'))
        if a.controls_only:
            print(json.dumps(controls(engine['basis'],engine['mix'])))
        else:
            caller=price(a.dependencies,files,a.out)
            if not a.price_only:
                scan(caller,engine,a.out,start+a.seconds-1,a.seconds)
    except TimeoutError:
        if a.out is not None:
            save(a.out,'TIMEOUT.json',dict(head=HEAD,unverified_root_cases=9568,status='hard_timeout',
                                         price_saved=(a.out/'PRICE.json').exists()))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__=='__main__':
    assert __debug__
    main()
