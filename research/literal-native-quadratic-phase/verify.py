"""Bounded complete-packet replay and direct polynomial/integer oracles.

The oracle enumerates addresses independently; it never uses the table's
incremental phase update. Prepared for CubeJerry with OpenAI assistance.
"""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import phase as P


def need(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(value):
    bits = bin(value)[2:]
    return '0'*(len(bits)-1)+bits


def phases(m, f, linear, rows, constant):
    radix = 1 << f
    out = []
    for address in itertools.product(range(radix), repeat=m):
        total = 0
        for column in range(f):
            bits = [(address[i] >> column) & 1 for i in range(m)]
            total += constant + sum(a*x for a, x in zip(linear, bits))
            total += 2*sum(bits[i]*bits[j] for i in range(m)
                           for j in range(i+1, m) if (rows[i] >> j) & 1)
        out.append(total % 4)
    return out


def rotate(z, mode):
    # Independent Gaussian-integer multiplication, not the table's case list.
    a, b = z
    c, d = ((1, 0), (0, 1), (-1, 0), (0, -1))[mode]
    return a*c-b*d, a*d+b*c


def encode(values, w):
    return ''.join(format(x % (1 << w), '0'+str(w)+'b')
                   for z in values for x in z)


def packet(f, r, outer, spectator, w, linear=P.SELECTED_LINEAR,
           rows=P.SELECTED_ROWS, constant=P.SELECTED_CONSTANT,
           values=None, code=None, corrupt=None, origins=None):
    m = len(linear)
    modes = phases(m, f, linear, rows, constant)
    modes = [q for _ in range(outer) for q in modes
             for _ in range(spectator) for _ in range(r)]
    if values is None:
        cap = (1 << (w-1))-1
        values = [((7*j+3) % (2*cap+1)-cap,
                   (11*j+1) % (2*cap+1)-cap) for j in range(len(modes))]
    need(len(values) == len(modes), 'complete payload extent')
    expected = [rotate(z, q) for z, q in zip(values, modes)]
    low, high = -(1 << (w-1)), (1 << (w-1))-1
    fits = all(low <= x <= high for z in expected for x in z)
    header = ''.join(gamma(x) for x in (f, r, outer, spectator, w))
    data = encode(values, w)
    V, Q, E = len(data), 1 << (m*f), len(header)
    if origins is None:
        origins = tuple(17-7*i for i in range(23))
    tapes = []
    for i, origin in enumerate(origins):
        span = V+E+sum((f, r, outer, spectator, w))+20
        cells = {origin-5: '1', origin-4: '|', origin+span: '0'}
        if i == P.HEADER:
            cells.update({origin+j: b for j, b in enumerate(header)})
        elif i == P.DATA:
            cells.update({origin+j: b for j, b in enumerate(data)})
        tapes.append(P.Tape(cells, origin))
    before = [dict(t.cells) for t in tapes]
    table = P.compile_phase(linear, rows, constant)[0] if code is None else code
    if corrupt:
        table = corrupt(table)
    machine = P.Machine(table, tapes)
    budget = 65536*(E+(m+1)*f+r+outer+spectator+w+(m+1)**2*outer*Q+V+1)
    rejected = False
    try:
        machine.run(budget)
    except ValueError as error:
        need(str(error) == 'invalid scanned symbol', 'unexpected rejection '+str(error))
        rejected = True
    need(rejected == (not fits), 'exact signed acceptance')
    need(tapes[P.HEADER].cells == before[P.HEADER], 'header preserved')
    if rejected:
        need(tapes[P.DATA].cells == before[P.DATA], 'all public data preserved on rejection')
    else:
        goal = dict(before[P.DATA])
        goal.update({origins[P.DATA]+i: bit for i, bit in enumerate(encode(expected, w))})
        need(tapes[P.DATA].cells == goal, 'independent direct phase/integer endpoint')
        need(all(t.head == origin for t, origin in zip(tapes, origins)), 'all heads restored')
        need(all(t.cells == old for t, old in zip(tapes[2:], before[2:])), 'private blank and opaque cells restored')
    delta_history = sum(t.high-t.low for t in tapes)
    # Public bodies are initially backed; this intentionally generous check
    # also includes their full scans rather than subtracting initial backing.
    history_bound = 3*V+5*E+(m+4)*f+4*(r+outer+spectator)+8*w+256
    need(delta_history <= history_bound, 'historical extent bound')
    return {'steps': machine.steps, 'rejected': rejected, 'V': V,
            'history': delta_history, 'modes': sorted(set(modes))}


def fixed_table_check(code, alphabet):
    need(tuple(alphabet) == ('_', '0', '1', '|'), 'fixed alphabet')
    for op, *args in code:
        need(op in ('read', 'write', 'move', 'goto', 'halt'), 'literal instruction')
        if op in ('read', 'write', 'move'):
            need(type(args[0]) is int and 0 <= args[0] < 23, 'fixed physical port')
        if op == 'read':
            need(set(args[1]) <= set(alphabet), 'read symbols')
            need(all(type(k) is int and 0 <= k < len(code) for k in args[1].values()), 'fixed branch')
        if op == 'write':
            need(args[1] in alphabet, 'write symbol')
        if op == 'move':
            need(args[1] in (-1, 1), 'unit move')
        if op == 'goto':
            need(type(args[0]) is int and 0 <= args[0] < len(code), 'fixed goto')


def main():
    code, alphabet = P.compile_phase()
    fixed_table_check(code, alphabet)
    recipe = json.loads((HERE/'RECIPE.json').read_text())
    need(tuple(recipe['recipe']['linear_Z4']) == P.SELECTED_LINEAR and
         tuple(recipe['recipe']['quadratic_rows']) == P.SELECTED_ROWS and
         recipe['recipe']['phase'] == P.SELECTED_CONSTANT, 'selected recipe constants')
    results = []
    # Genuine complete selected m=9 arrays at f=1; all 512 addresses.
    for args in ((1,1,1,1,2), (1,2,2,2,5), (1,1,1,1,1), (1,1,1,1,17)):
        results.append(packet(*args, code=code))
    # More than one column in complete lower-dimensional specializations.
    for m in (1,2,3):
        rows = tuple((1 << m)-1 for _ in range(m))
        linear = tuple(1+2*(i % 2) for i in range(m))
        for f in (1,2,3):
            for constant in range(4):
                results.append(packet(f,2,2,2,3,linear,rows,constant))
    # Every pair at widths 1..3, for every phase. Constant f=1 gives
    # the same phase at both addresses and isolates exact endpoint handling.
    endpoints = 0
    for w in (1,2,3):
        interval = range(-(1 << (w-1)), 1 << (w-1))
        for mode in range(4):
            table = P.compile_phase((0,), (0,), mode)[0]
            for pair in itertools.product(interval, repeat=2):
                results.append(packet(1,1,1,1,w,(0,),(0,),mode,[pair,pair],table))
                endpoints += 1
    controls = []
    # Wrong constant per column; f=2 must retain i^(2*q0).
    wrong = P.compile_phase((1,1), (3,3), 0)[0]
    try:
        packet(2,1,1,1,3,(1,1),(3,3),1,code=wrong)
    except ValueError:
        controls.append('drop_repeated_constant')
    # Dropping one actual quadratic edge while retaining parity/symmetry.
    rows = list(P.SELECTED_ROWS);rows[0] ^= 2;rows[1] ^= 1
    wrong = P.compile_phase(P.SELECTED_LINEAR,tuple(rows),P.SELECTED_CONSTANT)[0]
    try:
        packet(1,1,1,1,3,code=wrong)
    except ValueError:
        controls.append('drop_actual_quadratic_pair')
    # Changing one odd coefficient reverses its zero/one-flip contribution.
    linear = list(P.SELECTED_LINEAR);linear[0] = 1
    wrong = P.compile_phase(tuple(linear),P.SELECTED_ROWS,P.SELECTED_CONSTANT)[0]
    try:
        packet(1,1,1,1,3,code=wrong)
    except ValueError:
        controls.append('wrong_actual_linear_sign')
    # Corrupt the actual commit instruction, keeping input and oracle intact.
    wrong = list(code)
    index = next(i for i, row in enumerate(wrong) if row == ('write', P.DATA, '0'))
    wrong[index] = ('write', P.DATA, '1')
    try:
        packet(1,1,1,1,3,code=tuple(wrong))
    except ValueError:
        controls.append('commit_bit_corruption')
    need(len(controls) == 4, 'all semantic mutants rejected')
    out = {'status':'PASS_LITERAL_NATIVE_QUADRATIC_PHASE_NO_NEW_KAPPA',
           'source_sha256':hashlib.sha256((HERE/'phase.py').read_bytes()).hexdigest(),
           'table_locations':len(code), 'tapes':23,
           'table_sha256':hashlib.sha256(json.dumps(code,separators=(',',':'),sort_keys=True).encode()).hexdigest(),
           'complete_packets':len(results), 'selected_complete_packets':4,
           'signed_endpoint_pairs':endpoints, 'range_rejections':sum(x['rejected'] for x in results),
           'literal_transitions':sum(x['steps'] for x in results), 'negative_controls':controls,
           'scope':'Finite evidence; universal f, payload, head and cost statements are in PROOF.md.'}
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
