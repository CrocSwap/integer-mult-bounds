"""One cocharted helper split; no paid retiming.
Ali Romman's split/basis identity and CubeJerry's owned-field support are retained.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from split import split
from support import L

def prepare(word,hit):
    L.need(hit['paths']==[] and hit['paid_delta']=={},'No path or paid-profile edits')
    L.need(type(hit['cut']) is int and 0<hit['cut']<len(word['program']),'Interior source cut')
    spec={k:hit[k] for k in ('frame','pivot','ranks','a','b','c','d')}
    spec['cut_after']=hit['cut']-1
    return word,spec

def construct(word,hit):
    prepared,spec=prepare(word,hit)
    return split(prepared,spec)
