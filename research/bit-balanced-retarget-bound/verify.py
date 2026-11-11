"""Bounded next gate for same-rank balanced retargeting of the old paid ingress slots."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
import json
from pathlib import Path
from time import monotonic


NATIVE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
INVOICE = 'research/paired-query-only-bit/EFREE-RESULT.json'


def read(root):
    pins, raw = {}, {}
    for line in Path(__file__).with_name('SOURCES.tsv').read_text().splitlines():
        name, digest, _ = line.split('	')
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in pins:
            raise ValueError(f'ambiguous input path {name}')
        data = (root / path).read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {name}')
        pins[name], raw[name] = digest, data
    return pins, raw


def import_at(name,path):
    spec=spec_from_file_location(name,path)
    result=module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def cycle_edges(edges):
    """Return labeled arcs that can belong to a balanced directed circulation."""
    adjacency=defaultdict(set)
    for _,a,b in edges:
        adjacency[a].add(b)
    reachable={}
    for a in set(adjacency):
        found={a}
        work=[a]
        while work:
            new=adjacency[work.pop()]-found
            work.extend(new)
            found.update(new)
        reachable[a]=found
    return [e for e in edges if e[1] in reachable.get(e[2],set())]


def control():
    a=[(0,1,2),(1,2,3),(2,3,1),(3,3,4)]
    assert cycle_edges(a)==a[:3] and not cycle_edges([(0,1,2)])
    # The late reverse arc can balance an early useful delivery.
    late_return=[(1,1,2),(9,2,1)]
    assert [e for e in cycle_edges(late_return) if e[0]<5]==late_return[:1]


def run(root,seconds):
    deadline=monotonic()+seconds
    pins,raw=read(root)
    lin=import_at('round22',root/'round22/verify.py')
    old=import_at('round25',root/'round25/verify.py')
    prior=import_at('round24',root/'round24/verify.py')
    price=import_at('p7209',root/'pr7209/verify.py')
    R22=json.loads(raw['round22/RESULT.json'])
    R24=json.loads(raw['round24/RESULT.json'])
    R25=json.loads(raw['round25/RESULT.json'])
    w=json.loads(gzip.decompress(raw[NATIVE]))
    invoice=json.loads(raw[INVOICE])
    tariff=json.loads(raw['bit-price/RESULT.json'])
    marks=[p for p in R24['incidence'] if p['marked']]
    mark_events=[p['event'] for p in marks]
    singletons=[b['banks'][0] for b in R22['scope'][1]['endpoint_consistency']['blocks'] if len(b['banks'])==1]
    targets={f:j for j in singletons for f in marks[j]['compatible_literal_charts']}
    assert len(targets)==20 and len(R25['carriers'])==60
    dims={int(f):v['dim'] for f,v in w['frames'].items()}
    frames={int(f):price.rref([tuple(Fraction(x) for x in a) for a in v['B']]) for f,v in w['frames'].items()}
    pending=[(c['event'], h) for c in R25['carriers'] for h in sorted(targets)]

    def incomplete(stage, tested):
        return {'status':'INCOMPLETE_CAP','stage':stage,'pins':pins,
                'pairs_tested':tested,'unvisited_pairs':pending[tested:],
                'price_certified':False}

    try:
        paid,_,_,required=prior.paid_timeline(w,deadline)
    except TimeoutError:
        return incomplete('paid_timeline',0)
    terminal={e:v for e,(_,_,f,v) in paid.items() if f==1}
    W={}
    for i,e in enumerate(sorted(set(terminal)-set(mark_events))+mark_events):
        assert lin.insert(W,terminal[e],1<<i)[0]
    assert len(W)==lin.rnk(required)==545 and all(not lin.reduce(W,v)[0] for v in required)
    source={a['event']:[lin.encoded(v) for v in a['rows']] for a in R25['scopes'][-1]['carrier_source_bases']}
    geometry=[]
    nonnested=[]
    tested=0
    for c in R25['carriers']:
        e=c['event']
        owner,f,g,_=paid[e]
        assert (owner,f,g)==(c['owner'],c['source_chart'],c['target_chart'])
        assert dims[g]==7
        nested=dims[f]<7 and price.join(frames[f],frames[g])==frames[g]
        if not nested:
            nonnested.append(e)
        for h in sorted(targets):
            if monotonic()>=deadline:
                return incomplete('geometric_incidence',tested)
            if nested and h!=g and price.join(frames[f],frames[h])==frames[h]:
                geometry.append((e,g,h))
            tested+=1
    assert tested==1200
    # Even a late delivery may balance an early rebind. First grant all
    # geometric cycles, then filter which arrivals can help each recipient.
    cyclic=cycle_edges(geometry)
    trial=[]
    for quiet in (False,True):
        cutoff=lambda h: (marks[targets[h]]['quiet_window'][1]
                          if quiet else marks[targets[h]]['event'])
        edges=[(e,g,h) for e,g,h in geometry if e+1<=cutoff(h)]
        usable=[(e,g,h) for e,g,h in cyclic if e+1<=cutoff(h)]
        receivers=[]
        for j in singletons:
            moves=[e for e,_,h in usable if targets[h]==j]
            raw_rows={lin.encoded(v['row']) for v in R22['scope'][1]['banks'][j]['source_witnesses']}
            raw_rows.update(v for e in moves for v in source[e])
            _,inside=lin.intersection_projection(lin.raw_basis(sorted(raw_rows)),W)
            expanded={}
            for q,v in inside:
                lin.insert(expanded,(q>>523)&~(1<<j),v)
            receivers.append({'singleton':j,'timely_retarget_slots':moves,
                              'new_quotient_basis':[lin.positions(v) for v,_ in expanded.values()]})
        count=sum(bool(r['new_quotient_basis']) for r in receivers)
        trial.append({'clock':'quiet' if quiet else 'literal','source_target_pairs':tested,'nonnested_untested':nonnested,
                      'all_balancing_incidences':geometry,'cyclic_balancing_incidences':cyclic,
                      'timely_incidences':edges,'timely_cyclic_incidences':usable,'recipients':receivers,
                      'expanded_singleton_upper':count,'price':old.price(root,price,w,dims,invoice,count,tariff)})
    if monotonic()>=deadline:
        return incomplete('projection_and_price',tested)
    return {'status':'PASS_COMPLETE_STOCK_UPPER',
            'scope':'nested same-rank target rebinds within fixed 60/20 stock and fixed unmarked libraries',
            'pins':pins,'new_sites':0,'seconds_cap':seconds,'clocks':trial}


if __name__=='__main__':
    p=ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path,nargs='?')
    p.add_argument('--seconds',type=int,default=480)
    p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    control()
    if a.self_test:
        print('PASS synthetic circulation controls')
    elif a.root is None or not 1<=a.seconds<=480:
        p.error('explicit root and 1..480 seconds required')
    else:
        print(json.dumps(run(a.root,a.seconds),sort_keys=True,indent=2))
