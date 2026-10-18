# SPDX-License-Identifier: Apache-2.0
"""Check the opt-in parallel layer-end controls against the pinned serial reference.

Usage: python3 -B research/layer-end-controls-parallel/verify.py --work NEW_EMPTY_DIR [--jobs N] [--serial]

1. Extracts the pinned U8 barch word from the selected T37 archive (payload = PR870 RECIPE-U8 expect_sha256).
2. Runs controls_parallel.py: its COLD-END-CONTROLS.json must report PASS with the archived receipt's
   95 rejected controls, in order.
3. With --serial, also runs the pinned layer_end_controls.py with the same arguments and requires a
   byte-identical receipt and identical printed control lines (the timing receipt).
4. Control: a corrupted unmutated word must make the parallel runner fail, as the serial script does,
   because the pinned script's own assertion 'unmutated cold-end word must pass' fires in the replay pass.
Expected last line: PASS_LAYER_END_CONTROLS_PARALLEL
"""
import argparse
import gzip
import hashlib
import json
import os
import platform
import subprocess
import sys
import tarfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = json.loads((HERE / 'PINS.json').read_text())


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL ' + message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned(key):
    path = ROOT / PINS[key]['path']
    require(sha(path.read_bytes()) == PINS[key]['sha256'], key + ' digest')
    return path


def member(name):
    with tarfile.open(pinned('t37_archive'), 'r:gz') as tar:
        return tar.extractfile(tar.getmember(name)).read()


def run(cmd, log):
    code = ROOT / PINS['pr635_code']['path']
    require(sha((code / 'hpe_audit_and_transport.py').read_bytes()) == PINS['pr635_code']['audit_sha256'], 'audit digest')
    src = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src), PR635_CODE=str(code))
    t = time.monotonic()
    with open(log, 'w') as f:
        rc = subprocess.call(cmd, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
    return rc, time.monotonic() - t


def control_lines(log):
    return [x for x in Path(log).read_text().splitlines() if x.startswith(('rejected', 'PASS ', 'entering end'))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--serial', action='store_true')
    a = ap.parse_args()
    work = Path(a.work).resolve()
    require(not work.exists(), 'work directory must not exist')
    work.mkdir(parents=True)
    pinned('script')
    recipe = json.loads(pinned('recipe').read_text())
    data = member(PINS['t37_archive']['word_member'])
    require(sha(gzip.decompress(data)) == recipe['expect_sha256'], 'barch word payload')
    word = work / 'barch-word.json.gz'
    word.write_bytes(data)
    routing = pinned('routing')
    archived = json.loads(member(PINS['t37_archive']['receipt_member']))
    receipt = dict(platform=platform.platform(), python=platform.python_version(), cpu_count=os.cpu_count(), jobs=a.jobs)

    out = work / 'parallel'
    rc, secs = run([sys.executable, '-B', str(HERE / 'controls_parallel.py'), str(word), str(routing), str(out),
                    '--jobs', str(a.jobs)], work / 'parallel.log')
    require(rc == 0, 'parallel controls failed')
    got = json.loads((out / 'COLD-END-CONTROLS.json').read_text())
    require(got['status'] == archived['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS', 'status')
    require(got['rejected'] == archived['rejected'] and len(got['rejected']) == PINS['layer_controls'],
            'rejected controls differ from the archived receipt')
    receipt['parallel_seconds'] = round(secs, 1)
    if a.serial:
        ser = work / 'serial'
        rc, secs = run([sys.executable, '-B', str(ROOT / PINS['script']['path']), str(word), str(routing), str(ser)],
                       work / 'serial.log')
        require(rc == 0, 'serial reference failed')
        require((ser / 'COLD-END-CONTROLS.json').read_bytes() == (out / 'COLD-END-CONTROLS.json').read_bytes(),
                'serial and parallel receipts are not byte-identical')
        require(control_lines(work / 'serial.log') == control_lines(work / 'parallel.log'), 'printed control lines differ')
        receipt['serial_seconds'] = round(secs, 1)
        receipt['speedup'] = round(receipt['serial_seconds'] / receipt['parallel_seconds'], 2)

    # Control: a corrupted unmutated word fails in both runners.
    w = json.loads(gzip.decompress(data))
    w['A'][0][3] = w['A'][0][3] * 2                       # one gate coefficient doubled
    bad = work / 'corrupted-word.json.gz'
    bad.write_bytes(gzip.compress(json.dumps(w).encode(), mtime=0))
    rc, _ = run([sys.executable, '-B', str(HERE / 'controls_parallel.py'), str(bad), str(routing), str(work / 'C1'),
                 '--jobs', str(a.jobs)], work / 'C1.log')
    log = (work / 'C1.log').read_text()
    require(rc != 0 and 'unmutated cold-end word must pass' in log and not (work / 'C1' / 'COLD-END-CONTROLS.json').exists(),
            'corrupted word not rejected by the parallel runner')
    receipt['controls'] = ['C1_corrupted_unmutated_word_fails_in_replay']
    (work / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    print('PASS_LAYER_END_CONTROLS_PARALLEL')


if __name__ == '__main__':
    main()
