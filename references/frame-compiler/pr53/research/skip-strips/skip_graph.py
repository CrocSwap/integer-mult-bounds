"""Skip-prefix strip producer, stacked on the PR #48 pipeline.

Only the scalar addition DAG changes. Everything else is inherited from
Chafik Boukhalfa's PR #48 research/copied-fixed pipeline, which composes
Rohan Arun's PR #44 weighted carrier matching, exact data-corner recovery
(PR #46), RaD / hipotures PR #41 alternating pair order and PR #43's
original-envelope / fixed I+J framework. Those build in turn on icekylinx
PR #18/#32/#36 and earlier credited work.

New here: every leave-one-out "strip" vector (a vertex's star sums over the
other groups) uses a skip-prefix layout

    s_j = A_{j-2} + (v_{j-1} + B_{j+1}),

where A_i and B_i are ordinary prefix and suffix sums. In the usual layout
s_j = A_{j-1} + B_{j+1}, the two consumers of each prefix A_i are A_{i+1} and
s_{i+1}. Their point covers are incomparable, so the extra use of A_i always
needs a fresh role. With the skip layout the consumers of A_i are A_{i+1} and
s_{i+2}, and cover(A_{i+1}) is contained in cover(s_{i+2}). Likewise
cover(v_{i-1} + B_{i+1}) is contained in cover(B_{i-1}). These nested covers
are exactly what the inherited carrier matching may join.

The top recursion level applies the layout to the reversed value list. Deeper
levels apply it to the value list sorted by (support size, support), the
PR #48 sorting idea: ascending at h=23 and descending support at h=25. Totals
fold in reverse input order at h=23 (PR #48's rule) and in descending
(support size, support) order at h=25 (PR #43/#48's rule).

Apache-2.0, like the inherited files. Prepared with assistance from Claude
(Anthropic).
"""
from itertools import combinations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from partial_swap.paired import PairedExclusionCircuit
from partial_swap.shared import SharedPointCircuit


def alternating_points(h, common):
    """RaD PR #41 alternating global pair order (as specialized in PR #43/#48)."""
    pairs = [(a, a+1) for a in range(0, h-1, 2) if common not in (a, a+1)]
    if common % 2:
        pairs.reverse()
    head = [x for pair in pairs for x in pair]
    return head + [x for x in range(h) if x != common and x not in head]


def prefix_suffix(c, vals):
    """Ordinary leave-one-out: total and s_j = A_{j-1} + B_{j+1}."""
    n = len(vals)
    prefix = [0]
    for x in vals:
        prefix.append(c.add(prefix[-1], x))
    suffix = [0]*(n+1)
    for i in range(n-1, -1, -1):
        suffix[i] = c.add(vals[i], suffix[i+1])
    return prefix[-1], [c.add(prefix[i], suffix[i+1]) for i in range(n)]


def skip_prefix(c, vals):
    """Leave-one-out with s_j = A_{j-2} + (v_{j-1} + B_{j+1}) (1-indexed)."""
    k = len(vals)
    if k <= 2:
        return prefix_suffix(c, vals)
    v = [0] + list(vals)
    A = [0]*(k+1)
    for i in range(1, k):
        A[i] = c.add(A[i-1], v[i])
    B = [0]*(k+2)
    for i in range(k, 1, -1):
        B[i] = c.add(v[i], B[i+1])
    out = [0]*(k+1)
    out[1] = B[2]
    for j in range(2, k+1):
        out[j] = c.add(A[j-2], c.add(v[j-1], B[j+1]))
    return c.add(A[k-1], v[k]), out[1:]


def skip_prefix_reversed(c, vals):
    total, out = skip_prefix(c, list(vals)[::-1])
    return total, out[::-1]


def sorted_layout(layout, sign):
    """Apply a layout to values sorted by (support size, sign*support); restore order."""
    def apply(c, vals):
        order = sorted(range(len(vals)), key=lambda i: (c.support[vals[i]].bit_count(), sign*c.support[vals[i]]))
        total, out = layout(c, [vals[i] for i in order])
        restored = [0]*len(vals)
        for position, original in enumerate(order):
            restored[original] = out[position]
        return total, restored
    return apply


def leave_one_out(c, values, layout):
    """Zero entries are omitted; their leave-one-out value is the total."""
    values = list(values)
    nonzero = [i for i, x in enumerate(values) if x]
    if not nonzero:
        return 0, [0]*len(values)
    if len(nonzero) == 1:
        x = values[nonzero[0]]
        return x, [0 if i in nonzero else x for i in range(len(values))]
    total, out = layout(c, [values[i] for i in nonzero])
    result = [total]*len(values)
    for i, x in zip(nonzero, out):
        result[i] = x
    return total, result


def circuit_class(h):
    deep_sign = 1 if h == 23 else -1

    class SkipStripCircuit(PairedExclusionCircuit):
        base_threshold = 2

        def total(self, values):
            values = [x for x in values if x]
            if h == 23:
                values.reverse()
            else:
                values.sort(key=lambda node: (self.support[node].bit_count(), self.support[node]), reverse=True)
            result = 0
            for node in values:
                result = self.add(result, node)
            return result

        def block(self, points, edges, weights):
            level = getattr(self, '_level', -1) + 1
            self._level = level
            try:
                return self._block(points, edges, weights, level)
            finally:
                self._level = level - 1

        def _block(self, points, edges, weights, level):
            if len(points) <= self.base_threshold:
                return PairedExclusionCircuit.block(self, points, edges, weights)
            layout = skip_prefix_reversed if level == 0 else sorted_layout(skip_prefix, deep_sign)
            groups = self.grouping(points)
            ng = len(groups)
            e = lambda a, b: edges[tuple(sorted((a, b)))]
            coarse = {(i, j): self.total([e(a, b) for a in groups[i] for b in groups[j]])
                      for i, j in combinations(range(ng), 2)}
            wt = {i: self.total([weights[a] for a in g] + [e(a, b) for a, b in combinations(g, 2)])
                  for i, g in enumerate(groups)}
            total, outside, far = self.block(list(range(ng)), coarse, wt)
            strips, sums = {}, {}
            for i, g in enumerate(groups):
                other = [j for j in range(ng) if j != i]
                for a in g:
                    carry = self.total([weights[u] for u in g if u != a])
                    vals = [self.total([e(u, v) for u in g if u != a for v in groups[j]]) for j in other]
                    st, one = leave_one_out(self, [carry] + vals, layout)
                    strips[a] = {j: z for j, z in zip(other, one[1:])}
                    sums[a] = st
            out = {}
            single = {a: self.add(outside[i], sums[a]) for i, g in enumerate(groups) for a in g}
            for i, g in enumerate(groups):
                for a, b in combinations(g, 2):
                    out[a, b] = outside[i]
            for i, j in combinations(range(ng), 2):
                for a in groups[i]:
                    left = self.add(far[i, j], strips[a][j])
                    for b in groups[j]:
                        cross = self.total([e(u, v) for u in groups[i] if u != a for v in groups[j] if v != b])
                        out[a, b] = self.add(left, self.add(strips[b][i], cross))
            return total, single, out
    return SkipStripCircuit


def graph(h):
    assert h in (23, 25)
    local = circuit_class(h)(h-1)
    total = local.pair(list(range(h-1)))[0]
    local.outputs[()] = total
    stack = [total]
    while stack:
        node = stack.pop()
        if not node or node in local.active:
            continue
        local.active.add(node)
        if local.args[node]:
            stack.extend(local.args[node])
    local.additions = sum(local.args[node] is not None for node in local.active)
    return SharedPointCircuit(h, local, point_order=alternating_points)
