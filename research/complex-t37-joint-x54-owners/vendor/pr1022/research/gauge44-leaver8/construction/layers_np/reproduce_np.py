#!/usr/bin/env python3
"""Rebuild the layered no-triangle word (NP) and its native locals.

Input: a fresh `construction/notri/reproduce_notri.py --word-only` output directory. That driver pins the
no-triangle word (3e99ba77...) and writes its regroup/ and cold44/ words. Steps, each checked exactly:
  1. pivot-swap: ../layers/build_pivot_swap.py (PR641's constructor, signed, unchanged) on the no-triangle regroup word, with PIVOT-SWAP-NP.json:
     the six pivot-role swaps of research/gauge44-layered, mapped through the 504-helper map (494->566, 495->567,
     506->578, 507->579, 519->543, 531->555). Exact zero-response replay, unchanged profile and width multiset,
     30 negative controls.
  2. hpe: PR635's build_hpe.candidates, greedy with disjoint registers. Must equal HPE-RECIPE-NP.json (46 changes,
     the same helpers as the unswapped word); applied with build_hpe.apply.
  3. cold44-exact: notri/cold44x.py on the swapped HPE word, pairing ranks pinned [4]*14. Its 56 cold ends, premix
     and low tails must equal the unswapped no-triangle construction's.
  4. layers: PR635's unchanged build_cold_end.apply(HPE, COLD-LAYERS-RECIPE-NP): cold44 plus the entering ends
     566/567/578/579 at U24 (s4) and 608/610/543/555 at U30 (x30), BlockCombine's b6 and the q4 dim-8 cold ends.
     The output word sha and its profile and widths are pinned.
  5. layer-end-controls: ../layers/layer_end_controls.py (LayerReviewer's signed adaptation of PR635's
     cold_end_controls.py, unchanged) on the layered word; exactly 59 rejections at pinned reasons.
../layers/reproduce_layers.py is research/gauge44-layered's driver for the 492-helper word, shipped unchanged as
signed; it is not used for this word.
  6. native, ledgers, local-replay, wrappers, phases: PR635's native local programs, with pins.
Apache-2.0. Driver by ColdWitness after G44Stack's NP chain (NP/chain.py, seq.py).
"""
import argparse, gzip, hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTRI = HERE.parent / 'notri'
LAYERS = HERE.parent / 'layers'   # the signed research/gauge44-layered files, unchanged
REGROUP_SHA = '864ff4a1'   # prefix; full value checked against PIVOT-SWAP-NP.json's input_content_sha256
SWAP_SHA = 'beb3579f'
NP_SHA = 'a9de804f194eeb39f52a4c6e54c14d93e881bec4b632694249733ed410b58113'
LAYER_CONTROLS = 59
CANONICAL_SHA = '1ae812a336178760071efe347e876e0102b5b71f799d957db15c5f3004c19d7a'
PROGRAM_SHA = {'forward': 'a3882a428bdafab888072211d4ed8d34572746873d77c6ef900495853cc3fa11',
               'backward': 'f67a3dc20c27fb39295b8030e951e9779109ef1537f6f8de9d08510b9ad6792a'}
