#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cross-check of this package's stdlib bound (restore_bound.py) against lane K's CURRENT bound.py / lbforced.py
(the r12 BORROW-WORD harness bp.py on the #1186 frame toolkit; numpy). Not part of the registered replay: it needs lane
K's working tree. Usage: crosscheck_lanek.py LANE_K_CODE_DIR PACKAGE_DIR OUT.json. Marius-Paul Dumitrean, with
substantial AI assistance (Claude Code)."""
import gzip, hashlib, json, sys
from fractions import Fraction as Q
from pathlib import Path
lane, pkg, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(lane))
import bound as KB                      # lane K, current
import lbforced as KL
sys.path.insert(0, str(pkg))
import frames_exact as FX, restore_bound as RB
rows_out = []
for name in ('3042-base', '3042-extra', '2979-base', '2979-extra'):
    w = json.loads(gzip.decompress((pkg / ('data/WORD-%s.json.gz' % name)).read_bytes()))
    for variant in ('word', 'emptied-restore'):
        x = dict(w)
        if variant == 'emptied-restore':
            x['restore'] = []
        rows = RB.entry_rows(x)
        Mc, rk = RB.coordinates(rows, {c: {(c, ()): Q(1)} for c in RB.restored(x)})
        M = {q: {q: Q(1)} for q in RB.live_registers(x)}
        M.update({c: dict(v) for c, v in Mc.items()})
        kb = KB.bound(x, M=M)
        kl = KL.lb_forced(x, M=M)
        pb = RB.bound(x)
        rec = dict(word=name, variant=variant, laneK_bound=kb['bound'], laneK_LB_forced=kb['LB_forced'], laneK_lb_forced_direct=kl['cost'],
                   laneK_caps=kl['ncaps'], laneK_blocked=[kb['n_blocked'], kb['extras_blocked']], laneK_open=[kb['n_open_forced'], kb['extras_open']],
                   package_bound=pb['bound'], package_LB_forced=pb['LB_forced'], package_caps=pb['forced_caps'],
                   package_blocked=[pb['blocked'], pb['extras_blocked']], package_groups=[pb['groups'], pb['extras_open']])
        rec['agree'] = (rec['laneK_bound'] == rec['package_bound'] and rec['laneK_LB_forced'] == rec['package_LB_forced'] == rec['laneK_lb_forced_direct']
                        and rec['laneK_caps'] == rec['package_caps'])
        rows_out.append(rec)
        print(rec, flush=True)
assert all(r['agree'] for r in rows_out)
res = dict(status='PASS_LANEK_CROSSCHECK', laneK_files={f: hashlib.sha256((lane / f).read_bytes()).hexdigest() for f in ('bound.py', 'lbforced.py')},
           rows=rows_out)
out.write_text(json.dumps(res, indent=1, sort_keys=True) + '\n')
print('PASS_LANEK_CROSSCHECK', len(rows_out))
