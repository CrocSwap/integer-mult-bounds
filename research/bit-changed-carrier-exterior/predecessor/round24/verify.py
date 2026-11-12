"""One exact 185-port BIT incidence census for old funded rank-seven ingress."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import lcm
from pathlib import Path
from time import monotonic

NATIVE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
INVOICE = 'research/paired-query-only-bit/EFREE-RESULT.json'
TARGET = '10018846261809/2500000000000000'
TRIAL = '1002040748181/250000000000000'


def load_code(name, path):
    s = spec_from_file_location(name,path)
    m = module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(root):
    pins, source = {}, {}
    for line in Path(__file__).with_name('SOURCES.tsv').read_text().splitlines():
        name,digest,_ = line.split('\t')
        if name in pins:
            raise ValueError(f'duplicate dependency path: {name}')
        pins[name] = digest
        data = (root/name).read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {name}')
        source[name] = data
    return pins,source


def primitive(row):
    scale = lcm(*(x.denominator for x in row))
    return tuple(int(x*scale) for x in row)


def contains(rows, normal):
    return all(sum(a*b for a,b in zip(row,normal,strict=True)) == 0 for row in rows)


def paid_timeline(w, deadline):
    n = w['public']
    chart = w['start']+[None]*w['owned_fields']
    rows = [1<<i for i in range(n)]+[0]*w['owned_fields']
    moves, touches, history = {}, defaultdict(list), defaultdict(dict)

    def observe(owner,t,op):
        if rows[owner]:
            history[chart[owner]].setdefault((owner,rows[owner]),(t,op))

    for i in range(n):
        observe(i,0,'initial')
    for t,(op,i,*args) in enumerate(w['program']):
        if t % 1024 == 0 and monotonic() >= deadline:
            raise TimeoutError('185-port paid incidence exceeded cap')
        touches[i].append(t)
        if op == 'MOVE':
            f,g = args
            assert chart[i] == f and f != 1
            moves[t] = i,f,g,rows[i]
            chart[i] = g
        elif op == 'ADD':
            j,f = args
            assert chart[i] == chart[j] == f
            touches[j].append(t)
            rows[i] ^= rows[j]
        elif op == 'SWAP':
            j, = args
            touches[j].append(t)
            chart[i],chart[j] = chart[j],chart[i]
            rows[i],rows[j] = rows[j],rows[i]
            observe(j,t+1,op)
        else:
            assert op in ('INIT','CLEAR') and args[0] != 1
            assert chart[i] == (None if op == 'INIT' else args[0])
            chart[i],rows[i] = (args[0] if op == 'INIT' else None),0
        observe(i,t+1,op)
    want = [1<<i for i in range(n)]+[0]*w['owned_fields']
    for i in range(111):
        want[111+i] ^= 1<<i
    assert chart == w['final']+[None]*w['owned_fields'] and rows == want
    assert len(moves) == 2871
    window = {}
    for t,(owner,_,_,_) in moves.items():
        seen = touches[owner]
        i = seen.index(t)
        window[t] = (seen[i-1]+1 if i else 0, seen[i+1] if i+1<len(seen) else len(w['program']))
    return moves,window,history,[v for f,v in zip(chart,rows) if f==1]


def projected(raw,W,mask,lin):
    _, intersection = lin.intersection_projection(lin.raw_basis(sorted(raw)),W)
    marked,singleton = {},{}
    for v,row in intersection:
        outside = v>>523
        lin.insert(marked,outside,row)
        lin.insert(singleton,outside&mask,row)
    return list(marked.values()),list(singleton.values())


def rank_receipt(parts,events,lin):
    assigned,subset,rank = lin.transversal(parts)
    return {'rank':len(assigned),'rado_subset':subset,'rado_subset_rank':rank,
            'directions':[{'port':events[i],'projection':lin.positions(v),'source_row':lin.positions(row)}
                          for i,v,row in assigned]}


def bill(root,pricing,word,dims,invoice,t,s):
    g = load_code('price_intervals',root/'research/paired-query-only-bit/independent/interval_gate.py')
    ledger = pricing.terminal_ledger(word,dims)
    copies = len(invoice['native_instances'])
    assert copies == 36
    upper,need = [],[]
    for h in range(6):
        stock = min(22,12+min(22,t+h)+min(10,s+h))
        raw = pricing.prices(root,invoice,word,dims,ledger,stock)
        full = pricing.prices(root,invoice,word,dims,ledger,22)
        prices,requirements = {},{}
        for key in (TARGET,TRIAL):
            charge = g.smul(g.sub(g.exact(2),g.power(2,Fraction(key))),copies)
            c0,c1 = map(Fraction,g.show(charge))
            p0,p1 = map(Fraction,raw[key]['net_upper'])
            f0,f1 = map(Fraction,full[key]['net_upper'])
            assert 0<c0<=c1
            prices[key] = {'raw_net': [str(p0),str(p1)],'minimum_split_charge':[str(c0),str(c1)],
                           'charged_net_upper':[str(p0-h*c1),str(p1-h*c0)]}
            if f1-h*c0 >= 0:
                requirements[key] = max(0,raw[key]['needed']-12-2*(t+h))
        upper.append({'additional_separately_charged_donors':h,'stock_upper':stock,
                      'also_covers_more_charged_donors':h==5,'directed':prices})
        if requirements:
            need.append({'additional_separately_charged_donors':h,
                         'minimum_changed_singleton_marked_libraries':requirements})
    assert upper[-1]['stock_upper']==22
    return upper,need


def run(root,seconds):
    deadline = monotonic()+seconds
    pins,data = read(root)
    lin = load_code('round22',root/'round22/verify.py')
    pricing = load_code('pr7209',root/'pr7209/verify.py')
    assert contains([(1,0)],(0,1)) and not contains([(1,1)],(0,1))
    prior = json.loads(data['round23/RESULT.json'])
    local22 = json.loads(data['round22/RESULT.json'])
    public22 = json.loads(data['pr7258/SUMMARY.json'])
    peer = json.loads(data['pr7244/PROPOSED-CLAIM.json'])
    assert prior['target'] == public22['target'] == TARGET
    assert peer['complex_BIT_premise'] == public22['retained_BIT_premise'] == '376669/100000000'
    assert public22['receipt_sha256'] == sha256(data['round22/RESULT.json']).hexdigest()
    assert public22['scopes'][1]['endpoint_preserving_independent_stock'] == 12
    mark_maps = json.loads(data['pr7209/RESULT.json'])['bank_maps']
    marks = [m['event'] for m in mark_maps]
    word = json.loads(gzip.decompress(data[NATIVE]))
    invoice = json.loads(data[INVOICE])
    assert 1 not in word['start']
    dims = {int(f):x['dim'] for f,x in word['frames'].items()}
    rows = {int(f):[primitive(tuple(Fraction(v) for v in r)) for r in x['B']] for f,x in word['frames'].items()}
    normal = {f:primitive(tuple(Fraction(v) for v in pricing.normal(pricing.rref([tuple(map(Fraction,r)) for r in rows[f]]))))
              for f in rows if dims[f]==7}
    assert len(normal)==120 and [f for f in dims if dims[f]==8]==[1]
    paid,window,history,required = paid_timeline(word,deadline)
    terminal = {t:v for t,(_,_,g,v) in paid.items() if g==1}
    donors = sorted(set(terminal)-set(marks))
    cohort = [t for t in sorted(terminal) if dims[paid[t][1]]<=6]
    assert len(terminal)==545 and len(donors)==523 and len(cohort)==185
    assert set(marks)<=set(cohort)
    W = {}
    for i,t in enumerate(donors+marks):
        assert lin.insert(W,terminal[t],1<<i)[0]
    assert len(W)==lin.rnk(required)==545 and all(not lin.reduce(W,r)[0] for r in required)
    singleton = prior['quiet_singleton_mark_positions']
    assert singleton==[b['banks'][0] for b in local22['scope'][1]['endpoint_consistency']['blocks'] if len(b['banks'])==1]
    mask = lin.encoded(singleton)
    base_quiet = prior['scopes'][1]['donors']
    assert [x['event'] for x in base_quiet]==donors
    baseline = {x['event']:{lin.encoded(v['row']) for v in x['source_rows']} for x in base_quiet}
    baseline_useful = {x['event'] for x in base_quiet if x['projection_marked_basis']}
    assert baseline_useful=={21445}
    incoming = defaultdict(list)
    for t,(i,f,g,row) in paid.items():
        if dims[g]==7 and row:
            incoming[g].append((t,i,f,row))
    incidence = {}
    for t in cohort:
        if monotonic() >= deadline:
            raise TimeoutError('185-port paid incidence exceeded cap')
        i,f,g,old = paid[t]
        assert g==1
        mids = [mid for mid,n in normal.items() if contains(rows[f],n)]
        if t in marks:
            known = [v['literal_chart'] for v in mark_maps[marks.index(t)]['variants'] if v['literal_chart'] is not None]
            assert sorted(mids)==sorted(known)
        incidence[t] = {'event':t,'owner':i,'source_chart':f,'source_rank':dims[f],
                        'paid_rank':8-dims[f],'quiet_window':window[t], 'marked':t in marks,
                        'old_row':lin.positions(old),'compatible_literal_charts':mids, 'clocks':[]}
    scopes = []
    for retime in (False,True):
        all_m,all_s = [],[]
        funded_useful, any_useful = [],[]
        for t in sorted(terminal):
            raw = baseline.get(t,set())
            funded = set()
            grant = set()
            if t in incidence:
                cut = window[t][1] if retime else t
                choices = []
                for mid in incidence[t]['compatible_literal_charts']:
                    paid_rows = [(e,i,f,row) for e,i,f,row in incoming[mid] if e<cut]
                    cached = [(clock,i,op,row) for (i,row),(clock,op) in history[mid].items() if clock<=cut]
                    funded.update(row for _,_,_,row in paid_rows)
                    grant.update(row for _,_,_,row in paid_rows)
                    grant.update(row for _,_,_,row in cached)
                    choices.append({'chart':mid,'paid_ingress':[{'event':e,'after_cut':e+1,'owner':i,'source_chart':f,'row':lin.positions(row)}
                                                               for e,i,f,row in paid_rows],
                                    'literal_coframed_cache':[{'cut':clock,'owner':i,'operation':op,'row':lin.positions(row)}
                                                             for clock,i,op,row in sorted(cached)]})
                incidence[t]['clocks'].append({'deadline_cut':cut,'compatible_charts':choices})
            if t in marks:
                continue
            m,s = projected(raw|grant,W,mask,lin)
            m_paid,_ = projected(raw|funded,W,mask,lin)
            if m:
                any_useful.append(t)
            if m_paid and t not in baseline_useful:
                funded_useful.append(t)
            all_m.append(m)
            all_s.append(s)
            if t in incidence:
                incidence[t]['clocks'][-1]['W_over_U_basis'] = [lin.positions(v) for v,_ in m]
                incidence[t]['clocks'][-1]['singleton_basis'] = [lin.positions(v) for v,_ in s]
                incidence[t]['clocks'][-1]['paid_ingress_only_W_over_U_basis'] = [lin.positions(v) for v,_ in m_paid]
        t_rank = rank_receipt(all_m,donors,lin)
        s_rank = rank_receipt(all_s,donors,lin)
        t,s = t_rank['rank'],s_rank['rank']
        bills,changed = bill(root,pricing,word,dims,invoice,t,s)
        scopes.append({'scope':'owner quiet upper' if retime else 'literal pre-cut upper',
                       't':t_rank,'s':s_rank,'quotient_useful_slots':any_useful,
                       'additional_useful_slots_with_old_paid_ingress':funded_useful,
                       'paid_refinement_price':bills,'changed_marked_library_minimum':changed,
                       'aggregate_target_survives': any(Fraction(x['directed'][TARGET]['charged_net_upper'][1])>=0 for x in bills) and len(funded_useful)>=2,
                       'aggregate_stricter_survives': any(Fraction(x['directed'][TRIAL]['charged_net_upper'][1])>=0 for x in bills) and len(funded_useful)>=3})
    return {'status':'NO VERIFIED GAIN','pins':pins,'target':TARGET,'trial':TRIAL,'seconds_cap':seconds,
            'paid_moves':len(paid),'terminal_arrivals':len(terminal),'completed_incidence_ports':len(cohort),
            'pending_incidence_ports':0,'marked_ports_held_fixed':22,'unmarked_incidence_ports':163,
            'new_sites':0,'scopes':scopes,'incidence':list(incidence.values())}


if __name__=='__main__':
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('input_root',type=Path)
    cli.add_argument('--seconds',type=int,default=480)
    args = cli.parse_args()
    if not 1<=args.seconds<=480:
        cli.error('--seconds must be in 1..480')
    print(json.dumps(run(args.input_root,args.seconds),sort_keys=True,indent=2))
