#!/usr/bin/env python3
"""Fixture controls for the adjacent native_evidence module; no native reruns.

All inputs are CLI arguments. Only --work is created or changed; source,
native evidence, input word and pinned manifest remain untouched. RESULT.json
records the accepted portability fixtures and rejected corruption fixtures.
Predecessor credit: PR2288 and its retained notices. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import native_evidence as E


def read(path):
    return E._json(E._payload(path))


def write(path, value, compressed=False):
    data = json.dumps(value, indent=3, ensure_ascii=True).encode() + b'\n'
    path.write_bytes(gzip.compress(data, mtime=123456789) if compressed else data)


def update_refs(directory):
    for name, references in E.REFERENCE_TARGETS.items():
        if name == 'native.log':
            continue
        path = directory / name
        obj = read(path)
        for field, (target, encoding) in references.items():
            data = (directory / target).read_bytes() if encoding == 'raw' else E._payload(directory / target)
            obj[field] = hashlib.sha256(data).hexdigest()
        write(path, obj)


def alter_phase(value):
    if isinstance(value, dict):
        if 'phase' in value and type(value['phase']) is int:
            value['phase'] = (value['phase'] + 1) % 4
            return True
        return any(alter_phase(child) for child in value.values())
    if isinstance(value, list):
        return any(alter_phase(child) for child in value)
    return False


def run_controls(native_dir, source_package, word_path, manifest, work):
    native_dir, source_package, word_path, work = map(Path,
        (native_dir, source_package, word_path, work))
    work.mkdir(parents=True, exist_ok=False)
    E.validate_manifest(native_dir, source_package, word_path, manifest)
    checks = []

    def fixture(name):
        target = work / name
        shutil.copytree(native_dir, target)
        return target

    headers = fixture('gzip-headers-with-original-references')
    for name in E.LOCAL_FILES:
        if name.endswith('.gz'):
            path = headers / 'local' / name
            path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), mtime=1))
    E.validate_manifest(headers, source_package, word_path, manifest)
    checks.append({'name': 'gzip-headers-with-original-references', 'accepted': True})

    portable = fixture('portable-encoding-and-timings')
    for name in E.LOCAL_FILES:
        path = portable / 'local' / name
        obj = read(path)
        if name in ('SCALAR-FRAME-AUDIT.json', 'CLIFFORD-REVIEW.json'):
            obj['seconds'] += 1000.25
        write(path, obj, name.endswith('.gz'))
    update_refs(portable)
    scalar = read(portable / 'local/SCALAR-FRAME-AUDIT.json')
    scalar.pop('widths')
    write(portable / 'native.log', scalar)
    steps = read(portable / 'STEPS.json')
    for row in steps:
        row['seconds'] += 1000.5
    write(portable / 'STEPS.json', steps)
    phase_text = (portable / 'phases.log').read_text()
    phase_text = re.sub(r'(?<=seconds )([0-9.eE+-]+)',
                        lambda m: str(float(m[1]) + 1000), phase_text)
    phase_text = re.sub(r'(?<=PASS exact local phases )([0-9.eE+-]+)',
                        lambda m: str(float(m[1]) + 1000), phase_text)
    (portable / 'phases.log').write_text(phase_text)
    for name in E.LOG_FILES:
        if name == 'native.log':
            continue
        path = portable / name
        path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
    E.validate_manifest(portable, source_package, word_path, manifest)
    checks.append({'name': 'compression-json-newlines-and-explicit-timings', 'accepted': True})

    def reject(name, change, source=source_package, word=word_path):
        target = fixture(name)
        change(target)
        try:
            E.validate_manifest(target, source, word, manifest)
        except Exception as error:
            checks.append({'name': name, 'rejected': True,
                           'exception': type(error).__name__, 'reason': str(error)})
        else:
            raise RuntimeError('Accepted changed native evidence: ' + name)

    def recipe(target):
        path = target / 'local/CLIFFORD-RECIPES.json'
        obj = read(path)
        E._require(alter_phase(obj), 'No phase field found in recipe fixture')
        write(path, obj)
        update_refs(target)
    reject('coherent-recipe-phase-corruption', recipe)

    def program(target):
        path = target / 'local/LOCAL-PROGRAMS.json.gz'
        obj = read(path)
        event = next(e for e in obj['forward'] if e[0] == 'scalar' and e[1][0] == 'add')
        event[1][3] += 1
        write(path, obj, True)
        path = target / 'local/LOCAL-CHECKS.json'
        checks_obj = read(path)
        checks_obj['forward']['sha256'] = E.canonical_json_sha256(obj['forward'])
        write(path, checks_obj)
        update_refs(target)
    reject('coherent-program-coefficient-corruption', program)

    def wrapper(target):
        path = target / 'local/RESIDUAL-ADAPTERS.json'
        obj = read(path)
        E._require(alter_phase(obj), 'No phase field found in wrapper fixture')
        write(path, obj)
    reject('wrapper-phase-corruption', wrapper)

    def product(target):
        path = target / 'local/INDEPENDENT-LOCAL-REPLAY.json'
        obj = read(path)
        obj['local']['forward']['warp_product_sha256'] = '0' * 64
        write(path, obj)
    reject('warp-product-hash-corruption', product)

    def failed_step(target):
        path = target / 'STEPS.json'; obj = read(path)
        obj[4]['exit_code'] = 1; write(path, obj)
    reject('failed-native-step', failed_step)

    def status(target):
        path = target / 'local/CLIFFORD-REVIEW.json'; obj = read(path)
        obj['all_child_equalities_include_global_phase'] = False; write(path, obj)
    reject('global-phase-claim-erased', status)

    def stale_reference(target):
        path = target / 'local/INDEPENDENT-LOCAL-REPLAY.json'
        obj = read(path)
        obj['canonical_word_sha256'] = '0' * 64
        write(path, obj)
    reject('unknown-stale-container-reference', stale_reference)

    def bad_timing(target):
        path = target / 'STEPS.json'; obj = read(path)
        obj[0]['seconds'] = -1; write(path, obj)
    reject('invalid-ignored-timing', bad_timing)
    reject('extra-log-line', lambda target: (target / 'phases.log').write_text(
        (target / 'phases.log').read_text() + 'PASS unbound check\n'))
    reject('phase-log-unapproved-separator', lambda target: (target / 'phases.log').write_text(
        (target / 'phases.log').read_text().replace('\n', '\u2028', 1)))
    reject('phase-log-count-spelling', lambda target: (target / 'phases.log').write_text(
        (target / 'phases.log').read_text().replace('edges 0 /', 'edges 00 /', 1)))
    reject('changed-control-count', lambda target: (target / 'local-replay.log').write_text(
        (target / 'local-replay.log').read_text().replace('44 controls', '43 controls')))
    reject('missing-artifact', lambda target: (target / 'local/WRAPPER-CHECKS.json').unlink())
    reject('extra-artifact', lambda target: (target / 'UNBOUND.json').write_text('{}\n'))

    changed_word = work / 'changed-word.json.gz'
    obj = read(word_path); obj['A'][0][3] += 1; write(changed_word, obj, True)
    reject('input-word-corruption', lambda target: None, word=changed_word)

    source_fixture = work / 'changed-source'
    shutil.copytree(source_package, source_fixture)
    path = source_fixture / 'new/code/borrow/bw_gauss.py'
    path.write_bytes(path.read_bytes() + b'\n# changed fixture\n')
    reject('consumed-source-corruption', lambda target: None, source=source_fixture)
    shutil.copy2(source_package / 'new/code/borrow/bw_gauss.py', path)
    (source_fixture / 'new/code/borrow/shadow.py').write_text('raise RuntimeError("fixture")\n')
    reject('unmanifested-source-shadow', lambda target: None, source=source_fixture)
    result = {'status': 'PASS_NATIVE_EVIDENCE_FIXTURE_CONTROLS',
              'native_pipeline_rerun': False,
              'python_optimization': sys.flags.optimize, 'checks': checks,
              'negative_controls': sum(row.get('rejected', False) for row in checks),
              'positive_controls': sum(row.get('accepted', False) for row in checks)}
    (work / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-dir', type=Path, required=True)
    parser.add_argument('--source-package', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    result = run_controls(args.native_dir, args.source_package, args.word,
                          read(args.manifest), args.work)
    print(result['status'], result['negative_controls'], 'negative controls')


if __name__ == '__main__':
    main()
