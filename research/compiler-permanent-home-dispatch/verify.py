"""Exact source, chronology, literal tape and corruption checks. Apache-2.0."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from emit import Emitter, L
import independent as I
from tape_graph import compile_graph, initial_tapes, decoded, Tape

def require(condition, message):
    if not condition:
        raise ValueError(message)


def frozen():
    source = json.loads((HERE/'SOURCES.json').read_text())
    for entry in source['files']:
        data = (HERE/entry['local']).read_bytes()
        require(sha256(data).hexdigest() == entry['sha256'] and len(data) == entry['bytes'],
                'changed frozen scientific input')


def script(roles, rounds, owned):
    first, last, bank = roles[0][0], roles[-1][0], owned[0]
    segments = [(('XOR', (first, bank)),)]
    for j in range(len(rounds)):
        segments.append((('XOR', (bank, last)), ('NOT', (bank,))))
    return tuple(segments)


def fixture(roles, rounds, ambient, root, field_width, adapter=lambda _: 'REV'):
    owned = ('bank',)
    rows, flows = I.O.library(roles, rounds, owned, ambient, root)
    compiler = L.Compiler(L.C.Rule(roles, rounds, owned, ambient), rows, 'dispatch')
    segments = script(roles, rounds, owned)
    events, homes = Emitter(compiler, segments, adapter).compile()
    payloads = tuple(''.join('1' if ((row+1)*(i+3)+i*i+row//2) % 5 < 2 else '0'
                             for i in range(field_width)) for row in range(rows[root].width))
    expected_events, expected_homes, expected_values = I.run(
        roles, rounds, owned, ambient, root, rows, flows, segments, adapter, payloads)
    actual_events = tuple((e.kind, e.service, I.normalize(e.owners), I.normalize(e.context))
                          for e in events)
    require(actual_events == expected_events, 'full native/checkpoint/frame chronology')
    require(I.normalize(homes) == expected_homes, 'permanent home owner correspondence')
    leaves = [e for e in events if e.kind == 'leaf']
    require(len(leaves) == rows[root].leaves, 'actual compiler leaf census')
    for j, event in enumerate(leaves):
        leaf = compiler.locate(j)
        require(event.owners == (leaf.field,) and event.context == (leaf.calls, leaf.rank, leaf.axis),
                'exact frozen chronological leaf projection')
    graph = compile_graph(events, homes, productive_count=len(payloads))
    tapes = initial_tapes(payloads, len(homes))
    reserved = sum(t.peak for t in tapes)
    initial = payloads+('0'*field_width,)*(len(homes)-len(payloads))
    direct = {I.normalize(owner): bits for owner,bits in zip(homes,initial)}
    audited_until, boundaries = -1, 0
    def checkpoint(index, actual):
        nonlocal audited_until, boundaries
        for event in events[audited_until+1:index+1]:
            I.apply(direct,event.service,I.normalize(event.owners))
        audited_until, boundaries = index, boundaries+1
        require(decoded(actual,len(homes)) == tuple(direct[I.normalize(o)] for o in homes),
                'physical boundary disagrees with exact service and parked spectators')
        require(all(t.head == 0 for t in actual), 'interior service did not return every head')
        require(all(set(t.contents()[1:]) <= {'_'} for t in actual[1:]),
                'interior service retained an unerased physical working copy')
    steps = graph.run(tapes, checkpoint=checkpoint)
    require(decoded(tapes, len(homes)) == expected_values, 'physical payload delivery')
    require(all(t.head == 0 for t in tapes), 'full physical head return')
    require(all(set(t.contents()[1:]) <= {'_'} for t in tapes[1:]), 'scratch erased physically')
    require(all(value == '0'*field_width for value in expected_values[len(payloads):]),
            'all private homes retired at the full root extent')
    require(tapes[0].peak == len(homes)*(field_width+1)+2, 'home backing retained exactly')
    require(all(t.peak <= field_width+2 for t in tapes[1:]), 'fixed work bank backing')
    q = sum(bool(e.service) for e in events)
    require(boundaries == q, 'all physical service returns inspected')
    require(steps <= 64*(q+1)*(len(homes)+1)*(field_width+2), 'universal fixture step envelope')
    require(len(graph.rules) <= 64*(q+1)*(len(homes)+1), 'output graph state envelope')
    receipt = {'roles':roles,'rounds':rounds,'ambient':ambient,'rank':root,'F':field_width,
               'B':len(payloads),'K':len(homes),'events':len(events),'services':q,
               'leaves':len(leaves),'states':len(graph.rules),'steps':steps,'audited_boundaries':boundaries,
               'initial_reserved':reserved,'historical_backing':sum(t.peak for t in tapes),
               'events_sha256':sha256(repr(actual_events).encode()).hexdigest(),
               'values_sha256':sha256(repr(expected_values).encode()).hexdigest()}
    return receipt, events, homes, payloads, expected_values


def controls(events, homes, payloads, expected):
    controls = []
    def changed(name, altered):
        tapes = initial_tapes(payloads, len(homes))
        try:
            compile_graph(altered, homes,productive_count=len(payloads)).run(tapes)
            require(decoded(tapes, len(homes)) != expected, name+' escaped detection')
        except (KeyError, ValueError) as error:
            if str(error).endswith('escaped detection'):
                raise
        controls.append(name)
    leaf = next(i for i,e in enumerate(events) if e.kind == 'leaf')
    changed('dropped_paid_leaf', events[:leaf]+events[leaf+1:])
    pop = next(i for i,e in enumerate(events) if e.kind == 'pop')
    changed('missing_whole_job_return', events[:pop]+events[pop+1:])
    release = next(i for i,e in enumerate(events) if e.kind == 'release')
    changed('erased_productive_home', events[:release]+(replace(events[release], owners=(homes[0],)),)+events[release+1:])
    native = next(i for i,e in enumerate(events) if e.service == 'XOR')
    aliased = replace(events[native], owners=(events[native].owners[0],)*2)
    changed('simultaneous_owner_alias', events[:native]+(aliased,)+events[native+1:])
    wrong = replace(events[leaf], owners=(homes[(homes.index(events[leaf].owners[0])+1) % len(homes)],))
    changed('wrong_source_or_bank_route', events[:leaf]+(wrong,)+events[leaf+1:])
    changed('same_rank_different_cut_coalescing', tuple(e for i,e in enumerate(events)
                                                     if i == leaf or e.kind != 'leaf'))
    try:
        compile_graph(events, homes+(homes[-1],))
    except ValueError:
        controls.append('duplicate_permanent_owner_home')
    else:
        raise ValueError('duplicate home was accepted')
    graph = compile_graph(events, homes,productive_count=len(payloads))
    first_state = next(state for state in graph.rules if state.startswith('erase'))
    graph.rules[first_state] = [replace(rule,writes=()) for rule in graph.rules[first_state]]
    tapes = initial_tapes(payloads,len(homes))
    graph.run(tapes)
    require(any(set(t.contents()[1:]) - {'_'} for t in tapes[1:]), 'scratch-retirement fault escaped')
    controls.append('omitted_work_bank_erasure')
    graph = compile_graph(events,homes,productive_count=len(payloads))
    tapes = initial_tapes(payloads,len(homes))
    try:
        graph.run(tapes,start=graph.execution_start)
    except ValueError:
        controls.append('omitted_physical_home_reservation')
    else:
        raise ValueError('unprepared owned homes were accepted')
    with tempfile.TemporaryDirectory(prefix='_source-fault-',dir=HERE.parent) as directory:
        target=Path(directory)
        for name in ('inputs','reference'):
            shutil.copytree(HERE/name,target/name)
        for name in ('emit.py','SOURCES.json'):
            shutil.copy2(HERE/name,target/name)
        damaged=target/'inputs/leaf_index.py'
        damaged.write_bytes(damaged.read_bytes()+b'\n# altered scientific source\n')
        command=[sys.executable,'-I','-B','-c',
                 'import sys; sys.path.insert(0,'+repr(str(target))+'); import emit']
        result=subprocess.run(command,capture_output=True,text=True)
        require(result.returncode != 0 and 'changed frozen scientific input' in result.stderr,
                'actual frozen-input corruption was accepted')
    controls.append('changed_frozen_owner_resolver')
    return controls


def main():
    frozen()
    cases = []
    for roles, rounds, ambient, ranks in [
        ((('x',2),('y',3)), ((1,'x'),(1,'bank')), 3, (3,4,5,6)),
        ((('x',2),('y',2)), ((1,'x'),(1,'bank')), 2, (2,3,4)),
        ((('x',3),('y',4)), ((1,'bank'),(2,'x')), 5, (4,5,6,7)),
    ]:
        for n in ranks:
            for width in (1,3,8):
                result = fixture(roles, rounds, ambient, n, width)
                cases.append(result[0])
    # Choose a nontrivial source/complement/owned fixture for fault controls.
    chosen = fixture((('x',2),('y',3)), ((1,'x'),(1,'bank')), 3, 6, 8)
    rejecting = controls(*chosen[1:])
    long = fixture((('x',2),('y',3)), ((1,'x'),(1,'bank')), 3, 6, 257)[0]
    width_cases = [a for a in cases if a['roles'] == (('x',2),('y',3)) and a['rank'] == 6]
    low, mid, high = sorted(width_cases,key=lambda a:a['F'])
    slope, rem = divmod(mid['steps']-low['steps'],mid['F']-low['F'])
    require(rem == 0 and high['steps'] == low['steps']+slope*(high['F']-low['F'])
            and long['steps'] == low['steps']+slope*(long['F']-low['F']), 'literal runtime is not affine in F')
    require(long['states'] == low['states'] and long['events_sha256'] == low['events_sha256'],
            'template controller changed with input field extent')
    # Exact reuse of the SAME four Tape objects, including historical capacity.
    receipt, events, homes, payloads, expected = chosen
    tapes = initial_tapes(payloads, len(homes))
    graph = compile_graph(events, homes,productive_count=len(payloads))
    graph.run(tapes)
    previous_backing = sum(t.peak for t in tapes)
    public_now = decoded(tapes,len(homes))[:len(payloads)]
    values = {I.normalize(owner): data for owner,data in zip(homes,decoded(tapes,len(homes)))}
    for event in events:
        I.apply(values,event.service,I.normalize(event.owners))
    graph.run(tapes,start=graph.execution_start)
    require(decoded(tapes,len(homes)) == tuple(values[I.normalize(o)] for o in homes), 'reuse changed physical result')
    require(sum(t.peak for t in tapes) == previous_backing and all(t.head == 0 for t in tapes),
            'reuse discarded historical backing or head returns')
    scan_scaling=[]
    from emit import Event
    for q in (1,2,4,8):
        owners=tuple(L.SourceRow('scan-cost',i) for i in range(q))
        word=tuple(Event('native','NOT',(owner,),()) for owner in owners)
        graph=compile_graph(word,owners,productive_count=q)
        machine=initial_tapes(('01011001101',)*q,q)
        steps=graph.run(machine)
        require(steps >= 4*q*q*12 and len(graph.rules) >= 2*q*q,
                'scan route hid its output-squared factor')
        scan_scaling.append({'Q':q,'K':q,'F':11,'steps':steps,'states':len(graph.rules)})
    monitor=Tape()
    for _ in range(17):
        monitor.move(1)
    require(monitor.read() == '_' and monitor.peak == 18 and len(monitor.visited) == 18,
            'historical monitor ignored blank head travel')
    for _ in range(17):
        monitor.move(-1)
    require(monitor.peak == 18,'historical monitor shrank after head return')
    result = {'claim':'source-indexed physical dispatch under supplied primitive contracts',
              'case_count':len(cases),'cases':cases,'negative_controls':rejecting,
              'same_object_reuse':True,'max_tapes':4,'long_field':long,'fixed_graph_step_slope':slope,
              'scan_cost_scaling':scan_scaling,
              'python':sys.version.split()[0],
              'scope':'fixture primitives only; no selected multiplier or native semantic audit'}
    path = HERE/'VALIDATION.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(result,indent=2)+'\n')
    elif path.exists():
        saved=json.loads(path.read_text())
        saved.pop('python',None)
        compare=dict(result);compare.pop('python',None)
        # Canonical JSON preserves bool/int distinctions and normalizes tuples
        # to the array representation used by the retained receipt.
        require(json.dumps(saved,sort_keys=True,separators=(',',':')) ==
                json.dumps(compare,sort_keys=True,separators=(',',':')),
                'validation scientific payload changed')
    print('PASS_COMPILER_PERMANENT_HOME_DISPATCH',len(cases),'cases;',len(rejecting),'rejecting controls')


if __name__ == '__main__':
    main()