CLIFFORD_SHA = '890b60fc4ae183c773c51405e0f4ef6a945dc2aae55ba2480f134602e8296cda'


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def enc(x): return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def dump(p, v):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(gzip.compress(enc(v), mtime=0))


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--notri-dir', type=Path, required=True, help='construction/notri/reproduce_notri.py --word-only output')
    ap.add_argument('--hamming', type=Path, required=True, help='hamming/ of the construction/reproduce.py --until word output')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skip-phases', action='store_true')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'; gk = parent / 'complex-local/static44/gk'
    nd = a.notri_dir.resolve()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET'): env.pop(k, None)
    steps = []

    def run(label, script, *args):
        t = time.monotonic()
        with (out / (label + '.log')).open('w') as f:
            rc = subprocess.call([sys.executable, '-B', str(src / 'code/run_portable.py'), str(script), *map(str, args)],
                                 env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3)))
        (out / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert rc == 0, label
        print('PASS', label, flush=True)

    # the input must be the pinned no-triangle construction
    nr = load('notri_driver', NOTRI / 'reproduce_notri.py')
    assert hashlib.sha256(enc(read(nd / 'cold44/FULL-WORD.json.gz'))).hexdigest() == nr.NOTRI_SHA, 'notri word'
    # 1. pivot swaps on the regroup word
    rg = hashlib.sha256(enc(read(nd / 'regroup/FULL-WORD.json.gz'))).hexdigest()
    assert rg.startswith(REGROUP_SHA) and rg == read(HERE / 'PIVOT-SWAP-NP.json')['input_content_sha256'], ('regroup word', rg)
    run('pivot-swap', LAYERS / 'build_pivot_swap.py', '--input', nd / 'regroup/FULL-WORD.json.gz',
        '--recipe', HERE / 'PIVOT-SWAP-NP.json', '--gk-dir', gk, '--out', out / 'swap')
    w = read(out / 'swap/FULL-WORD.json.gz')
    sw = hashlib.sha256(enc(w)).hexdigest(); assert sw.startswith(SWAP_SHA) and sw == read(HERE / 'PIVOT-SWAP-NP.json')['output_content_sha256'], ('swap word', sw)
    # 2. HPE (greedy, must equal the pinned recipe)
    h = load('upstream_hpe', up / 'code/build_hpe.py')
    used, ch = set(), []
    for c in h.candidates(w):
        rs = set(h.regs(w['cleanup'][c['cleanup_index']]))
        if rs & used: continue
        used |= rs; ch.append(c)
    assert ch == read(HERE / 'HPE-RECIPE-NP.json')['changes'], 'HPE recipe'
    w = h.apply(w, ch); dump(out / 'hpe/FULL-WORD.json.gz', w)
    # 3. cold44 on the swapped word: same ends, premix and tails as the unswapped no-triangle construction
    hm = set(read(nd / 'raw/HELPER-MAP.json')['map'].values())
    env['EXTRAH'] = json.dumps(sorted(set(range(224, 224 + w['report']['R'])) - hm))
    env['PAIRING_RANKS'] = json.dumps([4] * 14)
    run('cold44-exact', NOTRI / 'cold44x.py', '--input', out / 'hpe/FULL-WORD.json.gz', '--out', out / 'cold44',
        '--hamming', a.hamming.resolve(), '--upstream-package', up)
    for k in ('EXTRAH', 'PAIRING_RANKS'): env.pop(k)
    new, old = read(out / 'cold44/RECIPE.json.gz'), read(nd / 'cold44/RECIPE.json.gz')
    for key in ('premix', 'early_cleanup', 'cold_ends'):
        assert new[key] == old[key], ('swapped cold44 differs from the pinned no-triangle construction', key)
    tail = len(new['early_cleanup']); assert new['cleanup'][:tail] == old['cleanup'][:tail], 'low tails'
    # 4. layers
    bce = load('upstream_cold', up / 'code/build_cold_end.py')
    layered = bce.apply(w, read(HERE / 'COLD-LAYERS-RECIPE-NP.json.gz'))
    raw = enc(layered); assert hashlib.sha256(raw).hexdigest() == NP_SHA, ('layered word', hashlib.sha256(raw).hexdigest())
    rep = layered['report']
    assert rep['local_profile'] == {'1': 2534, '2': 346, '3': 458, '4': 178, '5': 56, '8': 8}, rep['local_profile']
    assert rep['width_inventory'] == {'4': 64, '5': 48, '7': 54, '8': 116, '9': 222}, rep['width_inventory']
    (out / 'layers').mkdir(); word = out / 'layers/FULL-WORD.json.gz'; word.write_bytes(gzip.compress(raw, mtime=0))
    print('PASS layered no-triangle word', NP_SHA, flush=True)
    # 5. layer-end controls
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env['PR635_CODE'] = str(up / 'code')
    run('layer-end-controls', LAYERS / 'layer_end_controls.py', word, routing, out / 'controls')
    env.pop('PR635_CODE')
    ctl = json.loads((out / 'controls/COLD-END-CONTROLS.json').read_text())
    assert ctl['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS' and len(ctl['rejected']) == LAYER_CONTROLS, len(ctl['rejected'])
    # 6. native locals
    local = out / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', word, '--routing', routing, '--out', local)
    assert hashlib.sha256(gzip.decompress((local / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest() == CANONICAL_SHA, 'canonical word'
    run('ledgers', up / 'code/hpe_emit_local.py', local)
    run('local-replay', up / 'code/hpe_audit_local.py', local)
    run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz',
        local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    checks = read(local / 'LOCAL-CHECKS.json')
    for o, s in PROGRAM_SHA.items(): assert checks[o]['sha256'] == s, ('local program', o)
    if not a.skip_phases:
        run('phases', base / 'code/phases_full.py', local, parent / 'complex-global/vendor531/vendor/clifford')
        assert hashlib.sha256((local / 'CLIFFORD-RECIPES.json').read_bytes()).hexdigest() == CLIFFORD_SHA, 'clifford recipes'
    print('DONE', local, flush=True)


if __name__ == '__main__':
    main()
