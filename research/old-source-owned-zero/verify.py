"""Independent packet oracle and sparse physical execution of the fixed table."""
from pathlib import Path
import ast
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
sys.pycache_prefix = str(HERE/'_unwritten_bytecode_cache')
if Path(sys.pycache_prefix).exists():
    raise ValueError('bytecode isolation path must remain absent')
import zero as Z
C = Z.C
BLANK, LEFT, DELIMITER, END = [Z.HARDWARE_SYMBOL[s] for s in (Z.BLANK, Z.LEFT, Z.DELIMITER, Z.END)]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def old_header(values):
    out = []
    for key in C.SCHEMA:
        binary = [int(x) for x in bin(values[key])[2:][::-1]]
        out.extend([1]*len(binary)+[0]+binary)
    return out

def gamma(values):
    return [int(x) for n in values for x in '0'*(n.bit_length()-1)+bin(n)[2:]]

def fixture(a=9, u=0, f=1, K=1, rho=0, outer=1, rows=1, r=1, b=2, cutoff=1, ignored=0):
    h = dict.fromkeys(C.SCHEMA, 0)
    h.update(outer=outer, rows=rows, row_bits=(1 << a)*6*r*(b+1),
             within_bits=a, record_bits=6*r*(b+1), f=f, K=K, rho=rho,
             active_start=u, cutoff=cutoff, p=ignored, G=1, H=1,
             selected_axes=9*f, d=9*f, back_start=a-1)
    n = outer*rows*(1 << a)
    values = [((j*13+(j >> 2)*7+3) & ((1 << b)-1)) for j in range(2*r*n)]
    data = []
    for value in values:
        for bit in range(b):
            data.extend((0, 0, (value >> bit) & 1))
        data.extend((0, 1, 0))
    native = (f, r, outer*rows*(1 << u), 1 << (a-u-9*f), b, cutoff)
    header = gamma(native)
    body = header+[0]*(n*2*r*b)
    return h, data, header, body

class SparseTape:
    """Checker hardware only: dictionaries never select graph instructions."""
    def __init__(self, bits=(), origin=5, home=False, readonly=False, old_history=0):
        self.origin = origin
        self.home = home
        self.readonly = readonly
        self.cells = {origin-1: LEFT, origin-3: END, origin-2: DELIMITER}
        for i, value in enumerate(bits):
            if value != BLANK:
                self.cells[origin+i] = value
        self.head = origin-1 if home else origin
        self.low = origin-3
        self.high = max(origin+len(bits)+1, origin+old_history)
        self.entry_low, self.entry_high = self.low, self.high
        self.reads = self.writes = self.moves = 0
    def visit(self):
        self.low = min(self.low, self.head)
        self.high = max(self.high, self.head+1)
    def read(self):
        self.reads += 1
        self.visit()
        return self.cells.get(self.head, BLANK)
    def write(self, value):
        if self.readonly:
            raise ValueError('protected source/context write')
        if self.head < self.origin:
            raise ValueError('permanent marker or left exterior write')
        self.writes += 1
        self.visit()
        if value == BLANK:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = value
    def move(self, delta):
        need(delta in (-1, 1), 'nonunit move')
        self.moves += 1
        self.head += delta
        self.visit()
        need(self.head >= self.origin-1, 'crossed permanent relative guard')
    def snapshot(self):
        return dict(self.cells)

def make_tapes(data, context, home_body=None):
    tapes = [SparseTape(origin=5+i%5) for i in range(len(C.NAMES))]
    tapes[0] = SparseTape(data, 5, readonly=True)
    tapes[1] = SparseTape(context, 6, readonly=True)
    content = [] if home_body is None else list(home_body)+[DELIMITER, END]
    tapes[2] = SparseTape(content, 7, home=True)
    # Earlier visits survive every successful retirement.
    tapes[-1] = SparseTape(origin=7, old_history=3*(len(data)+len(context)+1))
    return tapes

def get_home(tape):
    out = []
    i = tape.origin
    while tape.cells.get(i, BLANK) in (0, 1):
        out.append(tape.cells[i])
        i += 1
    need(tape.cells.get(i) == DELIMITER and tape.cells.get(i+1) == END, 'exact HOME delimiters')
    return out

def restored(tapes, source, context):
    need(tapes[0].cells == source and tapes[1].cells == context, 'unchanged complete old/source context')
    need(tapes[0].writes == tapes[1].writes == 0, 'old/context were written')
    for i, tape in enumerate(tapes):
        need(tape.head == tape.origin-(1 if i == 2 else 0), 'successful relative head return')
        need(tape.cells.get(tape.origin-1) == LEFT, 'permanent guard changed')
        need(tape.cells.get(tape.origin-2) == DELIMITER and tape.cells.get(tape.origin-3) == END, 'opaque left exterior changed')
        if i >= 3:
            need(not any(k >= tape.origin for k in tape.cells), 'private guide body not retired')

