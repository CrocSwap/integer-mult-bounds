"""Lossless graph contraction for concave rank costs, with fixed scalar word.
A free node with a single distinct predecessor can take that predecessor's
frame: c(x)+c(y)>=c(x+y) on each incident role. Symmetric for one successor.
Transport nodes are excluded; multiplicities must balance.
"""

from collections import defaultdict


def reduce(loc, pr, nx):
    loc = list(loc)
    pr = defaultdict(list, {i: list(v) for i, v in pr.items()})
    nx = defaultdict(list, {i: list(v) for i, v in nx.items()})
    aliases = {}
    changed = True
    while changed:
        changed = False
        for i, where in enumerate(loc):
            if (
                where is None
                or where[0].startswith("warp_")
                or not pr[i]
                or len(pr[i]) != len(nx[i])
            ):
                continue
            if len(set(pr[i])) == 1:
                a = pr[i][0]
                for j in nx[i]:
                    pr[j].remove(i)
                    pr[j].append(a)
                nx[a] = [j for j in nx[a] if j != i] + list(nx[i])
            elif len(set(nx[i])) == 1:
                a = nx[i][0]
                for j in pr[i]:
                    nx[j].remove(i)
                    nx[j].append(a)
                pr[a] = [j for j in pr[a] if j != i] + list(pr[i])
            else:
                continue
            aliases[i] = a
            loc[i] = None
            pr[i] = []
            nx[i] = []
            changed = True

    def resolve(i):
        while i in aliases:
            i = aliases[i]
        return i

    return loc, pr, nx, {i: resolve(i) for i in aliases}
