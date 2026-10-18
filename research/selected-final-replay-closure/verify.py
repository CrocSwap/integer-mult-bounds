#!/usr/bin/env python3
"""Fresh unchanged final supplier stage plus complete closed-policy comparison.

This is not the full ancestor cold replay or a multiplication theorem proof.
Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from compare_outputs import (POLICY, STAGES, compare, digest, invoice, outer_log,
                             prepare, read_files, require, strict)

A1042 = 'research/community-frontier1042-audit/'
A1094 = 'research/community-frontier1094-audit/'
SUPPLIER = 'research/complex-t16-rare-pattern-exchanges/'
REF_WORK = '/private/tmp/batch1099-selected/candidate'
REF_LOCAL = '/private/tmp/batch1047-selected/slots/local'


def authenticate(root=ROOT):
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in sources['files']:
        if row['usage'] == 'input':
            path = root / row['path']
            require(path.is_file() and not path.is_symlink() and
                    digest(path.read_bytes()) == row['sha256'], 'source drift: ' + row['path'])
    for row in sources['vendored_sources']:
        require(digest((HERE / row['path']).read_bytes()) == row['sha256'], 'vendor drift')
    return sum(row['usage'] == 'input' for row in sources['files'])


def archive_files(path, prefix=''):
    result = {}
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            if not member.name.startswith(prefix):
                continue
            if member.isdir():
                continue
            name = member.name[len(prefix):]
            p = PurePosixPath(name)
            require(member.isfile() and name and not p.is_absolute() and '..' not in p.parts
                    and p.as_posix() == name and '\\' not in name, 'unsafe archive member')
            require(name not in result, 'duplicate archive member')
            result[name] = archive.extractfile(member).read()
    return result


def fixture():
    inputs = archive_files(ROOT / (A1042 + 'selected-replay.tar.gz'), 'slots/local/')
    receipt1042 = json.loads((ROOT / (A1042 + 'RESULT.json')).read_bytes())
    bound = {n.removeprefix('slots/local/'): h for n, h in receipt1042['artifacts'].items()
             if n.startswith('slots/local/')}
    require(len(bound) == 10 and {n: digest(b) for n, b in inputs.items()} == bound,
            'archived local input does not match complete reviewed receipt')
    archived = archive_files(ROOT / (A1094 + 'selected-replay.tar.gz'))
    for name in ('RESULT.json', 'STAGES.json'):
        require(archived[name] == (ROOT / (A1094 + name)).read_bytes(), 'outer archive binding: ' + name)
    for name in ('ASSEMBLY.json', 'REPLAY.json'):
        require(archived['candidate/strict/' + name] == (ROOT / (A1094 + name)).read_bytes(),
                'selected archive binding: ' + name)
    receipt1094 = json.loads(archived['RESULT.json'])
    require(receipt1094['baseline_receipt_sha256'] == digest((ROOT / (A1042 + 'RESULT.json')).read_bytes()),
            'selected baseline binding differs')
    require(receipt1094['assembly_sha256'] == digest(archived['candidate/strict/ASSEMBLY.json']),
            'selected certificate binding differs')
    source_stage = [s for s in receipt1094['stages'] if s['name'] == 'rare-pattern-exchanges']
    require(len(source_stage) == 1 and source_stage[0]['script_sha256'] ==
            digest((ROOT / (SUPPLIER + 'verify.py')).read_bytes()), 'reviewed stage source differs')
    files = {n.removeprefix('candidate/strict/'): b for n, b in archived.items()
             if n.startswith('candidate/strict/')}
    context = {'work': REF_WORK, 'local': REF_LOCAL, 'external': {
        'local-word': inputs['CANONICAL-WORD.json.gz'],
        'local-replay': inputs['INDEPENDENT-LOCAL-REPLAY.json'],
        # The reviewed output archive omits source/. Its literal owner edge is
        # authenticated against the separately pinned selected package input.
        'owners': (ROOT / (SUPPLIER + 'data/OWNERS.json.gz')).read_bytes()}}
    prepare(files, context)
    outer_log(archived['rare-pattern-exchanges.log'], files)
    return inputs, files, context, archived['rare-pattern-exchanges.log']


def run_stage(work, inputs):
    local = work / 'local'
    local.mkdir()
    for name, raw in inputs.items():
        (local / name).write_bytes(raw)
    output = work / 'run'
    log = work / 'stage.log'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    for key in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(key, None)
    argv = [sys.executable, '-B', str(ROOT / (SUPPLIER + 'verify.py')),
            '--main', str(ROOT), '--local', str(local), '--work', str(output)]
    with log.open('wb') as stream:
        result = subprocess.run(argv, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                timeout=300)
    require(result.returncode == 0, 'final supplier stage failed; log: ' + str(log))
    files = read_files(output / 'strict')
    context = {'work': str(output.resolve()), 'local': str(local.resolve()), 'external': {
        'local-word': (local / 'CANONICAL-WORD.json.gz').read_bytes(),
        'local-replay': (local / 'INDEPENDENT-LOCAL-REPLAY.json').read_bytes(),
        'owners': (output / 'source/data/OWNERS.json.gz').read_bytes()}}
    return files, context, log.read_bytes()


def decode(name, raw):
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def encode(name, value):
    raw = (json.dumps(value, sort_keys=True, indent=1, allow_nan=False) + '\n').encode('utf-8')
    return gzip.compress(raw, compresslevel=1, mtime=23) if name.endswith('.gz') else raw


def mutate(files, name, operation):
    value = decode(name, files[name])
    operation(value)
    return dict(files, **{name: encode(name, value)})


def repoint_invoice(files):
    result = dict(files)
    for name in invoice.CONSUMERS:
        result = mutate(result, name,
                        lambda value: value['input_sha256'].__setitem__('fresh_invoice', digest(result[invoice.INVOICE])))
    return result


def controls(reference, context, reference_log):
    negative, positive = [], []

    def rejects(label, candidate, candidate_context=None, against=None):
        try:
            report = compare(reference if against is None else against, candidate,
                             context, candidate_context or context)
        except (ValueError, TypeError, KeyError, OSError, EOFError):
            negative.append(label)
            return
        require(not report['equivalent'], 'control accepted: ' + label)
        negative.append(label)

    def accepts(label, candidate, candidate_context=None):
        require(compare(reference, candidate, context, candidate_context or context)['equivalent'],
                'positive rejected: ' + label)
        positive.append(label)

    accepts('complete-authenticated-reference', reference)
    for name in sorted(reference):
        missing = dict(reference)
        del missing[name]
        rejects('missing:' + name, missing)
    rejects('extra-file', dict(reference, **{'UNDECLARED.json': b'{}'}))

    # Full caller executions, one semantic change in EVERY output file. Logs
    # have both references repaired, so equality of log contents is exercised.
    for name in sorted(reference):
        if name.endswith('.log'):
            changed = dict(reference, **{name: reference[name] + b'UNDECLARED PROOF OUTPUT\n'})
            for receipt in ('STAGES.json', 'REPLAY.json'):
                def repair(value, receipt=receipt):
                    rows = value if receipt == 'STAGES.json' else value['stages']
                    next(row for row in rows if row['name'] + '.log' == name)['log_sha256'] = digest(changed[name])
                changed = mutate(changed, receipt, repair)
        else:
            def change(value):
                if type(value) is dict:
                    value['unrecognized_proof_claim'] = True
                else:
                    value.append({'unrecognized_proof_claim': True})
            changed = mutate(reference, name, change)
            if name == invoice.INVOICE:
                changed = repoint_invoice(changed)
        rejects('semantic:' + name, changed)

    portable = dict(reference)
    portable[invoice.INVOICE] = encode(invoice.INVOICE, decode(invoice.INVOICE, reference[invoice.INVOICE]))
    require(portable[invoice.INVOICE] != reference[invoice.INVOICE], 'invoice formatting control is ineffective')
    portable = repoint_invoice(portable)
    accepts('reformatted-invoice-with-both-raw-links', portable)
    for name in invoice.CONSUMERS:
        stale = mutate(portable, name, lambda value: value['input_sha256'].__setitem__('fresh_invoice', '0' * 64))
        rejects('stale-invoice:' + name, stale)
        rejects('identically-stale-invoice:' + name, stale, against=stale)

    relocated_context = {**context, 'work': '/portable/replay-root', 'local': '/portable/local-root'}
    keymap = {context[r['root']] + '/' + r['suffix']: relocated_context[r['root']] + '/' + r['suffix']
              for r in POLICY['input_roles']}
    portable = mutate(portable, 'INDEPENDENT-T16.json',
                      lambda value: value.__setitem__('input_sha256', {keymap[k]: v for k, v in value['input_sha256'].items()}))
    for receipt in ('STAGES.json', 'REPLAY.json'):
        def change_times(value, receipt=receipt):
            rows = value if receipt == 'STAGES.json' else value['stages']
            for index, row in enumerate(rows):
                row['seconds'] = 100 + index
        portable = mutate(portable, receipt, change_times)
    accepts('composed-invoice-six-role-relocation-and-22-times', portable, relocated_context)
    portable_log = ('\n'.join(['PASS ' + name + ' ' + str(100 + i) for i, name in enumerate(STAGES)] +
                              reference_log.decode('utf-8').splitlines()[11:]) + '\n').encode('utf-8')
    require(outer_log(portable_log, portable) == outer_log(reference_log, reference), 'outer log normalization differs')
    positive.append('complete-outer-log-with-coupled-times')
    gz = 'global/hosted/GLOBAL-TEMPLATE.json.gz'
    recompressed = dict(reference, **{gz: gzip.compress(gzip.decompress(reference[gz]), compresslevel=1, mtime=51)})
    accepts('generated-gzip-container-change', recompressed)

    for name, paths in POLICY['timings'].items():
        for path in paths:
            def omit(value, path=path):
                node = value
                for component in path[:-1]:
                    node = node[component]
                del node[path[-1]]
            rejects('missing-time:' + name + ':' + repr(path), mutate(reference, name, omit))
    for bad, label in [(True, 'boolean'), (-1, 'negative'), ('1', 'string')]:
        candidate = dict(reference)
        for receipt in ('STAGES.json', 'REPLAY.json'):
            def wrong_time(value, receipt=receipt):
                (value if receipt == 'STAGES.json' else value['stages'])[0]['seconds'] = bad
            candidate = mutate(candidate, receipt, wrong_time)
        rejects('invalid-coupled-time:' + label, candidate)
    for index, name in enumerate(STAGES):
        candidate = dict(reference)
        for receipt in ('STAGES.json', 'REPLAY.json'):
            def wrong_hash(value, receipt=receipt):
                (value if receipt == 'STAGES.json' else value['stages'])[index]['log_sha256'] = '0' * 64
            candidate = mutate(candidate, receipt, wrong_hash)
        rejects('stale-coupled-log:' + name, candidate)
    independent = decode('INDEPENDENT-T16.json', reference['INDEPENDENT-T16.json'])
    for key in independent['input_sha256']:
        rejects('stale-input:' + key, mutate(reference, 'INDEPENDENT-T16.json',
                lambda value: value['input_sha256'].__setitem__(key, '0' * 64)))
        def alias(value):
            value['input_sha256']['literal-placeholder:' + key] = value['input_sha256'].pop(key)
        rejects('input-role-alias:' + key, mutate(reference, 'INDEPENDENT-T16.json', alias))
    copied_times = []
    for name, raw in reference.items():
        if name.endswith('.json') and name not in POLICY['timings']:
            value = decode(name, raw)
            if type(value) is dict and 'seconds' in value:
                copied_times.append(name)
                rejects('copied-historical-time:' + name, mutate(reference, name,
                        lambda value: value.__setitem__('seconds', value['seconds'] + 1)))
    require(len(copied_times) == 12, 'copied timing inventory drift')
    for name in ('ASSEMBLY.json', 'global/audit/PREFIX-AND-INVOICE.json'):
        bad = b'{"duplicate":1,"duplicate":2,' + reference[name].lstrip()[1:]
        candidate = dict(reference, **{name: bad})
        rejects('duplicate-key:' + name, candidate)
        rejects('identically-duplicate-key:' + name, candidate, against=candidate)
    for raw, label in [(b'NaN', 'nonfinite'), (b'{"schema":true}', 'wrong-shape')]:
        rejects('invalid-replay:' + label, dict(reference, **{'REPLAY.json': raw}))
    bad = mutate(reference, 'INDEPENDENT-T16.json', lambda value: value.__setitem__('live', True))
    rejects('boolean-is-not-integer', bad)
    rejects('truncated-gzip', dict(reference, **{gz: reference[gz][:-8]}))
    for raw, label in [(reference_log + b'extra\n', 'extra-line'),
                       (reference_log.replace(b'PASS restore-parent', b'PASS wrong-stage'), 'stage-name'),
                       (reference_log.replace(b'2.328', b'2.329', 1), 'uncoupled-time')]:
        try:
            outer_log(raw, reference)
        except ValueError:
            negative.append('outer-log:' + label)
        else:
            raise ValueError('outer log control accepted: ' + label)
    # Immutable container hashes are not relaxed like generated outputs.
    archive = (ROOT / (A1094 + 'selected-replay.tar.gz')).read_bytes()
    changed_header = archive[:4] + bytes([archive[4] ^ 1]) + archive[5:]
    require(gzip.decompress(archive) == gzip.decompress(changed_header) and digest(archive) != digest(changed_header),
            'immutable header mutation ineffective')
    pinned = next(r for r in json.loads((HERE / 'SOURCES.json').read_bytes())['files']
                  if r['path'] == A1094 + 'selected-replay.tar.gz')['sha256']
    require(digest(changed_header) != pinned, 'immutable archive header was accepted')
    negative.append('immutable-source-header')
    return {'positive_controls': positive, 'negative_controls': negative,
            'negative_count': len(negative), 'positive_count': len(positive),
            'copied_historical_timings_retained': len(copied_times)}


def run(work):
    source_count = authenticate()
    inputs, reference, reference_context, reference_log = fixture()
    candidate, candidate_context, candidate_log = run_stage(work, inputs)
    comparison = compare(reference, candidate, reference_context, candidate_context)
    require(comparison['equivalent'], 'fresh final outputs differ: ' + json.dumps(
        {n: row for n, row in comparison['files'].items() if not strict.accepted(row)}))
    require(outer_log(candidate_log, candidate) == outer_log(reference_log, reference), 'fresh outer log differs')
    classifications = Counter(row['cls'] + (':' + row['verdict'] if 'verdict' in row else '')
                              for row in comparison['files'].values())
    print('PASS_FRESH_SELECTED_FINAL_STAGE', json.dumps(classifications, sort_keys=True), flush=True)
    checked = controls(reference, reference_context, reference_log)
    result = {'schema_version': 1, 'status': 'PASS_SELECTED_FINAL_REPLAY_CLOSURE',
              'selected_kappa': '836330098538459/500000000000000000', 'fresh_supplier_stage': True,
              'source_inputs': source_count, 'local_input_files': len(inputs),
              'strict_output_files': len(reference), 'json_outputs': 94, 'inner_logs': len(STAGES),
              'raw_edges_authenticated_per_side': 30, 'invoice_edges_rebound_per_side': 2,
              'input_roles_relocated_per_side': 6, 'stage_timing_fields_normalized_per_side': 22,
              'outer_log_lines_checked': 13, 'outer_times_bound_to_receipt': 11,
              'policy_sha256': digest((HERE / 'POLICY.json').read_bytes()), **checked,
              'scope': 'Unchanged final supplier stage from authenticated archived local inputs; not full cold ancestry, arbitrary graph admission, cross-platform execution, or a new kappa.'}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--work', type=Path, help='new external work directory; default cleans a temporary directory')
    parser.add_argument('--write-result', type=Path, help='write deterministic result to a new file instead of comparing it')
    args = parser.parse_args()
    if args.work:
        work = args.work.resolve()
        require(not work.exists() and not work.is_relative_to(ROOT), 'use fresh external work')
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(prefix='selected-final-closure.') as name:
            result = run(Path(name).resolve())
    if args.write_result:
        with args.write_result.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        require(strict.tree(result) == strict.tree(strict.read_json((HERE / 'RESULT.json').read_bytes())),
                'complete deterministic result differs')
    print(result['status'], 'files=' + str(result['strict_output_files']),
          'edges=30', 'positives=' + str(result['positive_count']),
          'negatives=' + str(result['negative_count']), 'no_new_kappa')


if __name__ == '__main__':
    main()
