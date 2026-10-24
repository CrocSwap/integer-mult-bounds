"""Live-role audit of the finite lockstep compiler (DELAYED-COVER-BRIDGE open question 1).

Question: does the finite lockstep compiler of FINITE-PRECOMPILATION.md
(Theorem 1G flow + batch clearing + source complements + exit substitution)
only substitute whole jobs, and give every simultaneously live child role a
distinct physical array?  The delayed BIT cover routes a child role by
x_g -> y_{gS} on the WHOLE cover fiber of its physical array, so two live
roles at the same level on one array would need two different routes on one
fiber.  Nested roles (child role on the array of the parent's issued job) are
fine: the routes compose g -> gS1 -> gS1S2 and are undone in LIFO order.

This script EXECUTES the compiler event by event (not only counts it) and keeps,
for every physical field, the stack of live roles on it.  Each push models one
whole-fiber cover route, each pop its inverse.  Checked at every event:

  I1  units that are live in the same class hold pairwise distinct fields
      (distinct physical arrays for simultaneously live child roles);
  I2  a role entering on an existing field is nested: the top of that field's
      stack is exactly the suspended parent unit that issued this job, with
      equal rank (whole-job substitution); a fresh source enters on a field
      whose top is the enclosing program's expected owner;
  I3  a unit issues a paid job only on a field whose top is itself (it is the
      current physical owner, no descendant still holds it), never while its
      previous child is live (lockstep), and the round's jobs are distinct;
  I4  every pop is LIFO and after a class/program all stacks are exactly back
      to their entry state (every route undone);
  I5  exit batches and complement batches hand B_e pairwise distinct fields to
      the smaller uniform program, each owned by its issuer;
  I6  every top-level array receives its complementary job and its source job
      exactly once, and the per-array leaf count equals the counting compiler.

Negative controls: one owned centre per depth (instead of per unit instance),
an eager parent that issues round j+1 before child class j finishes, and an
exit batch that repeats a field must all be rejected.

Imported by verify.py and test_verify.py.
"""
import gzip, json, random
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from math import factorial, gcd, lcm, prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


class Violation(Exception):
    pass


def need(ok, msg):
    if not ok:
        raise Violation(msg)


# ------------------------------------------------------------------ rules
class Rule:
    def __init__(self, name, roles, rounds, owned=("C0",)):
        self.name, self.roles, self.rounds, self.owned = name, tuple(roles), tuple(rounds), tuple(owned)
        names = [n for n, _ in self.roles]
        assert len(set(names)) == len(names)
        assert all(o in set(names) | set(self.owned) for _, o in self.rounds)
        self.targets = Counter(k for _, k in self.roles)
        self.types = tuple(sorted(self.targets))
        self.W = tuple(self.targets[k] for k in self.types)
        self.m = max(self.types)
        assert max(r for r, _ in self.rounds) < min(self.types), "strict hierarchy"

    def c(self, a):
        return prod(k ** e for k, e in zip(self.types, a))

    def u(self, a):
        return factorial(sum(a)) // prod(factorial(e) for e in a) * prod(w ** e for w, e in zip(self.W, a))

    def lattice(self, n, dil):
        bound = n // (self.m * dil)
        out = []

        def rec(i, a, val):
            if i == len(self.types):
                out.append(tuple(a))
                return
            e = 0
            while val <= bound:
                rec(i + 1, a + [e], val)
                e += 1
                val *= self.types[i]
        if bound:
            rec(0, [], 1)
        return out


