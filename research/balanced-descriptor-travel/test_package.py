"""Test source drift, complete coverage, and an isolated relocated replay."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(path, full=False):
    if full:
        argv = [sys.executable, '-I', '-O', '-B', str(path/'verify.py')]
    else:
        code = ('import importlib.util,sys;'
                'p=sys.argv[1];s=importlib.util.spec_from_file_location("audit",p);'
                'm=importlib.util.module_from_spec(s);sys.modules[s.name]=m;'
                's.loader.exec_module(m);m.load_dispatcher()')
        argv = [sys.executable, '-I', '-O', '-B', '-c', code, str(path/'verify.py')]
    return subprocess.run(argv, cwd=path.parent, text=True, capture_output=True, timeout=180)


def main():
    rejected = 0
    with tempfile.TemporaryDirectory(prefix='balanced-descriptor-') as tmp:
        root = Path(tmp)
        for kind in ('source_edit', 'missing_source', 'empty_inventory', 'extra_file', 'wrong_pin'):
            case = root/kind
            shutil.copytree(ROOT, case)
            if kind == 'source_edit':
                with (case/'vendor/dirty_stride.py').open('a') as f:
                    f.write('\n# source mutation\n')
            elif kind == 'missing_source':
                (case/'vendor/dirty_stride.py').unlink()
            elif kind == 'extra_file':
                (case/'vendor/unlisted.py').write_text('x=1\n')
            else:
                manifest = json.loads((case/'SOURCES.json').read_text())
                if kind == 'empty_inventory':
                    manifest['vendor_sha256'] = {}
                else:
                    manifest['source_head'] = '0'*40
                (case/'SOURCES.json').write_text(json.dumps(manifest))
            result = run(case)
            if result.returncode == 0:
                raise ValueError(f'accepted package fault: {kind}')
            rejected += 1
        case = root/'read only relocated'
        shutil.copytree(ROOT, case)
        before = {str(p.relative_to(case)): p.read_bytes() for p in case.rglob('*') if p.is_file()}
        for p in case.rglob('*'):
            p.chmod(0o555 if p.is_dir() else 0o444)
        case.chmod(0o555)
        try:
            result = run(case, full=True)
            if result.returncode:
                raise ValueError(result.stderr)
            receipt = json.loads(result.stdout)
            if receipt['status'] != 'PASS_BALANCED_DESCRIPTOR_TRAVEL':
                raise ValueError('relocated replay status')
            after = {str(p.relative_to(case)): p.read_bytes() for p in case.rglob('*') if p.is_file()}
            if before != after:
                raise ValueError('relocated source changed')
        finally:
            case.chmod(0o755)
            for p in case.rglob('*'):
                p.chmod(0o755 if p.is_dir() else 0o644)
    print(json.dumps({'status': 'PASS_DESCRIPTOR_PACKAGE', 'faults_rejected': rejected,
                      'read_only_relocated_replay': receipt}, indent=2))


if __name__ == '__main__':
    main()
