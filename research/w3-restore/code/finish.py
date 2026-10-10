#!/usr/bin/env python3
"""Cross-bind fresh source, complex, scalar, geometry, banks, price and invoice."""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,hashlib,json,struct

def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ceilq(x):return (x.numerator+x.denominator-1)//x.denominator

def finish(out):
 out=Path(out);base=read(out/'baseline/verification.json');complex=read(out/'COMPLEX-GUARD.json');bank=read(out/'BANK.json');price=read(out/'PRICE.json');inv=read(out/'INVOICE.json');cols=read(out/'COLUMNS.json');compact=read(out/'COMPACT-COLUMNS.json');binding=read(out/'candidate/SOURCE-BINDING.json');legal=read(out/'LEGALITY.json')
 assert base['status']=='PASS_IMMUTABLE_PARITY_REGAUGED_SOURCE527_FIVE_STAGE_BANKED_CONSTRUCTION' and base['inputs_unchanged']
 assert set(base['fresh_stages'])=={'raw','bit','scalar','primes','banks','complex','math','finite'} and len(base['negative_controls'])==8
 assert base['manifest_sha256']=='86e8bc5182079c00877077c8e4c7b2690ba2486bec385c0857f1794cd2e6bedb'
 log=(out/'logs/complex-source.log').read_text();assert 'PASS expected.json reproduced' in log
 assert complex['status']=='PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION'
 cg=complex['precision_guard'];assert cg['status']=='PASS_FRESH_EXACT_COMPLEX_GUARD' and cg['retained_row_coefficient']==20161 and cg['new_coefficient_recipes_checked']==40
 assert cg['physical_row_overcharge_coefficient']<20161 and cg['complete_local_group_upper']<2**48 and all(cg['controls'].values())
 expected=read(Path(__file__).resolve().parents[1]/'vendor/pr256/certificate/expected.json')['pr233']
 assert complex['five_stage_histogram']==expected['five_stage']['child_histogram'] and price['complex_saving']=='7547/10000000'
 assert cols['formal_columns_checked']==23627 and compact['formal_columns_checked']==22172
 for c in (cols,compact):
  assert c['copied_center_original_source_immutable'] and c['fresh_center_copies']==120 and c['payload_prefix_bits']==94
  assert len(c['negative_controls'])==6 and all(x['rejected'] for x in c['negative_controls'])
 assert binding['active_helpers']==15132 and len(binding['freed_roles'])==1455
 assert legal['all_final_frames_pass'] and legal['copies']==24 and legal['erasures']==24
 assert inv['status']=='PASS_COHORT_LITERAL_FIVE_STAGE_FINITE_INVOICE_AND_POSITIVE_CUTOFFS'
 assert bank['actual_role_replica_stage_assignments']==3026400 and bank['changed_projector_charts']==22806
 assert inv['normalizer_factor_bound']==787 and inv['new_chart_factor_max']==342
 hist=Counter();adds=units=copies=0
 for op,a,b,c,f,z in struct.iter_unpack('<6i',(out/'candidate/COHORT249-RECORDS.bin').read_bytes()):
  if op==0 and f:hist[f]+=1
  elif op==1:adds+=1;units+=abs(c)
  elif op==2:hist[z]+=1;copies+=1
 assert copies==24 and dict(hist)=={int(r):n for r,n in cols['local_raw_H']}
 literal={r:200*n for r,n in hist.items()}
 for r in (4,23,46,50):literal[r]=literal.get(r,0)+40*2*1760
 assert literal=={int(r):int(n) for r,n in inv['literal_histogram'].items()}
 p=price['cohort_candidate'];assert literal=={int(r):5*n for r,n in p['histogram'].items()}
 stock=inv['literal_stock'];children=sum(literal.values());mass=sum(r*n for r,n in literal.items())
 assert stock==809885 and p['stock']==161977 and 120*stock-mass==176000
 route=40*(24*1760+10*15132);high=16*(120**2+1)**2;good=8*120**2+8
 selectors=2*5*40*((stock-1)+15132*120*787)
 coefficient=40*(5*units+6*1760)+route*high+route*(stock+24)+children*good+children*(128*240**3)+16*120**3+120*40+children+selectors+1
 assert coefficient==int(inv['full_counted_primitive_coefficient'])==58322299353183001
 assert selectors==int(inv['extra_selector_calls'])==bank['selector_charge']==571950385600
 assert coefficient<2**80<price['prime'] and selectors<2**40
 assert Q(price['first_interval'][1])<1 and Q(price['second_interval'][1])<1
 assert Q(price['first_next'][0])>1 and Q(price['second_next'][0])>1
 assert price['prime_lucas_lehmer_residue']==0 and price['prime_lucas_lehmer_steps']==125
 gaps=[];bits=(coefficient-1).bit_length()
 for row in price['ordinary_gaps']:
  gap=min(map(Q,row.values()));assert gap>0
  cutoff=max(1,ceilq(Q(36)/gap**2),ceilq(Q(2*(4+bits))/gap))
  assert cutoff*gap**2>=36 and cutoff*gap>=2*(4+bits)
  gaps.append({'minimum_gap':str(gap),'counted_log2_cutoff':str(cutoff)})
 assert len(gaps)==9 and len(price['assembly']['strict_constraints'])==47
 assert min(map(Q,price['assembly']['strict_constraints'].values()))>0 and price['adjacent_rejected']
 result={'status':'PASS_SOURCE_BOUND_W3_TARGET_PREFIX_RESTORATION_CONDITIONAL_FINITE_CONSTRUCTION','kappa':price['kappa'],'word_sha256':binding['word_sha256'],'compact_word_sha256':binding['compact_word_sha256'],'source_regenerated':True,'complex_supplier_regenerated':True,'active_helpers':15132,'normalized_stock':162123,'bank_assignments':3026400,'new_frame_charts':3473,'changed_projector_charts':20844,'new_chart_factor_max':342,'normalizer':787,'finite_coefficient':coefficient,'selector_charge':selectors,'payload_bits':94,'finite_cutoffs':gaps,'complex_guard':cg,'full_constant_rule':'Replace the counted coefficient by C_full dominating every inherited primitive, wrapper, row, setup, routing and earlier-level constant in the same positive-gap cutoff formula. No recursive child is absorbed.','scope':'Conditional on inherited all-size compiler, weighted charts, restored rows, selectors, routing, prime supply, complex dirty lifting, precision/recovery and analytic interfaces. No unconditional multiplication theorem, new Lean build or runtime benchmark is claimed.'}
 receipts=['baseline/verification.json','COMPLEX-GUARD.json','BANK.json','PRICE.json','INVOICE.json','COLUMNS.json','COMPACT-COLUMNS.json','LEGALITY.json','candidate/SOURCE-BINDING.json','logs/complex-source.log']
 result['fresh_receipt_hashes']={name:sha(out/name) for name in receipts}
 (out/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS integrated construction',price['kappa'],flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);a=ap.parse_args();finish(a.output)
