#!/usr/bin/env python3
"""Pin complete repository-local H6 runtime import closure and cited data.

This does not replay the selected supplier or the H6 construction theorem.
"""
from pathlib import Path
import hashlib
import io
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '0b1cccf86e2f5132ed286a26ef0a681a495740ea'
FORK = 'b496aed769dd724cd1ff6b921cade626562be27b'
PINFILE = HERE / 'PINS.json'
RUNTIME = [
 'research/niemeier-lattices/workbench/paid-controller/banked.py',
 'research/niemeier-lattices/workbench/paid-controller/portable.py',
 'research/niemeier-lattices/code/costs.py',
 'research/leech-lattice/code/screen.py',
 'research/niemeier-lattices/code/e8_cubed.py',
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_bindings(root, pins):
    for name, entry in pins.items():
        require(digest(root / name) == entry['sha256'], 'Source/data hash mismatch: ' + name)


def main():
    pins = json.loads(PINFILE.read_text())
    check_bindings(ROOT, pins)
    for name, entry in pins.items():
        blob = subprocess.run(['git', 'show', entry['commit'] + ':' + name],
                              cwd=ROOT, check=True, capture_output=True).stdout
        require(hashlib.sha256(blob).hexdigest() == entry['sha256'], 'Commit pin: ' + name)
        if name.startswith(('research/niemeier-lattices/', 'research/leech-lattice/')):
            peer = subprocess.run(['git', 'show', FORK + ':' + name], cwd=ROOT,
                                  check=True, capture_output=True).stdout
            require(peer == blob, 'Inherited dependency changed in fork: ' + name)
    selected = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    packet = json.loads((ROOT / 'research/community-efficient500-audit/packets/1424.json').read_text())
    review = (ROOT / 'docs/research/community-efficient500-review.md').read_text()
    require('836330098538459/500000000000000000' == selected['kappa'], 'Selected comparison pin')
    require(packet['head'] == 'bfe423c24555baf35dab991a8d6fe723a038945c', 'Pending packet head')
    require(any('#1424' in line and 'pending PR1319' in line for line in review.splitlines()),
            'Pending 1424 distinction')
    with tempfile.TemporaryDirectory(prefix='h6-source-relocation-') as tmp:
        relocated = Path(tmp) / 'unrelated-location'
        for name in pins:
            target = relocated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        external = Path(tmp) / 'external-cwd'
        external.mkdir()
        command = [sys.executable, '-I', '-B', str(relocated / 'research/h6-banked-breakeven/price_h6.py')]
        replay = subprocess.run(command, cwd=external, capture_output=True, text=True, check=True)
        expected = (ROOT / 'research/h6-banked-breakeven/outputs/price_h6.txt').read_text()
        require(replay.stdout == expected, 'Relocated predecessor price output differs')
        check_bindings(relocated, pins)
        mutation = relocated / 'research/leech-lattice/code/screen.py'
        mutation.write_bytes(mutation.read_bytes() + b'\n# negative control\n')
        detected = False
        try:
            check_bindings(relocated, pins)
        except ValueError as exc:
            detected = 'screen.py' in str(exc)
        require(detected, 'Transitive-engine hash mutation detected')
    # Loading both endpoints inspects the closure without executing saved outputs.
    sys.path.insert(0, str(ROOT / 'research/niemeier-lattices/workbench/paid-controller'))
    import banked
    sys.path.insert(0, str(ROOT / 'research/niemeier-lattices/code'))
    import e8_cubed
    modules = [banked, sys.modules['portable'], banked.c, banked.c.engine, e8_cubed]
    observed = sorted(str(Path(module.__file__).resolve().relative_to(ROOT)) for module in modules)
    require(observed == sorted(RUNTIME), 'Unexpected direct/transitive import closure')
    # Independently bind the geometric intermediate used by structure2/walsh.
    import numpy as np
    _, _, ports, profiles = e8_cubed.construct_shell()
    P = ports[(profiles & 4) == 0, :16].astype(np.int64)
    buffer = io.BytesIO()
    np.save(buffer, P)
    p_sha = hashlib.sha256(buffer.getvalue()).hexdigest()
    require(p_sha == '349e84668d1528783aa22bc650837533bcc6134052d9dbfba87fb05aa54911fd', 'P.npy hash')
    audits = sorted((ROOT / 'research/h6-independent-audit').glob('*/*.py'))
    result = dict(status='PASS_PINNED_SOURCE_IMPORT_AND_RELOCATION_BINDINGS',
        base=BASE, fork=FORK, pinned_files=len(pins),
        repository_runtime_import_closure=observed,
        imported_dependencies_omitted_from_original_SOURCES=[RUNTIME[1], RUNTIME[3]],
        relocation=dict(predecessor_price='IDENTICAL_SAVED_STDOUT', isolated_python=True,
                        external_cwd=True, transitive_source_mutation_detected=True),
        geometric_intermediate=dict(shape=list(P.shape), npy_sha256=p_sha),
        saved_outputs={name: entry['sha256'] for name, entry in pins.items()
                       if name.startswith('research/h6-banked-breakeven/outputs/')},
        current_selected=dict(kappa=selected['kappa'], source='certificates/selected-result.json'),
        pending_1424=dict(head=packet['head'], title=packet['title'], status='PINNED_PENDING_COMPARISON_ONLY'),
        audit_script_sha256={str(path.relative_to(ROOT)): digest(path) for path in audits},
        environment=dict(python=sys.version.split()[0], numpy=np.__version__),
        limits=['Repository-local import closure of executed H6 calculator, bank helpers and geometry only.',
                'Saved structure/Walsh outputs are frozen predecessor evidence; their statements are adjudicated by the separate exhaustive audit.',
                'Relocation executed predecessor price only; invoice/helper/Walsh audit relocation not executed here.',
                'No selected-supplier cold replay, pending PR admission, all-stage optimizer replay, capacity theorem or construction claim.'])
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
