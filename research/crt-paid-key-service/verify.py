"""Source-bound independent key-event replay and one original caller layer.

JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
All word decoding, expected keys and address logs here are verification oracles.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, why):
    if not ok: raise ValueError(why)


def load(name, path, raw):
    m = types.ModuleType(name); m.__file__ = str(path); sys.modules[name] = m
    exec(compile(raw, str(path), 'exec'), m.__dict__); return m


def sources():
    data = {}
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input': continue
        raw = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 drift')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'source Git blob drift')
        data[row['path']] = raw
    def pred(name, path): return load(name, ROOT/path, data[path])
    query = pred('paid_query', 'research/crt-uniform-rom-query/machine.py')
    native = pred('paid_native', 'research/crt-dense-guard-scan/machine.py')
    oracle = pred('paid_oracle', 'research/crt-mask-repair-bridge/key_subroutine.py')
    crt = pred('paid_crt', 'research/unconditional-batched-crt/check_batched_crt.py')
    caller = pred('paid_caller', 'research/crt-mask-repair-bridge/verify.py')
    service = load('paid_service', P/'service.py', (P/'service.py').read_bytes())
    return query, native, oracle, crt, caller, service


def schedule(crt):
    nets = [crt.benes(crt.rotation(8, 5, (2*a)%5 if a<3 else 0)) for a in range(4)]
    result = []
    for index in range(5):
        target = nets[0][index][0]
        need(all(n[index][0] == target for n in nets), 'source common target')
        table = [nets[a][index][1][b] for a in range(4) for b in range(8)]
        need(all(table[y] == table[y ^ (1 << target)] for y in range(32)), 'source target independence')
        result.append((target, table))
    return result


def program_bound(query, service, target):
    code, marks = service.assemble(query, target)
    ranges = tuple(zip(marks['entries'], marks['returns']))
    need(all(end-start == len(query.PROGRAM) for start,end in ranges), 'unaltered full query instruction ranges')
    def inside(pc): return any(start <= pc < end for start,end in ranges)
    rewinds = 0
    for pc, inst in enumerate(code):
        op, *a = inst
        if op in ('read', 'write', 'write_reg', 'move'):
            need(a[0] in service.ROLES, 'static tape role')
        if op in ('write', 'write_reg'): need(a[0] not in ('counter','rom'), 'no borrowed write')
        if op == 'read': need(a[0] != 'stream', 'append port never read')
        if op == 'move': need(a[1] in (-1,1), 'unit movement')
        destinations = a[1:] if op == 'branch' else a if op == 'jump' else []
        for dest in destinations:
            need(type(dest) is int and 0 <= dest < len(code), 'fixed control destination')
            if dest <= pc and not inside(pc):
                need(op == 'jump' and dest == pc-4, 'outside-query loop is one rewind')
                read, eq, branch, move, jump = code[pc-4:pc+1]
                need(read[0] == 'read' and eq == ('eq','scan','<' if read[1]=='counter' else 'L','test')
                     and read[1] in ('counter',*service.OWNED_WIDTHS) and read[2] == 'scan' and branch == ('branch','test',pc+1,pc-1)
                     and move == ('move',read[1],-1) and jump == ('jump',pc-4), 'exact rewind loop syntax')
                rewinds += 1
    outside = len(code)-3*len(query.PROGRAM)
    bound = 3*512*(32+1)*(4+2+2)**2 + 14*outside
    need(bound <= 3_300_000, 'declared complete instruction majorant')
    return dict(target=target, static_instructions=len(code), outside_query_instructions=outside,
                rewind_loops=rewinds, proved_instruction_bound=bound)


def snapshot(tape):
    return dict(tape.cells) if isinstance(tape.cells,dict) else dict(enumerate(tape.cells))


def audit(service, initial, initial_heads, expected_status='accept'):
    run = service.last; cells = {role:[data.get(i,'_') for i in range(max(data,default=-1)+1)] for role,data in initial.items()}
    heads = dict(initial_heads); regs = {}; pc=0; counts=Counter(); halted=False; epochs=[]; interface=0
    returns = set(service.marks['returns'])
    for listed_pc, observed in run['events']:
        need(not halted and listed_pc==pc, 'instruction/control continuity')
        if pc in returns:
            y=sum((cells['y'][j+1]=='1') << j for j in range(8))
            epochs.append(dict(y=y, bit=int(cells['out'][1])))
        op,*a=service.program[pc];pc+=1;counts[op]+=1
        if op in ('read','write','write_reg','move'):
            role=a[0];head=heads[role];need(head>=0,'nonnegative head')
            if role in ('counter','stream'):interface+=1
        if op=='read':
            value=cells[role][head] if head<len(cells[role]) else '_';need(observed==value,'read event value');regs[a[1]]=value
        elif op in ('write','write_reg'):
            need(role not in ('counter','rom'),'borrowed ownership');value=a[1] if op=='write' else regs[a[1]]
            need(observed==value,'write event value')
            while len(cells[role])<=head:cells[role].append('_')
            cells[role][head]=value
        else:
            need(observed is None,'noncell event payload')
            if op=='move':need(a[1] in (-1,1),'unit movement');heads[role]+=a[1];need(heads[role]>=0,'left boundary')
            elif op=='set':regs[a[0]]=a[1]
            elif op=='copy':regs[a[1]]=regs[a[0]]
            elif op=='eq':regs[a[2]]=regs[a[0]]==a[1]
            elif op=='eq_reg':regs[a[2]]=regs[a[0]]==regs[a[1]]
            elif op in ('xorbit','andbit','orbit'):
                need(regs[a[0]] in '01' and regs[a[1]] in '01','single-bit arithmetic operands')
                x=regs[a[0]]=='1';y=regs[a[1]]=='1';value=(x^y) if op=='xorbit' else (x&y) if op=='andbit' else (x|y)
                regs[a[2]]='1' if value else '0'
            elif op=='branch':need(type(regs[a[0]]) is bool,'Boolean branch');pc=a[1] if regs[a[0]] else a[2]
            elif op=='jump':pc=a[0]
            elif op=='halt':need(a[0]==expected_status,'halt status');halted=True
            else:raise ValueError('unknown audit opcode')
    need(halted and counts==run['census'] and pc==run['pc'] and regs==run['registers'],'complete independent instruction replay')
    for role,tape in run['tapes'].items():
        need(heads[role]==tape.head,'final head replay')
        need({i:x for i,x in enumerate(cells[role]) if x!='_'}=={i:x for i,x in snapshot(tape).items() if x!='_'},'final cell replay')
        if role in ('counter','rom'):need(cells[role]==[initial[role][i] for i in range(len(initial[role]))] and heads[role]==0,'borrowed restore')
        elif role=='stream':
            prefix=initial_heads[role];need(cells[role][:prefix]==[initial[role][i] for i in range(prefix)],'protected prefix')
            need(heads[role]==prefix+(12 if expected_status=='accept' else 0),'exact append cursor')
            if expected_status=='accept':need(all(x in '01' for x in cells[role][prefix:prefix+12]),'twelve appended bits')
        else:need(heads[role]==0 and all(x=='_' for x in cells[role]),'private erasure/head return')
    return epochs, interface


def case(modules,target,table,address,fault='correct',bad_input=None):
    query,native,oracle,crt,caller,impl=modules
    raw=format(address,'012b') if bad_input is None else bad_input
    counter=native.Tape(['<',*raw,'>']);rom=native.Tape(['L',*map(str,table),'R'])
    stream=native.Tape(['<',('R',819),('R',17),'_']);stream.head=3
    service=impl.Service(query,target,rom,fault)
    roles=dict(service.private,counter=counter,stream=stream,rom=rom)
    initial={r:snapshot(t) for r,t in roles.items()};heads={r:t.head for r,t in roles.items()}
    meter={'calls':0,'interface_actions':0};before=counter.actions+stream.actions
    if bad_input is not None:
        try:service.evaluate_key(counter,stream,meter,trace=True)
        except ValueError:pass
        else:raise ValueError('malformed address admitted')
        audit(service,initial,heads,'reject');return None
    service.evaluate_key(counter,stream,meter,trace=True)
    epochs,interface=audit(service,initial,heads)
    need(meter['interface_actions']==interface==counter.actions+stream.actions-before,'interface subset exact')
    ref=oracle.ReverseWordKey(target,table);trace=[];original_source=ref.source
    def observed(y):
        bit=original_source(y);trace.append(dict(y=y,bit=bit));return bit
    ref.source=observed;expected=ref.key_of(raw)
    actual=''.join(stream.cells[3:15]);need(actual==expected,'literal reverse-word key oracle')
    need(epochs==trace,'three current-state query epochs')
    need(sum(service.last['census'].values())<=3_300_000,'complete service instruction bound')
    return dict(address=address,target=target,key=actual,epochs=epochs,
                instructions=sum(service.last['census'].values()),interface_actions=interface,
                census=dict(sorted(service.last['census'].items()))),service,initial,heads


def must_fail(call,label):
    try:call()
    except ValueError:return
    raise ValueError('undetected control: '+label)


def components(modules):
    query,native,oracle,crt,caller,impl=modules
    bounds=[program_bound(query,impl,t) for t in (0,1,2)]
    rows=[];layers=schedule(crt)
    addresses=sorted(set([0,1,2,3,4,7,15,31,63,127,128,254,255,256,257,511,512,767,1023,1024,1535,2047,2048,3071,4094,4095]+[(u<<10)|(t<<8)|y for u in range(4) for t in range(4) for y in (3,124,252)]))
    for target,table in layers:
        for address in addresses:rows.append(case(modules,target,table,address)[0])
    parity=[(x>>1).bit_count()&1 for x in range(32)]
    for address in (0,1,3,7,31,127,255,1023,2047,4094,4095):rows.append(case(modules,0,parity,address)[0])
    controls={}
    for fault in ('stale','drop_high','omit_clear','omit_rom_return'):
        found=False
        for address in addresses:
            try:case(modules,0,parity,address,fault)
            except ValueError:
                controls[fault]=address;found=True;break
        need(found,'discriminating service mutant '+fault)
    for malformed in ('','0'*11,'0'*13,'000000_00000'):
        case(modules,0,parity,0,bad_input=malformed)
    row,srv,initial,heads=case(modules,0,parity,1023)
    events=list(srv.last['events']);index=next(i for i,(pc,_) in enumerate(events) if srv.program[pc][0]=='eq')
    srv.last['events']=events[:index]+events[index+1:];must_fail(lambda:audit(srv,initial,heads),'omitted control event')
    srv.last['events']=events[:-1];must_fail(lambda:audit(srv,initial,heads),'omitted return event')
    return dict(status='PASS_PAID_KEY_COMPONENT',bounds=bounds,accepted_cases=len(rows),rejected_addresses=4,
                behavior_mutants=controls,ledger_mutants=2,total_replayed_instructions=sum(r['instructions'] for r in rows),
                min_instructions=min(r['instructions'] for r in rows),max_instructions=max(r['instructions'] for r in rows),
                cases_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
                source_layers=[{'target':t,'rom':''.join(map(str,table))} for t,table in layers],
                service_sha256=hashlib.sha256((P/'service.py').read_bytes()).hexdigest())


def full_caller(modules):
    query,native,oracle,crt,caller,impl=modules
    env=caller.Env();layers=caller.schedule(env);target,table=layers[2]
    rom=env.BitTape(['L',*map(str,table),'R']);service=impl.Service(query,target,rom)
    original_bridge=env.bridge.evaluate_key;observed_calls=[]
    def paid_port(counter,out,key_function,meter):
        # Observer-only address log, required by the unchanged caller assertions.
        # It neither chooses an action nor supplies a key to the tape service.
        observed=int(''.join(counter.cells[1:13]),2)
        observed_calls.append(observed);key_function.__self__.addresses.append(observed)
        before=counter.actions+out.actions
        prior=meter['interface_actions'];service.evaluate_key(counter,out,meter,trace=False)
        need(meter['interface_actions']-prior==counter.actions+out.actions-before,'caller interface accounting subset')
        need(counter.head==rom.head==0 and all(t.head==0 and all(x=='_' for x in t.cells.values()) for t in service.private.values()),'per-call service ownership')
    env.bridge.evaluate_key=paid_port
    result=caller.run_layer(env,list(range(4096)),target,table)
    env.bridge.evaluate_key=original_bridge
    need(result['final']==result['ideal'],'actual repaired payload equals ideal layer')
    own=result['ownership']
    need(own['all_roles_blank'] and own['all_heads_returned'] and own['protected_payload_stream_kept_length'],'full caller ownership')
    need(own['good_addresses_evaluated']==own['hole_addresses_missed']==0 and own['key_calls']==result['bad']==own['distinct_key_addresses']==service.calls,'actual source mask exact calls')
    need(rom.cells==['L',*map(str,table),'R'] and rom.head==0,'borrowed source ROM unchanged')
    cell_actions=sum(service.totals[x] for x in ('read','write','write_reg','move'))
    interface=result['meter']['interface_actions'];need(interface<=cell_actions,'interface subset')
    return dict(status='PASS_ACTUAL_MIDDLE_LAYER_PAID_KEY',schedule_index=2,target=target,payloads=4096,
                calls=service.calls,marked_holes=result['bad'],good_addresses_evaluated=0,hole_addresses_missed=0,
                protected_payload_sha256=caller.digest(result['final']),producer_actions=result['producer_actions'],
                scanner_actions=result['scanner_actions'],repair_actions_including_key_interface=result['repair_actions'],
                key_instructions=sum(service.totals.values()),key_cell_actions=cell_actions,key_interface_actions=interface,
                repair_and_key_cell_actions=result['repair_actions']+cell_actions-interface,
                key_census=dict(sorted(service.totals.items())),all_roles_blank=True,all_heads_returned=True,
                scope='One original middle layer, unchanged source producer/scanner/repair with only evaluate_key replaced; raw macro/ROM preparation and outer Boolean control costs remain external.',
                service_sha256=hashlib.sha256((P/'service.py').read_bytes()).hexdigest())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--part',choices=('components','caller','all'),default='all');parser.add_argument('--write-result',action='store_true');args=parser.parse_args()
    modules=sources()
    for name,fn,file in [('components',components,'COMPONENT.json'),('caller',full_caller,'CALLER.json')]:
        if args.part not in (name,'all'):continue
        result=fn(modules)
        if args.write_result:(P/file).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        else:need(result==json.loads((P/file).read_text()),'frozen '+name+' receipt')
        print(json.dumps(result,sort_keys=True),flush=True)

if __name__=='__main__':main()
