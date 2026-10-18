"""Standalone exact replay of the complete fixed 73-word exclusion corpus."""
if not __debug__:
    raise SystemExit('Run without -O: the inherited Clifford model requires assertions.')

from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import boolean
import model
import polynomial
import screen
import valuation


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reject(action):
    try:
        action()
    except (ValueError, AssertionError, KeyError, IndexError):
        return
    raise ValueError('Deliberately false certificate accepted')


def verify_word(program, case):
    records, blocks = valuation.direct_records(program)
    symbolic, symbolic_blocks = valuation.symbolic_records(program)
    require(blocks == symbolic_blocks and valuation.canonical(records) == valuation.canonical(symbolic),
            'Independent dense and symbolic paths differ')
    counts = Counter(dense_paths=sum(len(r['paths']) for r in records))
    if case['kind'] == 'inherited_global_valuation':
        valuation.check(records, blocks, case['vector'])
        counts['inherited_global_valuation'] = 1
        return dict(counts)
    require(case['kind'] in ('endpoint_matching', 'combined'), 'Unknown proof kind')
    choices = set(__import__('itertools').product(*valuation.targets(records)))
    covered = set()
    for certificate in case['valuations']:
        frames = tuple(certificate['frames'])
        require(frames in choices and frames not in covered, 'Invalid valuation coverage')
        valuation.check(records, blocks, certificate['vector'], frames)
        covered.add(frames)
        counts['valuation_certificates'] += 1
    cnf, coefficients = boolean.formula(records, blocks, case['valuations'])
    require(case['steps'] and case['steps'][-1]['support']['status'] == 'support_obstruction',
            'Missing terminal Boolean refutation')
    for index, step in enumerate(case['steps']):
        answer = step['support']
        require(answer['status'] in ('support_feasible', 'support_obstruction'), 'Incomplete search result')
        counts['resolution_clauses'] += boolean.check(cnf, answer)
        if answer['status'] == 'support_obstruction':
            require(index == len(case['steps'])-1, 'Premature terminal proof')
            continue
        selection = boolean.selected_support(cnf, answer)
        require(selection == step['selection'], 'Invalid support selection')
        clause = polynomial.check_core(coefficients, selection, step['gauge'], step['core'], cnf)
        require(clause == step['blocking_clause'], 'Wrong algebraic blocking clause')
        cnf['clauses'].append(clause)
        counts['polynomial_identities'] += 1
    counts[case['kind']] = 1
    return dict(counts)


def positive_controls():
    identity = ('mix3', 1, 0, 0, 0, 1, 0, 0, 0, 1)
    words = [tuple(('paid', r, a) for r in range(3) for a in (1, 2, 4))+(identity,)]
    for axes in ((1, 2, 4), (3, 2, 4)):
        a = ('mix3', 1, 1, 0, 0, 1, 1, 1, 0, 1)
        b = ('mix3', 1, 0, 0, 0, 1, 0, 0, 0, -1)
        c = ('mix3', 2, 1, 0, 1, 1, 1, 0, 1, 1)
        word = [a]
        word.extend(('paid', r, x) for r, u in enumerate(((), axes[:1], axes[:2])) for x in u)
        word.extend((b, identity))
        word.extend(('paid', r, x) for r, u in enumerate((axes, axes[1:], axes[2:])) for x in u)
        word.append(c)
        words.append(tuple(word))
    for word in words:
        ring = model.Engine()
        rows = model.execute(ring, word)
        frames = model.endpoint_frames(ring, rows)
        require(frames is not None, 'Nine-call endpoint failed')
        records, blocks = valuation.direct_records(word)
        symbolic, n = valuation.symbolic_records(word)
        require(n == blocks and valuation.canonical(symbolic) == valuation.canonical(records), 'Positive dense mismatch')
        cnf, _ = boolean.formula(records, blocks, [])
        matrices = [gate[1:] for gate in word if gate[0] == 'mix3']
        entries = [bool(x) for matrix in matrices for x in matrix]
        augment = [[sum(v for key, v in rows[i].items() if key & 3 == j) for j in range(3)] for i in range(3)]
        answer = []
        for label in cnf['labels'][1:]:
            kind = label[0]
            if kind == 'entry':
                _, k, i, j = label
                value = bool(matrices[k][3*i+j])
            elif kind == 'matching':
                _, k, perm = label
                value = all(matrices[k][3*i+j] for i, j in enumerate(perm))
            elif kind == 'frame':
                value = label[2] == frames[label[1]]
            elif kind == 'term':
                value = all(entries[e] for e in range(9*blocks) if label[1] & (1 << e))
            elif kind == 'endpoint_matching':
                value = all(augment[i][j] for i, j in enumerate(label[1]))
            else:
                raise ValueError('Unexpected Boolean variable')
            answer.append(int(bool(value)))
        boolean.check(cnf, {'status': 'support_feasible', 'model': answer})
    return len(words)


