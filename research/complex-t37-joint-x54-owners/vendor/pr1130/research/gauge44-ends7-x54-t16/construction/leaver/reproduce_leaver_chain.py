#!/usr/bin/env python3
"""Rebuild the leaver stack on top of the leaver cell word: layers (NP, p6n), promotions, joint exchange and U8-style
hybrids, and the final word's native locals.

Input: a fresh `construction/leaver/reproduce_leaver.py --word-only` output directory (raw/HELPER-MAP.json, regroup/,
cold44/; the cell word and its regroup word are pinned there by LEAVER-PINS.json). Each step uses an unchanged signed
builder with a LeaverSAT recipe (data only), and every intermediate word is pinned:
  1. pivot-swap: ../layers/build_pivot_swap.py with PIVOT-SWAP-<id>.json on the regroup word (its own 30 controls).
  2. hpe: PR635's build_hpe.candidates (greedy, disjoint registers) must equal HPE-RECIPE-<id>.json; build_hpe.apply.
     The swapped HPE word is pinned by the cold-layer recipes' input_content_sha256.
  3. cold44-exact: ../notri/cold44x.py on the swapped HPE word (pairing ranks pinned to LEAVER-PINS); its cold ends,
     premix and low tails must equal the unswapped leaver construction's.
  4. layers: PR635's build_cold_end.apply(HPE, COLD-LAYERS-RECIPE-NP-<id>) -> NP word and (.., -P6N-<id>) -> p6n word;
     output shas pinned by the recipes.
  5. promotion: ../promo/build_promotion.py with PROMO-RECIPE-<id>.json on the p6n word; ../promo/promo_controls.py.
  6. jx: ../jx/build_jx.py with RECIPE-X4-<id>.json on the promoted word; all recipe controls rerun at their pins.
  7. hybrids: ../barch/build_tri.py with RECIPE-U8-<id>.json on the jx word; ../barch/run_controls.py (all outcomes).
  8. frames: build_frames_lv.py (LeaverSAT2) applies FRAME-RECIPE-LV-<id>.json (B/T frame changes, exact global frame
     optimum) with ../promo/build_promotion.apply; scalar program unchanged; 3 pin controls; output pinned.
  8b. layer-end-controls: layer_end_controls_leaver.py (v2: the signed per-end controls with per-word reason re-pins
     and declared not-applicable sites, each replaced by a same-class substitute mutant) on the p6n, promoted, jx and
     hybrid words with LEC-REASON-PINS-STACK-<id>.json, and on the re-framed final word with LEC-REASON-PINS-<id>.json;
     counts, not-applicable sites and the sha256 of each pins file pinned.
  9. native, ledgers, local-replay, wrappers, phases on the final word; canonical, programs, Clifford pinned.
All counts and native pins are in CHAIN-PINS-<id>.json (--record-pins writes it from a run instead of checking;
a checking run requires its pins to equal the file exactly).
Apache-2.0. Driver by ColdWitness over LeaverSAT's frozen recipes and the signed builders.
"""
import argparse, gzip, hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = HERE.parent
MUTANTS = ('drop_restore', 'restore_full', 'drop_preread', 'donation_after')


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def enc(x): return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def csha(p): return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--leaver-dir', type=Path, required=True, help='construction/leaver/reproduce_leaver.py --word-only output')
    ap.add_argument('--hamming', type=Path, required=True, help='hamming/ of the construction/reproduce.py --until word output')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skip-phases', action='store_true')
    ap.add_argument('--id', default='k5', help='recipe set id: every recipe and pin file below is <NAME>-<id>')
    ap.add_argument('--record-pins', action='store_true')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'; gk = parent / 'complex-local/static44/gk'
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    lp = read(HERE / ('LEAVER-PINS-%s.json' % a.id))
    pins = {} if a.record_pins else read(HERE / ('CHAIN-PINS-%s.json' % a.id)); got = {}

    def pin(key, value):
        got[key] = value
        if not a.record_pins: assert pins[key] == value, (key, value, pins.get(key))

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE', 'LEC_REASON_PINS', 'SW4_PIN'): env.pop(k, None)
    steps = []

    def run(label, script, *args, portable=True, extra=None):
        t = time.monotonic(); e = dict(env, **(extra or {}))
        cmd = [sys.executable, '-B'] + ([str(src / 'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (out / (label + '.log')).open('w') as f:
            rc = subprocess.call(cmd, env=e, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3)))
        (out / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert rc == 0, label
        print('PASS', label, flush=True)
        return (out / (label + '.log')).read_text()

    def lec(label, word, pins_name):
        pf = HERE / ('%s-%s.json' % (pins_name, a.id)); pin(label + '_pins_sha256', hashlib.sha256(pf.read_bytes()).hexdigest())
        run(label, HERE / 'layer_end_controls_leaver.py', word, routing, out / label,
            extra=dict(PR635_CODE=str(up / 'code'), LEC_REASON_PINS=str(pf)))
        c = read(out / label / 'COLD-END-CONTROLS.json'); assert c['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS'
        pin(label, len(c['rejected'])); pin(label + '_not_applicable', {x['site']: x['reason'] for x in c['not_applicable']})

    ld = a.leaver_dir.resolve()
    assert hashlib.sha256(enc(read(ld / 'cold44/FULL-WORD.json.gz'))).hexdigest() == lp['cold44_sha256'], 'leaver cell word'
    rg = ld / 'regroup/FULL-WORD.json.gz'
    sw = read(HERE / ('PIVOT-SWAP-%s.json' % a.id))
    assert hashlib.sha256(enc(read(rg))).hexdigest() == lp['regroup_sha256'] == sw['input_content_sha256'], 'regroup word'
    # 1. pivot swaps
    run('pivot-swap', C / 'layers/build_pivot_swap.py', '--input', rg, '--recipe', HERE / ('PIVOT-SWAP-%s.json' % a.id), '--gk-dir', gk, '--out', out / 'swap')
    w = read(out / 'swap/FULL-WORD.json.gz'); assert hashlib.sha256(enc(w)).hexdigest() == sw['output_content_sha256'], 'swap word'
    # 2. HPE
    h = load('upstream_hpe', up / 'code/build_hpe.py'); used, ch = set(), []
    for c in h.candidates(w):
        rs = set(h.regs(w['cleanup'][c['cleanup_index']]))
        if rs & used: continue
        used |= rs; ch.append(c)
    assert ch == read(HERE / ('HPE-RECIPE-%s.json' % a.id))['changes'], 'HPE recipe'
    w = h.apply(w, ch); (out / 'hpe').mkdir(); (out / 'hpe/FULL-WORD.json.gz').write_bytes(gzip.compress(enc(w), mtime=0))
    rnp, rp6 = read(HERE / ('COLD-LAYERS-RECIPE-NP-%s.json.gz' % a.id)), read(HERE / ('COLD-LAYERS-RECIPE-P6N-%s.json.gz' % a.id))
    assert hashlib.sha256(enc(w)).hexdigest() == rnp['input_content_sha256'] == rp6['input_content_sha256'], 'swapped HPE word'
    # 3. cold44 on the swapped word: same ends, premix and tails
    hm = set(read(ld / 'raw/HELPER-MAP.json')['map'].values())
    run('cold44-exact', C / 'notri/cold44x.py', '--input', out / 'hpe/FULL-WORD.json.gz', '--out', out / 'cold44',
        '--hamming', a.hamming.resolve(), '--upstream-package', up,
        extra=dict(EXTRAH=json.dumps(sorted(set(range(224, 224 + w['report']['R'])) - hm)), PAIRING_RANKS=json.dumps(lp['pairing_ranks'])))
    new, old = read(out / 'cold44/RECIPE.json.gz'), read(ld / 'cold44/RECIPE.json.gz')
    for key in ('premix', 'early_cleanup', 'cold_ends'): assert new[key] == old[key], ('swapped cold44 differs', key)
    tail = len(new['early_cleanup']); assert new['cleanup'][:tail] == old['cleanup'][:tail], 'low tails'
    # 4. NP and p6n layers
    bce = load('upstream_cold', up / 'code/build_cold_end.py')
    for name, r in (('np', rnp), ('p6n', rp6)):
        lw = bce.apply(w, r); raw = enc(lw); assert hashlib.sha256(raw).hexdigest() == r['output_content_sha256'], (name, 'word')
        (out / name).mkdir(); (out / name / 'FULL-WORD.json.gz').write_bytes(gzip.compress(raw, mtime=0))
        pin(name + '_profile', lw['report']['local_profile'])
    p6n = out / 'p6n/FULL-WORD.json.gz'; lec('lec-p6n', p6n, 'LEC-REASON-PINS-STACK')
    # 5. promotion
    pr = HERE / ('PROMO-RECIPE-%s.json' % a.id)
    run('promotion', C / 'promo/build_promotion.py', '--input', p6n, '--recipe', pr, '--out', out / 'promo', portable=False)
    assert csha(out / 'promo/FULL-WORD.json.gz') == read(pr)['expected']['output_content_sha256']
    run('promo-controls', C / 'promo/promo_controls.py', '--input', p6n, '--recipe', pr, '--audit', C.parent / 'independent/audit_local.py',
        '--out', out / 'PROMO-CONTROLS.json', portable=False)
    pc = read(out / 'PROMO-CONTROLS.json'); assert pc['honest'] == 'PASS'; pin('promo_controls', pc['rejected'])
    lec('lec-promo', out / 'promo/FULL-WORD.json.gz', 'LEC-REASON-PINS-STACK')
    # 6. jx
    xr = HERE / ('RECIPE-X4-%s.json' % a.id); rec = read(xr); inp = out / 'promo/FULL-WORD.json.gz'
    (out / 'jx').mkdir(); jw = out / 'jx/FULL-WORD.json.gz'
    run('jx', C / 'jx/build_jx.py', '--input', inp, '--recipe', xr, '--out', jw, portable=False)
    assert csha(jw) == rec['expected']['output_content_sha256']
    for name, cc in sorted(rec['controls'].items()):
        log = run('jx-control-' + name, C / 'jx/build_jx.py', '--input', inp, '--recipe', xr, '--control', name, portable=False)
        if 'rejection_expected' in cc: assert 'CONTROL PINNED' in log, (name, log[-300:])
        else: assert ('OK ' + cc['expected_sha']) in log, (name, log[-300:])
    pin('jx_controls', sorted(rec['controls']))
    lec('lec-jx', jw, 'LEC-REASON-PINS-STACK')
    # 7. hybrids
    ur = HERE / ('RECIPE-U8-%s.json' % a.id); u = read(ur); (out / 'hyb').mkdir(); fw = out / 'hyb/FULL-WORD.json.gz'
    run('hybrids', C / 'barch/build_tri.py', jw, ur, fw, portable=False)
    assert csha(fw) == u['expect_sha256']
    run('hybrid-controls', C / 'barch/run_controls.py', jw, ur, C.parent / 'independent/audit_local.py', out / 'hybrid-controls', portable=False)
    res = read(out / 'hybrid-controls/controls.json')
    want = ['C0_identity', 'recipe', *MUTANTS] + [m + '@' + str(v['X']) for v in u.get('variants', []) for m in MUTANTS]
    assert sorted(res) == sorted(want) and all(x['ok'] for x in res.values()), res
    pin('hybrid_controls', sorted(want))
    lec('lec-hyb', fw, 'LEC-REASON-PINS-STACK')
    # 8. frame re-optimisation (LeaverSAT2): exact global frame optimum of the hybrid word; scalar program unchanged
    fr = HERE / ('FRAME-RECIPE-LV-%s.json' % a.id); frec = read(fr)
    run('frames', HERE / 'build_frames_lv.py', fw, out / 'frames', fr, portable=False)
    fw = out / 'frames/FULL-WORD.json.gz'; assert csha(fw) == frec['expected']['output_content_sha256']
    pin('frame_build_controls', len(read(out / 'frames/BUILD.json')['rejected_controls']))
    # 8b. layer-end controls on the re-framed final word (v2, not-applicable sites declared in LEC-REASON-PINS-<id>):
    # the frame re-optimisation lowers an entering-end tail frame to a dimension no helper_final frame has, so that
    # site's 'end at another hyperplane' mutant is replaced by its same-class substitute.
    lec('lec-frames', fw, 'LEC-REASON-PINS')
    # 9. native locals of the final word
    local = out / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', fw, '--routing', routing, '--out', local)
    pin('canonical_sha256', hashlib.sha256(gzip.decompress((local / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest())
    run('ledgers', up / 'code/hpe_emit_local.py', local)
    run('local-replay', up / 'code/hpe_audit_local.py', local)
    run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz', local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    checks = read(local / 'LOCAL-CHECKS.json'); pin('program_sha256', {o: checks[o]['sha256'] for o in ('forward', 'backward')})
    if not a.skip_phases:
        run('phases', base / 'code/phases_full.py', local, parent / 'complex-global/vendor531/vendor/clifford')
        pin('clifford_recipes_sha256', hashlib.sha256((local / 'CLIFFORD-RECIPES.json').read_bytes()).hexdigest())
    if a.record_pins: (out / ('CHAIN-PINS-%s.json' % a.id)).write_bytes((json.dumps(got, indent=1) + '\n').encode())
    else: assert got == pins, ('chain pins differ', sorted(set(got) ^ set(pins)))
    print('DONE', local, flush=True)


if __name__ == '__main__':
    main()
