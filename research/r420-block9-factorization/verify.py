#!/usr/bin/env python3
"""Verify one finite R420 circuit replacement and its complete local bill.

No search is run. Predecessor and selected-frontier files are read unchanged.
New code: Apache-2.0; substantial OpenAI Codex assistance.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
BIT = ROOT / 'research/e8-bit-carrier-skeleton/code/bit'
CHECKERS = BIT / 'checkers'
BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
REGISTERS = [8, 13, 33, 39, 42, 47, 80, 85, 88, 94, 114, 119]


class Reject(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_pins(pins):
    need(pins['base_commit'] == BASE, 'base pin')
    for name, expected in pins['files'].items():
        path = ROOT / name
        need(path.resolve().is_relative_to(ROOT), 'source outside repository')
        raw = path.read_bytes()
        need(digest(raw) == expected['sha256'], 'source pin: ' + name)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == expected['git_blob'], 'git blob pin: ' + name)


def matrix(ops, sign=1):
    rows = [[int(i == j) for j in range(12)] for i in range(12)]
    for a, b in ops:
        rows[a] = [x + sign * y for x, y in zip(rows[a], rows[b])]
    return rows


def product(left, right):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*right)] for row in left]


def at_most(left, right):
    return all(a <= b for x, y in zip(left, right) for a, b in zip(x, y))


def strict_entries(left, right):
    return sum(a < b for x, y in zip(left, right) for a, b in zip(x, y))


def check_candidate(original, candidate):
    need(candidate['format'] == 'r420-block9-positive-factorization-v1', 'candidate format')
    need(candidate['base_commit'] == BASE and candidate['source_sha256'] == digest(WORD.read_bytes()), 'candidate source')
    need(candidate['slice'] == [559, 597] and candidate['frame'] == 551 and candidate['block_index'] == 9, 'block location')
    need(candidate['registers'] == REGISTERS, 'physical register assignment')
    old = []
    for frame, dst, sources in original['B'][559:597]:
        need(frame == 551 and len(sources) == 1, 'source block shape')
        old.append([REGISTERS.index(dst), REGISTERS.index(sources[0])])
    need(old == candidate['original_operations'], 'original circuit pin')
    ops = candidate['operations']
    need(isinstance(ops, list) and len(ops) < len(old), 'no gate improvement')
    for gate in ops:
        need(isinstance(gate, list) and len(gate) == 2, 'gate shape')
        a, b = gate
        need(type(a) is int and type(b) is int and 0 <= a < 12 and 0 <= b < 12 and a != b, 'gate operands')
    old_f, new_f = matrix(old), matrix(ops)
    need(new_f == old_f, 'integer forward equality')
    old_r, new_r = matrix(old[::-1]), matrix(ops[::-1])
    need(at_most(new_r, old_r), 'reverse positive domination')
    inv = matrix(ops[::-1], -1)
    need(inv == matrix(old[::-1], -1), 'signed inverse equality')
    need(product(inv, new_f) == matrix([]), 'signed inverse identity')
    old_round, new_round = product(old_r, old_f), product(new_r, new_f)
    need(at_most(new_round, old_round), 'round trip positive domination')
    return {
        'gates_before': len(old), 'gates_after': len(ops),
        'saved_with_cleanup': 2 * (len(old) - len(ops)),
        'integer_forward_matrix': new_f, 'integer_signed_inverse_matrix': inv,
        'original_reverse_majorant': old_r, 'replacement_reverse_majorant': new_r,
        'strict_reverse_entries': strict_entries(new_r, old_r),
        'strict_round_trip_entries': strict_entries(new_round, old_round),
        'unit_round_trip_bound_before': max(map(sum, old_round)),
        'unit_round_trip_bound_after': max(map(sum, new_round)),
    }


def rebuild(original, candidate):
    word = copy.deepcopy(original)
    word['B'][559:597] = [[551, REGISTERS[a], [REGISTERS[b]]] for a, b in candidate['operations']]
    word['C'] = [[1, d, sources[:]] for _, d, sources in reversed(word['A'] + word['B'])
                 if not word['v'] <= d < 2 * word['v']]
    return word


def command(args, out, name):
    with (out / (name + '.stdout')).open('w') as stdout, (out / (name + '.stderr')).open('w') as stderr:
        environment = dict(os.environ, TMPDIR=str(out), OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
        result = subprocess.run([str(a) for a in args], cwd=ROOT, stdout=stdout, stderr=stderr, env=environment)
    need(result.returncode == 0, f'{name} failed; see {out / (name + ".stderr")}')


def native(xcheck, word):
    checker, labels, full, hypotheses, conclusion, _ = xcheck.check(word)
    need(all(hypotheses.values()) and all(conclusion.values()), 'native interface')
    return checker, {'labels': labels, 'full': full, 'hypotheses': hypotheses, 'conclusion': conclusion}


def control_suite(original, candidate, word, checker, xcheck, records, audit):
    passed = []

    def rejected(name, operation, reason):
        try:
            operation()
        except (Reject, xcheck.Reject, ValueError) as error:
            need(reason in str(error), f'{name}: wrong rejection: {error}')
            passed.append(name)
        else:
            raise Reject('negative control accepted: ' + name)

    def candidate_mutation(name, edit, reason):
        changed = copy.deepcopy(candidate)
        edit(changed)
        rejected(name, lambda: check_candidate(original, changed), reason)

    candidate_mutation('bad_source_pin', lambda c: c.update(source_sha256='0' * 64), 'candidate source')
    candidate_mutation('new_register', lambda c: c['operations'][0].__setitem__(0, 12), 'gate operands')
    candidate_mutation('self_xor', lambda c: c['operations'][0].__setitem__(1, c['operations'][0][0]), 'gate operands')
    candidate_mutation('omitted_block_gate', lambda c: c['operations'].pop(), 'integer forward equality')
    candidate_mutation('wrong_output_assignment', lambda c: c['registers'].reverse(), 'physical register assignment')
    neutral = copy.deepcopy(candidate)
    neutral['operations'] = [neutral['operations'][0]] * 2 + neutral['operations']
    need([[x % 2 for x in row] for row in matrix(neutral['operations'])] ==
         [[x % 2 for x in row] for row in matrix(candidate['operations'])], 'neutral control F2 precondition')
    rejected('F2_neutral_positive_inflation', lambda: check_candidate(original, neutral), 'integer forward equality')
    unsafe = candidate['reverse_domination_negative_control']['operations']
    need(matrix(unsafe) == matrix(candidate['operations']), 'reverse control integer precondition')
    need(not at_most(matrix(unsafe[::-1]), matrix(candidate['original_operations'][::-1])), 'reverse control precondition')
    unsafe_candidate = copy.deepcopy(candidate)
    unsafe_candidate['operations'] = unsafe
    rejected('integer_equal_but_reverse_inflated', lambda: check_candidate(original, unsafe_candidate),
             'reverse positive domination')

    def word_test(changed, interface=False):
        local = copy.copy(checker)
        local.w = changed
        local.full()
        if interface:
            h, c, _ = local.interface()
            need(all(h.values()) and all(c.values()), 'literal cleanup interface')

    changed = copy.deepcopy(word)
    changed['B'][559][2][0] = REGISTERS[0]
    changed['C'] = [[1, d, ss[:]] for _, d, ss in reversed(changed['A'] + changed['B'])
                    if not changed['v'] <= d < 2 * changed['v']]
    # Matching cleanup still restores the z registers; the target map is wrong.
    rejected('wrong_B_with_matching_cleanup', lambda: word_test(changed), 'targets not y + x')
    changed = copy.deepcopy(word)
    changed['C'].pop()
    rejected('omitted_cleanup', lambda: word_test(changed), 'not restored')
    changed = copy.deepcopy(word)
    changed['C'] = copy.deepcopy(original['C'])
    word_test(changed)  # Deliberately F2-correct, but not the claimed H4 boundary.
    rejected('stale_cleanup_interface', lambda: word_test(changed, True), 'literal cleanup interface')
    changed = copy.deepcopy(word)
    changed['B'][559][0] = 0
    rejected('illegal_zero_frame', lambda: word_test(changed), 'climb not nested')
    changed = copy.deepcopy(word)
    changed['D'][0][2].pop()
    rejected('missing_dirty_compensation', lambda: word_test(changed), 'targets not y + x')
    events = list(struct.iter_unpack('<6i', records))
    without_erase = events[:]
    del without_erase[next(i for i, e in enumerate(events) if e[0] == 3)]
    rejected('missing_ERASE', lambda: audit.interpret(without_erase, 660, 120, False), 'COPY lifecycle')
    changed_records = [list(e) for e in events]
    index = next(i for i, e in enumerate(events) if e[0] == 0)
    changed_records[index][4] += 1
    changed_bytes = b''.join(struct.pack('<6i', *e) for e in changed_records)
    rejected('wrong_paid_MOVE_rank', lambda: audit.audit(word, changed_bytes), 'exported record stream')
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    next(iter(pins['files'].values()))['sha256'] = '0' * 64
    rejected('bad_dependency_pin', lambda: check_pins(pins), 'source pin:')
    return passed


def verify(out, cxx):
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    check_pins(pins)
    original = json.loads(gzip.decompress(WORD.read_bytes()))
    candidate = json.loads((HERE / 'CANDIDATE.json').read_text())
    local = check_candidate(original, candidate)
    word = rebuild(original, candidate)
    need(all(word[k] == original[k] for k in original if k not in ['B', 'C']), 'exterior changed')
    need(word['B'][:559] == original['B'][:559] and word['B'][583:] == original['B'][597:], 'B exterior changed')
    word_path = out / 'word.json.gz'
    word_path.write_bytes(gzip.compress(canonical(word), mtime=0))
    xcheck = module(ROOT / 'research/e8-bit-r420/code/xcheck.py', 'predecessor_xcheck')
    audit = module(HERE / 'record_audit.py', 'block9_record_audit')
    receipts, paths, native_reports = {}, {}, {}
    print('Checking exact native maps, all dirty input columns, and physical frames...', flush=True)
    for name, w, path in [('original', original, WORD), ('replacement', word, word_path)]:
        destination = out / name
        destination.mkdir()
        checker, report = native(xcheck, w)
        native_reports[name] = report
        if name == 'replacement':
            new_checker = checker
        command([sys.executable, '-I', '-B', BIT / 'export_records.py', path, destination / 'records'], out, name + '-export')
        command([sys.executable, '-I', '-B', BIT / 'regression/stage_cohort.py', destination / 'records',
                 destination / 'records', destination / 'cin', destination / 'cout'], out, name + '-stage')
        raw = (destination / 'records/249-records.bin').read_bytes()
        receipts[name], paths[name] = audit.audit(w, raw)
    need(paths['original'] == paths['replacement'], 'per-register frame paths changed')
    expected_profile = {'1': 1320, '2': 1440, '4': 60, '5': 120, '8': 9}
    need(all(r['rank_profile'] == expected_profile and r['rank_mass'] == 5112 for r in receipts.values()), 'paid profile')
    controls = control_suite(original, candidate, word, new_checker, xcheck,
                             (out / 'replacement/records/249-records.bin').read_bytes(), audit)
    print(f'PASS_NATIVE_AND_CONTROLS controls={len(controls)}; compiling cohort checkers sequentially...', flush=True)
    common = [cxx, '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=120', '-DRHELP=420',
              '-I' + str(CHECKERS), '-I' + str(ROOT / 'research/e8-bit-carrier-skeleton/portable-include')]
    binary = out / 'legality'
    command(common + ['-o', binary, CHECKERS / 'legality_h.cpp'], out, 'compile-legality')
    legality = {}
    for name in receipts:
        destination = out / name
        command([binary, destination / 'cin', destination / 'cout', destination / 'legality.json'], out, name + '-legality')
        report = json.loads((destination / 'legality.json').read_text())
        need(report['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE', 'cohort legality')
        need(report['copies'] == report['erasures'] == 9 and report['rank_mass'] == 5112, 'cohort lifecycle or rank mass')
        legality[name] = {k: report[k] for k in ['status', 'records', 'common_frame_ADDs', 'rank_mass', 'copies', 'erasures']}
    cohort = {}
    for pairs in [2, 4, 5]:
        stages = 2 * pairs + 1
        binary = out / f'columns_k{pairs}'
        command(common + [f'-DKPAIRS={pairs}', '-o', binary, CHECKERS / 'columns_k.cpp'], out, f'compile-k{pairs}')
        cohort[str(stages)] = {}
        for name, native_receipt in receipts.items():
            destination = out / name
            report_path = destination / f'columns_k{pairs}.json'
            command([binary, destination / 'cout/COHORT249-RECORDS.bin', report_path], out, name + f'-k{pairs}')
            report = json.loads(report_path.read_text())
            need(report['status'].startswith('PASS_NEW_COHORT249_ALL_'), 'column status')
            need(report['formal_columns_checked'] == 2 * pairs * 120 + 420, 'column coverage')
            need(len(report['negative_controls']) == 6 * (pairs - 1) and
                 all(c['rejected'] for c in report['negative_controls']), 'bridge negative controls')
            need(report['local_scalar_additions'] == native_receipt['directions'][0]['additions'], 'independent ADD count')
            for got, expected in zip(report['signed_lift_prefix'], native_receipt['directions']):
                need(int(got['cancellation_free_signed_row_l1_upper']) == expected['norm_bound'], 'independent prefix bound')
            need(dict((str(k), v) for k, v in report['local_raw_H']) == expected_profile, 'independent paid profile')
            report.pop('seconds')
            report.pop('local_scalar_stream')
            cohort[str(stages)][name] = report
        print(f'PASS_COHORT stages={stages} columns={2 * pairs * 120 + 420} controls={6 * (pairs - 1)}', flush=True)
    budgets = {}
    for name, receipt in receipts.items():
        forward, reverse = [d['norm_bound'] for d in receipt['directions']]
        five = 64 * forward ** 3 * reverse ** 2
        nine = 2 ** 18 * forward ** 5 * reverse ** 4
        budgets[name] = {'five_stage_prefix_upper': str(five), 'five_stage_prefix_bits': five.bit_length(),
                         'nine_stage_prefix_upper': str(nine), 'nine_stage_prefix_bits': nine.bit_length(),
                         'nine_stage_charged_prefix_bits': ((nine.bit_length() + 63) // 64) * 64}
    need(receipts['original']['directions'][0]['additions'] == 26916, 'baseline ADD receipt')
    need(receipts['replacement']['directions'][0]['additions'] == 26888, 'replacement ADD receipt')
    need(receipts['original']['directions'][0]['norm_bound'] == 144651 and
         receipts['original']['directions'][1]['norm_bound'] == 2270064, 'baseline prefix receipt')
    assembly = json.loads((ROOT / 'research/community-k492-audit/pr626/replay/ASSEMBLY.json').read_text())
    return {
        'status': 'PASS_R420_BLOCK9_FACTORIZATION', 'base_commit': BASE,
        'candidate_sha256': digest(canonical(candidate)),
        'word_canonical_sha256': {'original': digest(canonical(original)), 'replacement': digest(canonical(word))},
        'block': local, 'native': native_reports, 'records': receipts, 'legality': legality,
        'cohort': cohort, 'prefix_budgets': budgets, 'negative_controls': controls,
        'selected_context_only': {'kappa': assembly['kappa'], 'binding': assembly['binding']},
        'scope': 'Finite block and native/cohort certificates only; no hosted invoice, new supplier exponent, or full multiplication theorem.',
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, help='fresh directory for replay evidence (default: unique directory under build/)')
    ap.add_argument('--write-certificate', action='store_true', help='maintainer operation: regenerate this package certificate')
    ap.add_argument('--cxx', default='c++')
    args = ap.parse_args()
    need(not sys.flags.optimize, 'run without -O')
    need(shutil.which(args.cxx) is not None, 'C++17 compiler not found')
    if args.output is None:
        build = ROOT / 'build'
        build.mkdir(exist_ok=True)
        out = Path(tempfile.mkdtemp(prefix='r420-block9-', dir=build))
    else:
        out = args.output.resolve()
        out.mkdir(parents=True, exist_ok=False)
    result = verify(out, args.cxx)
    rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
    (out / 'verification.json').write_text(rendered)
    environment = {'python': sys.version, 'platform': platform.platform(),
                   'compiler': subprocess.check_output([args.cxx, '--version'], text=True).splitlines()[0]}
    (out / 'environment.json').write_text(json.dumps(environment, indent=2) + '\n')
    if args.write_certificate:
        (HERE / 'CERTIFICATE.json').write_text(rendered)
    else:
        need(result == json.loads((HERE / 'CERTIFICATE.json').read_text()), 'certificate mismatch')
    print('Evidence:', out)
    print('PASS_R420_BLOCK9_FACTORIZATION gates=38->24 native_adds=26916->26888 columns=660/900/1380/1620 rank_mass=5112')


if __name__ == '__main__':
    try:
        main()
    except (Reject, ValueError) as error:
        print('REJECT:', error, file=sys.stderr)
        raise SystemExit(1)
