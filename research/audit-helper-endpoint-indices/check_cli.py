"""Public guard relocation and fail-before-import source corruption checks."""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(argv, success, marker):
    r = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    if (r.returncode == 0) != success or marker not in r.stdout+r.stderr:
        raise ValueError(repr((r.returncode, r.stdout, r.stderr)))


def main():
    with tempfile.TemporaryDirectory(prefix='endpoint-cli-') as temporary:
        root = Path(temporary)
        package = root/'research/audit-helper-endpoint-indices'
        package.parent.mkdir(parents=True)
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage'] == 'input':
                dest = root/row['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/row['path'], dest)
        command = [sys.executable, '-I', '-O', '-B', str(package/'guard.py')]
        run(command+[str(package/'inputs/BASE-WORD.json.gz')], True, 'PASS_HELPER_ENDPOINT_INDICES')
        base = json.loads(gzip.decompress((package/'inputs/BASE-WORD.json.gz').read_bytes()))
        for key in ('-592', '704', '0273', '+273', '112'):
            changed = json.loads(json.dumps(base))
            changed['helper_final'][key] = [256, 128, 64, 32, 16, 8, 4, 2, 1]
            path = root/'mutant.json'
            path.write_text(json.dumps(changed))
            run(command+[str(path)], False, 'FAIL_HELPER_ENDPOINT_INDICES')
        source = root/'research/gauge44-frames-x/independent/audit_local.py'
        original = source.read_bytes()
        source.write_bytes(b'raise RuntimeError("EXECUTED_CORRUPTED_SOURCE")\n'+original)
        verify = [sys.executable, '-I', '-O', '-B', str(package/'verify.py')]
        run(verify, False, 'source hash: research/gauge44-frames-x/independent/audit_local.py')
        source.write_bytes(original)
        vendor = package/'source/cut_guard.py'
        vendor.write_bytes(vendor.read_bytes()+b'\n')
        run(verify, False, 'source hash: source/cut_guard.py')
    print('PASS_ENDPOINT_GUARD_CLI relocated=1 semantic_rejections=5 source_rejections=2')


if __name__ == '__main__':
    main()
