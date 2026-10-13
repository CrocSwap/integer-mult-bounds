"""Portable path/provenance adapter of c3b501f5ed92e3f90fa5210e941283a91b745d17671a3a552552c41fc7a48efe. Mathematical generation is unchanged."""
from pathlib import Path
import argparse,json,re,hashlib,datetime

B=Path(__file__).resolve().parent
DATA_SHA='e04ebfffc4c2f43cb688c856f1f30e5ef1b7c215f76854ab1d75df03f4bff387'
LEAN_SHA='5339fe6f4a6a23693bb4193dd43721cc2092e35e0bf5af1a948d0c16b6522d63'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_lean_table(source,name):
 body=re.search(r'def '+re.escape(name)+r' : Fin 48 → Fin 16 → ℤ :=(.*?)(?=\ndef )',source,re.S)
 assert body,name
 rows=re.findall(r'!\[([^\[\]]*)\]',body.group(1));assert len(rows)==48,name
 result=[]
 for row in rows:
  vals=[x.strip() for x in row.split(',')];assert len(vals)==16
  assert all(re.fullmatch(r'-?\d+',x) for x in vals)
  result.append([int(x) for x in vals])
 return result
def add(*terms):
 out={}
 for scale,row in terms:
  for i,c in row.items():out[i]=out.get(i,0)+scale*c
 return {i:c for i,c in out.items() if c}
