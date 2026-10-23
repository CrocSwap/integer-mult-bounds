"""Arithmetic-only cross-check of the seven disclosed PR320 stage kappas."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import json
import reproduce_p10 as b
EXPECTED=['0.000764230861320245','0.000765146115390441','0.000765802240659923','0.000767751918266997','0.000768386813092527','0.000768798619422518','0.000769198971896986']

def run():
    final,receipt=b.final_profile();helper=Counter(receipt['base']['histogram']);report=[]
    deltas=[('base',{})]+[(name,row['delta']) for name,row in receipt['stages'].items()]
    for (name,delta),expected in zip(deltas,EXPECTED):
        helper.update(delta);profile=Counter({r:5*n for r,n in helper.items() if n});profile.update({r:1920 for r in (4,19,38,42)})
        W=F(b.mass(profile)+2040,100);root=b.bracket(profile,100,W);outer=b.assembly(root['lower'])
        assert outer['kappa']==F(expected),(name,outer['kappa'],expected)
        report.append(dict(stage=name,unreplicated_stock=W,local_histogram=b.clean(helper),bit_root=root['lower'],kappa=outer['kappa'],kappa_decimal=outer['kappa_decimal']))
    return dict(status='PASS_ALL_SEVEN_DISCLOSED_STAGE_KAPPAS',physical_admission=False,stages=report)
if __name__=='__main__':
    r=run();(b.HERE/'stage-root-receipt.json').write_text(json.dumps(b.ae.serial(r),indent=2)+'\n');print(json.dumps(b.ae.serial(r),indent=2))
