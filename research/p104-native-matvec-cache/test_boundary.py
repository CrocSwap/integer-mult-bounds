"""Source drift rejects before import; a Git-free export replays read-only."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='p104-cache-boundary-') as tmp:
        root = Path(tmp)
        package = root/'research/p104-native-matvec-cache'
        shutil.copytree(P, package)
        for item in json.loads((P/'SOURCES.json').read_text())['files']:
            if item.get('usage') == 'input':
                dest = root/item['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT/item['path'], dest)
        def digests():
            return {str(f.relative_to(root)): hashlib.sha256(f.read_bytes()).hexdigest()
                    for f in root.rglob('*') if f.is_file()}
        before = digests()
        command = [sys.executable, '-I', '-O', '-B', str(package/'accelerated.py')]
        result = subprocess.run(command, text=True, capture_output=True, timeout=120, cwd=root)
        if result.returncode or before != digests():
            raise ValueError('Git-free unchanged export failed: '+result.stdout+result.stderr)
        cases = ['check_native.py', 'vendor/native_verify.py', 'inputs/LOWRANK-WITNESS.json', 'NATIVE-RECIPES.json.gz']
        for name in cases:
            path = root/'research/p104-native-channel'/name
            original = path.read_bytes()
            path.write_bytes(original+b'\nCHANGED_SOURCE_BOUNDARY\n')
            result = subprocess.run(command, text=True, capture_output=True, timeout=10, cwd=root)
            path.write_bytes(original)
            if result.returncode == 0 or 'source drift before executable import:' not in result.stderr:
                raise ValueError('source drift did not fail at boundary: '+name)
        if before != digests():
            raise ValueError('export mutation not restored')
    print('PASS_P104_CACHE_BOUNDARY source_mutants=4 git_free_export=unchanged')


if __name__ == '__main__':
    main()
