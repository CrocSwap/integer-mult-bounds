"""Bounded interacting helper shears. Apache-2.0; substantial OpenAI Codex assistance."""
import argparse
import ast
import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f'
PREDECESSOR = 'research/r439-post-helper-shear-seed03/'
ORIGINAL = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
OWNER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPECTED = 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
FORMULA = ('research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/'
           'vendor/e8-r715-eleven-stage-whole/code/global_k.py')
INPUTS = (PREDECESSOR + 'candidate.json.gz', PREDECESSOR + 'search.py',
          PREDECESSOR + 'independent.py', PREDECESSOR + 'README.md',
          PREDECESSOR + 'CERTIFICATE.json', ORIGINAL, OWNER, EXPECTED, FORMULA)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def bad(value):
        raise ValueError('nonfinite JSON')
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data,
                      object_pairs_hook=pairs, parse_constant=bad)


def same(left, right, message):
    need(canonical(left) == canonical(right), message)


def guards(price):
    need(int(price['local_bound']) < 1 << 104, 'local precision')
    need(int(price['nine_stage_bound']) < 1 << 192, 'nine-stage precision')


def pins_check(pins):
    need(pins['base_commit'] == BASE, 'wrong base')
    need(set(pins['files']) == set(INPUTS), 'source inventory')
    for name in INPUTS:
        raw = (ROOT / name).read_bytes()
        entry = pins['files'][name]
        need(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'source hash: ' + name)
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob).hexdigest() == entry['git_blob'], 'source blob: ' + name)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def columns(parent):
    need(len(parent['D']) == 1167, 'pinned predecessor D shape')
    core = parent['D'][528:639]
    need([g[1] for g in core] == list(range(111, 222)), 'middle row order')
    result = [0] * 439
    for row, (frame, _, donors) in enumerate(core):
        need(frame == 0 and len(set(donors)) == len(donors), 'middle frame/duplicates')
        for donor in donors:
            need(222 <= donor < 661, 'middle donor')
            result[donor - 222] ^= 1 << row
    return result


def construct(parent, cols, edges):
    out = copy.deepcopy(parent)
    gates = [[0, 222 + d, [222 + s]] for d, s in edges]
    core = [[0, 111 + row, [222 + j for j, col in enumerate(cols) if col >> row & 1]]
            for row in range(111)]
    out['D'] = out['D'][:528] + gates + core + list(reversed(gates)) + out['D'][639:]
    return out


def independent_make(parent, edges):
    # Literal row edits give a separate check of the packed-column construction.
    out = copy.deepcopy(parent)
    core = out['D'][528:639]
    for d, s in edges:
        for _, _, donors in core:
            if 222 + d in donors:
                if 222 + s in donors:
                    donors.remove(222 + s)
                else:
                    donors.append(222 + s)
            donors.sort()
    gates = [[0, 222 + d, [222 + s]] for d, s in edges]
    out['D'] = out['D'][:528] + gates + core + copy.deepcopy(gates[::-1]) + out['D'][639:]
    return out


def nominees(cols, round_index):
    hist = Counter()
    positive = []
    sets = [{i for i in range(111) if col >> i & 1} for col in cols]
    for d in range(439):
        for s in range(439):
            if d == s:
                continue
            gain = cols[s].bit_count() - (cols[s] ^ cols[d]).bit_count() - 2
            independent_gain = len(sets[s]) - len(sets[s].symmetric_difference(sets[d])) - 2
            need(gain == independent_gain, 'support census disagreement')
            hist[str(gain)] += 1
            if gain > 0:
                key = f'15:{round_index}:{d}:{s}'
                tie = hashlib.sha256(key.encode('ascii')).hexdigest()
                positive.append((-gain, tie, d, s))
    positive.sort()
    return hist, positive


