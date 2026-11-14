"""Pre-MOVE source production and unchanged first-SUB literal verification.

Packet setup/oracles are verifier-only. No nonzero host write occurs after
entering any successful producer chain. Apache-2.0; OpenAI-assisted work
prepared for @CubeJerry with retained predecessor credit.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import copy
import gzip
import json

HERE = Path(__file__).resolve().parent
import types
import sys


def module(path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    sys.modules[name] = value
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__)
    return value


P = module(HERE/'producer.py','_checked_first_donor_producer')
C = P.lifetime()
# Frozen setup, returned-owner and capability observers, not numeric MOVE oracle.
V = module(HERE/'inputs/lifetime/verify.py','_frozen_lifetime_test_support')
need = P.need


def must_fail(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('negative control escaped: '+label)


def source_check(archive=None):
    witness = json.loads((HERE/'SOURCE-EVENT.json').read_text())
    P.source_binding(witness)
    result = {'exact_event':witness['event'],'index':witness['index'],
              'frames':witness['frames'],'pre_MOVE_frames':witness['current_frames_before_MOVE'],
              'two_unimplemented_paid_events':[28038,28040],
              'complete_archive_reextracted_this_run':bool(archive)}
    if archive:
        raw = Path(archive).read_bytes()
        need(len(raw) == witness['source']['archive_bytes']
             and sha256(raw).hexdigest() == witness['source']['archive_sha256'], 'full source archive')
        word = json.loads(gzip.decompress(raw))
        need(sha256(json.dumps(word,separators=(',',':'),sort_keys=True).encode()).hexdigest()
             == witness['source']['canonical_sha256'], 'full canonical source')
        need([[i,word['program'][i]] for i in range(28037,28042)] == witness['first_contacts'],
             'complete first-gap extraction')
        need({str(k):word['frames'][k] for k in (3,601)} == witness['frames'], 'source frame extraction')
        frames = dict(enumerate(word['initial']))
        for event in word['program'][:28039]:
            op,owner = event[:2]
            if op == 'INIT':
                need(owner not in frames,'live source INIT')
                frames[owner] = event[2]
            elif op == 'CLEAR':
                need(frames.pop(owner) == event[2],'source CLEAR frame')
            elif op == 'MOVE':
                need(frames[owner] == event[2],'source MOVE frame')
                frames[owner] = event[3]
            elif op in ('ADD','COPY'):
                need(frames[owner] == frames[event[2]] == event[4],'source binary frames')
            elif op == 'SCALE':
                need(frames[owner] == event[3],'source SCALE frame')
            else:
                raise ValueError('unknown source opcode')
        need({str(k):frames[k] for k in (1349,1526)} == witness['current_frames_before_MOVE'],
             'actual complete-prefix current frame')
    controls = []
    for name, change in (
        ('wrong-frame239', lambda w:w['frames'].__setitem__('601',[239])),
        ('wrong-source-owner', lambda w:w['event'].__setitem__(1,415)),
        ('stale-pre-MOVE-frame', lambda w:w['current_frames_before_MOVE'].__setitem__('1349',601)),
        ('deleted-unrelated-chronology', lambda w:w['first_contacts'].pop(1)),
    ):
        altered = copy.deepcopy(witness)
        change(altered)
        controls.append(must_fail(lambda:P.source_binding(altered),name))
    result['binding_controls'] = controls
    return result


def exact_source_algebra():
    ref = HERE/'inputs/lifetime/inputs/move/reference/source'
    sparse = module(ref/'native_verify.py','_independent_donor_sparse_source')
    dense = module(ref/'clifford_exact.py','_independent_donor_dense_source')
    source = sparse.frame([137],9)
    other = dense.canonical_frame(9,[137])
    word = C.inputs()[2].C.LINEAR.cnot_word(P.G)
    canonical = (('D',P.Q,P.ALPHA),('P',sparse.inverse(P.G)),('C',1,1),
                 ('P',P.G),('D',P.Q,P.ALPHA))
    for x in range(512):
        sign = -1 if (x & 9).bit_count()%2 else 1
        expected = {x:(1,1),x^137:(sign,-sign)}
        need(sparse.state(source,x) == (expected,1),'source/direct Pauli formula')
        need(sparse.state(canonical,x) == (expected,1),'source/canonical factor equality')
        values,denominator = other.zero_state(x)
        need(denominator == 1 and {y:v for y,v in enumerate(values) if v != (0,0)} == expected,
             'independent dense original-frame equality')
        at = x
        for target,control in word:
            at ^= ((at>>control)&1)<<target
        need(at == sparse.mul(P.G,x),'fixed G word')
        for target,control in reversed(word):
            at ^= ((at>>control)&1)<<target
        need(at == x,'reversed G word')
    need(sparse.state(sparse.frame([239],9),0) != sparse.state(source,0),
         'wrong239 operator must be separated')
    return {'all512_columns':'original sparse source, separate dense source, closed Pauli formula and five fixed factors agree',
            'fixed_G_word_length':len(word),'inverse_word_length':len(word),
            'native_xor':137,'native_sign_mask':9,'packed_f1_xor':290,'packed_f1_sign_mask':288,
            'wrong239_source_column_separated':True}


def direct_image(values):
    """Independent f=1 packed-address formula, no factor/oracle helper call."""
    need(len(values) == 1024,'complete512-address one-coefficient fixture')
    output = [0]*1024
    for x in range(512):
        ar,ai = values[2*x:2*x+2]
        br,bi = values[2*(x^290):2*(x^290)+2]
        sign = -1 if (x & 288).bit_count()%2 else 1
        real = ar-ai+sign*(br+bi)
        imag = ar+ai+sign*(bi-br)
        need(real%2 == imag%2 == 0,'direct source image integrality')
        output[2*x:2*x+2] = [real//2,imag//2]
    return output


def verify_retained_rows(graph):
    original,meta = C.compile_protocol()
    shared = set(graph.rules)&set(original.rules)
    need(shared,'missing frozen contact rows')
    need(all(graph.rules[name] == original.rules[name] for name in shared),
         'changed frozen INIT/SUB instruction')
    for event in (28037,28041):
        stack,seen = [meta['entries'][event]],set()
        while stack:
            name = stack.pop()
            if name == 'HALT' or name in seen:continue
            need(name in shared,'pruned reachable frozen contact state')
            seen.add(name)
            stack.extend(r.target for r in original.rules[name])
    return len(shared)


def check_producer_footprint(graph, entry):
    stack,seen,ports = [entry],set(),set()
    while stack:
        name = stack.pop()
        if name == 'HALT' or name in seen:continue
        seen.add(name)
        for r in graph.rules[name]:
            for sequence in (r.tests,r.writes,r.moves):
                ports.update(t for t,_ in sequence)
            stack.append(r.target)
    need(not ports & {0,1,2},'producer touches protected old/source/owned HOME')
    need(ports <= set(range(3,37))|{43},'producer unexpected private owner')
    return {'reachable_states':len(seen),'physical_ports':sorted(ports),
            'owned1526_never_touched':True}


def set_initial_donor(state, info, values):
    """Fixture construction BEFORE literal entry, never a continuation."""
    packet = info['header']+V.encode(values,info['width'])
    begin = state.origins[43]+1
    state.tapes[43][begin:begin+len(packet)] = bytes(C.SYMBOL[s] for s in packet)
    info['donors'][0] = values
    info['packets'][0] = packet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive')
    args = parser.parse_args()
    pins = P.authenticate()
    source = source_check(args.archive)
    algebra = exact_source_algebra()
    graph,meta = P.compile_join()
    need(len(graph.rules) == 71524 and P.digest(graph) == 'fec60dd4653c6c06846850b2d318d9eec0b7d9856af6b65bae2d336d5c5f99a0',
         'frozen source-producer graph')
    shared = verify_retained_rows(graph)
    footprint = check_producer_footprint(graph,meta['entries'][28039])
    program = C.Program(graph)
    # cutoff1 deliberately admits this rank-one source and first SUB while
    # failing the later2f rank-two requirement. No later admission is inferred.
    state,info = V.fixture(cutoff=1)
    original_home = state.tapes[2]
    original_bank = state.tapes[43]
    before_value = list(info['donors'][0])
    expected = direct_image(before_value)
    need(expected != before_value and any(expected[1::2]),'nontrivial complex produced field')
    costs = []
    start = state.steps
    program.run(state,start=meta['entries'][28037])
    costs.append({'event':28037,'transitions':state.steps-start})
    V.returned(state,info)
    zero_boundary = state.clone()
    need(V.body(state,2) == (info['header']+'0'*info['V'],),'literal INIT zero')
    start = state.steps
    program.run(state,start=meta['entries'][28039])
    costs.append({'event':28039,'transitions':state.steps-start})
    V.returned(state,info)
    V.check_gap_state(zero_boundary,state)
    need(state.writes[2] == zero_boundary.writes[2],'producer wrote owned1526')
    external = V.body(state,43,5)
    need(external == tuple([info['header']+V.encode(expected,info['width'])]+info['packets'][1:]),
         'same-owner actual source production and spectator fields')
    produced_boundary = state.clone()
    start = state.steps
    program.run(state,start=meta['entries'][28041])
    costs.append({'event':28041,'transitions':state.steps-start})
    V.returned(state,info)
    need(V.body(state,2) == (info['header']+V.encode([-x for x in expected],info['width']),),
         'unchanged first SUB consumes produced value')
    need(V.body(state,43,5) == external,'SUB changed donor or other external owners')
    need(state.tapes[2] is original_home and state.tapes[43] is original_bank,'physical owner replacement')
    limit = 2**20*(info['V_old']+info['E_old']+1)+2**24*(info['V']+len(info['header'])+1)+8192*(info['F']+1)+128
    history = sum(b-a+1 for a,b in zip(state.lows,state.highs))-info['initial_history']
    need(state.steps <= limit,'complete producer+SUB+INIT bill')
    need(history <= 64*(info['V_old']+info['E_old']+3)+2048*(info['F']+2),'historical union envelope')
    controls = []
    for mutation in ('wrong-phase','stale-donor'):
        bad_graph,bad_meta = P.compile_join(mutation=mutation)
        bad = zero_boundary.clone()
        start = bad.steps
        C.Program(bad_graph).run(bad,start=bad_meta['entries'][28039])
        V.returned(bad,info)
        V.check_gap_state(zero_boundary,bad)
        C.Program(bad_graph).run(bad,start=bad_meta['entries'][28041])
        V.returned(bad,info)
        need(V.body(bad,2) != V.body(state,2),'returning mutation was not separated')
        controls.append({'control':mutation,'literal_transitions':bad.steps-start,
                         'returns_all_capabilities':True,'direct_source_then_SUB_oracle_detected':True})
    # Actual source endpoint fits, but the first canonical D negates MIN.
    bad,binfo = V.fixture(cutoff=1)
    values = [0]*1024
    values[2*258] = -32 # native129: x7=1,x0=1,x3=0, reversed-nine-bit address258
    final = direct_image(values)
    need(all(-32 <= value < 32 for value in final),'endpoint-fit phase counterexample')
    set_initial_donor(bad,binfo,values)
    program.run(bad,start=meta['entries'][28037])
    bank_before,owned_before = bytes(bad.tapes[43]),bytes(bad.tapes[2])
    start = bad.steps
    controls.append({'control':must_fail(lambda:program.run(bad,start=meta['entries'][28039]),
                                        'endpoint-only-first-phase-overflow'),
                     'literal_transitions':bad.steps-start,'complete_source_endpoint_fits':True})
    need(bytes(bad.tapes[43]) == bank_before and bytes(bad.tapes[2]) == owned_before,
         'phase rejection changed either public HOME')
    bad = zero_boundary.clone()
    bad.tapes[36] = bad.tapes[35]
    controls.append(must_fail(lambda:program.run(bad,start=meta['entries'][28039]),'aliased-private-owner'))
    # Isolated actual central-entry header probe, explicitly not a full f2 run.
    bad = zero_boundary.clone()
    header = ''.join(map(V.gamma,(2,1,1,1,6,1)))
    for tape in range(5,36):bad.heads[tape] = bad.origins[tape]+2
    for tape in (7,8):bad.tapes[tape][bad.origins[tape]+1] = 3
    begin = bad.origins[5]+2
    bad.tapes[5][begin:begin+len(header)] = bytes(C.SYMBOL[s] for s in header)
    base = int(meta['producer_stages']['core_entry'].rsplit('.',1)[1])
    central = 'PRODUCE28039.'+str(base+meta['native_stages']['central_C_'])
    start = bad.steps
    controls.append({'control':must_fail(lambda:program.run(bad,start=central),
                                        'f2-cutoff1-actual-central-header-probe'),
                     'literal_transitions':bad.steps-start,'scope':'header-only inherited C entry, no f2 DATA'})
    need(bad.writes[2] == zero_boundary.writes[2] and bad.writes[43] == zero_boundary.writes[43],
         'header-only rejection touched public HOME')
    result = {'status':'PASS_SELECTED_FIRST_DONOR_PRODUCER','fixed_tapes':P.TAPES,
              'states':len(graph.rules),'native_locations_before_static_pruning':meta['native_locations'],
              'graph_sha256':P.digest(graph),'producer_sha256':sha256((HERE/'producer.py').read_bytes()).hexdigest(),
              'authenticated_sources':len(pins['files']),'source_binding':source,'source_algebra':algebra,
              'unchanged_reachable_C4_states':shared,'producer_footprint':footprint,
              'positive_fixture':{'f':1,'r':1,'P':1,'S':1,'width':info['width'],'cutoff':1,
                  'V_old':info['V_old'],'E_old':info['E_old'],'V':info['V'],'E_gamma':len(info['header']),
                  'F':info['F'],'contact_costs':costs,'total_literal_transitions':state.steps,
                  'history_increment':history,'no_nonzero_host_writes_after_entry':True,
                  'source_pre_MOVE_packet_only':True,'same_donor_and_owned_HOME':True,
                  'all44_heads_and_private_bodies_at_C4_service_return':True,
                  'owned1526_still_live_after_first_SUB':True,'later_rank_two_cutoff_admitted':False},
              'negative_controls':controls,'two_unrelated_ADDs_implemented':False,
              'whole_gap_implemented':False,'full_f2_packet_executed':False,
              'later_rank_two_prefix_admission_claimed':False,'assumptions_discharged':[],'new_kappa':False}
    print(json.dumps(result,indent=2))


if __name__ == '__main__':main()
