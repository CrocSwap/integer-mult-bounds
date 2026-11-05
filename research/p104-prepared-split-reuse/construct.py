"""Remove two queries from PR5599's independent helper split.

Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
Ali Romman's fifteen independent splits and source word remain credited.
"""
from copy import deepcopy


def need(ok, why):
    if not ok:
        raise ValueError(why)


def construct(source):
    w = deepcopy(source)
    need(w['public'] == 750 and len(w['program']) == 25502, 'Exact source shape')
    need(w['initial'][573] == 3 and w['final'][573] == 603, 'Rank-two prefix helper')
    need(w['frames'][3] == [] and len(w['frames'][603]) == 2, 'Prefix target rank')
    replacements = {
        13670: (['MOVE',573,3,595,False],
                [['CLEAR',573,3],['INIT',573,595],
                 ['COPY',573,572,'1',595],['ADD',573,732,'-2',595]]),
        13691: (['MOVE',573,595,603,False],
                [['CLEAR',573,595],['INIT',573,603],
                 ['COPY',573,572,'1',603],['ADD',573,710,'2',603]])}
    out = [['INIT',573,3]]
    for i,event in enumerate(source['program']):
        if i in replacements:
            old,new = replacements[i]
            need(event == old,'Pinned paid site '+str(i))
            out.extend(deepcopy(new))
        else:
            out.append(deepcopy(event))
    out.append(['CLEAR',573,603])
    w.update(schema='p104-prepared-split-reuse/1',program=out,
             retired_public=[573],fields=758,
             independent_public=[r for r in range(750) if r != 573],
             owned_roles=[573]+list(range(750,758)))
    return w
