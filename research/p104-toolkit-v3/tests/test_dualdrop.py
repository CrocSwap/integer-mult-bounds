# SPDX-License-Identifier: Apache-2.0
"""tokdrop.py on the frame-perp dual (needs numpy): the dual-side scan finds the main-902 drop that the primal engine
cannot see; mapped back it stacks on our #7601 word."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ok, check_data, base_word, word_7601, caller_path, KAPPA_7601  # noqa: E402
import accx  # noqa: E402
import dualword as DW  # noqa: E402
import lossless  # noqa: E402
import tokdrop as T  # noqa: E402

KAPPA_902 = '0.00364932638757719639692487'
check_data()
B = base_word(); W1 = word_7601(B)


def dual_ctx(W):
    D = DW.dual(W)
    Z = [i for i, f in enumerate(D['frames']) if not f][0]; V = [i for i, f in enumerate(D['frames']) if len(f) == 9][0]
    DS = DW.swap_frames(D, Z, V)          # {0} and V trade places under perp; swap back so the engine runs unchanged
    return T.Context(DS), Z, V


ctx, Z, V = dual_ctx(W1)
pi = DW.port_swap(W1)
ok(pi[902] == 794 and (Z, V) == (127, 3), 'dual of #7601: hosted main 902 is register 794 on the dual side; {0}/V frames swapped (3 <-> 127)')
# the primal engine cannot drop 902's stop: 902 is a main whose stop at 595 carries 5 owned writes
pctx = T.Context(W1)
pres = pctx.test_best([pctx.stay(902, 595)])
ok(not pres['ok'], 'primal NEG: dropping 902@595 on #7601 directly has no clean repair (K = %d, violations %d)' % (pres['K'], pres['nviol']))
st = ctx.stay(794, 595)
res = ctx.test_best([st])
a = ctx.settle_rank(res, 'A'); b = ctx.settle_rank(res, 'B')
ok(res['ok'] and res['K'] == 0 and a[0] == 0 and b[0] == 0, 'dual scan 794@595 %s: repaired with K = 0, settlement rank A 0 / B 0' % (st,))
Wd, rep = ctx.build_exact([st])
ok(rep['corrections'] == 0 and rep['premix'] == 0 and rep['owned_obs_lost'] == 1, 'dual build: 0 corrections, 0 premix, 1 owned observation removed')
W5 = DW.restore_copy(DW.dual(DW.swap_frames(Wd, Z, V)), W1)
import collections  # noqa: E402
key = lambda e: json.dumps(e)
dele = list((collections.Counter(map(key, W1['program'])) - collections.Counter(map(key, W5['program']))).elements())
dele = [json.loads(x) for x in dele]
ok(len(W5['program']) == len(W1['program']) - 6 and sum(e[0] == 'ADD' and 902 in (e[1], e[2]) for e in dele) == 5,
   'mapped back: main 902 climbs 3 -> 618 in one MOVE (2 MOVEs -> 1) and its 5 owned ADDs at chart 595 vanish')
out = []; r = accx.check(B, W5, caller_path(), out=out.append)
ok(r['ok'] and r['owned_moves_same'] and str(r['kappa_new']['lo']).startswith(KAPPA_902),
   'accx vs #7546 (strict): ALL CHECKS PASS; #7601 + 902@595 prices kappa %s' % KAPPA_902)
ok(r['kappa_new']['lo'] > r['kappa_base']['hi'], 'pricekit: above #7601 (%s) on the #7113 caller' % KAPPA_7601)
ok(not lossless.dual_scan(W5)[0], 'lossless: 0 lossy CLEARs')
# negative control: a tier-A-only stay on the dual (rank 0 with V-helper rows relaxed) is refused by the exact build
st = ctx.stay(1289, 117)
res = ctx.test_best([st])
a = ctx.settle_rank(res, 'A')[0] if res['ok'] else None
b = ctx.settle_rank(res, 'B')[0] if res['ok'] else None
try:
    ctx.build_exact([st]); built = True
except T.BuildError as ex:
    built = False; why = str(ex)
ok(res['ok'] and a == 0 and b >= 1 and not built, 'build NEG dual 1289@117: settlement rank A 0 / B %s, exact build refused (%s)' % (b, why))
print('PASS_TOOLKIT_DUAL_DROP')
