"""Independent exact verification of the serialized circuit, using only stdlib integers."""
from pathlib import Path
import argparse,json,hashlib,datetime,time,math

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sparse(entries,bound):
 assert isinstance(entries,list) and entries
 out={};last=-1
 for pair in entries:
  assert isinstance(pair,list) and len(pair)==2;i,c=pair
  assert type(i) is int and type(c) is int and last<i<bound and c!=0
  out[i]=c;last=i
 return out
def polynomial(left,right):
 out={}
 for a,x in left.items():
  for b,y in right.items():
   m=(a,b) if a<=b else (b,a);out[m]=out.get(m,0)+x*y
 return {m:c for m,c in out.items() if c}
def primitive(form):
 g=math.gcd(*form.values())
 first=form[min(form)];scale=g if first>0 else -g
 return tuple((i,c//scale) for i,c in sorted(form.items())),scale
def main():
 parser=argparse.ArgumentParser();parser.add_argument('circuit');parser.add_argument('--expected-sha256',required=True);parser.add_argument('--receipt',required=True);args=parser.parse_args()
 p=Path(args.circuit).resolve();start=time.perf_counter();initial=p.read_bytes();h=hashlib.sha256(initial).hexdigest();assert h==args.expected_sha256
 d=json.loads(initial);assert d['schema']=='personal-matrix-flat16-mixed-linear-products-integer-output-v1'
 assert d['common_output_denominator']==8 and d['gate_count']==2208 and len(d['gates'])==2208 and len(d['output_numerators'])==256
 assert d['variable_order']['variables']==512 and d['variable_order']['A']==[0,255] and d['variable_order']['B']==[256,511]
 gate_polys=[];exact_product_groups={};projective_product_groups={}
 for idx,g in enumerate(d['gates']):
  assert g['id']==idx and g['outer_term']==idx//46 and g['leaf_gate']==idx%46
  assert g['leaf_family'] in ['P','R','Q','M']
  left=sparse(g['left'],512);right=sparse(g['right'],512)
  pol=polynomial(left,right);assert pol,'Each of the2208 products must be nonzero as an integer polynomial'
  gate_polys.append(pol)
  a,b=tuple(left.items()),tuple(right.items());key=tuple(sorted((a,b)))
  exact_product_groups.setdefault(key,[]).append(idx)
  aa,as_=primitive(left);bb,bs=primitive(right);key=tuple(sorted((aa,bb)))
  projective_product_groups.setdefault(key,[]).append((idx,as_*bs))
 checked=[];uses=set();output_rows=[]
 for out in d['output_numerators']:
  o=out['id'];assert type(o) is int and o==len(checked);r,c=divmod(o,16)
  assert out['row']==r and out['col']==c
  row=sparse(out['terms'],2208);output_rows.append(row);uses.update(row)
  # Fully expand this output independently; normalize commutative quadratic monomials.
  coefficients={};expanded=0
  for g,q in row.items():
   for mon,value in gate_polys[g].items():
    coefficients[mon]=coefficients.get(mon,0)+q*value;expanded+=1
  coefficients={mon:v for mon,v in coefficients.items() if v}
  expected={(16*r+k,256+16*k+c):8 for k in range(16)}
  assert coefficients==expected,(o,[(m,v) for m,v in coefficients.items() if expected.get(m)!=v][:10])
  checked.append({'output':o,'row':r,'col':c,'PASS':True,'contributing_gates':len(row),'expanded_monomial_contributions':expanded,'remaining_monomials':len(coefficients),'AA_remaining':sum(a<256 and b<256 for a,b in coefficients),'BB_remaining':sum(a>=256 and b>=256 for a,b in coefficients),'AB_remaining':sum(a<256<=b for a,b in coefficients)})
 assert len(checked)==256 and uses==set(range(2208))
 # Optional optimization inventory only: do not change the independently checked2208schedule.
 sharing=[];cancelled=0
 for terms in projective_product_groups.values():
  if len(terms)<2:continue
  merged=[]
  for o,row in enumerate(output_rows):
   q=sum(scale*row.get(g,0) for g,scale in terms)
   if q:merged.append([o,q])
  if not merged:cancelled+=1
  sharing.append({'gates':[g for g,_ in terms],'product_scales':[s for _,s in terms],'nonzero_merged_output_count':len(merged)})
 assert p.read_bytes()==initial
 result={'schema':'personal-matrix-flat16-independent-integer-quadratic-verification-v1','status':'PASS_ALL256_EXACT_OUTPUT_POLYNOMIAL_IDENTITIES_AND2208_NONZERO_PRODUCT_GATES','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer':{'filename':Path(__file__).name,'sha256':sha(__file__)},'circuit':{'filename':p.name,'bytes':len(initial),'sha256':h},'source_lineage':d['source_lineage'],'method':'Serialized sparse integer forms independently multiplied and accumulated; unordered variable pairs identify every quadratic monomial over a commutative ring. Each output compared exactly with8sum_k A[r,k]B[k,c]. No generator/donor import, Fraction-to-int truncation, random testing or compiler calls.','variables':512,'output_denominator':8,'actual_outputs_verified':256,'actual_scheduled_gates':2208,'all_gates_left_and_right_nonzero':True,'all_gates_polynomial_nonzero':True,'all_gates_used_by_output':True,'all_AA_and_BB_output_coefficients_cancelled':True,'expected_AB_monomials_per_output':16,'all4096_classical_AB_terms_exact':True,'output_checks':checked,'exact_commutative_product_duplicate_saving':2208-len(exact_product_groups),'projectively_duplicate_product_saving':2208-len(projective_product_groups),'cancelled_normalized_product_group_count':cancelled,'projectively_duplicate_groups':sharing,'verified_original_schedule_unchanged':True,'runtime_seconds':time.perf_counter()-start,'Lean_or_native_guard_invocations':0,'formal_hybrid_qualification_claimed':False,'limits':['This is an executable exact polynomial identity, not a fresh Lean proof of the whole circuit.','Division is by fixed8; general scalar interpretation needs8invertible.','No optimality, numerical-stability, hardware-performance or priority conclusion follows.']}
 dest=Path(args.receipt).resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'receipt':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'status':result['status'],'seconds':result['runtime_seconds'],'exact_duplicates':result['exact_commutative_product_duplicate_saving'],'projective_duplicates':result['projectively_duplicate_product_saving']}))
if __name__=='__main__':main()
