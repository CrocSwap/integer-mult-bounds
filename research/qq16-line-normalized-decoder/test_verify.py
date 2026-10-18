"""Git-free export, source-first execution, typed receipts and exclusive writes."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='qq16-line-export-') as temp:
        root = Path(temp) / 'checkout'
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        pins = json.loads((HERE / 'SOURCES.json').read_text())
        for row in pins['files']:
            if row['usage'] == 'input':
                path = root / row['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], path)
        def run(*args, ok=True, needle=None):
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py'), *args],
                                    cwd=root, capture_output=True, text=True, encoding='utf-8', timeout=240)
            need((result.returncode == 0) == ok, result.stdout + result.stderr)
            if needle:
                need(needle in result.stdout + result.stderr, result.stdout + result.stderr)
            return result
        before = snapshot(root)
        run(needle='PASS_QQ16_LINE_NORMALIZED_DECODER')
        need(snapshot(root) == before, 'read-only Git-free replay wrote files')
        source = package / 'vendor/pr2681/verify.py'
        original = source.read_bytes()
        source.write_bytes(b"raise RuntimeError('EXECUTED_UNAUTHENTICATED_SOURCE')\n" + original)
        result = run(ok=False, needle='retained source SHA256')
        need('EXECUTED_UNAUTHENTICATED_SOURCE' not in result.stdout + result.stderr,
             'changed predecessor executed before binding')
        source.write_bytes(original)
        inventory = package / 'PREDECESSORS.json'
        original = inventory.read_bytes()
        data = json.loads(original)
        data['files'].pop()
        inventory.write_text(json.dumps(data))
        run(ok=False, needle='complete retained source set')
        inventory.write_bytes(original)
        evidence = package / 'RESULT.json'
        original = evidence.read_bytes()
        data = json.loads(original)
        data['invoice']['rank_eight_children'] = False
        evidence.write_text(json.dumps(data))
        run(ok=False, needle='typed complete receipt mismatch')
        evidence.write_bytes(original)
        run('--write', ok=False, needle='output already exists')
        need(snapshot(root) == before, 'failed checks changed export')
        word = package / 'WORD.json'
        expected_word = json.loads(word.read_text())
        expected_result = json.loads(evidence.read_text())
        word.unlink()
        evidence.unlink()
        run('--write', needle='PASS_QQ16_LINE_NORMALIZED_DECODER')
        need(json.loads(word.read_text()) == expected_word and json.loads(evidence.read_text()) == expected_result,
             'exclusive regeneration changed mathematical evidence')
        regenerated = snapshot(root)
        run('--write', ok=False, needle='output already exists')
        need(snapshot(root) == regenerated, 'exclusive output overwritten')
    print('PASS_QQ16_LINE_EXPORT groups=4')


if __name__ == '__main__':
    main()
