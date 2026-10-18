"""Variable nested helper ends, with complete frame domains and coupled cones.

Extends navinor's unchanged frame model in references/frame_model.py.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
M = ModuleType("retained_frame_model")
exec(compile((HERE / "references/frame_model.py").read_bytes(),
             str(HERE / "references/frame_model.py"), "exec", optimize=0), M.__dict__)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def cone_supports(word, n, v):
    """Separate support for every low-end helper; do not merge their end caps."""
    ident = lambda: [{k: Q(1)} for k in range(n)]
    main = word["A"] + word["cut"] + word["B"]
    raw = ident()
    for event in main:
        M.apply(event, raw)
    dirt = [{} for _ in range(n)]
    for y in range(v, 2 * v):
        dirt[y] = {k: a for k, a in raw[y].items() if k >= 2 * v}
    for event in word["precondition"]:
        M.apply(event, dirt)
    compensation = [["add", y, k, -a.numerator, a.denominator, []]
                    for y in range(v, 2 * v) for k, a in sorted(dirt[y].items())]
    prefix = word["precondition"] + compensation + main
    direct, inverse = ident(), ident()
    for event in prefix:
        M.apply(event, direct)
    for event in reversed(prefix):
        M.apply(M.invert(event), inverse)
    return {int(q): sorted((set(inverse[int(q)]) |
                           {k for k in range(n) if int(q) in direct[k]}) - {int(q)})
            for q in word["helper_final"]}


class Model(M.Model):
    """Every nested endpoint contraction with all original gate frames free."""

    def __init__(self, word):
        super().__init__(word)
        self.original_caps = {int(q): M.basis(U) for q, U in word["helper_final"].items()}
        self.cones = cone_supports(word, self.n, self.v)
        self.original_edges = dict(self.edges)
        self.boundaries = {}
        for q, chain in self.chains.items():
            before = [node for node in chain if node[0] in ("S", "P") or
                      (node[0] == "G" and node[1] < self.nA + self.nB)]
            self.boundaries[q] = before[-1]
        self.cone_edges = sorted({(self.boundaries[k], ("E", q))
                                  for q, support in self.cones.items() for k in support})
        for edge in self.cone_edges:
            self.edges.setdefault(edge, 0)
        # A cone edge imposes containment, but creates no recursive child.
        for q in self.original_caps:
            del self.fixed_frames[("E", q)]
        pins = sorted(node for node in self.fixed_frames if node[0] == "P")
        order = [("S", q) for q in range(self.n)]
        for i in range(len(self.gates)):
            if i == self.nA:
                order.extend(pins)
            order.append(("G", i))
        order.extend(("E", q) for q in range(self.n))
        self.order = order
        pos = {node: i for i, node in enumerate(order)}
        pred, succ = defaultdict(list), defaultdict(list)
        for a, b in self.edges:
            require(pos[a] < pos[b], "nonchronological containment edge")
            pred[b].append(a)
            succ[a].append(b)
        lo, hi = {}, {}
        for node in order:
            joined = M.join(lo[a] for a in pred[node])
            if node in self.fixed_frames:
                require(M.contained(joined, self.fixed_frames[node]), "inconsistent fixed lower frame")
                lo[node] = self.fixed_frames[node]
            else:
                lo[node] = joined
        for node in reversed(order):
            U = self.original_caps.get(node[1], M.FULL) if node[0] == "E" else M.FULL
            for b in succ[node]:
                U = M.meet(U, hi[b])
            if node in self.fixed_frames:
                require(M.contained(self.fixed_frames[node], U), "inconsistent fixed upper frame")
                U = self.fixed_frames[node]
            hi[node] = U
            require(M.contained(lo[node], U), "empty complete domain")
        self.lo, self.hi = lo, hi
        self.domain = {node: M.interval(lo[node], hi[node]) for node in order if lo[node] != hi[node]}
        for node, choices in self.domain.items():
            require(self.given_frame(node) in choices, "baseline missing from domain")
        self.profile(self.baseline())

    def given_frame(self, node):
        return self.given[node[1]] if node[0] == "G" else self.original_caps[node[1]]

    def baseline(self):
        return {node: self.given_frame(node) for node in self.domain}

    def profile(self, assignment):
        return {d: n for d, n in super().profile(assignment).items() if n}

    def components(self):
        return sorted([sorted(c) for c in super().components()], key=lambda c: c[0])


lp = M.lp
assignment_cost = M.assignment_cost
