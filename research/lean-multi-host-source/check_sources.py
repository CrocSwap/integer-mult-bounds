#!/usr/bin/env python3
"""Reproduce the source-to-literal boundary; this Python parser is not a Lean proof."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import struct
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def check():
    versions = json.loads((ROOT / 'source-versions.json').read_text())
    with tempfile.TemporaryDirectory(prefix='source-binding-') as tmp:
        work = Path(tmp)
        inputs = {}
        for name, expected in versions['inputs'].items():
            blob = (ROOT / 'inputs' / name).read_bytes()
            require(hashlib.sha256(blob).hexdigest() == expected['sha256_compressed'], name)
            raw = gzip.decompress(blob)
            require(hashlib.sha256(raw).hexdigest() == expected['sha256_uncompressed'], name)
            path = work / name.removesuffix('.gz')
            path.write_bytes(raw)
            inputs[name] = json.loads(raw) if path.suffix == '.json' else raw
        template = inputs['hosted-template.json.gz']
        parent = inputs['parent-template.json.gz']
        events = template['local_programs']['forward']
        require(events == parent['local_programs']['forward'], 'Parent/hosted word changed')
        require(len(events) == 19002, 'Event count changed')
        raw_records = list(struct.iter_unpack('<6i', inputs['records.bin.gz']))
        reconstructed = []
        for op, x, y, c, f, z in raw_records:
            require(op in range(4), 'Unknown record opcode')
            if op < 2:
                # The exporter uses ADD's last field for the five word
                # phases (D, A, scatter, B, C), not an address reflection.
                require(z == 0 if op == 0 else 1 <= z <= 5,
                        'Unexpected MOVE padding or ADD word-phase annotation')
                reconstructed.append([op, x, y, c, f, 0])
            else:
                require(z == (8 if op == 2 else 0), 'Wrong COPY/ERASE rank field')
                reconstructed.append([op, x, y, c, f, z, 0])
        require(reconstructed == events, 'Forward word differs from original binary records')
        canonical = json.dumps(events, separators=(',', ':')).encode()
        require(hashlib.sha256(canonical).hexdigest() ==
                versions['selected_invocation']['canonical_forward_sha256'],
                'Wrong canonical forward word hash')
        call = next(c for c in template['calls'] if c['stage'] == 2 and c['replica'] == 0)
        require(call['pair'] == 0 and call['orientation'] == 'forward', 'Wrong invocation')
        require(len(call['owners']) == 987, 'Wrong role count')
        require(all(e[-1] == 0 for e in events), 'Unexpected reflected event')
        frames = inputs['frames.json.gz']['frames']
        for e in events:
            require(len(e) == (6 if e[0] < 2 else 7), 'Wrong opcode-dependent record length')
            if e[0] == 1:
                require(e[3] == 1, 'ADD coefficient is not the literal +1')
            elif e[0] == 0:
                require(e[4] == frames[str(e[3])]['dim'] - frames[str(e[2])]['dim'],
                        'MOVE rank annotation disagrees with source dimensions')
        # An independent literal parser checks chronological event preservation;
        # it does not rely on the checkpoint generator's symbolic execution.
        matrix_source = (ROOT / 'MatrixData.lean').read_text()
        definitions = re.findall(
            r'^def (chunk\d+(?:_tail\d+)?) : List Event :=\s*([\s\S]*?)(?=^def |^end |\Z)',
            matrix_source, re.M)
        require(len(dict(definitions)) == len(definitions), 'Duplicate chunk declaration')
        bodies = dict(definitions)
        public = [name for name, _ in definitions if re.fullmatch(r'chunk\d+', name)]
        require(public == ['chunk' + str(i) for i in range(96)], 'Wrong chunk inventory')
        visited, active, expanded = set(), set(), {}

        def expand(name):
            require(name in bodies and name not in active, 'Missing or cyclic list suffix')
            visited.add(name)
            if name in expanded:
                return expanded[name]
            active.add(name)
            body = bodies[name].strip()
            entries = []
            while True:
                item = re.match(r'⟨(\d+),(\d+),(\d+),(true|false)⟩\s*::\s*', body)
                if item is None:
                    break
                o, x, y, bit = item.groups()
                entries.append((int(o), int(x), int(y), bit == 'true'))
                body = body[item.end():]
            if body != '[]':
                require(re.fullmatch(r'chunk\d+_tail\d+', body) is not None,
                        'Unparsed event or suffix text')
                require(body.split('_')[0] == name.split('_')[0], 'Cross-chunk suffix')
                entries.extend(expand(body))
            active.remove(name)
            expanded[name] = entries
            return entries

        actual = []
        for i, name in enumerate(public):
            entries = expand(name)
            require(len(entries) == (200 if i < 95 else 2), 'Changed checkpoint boundary')
            actual.extend(entries)
        require(visited == set(bodies), 'Unreferenced list suffix')
        expected_events = [(e[0], e[1], e[2], bool(e[3] & 1)) for e in events]
        require(actual == expected_events, 'Normalized literal word differs from source')
        require('def forwardWord : List Event := forwardChunks.flatten' in matrix_source,
                'Word definition changed')
        chunks_text = re.search(r'def forwardChunks : List \(List Event\) := \[(.*?)\]',
                                matrix_source, re.S).group(1)
        require(chunks_text.split(',') == ['chunk' + str(i) for i in range(96)],
                'Chunk order changed')

        def run(script, *args):
            result = subprocess.run([sys.executable, str(ROOT / script), *map(str, args)],
                                    text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=300)
            require(result.returncode == 0, script + '\n' + result.stdout)

        run('generate_matrix.py', ROOT / 'inputs/hosted-template.json.gz', work / 'matrix')
        def check_node_modules(directory, prefix):
            generated = sorted(directory.glob(prefix + '*.lean'))
            require([p.name for p in generated] ==
                    [p.name for p in sorted(ROOT.glob(prefix + '*.lean'))],
                    'Wrong generated module inventory: ' + prefix)
            for path in generated:
                require(path.read_bytes() == (ROOT / path.name).read_bytes(),
                        'Non-reproducible generated module: ' + path.name)

        check_node_modules(work / 'matrix', 'MatrixNodes')
        for name in ('MatrixData.lean', 'MatrixCheckpoints.lean', 'MatrixCertificate.lean'):
            require((work / 'matrix' / name).read_bytes() == (ROOT / name).read_bytes(),
                    'Non-reproducible generated file: ' + name)
        run('generate_port_data.py', work / 'geometry.json', '--check')
        run('generate_frame_data.py', work / 'frames.json',
            ROOT / 'inputs/hosted-template.json.gz', '--check')
        run('generate_ownership_data.py', '--template', ROOT / 'inputs/hosted-template.json.gz',
            '--states', work / 'states.json', '--frames', work / 'frames.json',
            '--out', ROOT / 'OwnershipData.lean', '--check')
        run('generate_parent_ownership.py', '--template', ROOT / 'inputs/parent-template.json.gz',
            '--states', work / 'states.json', '--frames', work / 'frames.json',
            '--out', work / 'ParentOwnershipData.lean')
        require((work / 'ParentOwnershipData.lean').read_bytes() ==
                (ROOT / 'ParentOwnershipData.lean').read_bytes(),
                'Non-reproducible original-bank ownership data')
        run('generate_frame_trace.py', ROOT / 'inputs/hosted-template.json.gz',
            work / 'states.json', work / 'FrameTraceData.lean')
        check_node_modules(work, 'FrameTraceNodes')
        for name in ('FrameTraceLiterals.lean', 'FrameTraceCheckpoints.lean', 'FrameTraceData.lean'):
            require((work / name).read_bytes() == (ROOT / name).read_bytes(),
                    'Non-reproducible frame trace data: ' + name)
        run('generate_frame_moves.py', '--template', ROOT / 'inputs/hosted-template.json.gz',
            '--out', ROOT / 'FrameMoveData.lean', '--check')
    return {'status': 'PASS', 'literal_events_in_order': 19002, 'live_roles': 987,
            'source_input_hashes_checked': len(versions['inputs']),
            'scope': 'Reproducible extraction; mathematical certificates are checked separately by Lean.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--receipt', type=Path)
    a = p.parse_args()
    result = check()
    if a.receipt:
        a.receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
