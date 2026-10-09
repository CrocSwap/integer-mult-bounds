#!/usr/bin/env python3
"""Import harness for the normalizer export contract.

`export-contract.json` says what the complex supplier's program must publish for C1-C3 to become
a bank increment. This module is its executable form: it consumes the exports, runs the seven
acceptance tests with their bounds, and -- today, when no body exists -- refuses cleanly instead
of certifying anything.

Two layers, and the difference between them is the point of the module.

* **The gate** is decidable from what the bodies declare: the hashes (A1), the cardinalities
  (A2, and A5's item counts), the published bounds (A3's denominators, A6's colouring, A7's prime
  threshold), the bijections (A2's id map, and A5 against this package's own `occurrences66.json`)
  and the counts that must come out of the exported tables rather than out of the certificate
  (A4).  Every gate check is exercised by `--self-test`, which builds synthetic bodies, patches
  the anchored digests to the synthetic hashes and then breaks each check in turn: the harness is
  proven to work, and to reject, while the real bodies are absent.
* **The replay** is the physics: the formal columns over F2 and over the defining integers, the
  fraction-free chart replay, the moment envelope re-derived.  This module does not reimplement
  any of it and never claims to have run it.  The contract pins the digest of the supplier's own
  checker (`E3` -> `lift.checker_sha256`), so the harness *requires that checker* by digest and
  reports the replay as NOT RUN until it is supplied.  A digest match is identity, not
  correctness -- the contract says so, and so does this module.

Exit codes (also published in the contract under `import_harness.exit_codes`)

    0  admissible: every body present, the gate green and the pinned replay checker passed
    1  a check failed (the report names the test, its bound and what was seen)
    2  refusing: at least one required body is absent, so nothing is run and nothing is certified
    3  gate green but the replay was not run (no checker supplied)
"""
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
CONTRACT = HERE / 'export-contract.json'
OURS = HERE / 'occurrences66.json'

PASS, FAIL, NOT_RUN = 'PASS', 'FAIL', 'NOT_RUNNABLE'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    """A body, decompressed if it is gzipped.  Digests are always of the published bytes."""
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw.decode('utf-8'))


def walk(node, dotted):
    """Follow a dotted path through a body, or raise KeyError."""
    for key in dotted.split('.'):
        node = node[key]
    return node


def refusal(contract, exports_dir):
    """The bodies the contract waits for, split into present and absent."""
    rows, missing = [], []
    for export in contract['required_exports']:
        for body in export['bodies']:
            path = Path(exports_dir) / body['file']
            rows.append(dict(export=export['id'], file=body['file'], path=path,
                             anchored=body.get('anchored_digest')))
            if not path.is_file():
                missing.append((export['id'], body['file']))
    return rows, missing


