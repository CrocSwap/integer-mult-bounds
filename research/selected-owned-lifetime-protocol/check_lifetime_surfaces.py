"""Independent sparse-tape checks of the C4 delivery seams, not its cores.

Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
Default execution is read-only; --receipt explicitly writes a JSON receipt.
"""
import argparse
from dataclasses import replace
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
import types


def require(value, message):
    if not value:
        raise ValueError(message)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def run(graph, start, tapes, heads=None, limit=100000):
    """All tests are read before any write; no predecessor CPU is imported."""
    heads = [0] * 44 if heads is None else list(heads)
    writes = []
    visits = [{head} for head in heads]
    steps, state = 0, start
    while state != 'HALT':
        choices = []
        for rule in graph.rules[state]:
            if all(tapes[t].get(heads[t], '_') == value for t, value in rule.tests):
                choices.append(rule)
        require(len(choices) == 1, 'missing or ambiguous literal transition')
        rule, = choices
        for t, value in rule.writes:
            require(heads[t] > 0, 'permanent origin or exterior write')
            tapes[t][heads[t]] = value
            writes.append((t, heads[t], value))
        for t, delta in rule.moves:
            require(delta in (-1, 1), 'nonunit move')
            heads[t] += delta
            require(heads[t] >= 0, 'crossed permanent origin')
            visits[t].add(heads[t])
        steps += 1
        require(steps <= limit, 'surface watchdog')
        state = rule.target
    return steps, heads, writes, visits


def tape(text='^'):
    result = dict(enumerate(text))
    result[-1] = '!'
    result[20000] = '?'
    return result


def body(t, length):
    return ''.join(t.get(i, '_') for i in range(1, length + 1))


def unchanged_exterior(before, after, allowed):
    for index, (left, right) in enumerate(zip(before, after)):
        for cell in left.keys() | right.keys():
            if (index, cell) not in allowed:
                require(left.get(cell, '_') == right.get(cell, '_'), 'unexpected exterior mutation')