def controls(data, words):
    counts = {'nine_call_endpoints': positive_controls()}
    matching = next(c for c in data['cases'] if c['kind'] == 'endpoint_matching')
    records, blocks = valuation.direct_records(words[matching['id']])
    cnf, _ = boolean.formula(records, blocks, [])
    forged = deepcopy(matching['steps'][0]['support'])
    forged['resolution'][-1]['clause'] = [1]
    reject(lambda: boolean.check(cnf, forged))
    counts['corrupt_resolution_rejected'] = 1
    combined = next(c for c in data['cases'] if any('gauge' in s for s in c.get('steps', [])))
    records, blocks = valuation.direct_records(words[combined['id']])
    cnf, coefs = boolean.formula(records, blocks, combined['valuations'])
    step = combined['steps'][0]
    altered = deepcopy(step['gauge'])
    altered['answer']['certificate'][0][2] = str(Fraction(altered['answer']['certificate'][0][2])+1)
    reject(lambda: polynomial.check_core(coefs, step['selection'], altered, step['core'], cnf))
    counts['corrupt_polynomial_identity_rejected'] = 1
    core = deepcopy(step['core'])
    core['nonzero_entries'] = []
    reject(lambda: polynomial.check_core(coefs, step['selection'], step['gauge'], core, cnf))
    counts['missing_gauge_premise_rejected'] = 1
    shortened = deepcopy(combined)
    shortened['steps'].pop()
    reject(lambda: verify_word(words[combined['id']], shortened))
    counts['missing_final_refutation_rejected'] = 1
    global_case = next(c for c in data['cases'] if c['kind'] == 'inherited_global_valuation')
    records, blocks = valuation.direct_records(words[global_case['id']])
    reject(lambda: valuation.check(records, blocks, [0]*len(global_case['vector'])))
    counts['zero_valuation_gap_rejected'] = 1
    removed = deepcopy(data)
    removed['cases'].pop()
    reject(lambda: replay(removed, run_controls=False))
    counts['missing_case_rejected'] = 1
    return counts


def replay(data=None, run_controls=True):
    source = json.loads(gzip.decompress((ROOT/'words.json.gz').read_bytes()))['cases']
    require(len(source) == len({c['id'] for c in source}) == 73, 'Wrong source corpus')
    words, inherited = {}, 0
    for case in source:
        program = model.decode(case['program'])
        certificate = screen.certificate(program)
        require(certificate['paid_calls'] == 8, 'Wrong call count')
        if certificate['status'] == 'excluded':
            inherited += 1
        else:
            words[case['id']] = program
    require(inherited == 64, 'Inherited homogeneity coverage changed')
    if data is None:
        data = json.loads(gzip.decompress((ROOT/'proofs.json.gz').read_bytes()))
    require(len(data['cases']) == len({c['id'] for c in data['cases']}) and
            {c['id'] for c in data['cases']} == set(words), 'Incomplete remaining-word coverage')
    reports = {case['id']: verify_word(words[case['id']], case) for case in data['cases']}
    totals = Counter()
    for report in reports.values():
        totals.update(report)
    return {'status': 'PASS_ENDPOINT_MATCHING_OBSTRUCTIONS', 'source_words': 73,
            'inherited_homogeneous_exclusions': inherited, 'new_whole_word_exclusions': 8,
            'total_excluded': inherited+len(reports), 'totals': dict(totals), 'cases': reports,
            'controls': controls(data, words) if run_controls else {}}


def check_manifest():
    manifest = json.loads((ROOT/'MANIFEST.json').read_bytes())
    actual = {p.name for p in ROOT.iterdir() if p.is_file() and p.name != 'MANIFEST.json'}
    require(actual == set(manifest['files']) | set(manifest['payloads']), 'Unexpected package inventory')
    for path in ROOT.iterdir():
        require(not path.is_symlink(), 'Symlink in package')
    for name, digest in manifest['files'].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == digest, 'Source hash mismatch: '+name)
    for name, digest in manifest['payloads'].items():
        require(sha256(gzip.decompress((ROOT/name).read_bytes())).hexdigest() == digest, 'Payload hash mismatch: '+name)
    origins = json.loads((ROOT/'ORIGINS.json').read_bytes())
    for name, digest in origins['copied_files_sha256'].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == digest, 'Copied source mismatch: '+name)
    require(manifest['payloads']['words.json.gz'] == origins['words_payload_sha256'], 'Word origin mismatch')


if __name__ == '__main__':
    check_manifest()
    report = replay()
    require(report == json.loads((ROOT/'EXPECTED.json').read_bytes()), 'Expected receipt mismatch')
    print(json.dumps(report, sort_keys=True))
