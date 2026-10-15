#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Exact target-vector transport; no physical/native admission is implied.

For a final correction c, compute the unique simultaneous correction at every
boundary of a target-affine gate word. Non-target source terms cancel from the
difference. Transport through target mixing, not only target scales.
"""
from fractions import Fraction as Q


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def step(c, gate, targets, inverse=False):
    out=dict(c)
    kind=gate[0]
    if kind not in ('add','scale'):
        return out
    t=gate[1]
    if kind=='add':
        s=gate[2]
        need(not (s in targets and t not in targets), 'non-target reads target')
        if t in targets and s in targets:
            a=Q(gate[3],gate[4])*(-1 if inverse else 1)
            out[t]=out.get(t,Q(0))+a*out.get(s,Q(0))
    elif t in targets:
        a=Q(gate[2],gate[3]);need(a!=0,'zero target scale')
        out[t]=out.get(t,Q(0))*(1/a if inverse else a)
    return {t:a for t,a in out.items() if a}


def suffix_corrections(gates, final, targets):
    need(set(final)<=set(targets),'correction outside targets')
    c={t:Q(a) for t,a in final.items() if a}
    vectors=[c]
    for g in reversed(gates):
        c=step(c,g,targets,inverse=True)
        vectors.append(c)
    return list(reversed(vectors))


def verify_transport(gates, final, targets):
    vectors=suffix_corrections(gates,final,targets)
    need(len(vectors)==len(gates)+1,'missing boundary')
    for i,g in enumerate(gates):
        need(step(vectors[i],g,targets)==vectors[i+1],f'transport boundary {i}')
    need(vectors[-1]=={t:Q(a) for t,a in final.items() if a},'wrong final')
    return vectors


def controls():
    # A correction on source target 11 is mixed into target 10 by an ADD;
    # a scalar-only backward transport would miss this exact obstruction.
    targets={10,11};gates=[['add',10,11,3,2,[]],['scale',11,-2,1,[]]]
    final={10:Q(5),11:Q(4)}
    v=verify_transport(gates,final,targets)
    need(v[0]=={10:Q(8),11:Q(-2)},'known noncommuting two-target example')
    wrong=dict(v[0]);wrong[10]=Q(5)
    for g in gates:wrong=step(wrong,g,targets)
    need(wrong!=final,'ignored-mixing control accepted')
    try:step({10:Q(1)},['add',0,10,1,1,[]],targets)
    except RuntimeError:pass
    else:raise RuntimeError('target read into non-target not rejected')
    return {'noncommuting_target_mix':'rejected_scalar_only_transport','non_target_read':'rejected'}


if __name__=='__main__':
    need(__debug__,'assertions must remain enabled')
    controls()
    print('PASS_EXACT_TARGET_TRANSPORT_CONTROLS')
