#!/usr/bin/env python3
"""Verify the source boundary, complete native words and hosted invoice.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


build = module('build')
pipeline = module('pipeline')


def digest(value):
    return hashlib.sha256(build.canonical(value)).hexdigest()


def boundary(word, local):
    receipt = build.lifetime(word)
    old, new = (local[name]['paths'] for name in ('baseline', 'candidate'))
    changes = {}
    for row, path in enumerate(old):
        if row != build.HELPER and path != new[row - (row > build.HELPER)]:
            changes[str(row)] = [path, new[row - (row > build.HELPER)]]
    build.require(changes == {'444': [[0, 79, 509, 392, 513, 1],
                                     [0, 186, 509, 392, 513, 1]]},
                  'Another surviving frame path changed')
    receipt.update(changed_surviving_paths=changes, removed_path=old[build.HELPER],
                   source_path=old[build.SOURCE],
                   frames={str(f): {'lines': word['frames'][f],
                           'rank': build.rank(word['lines'][i] for i in word['frames'][f])}
                           for f in (79, 186, 509)},
                   all_paths_sha256=digest({'baseline': old, 'candidate': new}))
    return receipt


def local_controls(original, candidate):
    controls = []

    def reject(name, action, reason):
        try:
            action()
        except ValueError as error:
            build.require(str(error) == reason, 'Control failed for another reason: ' + name)
            controls.append({'name': name, 'rejection': reason})
        else:
            raise ValueError('Control was accepted: ' + name)

    changed = copy.deepcopy(original)
    changed['A'][426] = [186, 77, [292]]
    reject('source77_changed_before_read', lambda: build.lifetime(changed),
           'Source changed before the late read')
    changed = copy.deepcopy(original)
    changed['A'][build.READ + 2][2].append(build.HELPER)
    reject('another_live_carrier_use', lambda: build.lifetime(changed),
           'Carrier has another live use')
    changed = copy.deepcopy(candidate)
    changed['A'][build.READ - 1][0] = 79
    reject('late_source_read_in_old_line_frame', lambda: build.replay(changed), 'Frame descent')
    changed = copy.deepcopy(candidate)
    changed['C'].pop(0)
    reject('omitted_literal_restoration', lambda: build.replay(changed), 'Wrong arbitrary-dirty endpoint')
    changed = copy.deepcopy(candidate)
    changed['D'][0][2].pop(0)
    reject('omitted_dirty_target_compensation', lambda: build.replay(changed), 'Wrong arbitrary-dirty endpoint')
    # A neutral pair is legal, but both native ADDs must be paid.
    changed = copy.deepcopy(candidate)
    duplicate = [0, changed['D'][0][1], [changed['D'][0][2][0]]]
    changed['D'][0:0] = [copy.deepcopy(duplicate), duplicate]
    positive, _ = build.replay(changed)
    clean, _ = build.replay(candidate)
    build.require(positive['adds'] == clean['adds'] + 2 and positive['profile'] == clean['profile'],
                  'Neutral paid ADD pair was not accepted and charged')
    return {'rejected': controls, 'accepted_paid_neutral_pair': {'extra_adds': 2, 'same_profile': True}}


def check_hosted_change(result, local):
    change = result['hosting_change']
    actual = {}
    for name in ('baseline', 'candidate'):
        audit = result[name]['hosted']['audit']
        profile = {int(rank): count for rank, count in audit['profile'].items()}
        build.require(sum(rank * count for rank, count in profile.items())
                      == 64 * audit['live'] - audit['deficit'], 'Wrong hosted rank mass')
        actual[name] = Counter(profile)
    expected = actual['baseline'].copy()
    for sign, name in ((-1, 'baseline'), (1, 'candidate')):
        for rank, count in local[name]['profile'].items():
            expected[int(rank)] += sign * 288 * count
    for sign, key in ((-1, 'old_remainders'), (1, 'new_remainders')):
        for rank, count in change[key].items():
            expected[int(rank)] += sign * 32 * count
    build.require(+expected == +actual['candidate'], 'Hosted profile differs from the complete recount')
    build.require(sum(actual['baseline'].values()) - sum(actual['candidate'].values()) == 576,
                  'Wrong paid recursive call saving')
    return {'paid_calls': {name: sum(profile.values()) for name, profile in actual.items()},
            'saved_calls': 576, 'returned_idle_rank': 32 * change['returned_idle_rank_per_replica']}


def idle_control(result, local):
    changed = copy.deepcopy(result)
    profile = changed['candidate']['hosted']['audit']['profile']
    delta = Counter()
    for sign, key in ((-1, 'old_remainders'), (1, 'new_remainders')):
        for rank, count in result['hosting_change'][key].items():
            delta[str(rank)] += sign * 32 * count
    for rank, count in delta.items():
        profile[rank] = profile.get(rank, 0) - count
    try:
        check_hosted_change(changed, local)
    except ValueError as error:
        build.require(str(error) == 'Wrong hosted rank mass', 'Idle control failed for another reason')
        return {'name': 'deleted_helper_without_returned_idle_charge', 'rejection': str(error)}
    raise ValueError('Omitted idle charge was accepted')


def certificate(original, local, result, selected):
    boundary_receipt = boundary(original, local)
    controls = local_controls(original, build.build(original))
    controls['rejected'].append(idle_control(result, local))
    hosted = {}
    for name in ('baseline', 'candidate'):
        section = result[name]['hosted']
        # Container hashes and running times are not mathematical outputs.
        audit = {key: value for key, value in section['audit'].items()
                 if key not in ('template_sha256', 'seconds')}
        parent = section['parent']
        parent_keys = ('all_scalar_columns_restored', 'bridge_additions', 'copy_erase_episodes',
                       'halving_integer_inequality', 'independent_unbanked_scalar_columns',
                       'local_checks', 'local_invocations', 'scalar_stages', 'omitted_bridge_shears_rejected')
        invoice = {key: value for key, value in section['invoice'].items() if key != 'kappa'}
        hosted[name] = {'audit': audit, 'invoice': invoice,
                        'parent': {key: parent[key] for key in parent_keys},
                        'parent_controls': section['parent_audit']['mutations_rejected']}
    old_c = Fraction(hosted['baseline']['invoice']['bit_lower'])
    new_c = Fraction(hosted['candidate']['invoice']['bit_lower'])
    build.require(old_c == Fraction(selected['bit_lower']) and new_c > old_c > Fraction(selected['complex_lower']),
                  'Selected supplier comparison changed')
    return {'status': 'PASS_R438_SOURCE_BOUNDARY_AND_FULL_HOSTED_INVOICE',
            'base_commit': build.BASE, 'boundary': boundary_receipt,
            'local': {name: {key: value for key, value in item.items() if key != 'paths'}
                      for name, item in local.items()},
            'native': {name: {key: result[name][key] for key in ('interface', 'legality', 'columns')}
                       for name in ('baseline', 'candidate')},
            'hosting_change': result['hosting_change'], 'hosted': hosted,
            'paid_recount': check_hosted_change(result, local), 'controls': controls,
            'selected_context': {key: selected[key] for key in ('kappa', 'complex_lower', 'bit_lower', 'binding')},
            'no_new_kappa': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory for the full replay')
    args = parser.parse_args()
    out = args.output.resolve()
    build.require(not out.exists(), 'Output directory already exists')
    manifest = pipeline.read(PACKAGE / 'SOURCES.json')
    build.require(manifest['base_commit'] == build.BASE, 'Wrong source base')
    for name, expected in manifest['files'].items():
        build.require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                      'Source hash mismatch: ' + name)
    original = build.load(ROOT / build.WORD)
    candidate = build.build(original)
    receipts, records = {}, {}
    for name, word in (('baseline', original), ('candidate', candidate)):
        receipts[name], records[name] = build.replay(word)
    paths = {name: receipt['paths'] for name, receipt in receipts.items()}
    build.require(paths == pipeline.read(PACKAGE / 'FRAME-PATHS.json'), 'Stored frame paths differ')
    expected = pipeline.read(PACKAGE / 'CERTIFICATE.json')
    for name in ('baseline', 'candidate'):
        build.require(receipts[name]['word_sha256'] == expected['local'][name]['word_sha256'],
                      'Constructed word differs from the certificate')
    with tempfile.TemporaryDirectory(prefix='bit-boundary-') as temporary:
        word_file = Path(temporary) / 'candidate.json.gz'
        build.save(word_file, candidate)
        result = pipeline.run(ROOT, out, {'baseline': ROOT / build.WORD, 'candidate': word_file}, receipts, records)
    selected = pipeline.read(ROOT / 'research/community-frontier942-audit/ASSEMBLY.json')
    observed = certificate(original, receipts, result, selected)
    pipeline.write(out / 'CERTIFICATE.json', observed)
    pipeline.write(out / 'FRAME-PATHS.json', paths)
    # Compare JSON objects so histogram keys have the same string type.
    build.require(build.canonical(pipeline.read(out / 'CERTIFICATE.json')) == build.canonical(expected),
                  'Full certificate differs')
    print('PASS_R438_SOURCE_BOUNDARY R=439->438 ADDs=24305->24248 '
          'paid_calls=904896->904320 c=0.001734176288479865766692 controls=6 no_new_kappa')


if __name__ == '__main__':
    main()
