#!/usr/bin/env python3
"""Rebuild the SW4F8 word (eight B-gate frame raises on the SW4 word, chafreaky's PR741 recipe) and its native locals.

Input: a fresh `construction/sw4/reproduce_sw4.py --recipe P6k4` output directory; its SW4 word (d232183f...) is pinned
there and by FRAME-RECIPE-<id>.json. Steps, each checked exactly:
  1. frames: build_frames.py (standard library only) applies the eight 'B' gate_frames with BlockInvert's
     build_promotion.apply. Scalar program, start and end frames unchanged; profile, widths and output sha pinned;
     three pin controls must be rejected (count pinned).
  2. frame-controls: frame_controls.py, PR741's ten focused mutants judged by PR635's unchanged native audit.
  3. layer-end-controls: ../layers_p6n/layer_end_controls.py (per-end variant) on the SW4F8 word; count pinned.
  4. native, ledgers, local-replay, wrappers, phases: PR635's native local programs, with the canonical word, local
     programs and Clifford recipes pinned (LOCAL-PINS-frames-<id>.json).
Apache-2.0.
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
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--recipe', default='sw4', help='FRAME-RECIPE-<id>.json and LOCAL-PINS-frames-<id>.json')
    ap.add_argument('--skip-phases', action='store_true')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'
    rfile = HERE / ('FRAME-RECIPE-%s.json' % a.recipe); rec = read(rfile); pins = read(HERE / ('LOCAL-PINS-frames-%s.json' % a.recipe))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE'): env.pop(k, None)
    steps = []

    def run(label, script, *args, portable=True):
        t = time.monotonic()
        cmd = [sys.executable, '-B'] + ([str(src / 'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (out / (label + '.log')).open('w') as f:
            rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3)))
        (out / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert rc == 0, label
        print('PASS', label, flush=True)

    inp = a.sw4_dir.resolve() / 'sw4/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(inp.read_bytes())).hexdigest() == rec['input_content_sha256'], 'input must be the pinned SW4 word'
    run('frames', HERE / 'build_frames.py', inp, out / 'frames', rfile, portable=False)
    b = read(out / 'frames/BUILD.json')
    assert b['status'] == 'PASS_EIGHT_FRAME_EXACT_CONSTRUCTION' and len(b['rejected_controls']) == pins['frame_build_controls'], b
    word = out / 'frames/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest() == rec['expected']['output_content_sha256']
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env['PR635_CODE'] = str(up / 'code')
    run('frame-controls', HERE / 'frame_controls.py', word, routing, out / 'FRAME-CONTROLS.json', rfile, portable=False)
    fc = read(out / 'FRAME-CONTROLS.json')
    assert fc['status'] == 'PASS_FOCUSED_EIGHT_FRAME_NATIVE_CONTROLS' and len(fc['rejected']) == pins['frame_controls'], len(fc['rejected'])
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
