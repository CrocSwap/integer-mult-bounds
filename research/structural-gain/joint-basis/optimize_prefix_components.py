#!/usr/bin/env python3
"""Select disjoint exact kernel components, then reconstruct the paid word.

The floating MILP is discovery only. Scalar relations and complete frame
profiles are checked exactly in the reconstructed output.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--screen',type=Path,required=True)
    ap.add_argument('--gk-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    assert __debug__ and not a.out.exists()
    sys.path.insert(0,str(a.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V=co.V=112;g.DATA=co.DATA=7168
    report=json.loads((a.screen/'SEARCH.json').read_text());records=report['components']
    base=json.loads(gzip.decompress((a.screen/'UNLOCKED-WORD.json.gz').read_bytes()))
    b=.00160337695754026285
    shadows={4:-7.734887784713593,5:-9.567009138574441,7:-5.83661301196174,
             8:-3.9714149486553896,9:-2.1062168853490393}
    costs={r:r*math.expm1(b*math.log(73/r))/b for r in range(1,10)}
    objective=[sum(costs[int(r)]*n for r,n in rec['profile_delta'].items())+
               rec['nullity']*(shadows[9-len(rec['frame'])]-shadows[9]) for rec in records]
    matrix=lil_matrix((504,len(records)))
    for i,rec in enumerate(records):
        for h in rec['helpers']:matrix[h,i]=1
    result=milp(np.asarray(objective),integrality=np.ones(len(records)),bounds=Bounds(0,1),
                constraints=LinearConstraint(matrix.tocsr(),0,1),options={'time_limit':60})
    assert result.x is not None
    chosen=[i for i,x in enumerate(result.x) if x>.5]
    assert np.max(matrix@np.asarray([int(i in chosen)for i in range(len(records))]))<=1
    word=copy.deepcopy(base);gates=[];predicted=g.profile(base)
    for i in chosen:
        rec=records[i];predicted.update({int(r):n for r,n in rec['profile_delta'].items()})
        for change in rec.get('frame_changes',[]):
            event=word[change['section']][change['index']]
            event[-1]=list(g.basis(list(event[-1])+change['frame']))
        for p in rec['pivots']:
            word['start_extra'][str(p+224)]=rec['frame']
            for d,q in rec['coefficients'][str(p)].items():
                q=-Q(q);gates.append(['add',int(d)+224,p+224,q.numerator,q.denominator,rec['frame']])
    word['A']=gates+word['A']
    word['cleanup']=[g.inverse(e,g.FULL)for e in reversed(word['A']+word['B'])if not 112<=e[1]<224]
    profile=g.profile(word)
    if not report.get('raised_first_frames'):
        assert profile==+predicted
    C=g.responses(word);assert all(not C[int(r)-224]for r in word['start_extra'])
    widths=co.widths_of(word)
    word['report'].update(local_profile=dict(profile),local_rank_mass=sum(r*n for r,n in profile.items()),
                         entrance_rank=sum(9-w for w in widths),entering_helpers=sum(w<9 for w in widths),
                         width_inventory=dict(Counter(widths)))
    a.out.mkdir(parents=True);(a.out/'FULL-WORD.json.gz').write_bytes(g.dump(word))
    receipt=dict(status='PASS_EXACT_DISJOINT_JOINT_PREFIX_CONSTRUCTION',
                 screen_sha256=hashlib.sha256((a.screen/'SEARCH.json').read_bytes()).hexdigest(),
                 selected_components=chosen,profile_after=dict(profile),widths_after=dict(Counter(widths)),
                 ordered_widths=widths,inserted_prefix_gates=len(gates),
                 all_entering_response_columns_zero=True,solver_status=int(result.status),
                 shared_frame_profile_delta={r:profile[r]-predicted[r]for r in set(profile)|set(predicted)
                                             if profile[r]!=predicted[r]},
                 solver_message=result.message,mip_gap=float(result.mip_gap),
                 floating_reduced_cost_delta=float(result.fun),
                 scope='Disjoint component choices only. Floating dual is a discovery objective; '
                       'exact literal scalar/frame checks pass. Full native, phase and hosting remain separate.')
    (a.out/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items()if k!='ordered_widths'},indent=2))


if __name__=='__main__':main()
