#!/usr/bin/env python3
"""Complete bounded replay, source binding, and actual package fault tests.

Apache-2.0; prepared for ToikY with substantial OpenAI Codex assistance.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def invoke(path, accepted=True):
    start = time.monotonic()
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(path)],
                            capture_output=True, text=True, timeout=120)
    need((result.returncode == 0) == accepted,
         'unexpected subprocess outcome for ' + path.name + '\n' + result.stdout + result.stderr)
    if accepted:
        need('PASS_' in result.stdout, 'missing success marker')
    return result.stdout.strip(), round(time.monotonic() - start, 3)


def compare():
    primary = json.loads((HERE / 'CENSUS.json').read_text())
    other = json.loads((HERE / 'INDEPENDENT.json').read_text())
    need(primary['maximum_area'] == other['maximum_area'] == 36, 'independent area agreement')
    need(primary['maximum_dirty_wrapper_saving'] == 12, 'complete wrapper saving')
    need(primary['common_record_count'] == other['legal_record_count'] == 2048, 'legal frame coverage')
    need(primary['common_records_sha256'] == other['legal_records_sha256']
         == 'ac3520884ea295130595b20b4703217ed6838ba49dae1e4ca63412371803be7a',
         'every legal-frame maximum agrees')
    for a, b in zip(primary['orbits'], other['summaries']):
        need(a['source_intersection'] == b['overlap'], 'orbit assignment')
        need(a['counts']['frames_examined'] == b['quotient_planes'] == 2667, 'all quotient planes')
        need(a['counts']['nondegenerate_frames'] == b['legal_planes'] == 1024, 'nondegenerate lifts')
        need(a['counts']['degenerate_frames'] == b['excluded_singular_planes'] == 1643, 'singular lifts')
        need({str(x): n for x, n in a['frame_maximum_area_histogram']} == b['area_histogram'],
             'per-orbit maximum histograms')


def faults_and_relocation():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='common frame seed48b ') as temp:
        root = Path(temp)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package)
        for rec in sources['repository_inputs']:
            dest = root / rec['path']; dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rec['path'], dest)
        selected = json.loads((ROOT / 'certificates/selected-result.json').read_text())
        certificate = root / selected['certificate']
        certificate.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / selected['certificate'], certificate)
        invoke(package / 'verify.py')
        witness = package / 'WITNESS.json'
        original = witness.read_bytes()
        d = json.loads(original)
        mutations = []
        for mode in ('missing_residual', 'bool_sign', 'wrong_word', 'missing_source_pin'):
            value = json.loads(original)
            if mode == 'missing_residual': value['witness']['outgoing_residual_bases'].pop()
            if mode == 'bool_sign': value['witness']['source_signs'][0] = True
            if mode == 'wrong_word': value['witness']['word'][0][2] *= -1
            if mode == 'missing_source_pin': value['source_pins'] -= 1
            mutations.append(json.dumps(value).encode())
        mutations.append(original.replace(b'"new_kappa": false', b'"new_kappa": false, "new_kappa": false'))
        for payload in mutations:
            witness.write_bytes(payload); invoke(package / 'verify.py', accepted=False)
        witness.write_bytes(original)
        corpus = package / 'CENSUS.json'; original_corpus = corpus.read_bytes()
        value = json.loads(original_corpus); value['orbits'][0]['counts']['frames_examined'] -= 1
        corpus.write_text(json.dumps(value)); invoke(package / 'census.py', accepted=False)
        corpus.write_bytes(original_corpus)
        corpus = package / 'INDEPENDENT.json'; original_corpus = corpus.read_bytes()
        value = json.loads(original_corpus); value['legal_record_count'] -= 1
        corpus.write_text(json.dumps(value)); invoke(package / 'independent.py', accepted=False)
        corpus.write_bytes(original_corpus)
        absent = package / 'INDEPENDENT.json.absent'
        corpus.rename(absent); invoke(package / 'independent.py', accepted=False)
        need(not corpus.exists(), 'default replay must not create missing evidence')
        absent.rename(corpus)
        source = root / sources['repository_inputs'][0]['path']; original_source = source.read_bytes()
        source.write_bytes(original_source + b'\nchanged source\n')
        invoke(package / 'verify.py', accepted=False); source.write_bytes(original_source)
        source = package / 'census.py'; original_source = source.read_bytes()
        source.write_bytes(original_source + b'\n# changed generator\n')
        invoke(package / 'verify.py', accepted=False); source.write_bytes(original_source)
        invoke(package / 'verify.py')
    return 10


def main():
    before = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    for name in ('census.py', 'independent.py', 'verify.py'):
        stdout, seconds = invoke(HERE / name)
        print(stdout)
        print('REPLAY_SECONDS ' + name + '=' + str(seconds))
    compare()
    count = faults_and_relocation()
    after = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(before == after, 'replay must preserve all package evidence')
    need(count == 10, 'package fault coverage')
    print('PASS_COMMON_FRAME_WEIGHT5_PACKAGE frames=5334 area=36 adds=24 controls=PASS no_new_kappa')


if __name__ == '__main__':
    main()
