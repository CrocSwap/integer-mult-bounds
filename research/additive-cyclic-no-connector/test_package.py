"""Fail-closed package controls and a full read-only optimized relocation."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(100000)


def require(value, message):
    if not value:
        raise ValueError(message)


def run(root, *args, code=None):
    command = [sys.executable, '-I', '-O', '-B']
    command += ['-c', code] if code is not None else [str(root/'verify.py'), *map(str, args)]
    return subprocess.run(command, cwd=root.parent, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=2400)


def rebind(root, name):
    path = root/'MANIFEST.json'
    record = json.loads(path.read_text())
    record['files'][name] = hashlib.sha256((root/name).read_bytes()).hexdigest()
    path.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out:
        require(not args.out.exists() and not args.out.resolve().is_relative_to(P), 'fresh external report')
    results = []
    with tempfile.TemporaryDirectory(prefix='additive package controls ') as temporary:
        base = Path(temporary)
        def copy(name):
            root = Path(shutil.copytree(P, base/name))
            # The supplied package may itself be read-only. Only these
            # disposable test fixtures must permit deliberate corruption.
            root.chmod(0o755)
            for path in root.rglob('*'):
                path.chmod(0o755 if path.is_dir() else 0o644)
            return root
        def rejection(name, mutate, *, full=False, code=None):
            root = copy(name)
            mutate(root)
            output = base/(name+' output.json')
            result = run(root, '--out', output, code=code(root) if code else None) if full or code else run(root, '--bindings-only')
            require(result.returncode != 0, 'mutation accepted: '+name)
            require(not output.exists(), 'failed verification wrote a receipt: '+name)
            results.append(dict(name=name, rejected=True, terminal=result.stdout.strip().splitlines()[-1]))
            print('PASS package control', name, flush=True)

        rejection('missing manifest', lambda root: (root/'MANIFEST.json').unlink())
        rejection('altered implementation', lambda root: (root/'gaussian.py').write_text((root/'gaussian.py').read_text()+'\n# altered\n'))
        rejection('extra file', lambda root: (root/'undeclared.txt').write_text('unbound\n'))
        rejection('missing source', lambda root: (root/'vendor/PR621-PROOF.md').unlink())
        def wrong_source(root):
            file = root/'vendor/PR621-PROOF.md'
            file.write_text(file.read_text()+'\nchanged\n')
            rebind(root, 'vendor/PR621-PROOF.md')
        rejection('source hash independent of manifest', wrong_source)
        def wrong_blob(root):
            file = root/'SOURCE-PINS.json'
            value = json.loads(file.read_text())
            value['sources'][0]['git_blob'] = '0'*40
            file.write_text(json.dumps(value)+'\n')
            rebind(root, 'SOURCE-PINS.json')
        rejection('source Git object independent of manifest', wrong_blob)
        rejection('duplicate manifest key', lambda root: (root/'MANIFEST.json').write_text('{"files":{},"files":{}}\n'))
        rejection('symlink injection', lambda root: (root/'linked.txt').symlink_to(root/'README.md'))
        rejection('preloaded module substitution', lambda root: None, code=lambda root:
                  "import sys,types,runpy; m=types.ModuleType('gaussian'); m.__file__='/not/the/package.py'; "
                  "sys.modules['gaussian']=m; sys.argv=["+repr(str(root/'verify.py'))+"] ; runpy.run_path(sys.argv[0],run_name='__main__')")
        def wrong_receipt(root):
            file = root/'EXPECTED.json.gz'
            value = json.loads(gzip.decompress(file.read_bytes()))
            require(value['additive_budget']['rows'][0]['p'] == 0, 'known zero budget field')
            value['additive_budget']['rows'][0]['p'] = False
            file.write_bytes(gzip.compress((json.dumps(value, indent=2, sort_keys=True)+'\n').encode(), mtime=0))
            rebind(root, 'EXPECTED.json.gz')
        rejection('false receipt boolean integer confusion', wrong_receipt, full=True)

        root = copy('existing output')
        existing = base/'existing.json'
        existing.write_bytes(b'preserve this exact output\n')
        result = run(root, '--out', existing)
        require(result.returncode != 0 and existing.read_bytes() == b'preserve this exact output\n', 'existing output preservation')
        results.append(dict(name='existing output preserved', rejected=True))
        print('PASS package control existing output preserved', flush=True)

        root = copy('read only isolated relocation')
        for file in root.rglob('*'):
            file.chmod(0o555 if file.is_dir() else 0o444)
        root.chmod(0o555)
        output = base/'relocated receipt.json'
        try:
            result = run(root, '--out', output)
            require(result.returncode == 0, 'full relocated replay failed: '+result.stdout[-2000:])
            require(output.read_bytes() == gzip.decompress((P/'EXPECTED.json.gz').read_bytes()), 'relocated receipt byte equality')
            require(run(root, '--bindings-only').returncode == 0, 'read-only package unchanged after replay')
        finally:
            root.chmod(0o755)
            for directory in root.rglob('*'):
                if directory.is_dir():
                    directory.chmod(0o755)
        results.append(dict(name='full read-only isolated optimized relocation', passed=True,
                            receipt_sha256=hashlib.sha256(output.read_bytes()).hexdigest()))
        print('PASS full read-only isolated optimized relocation', flush=True)
    report = dict(status='PASS_ADDITIVE_PACKAGE', controls=results, rejected=11, full_readonly_replay=True)
    if args.out:
        with args.out.open('x') as handle:
            handle.write(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('PASS_ADDITIVE_PACKAGE rejected=11 full_readonly_replay=True')


if __name__ == '__main__':
    main()
