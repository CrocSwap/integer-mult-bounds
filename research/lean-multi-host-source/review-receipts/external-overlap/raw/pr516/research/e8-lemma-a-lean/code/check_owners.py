# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
"""Instance check (O) (PROOF.md §4): one owner per stream in every invocation.

Units are physical streams (family, cover class) (PROOF.md §1; #442 idle-axis hosting, #458 §3, the template's
`route_semantics`).  An invocation at cover class d realizes register r on the stream (fam r, d * sigma_r^-1); by
`LemmaA.streamOwner_injective_of_disjoint` the owner map is injective once registers that share a family have pairwise
disjoint, nonempty footprints on it.  This script reads the emitted hosted template and checks, in every call:
  * data wires (route kind 1) are alone on their family;
  * registers sharing a family have pairwise disjoint nonempty footprints, computed in the family's own coordinates:
      [2, slot]                pure-bank width-9 slot: cells 9*slot .. 9*slot+8
      [2, off, w, spectators]  banked entering helper: cells off .. off+w-1 and its spectator cells
      [3, child, off]          hosted width-9: pending positions off .. off+8 of that idle child
      [4, child, off, w, sp]   hosted entering helper: pending positions off .. off+w-1, spectators as basis indices
    a shared family whose footprints live in different coordinate systems cannot be checked and counts as a violation;
  * no owner lies in the private namespace, and the private centre copies sit in one private slot per centre
    (template `private_namespace`), disjoint from the reserved tableau and coefficient slots;
  * the template runs each local invocation to completion before the next (`loop_order`): no other actor in a call.
It reports the calls with one register per family and the calls that share a family (covered through stream units), and
checks the template against #484's EXPECTED.json where it is pinned.

usage: check_owners.py BASE VARIANT [VARIANT ...] [--mutants]   reads BASE/<variant>/hosted/GLOBAL-TEMPLATE.json.gz and
       BASE/<variant>/split-centres/CANONICAL-WORD.json.gz;   or   check_owners.py --template T.json.gz NCENTRES [--mutants]
Standard library only."""
import gzip, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = json.loads((HERE.parents[1] / 'e8-complex-gauge-kernel' / 'EXPECTED.json').read_text())


def kind(r):
    return str(r[0]) if r[0] != 2 else ('2-slot' if len(r) == 2 else '2-entering')


def footprint(r):
    k = kind(r)
    if k == '2-slot': return 'cell', {9 * r[1] + x for x in range(9)}
    if k == '2-entering': return 'cell', set(range(r[1], r[1] + r[2])) | set(r[3])
    if k == '3': return ('pend', r[1]), set(range(r[2], r[2] + 9))
    if k == '4': return ('pend+B', r[1]), {('p', x) for x in range(r[2], r[2] + r[3])} | {('B', x) for x in r[4]}
    return 'data', set()


def check_template(t, ncent):
    live = t['live']; bad = []; kinds = Counter(); calls = 0; single = 0; shared_calls = 0; shared_regs = 0
    if 'each local invocation completes before the next' not in t['loop_order'].lower(): bad.append('loop_order: invocations not atomic')
    for c in t['calls']:
        own = c['owners']; calls += 1; tag = f"call stage {c['stage']} replica {c['replica']}"
        kinds.update(kind(r) for _, r in own)
        if any(f >= live for f, _ in own): bad.append(f'{tag}: owner in the private namespace')
        groups = defaultdict(list)
        for f, r in own: groups[f].append(r)
        shared = {f: rs for f, rs in groups.items() if len(rs) > 1}
        if not shared: single += 1; continue
        shared_calls += 1
        for f, rs in shared.items():
            shared_regs += len(rs)
            fps = [footprint(r) for r in rs]
            if any(sys_ == 'data' for sys_, _ in fps): bad.append(f'{tag}: a data wire shares family {f}'); continue
            if len({sys_ for sys_, _ in fps}) != 1 or fps[0][0][0] == 'pend+B': bad.append(f'{tag}: family {f} footprints in mixed coordinates'); continue
            seen = set()
            for _, fp in fps:
                if not fp or fp & seen: bad.append(f'{tag}: footprints overlap on family {f}'); break
                seen |= fp
    pn = t['private_namespace']; a, b = pn['centers']
    others = [tuple(pn[k]) for k in pn if k != 'centers']
    if b - a != ncent or a < live or any(not (b <= x0 or x1 <= a) for x0, x1 in others):
        bad.append(f'centre copies: private slots {pn["centers"]} for {ncent} centres, live {live}, others {others}')
    return dict(calls=calls, one_register_per_family=single, sharing_calls=shared_calls, sharing_registers=shared_regs,
                kinds=dict(sorted(kinds.items()))), bad


def main():
    args = [a for a in sys.argv[1:] if a != '--mutants']; ok = True
    if args[0] == '--template':
        raw = Path(args[1]).read_bytes(); jobs = [(args[1], raw, int(args[2]), None)]
    else:
        base = Path(args[0]); jobs = []
        for name in args[1:]:
            raw = (base / name / 'hosted' / 'GLOBAL-TEMPLATE.json.gz').read_bytes()
            ncent = len(json.loads(gzip.decompress((base / name / 'split-centres' / 'CANONICAL-WORD.json.gz').read_bytes()))['center_frames'])
            jobs.append((name, raw, ncent, EXPECTED['words'].get(name, {}).get('hosted_template_sha256')))
    for name, raw, ncent, exp in jobs:
        t = json.loads(gzip.decompress(raw))
        info, bad = check_template(t, ncent)
        if exp is not None and exp not in (hashlib.sha256(raw).hexdigest(), hashlib.sha256(gzip.decompress(raw)).hexdigest()):
            bad.append('hosted template differs from #484 EXPECTED.json')
        ok &= not bad
        print(f"{name}: calls {info['calls']}; one register per family {info['one_register_per_family']}/{info['calls']}; "
              f"sharing a family with disjoint footprints (stream units) {info['sharing_calls']}/{info['calls']} "
              f"({info['sharing_registers']} registers); centre copies {ncent} in private slots; "
              f"{'pinned to EXPECTED' if exp else 'no EXPECTED pin'}; route kinds {info['kinds']}; violations {len(bad)} {bad[:3]}", flush=True)
        if '--mutants' in sys.argv:
            import copy
            mu = {}
            m = copy.deepcopy(t)                            # a helper moved onto an active data wire's family
            c = m['calls'][0]; c['owners'][-1][0] = c['owners'][0][0]; mu['helper on a data wire family'] = len(check_template(m, ncent)[1])
            m = copy.deepcopy(t); hit = False               # two registers on one family with overlapping footprints
            for c in m['calls']:
                fams = defaultdict(list)
                for o in c['owners']: fams[o[0]].append(o)
                for f, os_ in fams.items():
                    if len(os_) > 1 and not hit: os_[1][1] = list(os_[0][1]); hit = True
                if not hit:
                    hs = [o for o in c['owners'] if o[1][0] in (2, 3, 4)]
                    if len(hs) > 1: hs[1][0] = hs[0][0]; hs[1][1] = list(hs[0][1]); hit = True
            mu['two registers with the same footprint on one family'] = len(check_template(m, ncent)[1])
            m = copy.deepcopy(t); m['private_namespace']['centers'] = [m['private_namespace']['centers'][0], m['private_namespace']['centers'][1] - 1]
            mu['a centre copy without its private slot'] = len(check_template(m, ncent)[1])
            ok &= all(v > 0 for v in mu.values()); print('  mutants (violations each):', mu, flush=True)
    print('PASS one owner per stream' if ok else 'FAIL owner check')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
