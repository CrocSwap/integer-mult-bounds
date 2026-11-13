"""Run both exact outward ADD engines with independent process limits."""
from gzip import decompress
from hashlib import sha256
from json import loads
from os import killpg
from pathlib import Path
from signal import SIGKILL
from subprocess import PIPE, Popen, TimeoutExpired
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
FILES = {'7481-WORD.json.gz','7481-APPLICATION.json','7003-slide_stops.py','pricing.py',
         'check_outward_contact.py','independent_outward.py','PROVENANCE.json',
         'receipts/PRIMARY.jsonl.gz','receipts/INDEPENDENT.json'}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def parse(raw):
    return loads(raw, object_pairs_hook=unique)


def authenticate(raw, digest):
    assert sha256(raw).hexdigest() == digest, 'changed bytes'


def exact_run(*args):
    process = Popen([executable,'-I','-B',*map(str,args)], cwd=ROOT,
                    stdout=PIPE, stderr=PIPE, start_new_session=True)
    try:
        output, errors = process.communicate(timeout=30)
    except TimeoutExpired:
        killpg(process.pid, SIGKILL)
        process.communicate()
        raise AssertionError('unresolved process cap') from None
    assert process.returncode == 0 and not errors, errors.decode(errors='replace')
    return output


def compare(primary, independent):
    assert len(primary) == 959
    assert primary[-1] == {'status':'SCOPED_EXHAUSTION','tested':958}
    keys = {(row['role'],*row['moves'],row['contact']) for row in primary[:-1]}
    assert len(keys) == 958
    assert all(row['earlier'] is None and row['later'] is None for row in primary[:-1])
    assert independent['cases'] == 958 and independent['cap_seconds'] == 30
    assert independent['unresolved'] == independent['survivors'] == 0
    assert independent['all_case_ids_agree'] is True


def must_reject(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('mutation passed')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3,12)
    pins = parse((ROOT/'PINS.json').read_bytes())
    assert set(pins) == FILES
    files = {name:(ROOT/name).read_bytes() for name in sorted(FILES)}
    for name, raw in files.items():
        authenticate(raw, pins[name])
    primary = exact_run(ROOT/'check_outward_contact.py','--input-root',ROOT)
    assert primary == decompress(files['receipts/PRIMARY.jsonl.gz'])
    independent = parse(exact_run(ROOT/'independent_outward.py'))
    assert independent == parse(files['receipts/INDEPENDENT.json'])
    rows = [parse(row) for row in primary.splitlines()]
    compare(rows, independent)
    raw = files['7481-WORD.json.gz']
    must_reject(lambda: authenticate(bytes([raw[0]^1])+raw[1:],pins['7481-WORD.json.gz']))
    must_reject(lambda: parse('{"word":1,"word":2}'))
    must_reject(lambda: compare(rows,dict(independent,survivors=1)))
    print('PASS_FIXED_ROUTE_OUTWARD_ADD: 958 cases, zero placements')


if __name__ == '__main__':
    main()
