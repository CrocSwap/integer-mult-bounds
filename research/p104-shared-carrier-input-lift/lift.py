"""Shared-carrier input lift: exact deterministic edit of the #6805 native word.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
The input-lift move class (a helper born at a later frame, its response delivered
there, then repaired) follows the #6349 line of work; the retimed
helper-split word being edited is by @CubeJerry (#6805) with OpenAI assistance.
LIFT.json lists every edit; every bound source event is asserted before use.
"""
from copy import deepcopy
from fractions import Fraction as Q
import native as N

def apply(source,lift):
    word=deepcopy(source);program=source['program']
    N.need(len(program)==18622 and word['public']==772,'Pinned #6805 program shape')
    for c in lift['initial']:
        r=c['role']
        N.need(word['initial'][r]==c['from']==3,'Source helper is born at frame 3')
        N.need(word['final'][r]in(127,246),'Source helper ends at a full frame')
        N.need(r not in set(word['live'])|{x+112 for x in word['live']},'Lifted role is an independent helper')
        N.need(len(word['frames'][c['to']])<len(word['frames'][word['final'][r]])and set(word['frames'][c['to']]).issubset(span_of(word['frames'][word['final'][r]])),'Birth frame lies inside the helper exit')
        word['initial'][r]=c['to']
    out=[];pos=0
    for edit in lift['edits']:
        at,old,new=edit['at'],edit['delete'],edit['insert']
        N.need(at>=pos,'Edits are ordered and disjoint')
        out.extend(program[pos:at])
        N.need(program[at:at+len(old)]==old,('Bound deleted source events',at))
        nxt=at+len(old)
        N.need((program[nxt]if nxt<len(program)else None)==edit['next'],('Bound following source event',at))
        for e in new:
            if e[0]in('ADD','SCALE'):N.need(Q(e[-2])!=0,'Nonzero coefficient')
        out.extend(new);pos=nxt
    out.extend(program[pos:])
    word['program']=out
    return word

def span_of(basis):
    return N.span(basis)
