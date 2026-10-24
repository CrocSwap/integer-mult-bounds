"""Own nine BIT helper relations and check all input columns.

The source word is due to DreamingOfClouds, eumemic and their predecessors.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/kappa-rebuild/bit/sources/pr589-regenerated'
SIZE, PORTS = 661, 111
OLD_PAID = {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}
NEW_PAID = {1:1314, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:10}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def source():
    word = json.loads(gzip.decompress((SOURCE / 'WORD.json.gz').read_bytes()))
    records = list(struct.iter_unpack('<6i', (SOURCE / 'records/249-records.bin').read_bytes()))
    frames = json.loads((SOURCE / 'records/frames.json').read_text())['frames']
    return word, records, frames


def relations(word, records):
    rows = [1 << i for i in range(SIZE)] + [0]
    result = []
    for op, x, y, coefficient, frame, _ in reversed(records):
        if op == 1 and coefficient & 1:
            rows[x] ^= rows[y]
        elif op == 3:
            need(y == SIZE and rows[SIZE] == 0, 'Source COPY entrance')
            result.append(rows[x])
            rows[SIZE] = rows[x]
        elif op == 2:
            need(y == SIZE and rows[x] == rows[SIZE], 'Source COPY exit')
            rows[SIZE] = 0
    want = [(1 << i) ^ ((1 << (i-PORTS)) if PORTS <= i < 2*PORTS else 0)
            for i in range(SIZE)] + [0]
    need(rows == want and len(result) == 9, 'Source reverse identity and all nine COPY forms')
    basis = {}
    for row in result:
        for pivot, value in sorted(basis.items()):
            if row >> pivot & 1:
                row ^= value
        helpers = row >> (2*PORTS)
        need(helpers != 0, 'Each relation has a new helper pivot')
        pivot = 2*PORTS + (helpers & -helpers).bit_length()-1
        for old in list(basis):
            if basis[old] >> pivot & 1:
                basis[old] ^= row
        basis[pivot] = row
    need(len(basis) == 9, 'Nine independent helper relations')
    pivots = sum(1 << i for i in basis)
    for pivot, row in basis.items():
        need(row & pivots == 1 << pivot, 'Reduced helper basis')
        need(all(word['final'][i] == 1 for i in range(SIZE) if row >> i & 1),
             'Every relation input has the full entrance frame')
    return dict(sorted(basis.items()))


def construct(word, records, basis):
    frames = list(word['final']) + [None]
    rows = [1 << i for i in range(SIZE+1)]
    program = [['CLEAR', SIZE, None]]
    rows[SIZE] = 0
    for pivot, row in basis.items():
        program.append(['CLEAR', pivot, 1])
        rows[pivot] = 0
        for i in range(SIZE):
            if i != pivot and row >> i & 1:
                program.append(['ADD', pivot, i, 1])
                rows[pivot] ^= rows[i]
    removed = []
    for index, (op, x, y, a, b, _) in enumerate(reversed(records)):
        if op == 0:
            old, new, rank = a, y, b
            need(frames[x] == old, 'Source MOVE entrance')
            if rows[x]:
                program.append(['MOVE', x, old, new, rank])
            else:
                program.append(['ZERO_MOVE', x, old, new])
                if rank:
                    removed.append([index, 'MOVE', x, rank])
            frames[x] = new
        elif op == 1:
            need(frames[x] == frames[y] == b, 'Source ADD frame')
            if a & 1:
                rows[x] ^= rows[y]
                program.append(['ADD', x, y, b])
        elif op == 3:
            need(y == SIZE and frames[x] == a and rows[x] == rows[SIZE] == 0,
                 'All nine source COPY values are zero')
            program.append(['CLEAR', SIZE, b])
            frames[SIZE] = b
            removed.append([index, 'COPY', x, 7])
        else:
            need(op == 2 and y == SIZE and rows[x] == rows[SIZE] == 0,
                 'Zero COPY close')
            program.append(['CLEAR', SIZE, None])
            frames[SIZE] = None
    for pivot in basis:
        program.append(['CLEAR', pivot, word['start'][pivot]])
    return program, removed


def replay(word, program, basis):
    owned = set(basis) | {SIZE}
    rows = [1 << i for i in range(SIZE+1)]
    frames = list(word['final']) + [None]
    paid = Counter()
    largest_row = 1
    for event in program:
        op, role = event[:2]
        if op == 'CLEAR':
            need(role in owned, 'Only an owned field can be cleared')
            rows[role], frames[role] = 0, event[2]
        elif op == 'ADD':
            _, dst, src, frame = event
            need(dst != src and frames[dst] == frames[src] == frame, 'Common-frame XOR')
            rows[dst] ^= rows[src]
            largest_row = max(largest_row, rows[dst].bit_count())
        elif op in ('MOVE', 'ZERO_MOVE'):
            _, role, old, new, *rank = event
            need(frames[role] == old, 'Native MOVE entrance')
            if op == 'ZERO_MOVE':
                need(rows[role] == 0, 'Only a zero value can change frame for free')
            elif rank[0]:
                paid[rank[0]] += 1
            frames[role] = new
        else:
            raise ValueError('Unknown local operation')
    for i, row in enumerate(rows):
        expected = 0 if i in owned else (1 << i) ^ ((1 << (i-PORTS)) if PORTS <= i < 2*PORTS else 0)
        need(row == expected, 'Every retained and arbitrary owned entry column')
    need(frames[:SIZE] == word['start'] and frames[SIZE] is None, 'All exit frames')
    need(dict(paid) == NEW_PAID, 'Exact changed local paid profile')
    return {'paid': dict(sorted(paid.items())), 'helpers': {8:439-len(basis)},
            'retained_inputs': SIZE-len(basis), 'arbitrary_owned_entries': len(owned),
            'events': len(program), 'scalar_events': sum(e[0] in ('ADD', 'CLEAR') for e in program),
            'maximum_binary_row_weight': largest_row,
            'word_sha256': sha256(json.dumps(program, separators=(',', ':')).encode()).hexdigest()}


def native(word, records, frame_data):
    load('research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/bit-compression/carrier-reuse/reference/joint_pair_dag.py', 'joint_pair_dag')
    module = load('research/kappa-rebuild/bit/mixed_productive_bit.py', 'bit_source_geometry')
    projectors = module.frame_projectors(frame_data)
    dims = {int(f): row['dim'] for f, row in frame_data.items()}
    pairs = {(e[2], e[3], e[4]) for e in records if e[0] == 0}
    for a, b, rank in pairs:
        p, q = projectors[a], projectors[b]
        need(module.matrix_multiply(p, q) == p == module.matrix_multiply(q, p), 'Nested exact projectors')
        need(dims[b]-dims[a] == rank, 'Every original and reversed child rank')
    multiply = module.matrix_multiply
    def eye(n):
        return [[Fraction(i == j) for j in range(n)] for i in range(n)]
    def swap(p):
        return [[Fraction(int(i == j)-(p[i][j] if i < 8 and j < 8 else p[i-8][j-8])
                         if (i < 8) == (j < 8) else p[i][j-8] if i < 8 else p[i-8][j])
                 for j in range(16)] for i in range(16)]
    for port in range(PORTS):
        p = projectors[word['start'][port]]
        complement = [[Fraction(i == j)-p[i][j] for j in range(8)] for i in range(8)]
        need(dims[word['start'][port]] == 1 and word['start'][port+PORTS] == 0,
             'Actual main entrance line and empty frame')
        need(word['final'][port] == 1 and projectors[word['final'][port+PORTS]] == complement,
             'Actual main full frame and complement')
        q = list(map(Fraction, word['lines'][port]))
        need(sum(x*x for x in q) == 4 and p == [[x*y/4 for y in q] for x in q],
             'Source root and actual entrance projector')
        u = [Fraction(i == 0)-q[i]/2 for i in range(8)]
        norm = sum(x*x for x in u)
        g = eye(8) if norm == 0 else [[Fraction(i == j)-2*u[i]*u[j]/norm for j in range(8)] for i in range(8)]
        a = [row[1:] for row in g]
        at = list(map(list, zip(*a)))
        need(multiply(at,a) == eye(7) and multiply(a,at) == complement, 'Fresh exact complement basis')
        rho = [p[i]+a[i] for i in range(8)] + [row+[Fraction(0)]*7 for row in at]
        full = [[Fraction(i == j and i < 8) for j in range(15)] for i in range(15)]
        active = [[p[i][j] if i < 8 and j < 8 else Fraction(i == j and i >= 8) for j in range(15)] for i in range(15)]
        central = [[p[i][j] if i < 8 and j < 8 else Fraction(0) for j in range(15)] for i in range(15)]
        need(multiply(rho,rho) == eye(15), 'Fresh port route is an involution')
        need(multiply(multiply(rho,full),rho) == active, 'Every port route maps the full local projector to the next active block')
        need(multiply(multiply(rho,central),rho) == central, 'Every route fixes the central query projector')
        need(multiply(swap(eye(8)),swap(p)) == swap(complement), 'Exact address map D_I D_P equals D_K')
        need(multiply(swap(p),swap(p)) == eye(16) and multiply(swap(complement),swap(complement)) == eye(16),
             'Both physical address factors are involutions')
    need(all(word['start'][i] == 0 and word['final'][i] == 1 for i in range(2*PORTS, SIZE)),
         'Every retained helper has a rank-eight target')
    return {'rational_projectors': len(projectors), 'nested_transition_pairs': len(pairs),
            'main_involution_ports': PORTS, 'fresh_port_routes': PORTS, 'new_nonzero_native_maps': 0,
            'all_f_rule': 'Source projectors tensor I_f; the source address involutions and all GF(2) identities stay exact.',
            'full_GL_cover_executed': False}


def controls(word, program, basis):
    bad = json.loads(json.dumps(program))
    bad.pop(next(i for i, e in enumerate(bad) if e[0] == 'CLEAR' and e[1] in basis))
    variants = {'missing_owned_entry_clear': bad}
    bad = json.loads(json.dumps(program))
    bad.pop(next(i for i, e in enumerate(bad) if e[0] == 'ADD' and e[1] in basis))
    variants['changed_relation'] = bad
    bad = json.loads(json.dumps(program))
    bad.pop(max(i for i, e in enumerate(bad) if e[0] == 'CLEAR' and e[1] in basis))
    variants['missing_owned_exit_clear'] = bad
    bad = json.loads(json.dumps(program))
    i = next(i for i, e in enumerate(bad) if e[0] == 'MOVE' and e[-1] > 0)
    bad[i] = ['ZERO_MOVE'] + bad[i][1:4]
    variants['unearned_free_transition'] = bad
    failures = {}
    for name, bad in variants.items():
        try:
            replay(word, bad, basis)
        except ValueError as error:
            failures[name] = str(error)
        else:
            raise ValueError('Accepted local mutation: ' + name)
    return failures


def run():
    word, records, frames = source()
    basis = relations(word, records)
    program, removed = construct(word, records, basis)
    result = replay(word, program, basis)
    need(Counter(e[-1] for e in removed) == {1:9, 7:9}, 'All removed jobs and no others')
    result.update({'relation_basis': {str(p): [i for i in range(SIZE) if row >> i & 1] for p, row in basis.items()},
                   'removed': removed, 'native': native(word, records, frames),
                   'negative_controls': controls(word, program, basis)})
    return result, program
