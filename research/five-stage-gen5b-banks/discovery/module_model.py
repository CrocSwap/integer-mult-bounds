"""Module-instance model: replica of compile_word arc feasibility restricted to one module instance.
Instance data: input covers (24-bit masks), output preann subspaces (rows). Circuit: {input_count, args, roots}.
preann[x] = join of out_preann[k] over outputs k reachable from x; initial = join(preann, pad(uncovered coords));
order by (h - dim initial, creation id); arcs: donor x -> use of an operand y at a later op t with initial[t] in initial[x]."""
import sys, pickle
from collections import defaultdict
from local_model import Table, P

class Instance:
    def __init__(self, inst, h):
        self.h = h; self.T = Table(h)
        self.in_cover = inst['in_cover']
        self.coord = [self.T.intern([[1 if k == j else 0 for k in range(h)]]) for j in range(h)]
        self.out_preann = [self.T.intern(list(rows)) for rows in inst['out_preann']]
        self.pad_cache = {}
        self.key = inst['key']
    def pad(self, cov):
        if cov not in self.pad_cache:
            self.pad_cache[cov] = self.T.join_many(self.coord[j] for j in range(self.h) if not cov >> j & 1)
        return self.pad_cache[cov]
    def evaluate(self, circ, want=False, check_roots=True):
        nin = circ['input_count']; args = circ['args']; roots = circ['roots']
        N = len(args); h = self.h
        sup = [1 << i for i in range(nin)]; cov = list(self.in_cover)
        for x in range(nin, N):
            a, b = args[x]; assert not sup[a] & sup[b], 'disjoint'; sup.append(sup[a] | sup[b]); cov.append(cov[a] | cov[b])
        # reachable outputs
        users = defaultdict(list)
        for x in range(nin, N):
            for j, y in enumerate(args[x]): users[y].append((x, j))
        outs_of = defaultdict(set)
        for k, r in enumerate(roots): outs_of[r].add(k)
        fed = [set() for _ in range(N)]
        for x in range(N - 1, -1, -1):
            s = set(outs_of.get(x, ()))
            for y, j in users[x]: s |= fed[y]
            fed[x] = s
        active = [x for x in range(N) if fed[x]]
        for x in range(nin, N): assert fed[x], 'unused node %d' % x
        preann = [self.T.join_many(self.out_preann[k] for k in sorted(fed[x])) for x in range(N)]
        initial = [self.T.join(preann[x], self.pad(cov[x])) for x in range(N)]
        ops = [x for x in range(nin, N)]
        order = sorted(ops, key=lambda x: (h - self.T.dim(initial[x]), x))
        pos = {x: i for i, x in enumerate(order)}
        uses = []  # (value, target op, ann)
        for x in order:
            for y in args[x]: uses.append((y, x, initial[x]))
        # root uses of outputs: useann = root ann; a root use could be a target of an arc only if the output is an operand
        # of some op (never: outputs are terminal), so omit.
        byval = defaultdict(list)
        for u, (y, t, ann) in enumerate(uses): byval[y].append(u)
        adj = {}
        for x in ops:
            lst = []
            for y in args[x]:
                for u in byval[y]:
                    yy, t, ann = uses[u]
                    if t == x or pos[t] <= pos[x]: continue
                    if self.T.contained(ann, initial[x]): lst.append(u)
            adj[x] = lst
        mR = {}; mL = {}
        def try_(x, seen):
            for u in adj[x]:
                if u in seen: continue
                seen.add(u)
                if u not in mR or try_(mR[u], seen):
                    mR[u] = x; mL[x] = u; return True
            return False
        for x in ops: try_(x, set())
        adds = len(ops); arcs = len(mL)
        if not want: return adds, arcs, adds - arcs
        return adds, arcs, adds - arcs, dict(initial=initial, preann=preann, order=order, uses=uses, adj=adj, match=mL, sup=sup, fed=fed)

def load(path):
    d = pickle.load(open(path, 'rb'))
    return d, [Instance(i, d['h']) for i in d['qmod']], [Instance(i, d['pair']) if False else Instance(i, d['h']) for i in d['pair']]

if __name__ == '__main__':
    from collections import Counter
    d, qi, pi = load(sys.argv[1])
    import time; t0 = time.time()
    rq = [I.evaluate(d['abo']) for I in qi]
    print('qmod', Counter(rq), '%.1fs' % (time.time() - t0))
    # compare matched arcs with pinned per instance (donor, operand, target) sets - matching may differ; compare counts
    t0 = time.time()
    rp = [pi[k].evaluate(d['mod']) for k in range(len(pi))]
    print('pair', Counter(rp), '%.1fs' % (time.time() - t0))
    # frame dims in qmod instance 0
    a, b, c, det = qi[0].evaluate(d['abo'], want=True)
    T = qi[0].T; nin = 10
    for x in det['order']:
        print(x, 'sup', bin(det['sup'][x])[2:].zfill(10)[::-1], 'fed', sorted(det['fed'][x]), 'framedim', 24 - T.dim(det['initial'][x]), 'preann', T.dim(det['preann'][x]),
              'arc', (det['uses'][det['match'][x]][0], det['uses'][det['match'][x]][1]) if x in det['match'] else None, 'feas', len(det['adj'][x]))
    print('inputs framedim', [24 - T.dim(det['initial'][x]) for x in range(nin)])
