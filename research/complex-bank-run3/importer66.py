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
    4  partial: the gate was run on the bodies present, for reporting only; nothing is discharged

A body may be declared `"stream": true`.  Such a body is a published byte stream rather than a
JSON document -- the canonical chart and incidence streams are exactly that -- so it is hashed as
published and never parsed, which is what makes a digest of a stream checkable (A1) without the
gate pretending to read a document that does not exist.

Absence and failure are different answers, and the report keeps them apart.  A body that is not
there is a missing datum: it is recorded against the tests that would have been decided on it, and
it never counts as a check that failed.  A body that is there but unreadable, or a check that
disagrees with its bound, is a failure and fails its test.  A test is decided only when some body
supplies its checks and none of its evidence is missing, so one absent body can hold a test that
another body has already checked: that is what the bit drop's `A6` and `A7` show, seventeen
passing checks each and no verdict until the controls arrive.  The default path stays
fail-closed -- one absent body and nothing runs -- and `--partial` is the reporting mode that
runs the gate on whatever is present, for inspection only, with exit code 4.
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

PASS, FAIL, NOT_RUN = 'PASS', 'FAIL', 'NOT_RUNNABLE'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(node, dotted, value):
    """Write a dotted path into a nested dict, creating the levels as needed."""
    parts = dotted.split('.')
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def resolved_source(source):
    """A file a contract compares against: this package's own, or one of the pins'."""
    for candidate in (HERE / source, HERE / 'references' / 'pr219-run1' / source):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError('the contract compares against %s, which is not in the package' % source)


def project(source, keys, fields):
    """The object at `keys` in `source`, optionally narrowed to `fields`."""
    node = json.loads(resolved_source(source).read_text())
    for key in keys:
        node = node[key]
    if fields is None:
        return node
    if isinstance(node, dict) and all(isinstance(row, dict) for row in node.values()):
        return {key: {field: row[field] for field in fields}   # one row per family, one per item
                for key, row in node.items()}
    return {field: node[field] for field in fields}


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
                             anchored=body.get('anchored_digest'),
                             stream=body.get('stream', False)))
            if not path.is_file():
                missing.append((export['id'], body['file']))
    return rows, missing


