"""Check the binary lowering, full states, meters, and retained tape storage."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
bm = runpy.run_path(str(HERE / 'binary_machine.py'))
need, lower, execute, admit, ENCODING = (bm[k] for k in ('need', 'lower', 'execute', 'admit', 'ENCODING'))

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_text())['files']
    result = {}
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            need(sha256(data).hexdigest() == row['sha256'], 'source bytes: ' + row['path'])
            result[Path(row['path']).name] = data
    return result

def encode(cells):
    return bytearray(bit for cell in cells for bit in ENCODING[cell])

def reject(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('negative control accepted')

def micro_checks():
    checked = 0
    for head in (0, 1, 4):
        for value in range(5):
            cells = [2, value, 3]
            if head == 0:
                cells[0] = value
            if head == 4:
                cells += [1, value]
            for symbol in range(5):
                source = (('test', 't', symbol, 1, 2), ('halt', 'returned'), ('halt', 'rejected'))
                code, entries = lower(source, {'run': 0}, ('t',))
                tapes, heads = {'t': encode(cells)}, {'t': 3*head}
                receipt = execute(code, tapes, heads, entries['run'])
                need(receipt == dict(status='returned' if value == symbol else 'rejected',
                     steps=9, reads=3, writes=0, moves=4, jumps=1), 'test meter or branch')
                need(tapes['t'] == encode(cells) and heads['t'] == 3*head, 'test frame')
                checked += 1
            for symbol in range(5):
                source = (('write', 't', symbol), ('halt', 'returned'))
                code, entries = lower(source, {'run': 0}, ('t',))
                tapes, heads = {'t': encode(cells[:2])}, {'t': 3*head}
                receipt = execute(code, tapes, heads, entries['run'])
                expected = cells[:2] + [4]*max(0, head+1-2)
                expected[head] = symbol
                need(tapes['t'] == encode(expected) and heads['t'] == 3*head, 'write frame or extent')
                need(receipt == dict(status='returned', steps=9, reads=0, writes=3, moves=4, jumps=1), 'write meter')
                checked += 1
    for step in (-1, 1):
        code, entries = lower((('move', 't', step), ('halt', 'returned')), {'run': 0}, ('t',))
        tapes, heads = {'t': encode([2])}, {'t': 6}
        receipt = execute(code, tapes, heads, entries['run'])
        need(heads['t'] == 6+3*step and tapes['t'] == encode([2]), 'move frame')
        need(receipt['steps'] == 5 and receipt['moves'] == 3, 'move meter')
        checked += 1
    negative_move, _ = lower((('move', 't', -1), ('halt', 'returned')), {'run': 0}, ('t',))
    reject(lambda: execute(negative_move, {'t': encode([2])}, {'t': 0}, 0))
    code, entries = lower((('test', 't', 4, 1, 2), ('halt', 'returned'), ('halt', 'closed')), {'run': 0}, ('t',))
    tapes, heads = {'t': bytearray()}, {'t': 21}
    need(execute(code, tapes, heads, 0)['status'] == 'returned' and not tapes['t'] and heads['t'] == 21, 'unallocated blank')
    for value in ((1, 0, 1), (1, 1, 0), (1, 1, 1)):
        tapes, heads = {'t': bytearray(value)}, {'t': 0}
        need(execute(code, tapes, heads, 0)['status'] == 'rejected' and heads['t'] == 0, 'invalid codeword')
    # Change real lowered instructions and require observable failures.
    bad = list(code)
    pos = next(i for i, row in enumerate(bad) if row == ('move', 't', -1))
    bad[pos] = ('jump', pos+1)
    tapes, heads = {'t': encode([4])}, {'t': 0}
    execute(bad, tapes, heads, 0)
    reject(lambda: need(heads['t'] == 0, 'missing alignment move'))
    write, _ = lower((('write', 't', 3), ('halt', 'returned')), {'run': 0}, ('t',))
    for index, label in ((0, 'wrong bit'), (4, 'missing tail write')):
        bad = list(write)
        bad[index] = ('write', 't', 0) if index == 0 else ('jump', index+1)
        tapes, heads = {'t': bytearray()}, {'t': 0}
        execute(bad, tapes, heads, 0)
        reject(lambda: need(tapes['t'] == encode([3]), label))
    reject(lambda: admit((('call', 'host'),), {'run': 0}, ('t',), (0, 1)))
    reject(lambda: admit((('jump', 0),), {'run': 0}, ('t',), (0, 1)))
    reject(lambda: admit((('write', 't', 2), ('halt', 'closed')), {'run': 0}, ('t',), (0, 1)))
    return dict(positive=checked+1, invalid_codewords=3,
                rejected=['left_origin_crossing', 'missing_alignment_move', 'wrong_bit', 'missing_tail_write',
                          'host_callback', 'control_only_cycle', 'nonbinary_write'])

def fixture(h, a=1, g=1, s=1, bits=None, install=False):
    n = a*4**h*g*s
    if bits is None:
        bits = [((i*13) ^ (i//3)) & 1 for i in range(n)]
    return dict(geometry=[h, a, g, s], bits=bits, install=install)

def permutation(case):
    h, a, g, s = case['geometry']
    return [case['bits'][((((p*2**h+x)*g+m)*2**h+y)*s)+b]
            for p in range(a) for y in range(2**h) for m in range(g)
            for x in range(2**h) for b in range(s)]

def run():
    source = authenticate()
    namespace = {}
    exec(compile(source['program.py'], 'pinned-program.py', 'exec'), namespace)
    original, original_entries = namespace['assemble']()
    need(sha256(canonical((original, original_entries)).encode()).hexdigest() ==
         json.loads(source['RESULT.json'])['program_sha256'], 'source program digest')
    roles, borrowed = namespace['ROLES'], namespace['BORROWED']
    code, entries = lower(original, original_entries, roles)
    sessions = [[fixture(h)] for h in range(4)]
    sessions += [[fixture(0, 2, 3, 2)], [fixture(1, 2, 2, 2)], [fixture(2, 1, 2, 1, install=True)]]
    sessions += [[fixture(1, g=2, bits=[int(i == j) for i in range(8)])] for j in range(8)]
    sessions += [[fixture(0), fixture(2, g=2), fixture(1)]]
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        for name in ('program.py', 'machine.py'):
            (directory/name).write_bytes(source[name])
        driver = directory/'reference.py'
        driver.write_bytes((HERE/'reference.py').read_bytes())
        response = subprocess.run([sys.executable, '-I', '-B', str(driver)], input=canonical(sessions),
                                  capture_output=True, text=True, timeout=60)
        need(response.returncode == 0, 'source process: ' + response.stderr)
        reference = json.loads(response.stdout)
    totals = dict(steps=0, reads=0, writes=0, moves=0, jumps=0)
    original_steps = 0
    events = 0
    state_digest = sha256()
    for session, source_events in zip(sessions, reference, strict=True):
        tapes = {r: encode([4]) for r in roles}
        heads = {r: 0 for r in roles}
        case_index = -1
        for event in source_events:
            entry = event['entry']
            if entry == 'run':
                case_index += 1
                case = session[case_index]
                h, a, g, s = case['geometry']
                tapes['SOURCE'] = encode([2] + case['bits'])
                for r, v in zip(('H', 'A', 'G', 'S'), (h, a, g, s)):
                    tapes[r] = encode([2] + [int(x) for x in reversed(bin(v)[2:])] + [3])
                for r in borrowed:
                    heads[r] = 3
            receipt = execute(code, tapes, heads, entries[entry])
            expected_tapes = {r: encode(v) for r, v in event['tapes'].items()}
            need(tapes == expected_tapes and heads == {r: 3*v for r, v in event['heads'].items()}, 'complete state')
            old = event['receipt']
            reads, writes, moves = (old[k] for k in ('reads', 'writes', 'moves'))
            jumps = old['steps'] - reads - writes - moves - 1
            expected = dict(status=old['status'], reads=3*reads, writes=3*writes,
                            moves=4*(reads+writes)+3*moves, jumps=reads+writes+moves+jumps,
                            steps=8*(reads+writes)+4*moves+jumps+1)
            need(receipt == expected and receipt['steps'] <= 8*old['steps'], 'exact meter')
            if entry == 'run':
                oracle = encode(permutation(case))
                need(tapes['OUTPUT'][3:3+len(oracle)] == oracle, 'independent permutation')
            for k in totals:
                totals[k] += receipt[k]
            original_steps += old['steps']
            state_digest.update(canonical(event).encode())
            events += 1
    controls = micro_checks()
    need(authenticate() == source, 'source changed during replay')
    return dict(status='PASS_BINARY_ELEMENTARY_INTERCHANGE', source_program_length=len(original),
                binary_program_length=len(code), binary_program_sha256=sha256(canonical((code, entries)).encode()).hexdigest(),
                entries=entries, binary_control_factor=admit(code, entries, roles, (0, 1)),
                tape_roles=len(roles), sessions=len(sessions), entry_comparisons=events,
                source_steps=original_steps, binary_actions=totals, source_states_sha256=state_digest.hexdigest(),
                controls=controls, code_sha256={n: sha256((HERE/n).read_bytes()).hexdigest()
                                              for n in ('binary_machine.py', 'reference.py')})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    expected = None if args.emit else json.loads((HERE/'RESULT.json').read_text())
    result = run()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        need(canonical(result) == canonical(expected), 'complete typed receipt')
        print(result['status'])
