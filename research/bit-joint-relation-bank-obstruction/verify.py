"""Check all joint-subspace charges against exact receiver bases."""
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def column_pivots(vectors, width, other):
    rows = [set(v) for v in vectors]
    columns, pivots = {}, []
    for i in range(width-1, -1, -1):
        column = {j for j, row in enumerate(rows) if i in row}
        if other.insert(column, columns):
            pivots.append(i)
    return sorted(pivots)


def check_group(record, original, state, other):
    initial, final, banks, moves = state
    roles = set(original['roles'])
    lost = original['lost_rank']
    other.require(record['roles'] == original['roles'] and record['lost_rank'] == lost,
                  'all productive targets charged')
    other.require((record['entrance'], record['exit']) == (original['entrance'], original['exit']), 'boundary group')
    basis = record['basis']
    reverse = record['direction'] == 'transpose'
    n = len(roles)
    other.require(len(basis) == n and other.rank(row['signal'] for row in basis) == n
                  and all(set(row['signal']) <= roles for row in basis), 'complete helper coordinate basis')
    terminal = record['exit']
    if reverse:
        other.require([row['key'] for row in basis] == original['terminal_pivots'], 'complete chronological terminal flag')
        for row in basis:
            other.require(set(row['signal']) == other.xor_rows(banks[terminal], row['relation'])
                          and max(row['relation']) == row['key'], 'terminal flag witness')
        profiles = [[moves[row['key']]] for row in basis]
    else:
        other.require(basis == [dict(signal=[i]) for i in original['roles']], 'original coordinate basis')
        profiles = [[original['terminal_rank_max']] for _ in basis]
    expected = {space['chart']: space for space in original['spaces'] if space['chart'] != terminal}
    supplied = {space['chart']: space for space in record['spaces']}
    other.require(set(supplied) == set(expected) and len(supplied) == len(record['spaces']), 'all nonterminal receivers')
    for chart, before in expected.items():
        space = supplied[chart]
        other.require(len(space['coordinates']) == len(before['basis']), 'complete transformed receiver basis')
        for coordinates, row in zip(space['coordinates'], before['basis']):
            signal = set()
            other.require(len(set(coordinates)) == len(coordinates) and all(0 <= i < n for i in coordinates), 'coordinate indices')
            for i in coordinates:
                signal.symmetric_difference_update(basis[i]['signal'])
            other.require(signal == set(row['signal']), 'exact transformed receiver')
        keys = list(banks[chart])
        positions = {key: i for i, key in enumerate(keys)}
        bank_vectors = [{positions[k] for k in row['relation']} for row in before['basis']]
        last = [keys[i] for i in column_pivots(bank_vectors, len(keys), other)]
        other.require(last == space['bank_pivots'] and max(moves[k] for k in last) == space['rank_max'], 'all possible bank ranks')
        pivots = column_pivots(space['coordinates'], n, other)
        other.require(pivots == space['pivots'], 'common receiver pivot set')
        for pivot in pivots:
            profiles[pivot].append(space['rank_max'])
    other.require(profiles == record['profiles'], 'complete per-coordinate charges')
    loads = [sum(p) for p in profiles]
    histogram = {str(k): v for k,v in sorted(Counter(loads).items())}
    other.require(histogram == record['load_histogram'], 'load histogram')
    if all(sum(p) < lost or p == [lost] for p in profiles):
        rule = 'coordinatewise'
        other.require(lost**99 > (lost-1)**100, 'strict coordinate power bound')
    else:
        other.require(reverse and record['entrance'] == 1 and terminal == 0 and lost == 8,
                      'only the declared joint exception')
        other.require(max(loads) == 8 and loads.count(8) == 1 and sum(x > 7 for x in loads) == 1, '7k+1 bound')
        other.require(2**100*8**99 > 15**100, 'all k>=2 power bound')
        rule = '7k+1 for k>=2; baseline certificate for k=1'
    other.require(record['rule'] == rule, 'codimension rule')


