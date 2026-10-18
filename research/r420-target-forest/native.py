"""Unchanged predecessor C++ legality and finite bridged-column checks.
Oscar Fennell, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys


def run(root, work, minimum_records):
    package = root / 'research/e8-bit-carrier-skeleton'
    code = package / 'code/bit'
    checkers = code / 'checkers'
    boost = Path(os.environ.get('BOOST_INCLUDE', '/usr/include'))
    if not (boost / 'boost/multiprecision/cpp_int.hpp').is_file():
        raise RuntimeError('Set BOOST_INCLUDE to the directory containing boost/multiprecision/cpp_int.hpp')
    common = [os.environ.get('CXX', 'c++'), '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9',
              '-DVPORTS=120', '-DRHELP=420', '-I'+str(package/'portable-include'),
              '-I'+str(checkers), '-I'+str(boost)]
    def command(args):
        proc = subprocess.run([str(a) for a in args], capture_output=True, text=True)
        if proc.returncode:
            raise RuntimeError('Command failed: '+str(args)+'\n'+proc.stderr[-4000:])
        return proc
    legality = work / 'legality'
    command(common + ['-o', legality, checkers/'legality_h.cpp'])
    bins = {}
    for pairs in (2, 4, 5):
        exe = work / ('columns'+str(pairs))
        command(common + ['-DKPAIRS='+str(pairs), '-o', exe, checkers/'columns_k.cpp'])
        bins[pairs] = exe
    receipts = {}
    for name in ('baseline', 'forest'):
        directory = work / name
        cin, cout = directory/'cin', directory/'cout'
        command([sys.executable, '-I', '-B', code/'regression/stage_cohort.py', directory, directory, cin, cout])
        command([legality, cin, cout, cout/'legality.json'])
        legal = json.loads((cout/'legality.json').read_text())
        if legal['common_frame_ADDs'] != (26916 if name == 'baseline' else 22132):
            raise RuntimeError('native ADD count')
        stages = []
        for pairs, exe in bins.items():
            out = cout / ('columns'+str(pairs)+'.json')
            command([exe, cout/'COHORT249-RECORDS.bin', out])
            report = json.loads(out.read_text())
            if not all(c['rejected'] for c in report['negative_controls']):
                raise RuntimeError('bridge control accepted')
            if report['formal_columns_checked'] != 2*pairs*120+420 or report['payload_prefix_bits'] > 104:
                raise RuntimeError('native column count or budget')
            expected = (144651, 2270064) if name == 'baseline' else (144651, 9640706)
            actual = tuple(int(p['cancellation_free_signed_row_l1_upper']) for p in report['signed_lift_prefix'])
            if actual != expected:
                raise RuntimeError('native prefix disagreement')
            stages.append({'stages':2*pairs+1,'columns':report['formal_columns_checked'],
                           'bridge_controls':len(report['negative_controls']),
                           'payload_bits':report['payload_prefix_bits']})
        receipts[name] = {'ADDs':legal['common_frame_ADDs'], 'records':legal['records'], 'rank_mass':legal['rank_mass'], 'checks':stages}
    # Keep the mathematically cheapest nominated tree as a genuine native budget rejection.
    minimum = work/'minimum.bin'
    minimum.write_bytes(b''.join(struct.pack('<6i', *r) for r in minimum_records))
    result = subprocess.run([str(bins[4]), str(minimum), str(work/'rejected.json')], capture_output=True, text=True)
    if result.returncode == 0 or 'payloadfiniteprefix2^104' not in result.stderr:
        raise RuntimeError('native minimum-tree budget control did not fail as intended')
    # A missing target restoration has legal geometry; it must fail scalar formal columns.
    raw = list(struct.iter_unpack('<6i', (work/'forest/249-records.bin').read_bytes()))
    index = max(i for i,r in enumerate(raw) if r[0] == 1 and r[5] == 1)
    del raw[index]
    corrupted = work/'missing-restore.bin'
    corrupted.write_bytes(b''.join(struct.pack('<6i', *r) for r in raw))
    for pairs, exe in bins.items():
        result = subprocess.run([str(exe), str(corrupted), str(work/'bad.json')], capture_output=True, text=True)
        if result.returncode == 0 or 'local defining-decoder full formal column' not in result.stderr:
            raise RuntimeError('native restoration control did not fail as intended')
    print('NATIVE_RECEIPT '+json.dumps(receipts, sort_keys=True))
    print('PASS_NATIVE_FOREST baseline_and_forest stages=5,9,11 bridge_controls=96 budget_control=1 restoration_controls=3')
