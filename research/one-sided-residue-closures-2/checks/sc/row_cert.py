"""Per-row certificate for every span-pass kill in the ledger (replaces the inherited config->row dominance table).
A row (d, weights, e) is killed by a PASS of config (f1,f2,f3)+s at target T when (Lemma B, as in #2985):
  T <= d (a pass at T proves span <= T-1 <= d-1), and some e-subset B of the pieces has sum g(w) < 53 and packs into the
  config: each piece goes into a flat with enough remaining dimension (dimensions add) or is a free piece costing g(w)
  lines, with total free lines <= s.  This script finds such a B and packing for every row and prints it; FAIL otherwise.
usage: python row_cert.py ledger2_consolidated.csv"""
import csv, itertools, json, re, sys
g = {1: 1, 2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
def packs(B, flats, s):
    B = sorted(B, reverse=True)
    def rec(i, cap, free):
        if i == len(B): return []
        w = B[i]
        for j in range(len(cap)):
            if cap[j] >= w:
                cap[j] -= w; r = rec(i + 1, cap, free); cap[j] += w
                if r is not None: return [(w, 'flat%d' % j)] + r
        if g[w] <= free:
            r = rec(i + 1, cap, free - g[w])
            if r is not None: return [(w, 'free')] + r
        return None
    return rec(0, list(flats), s)
bad = n = 0
for row in csv.DictReader(open(sys.argv[1])):
    m = re.search(r'span pass (\d)-(\d)(?:-(\d))?-s(\d)@T(\d)', row['killed_by'])
    if not m or row['status'] != 'KILLED(new)': continue
    n += 1
    flats = [int(x) for x in m.group(1, 2, 3) if x]; s = int(m.group(4)); T = int(m.group(5))
    d = int(row['d']); e = int(row['e']); ws = json.loads(row['weights'])
    cert = None
    if T <= d:
        for B in sorted(set(itertools.combinations(sorted(ws), e))):
            if sum(g[w] for w in B) >= 53: continue
            p = packs(B, flats, s)
            if p is not None: cert = (B, p); break
    if cert: print('PASS row %s d=%d T=%d config %s+%d: B=%s packing %s' % (row['row'], d, T, flats, s, list(cert[0]), cert[1]))
    else: bad += 1; print('FAIL row %s d=%d T=%d config %s+%d: no Lemma-B packing' % (row['row'], d, T, flats, s))
print(('PASS' if bad == 0 and n > 0 else 'FAIL') + ' span-pass row certificates: %d rows, %d without certificate' % (n, bad))
