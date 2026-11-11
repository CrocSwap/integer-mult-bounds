# SPDX-License-Identifier: Apache-2.0
"""Literal all-input comparison, independent of the correction search and adjoint."""
from fractions import Fraction as Q


def forward(w, cache=None):
    n=w['public'];rows=[{r:Q(1)} for r in range(n)]+[{} for _ in range(w['owned_fields'])]
    captures=[]
    for t,e in enumerate(w['program']):
        op,r=e[:2]
        if op=='MOVE':continue
        if op=='COPY' and rows[r]:raise ValueError(f'Dirty COPY at {t}')
        if op in ('INIT','CLEAR'):rows[r]={}
        elif op=='SCALE':
            v=Q(e[2]);rows[r]={i:v*q for i,q in rows[r].items() if v*q}
        else:
            s=e[2];v=Q(e[3]);updated=rows[r].copy()
            for i,q in rows[s].items():
                c=updated.get(i,0)+v*q
                if c:updated[i]=c
                else:updated.pop(i,None)
            rows[r]=updated
            if r==cache:
                if rows[r]!={863:Q(1)}:raise ValueError(f'Cache is not pure x_863 at {t}')
                captures.append(e[-1])
    if cache is not None and captures!=[3,240]:raise ValueError('Both literal cache captures are required')
    if any(rows[n:]):raise ValueError('Uncleared owned output')
    return rows[:n]


def check(old,new):
    # The complete native gate already compares two independent all-column
    # implementations. Keep this direct predecessor/candidate comparison as
    # an executable certificate that needs neither numerical nor price code.
    if forward(old)!=forward(new,new['public']+old['owned_fields']):
        raise ValueError('Literal arbitrary-input endpoints differ')
    return {'status':'PASS_EXACT_NORMALIZED_ARBITRARY_INPUT_ENDPOINTS','rows':new['public'],
            'physical_scope':'Normalized rational comparison; phase and catalogue are checked separately.'},{}
