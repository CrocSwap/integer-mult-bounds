"""Owned resynthesis adapter derived from Cao Yifan / Cinna Davis native walker.
Apache-2.0; substantial OpenAI assistance. Source notices retained in proof.
"""
from copy import deepcopy
def roles(e):
    if e[0] == 'scalar':
        g = e[1]
        return [r[1] for r in (g[1:3] if g[0] in ('add', 'copy') else g[1:2]) if r[0] == 'L']
    return [e[1][1]] if e[0] == 'warp' else []

def synthesize(F, c, program):
    current = c['start'][:]
    spaces = [F.span(b) for b in c['frames']]
    out = []

    def climb(r, new):
        old = current[r]
        if old == new:
            return
        F.need(spaces[old] < spaces[new], f"Positive reconstructed transport role={r} old={old} new={new} dimensions={len(c['frames'][old])},{len(c['frames'][new])}")
        out.append(['climb', 'warp_retimed', r, old, new, len(c['frames'][new]) - len(c['frames'][old])])
        current[r] = new
    for e in program:
        if e[0] == 'climb':
            continue
        if e[0] == 'scalar':
            for r in roles(e):
                climb(r, e[2])
        elif e[0] == 'warp':
            climb(e[1][1], e[3])
            current[e[1][1]] = e[4]
        out.append(deepcopy(e))
    for r, new in enumerate(c['final']):
        climb(r, new)
    return out
