"""Final response to centre-output errors in the declared scalar projection."""
from collections import Counter
from fractions import Fraction as Q
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
IDENTITY_EVENTS = {'idle_cover_sweep','terminal_Y_translations',
                   'bank_padding_cover_sweep','translate_every_live_family'}


def need(ok,why):
    if not ok:
        raise ValueError(why)


def authenticate():
    for row in json.loads((P/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        data = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'],'source SHA-256: '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],
             'source Git blob: '+row['path'])
    dependency = json.loads((P/'DEPENDENCY.json').read_text(encoding='utf-8'))
    need(dependency['commit'] == '30ec048eedcaca970f94bbec0fdd3c52eacf9fdc'
         and dependency['file'] == 'vendor/pr2199_verify.py','dependency identity')
    path = P/dependency['file']
    data = path.read_bytes()
    need(hashlib.sha256(data).hexdigest() == dependency['sha256'],'source SHA-256: PR2199')
    need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == dependency['git_blob'],
         'source Git blob: PR2199')
    spec = importlib.util.spec_from_file_location('pinned_pr2199',path)
    module = importlib.util.module_from_spec(spec)
    # Execute authenticated source bytes, never a cached bytecode file.
    exec(compile(data,str(path),'exec'),module.__dict__)
    return module


def add(a,b,q=1):
    for k,v in b.items():
        a[k] = a.get(k,0)+q*v
        if not a[k]:
            del a[k]


def local_errors(program):
    state = {('L',i):{} for i in range(704)}
    seen = set()
    for event in program:
        tag = event[0]
        if tag == 'scalar':
            op = event[1]; name,dest = op[0],tuple(op[1])
            if name == 'clear': state[dest] = {}
            elif name == 'copy': state[dest] = dict(state[tuple(op[2])])
            elif name == 'add': add(state[dest],state[tuple(op[2])],Q(op[3],op[4]))
            elif name == 'scale': state[dest] = {k:v*Q(op[2],op[3]) for k,v in state[dest].items()}
            else: raise ValueError('unknown scalar operation')
        elif tag == 'center':
            need(event[1] not in seen and event[4] == 8,'centre-error site')
            seen.add(event[1])
            add(state['C',event[1]],{event[1]:Q(1)})
        else:
            need(tag in {'phase','climb','adapter','residual_adapter'},'unknown projected event')
    need(seen == set(range(8)),'eight centre sites')
    need(all(not row for key,row in state.items() if key[0] != 'L'),'private error residue')
    return {key[1]:row for key,row in state.items() if key[0] == 'L' and row}


def bridge(state,event,omit=False):
    if omit: return
    base = event['replica']*896
    d,s = base+224*event['dst'],base+224*event['src']
    for port in range(112):
        add(state[d+port],state[s+port],event['coefficient'])
        add(state[s+112+port],state[d+112+port],-event['coefficient'])


def terminal(state,event):
    for pair in range(4):
        for port in range(112):
            x = event['replica']*896+pair*224+port
            state[x],state[x+112] = state[x+112],{k:-v for k,v in state[x].items()}