def gate(contract, exports_dir):
    """Every check decidable from the bodies that declare it.  Returns per-test results."""
    results = {test['id']: dict(test=test['id'], name=test['name'], status=NOT_RUN,
                                checks=[], reason=None, passed=0, failed=0)
               for test in contract['acceptance_tests']}

    def record(test, ok, detail):
        """`ok` is three-state: True and False are checks, None is a missing datum."""
        entry = results[test]
        entry['checks'].append(detail)
        if ok is None:
            need(test, detail)
        else:
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
        if row['stream']:              # a byte stream is hashed as published; it is not a document
            continue
        try:
            bodies[row['file']] = load(row['path'])
        except (json.JSONDecodeError, gzip.BadGzipFile, OSError, UnicodeDecodeError) as exc:
            # an absent body is a missing datum, not a failed check; a corrupt one is a failure
            if row['path'].is_file():
                record('A1', False, '%s is present but not readable as a body: %s' % (row['file'], exc))
            else:
                record('A1', None, '%s is absent' % row['file'])

    # A1 -- every anchored digest is the digest of the published bytes, and the integrity
    # manifest agrees with the files it lists.
    anchored = [row for row in rows if row['anchored']]
    for row in anchored:
        if not row['path'].is_file():          # nothing to hash: a missing datum, not a match
            record('A1', None, '%s is absent' % row['file'])
            continue
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
            if not row['path'].is_file():
                record('A1', None, '%s is absent' % row['file'])
                continue
            seen = sha256(row['path'])
            record('A1', declared.get(row['file']) == seen,
                   'A1 integrity declares %s = %s' % (row['file'], str(declared.get(row['file']))[:16]))

    # A2..A7 -- the declared gate of each export.
    for export in contract['required_exports']:
        declared = export['gate']
        tests = declared['test']
        subject = export['bodies'][0]['file']     # an export's declared checks are its primary
        # body's, unless named in `_on`.  A body is visited only when something is declared on it:
        # the subject, the manifest body, or a body with its own `equals_on` scope.  A stream cannot
        # be parsed, so nothing may be declared on it -- it is hashed by A1 and left alone.
        fields = [(subject, declared.get('equals', {}))]
        for body in export['bodies'][1:]:
            if body.get('stream'):
                continue
            scope = declared.get('equals_on', {}).get(body['file'], {})
            if body['file'] == declared.get('declares_every_body_on') or scope:
                fields.append((body['file'], scope))
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
                for dotted, bound in extra.get('at_most', {}).items():
                    try:
                        seen = walk(body, dotted)
                    except (KeyError, TypeError):
                        need(test, '%s has no %s' % (file_name, dotted))
                        continue
                    record(test, seen <= bound, '%s %s.%s = %r, bound at most %r'
                           % (test, file_name, dotted, seen, bound))
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

    # Counts that must equal a table this package or the pins already hold.
    for export in contract['required_exports']:
        declared = export['gate']
        for spec in declared.get('equals_in', []):
            test = declared['test'][0]
            body = bodies.get(export['bodies'][0]['file'])
            if body is None:
                need(test, '%s is absent' % export['bodies'][0]['file'])
                continue
            try:
                mine = walk(body, spec['body_key'])
            except (KeyError, TypeError):
                need(test, '%s has no %s' % (export['bodies'][0]['file'], spec['body_key']))
                continue
            wanted = project(spec['source'], spec['keys'], spec.get('fields'))
            if spec.get('per_key_of_body'):
                for key, row in wanted.items():
                    theirs = mine.get(key, mine.get(str(key)))
                    if isinstance(row, dict):            # one row per key: compare its fields
                        ok = theirs is not None and all(theirs.get(field) == value
                                                        for field, value in row.items())
                        detail = sorted(row)
                    else:                                # a flat projection off a dict of scalars:
                        ok = theirs == row               # the value itself is the datum
                        detail = 'value %s' % (str(row)[:24],)
                    record(test, ok, '%s %s[%s] matches %s: %s'
                           % (test, spec['body_key'], key, spec['source'], detail))
            else:
                record(test, mine == wanted, '%s %s matches %s' % (test, spec['body_key'],
                                                                  spec['source']))

    for entry in results.values():
        if entry['reason'] is None and not entry['passed'] and not entry['failed']:
            entry['reason'] = 'no body declares this test yet'
    settle()
    return results


def run(contract, exports_dir, checker=None, partial=False):
    """The whole import: refusal, gate, replay.  Returns (exit code, report).

    `partial=True` runs the gate on whatever bodies are present and reports every test's status from
    them, for reporting only: the report names what is absent and the exit code is 4, which is never
    admissible.  The default path stays fail-closed -- one absent body and nothing is run -- so a
    partial run can never be mistaken for an import.
    """
    rows, missing = refusal(contract, exports_dir)
    report = dict(exports_dir=str(exports_dir), bodies=[row['file'] for row in rows],
                  missing=['%s: %s' % pair for pair in missing], tests={}, replay=None,
                  partial=bool(partial))
    if missing and not partial:
        report['verdict'] = 'REFUSED: %d of %d required bodies are absent and nothing is run' % (
            len(missing), len(rows))
        return 2, report
    results = gate(contract, exports_dir)
    report['tests'] = {key: dict(status=value['status'], reason=value['reason'],
                                 passed=value['passed'], failed=value['failed'],
                                 checks=value['checks']) for key, value in results.items()}
    failed = sorted(key for key, value in results.items() if value['status'] == FAIL)
    if failed:
        report['verdict'] = 'FAILED: %s' % ', '.join(failed)
        return 1, report
    if missing:                    # partial, nothing failed: the gate ran, nothing is discharged
        report['replay'] = dict(status='NOT RUN',
                                reason='a partial drop cannot be replayed or certified')
        report['verdict'] = ('PARTIAL: %d of %d required bodies are absent, so the gate was run on '
                             'the %d present for reporting only; nothing is discharged'
                             % (len(missing), len(rows), len(rows) - len(missing)))
        return 4, report
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