def evaluate():
    generator = load(HERE/'generate.py', 'generator')
    primary, other = generator.module('census'), generator.module('independent')
    baseline_checker = generator.module('verify')
    baseline_checker.run()
    for pin in json.loads((HERE/'SOURCE-PINS.json').read_text()):
        data = (HERE/pin['path']).read_bytes()
        other.require(sha256(data).hexdigest() == pin['sha256'], 'source SHA-256')
        other.require(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['git_blob'], 'source Git blob')
    certificate = primary.read(HERE/'CERTIFICATE.json.gz')
    other.require(json.loads(json.dumps(generator.produce())) == certificate, 'joint certificate replay')
    baseline = primary.read(generator.BASE/'CERTIFICATE.json.gz')
    word, _ = primary.source()
    dimensions = {int(c): f['dim'] for c, f in word['frames'].items()}
    original, states = {}, {}
    for reverse, orientation in enumerate(baseline['orientations']):
        initial, final, banks, raw_moves = other.replay(word, bool(reverse))
        moves = {key: abs(dimensions[a]-dimensions[b]) for key,(a,b) in raw_moves.items()}
        state = initial, final, banks, moves
        for group in orientation['groups']:
            key = orientation['direction'], group['entrance'], group['exit']
            original[key], states[key] = group, state
    given = {(r['direction'],r['entrance'],r['exit']): r for r in certificate['groups']}
    other.require(set(given) == set(original) and len(given) == len(certificate['groups']), 'all 18 group-orientations')
    for key, record in given.items():
        check_group(record, original[key], states[key], other)
    controls = []
    key = 'transpose', 1, 0
    group = given[key]

    def reject(label, changed, message):
        try:
            check_group(changed, original[key], states[key], other)
        except ValueError as error:
            other.require(str(error) == message, label+' failed at wrong gate: '+str(error))
            controls.append(label)
        else:
            raise ValueError('accepted mutation: '+label)

    changed = deepcopy(group);changed['lost_rank'] = 0
    reject('omit all target debits', changed, 'all productive targets charged')
    changed = deepcopy(group);changed['spaces'].pop()
    reject('omit a joint receiver', changed, 'all nonterminal receivers')
    changed = deepcopy(group);changed['spaces'][0]['coordinates'][0].append(409)
    reject('change receiver coordinates', changed, 'exact transformed receiver')
    changed = deepcopy(group);changed['spaces'][0]['pivots'].pop()
    reject('omit a common pivot', changed, 'common receiver pivot set')
    changed = deepcopy(group);changed['basis'][0]['key'] += 1
    reject('change terminal chronology', changed, 'complete chronological terminal flag')
    changed = deepcopy(group);changed['profiles'][350].pop()
    reject('omit a receiver charge', changed, 'complete per-coordinate charges')
    # Three distinct lines in F2^2 have a joint gain that no line has alone.
    lines = [{0}, {1}, {0, 1}]
    for line in lines:
        killed = sum(line == receiver for receiver in lines)
        other.require(killed == 1 and 1+2*killed == 3 and 4**99 > 3**100, 'single-line toy loss')
    # Put x=2^t. The joint difference is 3x+2-2x^2=(2-x)(2x+1)>0.
    other.require(3*2+2 == 2*4 and (2*2+1) > 0 and 2**99 < 2**100, 'joint concavity toy')
    toy_pivots = [column_pivots([line], 2, other) for line in lines]
    toy_loads = [1+sum(2 for pivots in toy_pivots if i in pivots) for i in range(2)]
    other.require(toy_loads == [3,5], 'joint toy escapes coordinate charge gate')
    controls.append('single-line exclusions do not imply a joint exclusion')
    return dict(status=certificate['status'], source_pins=len(json.loads((HERE/'SOURCE-PINS.json').read_text())),
        group_orientations=len(given), charged_coordinates=sum(len(r['profiles']) for r in given.values()),
        nonterminal_spaces=sum(len(r['spaces']) for r in given.values()),
        groups=[dict(direction=r['direction'], entrance=r['entrance'], exit=r['exit'], helpers=len(r['roles']),
                     lost_rank=r['lost_rank'], load_histogram=r['load_histogram'], rule=r['rule']) for r in given.values()],
        source_invoice=baseline['source_invoice'], controls=controls, kappa_interval=certificate['kappa_interval'])


def run():
    receipt = evaluate()
    if receipt != json.loads((HERE/'RESULT.json').read_text()):
        raise ValueError('summary receipt')
    print(receipt['status'], receipt['group_orientations'], receipt['charged_coordinates'], receipt['nonterminal_spaces'])


if __name__ == '__main__':
    run()
