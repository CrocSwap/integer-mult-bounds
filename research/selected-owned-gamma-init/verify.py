"""Independent packet oracle, literal execution, and source/lifetime controls."""
from pathlib import Path
from collections import namedtuple
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
for pin in json.loads((HERE/'SOURCE-PINS.json').read_text())['files']:
    raw = (HERE/pin['local']).read_bytes()
    if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
        raise ValueError('retained input drift: '+pin['local'])
import init as I
import source
M = I.load('typed_init_machine', HERE/'inputs/machine.py')
A = I.load('typed_init_predecessor_add', HERE/'predecessor_add.py')
Event = namedtuple('Event', 'service owners')
DONOR = ('selected-7000-raw-native', 'productive', 728)
OWNED = ('selected-7000-raw-native', 'owned', 1526, 28037, 37618)

def need(ok, message):
    if not ok:
        raise ValueError(message)

def gamma(n):
    need(isinstance(n, int) and n > 0, 'positive Gamma input')
    b = bin(n)[2:]
    return '0'*(len(b)-1) + b

def packet(shape, values=None):
    f, r, p, s, w, cutoff = shape
    h = ''.join(gamma(n) for n in shape)
    count = 2*p*s*r*(1 << (9*f))
    if values is None:
        # Arbitrary, correlated donor data; zero production must ignore its value.
        bits = ('1011010001110010' * ((count*w+15)//16))[:count*w]
    else:
        bits = ''.join(format(values[i % len(values)] % (1 << w), '0'+str(w)+'b') for i in range(count))
    return h+bits, h, count*w

def state_for(payloads, tapes, old_history=0):
    need(payloads and len({len(x) for x in payloads}) == 1, 'fixture common F')
    state = M.initial((payloads[0], payloads[0]), tapes, old_history=old_history)
    text = '^' + '|'.join(payloads) + '|$'
    o = state.origins[0]
    state.tapes[0][o+1:-3] = bytes(len(state.tapes[0])-o-4)
    state.tapes[0][o:o+len(text)] = bytes(M.SYMBOLS[x] for x in text)
    state.highs[0] = state.entry_highs[0] = o+len(text)-1
    return state

def graph(events, owners=(DONOR, OWNED), productive=1, arithmetic=False, replacement=None):
    def service(g, name, arity, after):
        if replacement and name == 'CLEAR':
            return replacement(g, name, arity, after)
        if arithmetic and name in ('ADD', 'SUB'):
            return A.primitive(g, name, arity, after)
        return I.primitive(g, name, arity, after)
    return I.D.compile_graph(events, owners, primitive=service, productive_count=productive)

def history(state):
    return sum(b-a+1 for a, b in zip(state.lows, state.highs))

def basic_case(shape, clear=False):
    body, h, v = packet(shape)
    events = [Event('INIT', (DONOR, OWNED))]
    if clear:
        events.append(Event('CLEAR', (OWNED,)))
    g = graph(events)
    f = len(body)
    state = state_for((body,), I.TAPES, old_history=5*f)
    before_history = history(state)
    M.Program(g).run(state)
    expected = '0'*f if clear else h+'0'*v
    need(M.fields(state) == (body, expected), 'complete initialized/retired owned packet')
    M.check_retired(state)
    need(state.highs[-1] >= state.entry_highs[-1], 'earlier private history refunded')
    need(history(state)-before_history <= 4*(f+2)+8, 'complete historical increment')
    bound = 16*(len(events)+1)*5*(f+2) + (4*f+8) + (2*f+4 if clear else 0)
    need(state.steps <= bound, 'complete reserve/delivery/primitive bill')
    return {'shape': shape, 'E': len(h), 'V': v, 'F': f, 'clear': clear,
            'states': len(g.rules), 'steps': state.steps, 'complete_bound': bound,
            'history_entry': before_history, 'history_final': history(state),
            'donor_sha256': hashlib.sha256(body.encode()).hexdigest()}

def primitive_exact_cost(shape):
    body, h, v = packet(shape)
    f = len(body)
    g = I.D.Graph()
    g.start = I.primitive(g, 'INIT', 2, 'HALT')
    g.validate()
    state = state_for((body, '0'*f), I.TAPES)
    for t, text in ((1, '^'+body+'|'), (2, '^'+'0'*f+'|')):
        o = state.origins[t]
        state.tapes[t][o:o+len(text)] = bytes(M.SYMBOLS[x] for x in text)
    M.Program(g).run(state)
    a = sum(x.bit_length()-1 for x in shape)
    exact = 3*a + v + 2*f + 20
    need(state.steps == exact, 'independent exact primitive transition count')
    need(state.steps <= 4*f+8, 'uniform primitive linear bound')
    return {'shape': shape, 'states': len(g.rules), 'steps': state.steps, 'derived_steps': exact}

def additive_join():
    # This is a primitive ABI fixture. It is not a replay of the interleaved source word.
    shape = (1, 1, 1, 1, 8, 2)
    body, h, v = packet(shape, values=(3, -2, 1, 0, -5))
    owners = (DONOR, ('parked-correlated-public', 0), OWNED)
    parked = body[::-1]  # opaque binary same-F exterior HOME, never a typed operand
    events = [Event('INIT', (DONOR, OWNED)), Event('SUB', (DONOR, OWNED))]
    g = graph(events, owners, productive=2, arithmetic=True)
    state = state_for((body, parked), A.TAPES, old_history=7*len(body))
    M.Program(g).run(state)
    expected, _, _ = packet(shape, values=(-3, 2, -1, 0, 5))
    need(M.fields(state, 3) == (body, parked, expected), 'INIT to exact signed primitive ABI')
    M.check_retired(state)
    first = state.steps
    # Continue with a separately compiled real CLEAR at the already-reserved boundary.
    retire = graph([Event('CLEAR', (OWNED,))], owners, productive=2)
    M.Program(retire).run(state, start=retire.execution_start)
    need(M.fields(state, 3) == (body, parked, '0'*len(body)), 'nonzero DATA/full-header retirement')
    M.check_retired(state)
    return {'shape': shape, 'K': 3, 'productive': 2, 'tapes': A.TAPES,
            'INIT_SUB_steps': first, 'CLEAR_steps': state.steps-first,
            'scope': 'literal ABI composition; actual source donor-changing intervals remain supplied'}

def controls():
    checked = []
    body, h, v = packet((1, 1, 1, 1, 4, 2))
    f = len(body)
    g = graph([Event('INIT', (DONOR, OWNED))])
    program = M.Program(g)
    # No raw reservation in these malformed-entry tests: already-reserved body boundary.
    for label, donor, target in (
        ('incomplete_six_Gamma_header', '0'*f, '0'*f),
    ):
        state = state_for((donor, target), I.TAPES)
        before = bytes(state.tapes[0])
        try:
            program.run(state, start=g.execution_start)
        except M.Rejected:
            need(bytes(state.tapes[0]) == before and state.writes[0] == 0, 'rejected INIT scattered HOME')
        else:
            raise ValueError('malformed INIT admitted: ' + label)
        checked.append(label)
    try:
        graph([Event('INIT', (DONOR, DONOR))])
    except ValueError:
        checked.append('physical_operand_alias')
    else:
        raise ValueError('alias accepted')
    # Mutation: clear only the first body cell, still returning a full binary body.
    def partial(g, name, arity, after):
        done = g.rewind(1, after)
        loop = g.state('bad-partial-clear-remainder')
        g.add(loop, done, tests=((1, '|'),))
        for bit in '01':
            g.add(loop, loop, tests=((1, bit),), moves=((1, 1),))
        first = g.state('bad-partial-clear-first')
        for bit in '01':
            g.add(first, loop, tests=((1, bit),), writes=((1, '0'),), moves=((1, 1),))
        return g.jump(first, ((1, 1),))
    bad = graph([Event('CLEAR', (OWNED,))], replacement=partial)
    state = state_for((body, body), I.TAPES)
    M.Program(bad).run(state, start=bad.execution_start)
    M.check_retired(state)
    need(M.fields(state)[1] != '0'*f, 'partial-capacity clear negative control escaped')
    checked.append('partial_capacity_clear_detected_by_full_body_oracle')
    return checked

def arbitrary_inactive_cases():
    shape = (1, 1, 1, 1, 5, 2)
    body, h, v = packet(shape)
    f = len(body)
    g = graph([Event('INIT', (DONOR, OWNED))])
    program = M.Program(g)
    patterns = {'all_ones': '1'*f, 'same_as_donor': body,
                'complement_of_donor': ''.join('1' if b == '0' else '0' for b in body),
                'last_cell_only': '0'*(f-1)+'1'}
    receipts = []
    for label, old in patterns.items():
        state = state_for((body, old), I.TAPES, old_history=6*f)
        program.run(state, start=g.execution_start)
        need(M.fields(state) == (body, h+'0'*v), 'inactive dirty body not completely overwritten')
        M.check_retired(state)
        receipts.append({'pattern': label, 'steps': state.steps, 'F': f,
                         'old_sha256': hashlib.sha256(old.encode()).hexdigest()})
    return receipts

def verify():
    shapes = [(1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 2, 2),
              (1, 2, 2, 3, 3, 1), (1, 1, 1, 1, 17, 1 << 2048)]
    cases = [basic_case(s, clear=c) for s in shapes for c in (False, True)]
    # A complete f=2 packet; no synthetic component-only all-column control.
    cases.append(basic_case((2, 1, 1, 1, 1, 4), clear=True))
    return {'marker': 'PASS_SELECTED_OWNED_GAMMA_INIT', 'source': source.audit(),
            'cases': cases, 'exact_local_cost': [primitive_exact_cost(s) for s in shapes[:3]],
            'additive_join': additive_join(), 'controls': controls(),
            'arbitrary_inactive_cases': arbitrary_inactive_cases(),
            'scope': 'typed INIT and full-capacity CLEAR; no full chronological selected caller or new kappa'}

if __name__ == '__main__':
    result = verify()
    text = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(text)
    elif (HERE/'RESULT.json').exists():
        need(json.loads((HERE/'RESULT.json').read_text()) == json.loads(text), 'verification receipt changed')
    print(json.dumps({'marker': result['marker'], 'complete_packet_cases': len(result['cases']),
                      'source_controls': result['source']['controls'], 'machine_controls': result['controls'],
                      'additive_join': result['additive_join']}, sort_keys=True))