def gate(contract, exports_dir):
    """Every check decidable from the bodies that declare it.  Returns per-test results."""
    results = {test['id']: dict(test=test['id'], name=test['name'], status=NOT_RUN,
                                checks=[], reason=None, passed=0, failed=0)
               for test in contract['acceptance_tests']}

    def record(test, ok, detail):
        entry = results[test]
        entry['checks'].append(detail)
        entry['passed' if ok else 'failed'] += 1

    def need(test, reason):
        entry = results[test]
        if entry['reason'] is None:              # the first missing datum explains the state
            entry['reason'] = reason

    def settle():
        """A test is FAIL if a check failed, NOT_RUNNABLE if a datum was missing, else PASS."""
        for entry in results.values():
            if entry['failed']:
                entry['status'] = FAIL
            elif entry['reason'] is not None:
                entry['status'] = NOT_RUN
            elif entry['passed']:
                entry['status'] = PASS

    rows, _missing = refusal(contract, exports_dir)
    bodies = {}
    for row in rows:
        try:
            bodies[row['file']] = load(row['path'])
        except (json.JSONDecodeError, gzip.BadGzipFile, OSError, UnicodeDecodeError) as exc:
            record('A1', False, '%s is not readable as a body: %s' % (row['file'], exc))

    # A1 -- every anchored digest is the digest of the published bytes, and the integrity
    # manifest agrees with the files it lists.
    anchored = [row for row in rows if row['anchored']]
    for row in anchored:
        seen = sha256(row['path'])
        record('A1', seen == row['anchored'],
               'A1 %s hashes %s, contract anchors %s' % (row['file'], seen[:16], row['anchored'][:16]))
    integrity = bodies.get('integrity.json')
    if integrity is None:
        need('A1', 'integrity.json is absent, so no body is declared and nothing is self-checked')
    else:
        declared = integrity.get('files', {})
        for row in rows:
            if row['file'] == 'integrity.json':
                continue
            seen = sha256(row['path'])
            record('A1', declared.get(row['file']) == seen,
                   'A1 integrity declares %s = %s' % (row['file'], str(declared.get(row['file']))[:16]))

    # A2..A7 -- the declared gate of each export.
    for export in contract['required_exports']:
        declared = export['gate']
        tests = declared['test']
        subject = export['bodies'][0]['file']     # an export's declared checks are its primary
        fields = [(subject, declared.get('equals', {}))]        # body's, unless named in `_on`
        fields += [(body['file'], declared.get('equals_on', {}).get(body['file'], {}))
                   for body in export['bodies'][1:]]
        for file_name, scope in fields:
            body = bodies.get(file_name)
            if body is None:
                for test in tests:
                    need(test, '%s is absent' % file_name)
                continue
            for test in tests:
                extra = declared if file_name == subject else {}    # flags, bijections, witnesses
                for dotted, expected in scope.items():
                    try:
                        seen = walk(body, dotted)
                    except (KeyError, TypeError):
                        need(test, '%s has no %s' % (file_name, dotted))
                        continue
                    record(test, seen == expected, '%s %s.%s = %r, bound %r'
                           % (test, file_name, dotted, seen, expected))
                if file_name == declared.get('declares_every_body_on'):
                    # every required body except the manifest itself, whose digest cannot sit
                    # inside the file it would be a digest of
                    wanted = {row['file'] for group in contract['required_exports']
                              for row in group['bodies']} - {file_name}
                    declared_files = set(body.get('files', {}))
                    record(test, wanted <= declared_files,
                           '%s %s declares %d of the %d other required bodies'
                           % (test, file_name, len(wanted & declared_files), len(wanted)))
                for dotted in extra.get('bijection', []):
                    try:
                        seen = walk(body, dotted)
                    except (KeyError, TypeError):
                        need(test, '%s has no %s' % (file_name, dotted))
                        continue
                    keys = [str(k) for k in seen]
                    values = [str(v) for v in seen.values()]
                    ok = len(set(keys)) == len(keys) and len(set(values)) == len(values)
                    record(test, ok, '%s %s.%s is a bijection on %d ids' % (test, file_name, dotted, len(keys)))
                for flag in extra.get('flags_true', []):
                    try:
                        seen = walk(body, flag)
                    except (KeyError, TypeError):
                        need(test, '%s has no %s' % (file_name, flag))
                        continue
                    record(test, seen is True, '%s %s.%s = %r, must be true' % (test, file_name, flag, seen))
                for flag in extra.get('flags_present', []):
                    ok = flag in body
                    record(test, ok, '%s %s.%s is present' % (test, file_name, flag))
                if 'distinct_below' in extra:
                    spec = extra['distinct_below']
                    try:
                        witnesses = walk(body, spec['witnesses'])
                        bound = walk(body, spec['bound'])
                    except (KeyError, TypeError):
                        need(test, '%s has no %s or %s' % (file_name, spec['witnesses'], spec['bound']))
                        continue
                    labels = [w['witness'] if isinstance(w, dict) else w for w in witnesses]
                    factors = [w['residual_factor'] for w in witnesses if isinstance(w, dict)]
                    ok = len(set(labels)) == len(labels) and all(f < bound for f in factors)
                    record(test, ok, '%s %s: %d witnesses, distinct %s, all factors below %r'
                           % (test, file_name, len(labels), len(set(labels)) == len(labels), bound))
                if 'counted_in_tables' in extra:
                    for table, field in extra['counted_in_tables'].items():
                        rows_in_tables = sum(len(t.get(table, [])) for t in body.get('tables', []))
                        try:
                            claimed = walk(body, field)
                        except (KeyError, TypeError):
                            need(test, '%s has no %s' % (file_name, field))
                            continue
                        record(test, rows_in_tables == claimed,
                               '%s %s: %d rows come out of the tables, certificate claims %r'
                               % (test, file_name, rows_in_tables, claimed))

    # A5's bijection is against our own table, not against a declared one.
    if 'occurrences.complex.json' in bodies:
        ours = json.loads(OURS.read_text())
        theirs = bodies['occurrences.complex.json']
        families = theirs.get('families')
        if families is None:
            need('A5', 'occurrences.complex.json has no families')
        else:
            allowed = set(contract['required_exports'][4]['gate']['bins_allowed'])
            record('A5', set(map(str, families)) <= allowed,
                   'A5 bins %s are within %s' % (sorted(map(str, families)), sorted(allowed)))
            for rank, ours_row in ours['inventories'].items():
                mine = {key: ours_row[key] for key in ('items', 'banks', 'capacity_per_bank',
                                                       'children_per_vertex', 'padding_per_bank',
                                                       'bank_table_digest')}
                their_row = families.get(rank) or families.get(str(rank))
                if their_row is None:
                    record('A5', False, 'A5 family %s is missing from the export' % rank)
                    continue
                record('A5', all(their_row.get(key) == value for key, value in mine.items()),
                       'A5 family %s matches this package: %s' % (rank, sorted(mine)))
    else:
        need('A5', 'occurrences.complex.json is absent')

    for entry in results.values():
        if entry['reason'] is None and not entry['passed'] and not entry['failed']:
            entry['reason'] = 'no body declares this test yet'
    settle()
    return results


