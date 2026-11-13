"""Literal rank2/HOME replay, source binding and discriminating controls."""
from pathlib import Path
import atexit
import hashlib
import json
import random
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
_cache = tempfile.TemporaryDirectory(prefix='rank2-verifier-source-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode = True
sys.pycache_prefix = str(Path(_cache.name) / 'required-absent')
if Path(sys.pycache_prefix).exists():
    raise ValueError('fresh source cache')
sys.path.insert(0, str(HERE))
import adapter as A
import rank2 as C
from machine import Program, initial, fields, check_retired, Rejected
from oracle import header, encode, image_f1, expected_f1, reverse9
from bind_source import verify as bind_source


def need(ok, message):
    if not ok:
        raise ValueError(message)


def guards():
    from controller_reference import Machine, Tape
    code, _ = C.compile_guard()
    rows = []
    cases = [(f, t) for f in (1, 2, 3, 5, 16, 65, 129)
             for t in (2 * f - 1, 2 * f, 2 * f + 1)]
    cases += [(1, 1 << n) for n in (63, 257, 512, 1024, 4096)]
    for f, cutoff in cases:
        shape = (f, 2, 3, 2, 5, cutoff)
        text = header(shape)
        origins = [7 * i - 103 for i in range(29)]
        tapes = [Tape({o - 5: '0', o + 1000000: '1'}, o) for o in origins]
        tapes[0].cells.update({origins[0] + i: b for i, b in enumerate(text)})
        before = [t.cells.copy() for t in tapes]
        cpu = Machine(code, tapes)
        try:
            cpu.run(5000000)
            accepted = True
        except ValueError as exc:
            need(str(exc) == 'invalid scanned symbol', 'guard failed for unrelated reason')
            accepted = False
        need(accepted == (2 * f <= cutoff), 'actual 2f cutoff decision')
        need(tapes[0].cells == before[0], 'guard changed original header')
        if accepted:
            need([t.head for t in tapes] == origins and
                 [t.cells for t in tapes] == before, 'guard full retirement')
        rows.append(dict(f=f, cutoff_bitlength=cutoff.bit_length(), E=len(text),
                         accepted=accepted, steps=cpu.steps))
    # This executes the wrong guard, demonstrating why two old f guards are
    # insufficient to enforce the direct rank-two source branch.
    weak, _ = C.compile_guard(weak=True)
    ts = [Tape({}, 0) for _ in range(29)]
    ts[0] = Tape(dict(enumerate(header((1, 1, 1, 1, 5, 1)))), 0)
    Machine(weak, ts).run()
    return rows


def supplied_replacement(state, payloads):
    """Explicit caller work outside the primitive bill; retain all history."""
    text = '^' + '|'.join(payloads) + '|$'
    symbols = {s: i for i, s in enumerate('_01^|$')}
    o = state.origins[0]
    state.tapes[0][o + 1:-3] = bytes(len(state.tapes[0]) - o - 4)
    state.tapes[0][o:o + len(text)] = bytes(symbols[s] for s in text)


def source_corruption():
    with tempfile.TemporaryDirectory(prefix='rank2-source-control-') as directory:
        target = Path(directory)
        for name in ('rank2.py', 'SOURCES.json', 'RECIPE.json'):
            shutil.copy2(HERE / name, target / name)
        for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
            dest = target / pin['local']; dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HERE / pin['local'], dest)
        source = target / 'reference/linear/linear.py'
        source.write_bytes(source.read_bytes() + b'\n# actual changed retained byte\n')
        launcher = ('import sys,tempfile;from pathlib import Path;'
                    'd=tempfile.TemporaryDirectory();sys.dont_write_bytecode=True;'
                    'sys.pycache_prefix=str(Path(d.name)/"absent");'
                    'sys.path.insert(0,' + repr(str(target)) + ');import rank2')
        r = subprocess.run([sys.executable, '-I', '-B', '-c', launcher], capture_output=True, text=True)
        need(r.returncode != 0 and 'source drift' in r.stderr, 'actual source corruption imported')


