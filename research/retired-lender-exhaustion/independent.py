"""Independent per-role timeline and binary-elimination necessary census.

No imports from the set-span auditor or any predecessor executable.
"""


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length()-1
            if bit not in pivots:
                pivots[bit] = value; break
            value ^= pivots[bit]
    return len(pivots)


def census(word):
    active = sorted(set(range(704))-set(word['removed']))
    sequence = []
    def owners(e): return e[1:3] if e[0] == 'add' else e[1:2]
    for i,e in enumerate(word['A']):
        frame = e[4] if e[0] == 'warp' else e[-1]
        sequence.append((2*i+1,owners(e),rank(frame)))
    base = 2*len(word['A'])
    for i,e in enumerate(word['B']): sequence.append((base+2*i+1,owners(e),rank(e[-1])))
    for i,r,_,_,dest in word['warps']: sequence.append((base+2*i,[r],rank(dest)))
    boundary = base+2*(len(word['B'])+1)
    for i,e in enumerate(word['restore']): sequence.append((boundary+i,owners(e),rank(e[-1])))
    sequence.sort(key=lambda x:x[0])
    timeline = {r:[(t,d) for t,rs,d in sequence if r in rs] for r in active}
    forbidden = set(word['centers']) | {r for s in ('precondition','compensation','cut') for e in word[s] for r in owners(e)}
    forbidden |= {r-704 for e in word['cleanup'] for r in owners(e) if r>=704}
    forbidden |= set(map(int,word['helper_final'])) | {e[1] for e in word['warps']}
    helpers = [r for r in active if r>=224 and r not in forbidden and timeline[r] and base<=timeline[r][0][0]<boundary]
    lenders = [r for r in active if not 112<=r<224 and r not in word['centers']]
    out = []
    for h in helpers:
        for lender in lenders:
            if lender==h: continue
            last,dimension = timeline[lender][-1] if timeline[lender] else (-1,1 if lender<112 else rank(word['start_extra'].get(str(lender),[])))
            if last>=timeline[h][0][0] or dimension>timeline[h][0][1]:continue
            end = rank(word['helper_final'][str(lender)]) if str(lender) in word['helper_final'] else 9
            if timeline[h][-1][1] <= end:out.append([h,lender])
    return out
