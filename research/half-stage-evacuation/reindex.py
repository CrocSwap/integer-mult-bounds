"""Transfer the fixed owner fill to PR2588's equal-width helper inventory.

Apache-2.0. OpenAI Codex assistance. Each provider gets a width-preserving
bijection of its helper indices. Times, owners, ports and offsets are unchanged.
"""
from collections import defaultdict, Counter
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parent/'source-partner-lifetimes'
def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)
def reindex(source, out):
    old = read(OLD/'evidence/eight-providers.json')
    new = read(HERE/'vendor/pr2588/PROVIDERS.json')
    maps = {}
    for pid in old:
        ow, nw = old[pid]['widths'], new[pid]['widths']
        assert Counter(ow) == Counter(nw)
        by_width = defaultdict(list)
        for h, width in enumerate(nw): by_width[width].append(h)
        used = Counter(); mapping = {}
        for h, width in enumerate(ow):
            mapping[h] = by_width[width][used[width]]; used[width] += 1
        assert sorted(mapping.values()) == list(range(422))
        assert all(ow[h] == nw[mapping[h]] for h in mapping)
        maps[pid] = mapping
    # Both old providers and both new providers have identical width arrays.
    # Keep the dispatch explicit, rather than depending on that coincidence.
    order = read(HERE/'evidence/CANDIDATE-ORDER.json')
    # Dispatch is by (stage,replica), unaffected by the timing permutation.
    dispatch_file = HERE/'vendor/pr2588/DISPATCH.json'
    dispatch = {(s,r): pid for s,r,pid in read(dispatch_file)}
    fill = read(source)
    for s,r,pid in fill['dispatch_overrides']: dispatch[s,r] = pid
    rows = []
    for row in fill['rows']:
        z = list(row); pid = dispatch[tuple(order[z[0]])]
        z[1] = maps[pid][z[1]]; rows.append(z)
    result = dict(fill, rows=rows)
    out.write_bytes(gzip.compress(json.dumps(result,separators=(',',':')).encode(),mtime=0))
    return maps
if __name__ == '__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    maps = reindex(a.source,a.out)
    print('PASS_WIDTH_PRESERVING_HELPER_BIJECTIONS',len(maps),flush=True)
