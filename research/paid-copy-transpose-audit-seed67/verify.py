"""Full dirty-work transpose accounting; explicit checks survive -O."""
import argparse,hashlib,importlib.util,json,sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from source import BASE,ROOT,PATHS,source,need,enc,read
import independent

def matrix(ops,n):
 rows=[{i:F(1)} for i in range(n)]
 for op in ops:
  k,t=op[:2]
  if k=='clear':rows[t]={}
  elif k=='copy':rows[t]=rows[op[2]].copy()
  elif k in ('add','subtract'):
   s=op[2];q=1 if k=='add' else -1
   for j,v in rows[s].items():
    z=rows[t].get(j,F(0))+q*v
    if z:rows[t][j]=z
    else:rows[t].pop(j,None)
  else:
   q={'double':F(2),'halve':F(1,2),'negate':F(-1)}[k]
   rows[t]={j:q*v for j,v in rows[t].items()}
 return rows

def transposed(rows):
 out=[{} for _ in rows]
 for i,row in enumerate(rows):
  for j,v in row.items():out[j][i]=v
 return out

def transpose_ops(ops,wrong_copy=False):
 result=[]
 for op in reversed(ops):
  if op[0]=='copy':
   if wrong_copy:result.append(('copy',op[2],op[1]))
   else:result.extend([('add',op[2],op[1]),('clear',op[1])])
  elif op[0] in ('add','subtract'):result.append((op[0],op[2],op[1]))
  else:result.append(op)
 return result

def serialize(rows):return [[[j,v.numerator,v.denominator] for j,v in sorted(row.items())] for row in rows]
def digest(rows):return hashlib.sha256(enc(serialize(rows)).encode()).hexdigest()

def lower_word(macros,lower,n):
 result=[]
 for e in macros:
  op=e[:-1].copy();op[1]=('R',op[1])
  if op[0]=='add':op[2]=('R',op[2])
  for z in lower(op):result.append(tuple([z[0]]+[n if x[0]=='W' else x[1] for x in z[1:]]))
 return result

def macro_transpose(macros):
 result=[]
 for e in reversed(macros):
  z=e.copy()
  if z[0]=='add':z[1],z[2]=z[2],z[1]
  result.append(z)
 return result

def controls():
 copy=[('copy',1,0)];desired=transposed(matrix(copy,2))
 candidates=[[],*[[(k,t)] for k in ('clear','double','halve','negate') for t in range(2)],
  *[[(k,t,1-t)] for k in ('copy','add','subtract') for t in range(2)]]
 need(all(matrix(x,2)!=desired for x in candidates),'COPY transpose one-gate exclusion')
 need(matrix(transpose_ops(copy),2)==desired,'COPY transpose two-gate witness')
 exact_columns=[[F(1),F(0)],[F(1),F(0)]]
 need(all(independent.primitive_columns(x,2)!=exact_columns for x in candidates),'independent one-gate exclusion')
 need(independent.primitive_columns(transpose_ops(copy),2)==exact_columns,'independent two-gate witness')
 count=0
 broken=[transpose_ops(copy,True),[('add',0,1)],[('clear',1),('add',0,1)]]
 for x in broken:
  need(matrix(x,2)!=desired,'COPY transpose corruption');count+=1
 # Wrong order and wrong diagonal inversion each fail on exact matrices.
 test=[('copy',2,0),('halve',2),('subtract',1,2),('clear',2)]
 want=transposed(matrix(test,3));proper=transpose_ops(test)
 need(matrix(proper,3)==want,'nonunit transpose')
 for bad in [list(reversed(proper)),[tuple(['double']+list(z[1:])) if z[0]=='halve' else z for z in proper]]:
  need(matrix(bad,3)!=want,'transpose order/scale corruption');count+=1
 # Clean-work-only checks cannot detect discarded dirty input leakage.
 clean=[('add',1,0),('clear',2)];dirty=[('add',1,2)]+clean
 a,b=matrix(clean,3),matrix(dirty,3)
 need(all({j:v for j,v in a[i].items() if j<2}=={j:v for j,v in b[i].items() if j<2} for i in range(3)) and a!=b,'dirty input control');count+=1
 return {'controls':count,'two_register_programs_of_length_at_most_one':len(candidates),
  'copy_matrix':serialize(matrix(copy,2)),'transpose_matrix':serialize(desired),'minimum':2,'witness':transpose_ops(copy),
  'dirty_counterexample':{'input':[0,0,1],'correct':[0,0,0],'leaking':[0,1,0]}}

def compute():
 w=source();macros=w['cleanup'];n=2*w['v']+w['R']
 need(all(w['frames'][e[-1]]==[256,128,64,32,16,8,4,2,1] for e in macros),'FULL cleanup')
 need(all(e[0] in ('add','scale') and (e[0]!='add' or e[1]!=e[2]) for e in macros),'literal macro model')
 spec=importlib.util.spec_from_file_location('pinned_lower',ROOT/PATHS[2]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 f=lower_word(macros,m.lower,n);t=transpose_ops(f);direct=lower_word(macro_transpose(macros),m.lower,n)
 fm=matrix(f,n+1);tm=matrix(t,n+1);dm=matrix(direct,n+1)
 need(tm==transposed(fm)==dm,'full transpose and independent direct lowering')
 need(not fm[-1] and all(n not in row for row in fm),'arbitrary private work annihilated')
 columns=independent.macro_columns(macros,n)
 need(len(columns)==n and all(columns[j]=={i:fm[i][j] for i in range(n) if j in fm[i]} for j in range(n)),'independent full macro columns')
 counts=Counter(x[0] for x in f);need(len(t)==len(f)+counts['copy'] and len(direct)==len(f),'complete paid count identities')
 check=controls()
 return {'base':BASE,'local_source':'PR1094 unchanged PR1042 seven-slot R480 word','scalar_registers':n,'private_work_registers':1,
  'all_input_columns':n+1,'cleanup_macros':len(macros),'forward_real_primitives':len(f),'forward_inventory':dict(sorted(counts.items())),
  'mechanical_transpose_real_primitives':len(t),'mechanical_transpose_inventory':dict(sorted(Counter(x[0] for x in t).items())),
  'direct_transposed_macro_real_primitives':len(direct),'mechanical_extra_real_primitives':counts['copy'],
  'complex_counts':{'forward':2*len(f),'mechanical_transpose':2*len(t),'direct_transposed_macros':2*len(direct)},
  'forward_matrix_sha256':digest(fm),'transpose_matrix_sha256':digest(tm),'dirty_work_zero_input_and_output_blocks':True,
  'small_copy_certificate':check,'scope':'Literal primitive transpose surcharge only; direct macro lowering avoids it; no predecessor bug or unrestricted circuit optimum',
  'native_executed':False,'new_kappa':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r=compute()
 if a.write:(HERE/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
 else:need(enc(r)==enc(read((HERE/'RESULT.json').read_bytes())),'typed canonical result mismatch')
 print('PASS_PAID_COPY_TRANSPOSE columns='+str(r['all_input_columns'])+' controls='+str(r['small_copy_certificate']['controls'])+' no_new_kappa')
 print('forward/mechanical/direct',r['forward_real_primitives'],r['mechanical_transpose_real_primitives'],r['direct_transposed_macro_real_primitives'])
if __name__=='__main__':main()
