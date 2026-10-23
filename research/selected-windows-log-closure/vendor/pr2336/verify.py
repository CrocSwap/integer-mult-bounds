#!/usr/bin/env python3
"""Source-bound PR1094 successor replay and explicit Windows receipt comparison.

Apache-2.0. Dennis / antunishdPursuit, substantial OpenAI Codex assistance.
Predecessors: PR2316 (josecarlosgonzalezroque-design), Rohan Arun's PR1094,
Jeremy Kothe's PR1087, Douglas Colkitt's receipts, JosieElliston's portability audit.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import platform
import subprocess
import sys
import tarfile
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = ROOT / 'research/complex-t16-rare-pattern-exchanges'
A1042 = ROOT / 'research/community-frontier1042-audit'
A1094 = ROOT / 'research/community-frontier1094-audit'
KAPPA = '0.001672660197076918'
DELTA = [('str(f.relative_to(P))', 'f.relative_to(P).as_posix()'),
         ('str(f.relative_to(source))', 'f.relative_to(source).as_posix()')]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parsed(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def read_json(path):
    return parsed(path.read_bytes())


def authenticate():
    rows = read_json(HERE / 'SOURCES.json')['files']
    for row in rows:
        if row['usage'] == 'input':
            require(sha((ROOT / row['path']).read_bytes()) == row['sha256'],
                    'immutable input changed: ' + row['path'])
    selected = read_json(A1094 / 'SELECTED-SOURCE.json')['files']
    for p in PACKAGE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            require(selected[p.relative_to(ROOT).as_posix()] == sha(p.read_bytes()),
                    'not the selected supplier input')


def successor(raw):
    original = read_json(HERE / 'SOURCES.json')['files']
    pin = next(r['sha256'] for r in original if r['path'] ==
               'research/complex-t16-rare-pattern-exchanges/verify.py')
    require(sha(raw) == pin, 'successor original script pin mismatch')
    text = raw.decode('utf-8')
    for old, new in DELTA:
        require(text.count(old) == 1, 'successor delta is no longer exactly two substitutions')
        text = text.replace(old, new)
    # optimize=0 preserves every original assert, including __debug__, under -O.
    return compile(text, str(PACKAGE / 'verify.py'), 'exec', optimize=0)


def extract(archive, destination, prefix=None):
    destination.mkdir(parents=True)
    with tarfile.open(archive) as stream:
        members = [m for m in stream if prefix is None or m.name.startswith(prefix)]
        for member in members:
            require(member.isfile() or member.isdir(), 'nonregular archive member')
            require((destination / member.name).resolve().is_relative_to(destination.resolve()),
                    'unsafe archive path')
        stream.extractall(destination, members=members, filter='data')


def inventory(root):
    return {p.relative_to(root).as_posix(): p for p in root.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts}


def lf(raw):
    return raw.replace(b'\r\n', b'\n')


def path_keys(document, work, local):
    value = copy.deepcopy(document)
    pins = value['input_sha256']
    normalized = {}
    for key, digest in pins.items():
        # Only this receipt's six absolute input-path keys may be relocated.
        windows = PureWindowsPath(key).is_absolute()
        path = PureWindowsPath(key) if windows else PurePosixPath(key)
        matches = []
        for token, base in [('<WORK>', work), ('<LOCAL>', local)]:
            parent = PureWindowsPath(base) if windows else PurePosixPath(base)
            try:
                tail = path.relative_to(parent)
            except ValueError:
                continue
            require('..' not in tail.parts, 'noncanonical receipt path')
            matches.append(token + '/' + tail.as_posix())
        require(len(matches) == 1, 'unmapped or ambiguous receipt path')
        name = matches[0]
        require(name not in normalized, 'receipt path collision')
        normalized[name] = digest
    require(len(normalized) == 6, 'expected six independent input pins')
    value['input_sha256'] = normalized
    return value


def stage_rows(rows, directory):
    require(isinstance(rows, list) and len(rows) == 11, 'expected eleven stages')
    value = copy.deepcopy(rows)
    for row in value:
        # Resolve receipt links against the actual output rather than ignoring hashes.
        name = row['name'] + '.log'
        require('/' not in name and '\\' not in name, 'invalid stage name')
        raw = (directory / name).read_bytes()
        require(row['log_sha256'] == sha(raw), 'stage log digest mismatch')
        seconds = row['seconds']
        require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0,
                'invalid stage timing')
        row['seconds'] = '<WALL_TIME>'
        row['log_sha256'] = sha(lf(raw))
    return value


def compare(ref, run, ref_work, ref_local, run_work, run_local):
    left, right = inventory(ref), inventory(run)
    require(set(left) == set(right) and len(left) == 105, 'output inventory mismatch')
    classes = {}
    for name in sorted(left):
        a, b = left[name].read_bytes(), right[name].read_bytes()
        if a == b:
            classes[name] = 'bytes'
            continue
        if name.endswith('.log') and lf(a) == lf(b):
            classes[name] = 'crlf-only'
            continue
        if name == 'global/audit/PREFIX-AND-INVOICE.json':
            require(canonical(parsed(a)) == canonical(parsed(b)), 'invoice proof content changed')
            classes[name] = 'json-key-order-or-format'
        elif name in ('ASSEMBLY.json', 'ADMISSION-CONTROLS.json'):
            ja, jb = parsed(a), parsed(b)
            invoice = 'global/audit/PREFIX-AND-INVOICE.json'
            for doc, files in [(ja, left), (jb, right)]:
                require(doc['input_sha256']['fresh_invoice'] == sha(files[invoice].read_bytes()),
                        'fresh invoice digest mismatch')
                doc['input_sha256']['fresh_invoice'] = '<CHECKED_INVOICE>'
            require(canonical(ja) == canonical(jb), 'assembly/admission changed beyond checked invoice digest')
            classes[name] = 'checked-invoice-digest'
        elif name == 'INDEPENDENT-T16.json':
            require(canonical(path_keys(parsed(a), ref_work, ref_local)) ==
                    canonical(path_keys(parsed(b), run_work, run_local)),
                    'independent receipt changed beyond relocated input paths')
            classes[name] = 'six-relocated-input-paths'
        elif name in ('STAGES.json', 'REPLAY.json'):
            ja, jb = parsed(a), parsed(b)
            if name == 'REPLAY.json':
                ja['stages'] = stage_rows(ja['stages'], ref)
                jb['stages'] = stage_rows(jb['stages'], run)
            else:
                ja, jb = stage_rows(ja, ref), stage_rows(jb, run)
            require(canonical(ja) == canonical(jb), 'stage receipt changed beyond checked logs/timings')
            classes[name] = 'checked-stage-logs-and-timings'
        else:
            raise ValueError('unexplained output difference: ' + name)
    # Check links even when two corrupted receipts happen to match byte-for-byte.
    for directory in (ref, run):
        stages, replay = read_json(directory / 'STAGES.json'), read_json(directory / 'REPLAY.json')
        require(canonical(stages) == canonical(replay['stages']), 'stage receipt disagreement')
        stage_rows(stages, directory)
        require(replay['kappa_decimal'] == KAPPA, 'unexpected kappa')
        for name in ('ASSEMBLY.json', 'ADMISSION-CONTROLS.json'):
            require(read_json(directory / name)['input_sha256']['fresh_invoice'] ==
                    sha((directory / 'global/audit/PREFIX-AND-INVOICE.json').read_bytes()),
                    'fresh invoice digest mismatch')
    counts = {key: list(classes.values()).count(key) for key in sorted(set(classes.values()))}
    return {'counts': counts, 'classes': classes, 'files': len(classes),
            'gzip_byte_identical': sum(name.endswith('.gz') and cls == 'bytes'
                                       for name, cls in classes.items())}


def controls(ref, run, arguments):
    rejected = []
    def mutate(name, change, label):
        path = run / name
        old = path.read_bytes()
        path.write_bytes(change(old))
        try:
            compare(ref, run, *arguments)
        except (ValueError, KeyError, json.JSONDecodeError):
            rejected.append(label)
        else:
            raise ValueError('corruption accepted: ' + label)
        finally:
            path.write_bytes(old)
    def edit(fn):
        def apply(raw):
            value = json.loads(raw)
            fn(value)
            return (json.dumps(value, indent=2) + '\n').encode()
        return apply
    mutate('global/audit/PREFIX-AND-INVOICE.json',
           edit(lambda d: d.update({'corrupt_proof_value': 1})), 'invoice-proof-value')
    mutate('global/audit/PREFIX-AND-INVOICE.json',
           edit(lambda d: d['selected_calls'][0].update({'stage': False})), 'invoice-integer-to-boolean')
    mutate('global/audit/PREFIX-AND-INVOICE.json',
           lambda raw: b'{\"status\": \"duplicate\",' + raw[1:], 'duplicate-invoice-key')
    mutate('ASSEMBLY.json', edit(lambda d: d.update({'corrupt_proof_value': 1})), 'assembly-proof-value')
    mutate('ADMISSION-CONTROLS.json',
           edit(lambda d: d['input_sha256'].update({'fresh_invoice': '0'*64})), 'invoice-link')
    mutate('INDEPENDENT-T16.json', edit(lambda d: d['input_sha256'].update(
        {next(iter(d['input_sha256'])): '0'*64})), 'independent-input-digest')
    mutate('INDEPENDENT-T16.json', edit(lambda d: d['input_sha256'].update(
        {'/unmapped/extra': '0'*64})), 'unmapped-input-path')
    mutate('restore-parent.log', lambda raw: raw + b'ALTERED\n', 'stage-log-content')
    mutate('STAGES.json', edit(lambda d: d[0].update({'log_sha256': '0'*64})), 'stage-log-link')
    mutate('REPLAY.json', edit(lambda d: d.update({'kappa_decimal': '0.01'})), 'replay-kappa')
    mutate('REPLAY.json', edit(lambda d: d['stages'][0].update({'seconds': -1})), 'invalid-timing')
    gz = next(name for name in inventory(run) if name.endswith('.gz'))
    mutate(gz, lambda raw: raw + b'corrupt', 'gzip-output')
    path = run / 'restore-parent.log'
    old = path.read_bytes()
    path.unlink()
    try:
        try:
            compare(ref, run, *arguments)
        except ValueError:
            rejected.append('missing-output')
        else:
            raise ValueError('missing output accepted')
    finally:
        path.write_bytes(old)
    extra = run / 'unexpected-control'
    extra.write_bytes(b'extra')
    try:
        try:
            compare(ref, run, *arguments)
        except ValueError:
            rejected.append('extra-output')
        else:
            raise ValueError('extra output accepted')
    finally:
        extra.unlink()
    try:
        successor((PACKAGE / 'verify.py').read_bytes() + b'\n')
    except ValueError:
        rejected.append('changed-original-script')
    else:
        raise ValueError('changed original accepted')
    # No CR characters, path-like strings or volatile fields outside declared sites are waived.
    mutate('ASSEMBLY.json', edit(lambda d: d.update({'seconds': 1})), 'undeclared-timing-field')
    return rejected


def evaluate(work):
    authenticate()
    extract(A1042 / 'selected-replay.tar.gz', work / 'in1042', 'slots/local/')
    local = work / 'in1042/slots/local'
    bound = {name: digest for name, digest in read_json(A1042 / 'RESULT.json')['artifacts'].items()
             if name.startswith('slots/local/')}
    require(len(bound) == 10 and set(bound) == {'slots/local/'+p.name for p in local.iterdir()},
            'PR1042 input inventory mismatch')
    for name, digest in bound.items():
        require(sha((work / 'in1042' / name).read_bytes()) == digest, 'PR1042 input digest mismatch')
    extract(A1094 / 'selected-replay.tar.gz', work / 'reference')
    ref = work / 'reference/candidate/strict'
    for name in ('RESULT.json', 'STAGES.json'):
        require((work/'reference'/name).read_bytes() == (A1094/name).read_bytes(), 'reference receipt changed')
    require((ref/'REPLAY.json').read_bytes() == (A1094/'REPLAY.json').read_bytes(), 'reference replay changed')
    require((ref/'ASSEMBLY.json').read_bytes() == (A1094/'ASSEMBLY.json').read_bytes(), 'reference assembly changed')
    result = read_json(A1094/'RESULT.json')
    require(result['baseline_receipt_sha256'] == sha((A1042/'RESULT.json').read_bytes()), 'wrong baseline receipt')
    stage = [s for s in result['stages'] if s['name'] == 'rare-pattern-exchanges']
    require(len(stage) == 1 and stage[0]['script_sha256'] == sha((PACKAGE/'verify.py').read_bytes()), 'wrong stage source')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    # Reproduce the unchanged failure before executing the successor on Windows.
    original = 'not run on non-Windows'
    if os.name == 'nt':
        failed = work/'original-must-not-exist'
        run = subprocess.run([sys.executable, '-I', '-B', str(PACKAGE/'verify.py'), '--main',str(ROOT),
                              '--local',str(local),'--work',str(failed)], capture_output=True, env=env, timeout=30)
        require(run.returncode != 0 and b'AssertionError: Submission file inventory or hash changed' in run.stderr
                and not failed.exists(), 'original Windows failure no longer reproduced')
        original = 'submission inventory rejected before output creation'
    out = work/'run'
    log = work/'successor.log'
    with log.open('wb') as stream:
        run = subprocess.run([sys.executable, '-I', '-B', str(HERE/'verify.py'), '--stage',
                              '--local',str(local),'--work',str(out)], env=env, stdout=stream,
                             stderr=subprocess.STDOUT, timeout=240)
    require(run.returncode == 0, 'successor failed: '+log.read_text(errors='replace')[-5000:])
    require(log.read_text().endswith('PASS_T16_RARE_PATTERN_EXCHANGES '+KAPPA+'\n'), 'missing successor success')
    arguments = ['/private/tmp/batch1099-selected/candidate', '/private/tmp/batch1047-selected/slots/local',
                 str(out), str(local)]
    comparison = compare(ref, out/'strict', *arguments)
    rejected = controls(ref, out/'strict', arguments)
    require(compare(ref, out/'strict', *arguments) == comparison, 'controls did not restore outputs')
    authenticate()
    return {'status':'PASS_SELECTED1094_WINDOWS_SUCCESSOR', 'kappa':KAPPA, 'stages':11,
            'original_observation':original, 'comparison':comparison, 'corruptions_rejected':rejected,
            'assembly_byte_identical':(ref/'ASSEMBLY.json').read_bytes() == (out/'strict/ASSEMBLY.json').read_bytes(),
            'scope':'Selected final stage with archived PR1042 local inputs; not cold ancestry or theorem verification'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--local', type=Path)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.stage:
        require(args.local is not None and args.work is not None, 'stage paths required')
        authenticate()
        code = successor((PACKAGE/'verify.py').read_bytes())
        sys.argv = [str(PACKAGE/'verify.py'),'--main',str(ROOT),'--local',str(args.local),'--work',str(args.work)]
        exec(code, {'__name__':'__main__','__file__':str(PACKAGE/'verify.py')})
        return
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='selected1094-successor-') as temp:
        result = evaluate(Path(temp).resolve())
    if args.report:
        args.report.write_text(json.dumps({'python':sys.version, 'platform':platform.platform(),
            'seconds':round(time.monotonic()-start,3),'result':result},indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'], 'stages=11 files=105 controls='+str(len(result['corruptions_rejected'])),
          json.dumps(result['comparison']['counts'],sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
