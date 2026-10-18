#!/usr/bin/env python3
"""Fixed-schedule k8 helper endpoint audit; standard library, Python 3.12+.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
The span certificate is new code. Explicitly named retained auditors are
comparison targets, not claimed as independent implementations.
"""
import argparse
from collections import Counter
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz'
LOCAL = 'research/gauge44-slots/independent/audit_local.py'
OWNERS = 'research/t16-owner-audit-seed67/verify.py'
PACKAGE = 'research/complex-t16-rare-pattern-exchanges'
FULL = tuple(1 << i for i in reversed(range(9)))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(word):
    return json.dumps(word, sort_keys=True, separators=(',', ':')).encode()


def check_inputs(root=ROOT):
    pins = read(HERE / 'SOURCES.json')
    for pin in pins['files']:
        if pin['usage'] == 'input':
            need(digest((root / pin['path']).read_bytes()) == pin['sha256'],
                 'Source pin mismatch: ' + pin['path'])
    return pins


def basis(vectors):
    """Binary RREF of label subspaces, not complex scalar coefficients."""
    pivots = {}
    for vector in vectors:
        need(type(vector) is int and 0 <= vector < 512, 'Label outside F2^9')
        for bit in sorted(pivots, reverse=True):
            if vector & (1 << bit):
                vector ^= pivots[bit]
        if vector:
            bit = vector.bit_length() - 1
            for other in pivots:
                if pivots[other] & (1 << bit):
                    pivots[other] ^= vector
            pivots[bit] = vector
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def closure(vectors):
    """Separate explicit-set span, at most 512 labels."""
    points = {0}
    for vector in vectors:
        points |= {point ^ vector for point in tuple(points)}
    return points


def contained(left, right):
    return basis((*left, *right)) == basis(right)


def registers(gate):
    need(gate[0] in ('add', 'scale'), 'Unknown gate')
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def gaussian(n, k):
    numerator = denominator = 1
    for i in range(k):
        numerator *= 2**n - 2**i
        denominator *= 2**k - 2**i
    need(numerator % denominator == 0, 'Nonintegral Gaussian count')
    return numerator // denominator


def trace(word):
    """Necessary endpoint spans from actual touches, independent of end caps."""
    need((word['report']['v'], word['report']['h'], word['report']['R']) == (112, 9, 480),
         'Unexpected geometry')
    start = [(p,) for p in word['ports']] + [()] * 592
    for q, frame in word['start_extra'].items():
        start[int(q)] = basis(frame)
    current = list(start)
    last = [dict(section='entrance') for _ in current]

    def touch(gate, frame, section, index):
        frame = basis(frame)
        for q in registers(gate):
            need(contained(current[q], frame), 'Nonmonotone input word')
            current[q] = frame
            last[q] = dict(section=section, index=index)

    for section in ('A', 'B'):
        for index, gate in enumerate(word[section]):
            touch(gate, gate[-1], section, index)
    early = set()
    for index, frame in word['early_cleanup']:
        need(index not in early, 'Repeated early cleanup')
        early.add(index)
        touch(word['cleanup'][index], frame, 'early_cleanup', index)
    ordinary = {}
    for index, gate in enumerate(word['cleanup']):
        if index not in early:
            for q in registers(gate):
                ordinary.setdefault(q, index)
    forced = []
    for q in range(224, 704):
        end = basis(word['helper_final'].get(str(q), FULL))
        required = FULL if q in ordinary else current[q]
        need(required == end, 'Endpoint has slack: ' + str(q))
        need(contained(start[q], required), 'Entrance not in endpoint')
        need(closure(required) == closure(end) and len(closure(required)) == 2**len(required),
             'Set-span cross-check')
        forced.append(dict(register=q, start_basis=list(start[q]), end_basis=list(end),
                           forcing=dict(section='full_cleanup', index=ordinary[q])
                           if q in ordinary else last[q]))
    return forced


def replace_endpoint(word, item):
    """Different equal-rank cap, still containing the original entrance."""
    end, start = item['end_basis'], item['start_basis']
    extended = list(start)
    complements = []
    for vector in end:
        if vector not in closure(extended):
            extended.append(vector)
            complements.append(vector)
    need(complements and len(extended) == len(end), 'No endpoint complement')
    outside = next(vector for vector in (1 << i for i in range(9)) if vector not in closure(end))
    missing = complements[-1]
    replacement = basis([*start, *complements[:-1], outside])
    need(len(replacement) == len(end) and contained(start, replacement), 'Invalid fixture dimensions')
    need(missing in closure(end) and missing not in closure(replacement), 'Missing-label witness')
    mutant = dict(word, helper_final=dict(word['helper_final']))
    mutant['helper_final'][str(item['register'])] = list(replacement)
    return mutant, list(replacement), missing


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    target = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(target)
    return target


def local_trial(target, word, directory, rejected_register=None):
    path = directory / 'word.json.gz'
    path.write_bytes(gzip.compress(encode(word), mtime=0))
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            target.run(path, directory / 'local.json')
    except RuntimeError as error:
        need(rejected_register is not None, 'Positive local word rejected: ' + str(error))
        need(str(error).startswith('frame not monotone (' + str(rejected_register) + ','),
             'Unexpected local rejection: ' + str(error))
        need(output.getvalue().splitlines() == ['endpoint forward PASS', 'endpoint dual PASS'],
             'Mutant failed before exact scalar endpoint controls')
        return 'frame not monotone'
    need(rejected_register is None, 'Invalid endpoint accepted by retained local audit')
    report = read(directory / 'local.json')
    return {key: report[key] for key in ('status', 'checked_columns', 'local_profile', 'width_inventory')}