def complete_case(code, labels, params, dirty=False):
    h, data, header, body = fixture(**params)
    context = old_header(h)
    old = [1-data[i % len(data)] for i in range(len(body))] if dirty else None
    tapes = make_tapes(data, context, old)
    before, descriptor = tapes[0].snapshot(), tapes[1].snapshot()
    cpu = C.CPU(code, tapes)
    need(cpu.run(limit=200_000_000) == 'LIVE_HOME', 'literal zero production')
    need(get_home(tapes[2]) == body, 'independent complete Gamma6/zero oracle')
    restored(tapes, before, descriptor)
    initial_steps = cpu.steps
    V, E, F = len(data), len(context), len(body)
    need(cpu.steps <= 2**20*(V+E+1), 'uniform linear zero-production bound')
    growth = sum(t.high-t.entry_high+t.entry_low-t.low for t in tapes)
    need(growth <= 64*(V+E+3), 'complete incremental history bound')
    need(F <= V+E, 'combined output packet capacity bound')
    need(tapes[-1].high >= tapes[-1].entry_high, 'earlier erased history refunded')
    need(cpu.run(labels['CLEAR'], limit=200_000_000) == 'RETIRED_HOME', 'complete owned retirement')
    need(get_home(tapes[2]) == [0]*F, 'entire header and DATA retired')
    restored(tapes, before, descriptor)
    need(cpu.steps-initial_steps <= 16*(F+1), 'complete CLEAR bill')
    return {'parameters': params, 'inactive_dirty_target': dirty, 'V_old': V,
            'E_old': E, 'E_Gamma': len(header), 'F_HOME': F,
            'producer_steps': initial_steps, 'CLEAR_steps': cpu.steps-initial_steps,
            'history_growth': growth, 'old_writes': tapes[0].writes,
            'context_writes': tapes[1].writes,
            'source_sha256': hashlib.sha256(bytes(data)).hexdigest()}

def negative_controls(code, labels):
    h, data, header, body = fixture()
    context = old_header(h)
    bad = [('truncated_last_code', data[:-1], context),
           ('extra_old_body_bit', data+[0], context),
           ('noncoded_first_bit', [1]+data[1:], context),
           ('truncated_context', data, context[:-1]),
           ('extra_context_bit', data, context+[0])]
    for name, field, value in (
        ('wrong_complete_row_size', 'row_bits', h['row_bits']-1),
        ('nonintegral_r', 'record_bits', 19),
        ('zero_f', 'f', 0),
        ('selected_coordinates_outside_old_row', 'within_bits', 8),
        ('invalid_rho', 'rho', 1),
    ):
        wrong = dict(h)
        wrong[field] = value
        bad.append((name, data, old_header(wrong)))
    checked = []
    for name, old, ctx in bad:
        tapes = make_tapes(old, ctx)
        before, descriptor = tapes[0].snapshot(), tapes[1].snapshot()
        cpu = C.CPU(code, tapes)
        need(cpu.run() == 'REJECT', 'malformed old input accepted: '+name)
        need(tapes[0].cells == before and tapes[1].cells == descriptor, 'failed source/context preservation')
        checked.append(name)
    for delta in (-1, 1):
        tapes = make_tapes(data, context, [1]*(len(body)+delta))
        right = tapes[2].origin+len(body)+delta
        cpu = C.CPU(code, tapes)
        need(cpu.run() == 'REJECT', 'wrong inactive HOME extent accepted')
        need(tapes[2].cells.get(right) == DELIMITER and tapes[2].cells.get(right+1) == END,
             'wrong-size rejection overwrote the inactive HOME boundary')
        checked.append('inactive_HOME_extent_'+str(delta))
    tapes = make_tapes(data, context)
    tapes[2] = tapes[0]
    try:
        C.CPU(code, tapes)
    except ValueError:
        checked.append('old_output_alias')
    else:
        raise ValueError('source/output alias admitted')
    # Same successful ABI, but wrong initialization value.  The full scientific
    # zero oracle must distinguish it even though every private owner returns.
    mutated = tuple(('W', ins[1], 1) if ins[0] == 'W' and ins[1] == 2 and ins[2] == 0
                    and labels['ZERO_DATA'] <= pc < labels['ZERO_FINISHED'] else ins
                    for pc, ins in enumerate(code))
    tapes = make_tapes(data, context)
    cpu = C.CPU(mutated, tapes)
    need(cpu.run() == 'LIVE_HOME', 'mutation did not exercise a successful return')
    need(get_home(tapes[2]) != body, 'nonzero initializer mutation escaped independent oracle')
    checked.append('nonzero_output_mutation')
    # Remove every CLEAR write while retaining traversal and head restoration.
    mutated = tuple(('J', pc+1) if ins[0] == 'W' and ins[1] == 2 and pc >= labels['CLEAR'] else ins
                    for pc, ins in enumerate(code))
    tapes = make_tapes(data, context)
    cpu = C.CPU(mutated, tapes)
    need(cpu.run() == 'LIVE_HOME' and cpu.run(labels['CLEAR']) == 'RETIRED_HOME', 'CLEAR mutation path')
    need(get_home(tapes[2]) != [0]*len(body), 'header-only residual CLEAR mutation escaped')
    checked.append('omitted_CLEAR_write')
    return checked

