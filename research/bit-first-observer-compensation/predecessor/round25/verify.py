"""Joint 60-carrier literal BIT perturbation and endpoint quotient gate."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
import json
from pathlib import Path
from time import monotonic

NATIVE='research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
INVOICE='research/paired-query-only-bit/EFREE-RESULT.json'
TARGET='10018846261809/2500000000000000'
TRIAL='1002040748181/250000000000000'


def load(name,path):
    s=spec_from_file_location(name,path)
    m=module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(root):
    data,pins={},{}
    for line in Path(__file__).with_name('SOURCES.tsv').read_text().splitlines():
        name,digest,_=line.split('\t')
        if name in pins:
            raise ValueError(f'duplicate dependency path: {name}')
        blob=(root/name).read_bytes()
        if sha256(blob).hexdigest()!=digest:
            raise ValueError(f'SHA-256 mismatch: {name}')
        data[name],pins[name]=blob,digest
    return data,pins


def xor(values):
    q=0
    for v in values:
        q^=v
    return q


def record_timeline(word,carriers,watch,virtual,deadline):
    n=word['public']
    chart=word['start']+[None]*word['owned_fields']
    old=[1<<i for i in range(n)]+[0]*word['owned_fields']
    mark=[0]*len(chart)
    sources,protected,exterior,terminal={},{},{},{}
    seen=[defaultdict(dict),defaultdict(dict)]

    def observe(i,cut):
        if not mark[i]:
            return
        for j,bounds in watch.get(chart[i],()):
            for mode,lim in enumerate(bounds):
                if cut<=lim:
                    seen[mode][j].setdefault(mark[i],('literal',cut,i,chart[i]))

    for t,(op,i,*a) in enumerate(word['program']):
        if t%1024==0 and monotonic()>=deadline:
            raise TimeoutError('60-carrier cap expired')
        if op=='MOVE':
            f,g=a
            assert chart[i]==f and f!=1
            if g==1:
                terminal[t]=old[i]
                for j,mode,mid in virtual.get(t,()):
                    if mark[i]:
                        seen[mode][j].setdefault(mark[i],('virtual',t,i,mid))
            elif t not in carriers:
                protected[t]=mark[i]
            if t in carriers:
                e=carriers[t]
                assert (e['owner'],e['source_chart'],e['target_chart'],e['old_row'])==(i,f,g,old[i])
                sources[t]=[(k,old[k],mark[k]) for k,c in enumerate(chart) if k!=i and c==f]
                mark[i]^=1<<e['index']
            chart[i]=g
        elif op=='ADD':
            j,f=a
            assert chart[i]==chart[j]==f
            old[i]^=old[j]
            mark[i]^=mark[j]
        elif op=='SWAP':
            j,=a
            chart[i],chart[j]=chart[j],chart[i]
            old[i],old[j]=old[j],old[i]
            mark[i],mark[j]=mark[j],mark[i]
            observe(j,t+1)
        else:
            assert op in ('INIT','CLEAR') and a[0]!=1
            assert chart[i]==(None if op=='INIT' else a[0])
            chart[i],old[i],mark[i]=(a[0] if op=='INIT' else None),0,0
        observe(i,t+1)
    want=[1<<i for i in range(n)]+[0]*word['owned_fields']
    for i in range(111):
        want[111+i]^=1<<i
    assert chart==word['final']+[None]*word['owned_fields'] and old==want
    assert len(sources)==60 and len(protected)==2266 and len(terminal)==545
    exterior={i:mark[i] for i,f in enumerate(chart[:n]) if f!=1}
    assert len(exterior)==114
    return sources,protected,exterior,terminal,[row for f,row in zip(chart,old) if f==1],seen


def kernel(spaces,contacts,lin):
    variables=[]
    by_carrier=[]
    for i,source in enumerate(spaces):
        current=[]
        for row in source:
            current.append((len(variables),row))
            variables.append((i,row))
        by_carrier.append(current)
    equations=[]
    pivots={}
    for mask in sorted(set(contacts)-{0}):
        terms={}
        for i in lin.positions(mask):
            for j,row in by_carrier[i]:
                for k in lin.positions(row):
                    terms[k]=terms.get(k,0)^(1<<j)
        for row in terms.values():
            if row:
                equations.append(row)
                lin.insert(pivots,row)
    null=[]
    for j in range(len(variables)):
        if j in pivots:
            continue
        x=1<<j
        for k,(row,_) in sorted(pivots.items()):
            if (x&row).bit_count()%2:
                x^=1<<k
        assert all(not ((row&x).bit_count()%2) for row in equations)
        null.append(x)
    assert len(null)+len(pivots)==len(variables)
    solutions=[]
    for x in null:
        d=[0]*len(spaces)
        for j in lin.positions(x):
            i,row=variables[j]
            d[i]^=row
        assert all(not xor(d[i] for i in lin.positions(mask)) for mask in contacts)
        solutions.append(d)
    return variables,equations,len(pivots),null,solutions


def controls(lin):
    # Two leaking carriers cancel jointly, while either isolated one fails.
    _,_,rank,_,sol=kernel([[1],[1]],[3],lin)
    assert rank==1 and sol==[[1,1]]
    assert not kernel([[1],[1]],[1,2],lin)[-1]
    # Synthetic two-for-one exchange in the spirit of #7264, no old tape.
    u,p,q=1,2,4
    assert lin.rnk([p^q,u,q^u])==3
    assert lin.rnk([p^q,p^u,u])==3


def price(root,pricing,word,dims,invoice,expanded,tariff):
    interval=load('interval',root/'research/paired-query-only-bit/independent/interval_gate.py')
    ledger=pricing.terminal_ledger(word,dims)
    result={}
    for key in (TARGET,TRIAL):
        charge=list(map(Fraction,interval.show(interval.smul(interval.sub(interval.exact(2),interval.power(2,Fraction(key))),36))))
        result[key]=[]
        for entry in tariff[key]:
            h=entry['h']
            n=min(22,12+expanded+2*(1+h))
            old=pricing.prices(root,invoice,word,dims,ledger,n)[key]
            a,b=map(Fraction,old['net_upper'])
            net=a-h*charge[1],b-h*charge[0]
            result[key].append({'h':h,'stock_upper':n,'net_upper':list(map(str,net)),
                                'required_expansions':entry.get('needed_singleton_expansions'),
                                'affordable_upper':net[1]>=0 and not entry.get('unaffordable',False)})
    return result


def run(root,seconds):
    deadline=monotonic()+seconds
    data,pins=read(root)
    lin=load('round22',root/'round22/verify.py')
    pricing=load('pr7209',root/'pr7209/verify.py')
    controls(lin)
    r24=json.loads(data['round24/RESULT.json'])
    r22=json.loads(data['round22/RESULT.json'])
    tariff=json.loads(data['bit-price/RESULT.json'])
    assert [x.get('needed_singleton_expansions') for x in tariff[TARGET]]==[7,5,4]
    assert [x.get('needed_singleton_expansions') for x in tariff[TRIAL]]==[8,6,None]
    peer=json.loads(data['pr7244/PROPOSED-CLAIM.json'])
    assert peer['complex_BIT_premise']=='376669/100000000'
    assert r24['scopes'][1]['t']['rank']==r24['scopes'][1]['s']['rank']==1
    marked=[p for p in r24['incidence'] if p['marked']]
    marks=[p['event'] for p in marked]
    port_window={p['event']:p['quiet_window'] for p in r24['incidence']}
    markmap=json.loads(data['pr7209/RESULT.json'])['bank_maps']
    assert [p['event'] for p in markmap]==marks
    r22map=r22['scope'][1]['banks']
    singleton=[b['banks'][0] for b in r22['scope'][1]['endpoint_consistency']['blocks'] if len(b['banks'])==1]
    assert singleton==[0,1,2,3,4,5,6,10,14,17]
    carriers,watch,virtual={},defaultdict(list),defaultdict(set)
    for j in singleton:
        p=marked[j]
        bounds=p['event'],p['quiet_window'][1]
        for f in set([p['source_chart'],*p['compatible_literal_charts']]):
            watch[f].append((j,bounds))
        for c in p['clocks'][1]['compatible_charts']:
            for e in c['paid_ingress']:
                t=e['event']
                assert t not in carriers
                carriers[t]={'event':t,'after_cut':e['after_cut'],'owner':e['owner'],'source_chart':e['source_chart'],
                             'target_chart':c['chart'],'old_row':lin.encoded(e['row']),'recipient':j}
        # Also grant changed literal terminal operands along every compatible
        # old virtual prefix from the fixed-library predecessor.
        for v in markmap[j]['variants']:
            for e in v['virtual_bank_events']:
                for mode,lim in enumerate(bounds):
                    eligible=e<=lim if mode==0 else port_window[e][0]<=lim
                    if eligible:
                        virtual[e].add((j,mode,v['literal_chart']))
    events=sorted(carriers)
    for i,t in enumerate(events):
        carriers[t]['index']=i
    assert len(events)==60 and len({e['target_chart'] for e in carriers.values()})==20
    word=json.loads(gzip.decompress(data[NATIVE]))
    invoice=json.loads(data[INVOICE])
    dims={int(f):v['dim'] for f,v in word['frames'].items()}
    source,protected,exterior,terminal,required,seen=record_timeline(word,carriers,watch,virtual,deadline)
    donors=sorted(set(terminal)-set(marks))
    assert len(donors)==523
    W={}
    for i,t in enumerate(donors+marks):
        assert lin.insert(W,terminal[t],1<<i)[0]
    assert len(W)==lin.rnk(required)==545 and all(not lin.reduce(W,v)[0] for v in required)
    constraints=[*protected.values(),*exterior.values()]
    scopes=[]
    for closure, own in ((False,False),(True,False),(True,True)):
        spaces=[]
        for t in events:
            raw=[row for _,row,_ in source[t] if row]
            if own:
                raw.append(carriers[t]['old_row'])
            if closure:
                raw.extend(v for _,_,m in source[t] for i in lin.positions(m) for v in spaces[i])
            spaces.append(lin.raw_basis(sorted(raw)))
        variables,equations,rank,null,solutions=kernel(spaces,constraints,lin)
        _,_,protected_rank,_,_=kernel(spaces,list(protected.values()),lin)
        _,_,exterior_rank,_,_=kernel(spaces,list(exterior.values()),lin)
        marker_basis={}
        witness_exterior={}
        for owner,mask in exterior.items():
            if lin.insert(marker_basis,mask)[0]:
                witness_exterior[owner]=mask
        _,_,witness_rank,_,_=kernel(spaces,list(witness_exterior.values()),lin)
        assert witness_rank==exterior_rank
        live_carriers=[events[i] for i in range(60) if any(d[i] for d in solutions)]
        receivers=[]
        for mode in range(2):
            each=[]
            for j in singleton:
                base={lin.encoded(a['row']) for a in r22map[j]['source_witnesses']}
                raw={}
                for marker,path in sorted(seen[mode][j].items()):
                    for k,delta in enumerate(solutions):
                        v=xor(delta[i] for i in lin.positions(marker))
                        if v:
                            raw.setdefault(v,{'kernel_vector':k,'carrier_markers':lin.positions(marker),'path':path})
                _,inside=lin.intersection_projection(lin.raw_basis(sorted(base|set(raw))),W)
                q={}
                for v,row in inside:
                    lin.insert(q,(v>>523)&~(1<<j),row)
                each.append(list(q.values()))
                receivers.append({'mode':'quiet' if mode else 'literal','bank_index':j,'event':marks[j],
                                  'observed_marker_count':len(seen[mode][j]),
                                  'nonzero_joint_response_rows':[{'row':lin.positions(v),**a} for v,a in sorted(raw.items())],
                                  'new_quotient_basis':[lin.positions(v) for v,_ in q.values()]})
            match,_,_=lin.transversal(each)
            count=sum(bool(x) for x in each)
            receivers.append({'mode':'quiet' if mode else 'literal','expanded_singleton_upper':count,
                              'independent_recipient_direction_upper':len(match),
                              'price':price(root,pricing,word,dims,invoice,count,tariff)})
        scopes.append({'source_scope':'arbitrary current coframed replacement' if own else ('causal earlier-carrier closure' if closure else 'literal other-owner source rows'),
                       'variables':len(variables),'scalar_equation_rows':len(equations),'equation_rank':rank,
                       'joint_kernel_dimension':len(null),'protected_only_coefficient_rank':protected_rank,
                       'exterior_only_coefficient_rank':exterior_rank, 'exterior_scalar_marker_rank':len(marker_basis),
                       'exterior_basis_roles':list(witness_exterior),'kernel_coefficients':[lin.positions(v) for v in null],
                       'joint_live_carrier_events':live_carriers,
                       'carrier_source_bases':[{'event':e,'rows':[lin.positions(v) for v in s]} for e,s in zip(events,spaces)],
                       'recipients':receivers})
    return {'status':'NO VERIFIED GAIN','pins':pins,'target':TARGET,'seconds_cap':seconds,
            'completed_carriers':60,'pending_carriers':0,'new_sites':0,
            'protected_paid_contact_count':len(protected),'protected_exterior_output_count':len(exterior),
            'terminal_arrival_inputs_deferred':545,
            'nonzero_protected_contact_markers':{t:lin.positions(v) for t,v in protected.items() if v},
            'nonzero_exterior_markers':{i:lin.positions(v) for i,v in exterior.items() if v},
            'carriers':[{**c,'old_row':lin.positions(c['old_row']),
                         'live_other_coframed_sources':[{'owner':j,'row':lin.positions(v),'earlier_carriers':lin.positions(m)}
                                                         for j,v,m in source[t]]}
                        for t in events for c in [carriers[t]]],
            'scopes':scopes}


if __name__=='__main__':
    p=ArgumentParser(description=__doc__)
    p.add_argument('input_root',type=Path)
    p.add_argument('--seconds',type=int,default=480)
    a=p.parse_args()
    if not 1<=a.seconds<=480:
        p.error('--seconds must be in 1..480')
    print(json.dumps(run(a.input_root,a.seconds),sort_keys=True,indent=2))
