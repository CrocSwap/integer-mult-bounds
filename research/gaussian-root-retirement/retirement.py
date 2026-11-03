"""Return one Gaussian component before the two-stage suffix.

The word and binary suppliers are from PR6398. The independent boundary
uses the PR5599 dual-pair method. All extra operations are ordinary.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q

G = [['SCALE',4,'-1'],['LAMBDA',4,-1],['ADD',21,4,'1'],
     ['LAMBDA',4,1],['ADD',4,20,'1']]
J = [['ADD',4,2,'1'],['ADD',2,4,'-1'],['ADD',4,2,'1'],
     ['SCALE',2,'-1'],['SCALE',4,'-1'],['ADD',21,4,'1'],
     ['ADD',4,1,'1'],['LAMBDA',20,1],['ADD',4,20,'-1'],
     ['LAMBDA',20,-1],['ADD',4,21,'1']]


def inverse(events):
    out = deepcopy(list(reversed(events)))
    for e in out:
        e[-1] = (-e[-1] if e[0] == 'LAMBDA' else
                 str(1/Q(e[-1]) if e[0] == 'SCALE' else -Q(e[-1])))
    return out


def construct(source):
    word = deepcopy(source)
    if word['roles'] != 34 or word['stages'] != 18 or word['events'][328] != ['QUERY',20,21,-1]:
        raise ValueError('Exact source boundary')
    group, pivot, fresh, cut = (4,20,21),4,34,328
    if len({tuple(word['diagonal'][r][1:])for r in group}) != 1:
        raise ValueError('Equal stage targets on the boundary group')
    normalized = deepcopy(word['events'])
    for r in group:
        if word['diagonal'][r][0] == 1:
            normalized.append(['Q_POWER',r,-2])
        normalized.append(['LAMBDA',r,1])
    def rename(e):
        e=deepcopy(e)
        slots={'ADD':(1,2),'SWAP':(1,2),'SCALE':(1,),'LAMBDA':(1,),
               'Q_POWER':(1,),'QUERY':(1,2),'LOCAL':(2,3),'IDLE':(1,2),'IDLE_ONE':(1,)}[e[0]]
        for at in slots:
            if e[at] == pivot:
                e[at] = fresh
        return e
    word['events'] = inverse(G)+normalized[:cut+1]+J
    handoff = len(word['events'])-1
    word['events'] += [rename(e) for e in inverse(J)+normalized[cut+1:]+G]
    word['events'] += [['LAMBDA',r,-1]for r in group]
    word['roles'] += 1
    for r in group:
        word['diagonal'][r][0] = -1
    word['diagonal'][pivot] = [-1]+[0]*(word['stages']+1)
    word['diagonal'].append([0,*source['diagonal'][pivot][1:]])
    return word, {'cut_after':cut,'handoff_after':handoff,'pivot':pivot,'fresh':fresh,
                  'boundary':G,'middle':J,'group':list(group)}
