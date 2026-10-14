"""Verify exact outer refinement; --supplier-work and --outer-work bind completed unchanged parent checks."""
import argparse,hashlib,json,sys
from pathlib import Path
from fractions import Fraction as F
import ledger as L
sys.set_int_max_str_digits(0)
if not __debug__:raise RuntimeError('Assertions must be enabled')
P=Path(__file__).resolve().parent; ROOT=P.parents[1]
def rd(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decimal(x):
 scale=10**(L.DIG+46);scaled=x*scale
 assert scaled.denominator==1
 n=scaled.numerator; digits=str(n).zfill(L.DIG+47)
 return digits[:-L.DIG-46]+'.'+digits[-L.DIG-46:]
def check():
 sources=rd(P/'SOURCES.json')
 for r in sources['files']:
  if r['usage']=='input':assert sha(ROOT/r['path'])==r['sha256'],r['path']
 parent=L.PARENT; manifest=rd(parent/'MANIFEST.json')
 for name,h in manifest.items():assert sha(parent/name)==h,name
 row=L.ledger('struct_boundary_radix_union')
 assert len(row['strict_checks'])==62 and all(x>0 for x in row['strict_checks'].values())
 assert min(row['margins'].values())==row['margins']['main_transform']
 # Independent balance and cost equations, without the ledger function.
 delta=F(1025,1024*10**(L.DIG+10));e=1-delta;beta=1-3*delta
 q=F(rd(parent/'outer/B.json')['b'])-F(1,10**(L.DIG+10))
 c=F(3,32);s=F(1,10**(L.DIG+10));xi=e+e*q+s-c
 k=F((e*q*10**(L.DIG+46)).__floor__(),10**(L.DIG+46))-F(1,10**(L.DIG+22))
 assert k==row['kappa'] and delta>L.R0 and 0<k<q
 assert 1-delta*(1+1/q)<=beta<1-2*delta
 assert 1-e+q*beta-e*q==delta*(1-2*q)>0
 assert 1-e-L.R0==L.R0/F(1024)>0
 assert F(1,2)<xi<e<1 and 0<beta<e and xi<2
 assert 1-(2*xi-2)-L.R0-beta>L.ZETA>0
 assert 1-beta-2*(1-e)==delta>0 and 7**16<2**45
 costs={'transform':1-e*q,'global_router':1-L.a,'gaussian':e-q*beta,'group_router':e-L.a*beta,'group_scans':e-beta,'boundary':e-xi+(F(45,16)-1)/2,'sparse_union':e+F(1,2)-xi,'polynomials':1-e,'microfaces':e+beta+48-128+2}
 assert max(costs.values())==costs['transform'] and all(v<1-k for v in costs.values())
 prior=F(rd(parent/'outer/OUTER-CLAIM.json')['kappa'])
 prior_derived=F(((1-2*L.R0)*q*L.FLOOR).__floor__(),L.FLOOR)-L.BACKOFF
 assert prior==prior_derived and k>prior
 gain=k-prior; ideal=F(1023,1024)*q*L.R0
 assert abs(gain-ideal)<F(1,L.FLOOR)
 variants=[('endpoint_equality',{'q_':L.b}),('zero_layout_slack',{'slack':F(0)}),('old_per_axis_scan',{'old_scan':True}),('full_cell_gauge',{'full_gauge':True}),('full_key_sort',{'full_key':True}),('old_g_factor_union_row',{'old_union':True}),('old_theta_chirp_guard',{'old_theta':True}),('old_linear_guard',{'old_linear':True}),('old_union_tag_2beta',{'old_tag':True}),('matrix_below_strassen',{'tau_eff':F(14,5)}),('halo_too_short',{'halo_power':40}),('core_too_small',{'core_power':48}),('group_equals_dimension',{'beta_':L.EPS}),('epsilon_equals_one',{'eps_':F(1)}),('epsilon_not_above_r0_slack',{'eps_':1-L.R0}),('beta_below_gaussian_window',{'beta_':1-700*L.DELTA_E}),('beta_above_membership_window',{'beta_':1-2*L.DELTA_E})]
 controls={}
 for name,kw in variants:
  bad=L.ledger('struct_boundary_radix_union',**kw)
  failed=[n for n,v in bad['strict_checks'].items() if v<=0]
  assert failed,name
  controls[name]=failed
 assert 'old_g_factor_union_row_above_kappa' in controls['old_g_factor_union_row']
 assert 'unnecessary_full_key_sort_above_kappa' in controls['full_key_sort']
 # Independent limit controls: the closure points are strictly inadmissible.
 assert not (1-(1-L.R0)-L.R0>0)
 return {'kappa_decimal':decimal(k),'gain_rational':str(gain),'kappa_sha256':hashlib.sha256(decimal(k).encode()).hexdigest(),'strict_checks':62,'rejecting_controls':controls,'epsilon_delta_ratio':'1025/1024','parent_head':'322949a53488d64023fedb89a6774927707e57ba','parent_manifest_sha256':sha(parent/'MANIFEST.json'),'scope':'Conditional outer arithmetic refinement only; unchanged supplier finite admission and complete parent outer evidence replays are required separately.'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write-claim',action='store_true');ap.add_argument('--supplier-work',type=Path);ap.add_argument('--outer-work',type=Path);ap.add_argument('--outer-log',type=Path);ap.add_argument('--out',type=Path);args=ap.parse_args()
 result=check()
 if args.write_claim:(P/'CLAIM.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');return
 assert rd(P/'CLAIM.json')==result,'candidate claim drift'
 result['status']='PASS_EXACT_OUTER_REFINEMENT_ONLY'
 if any((args.supplier_work,args.outer_work,args.outer_log)):
  assert all((args.supplier_work,args.outer_work,args.outer_log)), 'All full-admission inputs are required'
  w=args.supplier_work; supplier=rd(w/'RESULT.json');assembly=rd(w/'strict/ASSEMBLY.json')
  assert supplier['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION' and supplier['manifest_sha256']==result['parent_manifest_sha256']
  assert all(s['exit_code']==0 for s in supplier['stages'])
  assert supplier['controls']=={'admission':114,'bit':12,'controller':15,'independent_owner':8,'geometry':6}
  assert assembly['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and len(assembly['outer'])==47 and len(assembly['conservative_outer'])==47
  assert F(assembly['complex_lower'])==L.certified_complex and F(assembly['bit_lower'])==L.bit
  assert {int(k):v for k,v in assembly['complex_profile'].items()}==L.profile
  for rows in (assembly['moments'],assembly['conservative_moments']):
   for r in rows:
    for engine in ('mercator','base_two'):
     lo,hi=map(F,r[engine]);assert lo<=hi
     # Parent receipts store M(endpoint)-1, so acceptance/rejection is relative to zero.
     assert hi<0 if r['accept'] else lo>0
  for key,side,endpoint in (('moments','complex',L.certified_complex),('conservative_moments','conservative_complex',F(L.spec['expected']['conservative_complex_lower']))):
   rows=[r for r in assembly[key] if r['side']==side]
   assert any(r['accept'] and F(r['endpoint'])==endpoint for r in rows)
   assert any(not r['accept'] and F(r['endpoint'])==endpoint+F(1,10**L.DIG) for r in rows)
  for name in ('LEDGER.json','INDEPENDENT.json'):
   assert (args.outer_work/'outer'/name).read_bytes()==(L.PARENT/'outer'/name).read_bytes(),name
  rawlog=args.outer_log.read_bytes();outerlog=rawlog.decode('utf-16' if rawlog.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8')
  assert outerlog.strip().splitlines()[-1]=='PASS_OUTER'
  assert 'PASS_EXACT_REPLAY 19' in outerlog
  assert rd(args.outer_work/'fine-padding.json')['status']=='PASS_FINE_PADDING_FINITE_CONTROLS'
  result['status']='PASS_SOURCE_BOUND_COMPLETE_FINITE_OUTER_REFINEMENT'
  result['parent_receipt_sha256']={n:sha(w/n) for n in ('RESULT.json','strict/ASSEMBLY.json','STAGES.json')}
  result['parent_outer_sha256']={n:sha(args.outer_work/'outer'/n) for n in ('LEDGER.json','INDEPENDENT.json')}
  result['parent_outer_log_sha256']=sha(args.outer_log)
  result['replay_scope']='Unchanged parent supplier checker on Linux and unchanged CRLF-bound outer checker on Windows; Linux aggregate release byte comparison failed solely on CRLF/LF artifact endings. No assertions or certificates were changed.'
 if args.out:args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(result['status'],'strict_checks=62 controls=17 positive_gain=True')
if __name__=='__main__':main()