def surface_checks(p, d):
    records = []
    for f in (1, 2, 17, 257):
        fields = [''.join(str(((i * i + 3 * slot + i // (slot + 1)) >> slot) & 1)
                          for i in range(f)) for slot in range(5)]
        replacement = ''.join('1' if i % 3 == 0 else '0' for i in range(f))
        for family in ('home', 'bank'):
            for selected in (range(5) if family == 'bank' else (0,)):
                for gather in (False, True):
                    graph = d.Graph()
                    start = (p.home_transfer(graph, 3, gather, 'HALT') if family == 'home'
                             else p.bank_transfer(graph, selected, 3, gather, 'HALT'))
                    tapes = [tape() for _ in range(44)]
                    owner = 2 if family == 'home' else 43
                    original = fields[selected] if family == 'home' else '|'.join(fields)
                    tapes[owner] = tape('^' + original + '|$')
                    if not gather:
                        tapes[3] = tape('^' + replacement + '|')
                    before = [dict(t) for t in tapes]
                    steps, heads, writes, visits = run(graph, start, tapes)
                    require(heads == [0] * 44, 'surface head return')
                    require(steps == ((3*f+7) if family == 'home' else (11*f+16)), 'exact surface price')
                    if gather:
                        require(body(tapes[3], f+1) == fields[selected] + '|', 'wrong gathered field')
                        require(tapes[owner] == before[owner], 'gather changed source')
                        allowed = {(3, i) for i in range(1, f+2)}
                    else:
                        require(body(tapes[3], f+1) == '_'*(f+1), 'scatter failed full retirement')
                        expected = list(fields)
                        expected[selected] = replacement
                        final = replacement if family == 'home' else '|'.join(expected)
                        require(body(tapes[owner], len(final)+2) == final+'|$', 'wrong scatter or guard')
                        offset = 0 if family == 'home' else selected*(f+1)
                        allowed = {(owner, offset+i) for i in range(1, f+1)} | {(3, i) for i in range(1, f+2)}
                    unchanged_exterior(before, tapes, allowed)
                    records.append([family, f, selected, gather, steps])
        graph = d.Graph()
        start = p.clear_work(graph, 3, 'HALT')
        tapes = [tape() for _ in range(44)]
        tapes[3] = tape('^' + replacement + '|')
        steps, heads, writes, visits = run(graph, start, tapes)
        require(steps == 2*f+4 and heads == [0]*44, 'clear exact price/return')
        require(body(tapes[3], f+1) == '_'*(f+1), 'clear incomplete')
        require(len(writes) == f+1, 'clear must write entire body and separator')
        records.append(['clear', f, steps])
    return records


def controls(p, d):
    graph = d.Graph()
    start = p.clear_work(graph, 3, 'HALT')
    for name, rules in graph.rules.items():
        graph.rules[name] = [replace(rule, writes=()) for rule in rules]
    tapes = [tape() for _ in range(44)]
    tapes[3] = tape('^10101|')
    steps, heads, writes, visits = run(graph, start, tapes)
    require(heads == [0]*44 and body(tapes[3], 6) != '_'*6,
            'missing-clear mutation must finish but fail retirement oracle')
    graph = d.Graph()
    start = p.home_transfer(graph, 3, True, 'HALT')
    tapes = [tape() for _ in range(44)]
    tapes[2] = tape('^10101|0')
    rejected = False
    try:
        run(graph, start, tapes)
    except ValueError as error:
        rejected = str(error) == 'missing or ambiguous literal transition'
    require(rejected, 'missing endpoint was accepted')
    for direction, origin in ((-1, 1), (1, 0)):
        graph = d.Graph()
        start = p.shifted_heads(graph, direction, 'HALT')
        heads = [0]*44
        for index in range(3, 43):
            heads[index] = origin
        tapes = [tape() for _ in range(44)]
        steps, result, writes, visits = run(graph, start, tapes, heads)
        require(steps == 40 and writes == [], 'head convention cost')
        require(result == [value+(direction if 3 <= i < 43 else 0)
                           for i, value in enumerate(heads)], 'head convention role drift')
    graph = d.Graph()
    relocated = p.Relocate(graph)
    for index in range(1, 35):
        state = graph.state('probe')
        relocated.add(state, 'HALT', ((index, '0'),), ((index, '1'),), ((index, 1),))
        rule, = graph.rules[state]
        require(rule.tests == ((index+2, '0'),) and rule.writes == ((index+2, '1'),)
                and rule.moves == ((index+2, 1),), 'service port relocation')
    return {'missing_clear_write_detected': True, 'missing_endpoint_rejected': True,
            'two_40_step_head_changes': True, 'all_34_service_roles_mapped': True}


def chronology(package):
    raw = (package/'SOURCE-INTERVAL.json.gz').read_bytes()
    binding = json.loads((package/'SOURCE-INTERVAL-BINDING.json').read_text())
    require(len(raw) == binding['interval_bytes'] and sha256(raw).hexdigest()
            == binding['interval_sha256'], 'retained interval bytes')
    source = json.loads(gzip.decompress(raw))
    begin, end = source['start'], source['end_inclusive']
    program = source['program']
    require((begin, end, len(program)) == (28037, 37618, 9582), 'interval extent')
    frames = {int(k): value for k, value in source['initial_current_frames'].items()}
    require(frames[1349] == 3 and 1526 not in frames, 'exact INIT entrance')
    contacts, receiver = [], []
    for index, row in enumerate(program, begin):
        operation, owner, *args = row
        if operation == 'INIT':
            require(owner not in frames, 'live INIT in retained chronology')
            frames[owner] = args[0]
            touched = {owner}
        elif operation in ('ADD', 'COPY'):
            donor, coefficient, frame = args
            require(frames[owner] == frame and frames[donor] == frame, 'contact frame mismatch')
            touched = {owner, donor}
        elif operation == 'MOVE':
            old, new, owned = args
            require(frames[owner] == old, 'MOVE entrance mismatch')
            frames[owner] = new
            touched = {owner}
        elif operation == 'SCALE':
            coefficient, frame = args
            require(frames[owner] == frame, 'SCALE entrance mismatch')
            touched = {owner}
        elif operation == 'CLEAR':
            require(frames.pop(owner) == args[0], 'CLEAR entrance mismatch')
            touched = {owner}
        else:
            raise ValueError('unknown source opcode')
        if 1526 in touched:
            contacts.append([index, row])
        if 1515 in touched:
            receiver.append([index, row])
    expected = [28037, 28041, 28129, 28135, 28139, 28141, 28159, 37618]
    require([item[0] for item in contacts] == expected, 'owner projection')
    require(receiver[:2] == [[28153, ['INIT', 1515, 470]],
                            [28159, ['ADD', 1515, 1526, '1', 470]]], 'actual receiver was not zero')
    gaps = [right-left-1 for left, right in zip(expected, expected[1:])]
    require(gaps == [3, 87, 5, 3, 1, 17, 9458], 'source gap lengths')
    return {'contacts': contacts, 'gap_lengths': gaps, 'all_9582_frame_steps_checked': True,
            'actual_receiver_is_zero': True, 'interval_sha256': binding['interval_sha256']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    package = args.package.resolve()
    p = load(package/'protocol.py', '_independent_lifetime_protocol')
    d = load(package/'inputs/add/inputs/tape_graph.py', '_independent_surface_graph')
    expected = 'c324967962e04a125bbdb5f503d3d6c3cff5d7eb69343443bc6ea4338af243bd'
    require(sha256((package/'protocol.py').read_bytes()).hexdigest() == expected, 'frozen protocol drift')
    result = {'status': 'PASS', 'protocol_sha256': expected,
              'surface_cases': surface_checks(p, d), 'controls': controls(p, d),
              'chronology': chronology(package),
              'scope': 'Only new delivery surfaces, port shifts and retained chronology; no embedded arithmetic replay.'}
    encoded = json.dumps(result, indent=2)+'\n'
    if args.receipt:
        args.receipt.write_text(encoded)
    print(json.dumps({'status': 'PASS', 'surface_cases': len(result['surface_cases']),
                      'source_events': 9582, 'controls': result['controls']}, sort_keys=True))


if __name__ == '__main__':
    main()