def run():
    source = bind_source()
    guard_rows = guards()
    code, alphabet, entries = C._compile_move()
    need(alphabet == ('_', '0', '1', '|'), 'fixed alphabet')
    need(not any(op == 'write' and args[0] == C.DATA for op, *args in code[:entries['commit']]),
         'core original owner write before final commit')
    for pc, (op, *args) in enumerate(code):
        if op in ('read', 'write', 'move'):
            need(0 <= args[0] < C.TAPES, 'core port bound')
        if op == 'read':
            need(all(0 <= target < len(code) for target in args[1].values()), 'core branch bound')
        if op == 'goto':
            need(0 <= args[0] < len(code), 'core goto bound')
        if op == 'move':
            need(args[1] in (-1, 1), 'unit core move')
    g, stages = A.compile_home()
    program = Program(g)
    rng = random.Random(28141)
    shape = (1, 1, 1, 1, 5, 2)
    values = [(2 * rng.randrange(-2, 3), 2 * rng.randrange(-2, 3)) for _ in range(512)]
    h, data = header(shape), encode(values, shape[4])
    bits = h + data
    output_values = image_f1(values, shape)
    expected = h + encode(output_values, shape[4])
    need(expected != bits and any(a or b for a, b in output_values), 'nontrivial dense owned packet')
    parked = ''.join(str(rng.randrange(2)) for _ in bits)
    state = initial((parked, bits), A.TAPES, old_history=3 * len(bits))
    entry_history = state.highs.copy()
    program.run(state, stop=stages['core_return'])
    need(fields(state) == (parked, bits) and state.writes[0] == 0, 'HOME changed before core return')
    prefix_steps = state.steps
    program.run(state, start=stages['core_return'], stop=stages['primitive_return'])
    need(fields(state) == (parked, bits) and state.writes[0] == 0, 'HOME changed before B1 scatter')
    program.run(state, start=stages['primitive_return'])
    need(fields(state) == (parked, expected), 'actual complete rank2 HOME image')
    check_retired(state)
    first = dict(shape=shape, F=len(bits), E=len(h), V=len(data), steps=state.steps,
                 core_return_steps=prefix_steps, HOME_writes=state.writes[0],
                 output_sha256=hashlib.sha256(expected.encode()).hexdigest())
    need(state.writes[0] == len(bits), 'complete same owned HOME commit')
    need(state.steps <= 128 * (len(bits) + 1) + (1 << 24) * (len(data) + len(h) + 1), 'complete MOVE bill')
    # Same actual owners/private tapes; caller supplies a smaller new packet.
    smaller = (1, 1, 1, 1, 4, 1 << 63)
    small_values = [(2 * rng.choice((-1, 1)), 2 * rng.choice((-1, 1))) for _ in range(512)]
    small_bits = header(smaller) + encode(small_values, 4)
    small_expected = header(smaller) + expected_f1(small_values, smaller)
    need(len(small_bits) < len(bits), 'shorter actual reuse')
    small_parked = ('10' * len(small_bits))[:len(small_bits)]
    old_highs = state.highs.copy(); before_steps = state.steps
    supplied_replacement(state, (small_parked, small_bits))
    program.run(state)
    need(fields(state) == (small_parked, small_expected), 'same-owner smaller packet')
    check_retired(state)
    need(all(a >= b for a, b in zip(state.highs, old_highs)), 'prior backing was refunded')
    reuse = dict(shape=smaller, F=len(small_bits), steps=state.steps - before_steps,
                 retained_guide_high=state.highs[-1], entry_guide_high=entry_history[-1])
    # The physical rank guard rejects where the old f guard would accept.
    bad_shape = (1, 1, 1, 1, 5, 1)
    bad_bits = header(bad_shape) + data
    rejected = initial(('0' * len(bad_bits), bad_bits), A.TAPES)
    saved = bytes(rejected.tapes[0])
    try:
        program.run(rejected)
    except Rejected:
        pass
    else:
        raise ValueError('f<=cutoff<2f accepted')
    need(rejected.writes[0] == 0 and bytes(rejected.tapes[0]) == saved, 'bad cutoff changed HOME')
    # Manufacture R*x with value one on both first-slot bits and zero
    # elsewhere. The first C pass and slot swap complete; the second pass
    # then has a genuine half-integral result. This exercises whole-call
    # staging after a completed child, without assuming rollback/retry.
    right = C.RECIPE['right']
    numeric = [(0, 0)] * 512
    for x in range(512):
        target = sum(((row & x).bit_count() & 1) << i for i, row in enumerate(right['matrix_rows']))
        if target in (0, 1):
            q = sum(right['linear_Z4'][i] for i in range(9) if (x >> i) & 1)
            q += 2 * sum(1 for i in range(9) for j in range(i + 1, 9)
                         if (x >> i) & (x >> j) & (right['quadratic_rows'][i] >> j) & 1)
            numeric[reverse9(x)] = ((1, 0), (0, -1), (-1, 0), (0, 1))[q % 4]
    numeric_bits = h + encode(numeric, shape[4])
    late = initial(('0' * len(numeric_bits), numeric_bits), A.TAPES)
    saved_late_home = bytes(late.tapes[0])
    base = int(stages['core_entry'].rsplit('.', 1)[1])
    second = 'MOVE28141.' + str(base + entries['second_C_'])
    need(second in program.labels, 'literal second-child location')
    program.run(late, stop=second)
    first_child_completed_steps = late.steps
    need(late.writes[0] == 0, 'HOME changed before second child')
    middle = [(0, 0)] * 512
    middle[0] = middle[128] = (1, 0)
    start = late.origins[A.CORE_BASE + C.WORK] + 2
    need(bytes(late.tapes[A.CORE_BASE + C.WORK][start:start + len(data)]) ==
         bytes(1 if b == '0' else 2 for b in encode(middle, shape[4])),
         'first C and exact slot swap did not complete')
    try:
        program.run(late, start=second)
    except Rejected:
        pass
    else:
        raise ValueError('second-child nonintegral prefix accepted')
    need(late.writes[0] == 0 and bytes(late.tapes[0]) == saved_late_home,
         'later numerical rejection changed original HOME')
    # Full actual graph with a wrong constant phase: should complete cleanly
    # but produce exactly i times the correct f=1 image, proving separation.
    wrong_graph, _ = A.compile_home(mutation='wrong_phase')
    wrong = initial((parked, bits), A.TAPES)
    Program(wrong_graph).run(wrong)
    rotated = h + encode([(-b, a) for a, b in output_values], shape[4])
    need(fields(wrong) == (parked, rotated) and rotated != expected, 'absolute-phase graph control')
    check_retired(wrong)
    source_corruption()
    return dict(marker='PASS_LITERAL_OWNED_RANK2_HOME', source=source,
                core_locations=len(code), core_graph_sha256=hashlib.sha256(repr(code).encode()).hexdigest(),
                HOME_states=len(g.rules), tapes=A.TAPES, core_tapes=C.TAPES,
                owned_entry='supplied already-reserved raw-native-owned28141/1526; no INIT producer',
                full_f1=first, same_owner_reuse=reuse, cutoff_rejection_steps=rejected.steps,
                second_child_rejection=dict(first_child_completed_steps=first_child_completed_steps,
                                            rejection_steps=late.steps, HOME_writes=late.writes[0]),
                wrong_phase_full_steps=wrong.steps, guard_cases=guard_rows,
                controls=['2f cutoff vs old f guard', 'full graph absolute phase', 'actual retained source corruption',
                          'inverse source orientation', 'one C instead of two', 'no early original-owner writes',
                          'second-child rejection after completed first C and slot swap'],
                scope='Exact supplied Gamma6/HOME leaf primitive only; no full lifetime, endpoint conversion or nonleaf rate.')


if __name__ == '__main__':
    start = time.monotonic()
    result = run()
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    elif (HERE / 'RESULT.json').exists():
        need(json.loads((HERE / 'RESULT.json').read_text()) == json.loads(json.dumps(result)), 'scientific receipt changed')
    print(json.dumps(result, indent=2, sort_keys=True))
    print('elapsed_seconds', round(time.monotonic() - start, 3))
