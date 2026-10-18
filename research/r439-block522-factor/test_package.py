#!/usr/bin/env python3
"""Relocated replay and fail-closed package controls; standard library only.

Jerry Chen (@CubeJerry), with OpenAI Codex assistance; Apache-2.0.
"""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    package = HERE.relative_to(ROOT)
    sources = json.loads((HERE / 'SOURCES.json').read_text())['sha256']
    with tempfile.TemporaryDirectory(prefix='r439-block522-relocated-') as temporary:
        relocated = Path(temporary)
        for relative in sources:
            destination = relocated / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        shutil.copytree(HERE, relocated / package, ignore=shutil.ignore_patterns('__pycache__'))
        target = relocated / package

        def replay():
            return subprocess.run([sys.executable, '-I', '-O', '-B', target / 'verify.py'],
                                  cwd=relocated, capture_output=True, text=True)

        result = replay()
        need(result.returncode == 0 and 'PASS_R439_BLOCK522_FACTOR' in result.stdout,
             'relocated optimized replay failed: ' + result.stderr)
        rejected = []

        def reject(name, path, altered, expected_error):
            original = path.read_bytes()
            try:
                if altered is None:
                    path.unlink()
                else:
                    path.write_bytes(altered)
                result = replay()
                need(result.returncode != 0 and expected_error in result.stderr,
                     'package control accepted or failed unexpectedly: ' + name + '\n' + result.stderr)
                rejected.append(name)
            finally:
                path.write_bytes(original)

        candidate_path = target / 'CANDIDATE.json'
        candidate = json.loads(candidate_path.read_text())
        candidate['operations'].pop(0)
        candidate['candidate_additions'] -= 1
        reject('candidate_math_not_just_count', candidate_path,
               json.dumps(candidate).encode(), 'integer block map mismatch')
        expected_path = target / 'EXPECTED.json'
        expected = json.loads(expected_path.read_text())
        expected['candidate']['reverse_positive_bound'] -= 1
        reject('falsified_receipt', expected_path, json.dumps(expected).encode(),
               'committed receipt mismatch')
        reject('missing_receipt', expected_path, None, 'FileNotFoundError')
        pins_path = target / 'SOURCES.json'
        pins = json.loads(pins_path.read_text())
        del pins['sha256']['research/e8-bit-p111-tuned/code/xcheck_p.py']
        reject('omitted_checker_pin', pins_path, json.dumps(pins).encode(),
               'incomplete source pin inventory')
        source_path = relocated / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
        word = json.loads(gzip.decompress(source_path.read_bytes()))
        word['scatter'][0].pop()
        reject('source_scatter_changed', source_path,
               gzip.compress(json.dumps(word).encode(), mtime=0), 'source pin mismatch')
        candidate = json.loads(candidate_path.read_text())
        candidate['source_sha256'] = '0' * 64
        reject('wrong_candidate_source', candidate_path, json.dumps(candidate).encode(),
               'candidate source mismatch')
        print('PASS_R439_BLOCK522_PACKAGE relocated_optimized_replay=PASS controls=%d' % len(rejected))
        print(' '.join(rejected))


if __name__ == '__main__':
    main()
