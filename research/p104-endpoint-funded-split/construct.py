"""Materialize a bounded endpoint nomination; no acceptance claim.

Retains Ali Romman, CubeJerry, Matarener and dillona's split/retiming methods.
Rohan Arun with OpenAI Codex assistance. Apache-2.0.
"""
import argparse, copy, gzip, json
from collections import Counter
from pathlib import Path
from support import L
from split import split
from retime import prepare

def construct(source, witness):
    word, hit = copy.deepcopy(source), copy.deepcopy(witness)
    prefix=[]
    for r in hit.get('extend_inputs',[]):
        new,old=hit['group'][0],word['initial'][r]
        L.need(L.span(word['frames'][new]) < L.span(word['frames'][old]),'Strict input extension')
        prefix.append(['MOVE',r,new,old,False]);word['initial'][r]=new
    if prefix:
        word['program']=prefix+word['program'];offset=len(prefix);hit['cut']+=offset
        for p in hit.get('paths',[]):
            p['lo']+=offset;p['hi']+=offset;p['moves']=[i+offset for i in p['moves']]
    for r in hit.get('elevate',[]):
        new,old=hit['group'][1],word['final'][r]
        L.need(L.span(word['frames'][old]) < L.span(word['frames'][new]),'Strict output extension')
        word['program'].append(['MOVE',r,old,new,False]);word['final'][r]=new
    if hit.get('paths'):
        d=Counter()
        for p in hit['paths']:
            d.update(r for r in p['new_paid'] if r);d.subtract(p['old_paid'])
        hit['paid_delta']={r:v for r,v in d.items() if v}
        word,spec=prepare(word,hit)
    else:
        spec={k:hit[k] for k in ('frame','pivot','ranks','a','b','c','d')}
        spec['cut_after']=hit['cut']-1
    return split(word,spec)