def sparse(x):return [[i,x[i]] for i in sorted(x)]
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',required=True);args=a.parse_args()
 data_path=B/'input/outer48_exact_rational_and_integer_data.json'
 lean_path=B/'lean/Outer48Data.lean'
 assert sha(data_path)==DATA_SHA and sha(lean_path)==LEAN_SHA
 data=json.loads(data_path.read_text(encoding='utf-8'));minimal=data['minimal_integer_certificate']
 alpha=minimal['alpha_integer'];beta=minimal['beta_integer'];gamma=minimal['gamma_numerator']
 source=lean_path.read_text(encoding='utf-8')
 assert read_lean_table(source,'alphaInteger')==alpha
 assert read_lean_table(source,'betaInteger')==beta
 assert read_lean_table(source,'gammaNumerator')==gamma
 assert data['per_leg_denominator_scales']=={'alpha':1,'beta':1,'gamma':8}
 donor=data['source_sha256'];assert donor=='a0dd1675fa9f8389230db4dc376639ee20b0f9786765b9e75abc60c14844f0ef'
 outer_receipt=B/'evidence/actual_nine_sources_35_standard_public_projection.json'
 assert sha(outer_receipt)=='8dba5fc5be9405ccc7d6605324442f8781c260afe3633fa9b1aff290a462c779'
 old=json.loads(outer_receipt.read_text(encoding='utf-8'))
 assert old['status']=='PASS_EXACT_9_SOURCE_35_STANDARD_SCOPE'
 assert old['source_count']==9 and old['unique_standard_endpoint_count']==35
 outer_row=next(x for x in old['module_rows'] if x['module']=='Outer48Data')
 assert outer_row['actual_exit_code']==0 and outer_row['source_sha256']==LEAN_SHA
 assert all(x['classification']=='STANDARD_KERNEL_AXIOMS' for x in outer_row['selected_axiom_outputs'])
 gates=[];outputs=[{} for _ in range(256)]
 for t in range(48):
  # A full coordinate: row=4*outer_row+inner_row, col=4*outer_col+inner_col.
  X={};Y={}
  for u in range(4):
   for v in range(4):
    X[u,v]={(4*i+u)*16+(4*j+v):alpha[t][4*i+j]
      for i in range(4) for j in range(4) if alpha[t][4*i+j]}
    Y[u,v]={256+(4*i+u)*16+(4*j+v):beta[t][4*i+j]
      for i in range(4) for j in range(4) if beta[t][4*i+j]}
  leaf=[]
  for family in ['P','R','Q','M']:
   if family in ['P','R']:
    for i in range(4):
     for h in range(2):
      u,v=2*h,2*h+1
      if family=='P':left=X[i,u];right=add((1,Y[u,0]),(1,X[i,v]));uses={4*i:1,**{4*i+j:-1 for j in range(1,4)}}
      else:left=X[i,v];right=add((1,Y[v,0]),(-1,X[i,u]));uses={4*i:1}
      leaf.append((family,{'i':i,'h':h},left,right,uses))
   elif family=='Q':
    for h in range(2):
     for j0 in range(3):
      u,v,j=2*h,2*h+1,j0+1
      leaf.append((family,{'h':h,'j0':j0},Y[v,j],add((1,Y[u,0]),(1,Y[u,j])),{4*i+j:-1 for i in range(4)}))
   else:
    for i in range(4):
     for h in range(2):
      for j0 in range(3):
       u,v,j=2*h,2*h+1,j0+1
       leaf.append((family,{'i':i,'h':h,'j0':j0},add((1,X[i,u]),(1,Y[v,j])),add((1,X[i,v]),(1,Y[u,0]),(1,Y[u,j])),{4*i+j:1}))
  assert len(leaf)==46
  for g,(family,indices,left,right,uses) in enumerate(leaf):
   gid=t*46+g;assert left and right
   gates.append({'id':gid,'outer_term':t,'leaf_gate':g,'leaf_family':family,'leaf_indices':indices,'left':sparse(left),'right':sparse(right)})
   for outer_o in range(16):
    c=gamma[t][outer_o]
    if not c:continue
    oi,oj=divmod(outer_o,4)
    for inner_o,leaf_c in uses.items():
     u,v=divmod(inner_o,4);o=(4*oi+u)*16+(4*oj+v)
     outputs[o][gid]=outputs[o].get(gid,0)+c*leaf_c
 outputs=[{i:c for i,c in row.items() if c} for row in outputs]
 assert len(gates)==2208 and len(outputs)==256
 participates={i for row in outputs for i in row};assert participates==set(range(2208))
 result={'schema':'personal-matrix-flat16-mixed-linear-products-integer-output-v1','status':'GENERATED_EXPLICIT_CIRCUIT_REQUIRES_INDEPENDENT_POLYNOMIAL_VERIFICATION','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer':{'filename':Path(__file__).name,'sha256':sha(__file__)},'source_lineage':{'outer_data_filename':data_path.name,'outer_data_sha256':DATA_SHA,'actual_Outer48_Lean_source_filename':lean_path.name,'actual_Outer48_Lean_source_sha256':LEAN_SHA,'actual_public_qualification_projection_filename':outer_receipt.name,'actual_public_qualification_projection_sha256':sha(outer_receipt),'original_Outer48_actual_receipt_sha256':outer_row['original_actual_receipt_sha256'],'donor_code_url':data['source_url'],'donor_code_commit':data['source_revision'],'donor_code_sha256':donor,'leaf_source':'Rosowski division-free even-inner-dimension P/R/Q/M identities;4×4 instance','leaf_primary_url':'https://arxiv.org/html/1904.07683v2','formal_leaf_interface':'PersonalMatrix.RosowskiEven.Gates(((I×H)⊕(I×H))⊕((H×J)⊕((I×H)×J))); I=Fin4,H=Fin2,J=Fin3','gate_derivation':'global_id=46*outer_term+leaf_gate; P8,R8,Q6,M24 in lexicographic product/sum order. All coefficient scalings are fixed; there are no additional input-dependent products in recombination.'},'variable_order':{'variables':512,'A':[0,255],'B':[256,511],'coordinate_rule':'A(r,c)=16*r+c; B(r,c)=256+16*r+c. Full row=4*outer_row+inner_row and full col=4*outer_col+inner_col.','paired_leaf_inner':'2*h+Bool (false0,true1)','leaf_column':'OptionFin3: none0,somej0→j0+1'},'common_output_denominator':8,'semantics':'For each scalar outputo, sum(output_numerator[o,g]·left_g·right_g)=8·(A*B)[o]. Over a commutative ring with8invertible, divide only by fixed8. The circuit is mixed-input quadratic, not a tensor-rank2208 decomposition.','gate_count':2208,'gates':gates,'output_numerators':[{'id':o,'row':o//16,'col':o%16,'terms':sparse(row)} for o,row in enumerate(outputs)],'claims_not_made':['No optimal product/addition count, numerical stability, measured speed, new exponent or universal priority.','Executable certificate correctness remains separate from the formal compound proof; exact source/base qualification is bound but no new Lean invocation occurs here.']}
 assert sha(data_path)==DATA_SHA and sha(lean_path)==LEAN_SHA
 dest=Path(args.output).resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'circuit':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'gates':len(gates),'output_numerator_nonzeros':sum(len(x) for x in outputs)}))
if __name__=='__main__':main()
