#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Native admission of Ross Richardson's PR1256 helper470 endpoint.

Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
The retirement patch is PR1256's construction, not a new circuit claim.
"""
import argparse
import ast
import collections
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
HUB = 'research/e8-bit-carrier-skeleton'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
PREFIX_SOURCE = ('research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/'
                 'vendor/e8-r715-eleven-stage-whole/code/global_k.py')
ADMITTED = 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
ADAPTER = 'research/e8-bit-p111-tuned/code/adapt9p.py'
RETIREMENT = [[186, 470, [77]], [513, 444, [470]], [513, 475, [470]]]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path):
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def source_pins(root):
    manifest = load(HERE / 'SOURCES.json')
    for item in manifest['files']:
        if item['usage'] != 'input':
            continue
        raw = (root / item['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source SHA256: ' + item['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == item['git_blob'], 'source Git blob: ' + item['path'])


def prefix_contract(root):
    tree = ast.parse((root / PREFIX_SOURCE).read_text())
    formulas = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'prefix' for t in node.targets)]
    expected = ast.parse('(1 << nb) * cf ** (K + 1) * cb ** K', mode='eval').body
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(expected), 'source prefix expression')
    bridge = ast.parse('nb == 6 * (K - 1)', mode='eval').body
    need(any(isinstance(node, ast.Compare) and ast.dump(node) == ast.dump(bridge)
             for node in ast.walk(tree)), 'source bridge exponent')
    admitted = load(root / ADMITTED)['nine']['bit']
    need(admitted['charged_prefix_bits'] == 192 and admitted['prefix_bits'] == 177,
         'pinned nine-stage precision charge')
    endpoint = ast.parse('all(dims[final[i]] == H for i in range(2 * V, LOCAL))', mode='eval').body
    need(sum(isinstance(node, ast.Assert) and ast.dump(node.test) == ast.dump(endpoint)
             for node in ast.walk(tree)) == 1, 'source full-helper endpoint condition')
    # The punctured-word adapter applies only these literal source replacements.
    # Check that none can consume or alter the full-helper assertion.
    adaptation = ast.parse((root / ADAPTER).read_text())
    edit_tables = [node.value for node in ast.walk(adaptation) if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'EDITS' for t in node.targets)]
    need(len(edit_tables) == 1 and isinstance(edit_tables[0], ast.Dict), 'pinned adapter edit table')
    guards = [ast.get_source_segment((root / PREFIX_SOURCE).read_text(), node)
              for node in ast.walk(tree) if isinstance(node, ast.Assert)
              and ast.dump(node.test) == ast.dump(endpoint)]
    for key, value in zip(edit_tables[0].keys, edit_tables[0].values):
        if isinstance(key, ast.Constant) and key.value == 'global_k.py':
            for edit in value.elts[1].elts:
                old = ast.literal_eval(edit.elts[0])
                need(old not in guards[0], 'adapter changes full-helper condition')


def candidate(word, full_endpoint=False):
    need(word['C'][580] == [1, 444, [470]], 'pinned cleanup replacement')
    need(word['C'][2343] == [1, 470, [77]], 'pinned cleanup omission')
    result = copy.deepcopy(word)
    result['B'] = copy.deepcopy(RETIREMENT) + result['B']
    result['C'][580] = [1, 444, [77]]
    del result['C'][2343]
    result['final'][470] = 1 if full_endpoint else 513
    return result


def owning_checker(root):
    spec = importlib.util.spec_from_file_location('pinned_xcheck', root / CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local_check(word, module):
    check = module.Word(word)
    values, frames, _ = check.replay()
    expected = [(1 << r) ^ (1 << (r - word['v']))
                if word['v'] <= r < 2 * word['v'] else 1 << r for r in range(check.n)]
    need(values == expected, 'complete local dirty scalar endpoint')
    for register, final in enumerate(word['final']):
        need(check.nested(frames[register], final), 'final frame descent')
    hypotheses, conclusion, _ = check.interface()
    return {'columns': check.n, 'hypotheses': hypotheses, 'conclusion': conclusion,
            'nonfull_helpers': [r for r in range(2 * word['v'], check.n)
                                if check.fdim[word['final'][r]] != 8]}


def record_invoice(records):
    rows = list(struct.iter_unpack('<6i', Path(records).read_bytes()))
    histogram = collections.Counter()
    paths = collections.defaultdict(list)
    adds = moves = copies = erasures = 0
    for op, a, b, c, f, z in rows:
        if op == 0:
            moves += 1
            need(f > 0, 'nonpositive exported MOVE')
            histogram[f] += 1
            paths[a].append([b, c, f])
        elif op == 1:
            adds += 1
        elif op == 2:
            copies += 1
            histogram[z] += 1
        elif op == 3:
            erasures += 1
        else:
            raise ValueError('record opcode')
    return {'records': len(rows), 'ADDs': adds, 'MOVEs': moves, 'COPYs': copies,
            'ERASEs': erasures, 'profile': {str(r): histogram[r] for r in sorted(histogram)},
            'children': sum(histogram.values()), 'rank_mass': sum(r * n for r, n in histogram.items()),
            'helper470_moves': paths[470]}, paths


def execute(argv, log, timeout=180):
    with Path(log).open('w') as stream:
        subprocess.run([str(x) for x in argv], stdout=stream, stderr=subprocess.STDOUT,
                       check=True, timeout=timeout)


def profile_delta(before, after):
    return {str(r): after.get(str(r), 0) - before.get(str(r), 0)
            for r in sorted(map(int, set(before) | set(after)))
            if after.get(str(r), 0) != before.get(str(r), 0)}


def native(root, output, words, boost):
    hub = root / HUB
    checker = hub / 'code/bit/checkers'
    flags = shlex.split(os.environ.get('CXX', 'c++')) + ['-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9',
        '-I' + str(hub / 'portable-include'), '-I' + str(checker), '-I' + str(boost)]
    execute(flags + [checker / 'legality_h.cpp', '-o', output / 'legality'], output / 'compile-legality.log')
    for pairs in (2, 4, 5):
        execute(flags + ['-DVPORTS=111', '-DRHELP=439', '-DKPAIRS=' + str(pairs),
            checker / 'columns_k.cpp', '-o', output / ('columns-' + str(pairs))],
            output / ('compile-columns-' + str(pairs) + '.log'))
    reports, paths = {}, {}
    for name, word in words.items():
        folder = output / name
        folder.mkdir()
        archive = folder / 'word.json.gz'
        archive.write_bytes(gzip.compress(canonical(word), mtime=0))
        records, cin, cout = (folder / x for x in ('records', 'cin', 'cout'))
        execute([sys.executable, '-I', '-B', hub / 'code/bit/export_records.py', archive, records], folder / 'export.log')
        execute([sys.executable, '-I', '-B', hub / 'code/bit/regression/stage_cohort.py', records, records, cin, cout], folder / 'stage.log')
        invoice, paths[name] = record_invoice(records / '249-records.bin')
        execute([output / 'legality', cin, cout, cout / 'legality.json'], folder / 'legality.log')
        legality = load(cout / 'legality.json')
        need(legality['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE', 'native geometry')
        legality['paid_histogram'] = {str(r): n for r, n in legality['paid_histogram']}
        for theirs, ours in [('records', 'records'), ('common_frame_ADDs', 'ADDs'), ('nested_MOVEs', 'MOVEs'),
            ('copies', 'COPYs'), ('erasures', 'ERASEs'), ('rank_mass', 'rank_mass'), ('paid_histogram', 'profile')]:
            need(legality[theirs] == invoice[ours], 'independent record recount: ' + ours)
        staged = {}
        for pairs in (2, 4, 5):
            label = 'columns-' + str(pairs)
            execute([output / label, cout / 'COHORT249-RECORDS.bin', cout / (label + '.json')], folder / (label + '.log'))
            report = load(cout / (label + '.json'))
            report.pop('seconds')
            report.pop('local_scalar_stream')
            report['local_raw_H'] = {str(r): n for r, n in report['local_raw_H']}
            expected_status = ('PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL'
                if pairs == 2 else 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL')
            need(report['status'] == expected_status, 'native column status')
            need(len(report['stages']) == 2 * pairs + 1, 'all stage reports')
            need(report['formal_columns_checked'] == 2 * pairs * 111 + 439, 'all staged columns')
            need(report['local_raw_H'] == invoice['profile'], 'staged paid histogram')
            need(report['local_scalar_additions'] == invoice['ADDs'], 'staged ADDs')
            need(report['fresh_center_copies'] == 9 * (2 * pairs + 1), 'all stage copies')
            need(report['bridge_additions'] == 6 * (pairs - 1) * 111, 'all bridge charges')
            need(len(report['negative_controls']) == 6 * (pairs - 1) and
                 all(c['rejected'] is True for c in report['negative_controls']), 'bridge controls')
            forward, backward = [int(x['cancellation_free_signed_row_l1_upper']) for x in report['signed_lift_prefix']]
            stages = 2 * pairs + 1
            need([x['reverse'] for x in report['signed_lift_prefix']] == [False, True], 'prefix orientation')
            payload = (1 << (6 * (pairs - 1))) * forward ** (pairs + 1) * backward ** pairs
            report['bridged_payload_upper'] = str(payload)
            report['bridged_payload_bits'] = payload.bit_length()
            if stages == 9:
                need(payload < 1 << 192, 'strict nine-stage precision cap')
            staged[str(stages)] = report
        reports[name] = {'invoice': invoice, 'native_geometry': legality, 'staged_scalar': staged}
        print('NATIVE_HELPER470', name, invoice['ADDs'], invoice['rank_mass'], flush=True)
    for name in ('retired', 'closed'):
        changed = [r for r in paths['baseline'] if paths['baseline'][r] != paths[name][r]]
        need(changed == [470], 'unexpected per-register MOVE itinerary')
    return reports


def negative_controls(output):
    """Actual record faults tested by the unchanged binaries, not just the driver."""
    root = output / 'controls'
    root.mkdir()
    answers = []

    def rows(name):
        return list(struct.iter_unpack('<6i', (output / name / 'cout/COHORT249-RECORDS.bin').read_bytes()))

    def locate(stream, record):
        found = [i for i, item in enumerate(stream) if item == record]
        need(len(found) == 1, 'unique negative-control record')
        return found[0]

    def check(name, source, stream, checker, reason, scalar_also_passes=False):
        folder = root / name
        folder.mkdir()
        record = folder / 'COHORT249-RECORDS.bin'
        record.write_bytes(b''.join(struct.pack('<6i', *r) for r in stream))
        if checker == 'geometry':
            for filename in ('COHORT249-FRAMES.json', 'COHORT249-INITIAL.json', 'COHORT249-SELECTION.json'):
                (folder / filename).write_bytes((output / source / 'cout' / filename).read_bytes())
            argv = [output / 'legality', output / source / 'cin', folder, folder / 'legality.json']
        else:
            argv = [output / 'columns-4', record, folder / 'columns.json']
        completed = subprocess.run([str(x) for x in argv], capture_output=True, text=True, timeout=60)
        need(completed.returncode != 0 and reason in completed.stderr, 'native control did not reject: ' + name)
        (folder / 'rejection.log').write_text(completed.stdout + completed.stderr)
        if scalar_also_passes:
            execute([output / 'columns-4', record, folder / 'scalar-pass.json'], folder / 'scalar-pass.log')
        answers.append({'name': name, 'checker': checker, 'reason': reason,
                        'rejected': True, 'scalar_columns_still_pass': scalar_also_passes})

    for name, record in (
            ('omit-restoration', (1, 470, 77, 1, 186, 4)),
            ('omit-clear-444', (1, 444, 470, 1, 513, 4)),
            ('omit-clear-475', (1, 475, 470, 1, 513, 4))):
        stream = rows('retired')
        del stream[locate(stream, record)]
        check(name, 'retired', stream, 'scalar', 'local defining-decoder full formal column')
    stream = rows('retired')
    i = locate(stream, (1, 444, 77, 1, 1, 5))
    stream[i] = (1, 444, 470, 1, 1, 5)
    check('wrong-cleanup-donor', 'retired', stream, 'scalar', 'local defining-decoder full formal column')
    stream = rows('retired')
    i = locate(stream, (1, 470, 77, 1, 186, 4))
    stream[i] = (1, 470, 77, 1, 0, 4)
    check('wrong-restoration-frame', 'retired', stream, 'geometry', 'ADD not in common frame', True)
    stream = rows('closed')
    i = locate(stream, (0, 470, 513, 1, 1, 0))
    stream[i] = (0, 470, 513, 1, 0, 0)
    check('underpriced-terminal-move', 'closed', stream, 'geometry', 'illegal or mispriced MOVE', True)
    stream = rows('closed')
    del stream[locate(stream, (0, 470, 513, 1, 1, 0))]
    check('omit-full-terminal-move', 'closed', stream, 'geometry', 'final frame', True)
    stream = rows('retired')
    i = next(i for i, item in enumerate(stream) if item[0] == 2)
    r = list(stream[i])
    r[5] -= 1
    stream[i] = tuple(r)
    check('underpriced-retained-copy', 'retired', stream, 'geometry', 'COPY rank', True)
    return answers


def local_evidence(root):
    source_pins(root)
    prefix_contract(root)
    word = load(root / WORD)
    words = {'baseline': word, 'retired': candidate(word), 'closed': candidate(word, True)}
    module = owning_checker(root)
    local = {name: local_check(w, module) for name, w in words.items()}
    need(all(local['baseline']['hypotheses'].values()), 'baseline H1-H5')
    for name in ('retired', 'closed'):
        h = local[name]['hypotheses']
        need([key for key, value in h.items() if not value] == ['H4_C_literal_reverse_at_full'], 'precise H4 boundary')
        need(all(local[name]['conclusion'].values()), 'semantic interleaved conclusion')
    # Keep the original owning full-frame condition: record its actual rejection.
    rejected = None
    try:
        module.Word(words['retired']).full()
    except module.Reject as error:
        rejected = str(error)
    need(rejected == 'helper final frame is not full', 'owning terminal contract rejection')
    module.Word(words['baseline']).full()
    module.Word(words['closed']).full()
    need(local['retired']['nonfull_helpers'] == [470] and not local['closed']['nonfull_helpers'],
         'exact terminal helper boundary')
    return words, {'words': {name: digest(w) for name, w in words.items()}, 'local': local,
                   'owning_retired_full_rejection': rejected}


def run(root, output, boost):
    words, evidence = local_evidence(root)
    reports = native(root, output, words, boost)
    controls = negative_controls(output)
    expected_counts = {'baseline': (24305, 2911, 5129, 2920), 'retired': (24307, 2912, 5128, 2921),
                       'closed': (24307, 2913, 5129, 2922)}
    for name, counts in expected_counts.items():
        inv = reports[name]['invoice']
        need(tuple(inv[key] for key in ('ADDs', 'MOVEs', 'rank_mass', 'children')) == counts, 'expected complete invoice')
    profiles = {name: report['invoice']['profile'] for name, report in reports.items()}
    deltas = {name: profile_delta(profiles['baseline'], profiles[name]) for name in ('retired', 'closed')}
    need(deltas == {'retired': {'1': 1, '5': 1, '7': -1},
                    'closed': {'1': 2, '5': 1, '7': -1}}, 'exact endpoint profile deltas')
    return {'status': 'PASS_HELPER470_NATIVE_SCALAR_AND_ENDPOINT_AUDIT', 'assignment_seed': 12,
        'predecessor': {'pr': 1256, 'head': 'd6d5a994fcdcd8d04ec439ff988daa8f37b17ece'},
        **evidence, 'native': reports, 'profile_deltas': deltas,
        'negative_controls': controls,
        'scope': 'Finite exported-record geometry and F2 staged scalar columns. The native legality receipt contains an inherited bank-audit flag; this package does not run that separate bank audit or hosted projector routing. H4 remains false for both modified words.',
        'no_new_kappa': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--boost', type=Path, default=Path(os.environ.get('BOOST_INCLUDE', '/usr/include')))
    parser.add_argument('--emit', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--local-only', action='store_true', help='check only the named scalar/interface/source evidence; no native claim')
    args = parser.parse_args()
    if args.local_only:
        need(not args.emit and not args.output, '--local-only cannot emit native receipts')
        _, evidence = local_evidence(args.root.resolve())
        expected = load(HERE / 'CERTIFICATE.json')
        need(evidence == {key: expected[key] for key in evidence}, 'complete local evidence mismatch')
        print('PASS_HELPER470_LOCAL_BOUNDARY columns=661 words=3 H4_open no_new_kappa')
        return
    need((args.boost / 'boost/multiprecision/cpp_int.hpp').is_file(), 'Boost headers: set BOOST_INCLUDE or --boost')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        result = run(args.root.resolve(), args.output.resolve(), args.boost.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='helper470-native-') as folder:
            result = run(args.root.resolve(), Path(folder), args.boost.resolve())
    if args.emit:
        with args.emit.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        need(result == load(HERE / 'CERTIFICATE.json'), 'complete certificate mismatch')
    print('PASS_HELPER470_NATIVE stages=5,9,11 words=3 retired_mass=5128 closed_mass=5129 H4_open no_new_kappa')


if __name__ == '__main__':
    main()
