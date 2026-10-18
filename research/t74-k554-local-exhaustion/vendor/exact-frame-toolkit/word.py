"""word: load a gauge44-lineage FULL-WORD into frames.Graph (inline) and recount its paid profile exactly as the lineage's
independent recount does (research/pr699-frame-retiming/independent_frames.py, ported verbatim).
usage: python -B word.py FULL-WORD.json.gz   (prints the recount and the Graph's literal profile)"""
import gzip, json, collections, functools, sys, time
import frames as F
V = 112

@functools.lru_cache(None)
def span(vectors):
    points = {0}
    for vector in vectors: points |= {p ^ vector for p in points}
    return frozenset(points)
def dimension(points): return len(points).bit_length() - 1

def recount(word):
    v, helpers, h = (word['report'][key] for key in ('v', 'R', 'h')); n = 2 * v + helpers
    full = frozenset(range(512))
    cur = [frozenset((0, p)) for p in word['ports']] + [frozenset((0,))] * (n - v)
    for register, vectors in word['start_extra'].items(): cur[int(register)] = span(tuple(vectors))
    starts = list(cur); paid = collections.Counter(); centre = collections.Counter()
    def climb(register, target):
        assert cur[register] <= target, ('nonmonotone', register)
        rank = dimension(target) - dimension(cur[register])
        if rank: paid[rank] += 1
        cur[register] = target
    for section in ('A', 'B'):
        if section == 'B':
            levels = {int(t): span(tuple(u)) for t, u in word.get('target_levels', {}).items()}
            for register, vectors in zip(word['centers'], word['center_frames']):
                current = span(tuple(vectors))
                served = {levels.get(e[1] - v, frozenset((0,))) for e in word['cut'] if e[2] == register}
                for target in sorted(served, key=len, reverse=True):
                    assert target <= current
                    if target != current: paid[dimension(current) - dimension(target)] += 1; centre[dimension(current) - dimension(target)] += 1
                    current = target
        for event in word[section]:
            target = span(tuple(event[-1])); registers = event[1:3] if event[0] == 'add' else event[1:2]
            for register in registers: climb(register, target)
    endB = list(cur)
    for index, vectors in word['early_cleanup']:
        event = word['cleanup'][index]; registers = event[1:3] if event[0] == 'add' else event[1:2]
        for register in registers: climb(register, span(tuple(vectors)))
    ends = [full] * v + [frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0) for p in word['ports']] + [full] * helpers
    for register, vectors in word['helper_final'].items(): ends[int(register)] = span(tuple(vectors))
    for register, target in enumerate(ends): climb(register, target)
    widths = [dimension(ends[q]) - dimension(starts[q]) for q in range(2 * v, n)]
    return paid, centre, widths, starts, ends, endB

def inline(word, targets_empty):
    w = dict(word); full = [1 << i for i in range(9)]; R = word['report']['R']
    start = [[p] for p in word['ports']] + [[] for _ in range(V + R)]
    for q, U in word.get('start_extra', {}).items(): start[int(q)] = list(U)
    if not targets_empty:
        for t in range(V): start[V + t] = list(word.get('target_levels', {}).get(str(t), []))
    end = [list(full) for _ in range(V)] + [list(F.G.perp(p)) for p in word['ports']] + [list(full) for _ in range(R)]
    for q, U in word.get('helper_final', {}).items(): end[int(q)] = list(U)
    w['_start_frames'] = start; w['_final_frames'] = end
    w['_tail'] = [word['cleanup'][i][:-1] + [U] for i, U in word.get('early_cleanup', [])]
    return w

if __name__ == "__main__":
    word = json.load(gzip.open(sys.argv[1]))
    paid, centre, widths, starts, ends, endB = recount(word)
    print("audit recount paid:", dict(sorted(paid.items())), "| centre descents:", dict(sorted(centre.items())))
    print("report local_profile:", word['report']['local_profile'], "| match:", {int(k): v for k, v in word['report']['local_profile'].items()} == dict(paid))
    print("width inventory:", dict(sorted(collections.Counter(widths).items())))
    print("sections:", {s: len(word[s]) for s in ('A', 'cut', 'B', 'cleanup', 'precondition')}, "early_cleanup:", len(word['early_cleanup']), "start_extra:", len(word['start_extra']), "helper_final:", len(word['helper_final']), "centers:", len(word['centers']))
    for te in (False, True):
        t0 = time.time()
        try:
            g = F.Graph(inline(word, te), check_literal=True)
            H = g.profile(g.literal())
            tot = collections.Counter(H); tot.update(centre)
            print(f"targets_empty={te}: Graph literal paid {dict(sorted(H.items()))} (+centre = {dict(sorted(tot.items()))}) | equals audit: {dict(tot) == dict(paid)} | vars {len(g.var)} comps {len(g.components)} largest {len(g.components[0]) if g.components else 0} max dom {max((len(d) for d in g.dom.values()), default=0)} | {time.time()-t0:.1f}s")
        except Exception as e:
            print(f"targets_empty={te}: ERR {repr(e)[:400]} | {time.time()-t0:.1f}s")
