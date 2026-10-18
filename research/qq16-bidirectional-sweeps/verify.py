#!/usr/bin/env python3
"""Optimal QQ16 sweep directions. Arham Tahir, OpenAI Codex assistance. Apache-2.0."""
import gzip
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
WINDOWS = ((633, 1066, 'L2'), (1172, 2125, 'F0_inverse'))
MAX_BYTES = 256_000
MAX_EVENTS = 1408
MAX_SITES = 64


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field(name):
    require(type(name) is str and 2 <= len(name) <= 4, 'field syntax')
    require(name[0] in 'ZW' and name[1:].isdigit(), 'owned field')
    bank = int(name[1:])
    require(0 <= bank < 112 and name == name[0] + str(bank), 'canonical bank')
    return (0 if name[0] == 'Z' else 1), bank


def roles(event):
    if event['op'] == 'clear':
        return [field(event['field'])]
    require(event['op'] == 'add', 'scalar-only instruction')
    require(event['coefficient'] in ('1', '-1', '1/4', '-1/4'), 'coefficient')
    require(event['src'] != event['dst'], 'distinct scalar fields')
    return [field(event['src']), field(event['dst'])]


def load_word():
    pins = json.loads((HERE / 'SOURCES.json').read_text())['pending_source']
    require(pins['archive'] == 'source-word.json.gz', 'fixed input path')
    archive = HERE / 'source-word.json.gz'
    require(archive.stat().st_size <= MAX_BYTES, 'compressed source capacity')
    with gzip.open(archive, 'rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) == pins['uncompressed_bytes'] <= MAX_BYTES, 'source capacity')
    require(hashlib.sha256(raw).hexdigest() == pins['sha256'], 'source SHA256')
    header = b'blob ' + str(len(raw)).encode() + b'\0'
    require(hashlib.sha1(header + raw).hexdigest() == pins['git_blob'], 'Git blob')
    word = json.loads(raw)
    require(type(word) is list and len(word) == 2415, 'source word extent')
    return word


def extract(word, start, stop, name):
    first, last = word[start], word[stop]
    active = ['W0'] if name == 'L2' else [f'W{i}' for i in range(16)]
    for marker, op in ((first, 'output_slices_begin'), (last, 'output_slices_end')):
        require(marker['op'] == op and marker['name'] == name, 'window marker')
        require(marker['fields'] == active, 'window scratch allocation')
    body = word[start + 1:stop]
    require(0 < len(body) <= MAX_EVENTS, 'window capacity')
    for event in body:
        for tape, bank in roles(event):
            require(tape == 0 or 'W' + str(bank) in active, 'active W field')
        if event['op'] == 'clear':
            require(event['frame'] in ('current', 'identity'), 'CLEAR frame')
    return body


def bridge(body):
    """Reconstruct PR2722's dirty bridges without importing its implementation."""
    rewritten, count = [], 0
    for event in body:
        touched = roles(event)
        if len(touched) == 2 and touched[0][0] == touched[1][0]:
            require(touched[0][0] == 1, 'only W-to-W bridges')
            require(event['coefficient'] == '-1', 'bridge subtraction')
            src, dst = event['src'], event['dst']
            require(int(src[1:]) == int(dst[1:]) + 8, 'paired W bridge')
            for source, target, value in (
                (src, 'Z0', '1'), ('Z0', dst, '-1'),
                (src, 'Z0', '-1'), ('Z0', dst, '1'),
            ):
                rewritten.append(dict(op='add', src=source, dst=target, coefficient=value))
            count += 1
        else:
            rewritten.append(dict(event))
    require(len(rewritten) <= MAX_EVENTS, 'rewritten event capacity')
    for event in rewritten:
        ts = [t for t, _ in roles(event)]
        require(len(ts) == len(set(ts)), 'at most one bank per tape per instruction')
    return rewritten, count


def transition(touched, banks, state, direction, sites):
    """Endpoint recurrence; direction 0 increases, 1 decreases."""
    next_state, cost = list(state), 0
    for tape, bank in touched:
        previous = banks[tape] * sites + state[tape] * (sites - 1)
        start = bank * sites + direction * (sites - 1)
        cost += abs(start - previous) + sites - 1
        next_state[tape] = 1 - direction
    return tuple(next_state), cost


def optimize(body):
    """Minimizing N=2 minimizes every N>1; all paths have the same cost at N=1."""
    states, banks, largest = {(0, 0): (0, '')}, [0, 0], 1
    for event in body:
        touched, following = roles(event), {}
        for state, (cost, path) in sorted(states.items()):
            for direction in (0, 1):
                key, charge = transition(touched, banks, state, direction, 2)
                candidate = cost + charge, path + str(direction)
                if key not in following or candidate < following[key]:
                    following[key] = candidate
        for tape, bank in touched:
            banks[tape] = bank
        states = following
        largest = max(largest, len(states))
        require(len(states) <= 4, 'two endpoint bits')
    options = []
    for state, (cost, path) in states.items():
        home = sum(2 * banks[tape] + state[tape] for tape in (0, 1))
        options.append((cost + home, path))
    minimum, path = min(options)
    base = literal_travel(body, path, 1)
    return path, [minimum - base, 2 * base - minimum], largest


def literal_travel(body, path, sites, return_home=True):
    """Separate reference: enumerate actual source and destination addresses."""
    require(type(sites) is int and 1 <= sites <= MAX_SITES, 'trace capacity')
    require(type(path) is str and len(path) == len(body), 'one direction per event')
    require(set(path) <= {'0', '1'}, 'binary directions')
    heads, total = [0, 0], 0
    for event, direction in zip(body, path, strict=True):
        order = range(sites) if direction == '0' else range(sites - 1, -1, -1)
        for site in order:
            for tape, bank in roles(event):
                address = bank * sites + site
                total += abs(address - heads[tape])
                heads[tape] = address
    return total + (sum(heads) if return_home else 0)


def execute(body, path, sites, wrong_pair=False):
    """Exact dirty scalar fixtures, independent of the movement recurrence."""
    require(1 <= sites <= 5, 'semantic fixture capacity')
    rows = {
        f'{tape}{bank}': [Fraction((bank + 3)**2 * (s + 1) + offset, 8)
                          for s in range(sites)]
        for tape, offset in (('Z', 0), ('W', 10000)) for bank in range(112)
    }
    bad_index = max(i for i, event in enumerate(body)
                    if event['op'] == 'add' and event['dst'][0] == 'Z')
    for index, (event, direction) in enumerate(zip(body, path, strict=True)):
        order = range(sites) if direction == '0' else range(sites - 1, -1, -1)
        for site in order:
            if event['op'] == 'clear':
                rows[event['field']][site] = Fraction(0)
            else:
                source_site = sites - 1 - site if wrong_pair and index == bad_index else site
                rows[event['dst']][site] += (
                    Fraction(event['coefficient']) * rows[event['src']][source_site]
                )
    return rows


def small_optimality_controls():
    """Exhaust every direction of all words through length 4 in a tiny alphabet."""
    alphabet = [dict(op='clear', field='Z0'), dict(op='clear', field='W1'),
                dict(op='add', src='Z2', dst='W0', coefficient='1')]
    words, paths = 0, 0
    for length in range(1, 5):
        for body in itertools.product(alphabet, repeat=length):
            chosen, (slope, intercept), _ = optimize(body)
            for sites in (1, 2, 3, 5):
                costs = [literal_travel(body, ''.join(p), sites)
                         for p in itertools.product('01', repeat=length)]
                require(min(costs) == slope * sites + intercept, 'exhaustive optimum')
                require(literal_travel(body, chosen, sites) == min(costs), 'attainment')
                paths += len(costs)
            words += 1
    return {'tiny_words': words, 'exhaustive_path_cases': paths}


def affine_controls():
    """Check the signed-distance derivation over the entire bank-delta alphabet."""
    cases = 0
    for delta in range(-111, 112):
        for previous, start in itertools.product((0, 1), repeat=2):
            offset = start - previous
            if delta > 0:
                slope, intercept = delta + offset, -offset
            elif delta < 0:
                slope, intercept = -delta - offset, offset
            else:
                slope, intercept = abs(offset), -abs(offset)
            for sites in (1, 2, 3, MAX_SITES):
                actual = abs(delta * sites + offset * (sites - 1))
                require(actual == slope * sites + intercept, 'affine edge law')
                cases += 1
    return cases


def check_window(body, name):
    candidate, count = bridge(body)
    require(count == (0 if name == 'L2' else 8), 'exact bridge inventory')
    path, polynomial, states = optimize(candidate)
    increasing = '0' * len(candidate)
    old = [3564, -896] if name == 'L2' else [8302, -1944]
    for sites in (*range(1, 33), MAX_SITES):
        require(literal_travel(candidate, path, sites) == polynomial[0] * sites
                + polynomial[1], 'literal optimized address trace')
        require(literal_travel(candidate, increasing, sites) == old[0] * sites
                + old[1], 'independent PR2722 tariff control')
    for sites in (2, 3, 5):
        reference = execute(body, '0' * len(body), sites)
        require(execute(candidate, path, sites) == reference, 'arbitrary dirty fixture')
        require(execute(candidate, path, sites, True) != reference, 'wrong-site control')
    require(literal_travel(candidate, path, 3, False) != polynomial[0] * 3
            + polynomial[1], 'omitted return control')
    return {'instructions': len(candidate), 'bridges': count,
            'maximum_DP_states': states, 'minimum_travel': polynomial,
            'increasing_travel': old, 'reverse_passes': path.count('1')}, path


def reject_controls(word):
    for mutation in ('native', 'borrowed', 'inactive', 'alias'):
        wrong = [dict(e) for e in word]
        if mutation == 'native':
            wrong[635] = dict(op='native', field='Z0')
        elif mutation == 'borrowed':
            wrong[635]['src'] = 'X76'
        elif mutation == 'inactive':
            wrong[635]['dst'] = 'W16'
        else:
            wrong[635]['src'] = wrong[635]['dst']
        try:
            extract(wrong, 633, 1066, 'L2')
        except (KeyError, ValueError):
            continue
        raise ValueError('accepted malformed source: ' + mutation)


def calculate():
    word = load_word()
    result, schedule = {}, {}
    for start, stop, name in WINDOWS:
        result[name], schedule[name] = check_window(extract(word, start, stop, name), name)
    reject_controls(word)
    receipt = {
        'windows': result,
        'minimum_total': [sum(r['minimum_travel'][i] for r in result.values())
                          for i in (0, 1)],
        'increasing_total': [11866, -2840],
        'scalar_invoice': {'unit_adds': 864, 'quarter_adds': 832, 'clears': 288,
                           'real_scalar_primitives': 17472},
        'small_controls': small_optimality_controls(),
        'affine_edge_cases': affine_controls(),
        'literal_sites': [*range(1, 33), MAX_SITES],
        'semantic_sites': [2, 3, 5],
        'scope': 'fixed instruction sweeps only; no complete caller or new kappa',
    }
    counts = {'unit': 0, 'quarter': 0, 'clear': 0}
    for event in word:
        if event['op'] == 'clear':
            counts['clear'] += 1
        if event['op'] == 'add':
            coefficient = abs(Fraction(event['coefficient']))
            require(coefficient in (1, Fraction(1, 4)), 'full-word scalar alphabet')
            counts['unit' if coefficient == 1 else 'quarter'] += 1
    require(counts == {'unit': 840, 'quarter': 832, 'clear': 288}, 'source invoice')
    return receipt, schedule


def main():
    result, schedule = calculate()
    for filename, actual in (('RESULT.json', result), ('SCHEDULE.json', schedule)):
        expected = json.loads((HERE / filename).read_text())
        require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
                'typed ' + filename + ' receipt')
    slope, intercept = result['minimum_total']
    print(f'PASS_QQ16_BIDIRECTIONAL_SWEEPS minimum={slope}*N{intercept:+d} '
          'scalar=17472 no_new_kappa')


if __name__ == '__main__':
    main()
