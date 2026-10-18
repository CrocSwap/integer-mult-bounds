# SPDX-License-Identifier: Apache-2.0
"""The five layer-end-control steps of the frontier1042 leaver chain, as lec() runs them.

Usage: chain_lec.py --chain CHAIN_DIR --out NEW_DIR [--runner parallel|pinned] [--jobs N] [--id k8]

CHAIN_DIR holds p6n/, promo/, jx/, hyb/ and frames/FULL-WORD.json.gz: a completed
reproduce_leaver_chain.py --out directory, or the chain/ members of the selected replay archive.
Before a step runs, its word's payload digest must equal the recipe pin that the chain itself
asserts when it builds that word. Each step then runs either the pinned serial script through
the pinned launcher (--runner pinned, the reference) or lec_parallel.py's runner (one pool and
one outcome table for all five steps). Afterwards it applies the checks of
reproduce_leaver_chain.py's lec() against CHAIN-PINS-<id>.json: the pins-file digest, a PASS
status, the number of rejected controls and the declared not-applicable sites.
Writes OUT/<step>/COLD-END-CONTROLS.json, OUT/<step>.log and OUT/LEC-STEPS.json.
"""
import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lec_parallel as lp  # noqa: E402

ROOT = lp.ROOT
LEAVER = ROOT / 'research/gauge44-leaver8/construction/leaver'
PR635_CODE = ROOT / 'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code'
MULTICOLD = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
ROUTING = MULTICOLD / 'vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
STEPS = (('lec-p6n', 'p6n', 'LEC-REASON-PINS-STACK'), ('lec-promo', 'promo', 'LEC-REASON-PINS-STACK'),
         ('lec-jx', 'jx', 'LEC-REASON-PINS-STACK'), ('lec-hyb', 'hyb', 'LEC-REASON-PINS-STACK'),
         ('lec-frames', 'frames', 'LEC-REASON-PINS'))


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def payload_sha(p):
    return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()


def word_pins(rid):
    """The payload digest the chain asserts for each word it builds (reproduce_leaver_chain.py)."""
    return dict(p6n=read(LEAVER / ('COLD-LAYERS-RECIPE-P6N-%s.json.gz' % rid))['output_content_sha256'],
                promo=read(LEAVER / ('PROMO-RECIPE-%s.json' % rid))['expected']['output_content_sha256'],
                jx=read(LEAVER / ('RECIPE-X4-%s.json' % rid))['expected']['output_content_sha256'],
                hyb=read(LEAVER / ('RECIPE-U8-%s.json' % rid))['expect_sha256'],
                frames=read(LEAVER / ('FRAME-RECIPE-LV-%s.json' % rid))['expected']['output_content_sha256'])


def chain_env():
    """reproduce_leaver_chain.py's step environment (before the per-step extras)."""
    env = dict(os.environ, MULTICOLD_SOURCE=str(MULTICOLD), GAIN_PR564_SOURCE=str(MULTICOLD), **lp.CHAIN_ENV)
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE',
              'LEC_REASON_PINS', 'SW4_PIN'):
        env.pop(k, None)
    return env


def main():
    lp.ensure_chain_interpreter([str(Path(__file__).resolve()), *sys.argv[1:]])
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--chain', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--runner', choices=('parallel', 'pinned'), default='parallel')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--id', default='k8')
    a = ap.parse_args()
    chain, out = a.chain.resolve(), a.out.resolve()
    assert not out.exists(), 'use a new --out directory'
    out.mkdir(parents=True)
    pins = read(LEAVER / ('CHAIN-PINS-%s.json' % a.id))
    expect = word_pins(a.id)
    for _, name, _ in STEPS:
        assert payload_sha(chain / name / 'FULL-WORD.json.gz') == expect[name], ('chain word is not the pinned one', name)
    env = chain_env()
    os.environ.clear()
    os.environ.update(env)
    runner = lp.Runner(PR635_CODE, a.jobs) if a.runner == 'parallel' else None
    steps, ok = [], False
    try:
        for label, name, pins_name in STEPS:
            pf = LEAVER / ('%s-%s.json' % (pins_name, a.id))
            assert hashlib.sha256(pf.read_bytes()).hexdigest() == pins[label + '_pins_sha256'], (label, 'pins file')
            word = chain / name / 'FULL-WORD.json.gz'
            extra = dict(PR635_CODE=str(PR635_CODE), LEC_REASON_PINS=str(pf))
            t = time.monotonic()
            with (out / (label + '.log')).open('w') as log:
                if runner is None:
                    rc = subprocess.call([sys.executable, '-B', str(lp.LAUNCHER), str(lp.SCRIPT), str(word),
                                          str(ROUTING), str(out / label)], env=dict(env, **extra),
                                         stdout=log, stderr=subprocess.STDOUT)
                    stats = {}
                else:
                    os.environ.update(extra)
                    try:
                        stats = runner.step(word, ROUTING, out / label, stdout=log)
                        rc = 0
                    except BaseException:
                        log.write(traceback.format_exc())
                        rc = 1
                    finally:
                        for k in extra:
                            os.environ.pop(k, None)
            steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3), **stats))
            (out / 'LEC-STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
            assert rc == 0, label
            c = read(out / label / 'COLD-END-CONTROLS.json')
            assert c['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS', label
            assert len(c['rejected']) == pins[label], (label, 'rejected controls')
            assert {x['site']: x['reason'] for x in c['not_applicable']} == pins[label + '_not_applicable'], (label, 'not applicable')
            print('PASS', label, len(c['rejected']), 'controls', '%.1f s' % steps[-1]['seconds'], flush=True)
        ok = True
    finally:
        if runner is not None:
            runner.close() if ok else runner.terminate()
    print('PASS_CHAIN_LEC', a.runner, '%.1f s' % sum(s['seconds'] for s in steps), flush=True)


if __name__ == '__main__':
    main()
