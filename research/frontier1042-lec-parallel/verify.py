# SPDX-License-Identifier: Apache-2.0
"""Check the opt-in parallel layer-end controls on the frontier1042 leaver chain.

Usage: python3 -B research/frontier1042-lec-parallel/verify.py --work NEW_EMPTY_DIR [--jobs N] [--serial]

1. Extracts the five chain words and their five layer-end-control receipts from the selected
   replay archive (every member digest pinned in PINS.json). chain_lec.py binds each word's
   payload to the recipe pin that the chain asserts when it builds that word.
2. Runs chain_lec.py --runner parallel. Every receipt must equal the archived maintainer receipt
   byte for byte, after the one recorded field that names the input path (`word`) is rewritten
   from the archived chain directory to this run's directory.
3. With --serial, also runs chain_lec.py --runner pinned (the pinned launcher and script, one
   process per step, as the chain does). The two runs must give byte-identical receipts and
   identical logs except for the audit's own wall-clock 'seconds' line. Timings go to
   BENCHMARK.json.
4. Secondary check (the variant PR1059 covered): the T37 layers_p6n/layer_end_controls.py step on the
   archived T37 barch word (payload bound to PR870's RECIPE-U8 pin) must reproduce the archived T37
   receipt the same way, and with --serial must be byte-identical to the pinned serial step.
5. Controls, on the final (frames) word, through the same runner:
   C1 a corrupted unmutated word fails at the pinned script's own first assertion;
   C2 a forged acceptance of one mutant makes the pinned script fail ('mutation accepted');
   C3 a forged rejection reason for one mutant makes it fail ('wrong reason');
   C4 a one-byte change to the pinned script, or to PR635's audit, is refused before any work.
   No control may leave a receipt behind.
Expected last line: PASS_FRONTIER1042_LEC_PARALLEL
"""
import argparse
import gzip
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chain_lec  # noqa: E402
import lec_parallel as lp  # noqa: E402

ROOT = lp.ROOT
PINS = json.loads((HERE / 'PINS.json').read_text())
TIMING = re.compile(r'"seconds": [0-9.eE+-]+')


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL ' + message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_pins():
    for key in ('selected_verifier', 'chain_driver', 'launcher', 'script', 't37_script', 'routing'):
        require(sha((ROOT / PINS[key]['path']).read_bytes()) == PINS[key]['sha256'], key + ' digest')
    audit = ROOT / PINS['pr635_code']['path'] / 'hpe_audit_and_transport.py'
    require(sha(audit.read_bytes()) == PINS['pr635_code']['audit_sha256'], 'PR635 audit digest')
    for path, digest in PINS['chain_pins'].items():
        require(sha((ROOT / path).read_bytes()) == digest, path + ' digest')
    require(lp.LAUNCHER_SHA256 == PINS['launcher']['sha256'] and lp.SCRIPT_SHA256 == PINS['script']['sha256'] and
            lp.T37_SCRIPT_SHA256 == PINS['t37_script']['sha256'], 'runner constants differ from PINS.json')


def extract(work):
    archive = ROOT / PINS['archive']['path']
    require(sha(archive.read_bytes()) == PINS['archive']['sha256'], 'archive digest')
    got = {}
    with tarfile.open(archive, 'r:gz') as tar:
        for name, digest in PINS['archive']['members'].items():
            data = tar.extractfile(tar.getmember(name)).read()
            require(sha(data) == digest, name + ' digest')
            got[name] = data
    chain = work / 'chain'
    for name, data in got.items():
        if name.endswith('FULL-WORD.json.gz'):
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return chain, got


