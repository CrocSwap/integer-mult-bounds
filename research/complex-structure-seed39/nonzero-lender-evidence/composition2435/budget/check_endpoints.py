#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact base-two/atanh check of composed428 moment endpoints.

Profile identities and owner geometry are separate pinned evidence. This
finite arithmetic check is not a proof of the all-size recurrence theorem.
Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ENGINE=HERE.parents[2]/'face-hoist-evidence/budget/inherited/vendor/base_two_moment.py'
PIN='aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098'
PROFILE_PIN='4988c001824ce2228e1048263390d8be7d26bd4a565cd8cfd6c4dc34cdb75dd8'
ENDPOINTS={'native_no_bad':Q('0.001699160892139825160028'),'inherited_bad':Q('0.001699160889218527231563')}

def need(ok,msg):
    if not ok:raise ValueError(msg)

def main():
    need(hashlib.sha256(ENGINE.read_bytes()).hexdigest()==PIN,'engine pin')
    raw=(HERE/'RESTRICTED-PROFILE.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest()==PROFILE_PIN,'profile pin')
    H={int(r):n for r,n in json.loads(raw).items()}
    need(73*66304-sum(r*n for r,n in H.items())==23680,'rank deficit')
    spec=importlib.util.spec_from_file_location('composition_independent_moment',ENGINE)
    engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    def moment(profile,b,bad):
        lo,hi=engine.moment(73,66304,list(profile.items()),b)
        if bad:
            lower,upper=engine.log_bounds(Q(73))
            lower=engine.exp_bounds(b*lower)[0];upper=engine.exp_bounds(b*upper)[1]
            charge=Q(32*73*sum(profile.values()),10**16*66304)
            lo+=charge*lower;hi+=charge*upper
        return lo,hi
    results={}
    for label,lower in ENDPOINTS.items():
        upper=lower+Q(1,10**24);bad=label=='inherited_bad'
        a=moment(H,lower,bad);b=moment(H,upper,bad)
        need(a[1]<1<b[0],'endpoint signs')
        changed=dict(H);changed[1]+=1
        need(moment(changed,lower,bad)[0]>1,'one unpaid rank1 child detected')
        need(moment(H,upper-2*Q(1,10**24),bad)[1]<1,'incorrect upper endpoint detected')
        results[label]=dict(lower=str(lower),upper=str(upper),lower_residual_upper=str(a[1]-1),upper_residual_lower=str(b[0]-1))
    receipt=dict(status='PASS_INDEPENDENT_BASE_TWO_COMPOSED428_MOMENT_BRACKETS',
        engine_sha256=PIN,profile_sha256=PROFILE_PIN,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        endpoints=results,controls=['one extra rank1 child rejects each lower endpoint','upper endpoint shifted down2e-24 rejects each upper sign'],
        scope='Independent exact rational arithmetic on the pinned full global profile, including the explicitly inherited bad envelope when requested. No native/global physical admission or modern outer-transfer claim.')
    (HERE/'INDEPENDENT-ENDPOINTS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])

if __name__=='__main__':main()
