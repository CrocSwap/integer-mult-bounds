"""Retiming within one contact-free interval, then a checked helper split.
OpenAI Codex for dillona; Ali Romman and CubeJerry's split method. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from split import split
from support import L

def prepare(word, hit):
    paths=hit['paths']; L.need(len(paths)==1,'Exactly one paid retiming')
    p=paths[0];r=p['role'];a,b,f=p['old'],p['new'],hit['frame'];cut=hit['cut']
    L.need(p['frame']==f and p['lo']<=cut<=p['hi'],'Cut in declared interval')
    actual=[i for i in range(p['lo'],p['hi']) if word['program'][i][1]==r]
    L.need(actual==p['moves'],'Every role event in interval is a relocated MOVE')
    L.need(all(not(e[0]in('ADD','COPY')and e[2]==r)for e in word['program'][p['lo']:p['hi']]),'No intervening source read')
    path=[word['program'][i]for i in actual]
    L.need(path and all(e[0]=='MOVE' and e[1]==r and e[4]==p['private']for e in path),'Only MOVE events')
    L.need(path[0][2]==a and path[-1][3]==b and all(x[3]==y[2]for x,y in zip(path,path[1:])),'Complete path')
    spaces=[L.span(x)for x in word['frames']]
    L.need(spaces[a]<=spaces[f]<=spaces[b] or spaces[b]<=spaces[f]<=spaces[a],'Nested intermediate frame')
    remove=set(actual);program=[];split_cut=None
    for i in range(len(word['program'])+1):
        if i==cut:
            if a!=f:program.append(['MOVE',r,a,f,p['private']])
            split_cut=len(program)-1
            if f!=b:program.append(['MOVE',r,f,b,p['private']])
        if i<len(word['program'])and i not in remove:program.append(deepcopy(word['program'][i]))
    out=deepcopy(word);out['program']=program
    L.need(split_cut is not None,'Retiming cut inserted')
    spec={k:hit[k]for k in ('frame','pivot','ranks','a','b','c','d')}
    spec['cut_after']=split_cut
    return out,spec

def construct(word,hit):
    prepared,spec=prepare(word,hit)
    return split(prepared,spec)