def compose(data,local,errors,initial=True,inject=False,omit_first_bridge=False):
    total = data['global']['live']
    state = {i:({i:Q(1)} if initial else {}) for i in range(total)}
    key = lambda c:tuple(c[k] for k in ('time','replica','stage','provider_id'))
    calls = {key(c):c for c in data['global']['calls']}
    need(len(calls) == 144,'unique scheduled calls')
    history,ordered,skipped = [],[],False
    for event in data['global']['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            c = calls[key(event)]; owners = [x[0] for x in c['owners']]
            orientation = c['orientation']
            # Source maps are recorded before the endpoint update.
            if initial:
                for form in local[orientation][0]:
                    row = {}
                    for role,q in form.items(): add(row,state[owners[role]],q)
                    history.append(row)
            for port in range(112):
                d,s,sign = (port+112,port,1) if orientation == 'forward' else (port,port+112,-1)
                add(state[owners[d]],state[owners[s]],sign)
            if inject:
                for role,row in errors[orientation].items():
                    add(state[owners[role]],{8*len(ordered)+k:q for k,q in row.items()})
            ordered.append([c['time'],c['replica'],c['stage'],orientation])
        elif kind == 'bridge':
            omit = omit_first_bridge and not skipped
            bridge(state,event,omit)
            skipped = True
        elif kind == 'terminal': terminal(state,event)
        else: need(kind in IDENTITY_EVENTS,'unknown global projection event')
    need(len(ordered) == 144,'complete call schedule')
    return state,history,ordered


def modular_rank(rows,prime=2147483647):
    """Independent modular elimination with the largest available pivot first."""
    basis = {}
    for row in reversed(rows):
        r = {k:(v.numerator*pow(v.denominator,-1,prime))%prime for k,v in row.items()}
        r = {k:v for k,v in r.items() if v}
        while r:
            j = max(r)
            if j not in basis:
                t = pow(r[j],-1,prime)
                basis[j] = {k:v*t%prime for k,v in r.items()}
                break
            t = r[j]
            for k,v in basis[j].items():
                z = (r.get(k,0)-t*v)%prime
                if z: r[k] = z
                else: r.pop(k,None)
    return len(basis)


def literal_probe(data,error_values):
    """Separate numeric interpreter of every scalar instruction at every call.

    Does not use local source maps, local error responses, or endpoint formulas.
    """
    physical = [Q(0)]*data['global']['live']
    bykey = {(c['time'],c['replica'],c['stage'],c['provider_id']):c for c in data['global']['calls']}
    call_index = 0
    scalar_count = 0
    for event in data['global']['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            c = bykey[tuple(event[k] for k in ('time','replica','stage','provider_id'))]
            owners = [row[0] for row in c['owners']]
            ordinary = [physical[o] for o in owners]
            private = {}
            def read(address):
                return ordinary[address[1]] if address[0] == 'L' else private[address[1]]
            def write(address,value):
                if address[0] == 'L': ordinary[address[1]] = value
                else: private[address[1]] = value
            for op in data['program'][c['orientation']]:
                if op[0] == 'scalar':
                    scalar_count += 1
                    ins = op[1]; name,d = ins[0],ins[1]
                    if name == 'clear': write(d,Q(0))
                    elif name == 'copy': write(d,read(ins[2]))
                    elif name == 'scale': write(d,read(d)*Q(ins[2],ins[3]))
                    elif name == 'add': write(d,read(d)+Q(ins[3],ins[4])*read(ins[2]))
                    else: raise ValueError('unknown literal scalar operation')
                elif op[0] == 'center': private[op[1]] += error_values[8*call_index+op[1]]
                else: need(op[0] in {'phase','climb','adapter','residual_adapter'},'unknown literal projected operation')
            need(not any(private.values()),'literal private error residue')
            for owner,value in zip(owners,ordinary): physical[owner] = value
            call_index += 1
        elif kind == 'bridge':
            base = 896*event['replica']; gain = event['coefficient']
            for p in range(112):
                dx,sx = base+224*event['dst']+p,base+224*event['src']+p
                physical[dx] += gain*physical[sx]
                physical[sx+112] -= gain*physical[dx+112]
        elif kind == 'terminal':
            for pair in range(event['pairs']):
                for p in range(112):
                    x = 896*event['replica']+224*pair+p
                    before_x,before_y = physical[x],physical[x+112]
                    physical[x],physical[x+112] = before_y,-before_x
        else: need(kind in IDENTITY_EVENTS,'unknown literal global event')
    return physical,scalar_count


def digest(rows):
    return hashlib.sha256(json.dumps([{str(k):str(v) for k,v in sorted(r.items())} for r in rows],
                                    separators=(',',':')).encode()).hexdigest()


def run():
    prior = authenticate()
    data,_,_ = prior.load(ROOT)
    need(data['global']['live'] == 16*4*2*112,'selected family count')
    for c in data['global']['calls']:
        program = data['program'][c['orientation']]
        bound = hashlib.sha256(json.dumps(program,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        need(c['local_program_sha256'] == bound,'call/program binding')
        base = 896*c['replica']+224*c['pair']
        need([r[0] for r in c['owners'][:224]] == list(range(base,base+224)),
             'bridge data-family numbering')
        owners = [r[0] for r in c['owners']]
        need(len(owners) == len(set(owners)) == 704 and all(0 <= o < 14336 for o in owners),
             'ordinary owner injection')
    for event in data['global']['execution_schedule']:
        if event['kind'] in {'bridge','terminal'}:
            need(event['replicas'] == [event['replica']],'single replica event')
        if event['kind'] == 'bridge':
            need(event['src'] != event['dst'] and all(0 <= event[k] < 4 for k in ('src','dst'))
                 and event['coefficient'] in (-1,1),'paired bridge schema')
        if event['kind'] == 'terminal': need(event['pairs'] == 4,'four signed exchanges')
    local = {o:prior.local_replay(data['program'][o]) for o in ('forward','backward')}
    for o in local:
        need(local[o][1] == prior.transvection_endpoint(o),'source local endpoint')
    errors = {o:local_errors(data['program'][o]) for o in local}
    ordinary,history,ordered = compose(data,local,errors)
    need(all(row == {i:Q(1)} for i,row in ordinary.items()),'complete projected endpoint identity')
    response,_,order2 = compose(data,local,errors,initial=False,inject=True)
    need(order2 == ordered,'response chronology')
    rows = list(response.values())
    rank_q,_ = prior.rank_q(rows)
    rank_p = modular_rank(rows)
    need(rank_q == rank_p == 1152,'final output error response is injective')
    history_rank = modular_rank(history)
    need(history_rank == 1152,'complete bridge history rank')
    columns = [{} for _ in range(1152)]
    for owner,row in response.items():
        for j,q in row.items(): columns[j][owner] = q
    minor_rank,pivot_owners = prior.rank_q(columns)
    need(minor_rank == len(pivot_owners) == 1152,'square output minor')
    need(modular_rank([response[o] for o in pivot_owners]) == 1152,'independent output-minor rank')
    probes = []
    for values in ([Q(((j*37+j*j)%29)-14,8) for j in range(1152)],
                   [Q(1) if j == 32 else Q(0) for j in range(1152)]):
        actual,count = literal_probe(data,values)
        expected = [sum((q*values[j] for j,q in row.items()),Q(0)) for row in rows]
        need(actual == expected,'independent full literal error replay')
        need(any(actual),'nonzero error remains observable')
        probes.append(dict(scalar_instructions=count,nonzero_final_owners=sum(bool(x) for x in actual),
                           endpoint_sha256=hashlib.sha256(json.dumps(list(map(str,actual))).encode()).hexdigest()))
    mutant,_,_ = compose(data,local,errors,omit_first_bridge=True)
    need(any(row != {i:Q(1)} for i,row in mutant.items()),'omitted bridge control')
    duplicate = [dict(r) for r in rows]
    for row in duplicate:
        row.pop(1,None)
        if 0 in row: row[1] = row[0]
    need(modular_rank(duplicate) == 1151,'duplicate error column control')
    return dict(status='PASS_SELECTED_CENTRE_ENDPOINT_ERROR',projection='Frame moves, idle factors and address translations are identity; all scalar calls, paired bridges and signed terminals execute.',
                calls=ordered,schedule_counts=dict(sorted(Counter(e['kind'] for e in data['global']['execution_schedule']).items())),
                complete_ordinary_endpoint='identity on 14336 independent scalar owner inputs',
                source_history_rank_mod_2147483647=history_rank,error_sites=1152,
                final_response_rank_Q=rank_q,final_response_rank_mod_2147483647=rank_p,
                output_minor_owners=pivot_owners,response_sha256=digest(rows),
                local_error_output_roles={o:sorted(errors[o]) for o in errors},
                local_error_response_sha256={o:digest([errors[o].get(i,{}) for i in range(704)]) for o in errors},
                literal_probes=probes,controls=['omitted_first_paired_bridge_breaks_identity','duplicate_error_column_rank1151','nonzero_single_site_error_observable'],
                source_pr2199_head='30ec048eedcaca970f94bbec0fdd3c52eacf9fdc')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    if args.out and args.out.exists():
        raise FileExistsError(args.out)
    result = run()
    text = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.out:
        with args.out.open('x',encoding='utf-8',newline='\n') as stream: stream.write(text)
    else:
        saved = json.loads((P/'RESULT.json').read_text(encoding='utf-8'))
        need(json.dumps(saved,sort_keys=True) == json.dumps(result,sort_keys=True),'typed receipt mismatch')
    print(result['status']+' sites=1152 final_rank=1152 scalar_bridges=144 terminal_exchanges=16')


if __name__ == '__main__': main()
