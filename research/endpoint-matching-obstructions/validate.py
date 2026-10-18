"""Relocation, recompression and repinned corruption controls for the package."""
if not __debug__:
    raise SystemExit('Run without -O: the inherited model requires assertions.')

from hashlib import sha256
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(directory, expected=None, optimized=False):
    command = [sys.executable, '-I', '-B']+(['-O'] if optimized else [])+[str(directory/'verify.py')]
    result = subprocess.run(command, capture_output=True, text=True, timeout=30, cwd=directory.parent)
    if expected is None:
        if result.returncode:
            raise ValueError('Relocated verification failed')
        return json.loads(result.stdout)
    if result.returncode == 0 or expected not in result.stdout+result.stderr:
        raise ValueError('Corrupted package was not rejected for the intended reason')
    return None


def repin(directory, payload):
    raw = (json.dumps(payload, separators=(',', ':'))+'\n').encode()
    (directory/'proofs.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    manifest = json.loads((directory/'MANIFEST.json').read_bytes())
    manifest['payloads']['proofs.json.gz'] = sha256(raw).hexdigest()
    (directory/'MANIFEST.json').write_bytes((json.dumps(manifest, indent=2)+'\n').encode())


def main():
    counts = {}
    with tempfile.TemporaryDirectory(prefix='endpoint proof controls ') as temporary:
        parent = Path(temporary)
        def fresh(name):
            out = parent/name
            out.mkdir()
            for source in ROOT.iterdir():
                if source.is_file():
                    shutil.copyfile(source, out/source.name)
            return out
        moved = fresh('relocated path with spaces')
        baseline = run(moved)
        counts['relocated_replay'] = 1
        for name in ('words.json.gz', 'proofs.json.gz'):
            source = gzip.decompress((moved/name).read_bytes())
            (moved/name).write_bytes(gzip.compress(source, compresslevel=1, mtime=123))
        if run(moved) != baseline:
            raise ValueError('Equivalent gzip payload changed mathematics')
        counts['recompressed_payloads'] = 2
        run(moved, expected='Run without -O', optimized=True)
        counts['optimized_mode_rejected'] = 1
        source = fresh('altered source')
        (source/'boolean.py').write_bytes((source/'boolean.py').read_bytes()+b'\n# corruption control\n')
        run(source, expected='Source hash mismatch')
        counts['source_corruption_rejected'] = 1
        altered = fresh('altered payload')
        raw = gzip.decompress((altered/'proofs.json.gz').read_bytes())+b' '
        (altered/'proofs.json.gz').write_bytes(gzip.compress(raw, mtime=0))
        run(altered, expected='Payload hash mismatch')
        counts['payload_corruption_rejected'] = 1
        missing = fresh('repinned missing coverage')
        data = json.loads(gzip.decompress((missing/'proofs.json.gz').read_bytes()))
        data['cases'].pop()
        repin(missing, data)
        run(missing, expected='Incomplete remaining-word coverage')
        counts['repinned_missing_case_rejected'] = 1
        wrong = fresh('repinned resolution')
        data = json.loads(gzip.decompress((wrong/'proofs.json.gz').read_bytes()))
        case = next(c for c in data['cases'] if c['kind'] == 'endpoint_matching')
        case['steps'][0]['support']['resolution'][-1]['clause'] = [1]
        repin(wrong, data)
        run(wrong, expected='Wrong learned clause')
        counts['repinned_resolution_rejected'] = 1
    print(json.dumps({'status': 'PASS_ENDPOINT_MATCHING_PACKAGE', 'controls': counts}, sort_keys=True))


if __name__ == '__main__':
    main()
