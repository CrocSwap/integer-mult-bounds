#!/usr/bin/env python3
"""Rebuild the SW4 word (BRoute read-set exchange on four entering-copy pairs) and its native locals.

Input: a fresh `construction/promo/reproduce_promo.py --base p6n --k <promo recipe>` output directory; its promoted
word is pinned there and by SW4-RECIPE-<id>.json (this package: --k p6n-k4, P6k4 0390ec65..., recipe P6k4). Steps, each checked exactly:
  1. sw4: BRoute's build_sw4.py (standard library only). It applies the 16 explicit moves of SW4-RECIPE-<id>.json:
     every listed read of h becomes a read of its face register r and vice versa, with the entrance pre-reads deleted
     or inserted. It checks the B-end state of every register mod p, the frame caps, tails and ends, and the output sha
     and profile. Its controls C0, N1, N2 and N3 run on every build and must all hold (count pinned to 4).
  2. layer-end-controls: ../layers_p6n/layer_end_controls.py (per-end variant, Q6Reviewer-signed) on the SW4 word;
     the count is pinned in LOCAL-PINS-sw4-<id>.json.
  3. native, ledgers, local-replay, wrappers, phases: PR635's native local programs. The canonical word, local
     programs and Clifford recipes are pinned (LOCAL-PINS-sw4-<id>.json).
Apache-2.0. Driver by ColdWitness around BRoute's constructor.
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
    ap.add_argument('--promo-dir', type=Path, required=True, help='construction/promo/reproduce_promo.py output')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--recipe', default='P6k4', help='SW4-RECIPE-<id>.json and LOCAL-PINS-sw4-<id>.json')
    ap.add_argument('--skip-phases', action='store_true')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'
    rfile = HERE / ('SW4-RECIPE-%s.json' % a.recipe); rec = read(rfile); pins = read(HERE / ('LOCAL-PINS-sw4-%s.json' % a.recipe))
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

    inp = a.promo_dir.resolve() / 'promo/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(inp.read_bytes())).hexdigest() == rec['input_sha256'], 'input must be the pinned promoted word'
    run('sw4', HERE / 'build_sw4.py', inp, out / 'sw4', rfile, portable=False)
    b = read(out / 'sw4/BUILD.json')
    assert len(b['controls']) == pins['sw4_controls'] and all(b['controls'].values()), b['controls']
    word = out / 'sw4/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest() == rec['output_sha256']
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
