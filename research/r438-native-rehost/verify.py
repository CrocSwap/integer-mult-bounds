#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound native/hosted emission of PR2423's R438 t154 construction.

@CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
Construction: Ali Romman (PR1043), Sagar Thakrar (PR2423).
Projector proof/checker: commdata2338 (PR2653). Inherited engines are unchanged.
"""
import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/bit-r438-transport-rehost/words/r438-t154.json.gz'
LAYOUT = 'research/bit-r438-transport-rehost/verify_rehost.receipt.json'
EXPECTED_C = Fraction('0.001734846264120199151475')
BASE_C = Fraction('0.001733427039589844234749')
SELECTED_COMPLEX = Fraction('0.001675462676808103522925')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # JSON histogram keys are strings after reading; normalize fresh integer
    # keys before sorting so comparisons do not depend on insertion order.
    value = json.loads(json.dumps(value))
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def load(name, path):
    # Execute authenticated source bytes, avoiding preexisting bytecode caches.
    path = ROOT / path
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def check_sources():
    pins = read(HERE / 'SOURCES.json')
    seen = set()
    for item in pins['files']:
        if item['usage'] != 'input':
            continue
        path = item['path']
        require(path not in seen, 'duplicate input pin')
        seen.add(path)
        raw = (ROOT / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source SHA256: ' + path)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == item['git_blob'], 'source Git blob: ' + path)
    require(seen == set(read(HERE / 'VERIFY.json')['inputs']), 'declared input coverage')
    return pins


def reject(name, action, expected, controls):
    try:
        action()
    except ValueError as error:
        require(expected in str(error), name + ' rejected for another reason: ' + str(error))
        controls.append({'name': name, 'rejection': str(error)})
        return
    raise ValueError('control accepted: ' + name)


def prepare():
    check_sources()
    builder = load('r438_native_builder', 'research/bit-boundary-persistence/build.py')
    pipeline = load('r438_native_pipeline', 'research/bit-boundary-persistence/pipeline.py')
    projector = load('r438_native_projector', 'research/r438-rehost-projectors/verify.py')
    layout = read(ROOT / LAYOUT)['placement']
    words = {'baseline': ROOT / builder.WORD, 'candidate': ROOT / WORD}
    local, records, decoded = {}, {}, {}
    for name, path in words.items():
        decoded[name] = json.loads(gzip.decompress(path.read_bytes()))
        local[name], records[name] = builder.replay(decoded[name])
    reference = projector.run()
    require(canonical(reference) == canonical(read(ROOT / 'research/r438-rehost-projectors/RESULT.json')),
            'projector predecessor receipt differs')
    require(canonical(decoded['candidate']) == canonical(json.loads(gzip.decompress(
        (ROOT / 'research/r438-rehost-projectors/sources/pr2423-word.json.gz').read_bytes()))),
        'projector/candidate word mismatch')
    _, children, windows = projector.chronology()
    slots, remaining = projector.expand(layout['selection'], children, windows, 438)
    require(local['candidate']['profile'] == {int(k): v for k, v in reference['local_profile'].items()},
            'independent local profiles disagree')
    require((local['candidate']['adds'], local['candidate']['rank_mass']) == (24248, 5121),
            'local cost changed')
    controls = []
    bad = copy.deepcopy(decoded['candidate'])
    bad['C'].pop()
    reject('omitted_candidate_cleanup', lambda: builder.replay(bad), 'Wrong arbitrary-dirty endpoint', controls)
    bad = copy.deepcopy(decoded['candidate'])
    bad['D'][0][2].pop()
    reject('omitted_candidate_dirty_compensation', lambda: builder.replay(bad),
           'Wrong arbitrary-dirty endpoint', controls)
    bad = copy.deepcopy(decoded['candidate'])
    require(bad['A'][154] == [79, 444, [77]], 'transport instruction changed')
    bad['A'][154][0] = 186
    reject('transport_retains_old_frame', lambda: builder.replay(bad), 'Frame descent', controls)
    return dict(builder=builder, pipeline=pipeline, projector=projector, layout=layout,
                words=words, local=local, records=records, reference=reference,
                children=children, windows=windows, slots=slots, remaining=remaining,
                local_controls=controls)


def install_selection(context):
    p = context['pipeline']
    children = context['children']
    projector = context['projector']
    layout = context['layout']
    remaining = context['remaining']

    def selection(root, output, template):
        actual = [e for e in template['schedule'] if e['kind'] == 'idle']
        fields = ('pair', 'source_level', 'target_level', 'rank')
        require([[e[k] for k in fields] for e in actual] ==
                [[e[k] for k in fields] for e in children], 'parent chronology differs')
        baseline = read(root / 'research/e8-bit-p111-tuned/data/selection9-p111.json')['bit']
        _, old_remaining = projector.expand(baseline, children, context['windows'], 439)
        # This floating heuristic is informational metadata required by the old
        # selection format. Acceptance and both moment engines use exact bills.
        cost = lambda r: r * math.log(64 / r) if r else 0.0
        proxy = sum(count * (cost(children[i]['rank']) - cost(children[i]['rank'] - sum(widths)))
                    for i, widths, count in layout['selection']['patterns'])
        selection_value = dict(layout['selection'], proxy_saving=proxy)
        p.write(output / 'candidate-selection.json', {'bit': selection_value})
        old_hist = Counter(r for r in old_remaining.values() if r)
        new_hist = Counter(r for r in remaining.values() if r)
        require(new_hist == Counter({int(k): v for k, v in layout['idle_per_replica'].items()}),
                'candidate remainders differ')
        require(sum(remaining.values()) - sum(old_remaining.values()) == 72,
                'deleted helper rank not returned')
        return {'old_remainders': dict(old_hist), 'new_remainders': dict(new_hist),
                'returned_idle_rank_per_replica': 72,
                'hosted_helpers_per_replica': len(context['slots'])}

    # A public data-choice callback, not a change to any acceptance predicate.
    p.selection = selection


def bind_emitted(template, parent, context):
    """Compare every actual emitted owner with the independent projector census."""
    projector = context['projector']
    children, slots = context['children'], context['slots']
    require(template['local_programs'] == parent['local_programs'], 'emitted local program changed')
    require(template['hosting']['slots'] == [list(x) for x in slots], 'emitted selection differs')
    require((template['stages'], template['replicas'], template['m'], template['live']) ==
            (9, 32, 64, 28416), 'emitted dimensions differ')
    calls = {}
    for call in template['calls']:
        key = (call['replica'], call['stage'])
        require(key not in calls, 'duplicate emitted call')
        require(len(call['owners']) == 660, 'emitted owner arity')
        calls[key] = call
    require(set(calls) == {(r, s) for r in range(32) for s in range(9)}, 'emitted call coverage')
    by_deadline = defaultdict(list)
    for child, cp, off, width, stage, helper in slots:
        by_deadline[child, cp].append((off, width, stage, helper))
    owner_rows = []
    for replica in range(32):
        for (child, cp), pieces in sorted(by_deadline.items()):
            side, port = divmod(cp, 111)
            expected_family = replica * 888 + (2 * children[child]['pair'] + side) * 111 + port
            axes = projector.axes(children[child]['mask'])
            for off, width, stage, helper in pieces:
                family, descriptor = calls[replica, stage]['owners'][222 + helper]
                require(family == expected_family, 'emitted owner family differs')
                require(descriptor == ['hosted', child, off, width], 'emitted owner slice differs')
                support = sum(1 << i for i in axes[off:off + width])
                owner_rows.append((replica, stage, helper, family, child, support))
    require(digest(owner_rows) == context['reference']['census']['owner_projector_sha256'],
            'emitted owner/projector digest differs')
    remainders = defaultdict(Counter)
    for (child, _), rank in context['remaining'].items():
        if child in {int(i) for i in template['hosting']['windows']}:
            remainders[str(child)][str(rank)] += 1
    require(template['hosting']['remainders'] == {i: dict(v) for i, v in remainders.items()},
            'emitted remainder factors differ')
    hist = Counter({int(r): 288 * n for r, n in context['local']['candidate']['profile'].items()})
    # Include all actual schedule remainders, including children with no hosting window.
    for event in template['schedule']:
        if event['kind'] != 'idle' or not event['rank']:
            continue
        child = str(event['idx'])
        if child in template['hosting']['remainders']:
            hist.update({int(r): 32 * n for r, n in template['hosting']['remainders'][child].items() if int(r)})
        else:
            hist[event['rank']] += 32 * 222
    require(dict(hist) == {int(k): v for k, v in context['reference']['global_profile'].items()},
            'emitted complete profile differs')
    return {'owner_projector_sha256': digest(owner_rows), 'owner_occurrences': len(owner_rows),
            'physical_deadlines': context['reference']['census']['deadline_families'],
            'remainder_factors_sha256': digest(template['hosting']['remainders']),
            'local_program_sha256': digest(template['local_programs']),
            'profile': dict(sorted(hist.items())), 'paid_children': sum(hist.values()),
            'rank_mass': sum(r * n for r, n in hist.items())}


def binding_controls(template, parent, context):
    controls = []
    # Mutate actual emitted structures. Preserve unrelated fields and counts.
    def owner_mutation(family_delta=0, offset_delta=0):
        bad = dict(template, calls=list(template['calls']))
        call = dict(bad['calls'][0], owners=list(bad['calls'][0]['owners']))
        bad['calls'][0] = call
        family, descriptor = call['owners'][222]
        descriptor = list(descriptor)
        descriptor[2] += offset_delta
        call['owners'][222] = [family + family_delta, descriptor]
        return bad
    reject('emitted_owner_wrong_port', lambda: bind_emitted(owner_mutation(1), parent, context),
           'owner family differs', controls)
    reject('emitted_owner_wrong_replica', lambda: bind_emitted(owner_mutation(888), parent, context),
           'owner family differs', controls)
    reject('emitted_owner_equal_width_wrong_slice', lambda: bind_emitted(owner_mutation(offset_delta=1), parent, context),
           'owner slice differs', controls)
    for kind in ('omit', 'undercharge'):
        bad = dict(template, hosting=dict(template['hosting']))
        remainders = copy.deepcopy(template['hosting']['remainders'])
        child = next(i for i, counts in remainders.items() if '34' in counts)
        n = remainders[child].pop('34')
        if kind == 'undercharge':
            remainders[child]['33'] = n
        bad['hosting']['remainders'] = remainders
        reject('emitted_rank34_' + kind, lambda: bind_emitted(bad, parent, context),
               'remainder factors differ', controls)
    bad = dict(template, local_programs=copy.deepcopy(template['local_programs']))
    key = next(iter(bad['local_programs']))
    bad['local_programs'][key].pop()
    reject('emitted_local_instruction_omitted', lambda: bind_emitted(bad, parent, context),
           'local program changed', controls)
    return controls


def summarize(out, context):
    result = read(out / 'RESULT.json')
    parent = json.loads(gzip.decompress((out / 'candidate/nine/GLOBAL-TEMPLATE.json.gz').read_bytes()))
    template = json.loads(gzip.decompress((out / 'candidate/hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()))
    binding = bind_emitted(template, parent, context)
    controls = binding_controls(template, parent, context)
    actual_global = read(out / 'candidate/hosted/GLOBAL.json')
    require(digest(template) == actual_global['template_sha256'], 'hosted template content digest')
    # The inherited geometry JSON includes wall-clock seconds, whose raw hash
    # propagates into both templates. Authenticate every original link first,
    # then replace only these timing-dependent links by semantic digests.
    geometry_raw = (out / 'geometry/GEOMETRY.json').read_bytes()
    geometry = json.loads(geometry_raw)
    require(isinstance(geometry.pop('seconds'), (int, float)), 'geometry elapsed-time field')
    raw_geometry_hash = hashlib.sha256(geometry_raw).hexdigest()
    semantic_geometry_hash = digest(geometry)
    for name in ('baseline', 'candidate'):
        entry = result[name]['hosted']
        parent_template = json.loads(gzip.decompress((out / name / 'nine/GLOBAL-TEMPLATE.json.gz').read_bytes()))
        hosted_template = json.loads(gzip.decompress((out / name / 'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()))
        require(entry['parent']['geometry_sha256'] == parent_template['geometry_sha256'] ==
                hosted_template['geometry_sha256'] == raw_geometry_hash, 'raw geometry hash binding')
        require(digest(parent_template) == entry['parent']['template_sha256'] ==
                entry['parent_audit']['template_sha256'], 'raw parent template hash binding')
        require(digest(hosted_template) == entry['audit']['template_sha256'] ==
                read(out / name / 'hosted/GLOBAL.json')['template_sha256'], 'raw hosted template hash binding')
        parent_template['geometry_sha256'] = semantic_geometry_hash
        hosted_template['geometry_sha256'] = semantic_geometry_hash
        for receipt, field, value in (
            (entry['parent'], 'geometry_sha256', semantic_geometry_hash),
            (entry['parent'], 'template_sha256', digest(parent_template)),
            (entry['parent_audit'], 'template_sha256', digest(parent_template)),
            (entry['audit'], 'template_sha256', digest(hosted_template)),
        ):
            receipt.pop(field)
            receipt['semantic_' + field] = value
    for name, expected in (('baseline', BASE_C), ('candidate', EXPECTED_C)):
        entry = result[name]
        require(all(entry['interface']['hypotheses'].values()) and
                all(entry['interface']['conclusion'].values()), 'inherited scalar interface failed')
        invoice = entry['hosted']['invoice']
        require(Fraction(invoice['bit_lower']) == expected, name + ' exact endpoint differs')
        require(Fraction(invoice['next_grid_point_rejected']) == expected + Fraction(1, 10**24),
                name + ' root bracket differs')
        require((invoice['bit']['charged_prefix_bits'], invoice['bit']['charged_two_level_coefficient_bits'],
                 invoice['bit']['row_coefficient']) == (192, 512, 18355), 'complete precision/row bill changed')
        require(len(entry['hosted']['parent_audit']['mutations_rejected']) == 17 and
                len(entry['hosted']['audit']['mutations_rejected']) == 16, 'inherited control coverage')
    candidate = result['candidate']['hosted']
    require(binding['profile'] == {int(k): v for k, v in candidate['audit']['profile'].items()},
            'emitted binding/audit profile mismatch')
    require(binding['rank_mass'] == 64 * 28416 - 10272 and binding['paid_children'] == 904320,
            'emitted complete bill mismatch')
    require(EXPECTED_C > BASE_C > SELECTED_COMPLEX, 'supplier binding changed')
    # Retain every proof-relevant field of the complete source pipeline result.
    # Runtime/toolchain fields and historical cited PR548 assembly are separate.
    result.pop('environment')
    for entry in (result['baseline'], result['candidate']):
        entry['hosted']['invoice'].pop('kappa')
    local = {name: {k: v for k, v in receipt.items() if k != 'paths'}
             for name, receipt in context['local'].items()}
    return {'schema_version': 1, 'status': 'PASS_R438_NATIVE_REHOST',
            'base_commit': read(HERE / 'SOURCES.json')['base_commit'],
            'normalization': 'Original raw geometry/template hashes checked within each run; semantic_* hashes omit only geometry.seconds and rebind that geometry digest in the templates.',
            'geometry': {'semantic_sha256': semantic_geometry_hash,
                         'h': geometry['h'], 'm': geometry['m'], 'stages': geometry['stages'],
                         'ports': len(geometry['ports']), 'route_checks': geometry['route_checks'],
                         'missing_route_factor_controls': geometry['missing_route_factor_controls'],
                         'full_generated_artifact': 'geometry/GEOMETRY.json'},
            'local': local, 'pipeline': result, 'emitted_binding': binding,
            'projector_receipt': context['reference'],
            'controls': context['local_controls'] + controls,
            'selected_context': {'bit_lower': str(BASE_C), 'complex_lower': str(SELECTED_COMPLEX),
                                 'kappa': '836330098538459/500000000000000000', 'binding': 'complex'},
            'no_new_kappa': True}


def execute(out, context):
    install_selection(context)
    context['pipeline'].run(ROOT, out, context['words'], context['local'], context['records'])
    result = summarize(out, context)
    write(out / 'CERTIFICATE.json', result)
    return result


def main():
    require(__debug__, 'Inherited checkers require assertions: do not use -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Retain a full replay in a NEW directory')
    parser.add_argument('--local-only', action='store_true', help='Recheck local/interface geometry only; no native claim')
    parser.add_argument('--write-certificate', type=Path, help='Write a fresh external certificate instead of comparing')
    args = parser.parse_args()
    require(not args.local_only or (args.output is None and args.write_certificate is None),
            'local-only is incompatible with output/certificate options')
    if args.write_certificate:
        require(not args.write_certificate.exists(), 'Certificate destination exists')
        require(HERE not in args.write_certificate.resolve().parents, 'Certificate output must be outside the package')
    context = prepare()
    if args.local_only:
        expected = read(HERE / 'CERTIFICATE.json')
        require(canonical(expected['projector_receipt']) == canonical(context['reference']), 'stored projector receipt')
        local = {name: {k: v for k, v in r.items() if k != 'paths'} for name, r in context['local'].items()}
        require(canonical(local) == canonical(expected['local']), 'stored local receipt')
        require(expected['controls'][:3] == context['local_controls'], 'stored local controls')
        print('PASS_R438_NATIVE_REHOST_LOCAL local_columns=660 native_not_run no_new_kappa')
        return
    if args.output:
        out = args.output.resolve()
        require(not out.exists(), 'Output directory already exists')
        result = execute(out, context)
    else:
        with tempfile.TemporaryDirectory(prefix='r438-native-rehost-') as temporary:
            result = execute(Path(temporary) / 'run', context)
    if args.write_certificate:
        with args.write_certificate.open('x') as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        require(canonical(result) == canonical(read(HERE / 'CERTIFICATE.json')), 'complete stored certificate differs')
    print('PASS_R438_NATIVE_REHOST native=5,9,11 owners=126144 children=904320 '
          'c=0.001734846264120199151475 no_new_kappa')


if __name__ == '__main__':
    main()
