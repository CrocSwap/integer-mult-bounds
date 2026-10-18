#!/usr/bin/env python3
"""Relocation, payload-repacking, corruption, and output-preservation controls.

Prepared for CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
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


def run(script, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(script), *map(str, args)],
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          cwd=script.parent)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    with tempfile.TemporaryDirectory(prefix='factory fusion relocated with spaces ') as tmp:
        root = Path(tmp)
        package = root / 'research/complex-factory-fused-seed23'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for rel in pins['files']:
            destination = root / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, destination)
        verifier = package / 'verify.py'
        result = run(verifier)
        require(result.returncode == 0, 'relocated replay failed:\n' + result.stdout)
        # Container bytes change; every consumed proof-relevant payload byte is retained.
        compressed = root / 'research/direct-delivery504-global/inputs/hamming/PACKET-PROGRAMS.json.gz'
        original = compressed.read_bytes()
        repacked = gzip.compress(gzip.decompress(original), compresslevel=1, mtime=23)
        require(repacked != original, 'repacking positive control did not change container')
        compressed.write_bytes(repacked)
        result = run(verifier)
        require(result.returncode == 0, 'payload-preserving repack failed:\n' + result.stdout)
        compressed.write_bytes(original)
        rejected = []

        def reject(name, path, replacement, reason):
            saved = path.read_bytes()
            try:
                path.write_bytes(replacement)
                result = run(verifier)
                require(result.returncode != 0 and reason in result.stdout,
                        name + ': wrong rejection:\n' + result.stdout)
                rejected.append(name)
            finally:
                path.write_bytes(saved)

        constructor = root / 'research/complex-k492-owner-repair/code/construct_k_triangle.py'
        reject('changed_source', constructor, constructor.read_bytes() + b'\n# altered\n',
               'Source pin mismatch')
        predecessor = root / 'research/complex-factory5-resynthesis/CIRCUIT.json'
        value = json.loads(predecessor.read_text())
        value['replacement'][0][3] *= -1
        reject('changed_predecessor', predecessor, json.dumps(value).encode(), 'Source pin mismatch')
        circuit = package / 'CIRCUIT.json'
        value = json.loads(circuit.read_text())
        value['replacement'][0][3] = True
        reject('boolean_coefficient', circuit, json.dumps(value).encode(), 'non-integer gate field')
        value = json.loads(circuit.read_text())
        value['fusions'][1]['pair_order'] = [1, 2]
        reject('wrong_second_fusion', circuit, json.dumps(value).encode(), 'fusion changes the exact map')
        expected = package / 'RESULT.json'
        value = json.loads(expected.read_text())
        value['after']['emitted']['forward']['real_component_primitive_bound'] -= 1
        reject('understated_invoice', expected, json.dumps(value).encode(), 'receipt differs from frozen result')
        existing = root / 'existing output'
        existing.mkdir()
        marker = existing / 'keep.txt'
        marker.write_text('preserve')
        result = run(verifier, '--out', existing)
        require(result.returncode != 0 and marker.read_text() == 'preserve',
                'existing replay output was not protected')
        rejected.append('existing_output_preserved')
        result = run(verifier, '--write', marker)
        require(result.returncode != 0 and 'receipt output already exists' in result.stdout
                and marker.read_text() == 'preserve', 'existing receipt was not protected')
        rejected.append('existing_receipt_preserved')
    print('PASS_FACTORY_FUSION_PACKAGE relocation=1 payload_repack=1 rejections=' + str(len(rejected)))


if __name__ == '__main__':
    main()
