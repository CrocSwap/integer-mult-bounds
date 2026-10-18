"""Public CLI export and mutation checks; no inherited assertions required."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(value, why):
    if not value:
        raise ValueError(why)


def cli(package, good, *args):
    env = os.environ.copy()
    env['PATH'] = ''
    env['PYTHONOPTIMIZE'] = '2'
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *args],
                            cwd=package, env=env, capture_output=True, text=True, timeout=90)
    need((result.returncode == 0) == good, result.stdout+result.stderr)
    return result.stdout+result.stderr


def main():
    with tempfile.TemporaryDirectory(prefix='padding-tape-export-') as directory:
        package = Path(directory)/'package'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        def digest():
            return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in package.iterdir() if p.is_file()}
        before = digest()
        cli(package, True)
        need(before == digest(), 'replay mutated package bytes')
        receipt = (package/'RESULT.json').read_bytes()
        broken = json.loads(receipt)
        broken['tapes'] = True
        (package/'RESULT.json').write_text(json.dumps(broken), encoding='utf-8')
        need('typed result receipt' in cli(package, False), 'typed receipt mutation diagnosis')
        (package/'RESULT.json').write_bytes(receipt)
        target = package/'tapes.py'
        original = target.read_text(encoding='utf-8')
        fragment = '            copy_template(self.template, self.genuine)\n'
        need(original.count(fragment) == 1, 'mutant has one physical reset target')
        target.write_text(original.replace(fragment, ''), encoding='utf-8')
        cli(package, False)
        target.write_text(original, encoding='utf-8')
        need('output already exists' in cli(package, False, '--out', str(package/'RESULT.json')), 'exclusive output refusal')
    print('PASS_PADDING_TAPE_EXPORT read_only=1 empty_PATH=1 fault_rejections=3')


if __name__ == '__main__':
    main()