def verify():
    pins = check_inputs()
    word = read(ROOT / WORD)
    raw = gzip.decompress((ROOT / WORD).read_bytes())
    recipe_path = 'research/gauge44-slots/construction/slots/RECIPE-SLOTS-k8.json'
    recipe = read(ROOT / recipe_path)
    need(digest(raw) == recipe['expect_sha256'], 'Word not the selected k8 recipe output')
    need(encode(word) == raw, 'Diagnostic serialization differs from source word')
    spec = read(ROOT / PACKAGE / 'data/SPEC.json')
    selected_sources = read(ROOT / 'research/community-frontier1094-audit/SELECTED-SOURCE.json')
    need(digest((ROOT / recipe_path).read_bytes()) == selected_sources['files'][recipe_path],
         'Recipe is not selected-source-bound')
    forced = trace(word)
    low = [item for item in forced if len(item['end_basis']) < 9]
    need(len(low) == 78, 'Low-end inventory')
    target = module('retained_k8_local_audit', ROOT / LOCAL)
    owner = module('retained_t16_owner_audit', ROOT / OWNERS)
    widths = owner.word_widths(word)
    need(Counter(widths) == owner.as_profile(spec['providers']['gauge44']['inventory']), 'Selected widths')
    geometry = owner.geometry(read(ROOT / owner.TEMPLATE), read(ROOT / owner.PHASES))
    plan = read(ROOT / PACKAGE / 'data/PLAN.json')
    roles = read(ROOT / PACKAGE / 'data/OWNERS.json.gz')
    local_profile = owner.as_profile(word['report']['local_profile'])
    need(local_profile == owner.as_profile(spec['providers']['gauge44']['expected_profile']), 'Selected local profile')
    owned = owner.audit(geometry, widths, local_profile, roles, plan,
                        owner.as_profile(spec['expected']['idle_remainder_profile']), 16)
    need(owned['profile'] == owner.as_profile(plan['profile']) == owner.as_profile(read(ROOT / PACKAGE / 'PROFILE.json')),
         'Selected owner profile')
    cases = []
    with tempfile.TemporaryDirectory(prefix='k8-endpoint-audit-') as temporary:
        directory = Path(temporary)
        positive = local_trial(target, word, directory)
        print('PASS selected local word and 69120-role owner audit', flush=True)
        for item in low:
            mutant, replacement, missing = replace_endpoint(word, item)
            need(owner.word_widths(mutant) == widths, 'Rank-only owner inputs changed')
            need(digest(encode(mutant)) != recipe['expect_sha256'], 'Mutant retains immutable word pin')
            # Other owner.audit inputs are unchanged. Its computation is identical;
            # we do not claim 78 separate owner runs.
            rejection = local_trial(target, mutant, directory, item['register'])
            s, d = len(item['start_basis']), len(item['end_basis'])
            cases.append(dict(register=item['register'], replacement_basis=replacement,
                              omitted_required_label=missing, local_rejection=rejection,
                              scalar_endpoints_passed_both_orientations=True,
                              rank_only_owner_inputs_unchanged=True,
                              immutable_word_pin_rejects_mutant=True,
                              alternative_caps_containing_entrance=gaussian(9-s, d-s)-1))
    print('PASS 78 same-rank mutations rejected after both scalar endpoints pass', flush=True)
    return dict(status='PASS_K8_HELPER_ENDPOINT_BOUNDARY_AUDIT', base_commit=pins['base_commit'],
                word_payload_sha256=digest(raw),
                helper_endpoints=480, restricted_endpoints=78, full_cleanup_forced_endpoints=402,
                restricted_endpoint_dimensions=dict(sorted(Counter(len(i['end_basis']) for i in low).items())),
                single_end_same_rank_alternatives_excluded=sum(c['alternative_caps_containing_entrance'] for c in cases),
                positive_local=positive, retained_owner_audit=owned,
                owner_replays=1, exact_local_replays=79,
                forced_restricted_endpoints=low,
                full_cleanup_witnesses=[[i['register'], i['forcing']['index']] for i in forced if len(i['end_basis']) == 9],
                adversarial_cases=cases,
                scope='Fixed gates/order, entrances, gate frames and early/full cleanup. Minimal helper endpoint subspaces only; no changed-gate/frame resynthesis, hosted realization, cold replay or new kappa.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='Write a receipt instead of comparing the committed one')
    args = parser.parse_args()
    result = verify()
    encoded = json.dumps(result, indent=2) + '\n'
    if args.write:
        args.write.write_text(encoded)
    else:
        need(json.loads(encoded) == read(HERE / 'RESULT.json'), 'Receipt mismatch')
    print(result['status'], 'helpers=480 restricted=78 same_rank_alternatives=' +
          str(result['single_end_same_rank_alternatives_excluded']))


if __name__ == '__main__':
    main()
