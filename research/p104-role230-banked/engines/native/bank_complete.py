#!/usr/bin/env python3
"""Bind the proved physical bank map catalogue and both dense graph receipts."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bank_phase as phase
from custody import need,read,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',type=Path,required=True)
    p.add_argument('--dense-first',type=Path,required=True)
    p.add_argument('--dense-second',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    pa=args.phase/'RESULT.json'
    data=read(pa)
    pin=sha(pa.read_bytes())
    need(data['status']=='PASS_PAIRED_BANK24_EXACT_NATIVE_MAPS' and data['source_head']==phase.HEAD
         and data['pivot_manifest_sha256']==phase.PIVOTS and data['forward_union']==3025
         and data['fresh_maps_512_each_direction']==19 and data['main_boundary_pairs']==104
         and data['hosted_correspondences']==96,'complete paired graph map/port denominator')
    for name,digest in data['artifact_sha256'].items():
        need(sha((args.phase/name).read_bytes())==digest,'complete catalogue artifact remains immutable')
    receipts = {}
    for pth,prime,seed in ((args.dense_first,1000000009,11),(args.dense_second,998244353,37)):
        path=pth/'RESULT.json'
        result=read(path)
        need(result['status']=='PASS_PAIRED_BANK24_ACTUAL_HELD_ARRAYS' and result['phase_sha256']==pin
             and result['prime']==prime and result['seed']==seed and result['graph_pins']==data['graph_pins']
             and result['exact_caller_sha256']==phase.DEC_CALLER,'same exact graph and actual finite tape orientation')
        need(result['main_outputs']==400 and result['positive_helper_outputs']==1101 and result['width']==512
             and len(result['exact_column_links'])==8,'complete actual width and output incidence')
        for side,ref in (('peer','source'),('candidate','candidate')):
            one=result[side]
            need(one['terminal_arrays_sha256']==result['independent_expected_sha256'] and
                 one['distinct_scientific_held_arrays']==15286 and one['independent_entry_banks']==1501
                 and one['paid_slots']==6142 and one['active_nodes']==7643 and one['terminal_rows']==1501
                 and one['local_scalar_terms']==data[ref]['local_terms'],'actual bank VM extent')
        faults=result['actual_negative_controls']
        if prime==1000000009:
            need(set(faults)=={'quarter phase','same-price sign'} and
                 all(v['injected_slot']==97471 and v['changed_public_roles'] for v in faults.values()),
                 'actual role-230 rejecting physical controls')
        receipts[str(prime)]={'sha256':sha(path.read_bytes()),'seed':seed,'borrowed_inputs_sha256':result['input_sha256'],
                              'terminal_arrays_sha256':result['independent_expected_sha256'],'faults':faults}
    phase.write(args.out,{'status':'PASS_PAIRED_BANK24_NATIVE_QUALIFICATION_COMPONENT',
                          'phase_sha256':pin,'graph_pins':data['graph_pins'],'source_head':phase.HEAD,
                          'pivot_manifest_sha256':phase.PIVOTS,'caller_sha256':phase.DEC_CALLER,
                          'source':data['source'],'candidate':data['candidate'],'forward_union':3025,
                          'diagnostic_only_pivot_orientations':5,'fresh_512_maps_each_direction':19,
                          'main_boundary_pairs':104,'hosted_correspondences':96,'dense':receipts,
                          'scope':'Actual scheduled banked native map bodies and two complete finite held-array projections. All-width physical extent, ordinary and outer are independent components.'})


if __name__=='__main__':
    main()
