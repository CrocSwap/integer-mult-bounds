#!/usr/bin/env python3
"""Rebuild the no-triangle gauge44 word (R = 504) and its native locals.

The no-triangle word is #645's gauge44 chain with none of the four (p,-1) K-triangles. In the six K-blocks
{0,1,2,11,12,13}, the completion priority is extended by the 6-row list PRIO6.json, the list blocks 3-10 already use.
Each block then pairs at rank 4, giving 56 rank-four cold ends instead of 44 (PartialK).

Input: a fresh `construction/reproduce.py --until word` output directory. Its shadow-early and shadow-prefix words and
its hamming inputs are pinned by reproduce.py itself. Steps, each checked exactly:
  1. gauge-forward: cgx.py, #645's construct_gauge_xcentre.py generalised by PartialK. The extra rows come from XPARAM,
     and the K-triangle schedule comes from the TRI file. Run on the triangle set {} with XPARAM = PRIO6.json.
  2. port0-3: port_stage_x.py, PR635's build_port_stage.py with the helper map allowed to be injective rather than onto.
     With R = 504 and no triangles, the map is onto again.
  3. regroup: PR635's k492 frame-regroup changes, applied where their `before` gate occurs. For this word none occurs,
     and that count (0) is pinned.
  4. hpe: PR635's build_hpe.candidates, taken greedily with disjoint registers, and build_hpe.apply. 46 changes, pinned.
  5. cold44: cold44x.py, #645's build_gauge_cold44.py generalised by PartialK to blocks whose helper list includes the
     helpers outside the 224+16b ranges (EXTRAH). 56 cold ends; the 14 pairing ranks are pinned to [4]*14 inside cold44x (PAIRING_RANKS) and rechecked here. The output word content sha256 is pinned (3e99ba77...).
  6. native, ledgers, local-replay, wrappers, phases: PR635's native local programs, as in reproduce.py.
--control-g44 instead runs steps 1-5 with #645's four triangles and no XPARAM. It must reproduce #645's pinned gauge44
cold44 word (78c7aada...), the same word #645's own reproduce.py builds. This shows the generalised scripts reduce to
#645's constructors.
Apache-2.0. Driver by ColdWitness from PartialK's variant.py; constructors credited above.
"""
import argparse, gzip, hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTRI_SHA = '3e99ba778ab8a97853f50912776247802b529439937176363f6c42786163b1f9'
G44_SHA = '78c7aadacb6eec2eeecc124ca236e5bcfdba6a52b30c2971aaa596d1d119b290'
# native-local pins (the strict locals the SPEC was frozen against: PartialK runs/none_p6/local)
CANONICAL_SHA = '4265a3bb7f9b46967dfadfca5f2cc1f5b3e6e8681f16c02590f1b9430c013637'
PROGRAM_SHA = {'forward': '0afda28699e15cf5a5a17aee5475ac608c9fb68b15766d463b93ec8e2df4ae85',
               'backward': '5be6cb4ea7a1da36d7bbe7eb2392873c058dd3cbb3cc2eeadd55ecca9310ca8a'}
