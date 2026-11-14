"""Bounded literal contact replay and independent source-frame expectations.

All packet construction, arithmetic expectations and contextual observations
are verifier-only. They are never counted as an implemented source producer.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import gzip
import json
import random
import sys
import types

HERE = Path(__file__).resolve().parent


def module(path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    sys.modules[name] = value
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value


C = module(HERE/'protocol.py', '_checked_owned_lifetime')
need = C.need
SCHEMA = ('outer','rows','stock','row_bits','within_bits','record_bits','p','d',
          'K','G','H','q0','qF','qB','D','f','rho','active_start','back_start',
          'selected_axes','entry_start','remainder','cutoff')
EXPECTED = (
    (28037, ['INIT',1526,601]),
    (28041, ['ADD',1526,1349,'-1',601]),
    (28129, ['ADD',1526,728,'-1',601]),
    (28135, ['ADD',1526,729,'-1',601]),
    (28139, ['ADD',1526,730,'-1',601]),
    (28141, ['MOVE',1526,601,470,True]),
    (28159, ['ADD',1515,1526,'1',470]),
    (37618, ['CLEAR',1526,470]),
)


def touched(event):
    op = event[0]
    need(op in ('INIT','CLEAR','MOVE','ADD','COPY','SCALE'), 'unknown source opcode')
    return event[1:3] if op in ('ADD','COPY') else event[1:2]


def audit_interval(interval):
    program, start = interval['program'], interval['start']
    frames = {int(k): v for k, v in interval['initial_current_frames'].items()}
    need(start == 28037 and len(program) == 9582 and 1526 not in frames,
         'exact interval/inactive lifetime entry')
    need(frames[1349] == 3, 'donor1349 starts in frame3')
    contacts = []
    receiver_events = []
    for relative, event in enumerate(program):
        index = start+relative
        if 1526 in touched(event):
            contacts.append((index, event))
        if 28153 <= index < 28159 and 1515 in touched(event):
            receiver_events.append((index, event))
        op, owner = event[:2]
        if op == 'INIT':
            need(owner not in frames and owner >= interval['public'], 'source INIT lifetime')
            frames[owner] = event[2]
        elif op == 'CLEAR':
            need(owner >= interval['public'] and frames.get(owner) == event[2],
                 'source CLEAR frame/lifetime')
            del frames[owner]
        elif op == 'MOVE':
            need(frames.get(owner) == event[2], 'source MOVE input frame')
            need(event[4] == (owner >= interval['public']), 'source MOVE owner type')
            frames[owner] = event[3]
        elif op in ('ADD','COPY'):
            need(frames.get(owner) == event[4] == frames.get(event[2]),
                 'source binary current frames')
        elif op == 'SCALE':
            need(frames.get(owner) == event[3], 'source SCALE current frame')
    need(tuple(contacts) == EXPECTED, 'complete actual owner1526 contact projection')
    need(receiver_events == [(28153, ['INIT',1515,470])], 'receiver is zero at28159')
    need(1526 not in frames, 'owned lifetime did not retire')
    need(program[28039-start] == ['MOVE',1349,3,601,False], 'actual donor frame change')
    need(interval['move_frames'] == {'601':[137], '470':[75,137,265]}, 'actual MOVE frames')
    gaps = [(a+1, b-1) for a, b in zip(C.EVENTS, C.EVENTS[1:])]
    for lo, hi in gaps:
        need(all(1526 not in touched(program[i-start]) for i in range(lo,hi+1)),
             'intervening source gap touches protected owner')
    return {'events_checked':len(program),'contacts':contacts,'gap_intervals':gaps,
            'gap_events':sum(hi-lo+1 for lo,hi in gaps),
            'receiver1515_zero_at28159':True,'donor1349_initial_frame':3,
            'donor1349_contact_frame':601}


def source_check(archive=None):
    raw = (HERE/'SOURCE-INTERVAL.json.gz').read_bytes()
    need(sha256(raw).hexdigest() == '517dd194611a7a180bd9229c7cd53167f2e8aaf9043d1c1fc7efece143ed89d1',
         'retained interval bytes')
    data = gzip.decompress(raw)
    need(sha256(data).hexdigest() == 'edd7c1531fa7c2ed3d9bc4cbf565a0f83bee8084f89fdd97d70be3e38605b846',
         'retained interval canonical bytes')
    interval = json.loads(data)
    result = audit_interval(interval)
    if archive:
        original = Path(archive).read_bytes()
        need(len(original) == 350722 and sha256(original).hexdigest() == interval['source']['archive_sha256'],
             'complete original archive binding')
        word = json.loads(gzip.decompress(original))
        need(sha256(json.dumps(word,separators=(',',':'),sort_keys=True).encode()).hexdigest()
             == interval['source']['canonical_sha256'], 'complete canonical word binding')
        frames = dict(enumerate(word['initial']))
        for event in word['program'][:28037]:
            op, owner = event[:2]
            if op == 'INIT':frames[owner] = event[2]
            elif op == 'CLEAR':del frames[owner]
            elif op == 'MOVE':frames[owner] = event[3]
        need({str(k):v for k,v in frames.items()} == interval['initial_current_frames'],
             'source prefix frame snapshot extraction')
        need(word['program'][28037:37619] == interval['program'], 'complete source interval extraction')
        need({str(k):word['frames'][k] for k in (601,470)} == interval['move_frames'],
             'source frame extraction')
    result['complete_archive_reextracted_this_run'] = bool(archive)
    changed = json.loads(data)
    changed['program'][1] = ['ADD',1526,1349,'1',601]
    must_fail(lambda:audit_interval(changed), 'gap mutation touching owned1526')
    changed = json.loads(data)
    changed['program'][28039-28037] = ['SCALE',1349,'1',3]
    must_fail(lambda:audit_interval(changed), 'stale actual donor frame')
    must_fail(lambda:touched(['UNRECOGNIZED',1526]), 'unknown opcode cannot hide a touch')
    result['controls'] = ['gap-owner-mutation','stale-donor-frame','unknown-opcode']
    return result


def must_fail(action, label):
    try:
        action()
    except (ValueError, C.Rejected):
        return label
    raise ValueError('negative control escaped: '+label)


def gamma(value):
    bits = bin(value)[2:]
    return '0'*(len(bits)-1)+bits


def old_header(values):
    result = []
    for name in SCHEMA:
        bits = list(map(int,bin(values[name])[2:][::-1]))
        result.extend([1]*len(bits)+[0]+bits)
    return result


def old_body(values, width):
    result = []
    for value in values:
        for digit in range(width):result.extend((0,0,(value>>digit)&1))
        result.extend((0,1,0))
    return result


def encode(values, width):
    need(all(-(1<<(width-1)) <= x < 1<<(width-1) for x in values), 'fixture signed range')
    return ''.join(f'{x%(1<<width):0{width}b}' for x in values)


def body(state, tape, count=1):
    data, at = state.tapes[tape], state.origins[tape]+1
    fields = []
    for _ in range(count):
        start = at
        while data[at] in (0,1):at += 1
        need(data[at] == 3, 'HOME field delimiter')
        fields.append(''.join(str(s) for s in data[start:at]))
        at += 1
    need(data[at] == 4, 'HOME endpoint')
    return tuple(fields)


def fixture(*, width=6, cutoff=(1<<67)+3, receiver_nonzero=False,
            overflow=False, wrong_header=False, short_home=False):
    rng = random.Random(152628141)
    h = dict.fromkeys(SCHEMA,0)
    h.update(outer=1,rows=1,row_bits=512*6*(width+1),within_bits=9,
             record_bits=6*(width+1),f=1,K=1,cutoff=cutoff,G=1,H=1,
             d=9,selected_axes=9,back_start=8)
    header = ''.join(map(gamma,(1,1,1,1,width,cutoff)))
    donors = [[2*rng.randrange(-1,2) for _ in range(1024)] for _ in range(4)]
    receiver = [rng.randrange(-1,2) if receiver_nonzero else 0 for _ in range(1024)]
    if overflow:
        donors[0] = [0]*1024
        donors[0][-1] = -(1<<(width-1))
    packets = [header+encode(v,width) for v in donors+[receiver]]
    if wrong_header:
        other = ''.join(map(gamma,(1,1,1,1,width,cutoff^1)))
        need(len(other) == len(header), 'same-length unequal header control')
        packets[0] = other+encode(donors[0],width)
    old_values = [rng.randrange(-3,4) for _ in range(1024)]
    old, descriptor = old_body(old_values,width), old_header(h)
    F = len(header)+1024*width
    capacity = 16*(len(old)+len(descriptor)+F+128)
    origins = [17+i%7 for i in range(C.TAPES)]
    tapes = [bytearray([6])*capacity for _ in range(C.TAPES)]
    for tape, origin in zip(tapes,origins):
        tape[origin] = 2
        tape[origin-3:origin] = bytes((4,1,5))
        tape[-3:] = bytes((5,1,4))
    for t, values in ((0,old),(1,descriptor)):
        start = origins[t]+1
        tapes[t][start:start+len(values)] = bytes(values)
    inactive = ''.join(str((i*7+i//3)%2) for i in range(F-(1 if short_home else 0)))
    for t,text in ((2,inactive+'|$'),(43,'|'.join(packets)+'|$')):
        start = origins[t]+1
        tapes[t][start:start+len(text)] = bytes(C.SYMBOL[s] for s in text)
    heads = [o+1 if i < 43 and i != 2 else o for i,o in enumerate(origins)]
    lows, highs = origins.copy(), heads.copy()
    for t,length in ((0,len(old)),(1,len(descriptor)),(2,len(inactive)+2),(43,5*(F+1)+1)):
        highs[t] = origins[t]+length
    # Retain larger historical backing on a reused private guide.
    highs[42] = origins[42]+2*len(old)+777
    state = C.State(tapes,heads,origins,lows,highs,[0]*C.TAPES)
    return state, {'width':width,'cutoff':cutoff,'header':header,'F':F,'V':1024*width,
                   'V_old':len(old),'E_old':len(descriptor),'donors':donors,'receiver':receiver,
                   'old':old,'descriptor':descriptor,'packets':packets,
                   'initial_history':sum(b-a+1 for a,b in zip(lows,highs))}


def returned(state, info, *, final=False):
    for t,(data,origin) in enumerate(zip(state.tapes,state.origins)):
        expected_head = origin+1 if t in (0,1) or (final and 3 <= t <= 42) else origin
        need(state.heads[t] == expected_head, 'complete returned head '+str(t))
        need(data[origin] == 2 and data[origin-3:origin] == bytes((4,1,5))
             and data[-3:] == bytes((5,1,4)), 'permanent guard and opaque exterior')
        need(state.lows[t] >= origin, 'no exterior visit')
        if 3 <= t <= 42:
            need(all(s == 6 for s in data[origin+1:-3]), 'all reused private bodies blank')
    for t,key in ((0,'old'),(1,'descriptor')):
        at = state.origins[t]+1
        need(list(state.tapes[t][at:at+len(info[key])]) == info[key] and state.writes[t] == 0,
             'immutable OLD23 source/context')


def source_kernel():
    n = module(HERE/'inputs/move/reference/source/native_verify.py', '_lifetime_source_frames')
    circuit = n.adjoint(n.frame([137],9))+n.frame([75,137,265],9)
    columns = []
    for x in range(512):
        values, exponent = n.state(circuit,x)
        columns.append((exponent,tuple(sorted((y,pair[0],pair[1]) for y,pair in values.items()))))
    return tuple(columns)


KERNEL = source_kernel()


def source_move(values):
    """Direct original-frame columns on packed addresses; no lowered factors."""
    def reverse9(value):
        return sum(((value>>i)&1)<<(8-i) for i in range(9))
    denominator = max(exponent for exponent,_ in KERNEL)
    numerators = [0]*1024
    for address in range(512):
        exponent, columns = KERNEL[reverse9(address)]
        ar,ai = values[2*address:2*address+2]
        scale = 1<<(denominator-exponent)
        for y,cr,ci in columns:
            out = 2*reverse9(y)
            numerators[out] += scale*(cr*ar-ci*ai)
            numerators[out+1] += scale*(cr*ai+ci*ar)
    divisor = 1<<denominator
    need(all(x%divisor == 0 for x in numerators), 'source image integrality')
    return [x//divisor for x in numerators]


def check_extension_graph(graph):
    """Sufficient static capability rule; verifier-only contract validation."""
    for rules in graph.rules.values():
        for rule in rules:
            for tape,_ in rule.writes+rule.moves:
                need(tape >= 43, 'continuation modifies a protected capability')


def check_gap_state(before, after):
    for tape in range(43):
        need(before.tapes[tape] == after.tapes[tape] and before.heads[tape] == after.heads[tape],
             'continuation changed protected owner/body/head')
    need(all(c <= a and b <= d for a,b,c,d in
             zip(before.lows,before.highs,after.lows,after.highs)),
         'continuation history was refunded')


def check_contact_frame(event, source_frame, target_frame):
    required = 470 if event == 28159 else 601
    need(source_frame == target_frame == required, 'stale/nonmatching contact frame')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive')
    args = parser.parse_args()
    sources = C.authenticate()
    source = source_check(args.archive)
    graph,meta = C.compile_protocol()
    need(len(graph.rules) == 121322 and C.digest(graph) == 'd1e393590eae49c483c191f5ccf1ccbe47e54b2517a4b7ff396819017666bbf4',
         'frozen literal protocol graph')
    program = C.Program(graph)
    state,info = fixture()
    original_owner = state.tapes[2]
    expected = [0]*1024
    checkpoints = []
    snapshots = {}
    for event in C.EVENTS:
        if event in (28041,28129,28135,28139):
            index = (28041,28129,28135,28139).index(event)
            expected = [a-b for a,b in zip(expected,info['donors'][index])]
            check_contact_frame(event,601,601)
        elif event == 28141:
            snapshots['before_move'] = state.clone()
            moved = source_move(expected)
            need(moved != expected and any(moved), 'nontrivial actual rank-two fixture')
            expected = moved
        elif event == 28159:
            check_contact_frame(event,470,470)
        before_steps = state.steps
        program.run(state,start=meta['entries'][event])
        need(state.tapes[2] is original_owner, 'same original owned HOME object')
        returned(state,info,final=event == 37618)
        if event == 37618:
            need(body(state,2) == ('0'*info['F'],), 'full dirty header+DATA erase')
        else:
            need(body(state,2) == (info['header']+encode(expected,info['width']),),
                 'exact owned value after literal contact')
        external = body(state,43,5)
        need(external[:4] == tuple(info['packets'][:4]), 'all supplied donor HOME values preserved')
        receiver = expected if event in (28159,37618) else info['receiver']
        need(external[4] == info['header']+encode(receiver,info['width']), 'actual zero-receiver consumption')
        checkpoints.append({'event':event,'transitions':state.steps-before_steps})
        if event == 28037:snapshots['zero'] = state.clone()
        if event == 28041:snapshots['first_sub'] = state.clone()
    local_limit = 2**20*(info['V_old']+info['E_old']+1)+2**24*(info['V']+len(info['header'])+1)+32768*(info['F']+1)+128
    history = sum(b-a+1 for a,b in zip(state.lows,state.highs))
    increment = history-info['initial_history']
    need(state.steps <= local_limit, 'complete local time bound')
    need(increment <= 64*(info['V_old']+info['E_old']+3)+2048*(info['F']+2), 'history union bound')
    controls = []
    # Re-entering these contacts uses supplied boundary packets, not a claim
    # that external source operations were implemented between contact returns.
    bad = snapshots['zero'].clone()
    bad.tapes[42] = bad.tapes[41]
    controls.append(must_fail(lambda:program.run(bad,start=meta['entries'][28041]),'physical-owner-alias'))
    for name,kwargs,event in (
        ('short-inactive-home',{'short_home':True},28037),
        ('unequal-same-length-header',{'wrong_header':True},28041),
        ('late-signed-overflow',{'overflow':True},28041),
        ('actual-rank-two-cutoff',{'cutoff':1},28141),
    ):
        bad,binfo = fixture(**kwargs)
        if event != 28037:program.run(bad,start=meta['entries'][28037])
        if event == 28141:
            for contact in (28041,28129,28135,28139):
                program.run(bad,start=meta['entries'][contact])
        owned_before = bytes(bad.tapes[2])
        writes_before = bad.writes[2]
        controls.append(must_fail(lambda:program.run(bad,start=meta['entries'][event]),name))
        if event != 28037:
            need(bytes(bad.tapes[2]) == owned_before and bad.writes[2] == writes_before,
                 'numerical/header rejection before owned scatter')
    altered,ameta = C.compile_protocol(mutation='wrong-first-sign')
    bad = snapshots['zero'].clone()
    C.Program(altered).run(bad,start=ameta['entries'][28041])
    need(body(bad,2) != body(snapshots['first_sub'],2), 'wrong exterior sign separated')
    controls.append('wrong-exterior-sign-detected-by-exact-integers')
    altered,ameta = C.compile_protocol(mutation='wrong_phase')
    bad = snapshots['before_move'].clone()
    start_steps = bad.steps
    C.Program(altered).run(bad,start=ameta['entries'][28141])
    need(body(bad,2) != (info['header']+encode(expected,info['width']),), 'absolute phase separated')
    returned(bad,info)
    controls.append({'control':'wrong-absolute-phase','literal_transitions':bad.steps-start_steps,
                     'source-frame-oracle-detected':True})
    bad = snapshots['zero'].clone()
    bad.tapes[2][bad.origins[2]+1] ^= 1
    controls.append(must_fail(lambda:check_gap_state(snapshots['zero'],bad),'continuation-owner-mutation'))
    controls.append(must_fail(lambda:check_contact_frame(28041,3,601),'stale-donor-frame-contract'))
    _,add,_ = C.inputs()
    extension = add.D.Graph()
    extension.add('entry','HALT',writes=((2,'0'),))
    controls.append(must_fail(lambda:check_extension_graph(extension),'literal-extension-protected-write'))
    extension = add.D.Graph()
    extension.add('entry','HALT',moves=((3,1),))
    controls.append(must_fail(lambda:check_extension_graph(extension),'literal-extension-private-head-move'))
    check_gap_state(snapshots['zero'],snapshots['zero'])
    for pin in sources:
        data = (HERE/pin['local']).read_bytes()
        need(sha256(data+b' ').hexdigest() != pin['sha256'], 'source mutation detection')
    result = {'status':'PASS_OWNED1526_LITERAL_CONTACT_PROTOCOL','fixed_tapes':C.TAPES,
              'states':len(graph.rules),'graph_sha256':C.digest(graph),
              'protocol_sha256':sha256((HERE/'protocol.py').read_bytes()).hexdigest(),
              'source_inputs':len(sources),'source_mutations_detected':len(sources),
              'source_chronology':source,'positive_local_fixture':{
                  'f':1,'r':1,'P':1,'S':1,'width':info['width'],
                  'cutoff_bit_length':info['cutoff'].bit_length(),
                  'V_old':info['V_old'],'E_old':info['E_old'],'V':info['V'],
                  'E_gamma':len(info['header']),'F':info['F'],
                  'contact_transitions':checkpoints,'total_local_transitions':state.steps,
                  'historical_increment':increment,'initial_retained_history':info['initial_history'],
                  'same_physical_owner':True,'all44_heads_and_private_capabilities_returned':True,
                  'receiver_boundary_zero':True,'nonzero_full_erase':True},
              'negative_controls':controls,'uninterrupted_selected_source_execution':False,
              'actual_external_continuations_implemented':False,'full_f2_execution':False,
              'assumptions_discharged':[],'new_kappa':False}
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
