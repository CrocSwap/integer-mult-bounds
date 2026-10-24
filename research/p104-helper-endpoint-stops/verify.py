"""Check every P104 helper endpoint stop and its unchanged quotient information.

Ali Romman, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = 'research/p104-native-channel/inputs/'
PREVIOUS = ROOT/'research/p104-live-helper-reads'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def authenticate():
    pins = json.loads((HERE/'SOURCES.json').read_text())['files']
    for row in pins:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source bytes: '+row['path'])

def span(basis):
    result = {0}
    for v in basis:
        result |= {q ^ v for q in tuple(result)}
    return frozenset(result)

def make_roots(fixture):
    rows = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0]*8
            row[i], row[j] = 2, 2*sign
            rows.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if sum(x == -1 for x in signs) % 2 == 0:
            rows.add((1, *signs))
    removed = fixture['section4_explicit_P104']
    rows -= {tuple(v) for v in removed['F0']+removed['C']}
    roots = sorted(rows)
    need(len(roots) == 104, 'root count')
    need([[sum(v[i]*v[j] for v in roots) for j in range(8)] for i in range(8)] ==
         [[104*int(i == j) for j in range(8)] for i in range(8)], 'tight root frame')
    return roots

def coordinates(row, roots):
    source = [F(row.get(f'X{s}', 0), 4) for s in range(104)]
    alpha = [sum(source[s]*roots[s][j] for s in range(104))/104 for j in range(8)]
    need(all(source[s] == sum(alpha[j]*roots[s][j] for j in range(8)) for s in range(104)), 'outside root code')
    return list(map(str, alpha))

def replay(word, roots, replacements=None):
    """Use sparse integer rows at scale four for all 280 logical inputs."""
    frames = {k: span(v) for k, v in word['initial_frames'].items()}
    rows = {k: {k: 4} for k in frames}
    targets = [span(word['final_frames'][f'Y{t}']) for t in range(104)]
    snapshots = []
    profile = Counter()
    program = []
    for i, event in enumerate(word['program']):
        program.extend(replacements.get(i, [event]) if replacements else [event])
    for index, event in enumerate(program):
        op = event[0]
        if op == 'add':
            _, dst, src, scalar, chart = event
            need(frames[dst] == frames[src] == span(chart), 'ADD frame')
            a = F(scalar)
            for key, value in tuple(rows[src].items()):
                numerator = a.numerator*value
                need(numerator % a.denominator == 0, 'quarter-grid exactness')
                updated = rows[dst].get(key, 0)+numerator//a.denominator
                if updated:
                    rows[dst][key] = updated
                else:
                    rows[dst].pop(key, None)
        elif op == 'transport':
            _, role, before, after, rank = event
            a, b = span(before), span(after)
            need(frames[role] == a and (a < b or b < a), 'transport frame')
            need(type(rank) is int and rank == abs(len(b).bit_length()-len(a).bit_length()), 'transport rank')
            profile[rank] += 1
            if role[0] in 'GQD':
                need(a < b, 'helper monotonicity')
                snapshots.append((index, role, a, b, dict(rows[role])))
            frames[role] = b
        elif op == 'zero':
            need(event[1] not in rows, 'private birth')
            rows[event[1]] = {}
            frames[event[1]] = span(event[2])
        elif op == 'copy':
            _, dst, src, chart = event
            need(not rows[dst] and frames[dst] == frames[src] == span(chart), 'private copy')
            rows[dst] = dict(rows[src])
        elif op == 'erase':
            need(frames[event[1]] == span(event[2]), 'private erase')
            del rows[event[1]], frames[event[1]]
        else:
            raise ValueError('unknown opcode')
    need(frames == {k: span(v) for k, v in word['final_frames'].items()}, 'final frames')
    for role, row in rows.items():
        expected = {role: 4}
        if role.startswith('Y'):
            t = int(role[1:])
            for s in range(104):
                dot = sum(a*b for a, b in zip(roots[t], roots[s]))
                need(dot % 2 == 0, 'integer target coefficient')
                if dot:
                    expected[f'X{s}'] = dot//2
        need(row == expected, 'complete endpoint: '+role)
    return snapshots, targets, profile, sha256(canonical(rows).encode()).hexdigest()

def reject(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('negative control accepted')

def run():
    authenticate()
    word = json.loads((ROOT/(PREFIX+'LOWRANK-WITNESS.json')).read_text())
    fixture = json.loads((ROOT/(PREFIX+'P104-FIXTURE.json')).read_text())
    roots = make_roots(fixture)
    snapshots, targets, profile, endpoint = replay(word, roots)
    contacts = []
    for event, role, before, after, row in snapshots:
        for t, h in enumerate(targets):
            if before < h < after:
                lower = len(before).bit_length()-1
                contacts.append(dict(event=event, role=role, target=t, lower_dimension=lower,
                    before=word['program'][event][2], endpoint=word['final_frames'][f'Y{t}'],
                    code_coordinates=coordinates(row, roots),
                    full_input_row={k: str(F(v, 4)) for k, v in sorted(row.items())},
                    removed_rank=9-lower, added_ranks=[8-lower, 1]))
    # Independent enumeration uses annihilating normals, not set containment.
    normals = []
    for h in targets:
        candidates = [n for n in range(1, 512) if all((n&v).bit_count() % 2 == 0 for v in h)]
        need(len(candidates) == 1, 'target hyperplane normal')
        normals.append(candidates[0])
    second = set()
    for index, event in enumerate(word['program']):
        if event[0] != 'transport' or event[1][0] not in 'GQD':
            continue
        _, role, before, after, rank = event
        if len(span(after)) != 512 or len(span(before)) >= 256:
            continue
        for t, normal in enumerate(normals):
            if all((normal&v).bit_count() % 2 == 0 for v in before):
                second.add((index, role, t))
    need(second == {(c['event'], c['role'], c['target']) for c in contacts}, 'complete contact census')
    need(len(contacts) == 52 and len({c['event'] for c in contacts}) == 32, 'frozen contact count')
    # Check all 52 actual split words, not only the original endpoint.
    for c in contacts:
        old = word['program'][c['event']]
        replacements = {c['event']: [['transport', c['role'], old[2], c['endpoint'], c['added_ranks'][0]],
                                    ['transport', c['role'], c['endpoint'], old[3], 1]]}
        _, _, changed, digest = replay(word, roots, replacements)
        expected = profile.copy()
        expected[c['removed_rank']] -= 1
        expected.update(c['added_ranks'])
        need(changed == expected and digest == endpoint, 'split word changes public endpoint or bill')
    # Replay the exact inherited theorem premises with its retained checker.
    old = runpy.run_path(str(PREVIOUS/'verify.py'))
    retained = json.loads((PREVIOUS/'RESULT.json').read_text())
    old_summary, paths, labels = old['trace'](word, roots)
    need(old_summary == retained['trace'] and old['geometry'](paths, labels, roots) == retained['targets'],
         'inherited quotient/arrival premises')
    c = contacts[0]
    row = {k: 4*F(v) for k, v in c['full_input_row'].items()}
    mutated = dict(row)
    mutated['X0'] = mutated.get('X0', 0)+4
    reject(lambda: coordinates(mutated, roots))
    # The earlier unfinished G25 row is outside K; it is a real scope boundary.
    outside = retained['trace']['outside_code_example']
    reject(lambda: coordinates({k: 4*F(v) for k, v in outside['full_input_row'].items()}, roots))
    wrong = json.loads(json.dumps(word))
    wrong['program'][c['event']][4] += 1
    reject(lambda: replay(wrong, roots))
    wrong = json.loads(json.dumps(word))
    last_add = max(i for i, e in enumerate(wrong['program']) if e[0] == 'add')
    wrong['program'][last_add][3] = '0'
    reject(lambda: replay(wrong, roots))
    reject(lambda: need(second == {(x['event'], x['role'], x['target']) for x in contacts[1:]}, 'omitted contact'))
    need(any(v.startswith('D') for v in row) and any(v.startswith('Q') for v in row), 'independent dirt retained')
    authenticate()
    return dict(status='PASS_P104_HELPER_ENDPOINT_STOPS', contacts=contacts,
                helper_transports=len(snapshots), endpoint_contacts=len(contacts),
                source_events=len(word['program']), targets=len({c['target'] for c in contacts}),
                split_word_replays=len(contacts), endpoint_sha256=endpoint,
                cases_by_lower_dimension=dict(sorted(Counter(str(c['lower_dimension']) for c in contacts).items())),
                inherited_state_certificates=old_summary['state_certificates'], inherited_target_certificates=len(retained['targets']),
                helper_lifetime_floor=208,
                controls=['outside_code_added_source', 'actual_earlier_outside_code_row', 'wrong_transport_rank',
                          'missing_dirty_cleanup', 'omitted_contact', 'independent_D_and_Q_dirt_retained'])

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