def run_chain(chain, out, runner, jobs, log):
    with open(log, 'w') as f:
        rc = subprocess.call([sys.executable, '-B', str(HERE / 'chain_lec.py'), '--chain', str(chain), '--out', str(out),
                              '--runner', runner, '--jobs', str(jobs)], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    require(rc == 0, 'chain_lec.py --runner %s failed; see %s' % (runner, log))
    return json.loads((out / 'LEC-STEPS.json').read_text())


def t37(work, jobs, serial):
    """Secondary check: the T37 variant (layers_p6n/layer_end_controls.py) on the archived T37 barch word."""
    arch = PINS['t37_archive']
    archive = ROOT / arch['path']
    require(sha(archive.read_bytes()) == arch['sha256'], 'T37 archive digest')
    with tarfile.open(archive, 'r:gz') as tar:
        got = {name: tar.extractfile(tar.getmember(name)).read() for name in arch['members']}
    for name, digest in arch['members'].items():
        require(sha(got[name]) == digest, name + ' digest')
    recipe = ROOT / arch['recipe']['path']
    require(sha(recipe.read_bytes()) == arch['recipe']['sha256'], 'T37 recipe digest')
    data = got['native/barch/FULL-WORD.json.gz']
    require(sha(gzip.decompress(data)) == json.loads(recipe.read_text())['expect_sha256'], 'T37 barch word payload')
    base = work / 't37'
    word = base / 'barch/FULL-WORD.json.gz'
    word.parent.mkdir(parents=True)
    word.write_bytes(data)
    env = dict(chain_lec.chain_env(), PR635_CODE=str(chain_lec.PR635_CODE))
    runs = [('parallel', [str(HERE / 'lec_parallel.py'), str(word), str(chain_lec.ROUTING), str(base / 'parallel'),
                          '--jobs', str(jobs), '--script', str(lp.T37_SCRIPT)])]
    if serial:
        runs.append(('pinned', [str(lp.LAUNCHER), str(lp.T37_SCRIPT), str(word), str(chain_lec.ROUTING), str(base / 'pinned')]))
    seconds = {}
    for name, args in runs:
        t = time.monotonic()
        with (base / (name + '.log')).open('w') as f:
            rc = subprocess.call([sys.executable, '-B', *args], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
        require(rc == 0, 'T37 %s run failed' % name)
        seconds[name + '_seconds'] = round(time.monotonic() - t, 1)
    archived = got['native/controls/COLD-END-CONTROLS.json']
    old, new = json.dumps(arch['recorded_word']).encode(), json.dumps(str(word)).encode()
    require(archived.count(old) == 1, 'T37: archived receipt does not name the recorded word path once')
    parallel = (base / 'parallel/COLD-END-CONTROLS.json').read_bytes()
    require(parallel == archived.replace(old, new), 'T37: receipt differs from the archived receipt')
    if serial:
        require((base / 'pinned/COLD-END-CONTROLS.json').read_bytes() == parallel, 'T37: pinned and parallel receipts differ')
        require(masked(base / 'pinned.log') == masked(base / 'parallel.log'), 'T37: logs differ beyond the audit timing line')
    return seconds


def expect_failure(fn, needle, outdir):
    try:
        fn()
    except AssertionError as e:
        message = ' '.join(map(str, e.args))
        require(needle in message, 'control failed for an unexpected reason: ' + message[:200])
        require(not (outdir / 'COLD-END-CONTROLS.json').exists(), 'a failing control left a receipt')
        return message[:160]
    raise SystemExit('FAIL control was not rejected: ' + needle)


def controls(work, chain, jobs):
    word = chain / 'frames/FULL-WORD.json.gz'
    pins = chain_lec.LEAVER / 'LEC-REASON-PINS-k8.json'
    os.environ.update(chain_lec.chain_env(), PR635_CODE=str(chain_lec.PR635_CODE), LEC_REASON_PINS=str(pins))
    results = {}
    logs = work / 'controls'
    logs.mkdir()
    with lp.Runner(chain_lec.PR635_CODE, jobs) as runner:
        def step(name, w, tamper=None):
            with (logs / (name + '.log')).open('w') as f:
                return runner.step(w, chain_lec.ROUTING, logs / name, stdout=f, tamper=tamper)

        def forge(kind, args):
            def tamper(table, recorded):
                key = recorded[17]                      # an arbitrary mutant (trial 0 is the unmutated word)
                table[key] = (kind, args, '')
            return tamper
        results['C2_forged_acceptance'] = expect_failure(
            lambda: step('C2', word, forge('pass', ())), 'cold-end mutation accepted', logs / 'C2')
        results['C3_forged_reason'] = expect_failure(
            lambda: step('C3', word, forge('assert', ('an unrelated assertion',))), 'rejected for the wrong reason', logs / 'C3')
        w = json.loads(gzip.decompress(word.read_bytes()))
        w['A'][0][3] = w['A'][0][3] * 2                       # one gate coefficient doubled
        bad = logs / 'corrupted-word.json.gz'
        bad.write_bytes(gzip.compress(json.dumps(w).encode(), mtime=0))
        results['C1_corrupted_unmutated_word'] = expect_failure(
            lambda: step('C1', bad, None), 'unmutated cold-end word must pass', logs / 'C1')
        tampered = logs / 'layer_end_controls_leaver.py'
        tampered.write_bytes(lp.SCRIPT.read_bytes() + b'\n')
        try:
            runner.step(word, chain_lec.ROUTING, logs / 'C4', script=tampered)
            raise SystemExit('FAIL tampered script was run')
        except RuntimeError as e:
            require('digest mismatch' in str(e) and not (logs / 'C4').exists(), 'tampered script not refused')
    code = logs / 'pr635-code'
    shutil.copytree(chain_lec.PR635_CODE, code)
    audit = code / 'hpe_audit_and_transport.py'
    audit.write_bytes(audit.read_bytes() + b'\n')
    try:
        lp.Runner(code, 1)
        raise SystemExit('FAIL tampered audit was loaded')
    except RuntimeError as e:
        require('digest mismatch' in str(e), 'tampered audit not refused')
    results['C4_tampered_script_and_audit_refused'] = 'refused before any work'
    return results


def masked(log):
    return TIMING.sub('"seconds": *', Path(log).read_text())


def main():
    lp.ensure_chain_interpreter([str(Path(__file__).resolve()), *sys.argv[1:]])
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--work', required=True)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--serial', action='store_true', help='also run the pinned serial reference (benchmark)')
    a = ap.parse_args()
    work = Path(a.work).resolve()
    require(not work.exists(), 'work directory must not exist')
    work.mkdir(parents=True)
    check_pins()
    chain, members = extract(work)
    receipt = dict(platform=platform.platform(), python=platform.python_version(), cpu_count=os.cpu_count(),
                   jobs=a.jobs, base_commit=PINS['base_commit'])

    par = work / 'parallel'
    steps = run_chain(chain, par, 'parallel', a.jobs, work / 'parallel.log')
    old_dir, new_dir = PINS['archive']['recorded_chain_dir'], str(chain)
    for label, name, _ in chain_lec.STEPS:
        archived = members['chain/%s/COLD-END-CONTROLS.json' % label]
        old = json.dumps(old_dir + '/%s/FULL-WORD.json.gz' % name).encode()
        new = json.dumps(new_dir + '/%s/FULL-WORD.json.gz' % name).encode()
        require(archived.count(old) == 1, label + ': archived receipt does not name the recorded word path once')
        got = (par / label / 'COLD-END-CONTROLS.json').read_bytes()
        require(got == archived.replace(old, new), label + ': receipt differs from the archived maintainer receipt')
    receipt['parallel'] = steps
    receipt['parallel_seconds'] = round(sum(s['seconds'] for s in steps), 1)
    receipt['archived_serial_seconds'] = round(sum(PINS['archived_step_seconds'].values()), 1)
    print('PASS parallel receipts equal the five archived receipts', receipt['parallel_seconds'], 's', flush=True)

    if a.serial:
        ser = work / 'pinned'
        ssteps = run_chain(chain, ser, 'pinned', a.jobs, work / 'pinned.log')
        for label, _, _ in chain_lec.STEPS:
            require((ser / label / 'COLD-END-CONTROLS.json').read_bytes() == (par / label / 'COLD-END-CONTROLS.json').read_bytes(),
                    label + ': pinned and parallel receipts are not byte-identical')
            require(masked(ser / (label + '.log')) == masked(par / (label + '.log')),
                    label + ': pinned and parallel logs differ beyond the audit timing line')
        receipt['pinned'] = ssteps
        receipt['pinned_seconds'] = round(sum(s['seconds'] for s in ssteps), 1)
        receipt['speedup'] = round(receipt['pinned_seconds'] / receipt['parallel_seconds'], 2)
        print('PASS pinned serial reference: identical receipts and logs', receipt['pinned_seconds'], 's', flush=True)

    receipt['t37'] = t37(work, a.jobs, a.serial)
    print('PASS T37 variant receipt equals the archived T37 receipt', receipt['t37'], flush=True)

    receipt['controls'] = controls(work, chain, a.jobs)
    print('PASS controls', ', '.join(receipt['controls']), flush=True)
    (work / ('BENCHMARK.json' if a.serial else 'RESULT.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    print('PASS_FRONTIER1042_LEC_PARALLEL')


if __name__ == '__main__':
    main()
