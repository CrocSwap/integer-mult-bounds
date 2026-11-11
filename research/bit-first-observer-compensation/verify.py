"""One augmented literal F2 pass over the 60 first-read compensation clocks."""
from argparse import ArgumentParser
from bisect import bisect_right
from collections import defaultdict
import gzip
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
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
    raw,pins={},{}
    for line in Path(__file__).with_name('SOURCES.tsv').read_text().splitlines():
        path,digest,_=line.split('\t')
        if path in pins:
            raise ValueError(f'duplicate dependency path: {path}')
        data=(root/path).read_bytes()
        if sha256(data).hexdigest()!=digest:
            raise ValueError(f'SHA-256 mismatch: {path}')
        pins[path],raw[path]=digest,data
    return pins,raw


def xor(values):
    result=0
    for v in values:
        result^=v
    return result


def trace(w,at,watch,virtual,deadline):
    n=w['public']
    f=w['start']+[None]*w['owned_fields']
    old=[1<<i for i in range(n)]+[0]*w['owned_fields']
    a=[0]*len(f)
    source,paid,terminal={},{},{}
    seen=[defaultdict(dict),defaultdict(dict)]

    def bind(slots):
        chart=slots[0]['chart']
        assert all(f[x['owner']]==chart and x['chart']==chart for x in slots)
        peers=[(j,old[j],a[j]) for j,x in enumerate(f) if x==chart]
        for s in slots:
            source[s['index']]=peers

    def witness(i,cut,phase):
        if not a[i]:
            return
        for j,limits in watch.get(f[i],()):
            for mode,last in enumerate(limits):
                if cut<=last:
                    seen[mode][j].setdefault(a[i],(cut,i,f[i],phase))

    for t,(op,i,*args) in enumerate(w['program']):
        if t%1024==0 and monotonic()>=deadline:
            raise TimeoutError('first-read compensation census exceeded cap')
        slots=at.get(t,())
        if op=='MOVE':
            x,y=args
            assert f[i]==x and x!=1
            if y==1:
                terminal[t]=old[i]
                if a[i]:
                    for j,mode,mid in virtual.get(t,()):
                        seen[mode][j].setdefault(a[i],(t,i,mid,'virtual pre-MOVE'))
            elif not slots:
                paid[t]=a[i]
            if slots:
                (slot,)=slots
                assert (slot['kind'],slot['owner'],slot['chart'],slot['target_chart'],slot['old_row'])==('paid',i,x,y,old[i])
                bind(slots)
                a[i]^=1<<slot['index']
            f[i]=y
        elif op=='ADD':
            j,x=args
            assert f[i]==f[j]==x
            old[i]^=old[j]
            a[i]^=a[j]
            witness(i,t+1,'old ADD')
            if slots:
                assert len(slots)==2 and {s['kind'] for s in slots}=={'ordinary'}
                assert [s['owner'] for s in slots]==[i,j]
                bind(slots)
                for s in slots:
                    k=s['owner']
                    a[k]^=1<<s['index']
                    witness(k,t+1,'ordinary correction')
        elif op=='SWAP':
            j,=args
            assert not slots
            f[i],f[j]=f[j],f[i]
            old[i],old[j]=old[j],old[i]
            a[i],a[j]=a[j],a[i]
            witness(j,t+1,'old SWAP')
        else:
            assert op in ('INIT','CLEAR') and args[0]!=1 and not slots
            assert f[i]==(None if op=='INIT' else args[0])
            f[i],old[i],a[i]=(args[0] if op=='INIT' else None),0,0
        witness(i,t+1,'end old event')
    want=[1<<j for j in range(n)]+[0]*w['owned_fields']
    for j in range(111):
        want[j+111]^=1<<j
    assert old==want and f==w['final']+[None]*w['owned_fields']
    ext={j:a[j] for j in range(n) if f[j]!=1}
    assert (len(source),len(paid),len(ext),len(terminal))==(180,2266,114,545)
    return source,paid,ext,terminal,[v for x,v in zip(f,old) if x==1],seen


