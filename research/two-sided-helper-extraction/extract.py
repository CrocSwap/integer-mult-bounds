# SPDX-License-Identifier: Apache-2.0
"""Two-sided dirty-helper extraction on the pinned PR2894 providers.

Jeremy Diviney with OpenAI Codex assistance. Exact frame accounting and inverse
cleanup are credited to Jeremy Kothe's preload_move.py (PR2894). This producer
is pure; the independent auditor derives the endpoint from its literal gates.
"""
import collections
import copy
from fractions import Fraction as Q
import preload_move as pm

ALLOWED = {'A', 'restore', 'helper_final', 'compensation', 'report', 'cleanup'}
PROFILE = {'1':2407,'2':640,'3':262,'4':128,'5':26,'8':8}
INVENTORY = {'4':26,'5':2,'7':62,'8':87,'9':231}

def apply(word, transform):
    h = transform['helper']
    before, after = transform['before'], transform['after']
    pm.require(h == 408 and str(h) not in word['helper_final'], 'fresh helper408')
    pm.require(str(h) not in word['start_extra'], 'zero entrance')
    pm.require(len(before)==24 and len(after)==3, 'declared literal gate counts')
    frame = after[0][-1]
    pm.require(pm.basis(frame)==(256,128,64,36,20,8,2,1), 'hyperplane52')
    protected = set(map(int,word['helper_final'])) | set(map(int,word['start_extra'])) | {c['source'] for c in word['initial_corrections']}
    for g in before:
        pm.require(g[0] in ('add','scale') and g[-1]==[], 'scalar zero-frame input change')
        roles = g[1:3] if g[0]=='add' else g[1:2]
        pm.require(all(224<=r<704 and r not in protected and r not in word['removed'] for r in roles), 'only available unprotected helpers')
    for g in after:
        pm.require(g[0]=='add' and g[-1]==frame, 'declared terminal frame')
    x=copy.deepcopy(word);n=x['prelude_events']
    x['A']=x['A'][:n]+copy.deepcopy(before)+x['A'][n:]
    x['restore']+=copy.deepcopy(after);x['helper_final'][str(h)]=list(frame)
    C=collections.defaultdict(dict)
    for g in x['compensation']:C[g[2]][g[1]]=C[g[2]].get(g[1],Q(0))+Q(g[3],g[4])
    # The preceding compensation becomes C*S; reverse literal gate order
    # computes right multiplication without trusting stored endpoint rows.
    for g in reversed(before):
        if g[0]=='scale':C[g[1]]={t:a*Q(g[2],g[3]) for t,a in C[g[1]].items()}
        else:
            t,s=g[1:3];c=Q(g[3],g[4])
            for target,a in C[t].items():C[s][target]=C[s].get(target,Q(0))+c*a
    x['compensation']=[['add',t,r,a.numerator,a.denominator,[]] for r,col in sorted(C.items()) for t,a in sorted(col.items()) if a]
    pm.require(not any(g[2]==h for g in x['compensation']), 'new cold helper has no target compensation')
    profile,inventory=pm.frame_report(x)
    pm.require(profile==PROFILE and inventory==INVENTORY, 'actual local profile/inventory')
    x['report']['local_profile']=profile;x['report']['width_inventory']=inventory
    z=copy.deepcopy(x);z['A']=z['A'][n:]
    x['cleanup']=pm.derive_cleanup(z,set(map(int,x['helper_final'])))
    pm.require({k for k in word if word[k]!=x[k]}==ALLOWED, 'exact changed sections')
    return x