CLIFFORD_SHA = '4b5789e43e04d71f02c2d480450ec0b354007d9cf523bda76c7345730806344b'


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
    ap.add_argument('--word-dir', type=Path, required=True, help='construction/reproduce.py --until word output')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--control-g44', action='store_true', help='rebuild #645 gauge44 (4 triangles) instead; word only')
    ap.add_argument('--skip-phases', action='store_true')
    ap.add_argument('--word-only', action='store_true', help='stop after the pinned scalar word (input to construction/layers_np)')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
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

    # 1. gauge-forward on the chosen K-triangle set
    tri = read(up / 'data/TRI-SCHEDULE.json')
    if not a.control_g44:
        tri = dict(full_pairs=tri['full_pairs'], triangles=[])
        env['XPARAM'] = str(HERE / 'PRIO6.json')
    (out / 'TRI.json').write_text(json.dumps(tri))
    raw = out / 'raw'
    run('gauge-forward', HERE / 'cgx.py', wd / 'hamming', raw, out / 'TRI.json')
    word = raw / 'FULL-WORD.json.gz'
    # 2. port stages (same chain as reproduce.py)
    chain = [parent / 'complex-local/static44/inputs/RAW504.json.gz', structural / 'global-replay/base/split-centres/FULL-WORD.json.gz',
             wd / 'shadow-early/FULL-WORD.json.gz', structural / 'multicold-eight-word/FULL-WORD.json.gz',
             wd / 'shadow-prefix/FULL-WORD.json.gz']
    for i, (b, c) in enumerate(zip(chain, chain[1:])):
        t = out / ('port%d' % i)
        run('port%d' % i, HERE / 'port_stage_x.py', '--shadow-input', b, '--shadow-output', c, '--input', word,
            '--map', raw / 'HELPER-MAP.json', '--gk-dir', gk, '--out', t)
        word = t / 'FULL-WORD.json.gz'
    # 3. PR635 frame regroup where its `before` gate occurs
    w = read(word); rg = {json.dumps(c['before']): c['after'] for c in read(up / 'data/recipes/k492-jp8-frame_regroup.json')['changes']}
    n = 0
    for part in ('A', 'B'):
        for i, e in enumerate(w[part]):
            k = json.dumps(e)
            if k in rg: w[part][i] = rg[k]; n += 1
    sys.path.insert(0, str(gk)); import gk_word as GW, gk_common as GC
    GW.V = GC.V = 112; GW.DATA = GC.DATA = 7168
    H = GW.profile(w)
    w['report'].update(local_profile={str(k): z for k, z in sorted(H.items()) if z}, local_rank_mass=sum(r * z for r, z in H.items()))
    assert n == (24 if a.control_g44 else 0), ('regroup count', n)
    dump(out / 'regroup/FULL-WORD.json.gz', w)
    # 4. HPE: PR635's candidates, greedy with disjoint registers
    h = load('upstream_hpe', up / 'code/build_hpe.py')
    used, ch = set(), []
    for c in h.candidates(w):
        rs = set(h.regs(w['cleanup'][c['cleanup_index']]))
        if rs & used: continue
        used |= rs; ch.append(c)
    assert len(ch) == (34 if a.control_g44 else 46), ('hpe count', len(ch))
    (out / 'HPE-RECIPE.json').write_text(json.dumps(dict(changes=ch)))
    w = h.apply(w, ch); dump(out / 'hpe/FULL-WORD.json.gz', w)
    # 5. cold44 (generalised): helpers outside the 224+16b ranges join their blocks
    hm = set(read(raw / 'HELPER-MAP.json')['map'].values())
    env['EXTRAH'] = json.dumps(sorted(set(range(224, 224 + w['report']['R'])) - hm))
    ranks = [2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 2, 2, 2] if a.control_g44 else [4] * 14
    env['PAIRING_RANKS'] = json.dumps(ranks)   # cold44x asserts every block's pairing rank
    run('cold44', HERE / 'cold44x.py', '--input', out / 'hpe/FULL-WORD.json.gz', '--out', out / 'cold44',
        '--hamming', wd / 'hamming', '--upstream-package', up)
    assert [b['pairing_rank'] for b in read(out / 'cold44/CONSTRUCTION.json')['blocks']] == ranks, 'pairing ranks'
    word = out / 'cold44/FULL-WORD.json.gz'; w = read(word)
    got = hashlib.sha256(enc(w)).hexdigest()
    assert got == (G44_SHA if a.control_g44 else NOTRI_SHA), ('word', got)
    rep = w['report']
    if a.control_g44:
        print('PASS control: #645 gauge44 word reproduced', got, flush=True); return
    assert rep['R'] == 504 and rep['local_rank_mass'] == 5674
    assert rep['local_profile'] == {'1': 2506, '2': 336, '3': 472, '4': 184, '5': 56, '8': 8}, rep['local_profile']
    assert rep['width_inventory'] == {'4': 64, '5': 48, '7': 46, '8': 114, '9': 232}, rep['width_inventory']
    print('PASS no-triangle scalar word', got, flush=True)
    if a.word_only:
        return
    # 6. native locals (PR635, as in reproduce.py)
    for k in ('XPARAM', 'EXTRAH', 'PAIRING_RANKS'): env.pop(k, None)
    local = out / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', word,
        '--routing', parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz', '--out', local)
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
