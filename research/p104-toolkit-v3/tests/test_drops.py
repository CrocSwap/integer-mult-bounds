# SPDX-License-Identifier: Apache-2.0
"""tokdrop.py on #7546 (needs numpy): the engine re-finds and rebuilds our #7601 drops byte-for-byte."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ok, check_data, base_word, word_7601, caller_path, KAPPA_7601  # noqa: E402
import accx  # noqa: E402
import modp  # noqa: E402
import tokdrop as T  # noqa: E402

check_data()
print('modp backend:', modp.BACKEND)
B = base_word()
ctx = T.Context(B)
recs = ctx.census()
ok(len(recs) > 3000 and ctx.Z == 3 and ctx.VF == 127, 'census: %d interior public stays on #7546; {0} = frame 3, V = frame 127' % len(recs))
m = {(x['r'], x['f']): x['m'] for x in recs}
ok(abs(m[(134, 595)] - 1.9095425) < 1e-6 and abs(m[(100, 783)] - 1.9095425) < 1e-6,
   'census: stop price m = f(3) - f(1) - f(2) = 1.9095 D0/call for both #7601 stays')

# controls: the two stays of #7601 repair in clean mode with settlement rank 0 (tiers A and B)
for r_, F in ((134, 595), (100, 783)):
    st = ctx.stay(r_, F)
    res = ctx.test_best([st])
    a = ctx.settle_rank(res, 'A'); b = ctx.settle_rank(res, 'B')
    ok(res['ok'] and res['nviol'] == 0 and a[0] == 0 and b[0] == 0 and a[2],
       'scan %d@%d %s: clean repair (K = %d candidates, r1 = r2 = %d), settlement rank A 0 / B 0, pi exact' % (r_, F, st, res['K'], res['r1']))
# negative controls: without correction candidates the same drops are damaging (the repair is what makes them free)
for r_, F in ((134, 595), (100, 783)):
    res = ctx.test([ctx.stay(r_, F)], frames_mode='none')
    ok(not res['ok'] and res['nviol'] > 0, 'scan NEG %d@%d with no correction candidates: not repairable (%d violated rows)' % (r_, F, res['nviol']))

# exact build of both drops = our #7601 word, byte-for-byte
W4, rep = ctx.build_exact([ctx.stay(100, 783), ctx.stay(134, 595)])
W7601 = word_7601(B)
ok(W4 == W7601, 'build: both drops -> exactly the #7601 word (%d events; %d corrections, %d premix ADDs at {0}, %d post-ops)'
   % (len(W4['program']), rep['corrections'], rep['premix'], rep['postops']))
ok(rep['owned_obs_lost'] == 1 and rep['owned_obs_new_only'] == 0 and abs(rep['saved_D0_per_call'] - 3.8190850) < 1e-6,
   'build: stop price 3.8191 D0/call; 1 owned observation removed (134 += -2*owned1503 at 595), none added')
out = []; r = accx.check(B, W4, caller_path(), out=out.append)
ok(r['ok'] and str(r['kappa_new']['lo']).startswith(KAPPA_7601), 'accx: rebuilt word ALL CHECKS PASS, kappa %s' % KAPPA_7601)
print('PASS_TOOLKIT_DROPS')