def nonzero_clear_case(code, labels):
    h, data, header, body = fixture(b=3)
    context = old_header(h)
    # A separately supplied valid live CLEAR entry, not an uncharged native call.
    live = header + [1]*(len(body)-len(header))
    tapes = make_tapes(data, context, live)
    before, descriptor = tapes[0].snapshot(), tapes[1].snapshot()
    cpu = C.CPU(code, tapes)
    need(cpu.run(labels['CLEAR']) == 'RETIRED_HOME', 'nonzero live CLEAR entry')
    need(get_home(tapes[2]) == [0]*len(body), 'nonzero final DATA/capacity not cleared')
    restored(tapes, before, descriptor)
    need(cpu.steps <= 16*(len(body)+1), 'nonzero CLEAR bound')
    return {'F': len(body), 'DATA_ones': len(body)-len(header), 'steps': cpu.steps,
            'scope': 'standalone arbitrary live-packet CLEAR contract'}

def source_checks():
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())
    for pin in pins['files']:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'], 'frozen source drift')
    tree = ast.parse((HERE/'inputs/old-header-provider.py').read_text())
    schema = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'SCHEMA' for t in n.targets))
    need(schema == C.SCHEMA, 'actual OLD23 source schema')
    old = ast.parse((HERE/'inputs/old-abi-machine.py').read_text())
    assignment = next(n for n in old.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Tuple) for t in n.targets))
    names = tuple(x.id for x in assignment.targets[0].elts)
    need(names == ('ZERO', 'ONE', 'LEFT', 'SEP', 'END', 'BASE', 'BLANK'), 'old physical symbol names')
    need(isinstance(assignment.value, ast.Call) and isinstance(assignment.value.func, ast.Name)
         and assignment.value.func.id == 'range' and ast.literal_eval(assignment.value.args[0]) == 7,
         'old physical symbol values')
    need((LEFT, BLANK, DELIMITER, END) == (2, 6, 3, 4), 'actual unchanged marker binding')
    import native_source
    audit = native_source.audit()
    return {'authenticated_inputs': len(pins['files']), 'OLD23_schema': schema,
            'physical_OLD_LEFT': LEFT, 'physical_OLD_BLANK': BLANK,
            'native_archive_sha256': audit['source']['sha256'],
            'native_INIT_lifetimes': audit['historical_owned_lifetimes'],
            'native_owned_labels': audit['owned_labels'],
            'scope': 'source schemas/lifetimes; actual current OLD23-to-owner binding remains a caller premise'}

def main():
    abstract, labels = Z.compile_zero()
    second, other_labels = Z.compile_zero()
    need(abstract == second and labels == other_labels, 'graph depends on runtime fixture')
    code = Z.hardware_code(abstract)
    for pc, ins in enumerate(code):
        need(ins[0] in ('R', 'W', 'M', 'J', 'H'), 'nonliteral instruction')
        if ins[0] == 'R':
            need(all(0 <= q < len(code) for q in ins[2].values()), 'unresolved branch')
        elif ins[0] == 'J':
            need(0 <= ins[1] < len(code), 'unresolved jump')
        elif ins[0] == 'M':
            need(ins[2] in (-1, 1), 'nonunit move')
        elif ins[0] == 'W':
            need(ins[1] not in (0, 1), 'static OLD/CONTEXT write')
    cases = [complete_case(code, labels, {}),
             complete_case(code, labels, {'b': 5}, dirty=True),
             complete_case(code, labels, {'a': 11, 'u': 1}),
             complete_case(code, labels, {'rows': 2, 'r': 2, 'b': 3, 'cutoff': (1 << 200)+7}),
             complete_case(code, labels, {'b': 22, 'ignored': (1 << 1024)+1}, dirty=True)]
    result = {'marker': 'PASS_OLD_SOURCE_OWNED_ZERO', 'locations': len(code), 'tapes': len(C.NAMES),
              'abstract_table_sha256': C.table_digest(abstract), 'hardware_table_sha256': C.table_digest(code),
              'source_checks': source_checks(), 'complete_packets': cases,
              'negative_controls': negative_controls(code, labels),
              'nonzero_live_CLEAR': nonzero_clear_case(code, labels),
              'scope': 'OLD23 to a separate owned zero HOME; no nonzero source conversion, full dispatcher or new kappa'}
    text = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(text)
    elif (HERE/'RESULT.json').exists():
        need(json.loads((HERE/'RESULT.json').read_text()) == json.loads(text), 'verification receipt drift')
    print(json.dumps({'marker': result['marker'], 'locations': len(code), 'tapes': len(C.NAMES),
                      'complete_packets': len(cases), 'controls': result['negative_controls']}, sort_keys=True))

if __name__ == '__main__':
    main()
