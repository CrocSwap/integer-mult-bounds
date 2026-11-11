# SPDX-License-Identifier: Apache-2.0
"""Independent normalized-event equivalence; physical maps are checked separately."""
from copy import deepcopy

def check(old,new):
    def scalar(w):return [e[:-1] for e in w['program'] if e[0]!='MOVE']
    def verify(w):
        if scalar(old)!=scalar(w):raise ValueError('Normalized event sequence differs')
        if w['initial']!=old['initial']:raise ValueError('Input boundary differs')
        if (w['public'],w['owned_fields'])!=(old['public'],old['owned_fields']):raise ValueError('Role inventory differs')
    verify(new)
    bad=deepcopy(new);i=next(i for i,e in enumerate(bad['program'])if e[0]=='ADD');bad['program'][i][-2]='0'
    try:verify(bad)
    except ValueError:control=True
    else:raise ValueError('Scalar mutation accepted')
    return {'status':'PASS_EXACT_NORMALIZED_EVENT_SEQUENCE','scalar_and_lifetime_events':len(scalar(new)),'arbitrary_cut_coordinates':new['public']+new['owned_fields'],'physical_scope':'Normalized equivalence only; every chart, phase and boundary checked by native and caller stages.'},{'changed_scalar_sequence_rejected':control}
