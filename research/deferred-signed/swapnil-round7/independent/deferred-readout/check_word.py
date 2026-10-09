"""Round-seven check, part 1 (stdlib only): the reordered stage-1 word, as scalars. No frames are used here.

From certificates/round7/{witness,deferred}_23.json.gz:
 A. side DAG from the definitions (disjoint additions, out(c,T) = {S : S cap T = {c}}, retained(c) = star(c));
    the schedule computes it: replaying the ops symbolically, every addition reads its two operands from the two slots
    it names, a linked operand stays on the non-pivot slot, every addition runs once, the node lists of every slot
    follow the replay, copies start where their source is, and every output / retained slot ends holding its node;
 B. garbage coefficients of every slot (the transpose sweep of L applied to the root reads), over Z and over F2;
 C. phase 1 = the ops that must precede the retained-total completions under per-slot sequence precedence; no
    deferred slot is read or written in phase 1, the retained slots complete in phase 1 and are not touched again,
    every V gate precedes its slot's first touch by L; the release rule: deferred readouts in increasing dim sigma_u,
    deferred V gates in increasing dim s_i, each X_S ordered as its early V gates then its deferred V gates;
 D. the stage-1 word of B-defer with V leaves, every event placed in time:
      readouts of the non-deferred slots (at 0), the early V gates, phase 1 of L, the centre copies read every target
      containing their centre, the deferred readouts in order, the deferred V gates, the rest of L, the output reads,
      L^-1, V^-1;
    replayed with arbitrary scratch and data over F2 and over Z (exact integer readout coefficients): every slot is
    restored and every target receives its definition sum (over F2 exactly x_T); negative controls must break it.
Usage: python3 check_word.py [h]"""
import sys, os, random, time
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deferred as dr

T0 = time.time()
def log(*a): print('[%5.0fs]' % (time.time() - T0), *a, flush=True)
OK = {}
def report(name, ok):
    OK[name] = bool(ok); log('%-100s %s' % (name, 'PASS' if ok else 'FAIL'))