def run(contract, exports_dir, checker=None):
    """The whole import: refusal, gate, replay.  Returns (exit code, report)."""
    rows, missing = refusal(contract, exports_dir)
    report = dict(exports_dir=str(exports_dir), bodies=[row['file'] for row in rows],
                  missing=['%s: %s' % pair for pair in missing], tests={}, replay=None)
    if missing:
        report['verdict'] = 'REFUSED: %d of %d required bodies are absent and nothing is run' % (
            len(missing), len(rows))
        return 2, report
    results = gate(contract, exports_dir)
    report['tests'] = {key: dict(status=value['status'], reason=value['reason'],
                                 checks=value['checks']) for key, value in results.items()}
    failed = sorted(key for key, value in results.items() if value['status'] == FAIL)
    if failed:
        report['verdict'] = 'FAILED: %s' % ', '.join(failed)
        return 1, report
    incomplete = sorted(key for key, value in results.items() if value['status'] == NOT_RUN)
    if incomplete:
        report['replay'] = dict(status='NOT RUN', reason='the gate cannot decide these tests')
        report['verdict'] = 'GATE INCOMPLETE: %s could not be run, so nothing may be discharged' \
                            % ', '.join(incomplete)
        return 3, report
    pinned_checker = contract['import_harness']['replay_requirement']['checker_digest']
    if checker is None:
        report['replay'] = dict(status='NOT RUN', reason='no checker supplied',
                                required='a checker whose sha256 is the digest E3 pins')
        report['verdict'] = 'GATE GREEN, REPLAY NOT RUN: the physics is not verified and no ' \
                            'obligation may be discharged on this import alone'
        return 3, report
    seen = sha256(checker)
    report['replay'] = dict(status='RUN' if seen == pinned_checker else 'REFUSED',
                            checker=str(checker), checker_sha256=seen, pinned=pinned_checker)
    if seen != pinned_checker:
        report['verdict'] = 'REFUSED: the checker is not the one the contract pins'
        return 2, report
    done = subprocess.run([sys.executable, '-B', str(checker), str(exports_dir)],
                          capture_output=True, text=True)
    report['replay'].update(returncode=done.returncode, tail=done.stdout[-500:])
    if done.returncode:
        report['verdict'] = 'FAILED: the pinned replay checker rejected the exports'
        return 1, report
    report['verdict'] = 'ADMISSIBLE: gate green and the pinned replay checker passed'
    return 0, report


