"""Reproduce the timed support cap, pilot and exact price receipts."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'source7165'


def unique_object(items):
    result = {}
    for key,value in items:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read_manifest(filename):
    return json.loads((ROOT/filename).read_text(encoding='utf-8'),object_pairs_hook=unique_object)


def main():
    if not __debug__ or sys.implementation.name != 'cpython' or sys.version_info[:2] != (3,12):
        raise SystemExit('Use CPython 3.12 with assertions enabled')
    pins = read_manifest('INPUTS.json')
    actual = {p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file()}
    if pins.keys() != actual:
        raise ValueError('source paths disagree with declared manifest')
    for name,record in pins.items():
        if sha256((SOURCE/name).read_bytes()).hexdigest() != record['sha256']:
            raise ValueError(f'changed exact source: {name}')
    frozen = read_manifest('RECEIPTS.json')
    commands = {
        'paid_delivery': ['paid_delivery.py'],
        'temporal_cap_one': ['temporal_barrier.py','--cap','1'],
        'temporal_barriers': ['temporal_barrier.py'],
    }
    assert frozen['stdout_sha256'].keys() == commands.keys()
    for name,(script,*args) in commands.items():
        argv = [sys.executable,'-I','-B',str(ROOT/'checks'/script),str(SOURCE),*args]
        output = subprocess.run(argv,check=True,capture_output=True).stdout
        if sha256(output).hexdigest() != frozen['stdout_sha256'][name]:
            raise ValueError(f'changed frozen receipt: {name}')
        print(f'PASS {name}',flush=True)
    print('PASS_P104_SERIAL_TEMPORAL_SUPPORT_BOUND')


if __name__ == '__main__':
    main()
