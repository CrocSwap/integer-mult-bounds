"""Checked simultaneous contact-free retiming, then attributed helper split.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
Extends #7105/#7107 retiming to an arbitrary finite cohort with an
exact declared total paid-histogram change; retains Ali Romman and CubeJerry split.
The complete signed invoice, not path cardinality, decides acceptance.
"""
from copy import deepcopy
from collections import Counter
from split import split
from support import L

def prepare(word,hit):
    paths=hit['paths'];L.need(1<=len(paths),'A nonempty finite retiming cohort')
    L.need(len({p['role']for p in paths})==len(paths),'Distinct retimed roles')
    f,cut=hit['frame'],hit['cut'];spaces=[L.span(x)for x in word['frames']];remove=set();paid_change=Counter()
    for p in paths:
        r,a,b=p['role'],p['old'],p['new']
        L.need(p['frame']==f and p['lo']<=cut<=p['hi'],'Cut in declared interval')
        actual=[i for i in range(p['lo'],p['hi'])if word['program'][i][1]==r]
        L.need(actual==p['moves'],'Every role event in interval is a relocated MOVE')
        L.need(all(not(e[0]in('ADD','COPY')and e[2]==r)for e in word['program'][p['lo']:p['hi']]),'No intervening source read')
        path=[word['program'][i]for i in actual]
        L.need(path and all(e[0]=='MOVE'and e[1]==r and e[4]==p['private']for e in path),'Only MOVE events')
        L.need(path[0][2]==a and path[-1][3]==b and all(x[3]==y[2]for x,y in zip(path,path[1:])),'Complete path')
        L.need(spaces[a]<=spaces[f]<=spaces[b]or spaces[b]<=spaces[f]<=spaces[a],'Nested intermediate frame')
        old_paid=Counter(abs(len(word['frames'][e[2]])-len(word['frames'][e[3]])) for e in path if spaces[e[2]]!=spaces[e[3]])
        new_paid=Counter(abs(len(word['frames'][x])-len(word['frames'][y])) for x,y in ((a,f),(f,b)) if spaces[x]!=spaces[y])
        L.need(old_paid==Counter(p['old_paid']) and new_paid==Counter(d for d in p['new_paid'] if d), 'Exact old and new path histogram declarations')
        paid_change.update(new_paid);paid_change.subtract(old_paid)
        L.need(not(remove&set(actual)),'Distinct removed events');remove.update(actual)
    L.need({r:c for r,c in paid_change.items() if c}=={int(r):c for r,c in hit['paid_delta'].items()}, 'Entire declared retiming paid delta')
    program=[];split_cut=None
    for i in range(len(word['program'])+1):
        if i==cut:
            for p in paths:
                if p['old']!=f:program.append(['MOVE',p['role'],p['old'],f,p['private']])
            split_cut=len(program)-1
            for p in paths:
                if f!=p['new']:program.append(['MOVE',p['role'],f,p['new'],p['private']])
        if i<len(word['program'])and i not in remove:program.append(deepcopy(word['program'][i]))
    out=deepcopy(word);out['program']=program;L.need(split_cut is not None,'Inserted cut')
    spec={k:hit[k]for k in('frame','pivot','ranks','a','b','c','d')};spec['cut_after']=split_cut
    return out,spec

def construct(word,hit):
    prepared,spec=prepare(word,hit);return split(prepared,spec)