def synthetic(directory):
    """A minimal set of bodies that satisfies the gate, for the self-test."""
    out = Path(directory)

    def write(name, payload, compress=False):
        raw = json.dumps(payload, sort_keys=True).encode('utf-8')
        if compress:
            raw = gzip.compress(raw)
        (out / name).write_bytes(raw)

    write('program.json', {'nodes': 18532, 'inverse_elementary_gates': 58165})
    write('frames.json', {'frames': 18532, 'vectors': 26200, 'edge_basis_values': 42787,
                          'id_map': {'0': 0, '1': 1, '2': 2},
                          'conflicting_assignment_rejected': True,
                          'color_stats': {'swaps': 733, 'longest_swapped_path': 11},
                          'q_bound': 10 ** 80,
                          'prime_witnesses': [{'witness': 7, 'residual_factor': 3},
                                              {'witness': 11, 'residual_factor': 5}]})
    write('graph.json', {'incoming_dependencies': 24, 'outgoing_dependencies': 8116})
    write('record.json', {'provenance': 'synthetic'})
    write('lift.certificate.json.gz', {'nodes': 18532, 'physical_R': 9412,
                                       'max_denominator': 2, 'max_abs_numerator': 2},
          compress=True)
    write('flow.witness.json', {'monotone': True})
    write('chronology.json', {'tables': [{'target_rows': [0] * 1320, 'source_columns': [0] * 1320}],
                              'checked_source_columns': 1320, 'checked_target_rows': 1320,
                              'read_counts': {'center': 22, 'deferred': 2310, 'side': 3135}})
    ours = json.loads(OURS.read_text())
    families = {}
    for rank, row in ours['inventories'].items():
        families[rank] = {key: row[key] for key in ('items', 'banks', 'capacity_per_bank',
                                                   'children_per_vertex', 'padding_per_bank',
                                                   'bank_table_digest')}
    write('occurrences.complex.json', {'families': families})
    write('envelope.json', {'W_per_vertex': 12052, 'deficit_per_vertex': 1320, 'h': 22, 'v': 1320})
    write('integrity.json', {'files': {name: sha256(out / name)
                                       for name in sorted(p.name for p in out.iterdir())}})
    return out


