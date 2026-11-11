"""Preserve the inherited 24-bit scalar numerator contract by exact ADD splitting.
Temporal constructor retained byte-identically from #7143 with its author credits.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from temporal_construct import construct as temporal_construct

def normalize(word):
    program=[];changed=0
    for event in word['program']:
        if event[0] not in ('ADD','COPY','SCALE') or abs(Q(event[-2]).numerator).bit_length()<=24:
            program.append(event);continue
        assert event[0]=='ADD' and event[1]!=event[2], 'Only distinct-role ADD may be split additively'
        q=Q(event[-2]);a=Q(q.numerator//2,q.denominator);b=q-a
        assert a+b==q and a and b and max(abs(a.numerator).bit_length(),abs(b.numerator).bit_length())<=24
        program.extend([[*event[:-2],str(a),event[-1]],[*event[:-2],str(b),event[-1]]]);changed+=1
    assert changed==4, 'Exact four charged scalar refinements'
    word['program']=program
    return word

def construct(word,hit,paths):
    return normalize(temporal_construct(word,hit,paths))
