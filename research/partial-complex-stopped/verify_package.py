"""Reproduce the bundled arithmetic and bind it to the finite Lean inputs."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    if sys.flags.optimize:
        raise RuntimeError('Run without -O: assertions must remain enabled')
    manifest = json.loads((HERE/'MANIFEST.json').read_text())
    for rel, digest in manifest['package_sha256'].items():
        assert hashlib.sha256((HERE/rel).read_bytes()).hexdigest() == digest, rel
    selection = json.loads((HERE/'schedule/selection.json').read_text())
    frames = {u: selection['frames'][i] for u, i in selection['role_frame_ids']}
    ranks = json.loads(gzip.decompress((HERE/'inputs/selected-ranks.json.gz').read_bytes()))
    assert set(frames) == {u for u, _, _, _ in ranks['roles']}
    assert all(len(frames[u]) == d for u, _, d, _ in ranks['roles'])
    receipt = json.loads((HERE/'schedule/receipt.json').read_text())
    raw = json.loads((HERE/'inputs/complex.json').read_text())
    digest = hashlib.sha256(json.dumps(raw['hist'], separators=(',', ':')).encode()).hexdigest()
    assert receipt['histogram_sha256'] == digest
    assert receipt['selection_sha256'] == hashlib.sha256((HERE/'schedule/selection.json').read_bytes()).hexdigest()
    assert receipt['selected_roles'] == raw['active_sigma_roles']
    for name in ('bit.json', 'complex.json'):
        assert (HERE/'inputs'/name).read_bytes() == (HERE/'kernel/inputs'/name).read_bytes()
    assert (HERE/'certificate.json').read_bytes() == (HERE/'kernel/inputs/assembly.json').read_bytes()
    with tempfile.TemporaryDirectory(prefix='partial-complex-arithmetic-') as tmp:
        out = Path(tmp)/'certificate.json'
        subprocess.run([sys.executable, str(HERE/'certify_partial.py'), '--output', str(out)], check=True)
        assert out.read_bytes() == (HERE/'certificate.json').read_bytes(), 'certificate drift'
    subprocess.run([sys.executable, str(HERE/'phase_controls.py')], check=True)
    print('PASS portable assembly, schedule bindings, kernel inputs and exact phase controls')


if __name__ == '__main__':
    main()
