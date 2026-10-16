# SPDX-License-Identifier: Apache-2.0
"""Generate path-free public evidence and the claim from actual complete receipts."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    need(not path.exists(), 'fresh generated public artifact')
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('native','admission','owners','moment','provider-premises'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    here=Path(__file__).resolve().parent
    native=read(args.native/'NATIVE-RECEIPT.json')
    result=read(args.admission/'RESULT.json')
    release_path=args.admission/'release/RELEASE-RECEIPT.json'
    release=read(release_path)
    verify=read(args.admission/'release/verify/RESULT.json')
    strict=args.admission/'release/verify/strict'
    admission=read(strict/'ADMISSION-CONTROLS.json')
    bit=read(strict/'BIT-CONTROLS.json')
    controller=read(strict/'global/audit/ASYNC-AUDIT.json')
    invoice=read(strict/'global/audit/PREFIX-AND-INVOICE.json')
    outer=read(args.admission/'package/outer/LEDGER.json')
    owner,moment=read(args.owners),read(args.moment)
    premises=read(args.provider_premises)
    previous=read(here/'PR2843-CLAIM.json')
    need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','full changed release')
    need(release['status']=='PASS_RELEASE' and sha(release_path)==result['release_receipt_sha256'],'release receipt binding')
    need(verify['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION','supplier complete verification')
    need(all(s['exit_code']==0 for s in result['stages']),'all complete adapter stages')
    need(native['fresh_current_provider_count']==native['fresh_retained_native_count']==2 and native['fresh_retained_parent'],'four fresh native chains and parent')
    need(result['native_receipt_sha256']==sha(args.native/'NATIVE-RECEIPT.json'),'native protocol binding')
    need(owner['status']=='PASS_INDEPENDENT_T_OWNER_CHRONOLOGY_MASKS' and len(owner['controls'])==7,'independent owner faults')
    need(moment['status']=='PASS_INDEPENDENT_EXACT_CANDIDATE_MOMENT' and len(moment['controls'])==5,'independent moment faults')
    need((owner['replicas'],owner['roles'],owner['live'],owner['physical'])==(134,492048,120064,120554),'complete constructed stock')
    kappa=Q(result['kappa'])
    need(kappa==Q(result['kappa_decimal'])==Q(release['kappa_decimal'])==Q(moment['proposed_outer_target'])>Q(previous['kappa']),'exact higher headline')
    need(Q(result['complex_lower'])==Q(moment['complex_lower']),'independent primitive bound')
    need(result['profile']==owner['profile']==json.loads((here/'data/PROFILE.json').read_bytes()),'actual complete paid profile')
    need(len(admission['rejected_controls'])==119 and len(bit['rejected_controls'])==12,'complete admission and BIT faults')
    need(controller['mutation_controls_run'] and controller['complex_hosted_residuals']==492048,'actual controller controls and owners')
    row=outer['rows']['struct_boundary_radix_union']
    need(len(row['strict_checks'])==63 and all(Q(v['rational'])>0 for v in row['strict_checks'].values()),'63 strict exact outer inequalities')
    rejected=outer['rejecting_controls']['struct_boundary_radix_union']
    need(len(rejected)==17 and all(v and any(Q(x['rational'])<=0 for x in v.values()) for v in rejected.values()),'17 semantic outer rejections')
    need(Q(row['kappa']['rational'])==kappa,'actual outer bound')
    need(premises['status']=='PASS_PR2833_ACTUAL_BLOCK_NORM_PROVIDER_PREMISES' and len(premises['semantic_faults_rejected'])==4,'actual native norm premise faults')
    bn=invoice['blocknorm']
    need(bn['status']=='PASS_TENSOR_BLOCK_NORM_CERTIFICATE' and bn['replicas']==134 and bn['max_active_depth']==18,'global block norm')
    need((verify['prefix_bits'],verify['charged_prefix_bits'],verify['physical_row_coefficient'])==(1453,2048,19547),'actual precision and row')
    need(1453==bn['actual_prefix_bits'] and bn['required_reserve_bits']==1511 and bn['stock_l2_bits']==1323,'full-stock norm conversion')
    for name,key in (('FILL.json.gz','fill_sha256'),('ORDER.json','order_sha256'),('DISPATCH.json','dispatch_sha256')):
        need(sha(here/'data'/name)==result[key],'release actual constructed payload')
    claim={
        'status':'PASS_CONDITIONAL_T134_BLOCK_NORM_COMPOSITION',
        'kappa':str(kappa),'kappa_decimal':result['kappa_decimal'],
        'replicas':134,'complex_lower':result['complex_lower'],'complex_upper':moment['complex_upper'],
        'supplier_kappa':verify['kappa'],'supplier_kappa_decimal':verify['kappa_decimal'],
        'comparison_pr':2843,'comparison_head':result['comparison_head'],
        'comparison_claim_sha256':sha(here/'PR2843-CLAIM.json'),
        'comparison_kappa':previous['kappa'],'exact_gain':str(kappa-Q(previous['kappa'])),
        'live':120064,'physical':120554,'helper_roles':492048,'rank_mass':owner['rank_mass'],
        'scope':'Conditional finite construction and modern outer arithmetic. Inherited all-size/compiler/source-access/hosting/precision/tape/recovery/BIT/analytic assumptions remain. No selected-frontier or full theorem claim.',
    }
    write(here/'CLAIM.json',claim)
    validation={
        'status':'PASS_OBSERVED_COMPLETE_T134_RELEASE',
        'kappa':str(kappa),'kappa_decimal':result['kappa_decimal'],
        'source_heads':{'native':'e9307b48d7d1b690939935ecef0f8e524e6d92f4',
                        'norm':'2fdd289fcd0896f4691f9dd78a8bf1511573e434','comparison':result['comparison_head']},
        'fresh_native_chains':4,'fresh_retained_parent':True,'explicit_authenticated_native_reuse_for_changed_release':True,
        'complete_stages':[{'name':s['name'],'exit_code':s['exit_code'],'script_sha256':s['script_sha256']} for s in result['stages']],
        'controls':{'admission':119,'bit':12,'controller':len(controller['mutations_rejected']),
                    'independent_owner':verify['controls']['independent_owner'],'geometry':verify['controls']['geometry'],
                    'independent_geometry':7,'independent_moment':5,'native_norm_premise':4,'outer':17},
        'outer_strict_inequalities':63,'actual_blocknorm':bn,
        'source_manifest_sha256':result['source_manifest_sha256'],
        'derived_runtime_manifest_sha256':result['package_manifest_sha256'],
        'observed_receipt_sha256':{'native':sha(args.native/'NATIVE-RECEIPT.json'),
                                   'complete_result':sha(args.admission/'RESULT.json'),'release':sha(release_path),
                                   'independent_owners':sha(args.owners),'independent_moment':sha(args.moment),
                                   'native_premises':sha(args.provider_premises)},
        'coverage':'Actual local source/frame/phase/wrapper checks, retained parent, complete allocation/controller/invoice/bootstrap and modern outer release. No new Lean kernel run, hosted CI or maintainer acceptance claimed.',
    }
    args.out.mkdir(parents=True,exist_ok=False)
    write(args.out/'VALIDATION.json',validation)
    write(args.out/'NATIVE-PREMISES.json',premises)
    print(validation['status'],claim['kappa_decimal'])


if __name__=='__main__':
    main()
