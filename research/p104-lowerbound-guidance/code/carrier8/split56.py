"""CARRIER8 split56.py: CARRIER-SPLIT of the asc56 U run (halvpay/f56run_nomix.pkl, our own FANOUT56 data).
Each owned lifetime O (cold intakes, then one climb to its 8-dim output span B_O, then outputs) is cut right after its
last intake into  cleaner O + public carrier HC_k + hot taker T:
   HC += O (HC at {0});  HC climbs to K (dim k, C_a <= K <= B_O);  INIT T at K;  T += HC  (hot pickup h + c);
   O climbs to K;  HC -= O  (clean);  T -= HC  (drops the token: T = c);  CLEAR O;  T replays O's remaining ops at charts D + K.
Expected: pinned, R = 56 for every k, own-price collapses (O: w = 0, T: c = 0), level cut still 56 (Lemma A, rendezvous form)."""
import pickle, sys, time; sys.path.insert(0, '.')
from pa import *

def split(prog, init, k, rng_pick=0):
    init = dict(init); out = []
    life = {}; cur = {}
    for i, op in enumerate(prog):
        if op[0] == 'INIT': cur[op[1]] = len(life); life[len(life)] = dict(reg=op[1], i0=i, ins=[], outs=[], charts=[op[2]])
        elif op[0] == 'CLEAR': life[cur[op[1]]]['i1'] = i; del cur[op[1]]
        elif op[0] == 'MOVE' and op[1] in cur: life[cur[op[1]]]['charts'].append(op[2])
        elif op[0] == 'ADD':
            if op[1] in cur: life[cur[op[1]]]['ins'].append(i)
            if op[3] in cur: life[cur[op[3]]]['outs'].append(i)
    plan = {}
    for li, lf in life.items():
        assert max(lf['ins']) < min(lf['outs'])     # GTD
        Bo = frozenset([0])
        for C in lf['charts']: Bo = join(Bo, C)
        # chart at last intake
        plan[max(lf['ins'])] = li; lf['Bo'] = Bo
    # replay to know charts at each step
    ch = {kk: v[0] for kk, v in init.items()}
    ren = {}; Kof = {}
    for i, op in enumerate(prog):
        if op[0] == 'INIT': ch[op[1]] = op[2]
        def R(r): return ren.get(r, r)
        if op[0] == 'MOVE':
            r = op[1]; D = op[2]
            if r in ren: D = join(D, Kof[r]); out.append(('MOVE', ren[r], D)); ch[ren[r]] = D
            else: out.append(op); ch[r] = D
        elif op[0] == 'ADD': out.append(('ADD', R(op[1]), op[2], R(op[3])))
        elif op[0] == 'CLEAR': out.append(('CLEAR', R(op[1])))
        else: out.append(op)
        if i in plan:
            li = plan[i]; lf = life[li]; O = lf['reg']; Ca = ch[O]; Bo = lf['Bo']
            # K: Ca + (k - dim Ca) basis vectors of Bo
            K = Ca; B = basis(Bo)
            for v in sorted(B):
                if fdim(K) >= k: break
                if v not in K: K = join(K, span([v]))
            H = ('HC', li); init[H] = (frozenset([0]), {('h', 'c', li): 1}); ch[H] = frozenset([0])
            T = ('T', li)
            out += [('ADD', H, 1, O), ('MOVE', H, K), ('INIT', T, K), ('ADD', T, 1, H)]
            if K != Ca: out.append(('MOVE', O, K))
            out += [('ADD', H, -1, O), ('ADD', T, -1, H), ('CLEAR', O)]
            ren[O] = T; Kof[O] = K; ch[T] = K
        if op[0] == 'CLEAR' and op[1] in ren:
            del ren[op[1]]
    # drop the original CLEAR of O (already cleared): the renamed CLEAR clears T
    return out, init

d = pickle.load(open('../halvpay/f56run_nomix.pkl', 'rb')); prog, init, P = d['prog'], d['init'], d['P']
F = Fld(0)
for k in [int(a) for a in sys.argv[1:]] or [1, 2, 4, 6, 8]:
    t0 = time.time()
    ops, ini = split(prog, init, k)
    r = analyze(ops, ini, P, F, ports=range(96))
    EP = r['EP']; live = [ep for ep in EP if ep['C'] is not None and ep['Ap'] is not None]
    src = [ep for ep in live if ep['c']]; snk = [ep for ep in live if ep['w']]
    Wr = [{t: v for t, v in ep['w'].items() if t < 96} for ep in live]; Cr = [{s: v for s, v in ep['C'].items() if s < 96} for ep in live]
    print('k', k, '| bad', len(r['bad']), 'pinned', r['pinned'][:3], 'R', r['R'], 'own-price', r['own'], 'drops', r['drops'],
          'acyclic', r['acyclic'], 'LS', r.get('LS'), {a: b for a, b in r['chk'].items() if b})
    print('   epochs', len(live), 'sources', len(src), 'sinks', len(snk), 'both', sum(1 for ep in live if ep['c'] and ep['w']),
          '| (dimA\',dimB,seg,drop,own,#relays):', sorted(set((fdim(ep['Ap']), fdim(ep['B']), ep['seg'], ep['drop'], ep['own'], len(ep['N'])) for ep in live)),
          '| rank W|Q96', rank(F, Wr), 'rank C|Q96', rank(F, Cr), 'src dimA\'<=1', all(fdim(ep['Ap']) <= 1 for ep in src),
          'snk dimB>=8', all(fdim(ep['B']) >= 8 for ep in snk), '%.0fs' % (time.time() - t0))
