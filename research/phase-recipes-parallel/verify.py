# SPDX-License-Identifier: Apache-2.0
"""Check the opt-in parallel phase runner against the pinned serial reference.

Usage: python3 -B research/phase-recipes-parallel/verify.py --work NEW_EMPTY_DIR [--jobs N] [--serial]

1. Extracts the pinned U8 canonical word from the selected T37 archive (in memory).
2. Runs phases_parallel.py with both engines (reference and the merged PR662 evaluator) and requires CLIFFORD-RECIPES.json to have the digest pinned in
   PR870's LOCAL-PINS-barch-U8.json (also the template's exact_local_clifford_recipe_sha256),
   and CLIFFORD-REVIEW.json to equal the archived review apart from elapsed seconds.
3. With --serial, also runs the pinned phases_full.py through its portable wrapper on a
   separate copy and requires byte-identical recipes (the timing receipt).
4. Runs failure-detection controls: a parent-side frame failure, a worker-side edge failure
   (which must fail the run without writing recipes), and the same edge failure in the
   pinned serial script.
Expected last line: PASS_PHASE_RECIPES_PARALLEL
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


def pinned_file(key):
    path = ROOT / PINS[key]['path']
    require(sha(path.read_bytes()) == PINS[key]['sha256'], f'{key} digest')
    return path


def archive_member(member, payload_sha):
    archive = pinned_file('t37_archive')
    with tarfile.open(archive, 'r:gz') as tar:
        data = tar.extractfile(tar.getmember(member)).read()
    return data


def word_dir(base, name):
    d = base / name
    d.mkdir()
    data = archive_member(PINS['canonical_word']['member'], None)
    require(sha(gzip.decompress(data)) == PINS['canonical_word']['payload_sha256'], 'canonical word payload')
    (d / 'CANONICAL-WORD.json.gz').write_bytes(data)
    return d


def run(cmd, log):
    t = time.monotonic()
    with open(log, 'w') as f:
        rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
                                      PYTHONINTMAXSTRDIGITS='0'))
    return rc, time.monotonic() - t


def review_equal(path):
    got = json.loads(Path(path).read_text())
    ref = json.loads(archive_member(PINS['archived_review']['member'], None))
    for d in (got, ref):
        d.pop('seconds')
    return got == ref


def mutated_word(src_dir, base, name, mutate):
    d = base / name
    d.mkdir()
    c = json.load(gzip.open(src_dir / 'CANONICAL-WORD.json.gz'))
    mutate(c)
    (d / 'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(json.dumps(c).encode(), mtime=0))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--serial', action='store_true', help='also time the pinned serial reference')
    a = ap.parse_args()
    work = Path(a.work).resolve()
    require(not work.exists(), 'work directory must not exist')
    work.mkdir(parents=True)
    local_pins = json.loads(pinned_file('local_pins').read_text())
    require(local_pins['clifford_recipes_sha256'] == PINS['recipes_sha256'], 'recipe pin differs from PR870 LOCAL-PINS')
    require(local_pins['canonical_sha256'] == PINS['canonical_word']['payload_sha256'], 'word pin differs from PR870 LOCAL-PINS')
    clifford = pinned_file('clifford_exact').parent
    serial_script = pinned_file('phases_full')
    wrapper = pinned_file('run_portable')
    runner = HERE / 'phases_parallel.py'
    receipt = dict(platform=platform.platform(), python=platform.python_version(), cpu_count=os.cpu_count(), jobs=a.jobs)

    raw = None
    for engine in ('reference', 'dense662'):
        par = word_dir(work, 'parallel-' + engine)
        rc, secs = run([sys.executable, '-B', str(runner), str(par), str(clifford), '--jobs', str(a.jobs),
                        '--engine', engine], work / f'parallel-{engine}.log')
        require(rc == 0, f'parallel run failed ({engine})')
        out = (par / 'CLIFFORD-RECIPES.json').read_bytes()
        require(sha(out) == PINS['recipes_sha256'], f'parallel recipes digest differs from the pin ({engine})')
        require(review_equal(par / 'CLIFFORD-REVIEW.json'), f'parallel review differs from the archived review ({engine})')
        require(raw is None or out == raw, 'engines disagree')
        raw = out
        receipt[f'parallel_{engine}_seconds'] = round(secs, 1)
    if a.serial:
        one = word_dir(work, 'dense662-one-job')
        rc, secs = run([sys.executable, '-B', str(runner), str(one), str(clifford), '--jobs', '1', '--engine', 'dense662'],
                       work / 'dense662-one-job.log')
        require(rc == 0 and (one / 'CLIFFORD-RECIPES.json').read_bytes() == raw, 'one-job dense662 run differs')
        receipt['dense662_one_job_seconds'] = round(secs, 1)
        ser = word_dir(work, 'serial')
        rc, secs = run([sys.executable, '-B', str(wrapper), str(serial_script), str(ser), str(clifford)], work / 'serial.log')
        require(rc == 0, 'serial reference failed')
        require((ser / 'CLIFFORD-RECIPES.json').read_bytes() == raw, 'serial and parallel recipes differ')
        receipt['serial_seconds'] = round(secs, 1)
        receipt['speedup_reference_parallel'] = round(receipt['serial_seconds'] / receipt['parallel_reference_seconds'], 2)
        receipt['speedup_dense662_parallel'] = round(receipt['serial_seconds'] / receipt['parallel_dense662_seconds'], 2)
    par = work / 'parallel-reference'

    # Controls. C1: a frame that no longer has full-rank Lagrangian data fails in the parent.
    def break_frame(c):
        c['frames'][5] = c['frames'][5] + c['frames'][5][:1]   # duplicated generator: rank checks fail
    d1 = mutated_word(par, work, 'C1', break_frame)
    rc, _ = run([sys.executable, '-B', str(runner), str(d1), str(clifford), '--jobs', str(a.jobs)], work / 'C1.log')
    require(rc != 0 and not (d1 / 'CLIFFORD-RECIPES.json').exists(), 'C1 frame failure not detected')

    # C2: an edge between two different frames of equal rank fails the per-edge rank check in a worker.
    def bad_edge(c):
        by_rank = {}
        for i, U in enumerate(c['frames']):
            by_rank.setdefault(len(U), []).append(i)
        a2, b2 = next(v[:2] for r, v in sorted(by_rank.items()) if 0 < r and len(v) > 1)
        c['edges'] = [[a2, b2]]
    for engine in ('reference', 'dense662'):
        d2 = mutated_word(par, work, 'C2-' + engine, bad_edge)
        rc, _ = run([sys.executable, '-B', str(runner), str(d2), str(clifford), '--jobs', str(a.jobs), '--engine', engine],
                    work / f'C2-{engine}.log')
        log2 = (work / f'C2-{engine}.log').read_text()
        require(rc != 0 and 'AssertionError' in log2 and not (d2 / 'CLIFFORD-RECIPES.json').exists(),
                f'C2 worker failure not propagated ({engine})')
    d3 = mutated_word(par, work, 'C2-serial', bad_edge)
    rc, _ = run([sys.executable, '-B', str(wrapper), str(serial_script), str(d3), str(clifford)], work / 'C2-serial.log')
    require(rc != 0 and 'AssertionError' in (work / 'C2-serial.log').read_text(), 'C2 not rejected by the serial reference')
    receipt['controls'] = ['C1_frame_rank_failure_in_parent', 'C2_edge_rank_failure_in_worker_reference',
                           'C2_edge_rank_failure_in_worker_dense662', 'C2_same_failure_in_serial_reference']
    (work / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    print('PASS_PHASE_RECIPES_PARALLEL')


if __name__ == '__main__':
    main()
