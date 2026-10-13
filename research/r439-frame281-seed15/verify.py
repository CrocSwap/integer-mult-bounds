"""Source-bound finite frame281 circuit verification; no new kappa.

Prepared for woklerx with substantial OpenAI Codex assistance, Apache-2.0.
Reuses credited, pinned PR925 framing/record checks and PR952 positive bounds.
The new local independent implementation does not import discovery code.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
PR952 = 'research/r439-six-wire-boolean/candidate.json.gz'
AUDITOR = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
REQUIRED_INPUTS = {
    WORD, PR952, AUDITOR, EXPORTER,
    'research/r439-six-wire-boolean/verify.py',
    'research/r439-six-wire-boolean/common.py',
    'research/r439-six-wire-boolean/SOURCES.json',
    'research/r439-six-wire-boolean/CERTIFICATE.json',
    'research/r439-six-wire-boolean/NOTICE.md',
    'research/r439-frame267-seed01/verify.py',
    'research/r439-frame267-seed01/WITNESS.json',
    'research/r439-frame267-seed01/search.py',
    'research/e8-bit-carrier-skeleton/code/bit/regression/stage_cohort.py',
    'research/e8-bit-carrier-skeleton/code/bit/checkers/columns_k.cpp',
    'research/e8-bit-carrier-skeleton/code/bit/checkers/legality_h.cpp',
    'research/e8-bit-carrier-skeleton/code/bit/checkers/json.hpp',
    'research/e8-bit-carrier-skeleton/portable-include/bits/stdc++.h',
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py',
    'docs/research/community-batch952-review.md',
}


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path):
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    def unique(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('non-finite JSON constant: ' + value)

    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def source_pins():
    pins = load(HERE / 'SOURCES.json')
    need(set(pins['files']) == REQUIRED_INPUTS, 'source inventory mismatch')
    need(pins['base_commit'] == 'bbc600db2fc15007b7c914f4f2b2ed55fa909c87', 'base pin mismatch')
    for name, expected in pins['files'].items():
        raw = (ROOT / name).read_bytes()
        if not name.endswith('.gz'):
            raw = raw.replace(b'\r\n', b'\n')
        need(hashlib.sha256(raw).hexdigest() == expected, 'source pin mismatch: ' + name)
    return pins


def extract(word):
    indices = [i for i, g in enumerate(word['A']) if g[0] == 281]
    need(indices and indices == list(range(indices[0], indices[-1] + 1)), 'frame281 not contiguous')
    gates = word['A'][indices[0]:indices[-1] + 1]
    need(all(len(s) == 1 for _, _, s in gates), 'non-elementary frame281 gate')
    wires = sorted({r for _, d, ss in gates for r in [d] + ss})
    need(len(wires) == 6, 'frame281 wire count')
    ops = [[wires.index(d), wires.index(ss[0])] for _, d, ss in gates]
    return indices[0], indices[-1] + 1, wires, ops


def local_check(original, replacement, checks):
    need(checks.matrix(original) == checks.matrix(replacement), 'local Boolean map changed')
    need(checks.matrix(original, True) == checks.matrix(replacement, True),
         'fixed integer transfer changed')
    return {direction: {'original': checks.matrix(a, True),
                        'replacement': checks.matrix(b, True)}
            for direction, a, b in (('forward', original, replacement),
                                    ('reverse', original[::-1], replacement[::-1]))}


def splice(base, witness, checks):
    start, stop, wires, original = extract(base)
    need((start, stop) == (825, 838), 'PR952 frame281 slice changed')
    need(witness['phase'] == 'A' and witness['frame'] == 281 and witness['quad'] == 15,
         'wrong witness object')
    need(witness['assignment_seed'] == 15, 'assignment seed mismatch')
    need((witness['start'], witness['stop']) == (start, stop), 'witness slice mismatch')
    need(witness['registers'] == wires and witness['original'] == original, 'witness input mismatch')
    need(witness['source_pr'] == 952, 'wrong source PR')
    local_check(original, witness['replacement'], checks)
    candidate = copy.deepcopy(base)
    candidate['A'][start:stop] = [[281, wires[d], [wires[s]]] for d, s in witness['replacement']]
    candidate['C'] = checks.cleanup(candidate)
    need(checks.paths(base) == checks.paths(candidate), 'register frame paths changed')
    return candidate


def run(output, write):
    pins = source_pins()
    discovery = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'search.py')],
                               capture_output=True, text=True)
    need(discovery.returncode == 0, 'discovery replay failed: ' + discovery.stderr)
    selected, base = load(ROOT / WORD), load(ROOT / PR952)
    witness = load(HERE / 'WITNESS.json')
    checks = module('credited_pr925_checks', ROOT / 'research/r439-frame267-seed01/verify.py')
    bounds = module('credited_pr952_checks', ROOT / 'research/r439-six-wire-boolean/verify.py')
    independent = module('independent_frame281', HERE / 'independent.py')
    # Discovery is run separately; this path never imports search.py.
    candidate = splice(base, witness, checks)
    old_ops = witness['original']
    new_ops = witness['replacement']
    old_start, old_stop, wires, _ = extract(base)
    selected_start, selected_stop, selected_wires, selected_ops = extract(selected)
    need(wires == selected_wires, 'selected frame281 wires changed')
    need(checks.matrix(old_ops) == checks.matrix(selected_ops), 'selected comparison map differs')
    independent_result = independent.verify(witness)
    positive = local_check(old_ops, new_ops, checks)
    scalar = {name: bounds.word_checks(word) for name, word in
              (('original', base), ('replacement', candidate), ('selected589', selected))}
    need(scalar['selected589']['ADDs'] == 24305 and scalar['original']['ADDs'] == 23673,
         'predecessor ADD bills')
    saved = 2 * (len(old_ops) - len(new_ops))
    need(scalar['original']['ADDs'] - scalar['replacement']['ADDs'] == saved,
         'complete forward/cleanup ADD saving')
    # Local reverse domination is sufficient, not necessary. word_checks prices
    # both whole-word orientations and enforces 104/192-bit inherited caps.
    prefix_source = bounds.prefix_binding(ROOT)
    print('Local matrix, all-word dirty columns and positive bounds passed', flush=True)

    checker = module('pinned_interface_checker', ROOT / AUDITOR)
    geometry, labels, original_full, h, conclusions, _ = checker.check(base)
    need(all(h.values()) and all(conclusions.values()), 'original H1-H5 failed')
    candidate_full = checks.audit(candidate, checker, geometry)
    need(candidate_full['columns'] == 661, 'all-column coverage')
    evidence = {}
    for name, word in (('original', base), ('replacement', candidate)):
        path = output / (name + '.json.gz')
        path.write_bytes(gzip.compress(canonical(word), mtime=0))
        records = output / name / 'records'
        completed = subprocess.run([sys.executable, '-I', '-B', str(ROOT / EXPORTER),
                                    str(path), str(records)], capture_output=True, text=True)
        need(completed.returncode == 0, 'export failed: ' + completed.stderr)
        evidence[name] = checks.records_check(records, word)
    for key in ('moves', 'copies', 'erasures', 'paid_histogram', 'rank_mass'):
        need(evidence['original'][key] == evidence['replacement'][key], 'paid cost changed: ' + key)
    need(evidence['replacement']['rank_mass'] == 5129 and evidence['replacement']['copies'] == 9,
         'rank mass or copy count')
    need(evidence['original']['adds'] - evidence['replacement']['adds'] == saved, 'exported ADD saving')

    controls = []
    exceptions = (ValueError, checks.Reject, checker.Reject)

    def reject(name, action):
        try:
            action()
        except exceptions:
            controls.append(name)
            return
        raise ValueError('negative control accepted: ' + name)

    reject('drop circuit gate', lambda: local_check(old_ops, new_ops[1:], checks))
    bad_ops = copy.deepcopy(new_ops)
    bad_ops[0].reverse()
    reject('reverse circuit operands', lambda: local_check(old_ops, bad_ops, checks))
    inflated = new_ops + [[0, 1], [0, 1]]
    need(checks.matrix(inflated) == checks.matrix(new_ops), 'inflation must be F2-neutral')
    reject('F2-neutral positive inflation', lambda: local_check(old_ops, inflated, checks))
    bad = copy.deepcopy(candidate)
    bad['C'].pop()
    reject('drop cleanup gate', lambda: checks.audit(bad, checker, geometry))
    bad = copy.deepcopy(candidate)
    bad['C'] = copy.deepcopy(base['C'])
    # The stale cleanup has the right Boolean endpoint but fails literal H4.
    obj = copy.copy(geometry)
    obj.w = bad
    obj.full()
    reject('stale nonliteral cleanup', lambda: checks.audit(bad, checker, geometry))
    bad = copy.deepcopy(candidate)
    bad['A'][old_start][0] = 0
    reject('illegal frame descent', lambda: checks.audit(bad, checker, geometry))
    bad = copy.deepcopy(candidate)
    bad['D'][0][2].pop()
    reject('missing dirty compensation', lambda: checks.audit(bad, checker, geometry))

    # A source-bound comparison, not an assumed sum of other PRs' savings.
    overlap = {'pr952_frame_gates': len(old_ops), 'selected_frame_gates': len(selected_ops),
               'new_frame_gates': len(new_ops), 'selected_slice': [selected_start, selected_stop],
               'same_positive_transfer_as_selected': checks.matrix(selected_ops, True) == checks.matrix(old_ops, True),
               'additional_frame_saving_vs_pr952': len(old_ops) - len(new_ops),
               'selected_ops': selected_ops, 'pr952_word_ADDs': scalar['original']['ADDs']}
    certificate = {'status': 'PASS_R439_FRAME281', 'base_commit': pins['base_commit'],
                   'frame': 281, 'quad': 15, 'source_slice': [old_start, old_stop],
                   'wires': wires, 'old_gates': len(old_ops), 'new_gates': len(new_ops),
                   'saved_with_cleanup': saved, 'independent': independent_result,
                   'positive_matrices': positive, 'scalar': scalar, 'prefix_source': prefix_source,
                   'labels': labels, 'columns': candidate_full['columns'],
                   'exported_records': evidence, 'overlap': overlap,
                   'controls_rejected': controls, 'word_sha256': digest(candidate),
                   'kappa_claim': 'none; unchanged paid profile; full hosted adoption not performed'}
    path = HERE / 'CERTIFICATE.json'
    if write:
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        need(canonical(certificate) == canonical(load(path)), 'certificate mismatch')
    print('PASS_R439_FRAME281 gates={}->{} local_ADDs=23673->{} columns=661 rank_mass=5129 controls={}'.format(
        len(old_ops), len(new_ops), evidence['replacement']['adds'], len(controls)))
    return certificate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='fresh directory for both reconstructed words and records')
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_certificate)
    else:
        with tempfile.TemporaryDirectory(prefix='r439-frame281-') as temporary:
            run(Path(temporary), args.write_certificate)


if __name__ == '__main__':
    main()
