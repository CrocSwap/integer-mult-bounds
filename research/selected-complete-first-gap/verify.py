"""Bounded literal first-gap replay; all host arithmetic is an external oracle.

Initial packets are supplied once. A successful full case executes one graph
entry through HALT without callbacks, decoded runtime words or host writes.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""
from pathlib import Path
from hashlib import sha256
from dataclasses import replace
import argparse
import ast
import copy
import gzip
import json
import sys
import types

HERE = Path(__file__).resolve().parent


def module(path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    sys.modules[name] = value
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value


G = module(HERE/'gap.py', '_checked_complete_first_gap')
P = G.predecessor()
C = P.lifetime()
Q = module(HERE/'inputs/first-donor/verify.py', '_frozen_first_donor_test_support')
V = Q.V
CPU = module(HERE/'cpu.py', '_first_gap_literal_cpu')
Program = CPU.program_class(C)
need = G.need


def must_fail(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('negative control escaped: '+label)


def source_check(archive=None):
    witness = json.loads((HERE/'SOURCE-PREFIX.json').read_text())
    G.source_binding(witness)
    if archive:
        raw = Path(archive).read_bytes()
        need(len(raw) == witness['source']['archive_bytes']
             and sha256(raw).hexdigest() == witness['source']['archive_sha256'],
             'original complete source archive')
        word = json.loads(gzip.decompress(raw))
        need(sha256(json.dumps(word, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
             == witness['source']['canonical_sha256'], 'canonical original source')
        need([[i, word['program'][i]] for i in G.EVENTS] == witness['events'],
             'complete five-event source extraction')
        need({str(k):word['frames'][k] for k in (3,601)} == witness['frames']
             and word['public'] == witness['public'], 'source frame/public inventory')
        frames = dict(enumerate(word['initial']))
        for index, event in enumerate(word['program'][:28042]):
            if index == 28037:
                need({str(k):frames[k] for k in (124,212,449,1349)}
                     == witness['initial_before_28037'] and 1526 not in frames,
                     'actual initial live/inactive prefix')
            op, owner = event[:2]
            if op == 'INIT':
                need(owner >= word['public'] and owner not in frames, 'actual INIT ownership')
                frames[owner] = event[2]
            elif op == 'CLEAR':
                need(owner >= word['public'] and frames.pop(owner) == event[2],
                     'actual CLEAR ownership/frame')
            elif op == 'MOVE':
                need(frames[owner] == event[2] and event[4] == (owner >= word['public']),
                     'actual MOVE ownership/frame')
                frames[owner] = event[3]
            elif op in ('ADD', 'COPY'):
                need(frames[owner] == frames[event[2]] == event[4], 'actual binary current frames')
            elif op == 'SCALE':
                need(frames[owner] == event[3], 'actual scalar current frame')
            else:
                raise ValueError('unknown source opcode')
        need({str(k):frames[k] for k in (124,212,449,1349,1526)} == witness['final_frames'],
             'actual complete prefix exit')
    controls = []
    for label, change in (
        ('wrong-half-coefficient', lambda x:x['events'][1][1].__setitem__(3, '1')),
        ('stale-212-source', lambda x:x['events'][3][1].__setitem__(2,449)),
        ('wrong-initial-frame', lambda x:x['initial_before_28037'].__setitem__('449',601)),
        ('wrong-source-order', lambda x:x['events'].__setitem__(slice(1,3),list(reversed(x['events'][1:3])))),
        ('wrong-frame137', lambda x:x['frames'].__setitem__('601',[239])),
    ):
        changed = copy.deepcopy(witness)
        change(changed)
        controls.append(must_fail(lambda:G.source_binding(changed), label))
    return {'typed_prefix_events':28042, 'events':witness['events'],
            'complete_archive_reextracted_this_run':bool(archive), 'controls':controls}


def row_key(rule):
    return rule.tests, rule.writes, rule.moves, rule.target


def graph_checks(graph, meta):
    original, old = P.compile_join()
    replaced = set(meta['replaced_C5_returns'])
    need(set(original.rules) <= set(graph.rules), 'lost retained source-producer row')
    for name, rows in original.rules.items():
        if name not in replaced:
            need([row_key(r) for r in rows] == [row_key(r) for r in graph.rules[name]],
                 'changed retained row: '+name)
    expected_next = {28037:28038, 28038:28039, 28039:28040, 28040:28041}
    for event in G.EVENTS:
        rows = graph.rules[meta['returns'][event]]
        destination = meta['entries'][expected_next[event]] if event in expected_next else 'HALT'
        need(len(rows) == 1 and row_key(rows[0]) == ((),(),(),destination),
             'fixed exact source continuation')
    need(graph.start == meta['entries'][28037], 'single literal source entry')
    source_ast = ast.parse((HERE/'inputs/first-donor/inputs/lifetime/protocol.py').read_bytes())
    cpu_ast = ast.parse((HERE/'cpu.py').read_bytes())
    def run_node(tree):
        candidates = [n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name == 'run']
        need(len(candidates) == 1, 'one literal run method')
        return ast.dump(candidates[0],include_attributes=False)
    need(run_node(source_ast) == run_node(cpu_ast), 'retained literal CPU method')
    need(len(graph.rules) == 71793 and G.digest(graph)
         == 'dbe04f2f719bf7c48ce02477871944a6c8ee1a6e1e73c331dc6c06d2de84ace7',
         'fixed45-tape graph identity')
    return {'retained_states':len(original.rules), 'changed_retained_return_edges':2,
            'new_states':len(graph.rules)-len(original.rules), 'states':len(graph.rules),
            'tapes':45, 'graph_sha256':G.digest(graph), 'literal_CPU_method_identical':True}


def history(state):
    return sum(b-a+1 for a,b in zip(state.lows,state.highs))


def install_text(state, tape, text):
    at = state.origins[tape]+1
    state.tapes[tape][at:at+len(text)] = bytes(C.SYMBOL[s] for s in text)
    state.highs[tape] = max(state.highs[tape],state.origins[tape]+len(text))


def new_state(capacity):
    origins = [17+i%7 for i in range(45)]
    tapes = [bytearray([6])*capacity for _ in origins]
    for tape, origin in zip(tapes,origins):
        tape[origin] = 2
        tape[origin-3:origin] = bytes((4,1,5))
        tape[-3:] = bytes((5,1,4))
    return C.State(tapes,origins.copy(),origins,origins.copy(),origins.copy(),[0]*45)


def half_graph(*, mutation=None):
    _, add, _ = C.inputs()
    graph = add.D.Graph()
    stages = {}
    graph.start = G.half_primitive(C.Relocate(graph), 'HALT', mutation=mutation, stages=stages)
    graph.execution_start = graph.start
    graph.validate()
    return graph, stages


def half_fixture(width, cutoff=1):
    header = ''.join(map(V.gamma,(1,1,1,1,width,cutoff)))
    low = -(1<<(width-1))
    high_even = (1<<(width-1))-2
    if width <= 7:
        sample = list(range(low,high_even+1,2))
    else:
        sample = [low,low+2,-2,0,2,high_even]
    values = [sample[i%len(sample)] for i in range(1024)]
    targets = [low+(i%min(1<<width,17)) for i in range(1024)]
    F = len(header)+1024*width
    state = new_state(4*(F+128))
    install_text(state,3,header+V.encode(values,width)+'|')
    install_text(state,4,header+V.encode(targets,width)+'|')
    state.highs[42] = state.origins[42]+F+97
    return state, {'width':width,'cutoff':cutoff,'header':header,'F':F,'values':values,
                   'targets':targets,'initial_history':history(state)}


def read_work(state,tape,length):
    at = state.origins[tape]+1
    raw = state.tapes[tape][at:at+length]
    need(all(x in (0,1) for x in raw) and state.tapes[tape][at+length] == 3,
         'exact working binary field and delimiter')
    return ''.join(str(x) for x in raw)


def half_returned(state,info,*,numeric=True,clean=True):
    if numeric:
        need(read_work(state,3,info['F']) == info['header']+V.encode([x//2 for x in info['values']],info['width']),
             'signed arithmetic half-copy oracle')
    need(read_work(state,4,info['F']) == info['header']+V.encode(info['targets'],info['width']),
         'half-copy target preservation')
    for t,(tape,origin) in enumerate(zip(state.tapes,state.origins)):
        need(state.heads[t] == origin and state.lows[t] >= origin, 'half-copy complete returned heads')
        need(tape[origin] == 2 and tape[origin-3:origin] == bytes((4,1,5))
             and tape[-3:] == bytes((5,1,4)), 'half-copy guards and opaque exteriors')
        if t not in (3,4) and clean:
            need(all(s == 6 for s in tape[origin+1:-3]), 'half-copy private cleanup')
        if t not in range(3,8):
            need(state.writes[t] == 0, 'half-copy unrelated owner writes')
    need(state.steps <= 4096*(info['F']+1), 'paid half-copy transition envelope')
    need(history(state)-info['initial_history'] <= 8*(info['F']+2), 'paid half-copy historical union')


def half_checks():
    graph, _ = half_graph()
    program = Program(graph)
    cases = []
    for width,cutoff in ((2,1),(3,1),(6,1),(17,1),(129,(1<<2048)+3)):
        state,info = half_fixture(width,cutoff)
        program.run(state)
        half_returned(state,info)
        cases.append({'width':width,'cutoff_bits':cutoff.bit_length(),'header_bits':len(info['header']),
                      'components':1024,'transitions':state.steps,
                      'history_increment':history(state)-info['initial_history']})
    controls = []
    bad,_ = half_graph(mutation='zero-fill')
    state,info = half_fixture(6)
    Program(bad).run(state)
    half_returned(state,info,numeric=False)
    controls.append({'name':'returning-zero-fill', 'transitions':state.steps,
                     'detected':must_fail(lambda:half_returned(state,info),'signed-half-numeric-oracle')})
    bad,_ = half_graph()
    changed = 0
    for name,rows in list(bad.rules.items()):
        if name.startswith('half-retire-width.'):
            for i,rule in enumerate(rows):
                if rule.writes == ((6,'_'),):
                    rows[i] = replace(rule,writes=())
                    changed += 1
    need(changed == 1,'one missing width-retirement mutation')
    state,info = half_fixture(6)
    Program(bad).run(state)
    half_returned(state,info,clean=False)
    controls.append({'name':'returning-unretired-width','transitions':state.steps,
                     'detected':must_fail(lambda:half_returned(state,info),'private-width-retirement-oracle')})
    for label,mutate in (
        ('late-odd-component',lambda s,i:s.tapes[3].__setitem__(s.origins[3]+i['F'],1)),
        ('short-source-word',lambda s,i:s.tapes[3].__setitem__(s.origins[3]+i['F']-1,3)),
        ('unequal-header',lambda s,i:s.tapes[4].__setitem__(s.origins[4]+1,0)),
        ('aliased-owners',lambda s,i:s.tapes.__setitem__(4,s.tapes[3])),
    ):
        state,info = half_fixture(6)
        mutate(state,info)
        controls.append({'name':label,'detected':must_fail(lambda:program.run(state),label),
                         'transitions_before_rejection':state.steps})
    return {'states':len(graph.rules),'cases':cases,'controls':controls}


def bank_checks():
    _,add,_ = C.inputs()
    cases = []
    for F in (2,3,17,129):
        fields = [''.join(str((i+j)//(j+1)%2) for i in range(F)) for j in range(3)]
        for selected in range(3):
            for gather in (True,False):
                graph = add.D.Graph()
                graph.start = G.bank_transfer(graph,selected,3,gather,'HALT')
                graph.validate()
                state = new_state(8*(F+32))
                install_text(state,44,'|'.join(fields)+'|$')
                replacement = ''.join('1' if bit == '0' else '0' for bit in fields[selected])
                if not gather:
                    install_text(state,3,replacement+'|')
                Program(graph).run(state)
                expected = list(fields)
                if not gather:
                    expected[selected] = replacement
                need(V.body(state,44,3) == tuple(expected),'fixed selected three-field bank transfer')
                need(all(h == o for h,o in zip(state.heads,state.origins)), 'complete bank/work returns')
                if gather:
                    need(read_work(state,3,F) == fields[selected],'gather exact field')
                else:
                    need(all(x == 6 for x in state.tapes[3][state.origins[3]+1:-3]),
                         'scatter retires complete work')
                need(state.steps == 7*F+12,'exact three-field transfer count')
                cases.append({'F':F,'selected':selected,'gather':gather,'transitions':state.steps})
    # A returned copy from a valid but wrong slot must fail the position oracle.
    graph = add.D.Graph()
    graph.start = G.bank_transfer(graph,2,3,True,'HALT')
    state = new_state(256)
    install_text(state,44,'000|101|111|$')
    Program(graph).run(state)
    need(all(h == o for h,o in zip(state.heads,state.origins)), 'wrong-position returns')
    control = must_fail(lambda:need(read_work(state,3,3) == '101','requested owner212 slot'),
                        'returning-wrong-owner-position')
    return {'cases':cases,'controls':[control]}


def fixture():
    state,info = V.fixture(width=6,cutoff=1)
    A = [k%5-2 for k in range(1024)]
    B = [2*(k%7-3) for k in range(1024)]
    D = [1-k%3 for k in range(1024)]
    origin = 29
    tape = bytearray([6])*len(state.tapes[0])
    tape[origin] = 2
    tape[origin-3:origin] = bytes((4,1,5))
    tape[-3:] = bytes((5,1,4))
    state.tapes.append(tape)
    state.heads.append(origin)
    state.origins.append(origin)
    state.lows.append(origin)
    state.highs.append(origin)
    state.writes.append(0)
    info.update(A=A,B=B,C=D)
    set_public(state,info,A=A,B=B,D=D)
    info['initial_history'] = history(state)
    return state,info


def set_public(state,info,*,A=None,B=None,D=None):
    for key,value in (('A',A),('B',B),('C',D)):
        if value is not None:
            info[key] = value
    packets = [info['header']+V.encode(info[k],info['width']) for k in ('C','A','B')]
    install_text(state,44,'|'.join(packets)+'|$')


def expected_fields(info,*,skip=False):
    image = Q.direct_image(info['donors'][0])
    A = info['A'] if skip else [a+b//2 for a,b in zip(info['A'],info['B'])]
    D = [c+a for c,a in zip(info['C'],A)]
    public = tuple(info['header']+V.encode(v,info['width']) for v in (D,A,info['B']))
    old_bank = tuple([info['header']+V.encode(image,info['width'])]+info['packets'][1:])
    owned = (info['header']+V.encode([-x for x in image],info['width']),)
    return public,old_bank,owned


def full_returned(state,info,identities,*,skip=False):
    V.returned(state,info)
    public,old_bank,owned = expected_fields(info,skip=skip)
    need(V.body(state,44,3) == public,'all124/212/449 public endpoints')
    need(V.body(state,43,5) == old_bank,'productive1349 and four spectators')
    need(V.body(state,2) == owned,'owned1526 consumes literal producer')
    need(tuple(id(state.tapes[t]) for t in (2,43,44)) == identities,'same physical owner arrays')
    limit = 2**20*(info['V_old']+info['E_old']+1)+2**24*(info['V']+len(info['header'])+1)+32768*(info['F']+1)+128
    need(state.steps <= limit,'complete five-event transition bound')
    need(history(state)-info['initial_history'] <= 64*(info['V_old']+info['E_old']+3)+4096*(info['F']+2),
         'complete five-event history bound')


def full_checks(graph,meta):
    program = Program(graph)
    state,info = fixture()
    identities = tuple(id(state.tapes[t]) for t in (2,43,44))
    need(any(info['B']) and Q.direct_image(info['donors'][0]) != info['donors'][0],
         'nontrivial additional ADDs and producer')
    program.run(state)
    full_returned(state,info,identities)
    result = {'single_uninterrupted_run':True,'transitions':state.steps,
              'history_increment':history(state)-info['initial_history'],
              'V_old':info['V_old'],'E_old':info['E_old'],'V':info['V'],'E':len(info['header']),
              'F':info['F'],'width':info['width'],'cutoff':info['cutoff'],
              'checked_public_owners':[124,212,449,1349],'checked_owned_owner':1526,
              'returned_heads':len(state.heads),'preserved_private_bodies':40}
    controls = []
    bad,_ = G.compile_gap(mutation='skip-28038')
    stale,initial = fixture()
    ids = tuple(id(stale.tapes[t]) for t in (2,43,44))
    Program(bad).run(stale)
    full_returned(stale,initial,ids,skip=True)
    need(V.body(stale,2) == expected_fields(initial)[2]
         and V.body(stale,43,5) == expected_fields(initial)[1],
         'skipped ADD preserves owned and donor endpoint, exposing weak oracle')
    controls.append({'name':'returning-skipped28038','transitions':stale.steps,
                     'owned_only_oracle_would_miss':True,
                     'detected':must_fail(lambda:full_returned(stale,initial,ids),'all-public-endpoint-oracle')})
    for label in ('odd-half-source','first-ADD-overflow','later-MOVE-overflow'):
        failed,initial = fixture()
        if label == 'odd-half-source':
            B = initial['B'].copy()
            B[-1] = 1
            set_public(failed,initial,B=B)
        elif label == 'first-ADD-overflow':
            A,B = initial['A'].copy(),initial['B'].copy()
            A[0],B[0] = 31,2
            set_public(failed,initial,A=A,B=B)
        else:
            values = [0]*1024
            values[2*258] = -32 # packed address258, real component516; native address129
            need(all(-32 <= x < 32 for x in Q.direct_image(values)),
                 'complete MOVE endpoint fits despite first-phase overflow')
            Q.set_initial_donor(failed,initial,values)
        original_public = V.body(failed,44,3)
        original_old = V.body(failed,43,5)
        controls.append({'name':label,'detected':must_fail(lambda:program.run(failed),label),
                         'transitions_before_rejection':failed.steps})
        need(V.body(failed,43,5) == original_old,'failing MOVE or earlier contact changed source bank')
        need(V.body(failed,2) == (initial['header']+'0'*initial['V'],),
             'earlier INIT remains committed')
        if label == 'later-MOVE-overflow':
            A = [a+b//2 for a,b in zip(initial['A'],initial['B'])]
            expected = (original_public[0],initial['header']+V.encode(A,initial['width']),original_public[2])
            need(V.body(failed,44,3) == expected and expected != original_public,
                 'later failure preserves earlier completed ADD, without global rollback')
            controls[-1]['prior_ADD_remains_committed'] = True
        else:
            need(V.body(failed,44,3) == original_public,'failing new ADD public contents changed')
        controls[-1]['prior_INIT_remains_committed'] = True
    alias,info = fixture()
    alias.tapes[44] = alias.tapes[43]
    controls.append({'name':'full-bank-owner-alias',
                     'detected':must_fail(lambda:program.run(alias),'full-bank-owner-alias'),
                     'transitions_before_rejection':alias.steps})
    return {'positive':result,'controls':controls}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive')
    parser.add_argument('--half-only',action='store_true')
    args = parser.parse_args()
    pins = G.authenticate()
    result = {'status':'PASS','source':source_check(args.archive),
              'exact_retained_inputs':len(pins['files']), 'half':half_checks(), 'bank':bank_checks()}
    if not args.half_only:
        graph,meta = G.compile_gap()
        result['graph'] = graph_checks(graph,meta)
        result['full'] = full_checks(graph,meta)
    result['scientific_sha256'] = {name:sha256((HERE/name).read_bytes()).hexdigest()
                                  for name in ('gap.py','cpu.py','verify.py')}
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
