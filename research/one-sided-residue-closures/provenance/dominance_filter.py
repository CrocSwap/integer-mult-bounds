# Dominance filter: applies the eight span facts (CONF) to the slack<=7 survivor lists in generator/land7.out
# (Lemma B: a basis of e pieces with total support < 53 whose pieces fit into the flats/free lines of a config with span <= d-1 kills the row).
# usage: python3 dominance_filter.py [land7.out]   -> prints "<all survivors> <not dominated>" and writes the open rows as open_rows.json
import re, itertools, sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
g = {1:1, 2:2, 3:4, 4:8, 5:12, 6:20, 7:36}
# (flat dimensions, free lines, proven span bound):  see SPANFACTS.md
CONF = [((6,6),1,3), ((6,6),2,4), ((6,6,3),0,4), ((7,4),0,4), ((7,5),0,4), ((6,6,4),0,5), ((6,5,4),1,4), ((6,4,4),1,4)]
def fits(B, dims, s):
    B = sorted(B, reverse=True); n = len(B); k = len(dims)
    def rec(i, cap, free):
        if i == n: return True
        w = B[i]
        for j in range(k):
            if cap[j] >= w:
                cap[j] -= w
                if rec(i+1, cap, free): cap[j] += w; return True
                cap[j] += w
        if g[w] <= free and rec(i+1, cap, free-g[w]): return True
        return False
    return rec(0, list(dims), s)
def killer(ws, d, e):
    for B in set(itertools.combinations(sorted(ws), e)):
        if sum(g[w] for w in B) >= 53: continue
        for dims, s, span in CONF:
            if span <= d-1 and fits(B, dims, s): return 1
    return None
def main(path):
    rows = []
    for l in open(path):
        m = re.match(r'd (\d) slack (\d) (\{.*?\}) (\[.*\])', l.strip())
        if not m: continue
        d = int(m.group(1)); k = int(m.group(2))
        for (kk, ws, e) in eval(m.group(4)): rows.append((d, k, ws, e))
    L = [r for r in rows if not killer(r[2], r[0], r[3])]
    print(len(rows), len(L))
    json.dump(L, open(os.path.join(os.environ.get('OUT', '.'), 'open_rows.json'), 'w'))
main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'generator', 'land7.out'))
