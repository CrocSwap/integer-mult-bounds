"""Event-level executor of the FINITE-PRECOMPILATION lockstep compiler, extended with
(a) tagged rounds produced by the completion/splitting pass and (b) a LIFO owned-bank
allocator ("stack" policy) whose peak occupancy is measured.

Derived from research/lockstep-live-role-audit/live_roles.py (our #4691), which keeps,
for every physical field, the stack of live roles and checks the ownership invariants
I1-I6 at every event.  Everything from that file is retained; the additions are:

  * Rule.kinds   one tag per chronological round: "orig" (an original paid job),
                 "piece" (a non-leading piece of a split job) or "completion"
                 (a piece of the paid completion of a small target on its own owner);
  * Rule.completed  role -> (K, L) for every role completed from rank K to rank L;
  * owned_policy="stack": owned banks are taken from one LIFO stack of bank slots.
    A unit allocates its banks when its class starts and frees them when its class
    ends; the executor requires the freed banks to be exactly the top of the stack
    (nested lifetimes, invariant I7) and records the peak number of live slots;
  * owned_policy="release_early": a deliberately wrong allocator that frees the
    class's banks before its rounds run (must be rejected);
  * per-execution counters for pieces, completions, adapters and bank scans.

Imported by counts.py, verify.py and test_verify.py.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from math import factorial, gcd, lcm, prod
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


class Violation(Exception):
    pass


def need(ok, msg):
    if not ok:
        raise Violation(msg)


# ------------------------------------------------------------------ rules
class Rule:
    def __init__(self, name, roles, rounds, owned=("C0",), kinds=None, completed=None):
        self.name, self.roles, self.rounds, self.owned = name, tuple(roles), tuple(rounds), tuple(owned)
        self.kinds = tuple(kinds) if kinds is not None else tuple("orig" for _ in self.rounds)
        self.completed = dict(completed or {})
        assert len(self.kinds) == len(self.rounds)
        assert all(k in ("orig", "piece", "completion") for k in self.kinds)
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

    # per-unit record counts of the pass (see PROOF.md, Lemma A)
    def pass_counts(self):
        kinds = Counter(self.kinds)
        return {"rounds": len(self.rounds), "orig_rounds": kinds["orig"], "piece_rounds": kinds["piece"],
                "completion_rounds": kinds["completion"], "completed_roles": len(self.completed),
                "adapters": 2 * len(self.completed),
                "relocations": kinds["piece"] + kinds["completion"],
                "owned_banks": len(self.owned)}


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
        self.bank_stack = []                 # LIFO allocator of owned-bank slots ("stack" policy)
        self.peak_banks = 0
        self.total_bank_allocations = 0

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

    # ---------------- owned banks
    def alloc_bank(self, g, oname, frame, d):
        """Return the physical field of one owned bank of unit g under the current policy."""
        if self.policy in ("unit",):
            of = ("own", g, oname)
        elif self.policy == "depth":
            of = ("own-depth", id(frame), d, oname)
        elif self.policy in ("stack", "release_early"):
            slot = len(self.bank_stack)
            self.bank_stack.append((g, oname))
            self.peak_banks = max(self.peak_banks, len(self.bank_stack))
            of = ("bank", slot)
        else:
            raise ValueError(self.policy)
        self.total_bank_allocations += 1
        self.stats["bank_init_scans"] += 1
        return of

    def free_class_banks(self, units):
        """Invariant I7 (nested lifetimes): the banks of a finishing class are exactly the
        top of the LIFO allocator.  Banks are then released for reuse by sibling classes."""
        if self.policy not in ("stack", "release_early"):
            return
        mine = [(g, oname) for _, g, _, _, _, omap, _ in units for oname in omap]
        top = self.bank_stack[len(self.bank_stack) - len(mine):]
        need(len(self.bank_stack) >= len(mine) and Counter(top) == Counter(mine),
             "I7 nested bank lifetimes: a finishing class's banks are not the top of the allocator")
        del self.bank_stack[len(self.bank_stack) - len(mine):]
        self.stats["bank_erase_scans"] += len(mine)

    # ---------------- execution
    def blackbox(self, n, fields, tops):
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
        by_rank = defaultdict(list)
        for c in range(a):
            for i, s in enumerate(sources):
                by_rank[s].append(fields[c * S + i])
        for s in sorted(by_rank):
            grp = by_rank[s]
            if top_level:
                for f in grp:
                    self.received[f] += 1
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
        units = []      # (copy, guid, point, column, {role: field}, owned {name: field}, issuing)
        for c in range(a):
            for pt in R.lattice(n, dil):
                if sum(pt) != G - d:
                    continue
                for _ in range(R.u(pt)):
                    units.append([c, self.next_guid(), pt, dil * R.c(pt), {}, {}, None])
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
                of = self.alloc_bank(g, oname, frame, d)
                self.push(of, (g, oname), None)    # owned bank must be free when allocated
                omap[oname] = of
                live.append(of)
        need(all(used[k] == len(v) for k, v in supply.items()), "every parent job consumed")
        need(len(live) == len(set(live)), "I1 simultaneously live roles of a class are distinct arrays")
        self.stats["classes"] += 1
        self.stats["units"] += len(units)
        self.stats["max_class_live_roles"] = max(self.stats["max_class_live_roles"], len(live))
        pc = R.pass_counts()
        self.stats["adapter_records"] += pc["adapters"] * len(units)
        self.stats["relocation_records"] += pc["relocations"] * len(units)
        if self.policy == "release_early":
            # wrong allocator: give the slots back before the rounds (children may alias them)
            mine = [(g, oname) for _, g, _, _, _, omap, _ in units for oname in omap]
            del self.bank_stack[len(self.bank_stack) - len(mine):]
            for U in units:
                for oname, of in U[5].items():
                    self.pop(of, (U[1], oname))
        pending = []
        for j, ((r, owner), kind) in enumerate(zip(R.rounds, R.kinds)):
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
            self.stats[f"{kind}_jobs"] += len(out)
            if d < G:
                if self.eager:
                    pending.append((r, out))
                    if len(pending) == 2 or j == len(R.rounds) - 1:
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
        if self.policy != "release_early":
            self.free_class_banks(units)
            for U in units:
                c, g, pt, col, fmap, omap, _ = U
                for oname, of in omap.items():
                    self.pop(of, (g, oname))
        for U in units:
            c, g, pt, col, fmap, omap, _ = U
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
    need(not C.bank_stack, "I7 allocator empty at the end")
    return {"rank": n, "generations": G, "width_B_log10": len(str(B)) - 1, "replication_a_log10": len(str(a)) - 1,
            "P_over_B": float(Fraction(P, B)), "executed_tree_copies": k, "full_width_executed": copies is None,
            "events": C.events, "max_live_stack_on_one_array": C.max_live_depth,
            "peak_banks": C.peak_banks, "total_bank_allocations": C.total_bank_allocations, **dict(C.stats)}


def negative(rule, n, **kw):
    try:
        audit(rule, n, **kw)
        return None
    except Violation as e:
        return str(e)


# ------------------------------------------------------------------ the pass (Lemma A)
class RawRule:
    """Input of the pass: a native unit whose paid ranks may overlap its target ranks, so the
    lockstep hierarchy r_max < k_min is not asserted (it holds only after the pass)."""

    def __init__(self, name, roles, rounds, owned=("C0",)):
        self.name, self.roles, self.rounds, self.owned = name, tuple(roles), tuple(rounds), tuple(owned)
        self.kinds = tuple("orig" for _ in self.rounds)
        self.completed = {}
        self.targets = Counter(k for _, k in self.roles)

    @property
    def separated(self):
        return max(r for r, _ in self.rounds) < min(self.targets)


def pieces(rank, J):
    """Consecutive disjoint-axis pieces of a job of the given rank at cutoff J."""
    q, r = divmod(rank, J)
    return [J] * q + ([r] if r else [])


def complete_and_split(rule, J, L, name=None, completion_owner="self", drop_remainder=False,
                       completion_rank_shift=0):
    """Completion of every role of rank K<L to rank L by a paid job of rank L-K on disjoint
    axes of that same owner (after every original round), then splitting of every paid job,
    original or completion, into consecutive pieces of rank <= J.  Returns the new Rule.
    The keyword mutations are rejecting controls, never used for a result."""
    assert 0 < J < L, "cutoff must be below the completion floor"
    roles = tuple((nm, max(k, L)) for nm, k in rule.roles)
    rounds, kinds = [], []
    for (r, owner), kind in zip(rule.rounds, rule.kinds):
        ps = pieces(r, J)
        if drop_remainder and len(ps) > 1 and ps[-1] != J:
            ps = ps[:-1]
        for i, p in enumerate(ps):
            rounds.append((p, owner))
            kinds.append(kind if i == 0 else "piece")
    completed = dict(rule.completed)
    for nm, k in rule.roles:
        if k < L:
            D = L - k + completion_rank_shift
            owner = nm if completion_owner == "self" else completion_owner
            for p in pieces(D, J):
                rounds.append((p, owner))
                kinds.append("completion")
            completed[nm] = (k, L)
    return Rule(name or f"{rule.name} | completed L={L}, split J={J}", roles, rounds, rule.owned, kinds, completed)


# ------------------------------------------------------------------ rule zoo
def toy():
    return Rule("toy (finite_dag_audit synthetic)", (("a", 3), ("b", 3), ("c", 4)),
                ((1, "a"), (1, "C0"), (1, "b"), (1, "a"), (2, "c"), (2, "C0")))


def overlapping_toy():
    """Paid ranks reach the smallest target: the lockstep hierarchy fails before the pass."""
    roles = (("a", 3), ("b", 5), ("c", 8))
    rounds = ((1, "a"), (4, "C0"), (7, "b"), (2, "a"), (5, "c"), (3, "C0"), (6, "b"))
    return roles, rounds


def shaped(name, target_ranks, role_counts, paid_ranks, n_rounds, seed, owned=("C0",), adversarial=None):
    rng = random.Random(seed)
    roles = [(f"t{k}_{i}", k) for k, cnt in zip(target_ranks, role_counts) for i in range(cnt)]
    names = [nm for nm, _ in roles] + list(owned)
    rounds = []
    for _ in range(n_rounds):
        r = rng.choice(paid_ranks)
        if adversarial == "one_owner":
            o = names[0]
        elif adversarial == "centre":
            o = owned[0]
        else:
            o = rng.choice(names)
        rounds.append((r, o))
    return roles, rounds


P7_TARGET_RANKS = (5, 6, 7, 8, 9, 25, 41, 57, 121)
P7_PAID_RANKS = (1, 2, 3, 4, 5, 8, 16, 32, 48)
SELECTED_TARGET_RANKS = (4, 7, 8, 9, 17, 25, 33, 41, 49, 57, 65, 73, 145)
SELECTED_PAID_RANKS = (1, 2, 3, 4, 5, 8, 16, 24, 32, 40, 48, 56, 64, 72)


def p7_shaped(seed, role_counts=(2, 1, 1, 1, 2, 1, 1, 1, 1), n_rounds=20, adversarial=None):
    roles, rounds = shaped("p7", P7_TARGET_RANKS, role_counts, P7_PAID_RANKS, n_rounds, seed, adversarial=adversarial)
    return roles, rounds, f"p7-shaped seed={seed} {adversarial or 'random'}"


def selected_shaped(seed, n_local=3, adversarial=None):
    """Rank sets of the selected #5413 caller with reduced multiplicities and the caller's
    chronology shape: LOCAL blocks of small-rank jobs on helper roles and the owned centre,
    IDLE jobs of rank 16..72 on main roles, rank-one QUERY jobs on the owned query bank."""
    rng = random.Random(seed)
    helpers = [(f"h{k}_{i}", k) for k, cnt in zip((4, 7, 8, 9), (1, 1, 1, 2)) for i in range(cnt)]
    mains = [(f"m{k}", k) for k in (17, 25, 33, 41, 49, 57, 65, 73, 145)]
    roles = helpers + mains
    owned = ("C0", "Q")
    hnames = [nm for nm, _ in helpers] + ["C0"]
    mnames = [nm for nm, _ in mains]
    rounds = []
    idle = iter((16, 24, 32, 40, 48, 56, 64, 72) * 2)
    for _ in range(n_local):
        for _ in range(4):
            r = rng.choice((1, 2, 3, 4, 5, 8))
            o = hnames[0] if adversarial == "one_owner" else "C0" if adversarial == "centre" else rng.choice(hnames)
            rounds.append((r, o))
        rounds.append((next(idle), "C0" if adversarial == "centre" else rng.choice(mnames)))
        rounds.append((1, "Q"))
    return roles, rounds, owned, f"selected-shaped seed={seed} {adversarial or 'random'}"
