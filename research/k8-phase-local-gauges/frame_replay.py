"""Run the unchanged source-pinned emitted scalar/frame/wrapper checker."""
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('verify', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def main():
    receipt, witnesses = v.compute()
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    lib = v.engine()
    with tarfile.open(v.ROOT / lib.ARCHIVE) as archive:
        word = archive.extractfile('slots/local/CANONICAL-WORD.json.gz').read()
    for prefix in ('', 'pr1214_', 'wrapped_'):
        programs = {orientation: witnesses[prefix + orientation]
                    for orientation in ('forward', 'backward')}
        with tempfile.TemporaryDirectory(prefix='k8-phase-gauges-') as directory:
            out = Path(directory)
            (out / 'CANONICAL-WORD.json.gz').write_bytes(word)
            (out / 'LOCAL-PROGRAMS.json.gz').write_bytes(gzip.compress(v.canonical(programs), mtime=0))
            # The historical checker uses asserts. Deliberately do not inherit -O.
            command = [sys.executable, '-I', '-B', str(v.ROOT / pins['frame_checker']['path']), str(out)]
            run = subprocess.run(command, check=True, capture_output=True, text=True)
            result = json.loads((out / 'INDEPENDENT-LOCAL-REPLAY.json').read_text())
            v.need(result['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'frame status')
            v.need(len(result['negative_controls_rejected']) == 25, 'frame control coverage')
            print(prefix or 'selected_', result['status'], len(result['negative_controls_rejected']), 'controls')
            if '--write' in sys.argv:
                # Container hashes are run metadata; stable payload digests live in CERTIFICATE.
                (HERE / ((prefix or 'selected_') + 'FRAME-RECEIPT.json')).write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
