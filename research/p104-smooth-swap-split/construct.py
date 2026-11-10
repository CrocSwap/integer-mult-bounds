"""Six integer additions implement an attributed independent helper split.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from split import split
from support import L

def construct(word, witness):
    L.need(witness['paths'] == [], 'This witness has no retiming')
    spec = {k: witness[k] for k in ('frame', 'pivot', 'ranks', 'a', 'b', 'c', 'd')}
    spec['cut_after'] = witness['cut']-1
    return split(word, spec)
