#!/usr/bin/env python3
"""Rebuild the leaver word: the no-triangle word with no-helper mutable-leaver all-K cells, and its native locals.

Each cell (pair p, sign e) replaces the three face events of the blocks containing p and their three packet copies
by a 21-gate circuit on the cell's six leaver sources x_j (the face-event operands, which have no later reads and are
restored by the inherited cleanup at FULL) and its six targets y_i: 3 leaver gates x_k += c x_m, 3 target gates
y_a += c y_b (inverted at frame zero in the precondition and scatter, #781's recipe) and 15 reads y_i += c x_j.
Unit circuit (LeaverSAT, layered CP-SAT on the exact set model), relabelled per cell so that no y += y source carries
port-stage entering-helper dirt at the gate; coefficients rescaled exactly to the cell (C_ij = r_i c_j).
Input: a fresh `construction/reproduce.py --until word` output directory (hamming/, shadow-early/, shadow-prefix/).
Steps, each checked exactly (pins in LEAVER-PINS.json):
  0. cells: CODED-CELLS.json's scaled gates are re-derived from the unit circuits and the cell coefficients, and the
     clean map Y_i = sum_j C_ij X_j is checked in exact rationals.
  1. gauge-forward: cgx_leaver.py (notri/cgx.py + the leaver edits) with TRI-LEAVER.json, XPARAM = notri/PRIO6.json.
  2. port0-3: notri/port_stage_x.py.
  3. regroup: REGROUP-LEAVER.json's changes where their `before` gate occurs (count pinned).
  4. hpe: PR635's build_hpe.candidates greedy with disjoint registers, build_hpe.apply (recipe pinned).
  5. cold44: notri/cold44x.py with EXTRAH and pinned pairing ranks; output sha, profile and widths pinned.
  6. native, ledgers, local-replay, wrappers, phases: PR635's native local programs (pins).
Apache-2.0. LeaverSAT (Claude Code research agent), driver after construction/notri/reproduce_notri.py.
"""
import argparse, gzip, hashlib, importlib.util, json, os, shutil, subprocess, sys, time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTRI = HERE.parent / 'notri'


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def enc(x): return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def dump(p, v):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(gzip.compress(enc(v), mtime=0))


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def check_cells(cells):
    for c in cells:
        C = [[Fraction(q) for q in r] for r in c['coefficients']]
        col = [None] * 6; row = [Fraction(1)] + [None] * 5
        for j in range(1, 6): col[j] = C[0][j]
        col[0] = C[1][0] / (C[1][2] / col[2])
        for i in range(1, 6): row[i] = C[i][(i + 1) % 6] / col[(i + 1) % 6]
        assert all(C[i][j] == row[i] * col[j] for i in range(6) for j in range(6) if i != j), ('rank-one cell', c['cell'])
        idx = lambda s: int(s[1:])
        scaled = []
        for t, s, q in c['unit']:
            assert Fraction(q) == 1
            if t[0] == 'x': assert s[0] == 'x'; q = col[idx(s)] / col[idx(t)]
            elif s[0] == 'y': q = row[idx(t)] / row[idx(s)]
            else: q = row[idx(t)] * col[idx(s)]
            scaled.append([t, s, str(q)])
        assert scaled == c['scaled'], ('scaled gates', c['cell'])
        R = {f'x{j}': {j: Fraction(1)} for j in range(6)}; R.update({f'y{i}': {} for i in range(6)})
        for t, s, q in scaled:
            for k, x in list(R[s].items()): R[t][k] = R[t].get(k, 0) + Fraction(q) * x
        for i in range(6):
            assert {k: x for k, x in R[f'y{i}'].items() if x} == {j: C[i][j] for j in range(6) if j != i}, ('clean map', c['cell'], i)


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--word-dir', type=Path, required=True, help='construction/reproduce.py --until word output')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skip-phases', action='store_true')
    ap.add_argument('--word-only', action='store_true', help='stop after the pinned scalar word (input to the layers)')
    ap.add_argument('--id', default='k5', help='cell set: TRI-LEAVER-<id>, CODED-CELLS-<id>, REGROUP-LEAVER-<id>, LEAVER-PINS-<id>')
    ap.add_argument('--record-pins', action='store_true', help='write LEAVER-PINS.json from this run instead of checking')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    pins = {} if a.record_pins else read(HERE / ('LEAVER-PINS-%s.json' % a.id)); got = {}
    def pin(k, v):
        got[k] = v
        if not a.record_pins: assert pins[k] == v, ('pin', k, v, pins[k])
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'; gk = parent / 'complex-local/static44/gk'
    structural = a.main.resolve() / 'research/structural-gain/frontier-composition'
    wd = a.word_dir.resolve()
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

    # 0. cells
    cells = read(HERE / ('CODED-CELLS-%s.json' % a.id)); check_cells(cells); print('PASS cells', [c['cell'] for c in cells], flush=True)
    # 1. gauge-forward
    shutil.copy(HERE / ('TRI-LEAVER-%s.json' % a.id), out / 'TRI.json'); shutil.copy(HERE / ('CODED-CELLS-%s.json' % a.id), out / 'CODED-CELLS.json')
    env['XPARAM'] = str(NOTRI / 'PRIO6.json')
    raw = out / 'raw'
    run('gauge-forward', HERE / 'cgx_leaver.py', wd / 'hamming', raw, out / 'TRI.json')
    word = raw / 'FULL-WORD.json.gz'; pin('raw_sha256', hashlib.sha256(enc(read(word))).hexdigest())
    # 2. port stages
    chain = [parent / 'complex-local/static44/inputs/RAW504.json.gz', structural / 'global-replay/base/split-centres/FULL-WORD.json.gz',
             wd / 'shadow-early/FULL-WORD.json.gz', structural / 'multicold-eight-word/FULL-WORD.json.gz',
             wd / 'shadow-prefix/FULL-WORD.json.gz']
    for i, (b, c) in enumerate(zip(chain, chain[1:])):
        t = out / ('port%d' % i)
        run('port%d' % i, NOTRI / 'port_stage_x.py', '--shadow-input', b, '--shadow-output', c, '--input', word,
            '--map', raw / 'HELPER-MAP.json', '--gk-dir', gk, '--out', t)
        word = t / 'FULL-WORD.json.gz'
    # 3. regroup
    w = read(word); rg = {json.dumps(c['before']): c['after'] for c in read(HERE / ('REGROUP-LEAVER-%s.json' % a.id))['changes']}
    n = 0
    for part in ('A', 'B'):
        for i, e in enumerate(w[part]):
            k = json.dumps(e)
            if k in rg: w[part][i] = rg[k]; n += 1
    sys.path.insert(0, str(gk)); import gk_word as GW, gk_common as GC
    GW.V = GC.V = 112; GW.DATA = GC.DATA = 7168
    H = GW.profile(w)
    w['report'].update(local_profile={str(k): z for k, z in sorted(H.items()) if z}, local_rank_mass=sum(r * z for r, z in H.items()))
    pin('regroup_count', n); dump(out / 'regroup/FULL-WORD.json.gz', w); pin('regroup_sha256', hashlib.sha256(enc(w)).hexdigest())
    # 4. HPE
    h = load('upstream_hpe', up / 'code/build_hpe.py')
    used, ch = set(), []
    for c in h.candidates(w):
        rs = set(h.regs(w['cleanup'][c['cleanup_index']]))
        if rs & used: continue
        used |= rs; ch.append(c)
    (out / 'HPE-RECIPE.json').write_text(json.dumps(dict(changes=ch)))
    pin('hpe_recipe_sha256', hashlib.sha256(enc(dict(changes=ch))).hexdigest())
    w = h.apply(w, ch); dump(out / 'hpe/FULL-WORD.json.gz', w)
    # 5. cold44
    hm = set(read(raw / 'HELPER-MAP.json')['map'].values())
    env['EXTRAH'] = json.dumps(sorted(set(range(224, 224 + w['report']['R'])) - hm))
    if not a.record_pins: env['PAIRING_RANKS'] = json.dumps(pins['pairing_ranks'])
    run('cold44', NOTRI / 'cold44x.py', '--input', out / 'hpe/FULL-WORD.json.gz', '--out', out / 'cold44',
        '--hamming', wd / 'hamming', '--upstream-package', up)
    pin('pairing_ranks', [b['pairing_rank'] for b in read(out / 'cold44/CONSTRUCTION.json')['blocks']])
    word = out / 'cold44/FULL-WORD.json.gz'; w = read(word)
    pin('cold44_sha256', hashlib.sha256(enc(w)).hexdigest()); rep = w['report']
    pin('R', rep['R']); pin('local_profile', rep['local_profile']); pin('width_inventory', rep['width_inventory'])
    print('PASS leaver scalar word', got['cold44_sha256'], flush=True)
    if not a.word_only:
        for k in ('XPARAM', 'EXTRAH', 'PAIRING_RANKS'): env.pop(k, None)
        local = out / 'local'
        run('native', up / 'code/hpe_audit_and_transport.py', '--raw', word,
            '--routing', parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz', '--out', local)
        pin('canonical_sha256', hashlib.sha256(gzip.decompress((local / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest())
        run('ledgers', up / 'code/hpe_emit_local.py', local)
        run('local-replay', up / 'code/hpe_audit_local.py', local)
        run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz',
            local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
        checks = read(local / 'LOCAL-CHECKS.json')
        pin('program_sha256', {o: checks[o]['sha256'] for o in ('forward', 'backward')})
        if not a.skip_phases:
            run('phases', base / 'code/phases_full.py', local, parent / 'complex-global/vendor531/vendor/clifford')
            pin('clifford_recipes_sha256', hashlib.sha256((local / 'CLIFFORD-RECIPES.json').read_bytes()).hexdigest())
    if a.record_pins: (HERE / ('LEAVER-PINS-%s.json' % a.id)).write_text(json.dumps(got, indent=1) + '\n')
    print('DONE', out, flush=True)


if __name__ == '__main__':
    main()