def synthetic(contract, directory):
    """Bodies that satisfy the gate, built from the contract's own declared expectations.

    Nothing here is specific to one contract: the exports, their bodies, their bounds, their
    bijections, their witness lists and the tables they compare against all come out of the
    contract, so a second contract gets the same self-test for free.
    """
    out = Path(directory)

    def write(name, payload, compress=False):
        raw = json.dumps(payload, sort_keys=True).encode('utf-8')
        if compress:
            raw = gzip.compress(raw)
        (out / name).write_bytes(raw)

    manifests = []
    for export in contract['required_exports']:
        declared, primary = export['gate'], export['bodies'][0]['file']
        body = {}
        for dotted, value in declared.get('equals', {}).items():
            put(body, dotted, value)
        for dotted in declared.get('bijection', []):
            put(body, dotted, {'0': 0, '1': 1, '2': 2})
        for flag in declared.get('flags_true', []):
            put(body, flag, True)
        for flag in declared.get('flags_present', []):
            put(body, flag, {})
        for dotted, bound in declared.get('at_most', {}).items():
            put(body, dotted, bound)      # the bound itself: the tightest value the contract allows
        if 'distinct_below' in declared:
            spec = declared['distinct_below']
            put(body, spec['witnesses'], [{'witness': 7, 'residual_factor': 3},
                                          {'witness': 11, 'residual_factor': 5}])
            put(body, spec['bound'], 10 ** 80)
        tables = {table: [0] * declared['equals'][field]        # one table per counted column set
                  for table, field in declared.get('counted_in_tables', {}).items()}
        if tables:
            put(body, 'tables', [tables])
        for spec in declared.get('equals_in', []):
            wanted = project(spec['source'], spec['keys'], spec.get('fields'))
            put(body, spec['body_key'], wanted)
        first = export['bodies'][0]
        if first.get('stream'):                               # never valid JSON, by construction
            (out / primary).write_bytes(b'%s: a byte stream, as published\n' % primary.encode())
        else:
            write(primary, body, compress=primary.endswith('.gz'))
        for extra, fields in declared.get('equals_on', {}).items():
            body = {}
            for dotted, value in fields.items():
                put(body, dotted, value)
            write(extra, body, compress=extra.endswith('.gz'))
        for row in export['bodies'][1:]:
            other = row['file']
            if (out / other).is_file():
                continue
            if row.get('stream'):
                (out / other).write_bytes(b'%s: a byte stream, as published\n' % other.encode())
            else:
                write(other, {}, compress=other.endswith('.gz'))
        manifests.append(export)
    for export in contract['required_exports']:
        name = export['gate'].get('declares_every_body_on')
        if name:
            write(name, {'files': {p.name: sha256(p) for p in sorted(out.iterdir())}})
    return out