# ------------------------------------------------------------------ executor
class Compiler:
    """Counting pass (widths, source order) and event-level execution."""

    def __init__(self, rule, owned_policy="unit", eager=False, bad_exit=False, budget=3_000_000):
        self.R = rule
        self.policy, self.eager, self.bad_exit = owned_policy, eager, bad_exit
        self.budget = budget
        self.stack = defaultdict(list)       # field -> list of entries (guid, role)
        self.guid = 0
        self.fresh = 0
        self.events = 0
        self.stats = Counter()
        self.received = Counter()            # top-level field -> number of full-rank completions
        self.max_live_depth = 0
        self.partial = False

    # ---------------- counting
    @lru_cache(None)
    def plan(self, n):
        """Ordered source ranks of one tree copy and ordered exit batches (rank, t)."""
        R = self.R
        pts = R.lattice(n, 1)
        G = max(map(sum, pts))
        sources, exits, units = [], [], [0]

        def cls(d, dil, incoming):
            us = [(a, dil * R.c(a)) for a in R.lattice(n, dil) if sum(a) == G - d for _ in range(R.u(a))]
            units[0] += len(us)
            demand = defaultdict(int)
            for a, col in us:
                for _, k in R.roles:
                    i = R.types.index(k)
                    demand[tuple(x + (j == i) for j, x in enumerate(a))] += 1
            supply = Counter(p for p, _ in incoming)
            assert set(supply) <= set(demand) and all(supply[p] <= demand[p] for p in supply)
            # same deterministic slot order as execution
            used = Counter()
            for a, col in us:
                for _, k in R.roles:
                    i = R.types.index(k)
                    p = tuple(x + (j == i) for j, x in enumerate(a))
                    if used[p] < supply[p]:
                        used[p] += 1
                    else:
                        sources.append(k * col)
            for j, (r, _) in enumerate(R.rounds):
                out = [(a, r * col) for a, col in us]
                if d < G:
                    cls(d + 1, dil * r, out)
                else:
                    ranks = {rk for _, rk in out}
                    assert len(ranks) == 1
                    exits.append((ranks.pop(), len(out)))
        cls(0, 1, [])
        return tuple(sources), tuple(exits), units[0], G

    @lru_cache(None)
    def compile(self, n):
        """(width B_n, replication a, leaves P_n, roles_executed) ; base: ordinary rank-one program."""
        if n < self.R.m:
            return (1, 1, n, 0)
        sources, exits, units, G = self.plan(n)
        S = len(sources)
        a = 1
        for e, t in exits:
            B = self.compile(e)[0]
            a = lcm(a, B // gcd(B, t))
        for s, cnt in Counter(sources).items():
            if n - s:
                B = self.compile(n - s)[0]
                a = lcm(a, B // gcd(B, cnt))
        width = a * S
        leaves = Fraction(0)
        cost = a * units * len(self.R.roles)
        for e, t in exits:
            B, _, P, c = self.compile(e)
            leaves += Fraction(a * t * P, B)
            cost += a * t // B * c
        for s in sources:
            if n - s:
                B, _, P, c = self.compile(n - s)
                leaves += Fraction(a * P, B)
        for s, cnt in Counter(sources).items():
            if n - s:
                B, _, P, c = self.compile(n - s)
                cost += a * cnt // B * c
        assert leaves.denominator == 1
        return (width, a, leaves.numerator, cost)

    # ---------------- execution helpers
    def new_field(self, tag):
        self.fresh += 1
        return (tag, self.fresh)

    def push(self, f, entry, expect_top):
        st = self.stack[f]
        top = st[-1] if st else None
        need(top == expect_top, f"I2 nesting: field {f} top {top} != expected {expect_top}")
        st.append(entry)
        self.max_live_depth = max(self.max_live_depth, len(st))
        self.events += 1

    def pop(self, f, entry):
        st = self.stack[f]
        need(st and st[-1] == entry, f"I4 LIFO: field {f} top {st[-1] if st else None} != {entry}")
        st.pop()
        self.events += 1

    # ---------------- execution
    def blackbox(self, n, fields, tops):
        """Interface check of a smaller compiled program that is not executed in full:
        it receives distinct fields, each owned by its issuer, and (being itself a
        compiled program, audited by induction) returns them with routes undone."""
        need(len(set(fields)) == len(fields), "I5 distinct fields handed to a smaller program")
        for f, t in zip(fields, tops):
            st = self.stack[f]
            need((st[-1] if st else None) == t, "I5 handed field is owned by its issuer")
        g = ("sub", self.next_guid())
        for f, t in zip(fields, tops):
            self.push(f, g, t)
        for f in fields:
            self.pop(f, g)
        self.stats["interface_checked_subprogram_fields"] += len(fields)

    def sub(self, n, fields, tops):
        """Hand a batch to the rank-n compiled program (full execution when it is a complete,
        small batch; otherwise interface check)."""
        if n < self.R.m:
            self.blackbox(n, fields, tops)
            self.stats["base_rank_lt_m_fields"] += len(fields)
            return
        B, a, P, cost = self.compile(n)
        if len(fields) == B and cost <= self.budget and not self.partial:
            self.uniform(n, fields, tops)
        else:
            self.blackbox(n, fields, tops)

    def uniform(self, n, fields, tops, top_level=False, copies=None):
        """Run the compiled rank-n program on its arrays (all B_n of them, or `copies`
        of the a lockstep tree copies when the full width is astronomically large).
        tops[i] is the entry currently owning fields[i] (None for fresh top-level arrays)."""
        B, a, P, cost = self.compile(n)
        sources, exits, units, G = self.plan(n)
        S = len(sources)
        if copies is not None and copies < a:
            a = copies
            self.partial = True
        need(len(fields) == a * S, "I5 width")
        need(len(set(fields)) == len(fields), "I5 distinct fields handed to a program")
        for f, t in zip(fields, tops):
            st = self.stack[f]
            need((st[-1] if st else None) == t, "I5 handed field is owned by its issuer")
        self.stats["executed_programs"] += 1
        snapshot = {f: list(self.stack[f]) for f in fields}
        prog = ("prog", self.next_guid())
        for f, t in zip(fields, tops):
            self.push(f, prog, t)
        # source complements (complete the N-s other coordinates first)
        by_rank = defaultdict(list)
        for c in range(a):
            for i, s in enumerate(sources):
                by_rank[s].append(fields[c * S + i])
        for s in sorted(by_rank):
            grp = by_rank[s]
            if top_level:
                for f in grp:
                    self.received[f] += 1        # complement (empty when s = n)
            if n - s:
                Bc = self.compile(n - s)[0]
                if self.partial:
                    self.sub(n - s, grp, [prog] * len(grp))
                else:
                    need(len(grp) % Bc == 0, "complement batch integral")
                    for i in range(0, len(grp), Bc):
                        self.sub(n - s, grp[i:i + Bc], [prog] * Bc)
        if top_level:
            self.top_prog = prog
        frame = (fields, S, prog, [0] * a)
        self.run_class(frame, n, a, G, 0, 1, None, iter(exits))
        need(all(p == S for p in frame[3]), "every source slot used exactly once")
        for f in fields:
            self.pop(f, prog)
        need(all(self.stack[f] == snapshot[f] for f in fields), "I4 program restores all stacks")

    def next_guid(self):
        self.guid += 1
        return self.guid

    def run_class(self, frame, n, a, G, d, dil, incoming, exits_iter):
        R = self.R
        fields, S, prog, ptr = frame
        units = []      # (copy, guid, point, column, {role: field}, owned {name: field})
        for c in range(a):
            for pt in R.lattice(n, dil):
                if sum(pt) != G - d:
                    continue
                for _ in range(R.u(pt)):
                    units.append([c, self.next_guid(), pt, dil * R.c(pt), {}, {}, None])
        # match incoming jobs (per copy, per point) to role slots in deterministic order
        supply = defaultdict(list)
        if incoming:
            for job in incoming:
                supply[(job["copy"], job["point"])].append(job)
        used = Counter()
        live = []
        for U in units:
            c, g, pt, col, fmap, omap, _ = U
            for name, k in R.roles:
                i = R.types.index(k)
                p = tuple(x + (j == i) for j, x in enumerate(pt))
                lst = supply.get((c, p), [])
                if used[(c, p)] < len(lst):
                    job = lst[used[(c, p)]]
                    used[(c, p)] += 1
                    need(job["rank"] == k * col, "I2 whole job: child role rank == parent job rank")
                    self.push(job["field"], (g, name), job["issuer"])
                    fmap[name] = job["field"]
                    self.stats["nested_role_entries"] += 1
                else:
                    f = fields[c * S + ptr[c]]
                    ptr[c] += 1
                    need(n < R.m * k * col <= R.m * n, "source band")
                    self.push(f, (g, name), prog)
                    if prog == getattr(self, "top_prog", None):
                        self.received[f] += 1
                    fmap[name] = f
                    self.stats["source_role_entries"] += 1
                live.append(fmap[name])
            for oname in R.owned:
                if self.policy == "unit":
                    of = ("own", g, oname)
                elif self.policy == "depth":
                    of = ("own-depth", id(frame), d, oname)
                else:
                    raise ValueError(self.policy)
                self.push(of, (g, oname), None)    # owned centre must be free when allocated
                omap[oname] = of
                live.append(of)
        need(all(used[k] == len(v) for k, v in supply.items()), "every parent job consumed")
        need(len(live) == len(set(live)), "I1 simultaneously live roles of a class are distinct arrays")
        self.stats["classes"] += 1
        self.stats["units"] += len(units)
        self.stats["max_class_live_roles"] = max(self.stats["max_class_live_roles"], len(live))
        pending = []
        for j, (r, owner) in enumerate(R.rounds):
            out = []
            for U in units:
                c, g, pt, col, fmap, omap, issuing = U
                need(issuing is None, "I3 lockstep: parent suspended until its child finished")
                f = fmap.get(owner, omap.get(owner))
                st = self.stack[f]
                need(st and st[-1] == (g, owner), "I3 paid job issued on a field the unit currently owns")
                U[6] = f
                out.append({"copy": c, "point": pt, "rank": r * col, "field": f, "issuer": (g, owner)})
            need(len({o["field"] for o in out}) == len(out), "I3 ordered round has no field alias")
            if d < G:
                if self.eager:
                    pending.append((r, out))
                    if len(pending) == 2 or j == len(R.rounds) - 1:
                        # eager parent: issue next round before the earlier child class finished
                        for U in units:
                            U[6] = None
                        for rr, oo in pending:
                            self.run_class(frame, n, a, G, d + 1, dil * rr, oo, exits_iter)
                        pending = []
                    continue
                self.run_class(frame, n, a, G, d + 1, dil * r, out, exits_iter)
            else:
                e, t = next(exits_iter)
                need(all(o["rank"] == e for o in out) and len(out) == a * t, "exit batch shape")
                Be = self.compile(e)[0]
                flds = [o["field"] for o in out]
                tps = [o["issuer"] for o in out]
                if self.bad_exit and len(flds) >= 2:
                    flds[1] = flds[0]
                if self.partial:
                    self.sub(e, flds, tps)
                else:
                    need(len(out) % Be == 0, "I5 exit batch integral")
                    for i in range(0, len(flds), Be):
                        self.sub(e, flds[i:i + Be], tps[i:i + Be])
                self.stats["exit_jobs"] += len(out)
            for U in units:
                f = U[6]
                if f is not None:
                    st = self.stack[f]
                    need(st[-1] == (U[1], owner), "I4 field returned to the parent after the child class")
                U[6] = None
        for U in units:
            c, g, pt, col, fmap, omap, _ = U
            for oname, of in omap.items():
                self.pop(of, (g, oname))
            for name, _ in reversed(R.roles):
                self.pop(fmap[name], (g, name))


def audit(rule, n, copies_if_large=2, **kw):
    C = Compiler(rule, **kw)
    B, a, P, cost = C.compile(n)
    sources = C.plan(n)[0]
    G = C.plan(n)[3]
    copies = None if cost <= C.budget else min(a, copies_if_large)
    k = a if copies is None else copies
    fields = [("array", i) for i in range(k * len(sources))]
    C.uniform(n, fields, [None] * len(fields), top_level=True, copies=copies)
    need(all(not C.stack[f] for f in C.stack), "I4 all stacks empty at the end")
    need(all(C.received[f] == 2 for f in fields), "I6 every array: complement + source job exactly once")
    return {"rank": n, "generations": G, "width_B_log10": len(str(B)) - 1, "replication_a_log10": len(str(a)) - 1,
            "P_over_B": float(Fraction(P, B)), "executed_tree_copies": k, "full_width_executed": copies is None,
            "events": C.events, "max_live_stack_on_one_array": C.max_live_depth, **dict(C.stats)}


def negative(rule, n, **kw):
    try:
        audit(rule, n, **kw)
        return None
    except Violation as e:
        return str(e)


# ------------------------------------------------------------------ rule zoo
def toy():
    return Rule("toy (finite_dag_audit synthetic)", (("a", 3), ("b", 3), ("c", 4)),
                ((1, "a"), (1, "C0"), (1, "b"), (1, "a"), (2, "c"), (2, "C0")))


def bit_shaped(seed, roles_per_rank=(4, 2, 1), n_rounds=24, adversarial=None):
    """Target ranks {8,22,50} and paid ranks 1..7 of the BIT p3 word, reduced multiplicities,
    random (or adversarial) chronological owners including the owned centre."""
    rng = random.Random(seed)
    roles = [(f"t{k}_{i}", k) for k, cnt in zip((8, 22, 50), roles_per_rank) for i in range(cnt)]
    names = [nm for nm, _ in roles] + ["C0"]
    rounds = []
    for j in range(n_rounds):
        r = rng.randint(1, 7)
        if adversarial == "one_owner":
            o = names[0]
        elif adversarial == "centre":
            o = "C0"
        else:
            o = rng.choice(names)
        rounds.append((r, o))
    return Rule(f"BIT-shaped seed={seed} {adversarial or 'random'}", roles, rounds)


def complex_p2():
    """Actual p2 complex rule, owners in native order (same extraction as finite_dag_audit)."""
    def rd(p):
        raw = Path(p).read_bytes()
        return json.loads(gzip.decompress(raw) if str(p).endswith(".gz") else raw)
    ctl = rd(REPO / "research/kappa-rebuild/controller/GLOBAL-IDENTITY-COVER.json.gz")["all_three"]
    nat = rd(REPO / "research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz")
    roles = [(f"{s}{p}:{q}", 41) for p in range(2) for s in "XY" for q in range(112)]
    roles += [(row["owner"], row["target_rank"]) for row in ctl["fresh_outputs"]]
    rounds = []
    for stage, (pair, dirn) in enumerate(((0, "forward"), (0, "backward"), (0, "forward"), (1, "backward"), (1, "forward"))):
        helper = {row["role"]: row["owner"] for row in ctl["helper_bindings"] if row["stage"] == stage}
        for ev in nat[dirn]:
            if ev[0] == "climb":
                _, part, role, old, new, rank = ev
                owner = f"X{pair}:{role}" if role < 112 else f"Y{pair}:{role-112}" if role < 224 else helper[role]
                rounds.append((rank, owner))
            elif ev[0] == "center":
                rounds.append((ev[-1], "C0"))
        for res in ctl["paid_residuals"]:
            if res["after_stage"] == stage:
                rounds.append((res["rank"], res["owner"]))
    assert Counter(r for r, _ in rounds) == Counter({int(k): v for k, v in ctl["paid"].items()})
    return Rule("complex p2 actual native owners", roles, rounds)
