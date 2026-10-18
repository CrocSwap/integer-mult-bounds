"""exchange: BRoute's read-set exchange family on gauge44-lineage words (copy pairs h = E_h + r after the copy
gate add(h, r, 1); post-copy target reads of h <-> r with entrance pre-reads deleted / inserted), as a move library:
pair detection, movable reads, move application (ported from construction/sw4/build_sw4.py), B-segment exactness mod p."""
import gzip, json, collections, hashlib, sys
V = 112; PR = 2147483629
def regs(e): return e[1:3] if e[0] == 'add' else e[1:2]
def is_target(q): return V <= q < 2 * V
def copy_pairs(w):
    """h (entering) -> (r, copy index): first B write of h is add(h, r, 1/1) from a non-target r; earlier B gates on h are target pre-reads."""
    entering = set(map(int, w['start_extra'])); B = w['B']; first = {}
    for i, e in enumerate(B):
        if e[1] in entering and e[1] not in first: first[e[1]] = i
    pairs = {}
    for h, i in sorted(first.items()):
        e = B[i]
        if e[0] == 'add' and (e[3], e[4]) == (1, 1) and not is_target(e[2]) and e[2] != h:
            if all(g[0] == 'add' and is_target(g[1]) and g[2] == h for g in B[:i] if h in regs(g)): pairs[h] = (e[2], i)
    return pairs
def movable_reads(w, h, r, i):
    """target reads of h or r after the copy gate i and before the next write of h or r: list of (index, target, source, coef)."""
    B = w['B']; out = []
    for j in range(i + 1, len(B)):
        e = B[j]
        if e[1] in (h, r): break
        if e[0] == 'add' and is_target(e[1]) and e[2] in (h, r): out.append((j, e[1], e[2], (e[3], e[4])))
    return out
def prereads(w, h, i):
    """index -> (target, coef) of the entrance pre-reads add(t, h, c) before the copy gate i."""
    return {j: (e[1], (e[3], e[4])) for j, e in enumerate(w['B'][:i]) if e[0] == 'add' and e[2] == h and is_target(e[1])}
def moves_for(w, h, r, i, subset):
    """explicit moves (build_sw4 recipe format) for a subset of movable reads of pair (h, r); None if a needed pre-read is missing."""
    pre = prereads(w, h, i); by_target = {t: (j, c) for j, (t, c) in pre.items()}
    last_pre = max(pre) if pre else -1; ins_before = last_pre + 1
    out = []
    for j, t, s, (a, b) in subset:
        if s == h:
            if t not in by_target or by_target[t][1] != (-a, b): return None
            out.append(dict(kind='h2r', read_index=j, target=t, h=h, r=r, coef=[a, b], delete_preread_index=by_target[t][0]))
        else:
            if t in by_target: return None    # t already pre-reads h: inserting a second pre-read is outside the family
            out.append(dict(kind='r2h', read_index=j, target=t, h=h, r=r, coef=[a, b], preread=['add', t, h, -a, b], insert_preread_before=ins_before))
    return out
def apply_moves(w, moves):
    """ported from build_sw4.apply_recipe (frames of moved / inserted gates cleared; kept frames retained)."""
    B = [list(e[:-1]) + [list(e[-1]) if e[-1] is not None else None] for e in w['B']]
    dele = set(); ins = collections.defaultdict(list)
    for m in moves:
        i = m['read_index']; e = B[i]; t = m['target']; a, b = m['coef']
        assert e[0] == 'add' and e[1] == t and [e[3], e[4]] == [a, b], ('recipe/word mismatch', m)
        if m['kind'] == 'h2r':
            assert e[2] == m['h']; pi = m['delete_preread_index']; g = B[pi]
            assert g[:5] == ['add', t, m['h'], -a, b], ('pre-read mismatch', m)
            B[i] = ['add', t, m['r'], a, b, []]; dele.add(pi)
        else:
            assert e[2] == m['r']; B[i] = ['add', t, m['h'], a, b, []]
            ins[m['insert_preread_before']].append(list(m['preread']) + [[]])   # [] = no stored frame (re-solved by frames.py)
    NB = []
    for i, e in enumerate(B):
        for g in ins.get(i, []): NB.append(g)
        if i in dele: continue
        NB.append(e)
    w2 = dict(w); w2['B'] = NB; w2['early_cleanup'] = [list(x) for x in w.get('early_cleanup', [])]
    return w2
def coef_mod(e):
    a, b = (e[3], e[4]) if e[0] == 'add' else (e[2], e[3]); return a % PR * pow(b % PR, PR - 2, PR) % PR
def b_state(w):
    """sparse rows mod p of the B segment as a linear map (identity start), only rows touched."""
    rows = {}
    for e in w['B']:
        for q in regs(e): rows.setdefault(q, {q: 1})
        q = coef_mod(e); t = e[1]
        if e[0] == 'scale': rows[t] = {k: x * q % PR for k, x in rows[t].items()}
        else:
            d = rows[t]
            for k, x in rows[e[2]].items():
                y = (d.get(k, 0) + q * x) % PR
                if y: d[k] = y
                else: d.pop(k, None)
    return rows
def same_b_map(w1, w2):
    a, b = b_state(w1), b_state(w2)
    return all(a.get(q, {q: 1}) == b.get(q, {q: 1}) for q in set(a) | set(b))
def strip(B): return [e[:-1] for e in B]
if __name__ == "__main__":
    # self-check: regenerate the published SW4 word (d232183f) from the promoted word (0390ec65) with our own move generator
    from paths import ROOT; VAL = str(ROOT / "research/complex-sw4-frame8-validation/platforms/macos")
    prom = json.load(gzip.open(VAL + "/promoted/FULL-WORD.json.gz")); sw4 = json.load(gzip.open(VAL + "/sw4/FULL-WORD.json.gz"))
    rec = json.load(open(ROOT / "research/gauge44-frames-x/construction/sw4/SW4-RECIPE-P6k4.json", encoding="utf-8"))
    print("promoted sha", hashlib.sha256(json.dumps(prom, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:8], "recipe input", rec['input_sha256'][:8], "| sw4 sha", hashlib.sha256(json.dumps(sw4, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:8], "recipe output", rec['output_sha256'][:8])
    pairs = copy_pairs(prom); print("copy pairs on promoted word:", len(pairs), "| with movable reads:", sum(1 for h, (r, i) in pairs.items() if movable_reads(prom, h, r, i)))
    # our moves for the four published pairs (full exchange of all movable reads)
    ours = []
    for h, r in [(461, 25), (581, 89), (591, 415), (603, 431)]:
        rr, i = pairs[h]; assert rr == r, (h, rr, r); mv = moves_for(prom, h, r, i, movable_reads(prom, h, r, i)); assert mv is not None; ours += mv
    theirs = rec['moves']
    key = lambda m: (m['kind'], m['read_index'], m['target'], tuple(m['coef']), m.get('delete_preread_index'), m.get('insert_preread_before'))
    print("moves ours", len(ours), "theirs", len(theirs), "| identical move sets:", sorted(map(key, ours)) == sorted(map(key, theirs)))
    w2 = apply_moves(prom, ours)
    print("B scalar program equals published SW4:", strip(w2['B']) == strip(sw4['B']), "| B map unchanged mod p:", same_b_map(prom, w2))
