#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check retained cold-run evidence integrity; this does not rerun the proof.

Companion to verify.py's exact bounded mathematics. full_replay.py remains the
command for a fresh native/global/outer replay. Prepared by Mason Hale with
substantial OpenAI Codex assistance.
"""
import argparse
import copy
import hashlib
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path, PurePosixPath

FULL_STAGES = [
    'reconstruct', 'lift', 'native-base', 'native-extra', 'rebuild-borrow',
    'rebind', 'lemma-g', 'discover', 'strict', 'geometry', 'outer-ledger',
    'outer-independent', 'outer-replay',
]
WRAPPER_STAGES = ['generate', 'baseline', 'candidate']
NATIVE_STEPS = ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
BASELINE_STAGES = [
    'fine-engine-oracle', 'retained-provider-and-parent-admission',
    'reconstruct-owners', 'lift-parent', 'native-new-base', 'native-new-extra',
    'rebuild-words-566', 'rebuild-borrow-words', 'audit-local-566-base',
    'audit-local-566-extra', 'rebind-566', 'lemmag-labels', 'strict-t74',
    'geometry-controls',
]
FILES = {
    'outer_ledger_sha256': 'OUTER-LEDGER.json',
    'strict_assembly_sha256': 'STRICT-ASSEMBLY.json',
    'invoice_sha256': 'PREFIX-AND-INVOICE.json',
    'outer_independent_sha256': 'OUTER-INDEPENDENT.json',
    'baseline_result_sha256': 'BASELINE-RESULT.json',
    'baseline_release_sha256': 'BASELINE-RELEASE-RECEIPT.json',
    'local_generation_sha256': 'LOCAL-GENERATION-RESULT.json',
}
EVIDENCE_NAMES = ['FULL-RESULT.json', *FILES.values(),
                  'NATIVE-BASE-STEPS.json', 'NATIVE-EXTRA-STEPS.json']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def parse(raw):
    def invalid(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid)


def is_digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def stages(rows, names, label, native=False, wrapper=False):
    require(type(rows) is list and len(rows) == len(names), label + ': exact stage count')
    key = 'step' if native else 'name'
    fields = {key, 'exit_code', 'seconds'}
    if not native:
        fields.add('log_sha256')
    if wrapper:
        fields.add('command')
    for row, name in zip(rows, names):
        require(type(row) is dict and set(row) == fields, label + ': stage fields')
        require(row[key] == name, label + ': exact stage order')
        require(type(row['exit_code']) is int and row['exit_code'] == 0,
                label + ': successful integer exit code')
        seconds = row['seconds']
        require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0,
                label + ': finite nonnegative elapsed time')
        if not native:
            require(is_digest(row['log_sha256']), label + ': log digest')
        if wrapper:
            command = row['command']
            require(type(command) is list and len(command) >= 3 and
                    all(type(x) is str for x in command), label + ': command list')
            expected = {'generate': 'generator.py', 'baseline': 'verify_release.py',
                        'candidate': 'admit.py'}[name]
            require(command[1] == '-B' and Path(command[2]).name == expected,
                    label + ': exact wrapper program')
            require('--native-cache' not in command, label + ': no native cache argument')


def histogram(value, label):
    require(type(value) is dict and value, label + ': nonempty histogram')
    result = {}
    for rank, count in value.items():
        require(type(rank) is str and rank.isdigit() and str(int(rank)) == rank and
                0 < int(rank) < 73, label + ': canonical rank')
        require(type(count) is int and count > 0, label + ': positive integer count')
        result[int(rank)] = count
    return result


def validate(full, blobs, predecessors, claim):
    require(type(full) is dict, 'Full receipt object')
    require(full['status'] == 'PASS_CHANGED_T74_FULL_CONDITIONAL_ADMISSION', 'Full status')
    require(full['fresh_baseline'] is True and full['fresh_changed_natives'] is True,
            'Exact fresh-admission booleans')
    stages(full['stages'], FULL_STAGES, 'candidate')
    stages(full['reproduction_stages'], WRAPPER_STAGES, 'wrapper', wrapper=True)
    for field, name in FILES.items():
        require(is_digest(full[field]) and digest(blobs[name]) == full[field],
                'Retained evidence digest: ' + name)
    require(type(full['native_steps_sha256']) is dict and
            set(full['native_steps_sha256']) == {'base', 'extra'}, 'Native digest keys')
    for tag in ('base', 'extra'):
        name = 'NATIVE-' + tag.upper() + '-STEPS.json'
        expected = full['native_steps_sha256'][tag]
        require(is_digest(expected) and digest(blobs[name]) == expected,
                'Retained native digest: ' + tag)
        stages(parse(blobs[name]), NATIVE_STEPS, 'native ' + tag, native=True)

    docs = {name: parse(blobs[name]) for name in FILES.values()}
    baseline = docs['BASELINE-RESULT.json']
    release = docs['BASELINE-RELEASE-RECEIPT.json']
    source_manifest = predecessors['sources']['2588']['manifest_sha256']
    require(full['source_manifest'] == baseline['manifest_sha256'] ==
            release['manifest_sha256'] == source_manifest, 'Predecessor manifest binding')
    require(baseline['status'] == 'PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION' and
            release['status'] == 'PASS_RELEASE', 'Complete predecessor admission')
    require(baseline['native_reuse'] == {'base': False, 'extra': False} and
            all(value is False for value in baseline['native_reuse'].values()),
            'Fresh predecessor native runs')
    stages(baseline['stages'], BASELINE_STAGES, 'baseline')
    # The inherited strict assembly and release use different outer maps.
    # Their exact file digests bind both results; presentation decimals are
    # deliberately not treated as rational endpoints or equated across layers.
    require(Fraction(baseline['kappa']) > 0, 'Positive baseline rational endpoint')

    generated = docs['LOCAL-GENERATION-RESULT.json']
    require(generated['status'] == 'PASS_LATE_ASSIGNMENT_LOCAL_WORDS_AND_CONTROLS',
            'Exact local generation status')
    require(type(generated['providers']) is dict and
            set(generated['providers']) == {'base', 'extra'}, 'Both generated providers')
    control_names = ['removed_prelude', 'missing_restoration', 'wrong_restoration_sign',
                     'wrong_alias', 'wrong_warp']
    for tag in ('base', 'extra'):
        controls = generated['providers'][tag]['controls']
        require(type(controls) is list and len(controls) == 5, 'Five local controls ' + tag)
        require([row['name'] for row in controls] == control_names, 'Local control names ' + tag)
        require(all(row['rejected'] is True and row['cleanup_rederived'] is True
                    for row in controls), 'Local control rejections ' + tag)

    assembly = docs['STRICT-ASSEMBLY.json']
    invoice = docs['PREFIX-AND-INVOICE.json']
    ledger = docs['OUTER-LEDGER.json']
    independent = docs['OUTER-INDEPENDENT.json']
    require(assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY',
            'Strict assembly status')
    require(invoice['status'] == 'PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE',
            'Physical invoice status')
    require(ledger['status'] == 'PASS_FINE_PRIME_PADDING_EXACT_ARITHMETIC' and
            independent['status'] == 'PASS_INDEPENDENT_BALANCE_DERIVATION',
            'Outer checked statuses')
    require(type(full['physical']) is int and full['physical'] == invoice['physical'] == 66814 and
            type(full['private_zero_buffers']) is int and
            full['private_zero_buffers'] == invoice['private_zero_buffers'] == 78 and
            invoice['live'] == ledger['W'] == 66304 and ledger['m'] == 73,
            'Full physical inventory')
    profile = histogram(full['profile'], 'full')
    require(profile == histogram(assembly['complex_profile'], 'assembly') ==
            histogram(ledger['profile'], 'outer'), 'All complete paid profiles agree')
    require(sum(rank * count for rank, count in profile.items()) == 4816512,
            'Complete charged rank mass')
    row = ledger['rows']['struct_boundary_radix_union']
    checks = row['strict_checks']
    require(type(checks) is dict and len(checks) == 63 and
            all(Fraction(value['rational']) > 0 for value in checks.values()),
            '63 strict rational outer checks')
    kappa = Fraction(full['kappa'])
    require(kappa == Fraction(row['kappa']['rational']) ==
            Fraction(independent['rows']['struct_boundary_radix_union']['kappa']),
            'Full and independent outer rational agreement')
    require(Fraction(full['comparison_kappa']) < Fraction(claim['kappa']) <= kappa <
            Fraction(assembly['complex_lower']), 'Published improved outer claim')
    require(Fraction(full['gain']) == kappa - Fraction(full['comparison_kappa']), 'Exact gain')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    package = args.package.resolve()
    blobs = {name: (package / 'evidence' / name).read_bytes() for name in EVIDENCE_NAMES}
    full = parse(blobs['FULL-RESULT.json'])
    predecessors = parse((package / 'PREDECESSORS.json').read_bytes())
    claim = parse((package / 'CLAIM.json').read_bytes())
    pins = full['execution_inputs']
    require(type(pins) is dict and pins, 'Execution input digest object')
    required = {'full_replay.py', 'admit.py', 'generator.py', 'packing.py', 'verify.py',
                'common.py', 'independent_late8.py', 'PREDECESSORS.json', 'SOURCE-PINS.json',
                'BOUNDED-SOURCES.json', 'inputs/pr2673/FILL.json.gz',
                'inputs/pr2673/ORDER.json', 'inputs/pr2673/DISPATCH.json',
                'inputs/pr2673/OUTER-CLAIM.json', 'inputs/pr2673/PROFILE.json'}
    require(required <= set(pins), 'Required full execution input bindings')
    execution_files = set(package.rglob('*.py')) | {p for p in (package / 'inputs').rglob('*') if p.is_file()}
    execution_files.update(package / name for name in ('PREDECESSORS.json', 'SOURCE-PINS.json', 'BOUNDED-SOURCES.json'))
    require(set(pins) == {p.relative_to(package).as_posix() for p in execution_files},
            'Complete execution input inventory')
    comparison = parse((package / 'inputs/pr2673/OUTER-CLAIM.json').read_bytes())
    require(Fraction(full['comparison_kappa']) == Fraction(claim['comparison']['kappa']) ==
            Fraction(comparison['kappa_rational']), 'Pinned comparison rational binding')
    for name, expected in pins.items():
        path = PurePosixPath(name)
        require(type(name) is str and not path.is_absolute() and '..' not in path.parts and
                str(path) == name and is_digest(expected), 'Safe execution digest entry')
        require(digest((package / name).read_bytes()) == expected, 'Changed execution input: ' + name)
    validate(full, blobs, predecessors, claim)

    rejected = []
    def reject(name, mutated_full, mutated_blobs):
        try:
            validate(mutated_full, mutated_blobs, predecessors, claim)
        except (ValueError, KeyError, TypeError, IndexError):
            rejected.append(name)
        else:
            raise ValueError('Invalid retained evidence accepted: ' + name)
    for key in ('stages', 'reproduction_stages'):
        bad = copy.deepcopy(full)
        bad[key] = []
        reject('empty ' + key, bad, blobs)
        bad = copy.deepcopy(full)
        bad[key].pop()
        reject('truncated ' + key, bad, blobs)
        bad = copy.deepcopy(full)
        bad[key][0], bad[key][1] = bad[key][1], bad[key][0]
        reject('reordered ' + key, bad, blobs)
    bad = copy.deepcopy(full)
    bad['stages'][0]['exit_code'] = False
    reject('boolean exit code', bad, blobs)
    bad_blobs = dict(blobs)
    bad_blobs['OUTER-LEDGER.json'] += b'\n'
    reject('byte-only outer ledger drift', full, bad_blobs)
    bad_blobs = dict(blobs)
    altered = parse(blobs['OUTER-LEDGER.json'])
    altered['scope'] = 'altered retained scope'
    bad_blobs['OUTER-LEDGER.json'] = json.dumps(altered).encode()
    reject('outer ledger field drift', full, bad_blobs)
    bad_blobs = dict(blobs)
    steps = parse(blobs['NATIVE-BASE-STEPS.json'])[:-1]
    bad_blobs['NATIVE-BASE-STEPS.json'] = json.dumps(steps).encode()
    bad = copy.deepcopy(full)
    bad['native_steps_sha256']['base'] = digest(bad_blobs['NATIVE-BASE-STEPS.json'])
    reject('truncated native steps with updated digest', bad, bad_blobs)
    print('PASS_RETAINED_FULL_EVIDENCE_INTEGRITY', 'candidate_stages=13 wrapper_stages=3',
          'native_steps=5+5', 'controls=' + str(len(rejected)))


if __name__ == '__main__':
    main()