def self_test(contract):
    """Prove the harness works and rejects, on synthetic bodies, while no real body exists."""
    observed = {}

    def fresh(directory):
        synthetic(directory)
        patched = json.loads(json.dumps(contract))
        for export in patched['required_exports']:
            for body in export['bodies']:
                path = Path(directory) / body['file']
                if body.get('anchored_digest') is not None or path.is_file():
                    if body.get('anchored_digest') is not None or body['file'] in (
                            'occurrences.complex.json', 'chronology.json', 'envelope.json',
                            'integrity.json'):
                        if body.get('anchored_digest') is not None:
                            body['anchored_digest'] = sha256(path)
        return patched

    def code(patched, directory, checker=None):
        return run(patched, directory, checker)[0]

    with tempfile.TemporaryDirectory() as tmp:
        patched = fresh(tmp)
        observed['gate green without a checker'] = code(patched, tmp) == 3

        # A1: tamper a body after the contract was anchored to its pristine hash.
        patched = fresh(tmp)
        (Path(tmp) / 'frames.json').write_bytes(b'{"frames": 18532}')
        observed['A1 rejects a tampered body'] = code(patched, tmp) == 1

        # A2: a wrong cardinality in the program.
        patched = fresh(tmp)
        body = json.loads((Path(tmp) / 'program.json').read_text())
        body['nodes'] = 18531
        (Path(tmp) / 'program.json').write_text(json.dumps(body))
        (Path(tmp) / 'integrity.json').write_text(json.dumps(
            {'files': {p.name: sha256(p) for p in Path(tmp).iterdir()}}))
        observed['A2 rejects a wrong cardinality'] = code(patched, tmp) == 1

        # A3: a denominator above the published bound.
        patched = fresh(tmp)
        with gzip.open(Path(tmp) / 'lift.certificate.json.gz', 'wt') as handle:
            json.dump({'nodes': 18532, 'physical_R': 9412, 'max_denominator': 3,
                       'max_abs_numerator': 2}, handle)
        (Path(tmp) / 'integrity.json').write_text(json.dumps(
            {'files': {p.name: sha256(p) for p in Path(tmp).iterdir()}}))
        observed['A3 rejects a denominator above the bound'] = code(patched, tmp) == 1

        # A4: counts quoted rather than counted out of the tables.
        patched = fresh(tmp)
        body = json.loads((Path(tmp) / 'chronology.json').read_text())
        body['tables'] = [{'target_rows': [], 'source_columns': []}]
        (Path(tmp) / 'chronology.json').write_text(json.dumps(body))
        (Path(tmp) / 'integrity.json').write_text(json.dumps(
            {'files': {p.name: sha256(p) for p in Path(tmp).iterdir()}}))
        observed['A4 rejects counts not coming out of the tables'] = code(patched, tmp) == 1

        # A5: a family digest that is not ours, and a bin outside the ledger.
        patched = fresh(tmp)
        body = json.loads((Path(tmp) / 'occurrences.complex.json').read_text())
        body['families']['16']['bank_table_digest'] = 'ff' * 32
        body['families']['12'] = body['families']['16']
        (Path(tmp) / 'occurrences.complex.json').write_text(json.dumps(body))
        (Path(tmp) / 'integrity.json').write_text(json.dumps(
            {'files': {p.name: sha256(p) for p in Path(tmp).iterdir()}}))
        observed['A5 rejects a foreign table and a foreign bin'] = code(patched, tmp) == 1

        # A6: a conflicting colouring accepted.
        patched = fresh(tmp)
        body = json.loads((Path(tmp) / 'frames.json').read_text())
        body['conflicting_assignment_rejected'] = False
        (Path(tmp) / 'frames.json').write_text(json.dumps(body))
        (Path(tmp) / 'integrity.json').write_text(json.dumps(
            {'files': {p.name: sha256(p) for p in Path(tmp).iterdir()}}))
        observed['A6 rejects an accepted conflict'] = code(patched, tmp) == 1

        # A7: a repeated witness.
        patched = fresh(tmp)
        body = json.loads((Path(tmp) / 'frames.json').read_text())
        body['prime_witnesses'] = [{'witness': 7, 'residual_factor': 3},
                                   {'witness': 7, 'residual_factor': 5}]
        (Path(tmp) / 'frames.json').write_text(json.dumps(body))
        (Path(tmp) / 'integrity.json').write_text(json.dumps(
            {'files': {p.name: sha256(p) for p in Path(tmp).iterdir()}}))
        observed['A7 rejects a repeated witness'] = code(patched, tmp) == 1

        # Refusal: one body removed.
        patched = fresh(tmp)
        (Path(tmp) / 'envelope.json').unlink()
        observed['refuses when a body is absent'] = code(patched, tmp) == 2

        # Replay: a checker that is not the pinned one, then one that is and passes.
        patched = fresh(tmp)
        checker = Path(tmp) / 'checker.py'
        checker.write_text('raise SystemExit(0)\n')
        observed['refuses a checker the contract does not pin'] = code(patched, tmp, checker) == 2
        patched['import_harness']['replay_requirement']['checker_digest'] = sha256(checker)
        observed['admits a pinned checker that passes and certifies the import'] = \
            code(patched, tmp, checker) == 0

        # Absent today: the real exports directory does not exist.
        observed['refuses the real drop, which does not exist yet'] = \
            code(contract, HERE / 'exports') == 2

    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--exports', type=Path, default=None,
                        help='directory holding the published bodies')
    parser.add_argument('--checker', type=Path, default=None,
                        help='the supplier checker whose digest E3 pins (enables the replay)')
    parser.add_argument('--self-test', action='store_true',
                        help='exercise the gate and the refusals on synthetic bodies')
    parser.add_argument('--json', action='store_true', help='print the report as JSON')
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text())

    if args.self_test:
        observed = self_test(contract)
        for name, ok in observed.items():
            print('%s  %s' % ('ok  ' if ok else 'FAIL', name))
        failures = [name for name, ok in observed.items() if not ok]
        print('self-test: %d checks, %d failed' % (len(observed), len(failures)))
        return 1 if failures else 0

    exports_dir = args.exports or HERE / contract['import_harness']['exports_dir']
    status, report = run(contract, exports_dir, args.checker)
    if args.json:
        print(json.dumps(report, indent=1, sort_keys=True))
    else:
        print('import harness: %s' % report['verdict'])
        if report['missing']:
            for name in report['missing']:
                print('  missing %s' % name)
            print('  the contract names each body and the digest it must reproduce; nothing is '
                  'run until they arrive')
        for key, value in sorted(report['tests'].items()):
            print('  %s %-10s %s' % (key, value['status'], value['reason'] or ''))
        if report['replay']:
            print('  replay %s %s' % (report['replay'].get('status'),
                                      report['replay'].get('reason', '')))
        print('  required today: %s' % ', '.join(report['bodies']))
    return status


if __name__ == '__main__':
    sys.set_int_max_str_digits(0)
    sys.exit(main())
