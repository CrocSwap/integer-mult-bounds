#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Pinned-versus-accelerated equivalence of four real transport-audit control suites of the selected cold chain.

For each suite the input word, archived receipt and archived log are read from the repository's own evidence tarballs.
The unchanged control script is run three ways: directly, as the orchestrators run it (D); through fast_controls.py
--pinned (P); and through fast_controls.py --require-fast (F).  All of the following must hold:
  * COLD-END-CONTROLS.json byte-identical across D, P and F, and equal to the archived receipt apart from its
    machine-specific absolute 'word' path;
  * stdout identical across D, P and F, and equal to the archived log where one exists, after dropping only the
    audit's own top-level '"seconds"' line;
  * the audit module resolved by the script's own import rule is the expected file, unaccelerated in P and
    accelerated in F;
  * every per-audit outcome identical between P and F: exception type, repr(args) and the run() line it propagated
    through, or the receipt text without its seconds line plus both output-word hashes.
Usage: python3 -I -B equivalence.py [--suite NAME ...] [--out RESULT.json]   (about 4-8 minutes for all four)
"""
import argparse
import hashlib
import io
import json
import os
import resource
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODE = 'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code'
ROUTING = ('research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/'
           'vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz')
T942 = 'research/community-frontier942-audit/t37-replay.tar.gz'
T799 = 'research/community-frontier799-audit/integrated799-replay.tar.gz'
T741 = 'research/community-frontier741-audit/composed-replay-evidence.tar.gz'
SUITES = {
    't37-u8-layer-end': dict(
        script='research/complex-t21-owners/vendor/pr870/construction/layers_p6n/layer_end_controls.py', audit=CODE,
        tar=T942, word='native/barch/FULL-WORD.json.gz', receipt='native/controls/COLD-END-CONTROLS.json',
        log='native/layer-end-controls.log', word_sha256='090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a'),
    '799-x4-layer-end': dict(
        script='research/gauge44-frames-x/construction/layers_p6n/layer_end_controls.py', audit=CODE,
        tar=T799, word='native/jx/FULL-WORD.json.gz', receipt='native/controls/COLD-END-CONTROLS.json',
        log='native/layer-end-controls.log', word_sha256=None),
    '741-p6n-layer-end': dict(
        script='research/complex-sw4-frame8/construction/layers_p6n/layer_end_controls.py', audit=CODE,
        tar=T741, word='complex/p6n/p6n/FULL-WORD.json.gz', receipt='complex/p6n/controls/COLD-END-CONTROLS.json',
        log=None, word_sha256=None),
    '741-inherited-cold-end': dict(
        script='research/complex-sw4-frame8/local/cold_end_controls.py', audit='research/complex-sw4-frame8/local',
        tar=T741, word='complex/frames/FULL-WORD.json.gz', receipt='complex/cold-controls/COLD-END-CONTROLS.json',
        log='complex/inherited-cold-controls.log', word_sha256=None),
}
# sha256 of the unchanged control scripts and audit modules this harness was validated with
PINS = {
    'research/complex-t21-owners/vendor/pr870/construction/layers_p6n/layer_end_controls.py': 'fc58c5699ba6191c1163a3041241f6f0b619626c4462cd99bcf88210bac9e81e',
    'research/gauge44-frames-x/construction/layers_p6n/layer_end_controls.py': 'fc58c5699ba6191c1163a3041241f6f0b619626c4462cd99bcf88210bac9e81e',
    'research/complex-sw4-frame8/construction/layers_p6n/layer_end_controls.py': 'fc58c5699ba6191c1163a3041241f6f0b619626c4462cd99bcf88210bac9e81e',
    'research/complex-sw4-frame8/local/cold_end_controls.py': '6f8cfe711aea1d688c255a1f1c158d94aab8ce4adaa526113d58ca58db87078c',
    CODE + '/hpe_audit_and_transport.py': 'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3',
    'research/complex-sw4-frame8/local/hpe_audit_and_transport.py': 'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3',
}


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL ' + msg)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def member(tar, name):
    with tarfile.open(ROOT / tar) as t:
        return t.extractfile(name).read()


def strip(text):
    """Drop only the audit's own wall-clock line, printed and written as a top-level key with two-space indent."""
    return '\n'.join(line for line in text.splitlines() if not line.startswith('  "seconds":'))