def run(verbose=False):
    pins = read(HERE / 'SOURCES.json')
    pins_check(pins)
    S = load('seed03_search', ROOT / (PREDECESSOR + 'search.py'))
    I = load('seed03_independent', ROOT / (PREDECESSOR + 'independent.py'))
    parent = read(ROOT / INPUTS[0])
    original = read(ROOT / ORIGINAL)
    source_receipt = read(ROOT / (PREDECESSOR + 'CERTIFICATE.json'))
    same(S.bill(parent), source_receipt['candidate_bill'], 'predecessor invoice')
    tree = ast.parse((ROOT / FORMULA).read_text())
    formulas = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'prefix' for t in node.targets)]
    formula = ast.parse('(1<<nb)*cf**(K+1)*cb**K', mode='eval').body
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(formula), 'prefix formula')
    bridge = ast.parse('nb==6*(K-1)', mode='eval').body
    need(any(isinstance(node, ast.Compare) and ast.dump(node) == ast.dump(bridge)
             for node in ast.walk(tree)), 'bridge exponent')
    need(read(ROOT / EXPECTED)['nine']['bit']['charged_prefix_bits'] == 192, 'prefix allocation')
    need(I.d_rows(parent) == I.d_rows(original), 'parent semantic D')
    cols = columns(parent)
    edges = []
    rounds = []
    candidate = parent
    for round_index in range(15):
        hist, positive = nominees(cols, round_index)
        trials = []
        winner = None
        old_price = S.bill(candidate)
        for neg, tie, d, s in positive[:32]:
            changed = list(cols)
            changed[s] ^= changed[d]
            word = construct(parent, changed, edges + [[d, s]])
            price = S.bill(word)
            independent_word = independent_make(parent, edges + [[d, s]])
            same(word, independent_word, 'trial literal construction')
            f, adds = I.check_full(independent_word)
            b, reverse_adds = I.check_full(independent_word, True)
            local, nine = (1 << 6) * f**3 * b**2, (1 << 18) * f**5 * b**4
            same(price, {'ADDs': adds, 'D_ADDs': sum(len(g[2]) for g in word['D']),
                         'F': f, 'B': b, 'local_bound': str(local), 'nine_stage_bound': str(nine),
                         'admitted': local < 1 << 104 and nine < 1 << 192}, 'trial full invoice')
            need(adds == reverse_adds, 'trial reverse count')
            need(old_price['ADDs'] - price['ADDs'] == -neg, 'complete restoration charge')
            trials.append({'destination': d, 'source': s, 'saving': -neg,
                           'tie': tie, 'bill': price})
            if winner is None and price['admitted']:
                winner = len(trials) - 1
        rounds.append({'round': round_index, 'pairs': 439 * 438,
                       'positive_pairs': len(positive), 'gain_histogram': dict(hist),
                       'trials': trials, 'winner': winner})
        if winner is None:
            break
        choice = trials[winner]
        d, s = choice['destination'], choice['source']
        cols[s] ^= cols[d]
        edges.append([d, s])
        candidate = construct(parent, cols, edges)
        same(candidate, independent_make(parent, edges), 'literal construction')
        need(I.d_rows(candidate) == I.d_rows(original), 'all dirty D columns')
        f, adds = I.check_full(candidate)
        b, reverse_adds = I.check_full(candidate, True)
        need((f, b, adds, reverse_adds) ==
             (choice['bill']['F'], choice['bill']['B'], choice['bill']['ADDs'], adds),
             'independent full forward/reverse prefix price')
        if verbose:
            print(f'round {round_index}: {d}<-{s}, saved {choice["saving"]}, '
                  f'ADDs {adds}, F {f}, B {b}', flush=True)
    owner = load('bit_geometry', ROOT / OWNER)
    W, labels, full, H, C, info = owner.check(candidate)
    need(not H['H2_D_frame0_targets_from_helpers'] and not C['K_equals_D'], 'semantic D scope')
    need(all(v for k, v in H.items() if not k.startswith('H2')) and
         all(v for k, v in C.items() if k != 'K_equals_D'), 'remaining interface')
    profile, paths = I.paid_profile(candidate, W.fdim)
    old_profile, old_paths = I.paid_profile(parent, W.fdim)
    same(profile, old_profile, 'paid ranks')
    same(paths, old_paths, 'register frame paths')
    same(profile, read(ROOT / EXPECTED)['word']['local_histogram'], 'selected paid profile')
    same({k: v for k, v in candidate.items() if k != 'D'},
         {k: v for k, v in parent.items() if k != 'D'}, 'non-D content')
    need(sum(int(k) * v for k, v in profile.items()) == 5129, 'rank mass')
    guards(S.bill(candidate))
    controls = []
    def reject(name, action):
        try:
            action()
        except ValueError:
            controls.append(name)
            return
        raise ValueError('negative control accepted: ' + name)
    target = I.d_rows(original)
    def boundary(word):
        need(I.d_rows(word) == target, 'dirty boundary')
    need(edges, 'no admitted extension')
    n = len(edges)
    for name, index in [('preparation', 528), ('restoration', 528 + n + 111)]:
        bad = copy.deepcopy(candidate)
        bad['D'].pop(index)
        reject('missing ' + name, lambda: boundary(bad))
    bad = construct(parent, columns(parent), edges)
    reject('missing middle correction', lambda: boundary(bad))
    bad = copy.deepcopy(candidate)
    d, s = edges[0]
    bad['D'][528] = [0, 222 + s, [222 + d]]
    reject('wrong preparation direction', lambda: boundary(bad))
    bad = copy.deepcopy(candidate)
    bad['D'][528 + n + 111:528 + 2 * n + 111] = bad['D'][528:528 + n]
    boundary(bad)
    need(all(d != t and s != e for d, s in edges for e, t in edges), 'commuting accepted edges')
    toy_edges = [[0, 1], [1, 2]]
    toy = independent_make(parent, toy_edges)
    boundary(toy)
    toy['D'][641:643] = copy.deepcopy(toy['D'][528:530])
    reject('noncommuting forward-order restoration', lambda: boundary(toy))
    reject('unpaid restore', lambda: need(S.bill(candidate)['ADDs'] ==
           S.bill(parent)['ADDs'] - sum(r['trials'][r['winner']]['saving']
           for r in rounds if r['winner'] is not None) - n, 'unpaid restoration'))
    missing = copy.deepcopy(pins)
    del missing['files'][INPUTS[0]]
    reject('missing source pin', lambda: pins_check(missing))
    reject('Boolean certificate integer', lambda: same(1, True, 'typed receipt'))
    equality = copy.deepcopy(S.bill(candidate))
    equality['nine_stage_bound'] = str(1 << 192)
    reject('strict192 equality', lambda: guards(equality))
    rejected = next(t for t in rounds[-1]['trials'] if not t['bill']['admitted'])
    reject('positive saving outside precision', lambda: guards(rejected['bill']))
    neutral = copy.deepcopy(candidate)
    neutral['D'][528:528] = [[0, 222, [223]], [0, 222, [223]]]
    boundary(neutral)
    need(S.bill(neutral)['ADDs'] == S.bill(candidate)['ADDs'] + 2, 'neutral pair charge')
    coverage = []
    for row in rounds:
        coverage.append({k: v for k, v in row.items() if k != 'trials'})
        coverage[-1]['trials'] = [[t['destination'], t['source'], t['saving'], t['bill']['F'],
                                  t['bill']['B'], t['bill']['ADDs'], t['bill']['admitted']]
                                 for t in row['trials']]
    result = {'format': 'r439-helper-descent/1', 'status': 'PASS_R439_HELPER_DESCENT',
              'base_commit': BASE, 'seed': 15, 'source_pins': pins,
              'domain': 'at most15 rounds; all439*438 ordered pairs each; first32 positive nominees priced',
              'stopping_reason': 'round cap' if len(edges) == 15 else 'no admitted nominee in prefix',
              'trial_columns': ['destination', 'source', 'saving', 'F', 'B', 'ADDs', 'admitted'],
              'edges': edges, 'rounds': coverage, 'parent_bill': S.bill(parent),
              'candidate_bill': S.bill(candidate), 'dirty_columns': 661,
              'paid_profile': profile, 'paid_rank_mass': 5129,
              'interface_hypotheses': H, 'interface_conclusions': C,
              'controls_rejected': controls, 'neutral_pair_extra_ADDs': 2,
              'accepted_shears_commute': True,
              'candidate_sha256': hashlib.sha256(canonical(candidate).encode()).hexdigest(),
              'no_new_kappa': True}
    return result, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--show', action='store_true', help='print the reproducible certificate')
    args = parser.parse_args()
    result, _ = run(verbose=not args.show)
    if args.show:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        same(result, read(HERE / 'CERTIFICATE.json'), 'complete saved certificate')
        print('PASS_R439_HELPER_DESCENT ADDs=' + str(result['parent_bill']['ADDs']) + '->' +
              str(result['candidate_bill']['ADDs']) + ' rounds=' + str(len(result['edges'])) +
              ' columns=661 no_new_kappa')


if __name__ == '__main__':
    main()