def main(h=23):
    W, D = dr.load(h); S = dr.Schedule(W, D)
    trip, v, R, tid, ops, args = S.trip, S.v, S.R, S.tid, S.ops, S.args
    act = sorted(args)
    # ------------------------------------------------------------------ A. DAG and schedule semantics
    star = [sum(1 << i for i, T in enumerate(trip) if q in T) for q in range(h)]
    sup = {}; okA = True
    for n in act:
        if args[n] is None: okA &= 1 <= n <= v and tuple(W['leaf'][str(n)]) == trip[n - 1]; sup[n] = 1 << (n - 1)
        else:
            a, b = args[n]; okA &= a < n and b < n and not (sup[a] & sup[b]); sup[n] = sup[a] | sup[b]
    outputs = {(c, tuple(T)): n for c, T, n in W['outputs']}; retained = {c: n for c, n in W['retained']}
    for (c, T), n in outputs.items():
        A_, B_ = [q for q in T if q != c]
        okA &= c in T and sup[n] == star[c] & ~star[A_] & ~star[B_]
    okA &= len(outputs) == 3 * v and sorted(retained) == list(range(h)) and all(sup[n] == star[c] for c, n in retained.items())
    report('A. disjoint additions; out(c,T) = {S: S cap T = {c}}; retained(c) = star(c) (%d outputs, %d totals)' % (
        len(outputs), len(retained)), okA)
    mL = {x: (y, k) for x, y, k in W['links']}
    val = {}; pos = [0] * R; seen = set(); okS = True; started = set()
    for op in ops:
        if op[0] == 'src':
            s, n = op[1], op[2]; okS &= s not in started and args[n] is None and S.hold[s][0] == n
            val[s] = n; started.add(s)
        elif op[0] == 'fan':
            p = op[1]; okS &= p in started
            for g in op[2]:
                okS &= g not in started and S.hold[g][0] == val[p] and S.start[g][0] == 'fresh' and S.start[g][1] == val[p]
                val[g] = val[p]; started.add(g)
        else:
            _, p, o, n = op; okS &= n not in seen and args[n] is not None and p in started and o in started; seen.add(n)
            okS &= (val[p], val[o]) in (args[n], args[n][::-1])
            if n in mL: okS &= mL[n][0] == val[o]                     # the linked operand stays on the non-pivot
            for s_ in (p, o):                                          # both wires pass the gate of n
                okS &= pos[s_] + 1 < len(S.hold[s_]) and S.hold[s_][pos[s_] + 1] == n; pos[s_] += 1
            val[p] = n
    okS &= seen == {n for n in act if args[n] is not None} and len(started) == R
    okS &= all(pos[s] == len(S.hold[s]) - 1 for s in range(R))
    okS &= all(val[s] == outputs[cT] for s, cT in S.out.items()) and all(val[s] == retained[c] for s, c in S.ret.items())
    okS &= sorted(S.out.values()) == sorted(outputs) and sorted(S.ret.values()) == list(range(h))
    okS &= R == len(seen) + len(outputs) + len(retained) - len(mL)
    report('A. schedule computes the DAG: %d ops, R = adds + outputs + totals - links = %d, node lists follow the replay' % (
        len(ops), R), okS)

    # ------------------------------------------------------------------ B. coefficients
    CZ = S.adjoint(); CF = [{t: 1 for t, x in d.items() if x % 2} for d in CZ]
    report('B. garbage coefficients by the transpose sweep: %d nonzero over Z, %d odd' % (
        sum(len(d) for d in CZ), sum(len(d) for d in CF)), all(x > 0 for d in CZ for x in d.values()))

    # ------------------------------------------------------------------ C. phase 1 and the release rule
    prev = {}; pred = defaultdict(list); first = {}; last = {}
    for i, op in enumerate(ops):
        for s in S.touch(op):
            if s in prev: pred[i].append(prev[s])
            prev[s] = i; first.setdefault(s, i); last[s] = i
    Anc = set(); st = [last[s] for s in S.ret]
    while st:
        i = st.pop()
        if i in Anc: continue
        Anc.add(i); st.extend(pred[i])
    sel = S.sel; srcop = S.srcop
    srcidx = {o[1]: i for i, o in enumerate(ops) if o[0] == 'src'}
    okC = not any(set(S.touch(ops[i])) & sel for i in Anc)
    okC &= all(last[s] in Anc for s in S.ret)
    okC &= all(s not in first or srcidx[s] < first[s] for s in srcop)
    report('C. deferred slots (%d, %d of them V leaves) untouched by phase 1 (%d of %d ops); totals complete in phase 1' % (
        len(sel), len(sel & set(srcop)), len(Anc), len(ops)), okC)
    dimv = {s: len(B) for s, B in S.vstart.items()}
    late_V = [s for s in S.late_v]; early = set(srcop) - sel
    okR = S.readout == sorted(sel, key=lambda s: (S.f[s], s)) and all(S.f[s] > 0 for s in sel)
    okR &= set(late_V) == sel & set(srcop) and late_V == sorted(late_V, key=lambda s: (dimv[s], s))
    posl = {s: i for i, s in enumerate(late_V)}; okX = True; leaves = defaultdict(list)
    for s, n in srcop.items(): leaves[n].append(s)
    okX &= sorted(n for n, _ in S.xs) == sorted(leaves)
    for n, us in S.xs:
        e = sorted((s for s in leaves[n] if s in early), key=lambda s: (dimv[s], s))
        l = sorted((s for s in leaves[n] if s in sel), key=lambda s: posl[s])
        okX &= us == e + l
    report('C. release rule: readouts by dim sigma_u, deferred V gates by dim s_i, X_S = early then deferred V gates', okR and okX)

    # ------------------------------------------------------------------ D. the word
    ph1 = [i for i in range(len(ops)) if i in Anc and ops[i][0] != 'src']
    rest = [i for i in range(len(ops)) if i not in Anc and ops[i][0] != 'src']
    early_V = sorted(early, key=lambda s: (srcop[s], dimv[s], s))
    def expected(x):
        want = [0] * v
        for (c, T), n in outputs.items():
            A_, B_ = [q for q in T if q != c]
            want[tid[T]] += sum(x[i] for i, Sx in enumerate(trip) if c in Sx and A_ not in Sx and B_ not in Sx)
        for c in range(h):
            tot = sum(x[i] for i, Sx in enumerate(trip) if c in Sx)
            for t, T in enumerate(trip):
                if c in T: want[t] += tot
        return want
    selist = S.readout
    def word(ring, rng, ctl=None):
        mod = (lambda z: z & 1) if ring == 2 else (lambda z: z)
        co = CF if ring == 2 or ctl == 'f2coef_in_Z' else CZ
        x = [rng.randrange(-10**6, 10**6) for _ in range(v)]
        a0 = [rng.randrange(-10**6, 10**6) for _ in range(R)]; y0 = [rng.randrange(-10**6, 10**6) for _ in range(v)]
        a = list(a0); y = list(y0)
        drop = selist[len(selist) // 2] if ctl == 'drop' else None
        def readout(s):
            for t, c in co[s].items():
                if s == drop and t == min(co[s]): continue
                y[t] -= c * a[s]
        def runop(i):
            op = ops[i]
            if op[0] == 'add': a[op[1]] += a[op[2]]
            elif op[0] == 'fan':
                for g in op[2]: a[g] += a[op[1]]
        late_slot = early_slot = None
        if ctl == 'late_readout':            # one deferred slot reads out right after its first modifying touch
            late_slot = next(s for s in selist if ops[first[s]][0] == 'fan' and s in ops[first[s]][2] or
                             ops[first[s]][0] == 'add' and ops[first[s]][1] == s)
        if ctl == 'phase1_slot':             # a slot modified in phase 1 treated as deferred
            early_slot = next(s for s in range(R) if s not in sel and s not in srcop and any(
                (ops[i][0] == 'add' and ops[i][1] == s) or (ops[i][0] == 'fan' and s in ops[i][2]) for i in ph1))
        for s in range(R):
            if s not in sel and s != early_slot: readout(s)
        for s in early_V: a[s] += x[srcop[s] - 1]
        if ctl == 'V_before_readout': a[late_V[0]] += x[srcop[late_V[0]] - 1]
        done = []
        for i in ph1: runop(i); done.append(i)
        for s, c in S.ret.items():                    # centre copies: the totals are complete; read every T with c in T
            for t, T in enumerate(trip):
                if c in T: y[t] += a[s]
        if early_slot is not None: readout(early_slot)
        for s in selist:
            if s != late_slot: readout(s)
        for s in late_V:
            if not (ctl == 'V_before_readout' and s == late_V[0]): a[s] += x[srcop[s] - 1]
        for i in rest:
            runop(i); done.append(i)
            if late_slot is not None and i == first[late_slot]: readout(late_slot)
        for s, (c, T) in S.out.items(): y[tid[T]] += a[s]
        for i in reversed(done):
            op = ops[i]
            if op[0] == 'add': a[op[1]] -= a[op[2]]
            elif op[0] == 'fan':
                for g in op[2]: a[g] -= a[op[1]]
        for s, n in srcop.items(): a[s] -= x[n - 1]
        if any(mod(p - q) for p, q in zip(a, a0)): return False
        want = expected(x)
        if any(mod(y[t] - y0[t] - want[t]) for t in range(v)): return False
        if ring == 2 and any(mod(y[t] - y0[t] - x[t]) for t in range(v)): return False
        return True
    rng = random.Random(20261009)
    report('D. scalar identity over F2 (3 random scratch/data): scratch restored, y_T += x_T and == definition sums',
           all(word(2, rng) for _ in range(3)))
    report('D. scalar identity over Z, exact integer readout coefficients', word(0, rng))
    for ctl in ('drop', 'late_readout', 'V_before_readout', 'phase1_slot'):
        # one F2 trial can miss a fault whose error term is even, so 8 trials (any failure = broken)
        report('D. NEG control %-18s breaks the identity (F2, 8 trials; and Z)' % ctl,
               not all(word(2, rng, ctl) for _ in range(8)) and not word(0, rng, ctl))
    report('D. NEG control F2 coefficients used over Z break the Z identity', not word(0, rng, 'f2coef_in_Z'))
    log('ALL %s' % ('PASS' if all(OK.values()) else 'FAIL: ' + str([k for k, x in OK.items() if not x])))
    return all(OK.values())


if __name__ == '__main__':
    sys.exit(0 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 23) else 1)