def run_mode(mode, spec, word, out, work):
    """D: the control script exactly as the orchestrators run it.  P/F: through fast_controls.py, pinned or fast."""
    env = dict(os.environ, PR635_CODE=str(ROOT / CODE), PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0')
    args = [str(word), str(ROOT / ROUTING), str(out)]
    if mode == 'direct':
        cmd = [sys.executable, '-B', str(ROOT / spec['script']), *args]
    else:
        env['FAST_HPE_RECORD'] = str(work / ('%s-record.json' % mode))
        flag = '--pinned' if mode == 'pinned' else '--require-fast'
        cmd = [sys.executable, '-B', str(HERE / 'fast_controls.py'), flag, str(ROOT / spec['script']), *args]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    wall = time.monotonic() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    need(proc.returncode == 0, '%s run failed: %s' % (mode, proc.stderr[-2000:]))
    record = json.loads(Path(env['FAST_HPE_RECORD']).read_text()) if mode != 'direct' else None
    return dict(stdout=proc.stdout, record=record, receipt=(out / 'COLD-END-CONTROLS.json').read_bytes(),
                wall=round(wall, 2), cpu=round(after.ru_utime - before.ru_utime + after.ru_stime - before.ru_stime, 2))


def suite(name, work):
    spec = SUITES[name]
    word_bytes = member(spec['tar'], spec['word'])
    content = sha(__import__('gzip').decompress(word_bytes))
    if spec['word_sha256']:
        need(content == spec['word_sha256'], name + ' input word hash')
    word = work / 'word.json.gz'
    word.write_bytes(word_bytes)
    archived_receipt = member(spec['tar'], spec['receipt'])
    runs = {mode: run_mode(mode, spec, word, work / mode, work) for mode in ('direct', 'pinned', 'fast')}
    d, p, f = runs['direct'], runs['pinned'], runs['fast']
    need(d['receipt'] == p['receipt'] == f['receipt'], name + ' COLD-END-CONTROLS.json bytes differ')
    # The receipt records the absolute input path ('word'), which differs by machine; everything else must match.
    drop = lambda b: {k: v for k, v in json.loads(b).items() if k != 'word'}
    need(drop(d['receipt']) == drop(archived_receipt), name + ' receipt differs from archived receipt')
    need(strip(d['stdout']) == strip(p['stdout']) == strip(f['stdout']), name + ' stdout differs')
    if spec['log']:
        need(strip(d['stdout']) == strip(member(spec['tar'], spec['log']).decode()), name + ' stdout differs from archived log')
    need(p['record']['audits'] == f['record']['audits'], name + ' per-audit outcomes differ')
    lp, lf = p['record']['loaded'], f['record']['loaded']
    need(len(lp) == len(lf) == 1 and lp[0]['path'] == lf[0]['path'] == str(ROOT / spec['audit'] / 'hpe_audit_and_transport.py')
         and lp[0]['sha256'] == lf[0]['sha256'] and not lp[0]['accelerated'] and lf[0]['accelerated'],
         name + ' audit module resolution')
    audits = p['record']['audits']
    receipt = json.loads(d['receipt'])
    return dict(input_word=spec['word'], input_content_sha256=content, control_script=spec['script'],
                audit_module=spec['audit'] + '/hpe_audit_and_transport.py',
                audits=len(audits), passes=sum('receipt' in r for r in audits),
                rejected_controls=len(receipt.get('rejected', [])),
                distinct_failure_points=len({tuple(r['exception']) for r in audits if 'exception' in r}),
                receipt_sha256_without_word=sha(json.dumps(drop(d['receipt']), sort_keys=True).encode()),
                archived_receipt_sha256=sha(archived_receipt),
                rejected_sha256=sha(json.dumps(receipt['rejected']).encode()),
                stdout_sha256_without_seconds=sha(strip(d['stdout']).encode()),
                archived_log_compared=bool(spec['log']), outcomes_sha256=sha(json.dumps(audits, sort_keys=True).encode()),
                timing=dict(direct_wall=d['wall'], fast_wall=f['wall'], direct_cpu=d['cpu'], pinned_wrapper_cpu=p['cpu'],
                            fast_cpu=f['cpu'], cpu_ratio=round(d['cpu']/f['cpu'], 2),
                            load_average=[round(x, 1) for x in os.getloadavg()]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--suite', action='append', choices=sorted(SUITES))
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    for path, digest in PINS.items():
        need(sha((ROOT / path).read_bytes()) == digest, 'pin ' + path)
    results = {}
    for name in a.suite or list(SUITES):
        with tempfile.TemporaryDirectory(prefix='fast-hpe-eq-') as tmp:
            results[name] = suite(name, Path(tmp))
        t = results[name]['timing']
        print('PASS %s: %d audits, receipt %s, cpu %.1fs -> %.1fs (%.2fx)' % (
            name, results[name]['audits'], results[name]['receipt_sha256_without_word'][:12], t['direct_cpu'], t['fast_cpu'], t['cpu_ratio']), flush=True)
    report = dict(status='PASS_FAST_HPE_TRANSPORT_EQUIVALENCE', python=sys.version.split()[0], suites=results)
    if a.out:
        a.out.write_text(json.dumps(report, indent=1, sort_keys=True) + '\n')
    print(report['status'])


if __name__ == '__main__':
    main()