def direction_basis(mask_to_path,solutions,old,W,j,lin):
    exposed={}
    for mask,path in sorted(mask_to_path.items()):
        indices=lin.positions(mask)
        for k,d in enumerate(solutions):
            value=xor(d[i] for i in indices)
            if value:
                exposed.setdefault(value,(k,indices,path))
    _,inside=lin.intersection_projection(lin.raw_basis(sorted(old|set(exposed))),W)
    q={}
    for v,row in inside:
        lin.insert(q,(v>>523)&~(1<<j),row)
    return exposed,q


def run(root,seconds):
    deadline=monotonic()+seconds
    pins,data=read(root)
    lin=load('round22',root/'round22/verify.py')
    engine=load('round25',root/'round25/verify.py')
    p7209=load('pr7209',root/'pr7209/verify.py')
    engine.controls(lin)
    r22=json.loads(data['round22/RESULT.json'])
    r24=json.loads(data['round24/RESULT.json'])
    r25=json.loads(data['round25/RESULT.json'])
    tariff=json.loads(data['bit-price/RESULT.json'])
    assert [x.get('needed_singleton_expansions') for x in tariff[TARGET]]==[7,5,4]
    assert [x.get('needed_singleton_expansions') for x in tariff[TRIAL]]==[8,6,None]
    marked=[x for x in r24['incidence'] if x['marked']]
    marks=[x['event'] for x in marked]
    windows={x['event']:x['quiet_window'] for x in r24['incidence']}
    singleton=[b['banks'][0] for b in r22['scope'][1]['endpoint_consistency']['blocks'] if len(b['banks'])==1]
    watch,virtual=defaultdict(list),defaultdict(set)
    maps=json.loads(data['pr7209/RESULT.json'])['bank_maps']
    assert marks==[p['event'] for p in maps]
    for j in singleton:
        p=marked[j]
        limits=p['event'],p['quiet_window'][1]
        for f in set([p['source_chart'],*p['compatible_literal_charts']]):
            watch[f].append((j,limits))
        for v in maps[j]['variants']:
            for e in v['virtual_bank_events']:
                for mode,last in enumerate(limits):
                    if (e if not mode else windows[e][0])<=last:
                        virtual[e].add((j,mode,v['literal_chart']))
    prior={c['event']:c for c in r25['carriers']}
    assert len(prior)==60
    word=json.loads(gzip.decompress(data[NATIVE]))
    program=word['program']
    contacts=defaultdict(list)
    for t,(op,i,*args) in enumerate(program):
        contacts[i].append(t)
        if op in ('ADD','SWAP'):
            contacts[args[0]].append(t)
    specs,observers=defaultdict(list),set()
    for e,c in prior.items():
        owner=c['owner']
        times=contacts[owner]
        assert program[e]==['MOVE',owner,c['source_chart'],c['target_chart']]
        t=times[bisect_right(times,e)]
        op,dest,source,chart=program[t]
        assert op=='ADD' and source==owner and chart==c['target_chart'] and t not in observers
        observers.add(t)
        specs[e].append({'event':e,'cut':e,'owner':owner,'chart':c['source_chart'],'target_chart':c['target_chart'],
                         'old_row':lin.encoded(c['old_row']),'kind':'paid','carrier':e,'recipient':c['recipient']})
        for i,role in ((dest,'destination'),(source,'source')):
            specs[t].append({'event':t,'cut':t+1,'owner':i,'chart':chart,'kind':'ordinary',
                             'lane':role,'carrier':e,'recipient':c['recipient']})
    slots=[s for t in sorted(specs) for s in specs[t]]
    for i,s in enumerate(slots):
        s['index']=i
    assert len(slots)==180 and len(observers)==60 and len(specs)==120
    invoice=json.loads(data[INVOICE])
    dims={int(f):v['dim'] for f,v in word['frames'].items()}
    source,paid,ext,terminal,required,seen=trace(word,specs,watch,virtual,deadline)
    # With the 120 corrections disabled, recover the exact predecessor masks.
    old_indices={s['index']:prior[s['event']]['index'] for s in slots if s['kind']=='paid'}
    for rows,key in ((paid,'nonzero_protected_contact_markers'),(ext,'nonzero_exterior_markers')):
        for k,m in rows.items():
            old=sorted(old_indices[i] for i in lin.positions(m) if i in old_indices)
            assert old==r25[key].get(str(k),[])
    donors=sorted(set(terminal)-set(marks))
    W={}
    for i,e in enumerate(donors+marks):
        assert lin.insert(W,terminal[e],1<<i)[0]
    assert len(W)==lin.rnk(required)==545 and all(not lin.reduce(W,v)[0] for v in required)
    spaces=[]
    for i in range(len(slots)):
        raw=[row for _,row,_ in source[i] if row]
        raw.extend(v for _,_,m in source[i] for j in lin.positions(m) for v in spaces[j])
        spaces.append(lin.raw_basis(sorted(raw)))
    available_receipts=[]
    for s,b in zip(slots,spaces,strict=True):
        case=dict(s)
        if 'old_row' in case:
            case['old_row']=lin.positions(case['old_row'])
        case['source_rows']=[{'owner':j,'old_row':lin.positions(v),'earlier_slots':lin.positions(m)} for j,v,m in source[s['index']]]
        case['causal_source_basis']=[lin.positions(v) for v in b]
        available_receipts.append(case)
    scopes=[]
    for scope,contacts in [('joint protected and exterior',[*paid.values(),*ext.values()]),
                           ('no leak constraints',[])]:
        if monotonic()>=deadline:
            raise TimeoutError('first-read compensation census exceeded cap')
        variables,equations,rank,null,solutions=engine.kernel(spaces,contacts,lin)
        clocks=[]
        for mode in range(2):
            recipients=[]
            for j in singleton:
                old={lin.encoded(v['row']) for v in r22['scope'][1]['banks'][j]['source_witnesses']}
                exposed,q=direction_basis(seen[mode][j],solutions,old,W,j,lin)
                recipients.append({'bank_index':j,'event':marks[j],
                                   'observed_markers':[{'slots':lin.positions(m),'witness':p} for m,p in sorted(seen[mode][j].items())],
                                   'exposed_response_rank':lin.rnk(exposed),
                                   'new_quotient_basis':[lin.positions(v) for v,_ in q.values()]})
            count=sum(bool(x['new_quotient_basis']) for x in recipients)
            clocks.append({'clock':'quiet' if mode else 'literal','recipients':recipients,
                           'expanded_singleton_upper':count,'price':engine.price(root,p7209,word,dims,invoice,count,tariff)})
        scopes.append({'scope':scope,'source_variables':len(variables),'equation_rows':len(equations),
                       'rank':rank,'nullity':len(null),'null_basis':[lin.positions(x) for x in null],
                       'live_slots':[i for i in range(len(slots)) if any(d[i] for d in solutions)],'clocks':clocks})
    return {'status':'NO VERIFIED GAIN','pins':pins,'seconds_cap':seconds,'target':TARGET,
            'paid_carriers':60,'ordinary_observer_clocks':60,'ordinary_slots':120,'pending_slots':0,
            'terminal_inputs_deferred':545,'protected_old_paid_operands':2266,'exterior_outputs':114,
            'new_sites':0,'sources':available_receipts,'scopes':scopes,
            'nonzero_protected_markers':{t:lin.positions(m) for t,m in paid.items() if m},
            'nonzero_exterior_markers':{j:lin.positions(m) for j,m in ext.items() if m}}


if __name__=='__main__':
    p=ArgumentParser(description=__doc__)
    p.add_argument('input_root',type=Path)
    p.add_argument('--seconds',type=int,default=480)
    a=p.parse_args()
    if not 1<=a.seconds<=480:
        p.error('--seconds must be in 1..480')
    print(json.dumps(run(a.input_root,a.seconds),sort_keys=True,indent=2))
