"""BIG-RELAY drive.py: frame-level removal of relay frames by shear transport; builds + verifies (fastx projections vs base)."""
import sys, pickle, time, gzip, json
sys.path.insert(0, '../../NETCAUX'); import fastx
from mover import *
W = load(); NP, mains, fixed, dim = setup(W)
X = pickle.load(open('explore.pkl', 'rb'))
def remove_frame(ops, F, stopsF, tl, verbose=False):
    hs = {s[0] for s in stopsF}
    for it in range(200):
        idx = [i for i, (k, e) in enumerate(ops) if evframe(e) == F]
        if not idx: break
        moved = False
        for j in idx:
            e = ops[j][1]
            if e[0] not in ('ADD', 'SCALE'): return None, 'nonadd'
            for d in (-1, 1):
                r = try_move(ops, j, F, tl, d)
                if r is not None:
                    ops = r[0]; moved = True
                    if verbose: print('   moved', e, 'dir', d, 'to', r[1])
                    break
            if moved: break
        if not moved:
            if verbose: print('   stuck on', [ops[j][1] for j in idx])
            return None, 'stuck %d' % len(idx)
    # merge MOVEs a->F->b
    out = []; drop = set()
    for s in stopsF:
        h = s[0]
        i1 = next(i for i, (k, e) in enumerate(ops) if e[0] == 'MOVE' and e[1] == h and e[3] == F)
        i2 = next(i for i, (k, e) in enumerate(ops) if e[0] == 'MOVE' and e[1] == h and e[2] == F)
        a = ops[i1][1][2]; drop.add(i1); e2 = list(ops[i2][1]); e2[2] = a; ops[i2] = (ops[i2][0], e2)
    return [x for i, x in enumerate(ops) if i not in drop], 'ok'
def gainF(F):
    return sum(f(dim[s[4]] - dim[s[3]]) - f(dim[F] - dim[s[3]]) - f(dim[s[4]] - dim[F]) for s in X['stops'][F])
if __name__ == '__main__':
    base_ops = [(float(i), e) for i, e in enumerate(W['program'])]
    tl = timeline(base_ops, NP, W['owned_fields'], W['initial'])
    for F in map(int, sys.argv[1:]):
        t = time.time(); r, why = remove_frame(list(base_ops), F, X['stops'][F], tl, verbose=True)
        print('F', F, why, 'gain %.4f' % gainF(F), '%.1fs' % (time.time() - t))
        if r is None: continue
        W2 = dict(W); W2['program'] = [e for k, e in r]
        R = fastx.proj_matrix(NP, 4, 1); a = fastx.FastReplay(W, R, 4); b = fastx.FastReplay(W2, R, 4)
        print('   replay ok', b.ok, b.bad[:3], 'rows equal', a.proj == b.proj)