def self_test(contract):
    """Prove the harness works and rejects, on synthetic bodies, while no real body exists.

    Every case is derived from the contract itself, so each contract gets the same proof: the gate
    goes green on bodies built from its own declared expectations, and then every declared check is
    broken in turn and must fail, with the refusals and the replay gating checked as well.  No part
    of this is specific to the complex side.
    """
    observed = {}

    def first(key):
        """The first place the contract declares a check of this kind: file, spec, test id."""
        for export in contract['required_exports']:
            declared = export['gate']
            if declared.get(key):
                return export['bodies'][0]['file'], declared[key], declared['test'][0]
        return None, None, None

    def fails(report):
        return {test for test, row in report['tests'].items() if row['status'] == FAIL}

    def mutate(directory, file_name, fn):
        path = Path(directory) / file_name
        body = load(path)
        fn(body)
        raw = json.dumps(body, sort_keys=True).encode('utf-8')
        path.write_bytes(gzip.compress(raw) if file_name.endswith('.gz') else raw)

    def refresh(patched, directory):
        """Re-anchor every digest to the current bytes and refresh the manifests."""
        for export in patched['required_exports']:
            for body in export['bodies']:
                path = Path(directory) / body['file']
                if body.get('anchored_digest') is not None and path.is_file():
                    body['anchored_digest'] = sha256(path)
            name = export['gate'].get('declares_every_body_on')
            if name:
                (Path(directory) / name).write_text(json.dumps(
                    {'files': {p.name: sha256(p) for p in sorted(Path(directory).iterdir())}}))

    def broke(value):
        if isinstance(value, bool):
            return not value
        if isinstance(value, int):
            return value + 1
        if isinstance(value, dict) and value:
            key = sorted(value)[0]
            return dict(value, **{key: broke(value[key])})
        if isinstance(value, str):
            return value + '-'
        return 'broken'

    def case(**how):
        with tempfile.TemporaryDirectory() as tmp:
            patched = json.loads(json.dumps(contract))
            synthetic(patched, tmp)
            checker = None
            if how.get('equals'):
                file_name, spec, _test = first('equals')
                dotted, value = sorted(spec.items())[0]
                mutate(tmp, file_name, lambda body: put(body, dotted, broke(value)))
            if how.get('at_most'):
                file_name, spec, _test = first('at_most')
                dotted, bound = sorted(spec.items())[0]
                mutate(tmp, file_name, lambda body: put(body, dotted, bound + 1))
            if how.get('flag'):
                file_name, flags, _test = first('flags_true')
                mutate(tmp, file_name, lambda body: put(body, flags[0], False))
            if how.get('bijection'):
                file_name, names, _test = first('bijection')
                dotted = names[0]
                mutate(tmp, file_name, lambda body: put(body, dotted, {'0': 0, '1': 0}))
            if how.get('witnesses'):
                file_name, spec, _test = first('distinct_below')

                def duplicate(body):
                    seen = walk(body, spec['witnesses'])
                    put(body, spec['witnesses'], [seen[0], seen[0]])

                mutate(tmp, file_name, duplicate)
            if how.get('tables'):
                file_name, _spec, _test = first('counted_in_tables')
                mutate(tmp, file_name, lambda body: put(body, 'tables', []))
            if how.get('equals_in'):
                file_name, specs, _test = first('equals_in')
                spec = specs[0]

                def foreign(body):
                    mine = walk(body, spec['body_key'])
                    key = sorted(mine)[0]
                    row = mine[key]
                    if isinstance(row, dict):             # a table of rows: break one field
                        row = dict(row)
                        field = sorted(row)[0]
                        row[field] = 'foreign'
                    else:                                 # a flat map: the value is the datum
                        row = 'foreign'
                    mine[key] = row

                mutate(tmp, file_name, foreign)
            if how.get('tamper'):
                (Path(tmp) / contract['required_exports'][0]['bodies'][0]['file']).write_bytes(
                    b'not a body')
            if how.get('drop'):
                (Path(tmp) / contract['required_exports'][0]['bodies'][0]['file']).unlink()
            if how.get('checker'):
                checker = Path(tmp) / 'checker.py'
                checker.write_text('raise SystemExit(0)\n')
                if how['checker'] == 'pinned':
                    patched['import_harness']['replay_requirement'][
                        'checker_digest'] = sha256(checker)
            if not how.get('tamper') and not how.get('drop'):
                refresh(patched, tmp)
            return run(patched, tmp, checker)

    def broken_code(**how):
        """A mutation must be rejected *by the test the contract says covers it*, not by luck."""
        key = next(iter(how))
        _file, _spec, test = first({'equals': 'equals', 'at_most': 'at_most', 'flag': 'flags_true',
                                    'bijection': 'bijection', 'witnesses': 'distinct_below',
                                    'tables': 'counted_in_tables', 'equals_in': 'equals_in'}[key])
        code, report = case(**how)
        return code == 1 and test in fails(report)

    code, report = case()
    observed['gate green without a checker'] = code == 3 and not fails(report)
    observed['A1 rejects a tampered body'] = case(tamper=True)[0] == 1
    observed['a broken equality bound is rejected'] = broken_code(equals=True)
    observed['a bound above at_most is rejected'] = broken_code(at_most=True)
    observed['a false flag is rejected'] = broken_code(flag=True)
    observed['a broken bijection is rejected'] = broken_code(bijection=True)
    observed['a repeated witness is rejected'] = broken_code(witnesses=True)
    observed['counts not coming out of the tables are rejected'] = broken_code(tables=True)
    observed['a foreign table is rejected'] = broken_code(equals_in=True)
    observed['a missing body is refused'] = case(drop=True)[0] == 2
    observed['a checker the contract does not pin is refused'] = case(checker='unpinned')[0] == 2
    observed['the pinned checker passing certifies the import'] = case(checker='pinned')[0] == 0
    real = HERE / contract['import_harness']['exports_dir']
    observed['the real drop is refused, and reportable in part'] = (
        run(contract, real)[0] == 2 and run(contract, real, partial=True)[0] == 4)
    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--contract', type=Path, default=CONTRACT,
                        help='the export contract to import against (the complex side by default)')
    parser.add_argument('--exports', type=Path, default=None,
                        help='directory holding the published bodies')
    parser.add_argument('--checker', type=Path, default=None,
                        help='the supplier checker whose digest the contract pins (enables the replay)')
    parser.add_argument('--partial', action='store_true',
                        help='run the gate on the bodies present and report them (code 4, never '
                             'admissible)')
    parser.add_argument('--self-test', action='store_true',
                        help='exercise the gate and the refusals on synthetic bodies')
    parser.add_argument('--json', action='store_true', help='print the report as JSON')
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())

    if args.self_test:
        observed = self_test(contract)
        for name, ok in observed.items():
            print('%s  %s' % ('ok  ' if ok else 'FAIL', name))
        failures = [name for name, ok in observed.items() if not ok]
        print('self-test: %d checks, %d failed' % (len(observed), len(failures)))
        return 1 if failures else 0

    exports_dir = args.exports or HERE / contract['import_harness']['exports_dir']
    status, report = run(contract, exports_dir, args.checker, partial=args.partial)
    if args.json:
        # written as bytes: a redirected report is the file the manifest pins, and the default text
        # stream would translate its newlines, so the digest would not survive the round trip
        sys.stdout.buffer.write((json.dumps(report, indent=1, sort_keys=True) + '\n').encode('utf-8'))
        sys.stdout.buffer.flush()
    else:
        print('import harness: %s' % report['verdict'])
        if report['missing']:
            for name in report['missing']:
                print('  missing %s' % name)
            print('  the contract names each body and the digest it must reproduce; nothing is '
                  'run until they arrive')
        for key, value in sorted(report['tests'].items()):
            tally = ('' if not (value['passed'] or value['failed']) else
                     '%d of %d checks pass, %d fail ' % (value['passed'],
                                                         value['passed'] + value['failed'],
                                                         value['failed']))
            print('  %s %-10s %s%s' % (key, value['status'], tally, value['reason'] or ''))
        if report['replay']:
            print('  replay %s %s' % (report['replay'].get('status'),
                                      report['replay'].get('reason', '')))
        print('  required today: %s' % ', '.join(report['bodies']))
    return status


if __name__ == '__main__':
    sys.set_int_max_str_digits(0)
    sys.exit(main())
