#!/usr/bin/env python3
"""Rebuild the X4 word (JointXF: joint read-set exchange on four further copy-pair instances plus explicit B frame
raises, including chafreaky's PR741 eight frames) and its native locals.

Input: a fresh `construction/sw4/reproduce_sw4.py --recipe P6k4` output directory; its SW4 word (d232183f...) is pinned
there and by RECIPE-X4.json. Steps, each checked exactly:
  1. jx: build_jx.py (standard library only; JointXF) applies the recipe's explicit B edits (replace / delete / insert,
     each old gate asserted), the PR741 frames and the explicit raises, repairs all other frames monotonically, checks
     target frames inside u_t^perp, tails and ends, and the exactness of the whole B segment (rational replay), and
     pins the output sha.
  2. jx-controls: every control in the recipe is rebuilt and must reproduce its pinned outcome exactly: a pinned
     rejection site (exit 0 with CONTROL PINNED) or a pinned output sha. C1_741_only must reproduce PR741's word
     e78047028c... (the construction/frames step's output); C0_identity reproduces the input.
  3. layer-end-controls: ../layers_p6n/layer_end_controls.py (per-end variant) on the X4 word; count pinned.
  4. native, ledgers, local-replay, wrappers, phases: PR635's native local programs; canonical word, local programs
     and Clifford recipes pinned (LOCAL-PINS-jx-X4.json).
Apache-2.0. Driver by ColdWitness around JointXF's builder.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P6 = HERE.parent / 'layers_p6n'


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--sw4-dir', type=Path, required=True, help='construction/sw4/reproduce_sw4.py output')
    ap.add_argument('--recipe', default='X4', help='RECIPE-<id>.json and LOCAL-PINS-jx-<id>.json')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skip-phases', action='store_true')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'
    rfile = HERE / ('RECIPE-%s.json' % a.recipe); rec = read(rfile); pins = read(HERE / ('LOCAL-PINS-jx-%s.json' % a.recipe))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE'): env.pop(k, None)
    steps = []

    def run(label, script, *args, portable=True, ok=(0,)):
        t = time.monotonic()
        cmd = [sys.executable, '-B'] + ([str(src / 'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (out / (label + '.log')).open('w') as f:
            rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3)))
        (out / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert rc in ok, (label, rc)
        print('PASS', label, flush=True)
        return (out / (label + '.log')).read_text()

    inp = a.sw4_dir.resolve() / 'sw4/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(inp.read_bytes())).hexdigest() == rec['input_content_sha256'], 'input must be the pinned SW4 word'
    (out / 'jx').mkdir(); word = out / 'jx/FULL-WORD.json.gz'
    run('jx', HERE / 'build_jx.py', '--input', inp, '--recipe', rfile, '--out', word, portable=False)
    assert hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest() == rec['expected']['output_content_sha256']
    assert len(rec['controls']) == pins['jx_controls'], len(rec['controls'])
    results = {}
    for name, c in sorted(rec['controls'].items()):
        log = run('jx-control-' + name, HERE / 'build_jx.py', '--input', inp, '--recipe', rfile, '--control', name, portable=False)
        if 'rejection_expected' in c:
            assert 'CONTROL PINNED' in log, (name, log[-300:]); results[name] = dict(rejected=c['rejection_expected'])
        else:
            assert ('OK ' + c['expected_sha']) in log, (name, log[-300:]); results[name] = dict(sha=c['expected_sha'])
    assert rec['controls']['C1_741_only']['expected_sha'] == rec['frames_741_source']['frames_only_output_sha']
    (out / 'JX-CONTROLS.json').write_text(json.dumps(dict(status='PASS_JX_PINNED_CONTROLS', controls=results), indent=1) + '\n')
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env['PR635_CODE'] = str(up / 'code')
    run('layer-end-controls', P6 / 'layer_end_controls.py', word, routing, out / 'controls')
    env.pop('PR635_CODE')
    ctl = read(out / 'controls/COLD-END-CONTROLS.json')
    assert ctl['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS' and len(ctl['rejected']) == pins['layer_controls'], len(ctl['rejected'])
    local = out / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', word, '--routing', routing, '--out', local)
    assert hashlib.sha256(gzip.decompress((local / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest() == pins['canonical_sha256'], 'canonical word'
    run('ledgers', up / 'code/hpe_emit_local.py', local)
    run('local-replay', up / 'code/hpe_audit_local.py', local)
    run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz',
        local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    checks = read(local / 'LOCAL-CHECKS.json')
    for o, s in pins['program_sha256'].items(): assert checks[o]['sha256'] == s, ('local program', o)
    if not a.skip_phases:
        run('phases', base / 'code/phases_full.py', local, parent / 'complex-global/vendor531/vendor/clifford')
        assert hashlib.sha256((local / 'CLIFFORD-RECIPES.json').read_bytes()).hexdigest() == pins['clifford_recipes_sha256'], 'clifford recipes'
    print('DONE', local, flush=True)


if __name__ == '__main__':
    main()
