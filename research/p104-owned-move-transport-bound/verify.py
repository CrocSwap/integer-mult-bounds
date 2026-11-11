"""Reproduce the exact charged owned-MOVE price and span checks offline."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / 'inputs'
CHECKS = ROOT / 'checks'


def main():
    if sys.implementation.name != 'cpython' or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit('Use CPython 3.12 with assertions enabled')
    pins = json.loads((ROOT / 'INPUTS.json').read_text())
    for record in pins:
        data = (INPUTS / record['path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError(f"changed source: {record['path']}")
    receipts = json.loads((ROOT / 'RECEIPTS.json').read_text())
    peer = INPUTS / 'peer'
    caller = INPUTS / 'caller' / 'CALLER.json'
    interval = INPUTS / 'caller' / 'interval_gate.py'
    word = peer / 'research/p104-rank8-exit-funded-split/WORD.json.gz'
    owned = CHECKS / 'owned.py'
    side = CHECKS / 'side_rows.py'
    donor = CHECKS / 'donor_intervals.py'
    names = set()

    def run(label, script, *args):
        data = subprocess.run([sys.executable, '-I', '-B', str(CHECKS / script), *map(str,args)],
                              stdout=subprocess.PIPE, check=True).stdout
        if hashlib.sha256(data).hexdigest() != receipts[label]['stdout_sha256']:
            raise ValueError(f'changed scientific output: {label}')
        names.add(label)
        print(f'PASS {label}', flush=True)
        return data

    with TemporaryDirectory() as path:
        saved = Path(path)
        saved_owned = saved / 'owned.json'
        saved_side = saved / 'side.json'
        saved_owned.write_bytes(run('owned', 'owned.py', peer, caller, interval))
        run('direct_sum', 'direct_sum.py', saved_owned, interval)
        saved_side.write_bytes(run('side_rows', 'side_rows.py', peer, caller, interval, owned))
        run('pair_relations', 'pair_relations.py', word, saved_side)
        run('donor_intervals', 'donor_intervals.py', peer, caller, interval, owned)
        for count in (1, 2):
            run(f'charged_charts_{count}', 'charged_charts.py', peer, caller, interval, owned, side, donor,
                '--source-count', count)
        run('multi_gate', 'multi_gate.py', peer, caller, interval, owned, side, donor,
            CHECKS / 'charged_charts.py')
    assert names == receipts.keys()
    print('PASS_P104_OWNED_MOVE_TRANSPORT_BOUND')


if __name__ == '__main__':
    main()
