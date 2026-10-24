#!/usr/bin/env python3
"""Fresh literal one-provider envelope, two norms; no submitted Python execution.
Max-field Euclidean norm matches the author's stated geometry. Joint-field
Euclidean norm requires a COPY factor. No caller/compiler/precision admission.
Chris R/Clear1nsight with substantial OpenAI Codex assistance; retain source credit.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import argparse,gzip,json,resource,time
HERE=Path(__file__).resolve().parent

def need(v,s):
 if not v:raise ValueError(s)
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def ceil_log2(q):
 q=max(Q(1),q);e=0
 while q>1:q/=2;e+=1
 return e

def rank(rows):
 piv={}
 for x in rows:
  while x:
   b=x.bit_length()-1
   if b in piv:x^=piv[b]
   else:piv[b]=x;break
 return len(piv)
def exponent(g,geometry):
 if g[0]=='add':return ceil_log2(1+abs(Q(g[-2],g[-1])))
 if g[0]=='scale':return ceil_log2(abs(Q(g[-2],g[-1])))
 if g[0]=='copy':return int(geometry=='joint_field_l2')
 need(g[0]in('clear','swap','unitary','zero_retag','annotation'),'unknown geometry gate')
 return 0

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();start=time.monotonic();resource.setrlimit(resource.RLIMIT_AS,(128*1024*1024,128*1024*1024))
 pins=load(HERE/'inputs/ALL-PINS.json')+load(HERE/'envelope-inputs/SOURCES.json')
 for pin in pins:need(sha256((HERE/pin['local']).read_bytes()).hexdigest()==pin['sha256'],'changed norm input '+pin['local'])
 a=load(HERE/'inputs/PROVIDER.json');word=load(HERE/'inputs/WORD.json.gz')['word'];source=load(HERE/'inputs/SOURCE-WORD.json.gz');n=load(HERE/'inputs/NORMALIZERS.json');c=source['canonical']
 # Every frame is an independent subspace basis within the same nine-axis field.
 need(all(len(v)<=9 and rank(v)==len(v)and all(0<x<512 for x in v)for v in c['frames']),'valid square canonical frame domains')
 need(all(len(w['G_columns'])==9 and rank(w['G_columns'])==9 for w in c['warps']),'invertible native warp address matrices')
 # All literal boundary words have an invertible address permutation and unit phases.
 wraps=[port['compiled_wrappers'][k]['word']for port in n['ports']for k in ['backward_input_X','backward_input_Y','backward_output_X','backward_output_Y']]
 wraps += [m[k]['literal_word']for m in a['mode_boundaries']for k in ['input_K','output_N']]
 for w in wraps:
  for g in w:
   need(g[0]in('D','P','X','phase'),'boundary word is monomial')
   if g[0]=='P':need(len(g[1])==9 and rank(g[1])==9,'boundary permutation invertible')
 groups=[]
 def group(label,gates):groups.append((label,gates))
 def basis_gates(program):
  out=[]
  for g in program:
   q=Q(g[-1]);out.append([g[0],q.numerator,q.denominator])
  return out
 group('224_fused_main_input_wrappers',[['unitary']]*224)
 group('eight_mode_inputs',[g for m in a['mode_boundaries']for g in [['unitary'],['scale',2,1]]])
 group('input_basis',basis_gates(a['input_basis_program']))
 body=[];record=Counter()
 for e in word:
  record[e[0]]+=1
  if e[0]=='scalar':
   g=e[1]
   if g[0]in('add','scale'):body.append([g[0],g[-2],g[-1]])
   else:need(g[0]in('copy','clear'),'literal scalar alphabet');body.append([g[0]])
  elif e[0]in('warp','climb','center'):body.append(['unitary'])
  elif e[0]=='zero_retag':body.append(['zero_retag'])
  else:need(e[0]in('phase','adapter','residual_adapter'),'source record alphabet');body.append(['annotation'])
 group('changed_native_word',body)
 group('output_basis',basis_gates(a['output_basis_program']))
 exit=[]
 for m in a['mode_boundaries']:
  q=Q(m['cache_scalar']);exit.extend([['scale',q.numerator,q.denominator],['unitary'],['swap'],['clear']])
 group('eight_cache_output_normalizers_and_consumption',exit)
 group('224_fused_main_output_wrappers',[['unitary']]*224)
 rows=[];total_max=total_joint=0;allg=[]
 for label,gates in groups:
  lm=sum(exponent(g,'max_field_l2')for g in gates);lj=sum(exponent(g,'joint_field_l2')for g in gates);total_max+=lm;total_joint+=lj;allg.extend(gates);rows.append(dict(group=label,gate_count=len(gates),counts=dict(Counter(g[0]for g in gates)),max_field_l2_exponent=lm,joint_field_l2_exponent=lj))
 copies=sum(g[0]=='copy'for g in allg);need(copies==16 and total_joint-total_max==copies,'COPY geometry difference')
 author=a['local_error_amplification_power2_bound'];need(total_max==author,'fresh max-field exponent differs from author scalar claim')
 # Local controls exercise the same exact exponent function, not hashes alone.
 need(ceil_log2(Q(1))==0 and ceil_log2(Q(2))==1 and ceil_log2(Q(3))==2 and ceil_log2(Q(9,8))==1,'exact upward logarithm controls')
 need(exponent(['copy'],'max_field_l2')==0 and exponent(['copy'],'joint_field_l2')==1,'COPY geometry control')
 need(exponent(['scale',2,1],'max_field_l2')==1 and exponent(['scale',1,4],'max_field_l2')==0,'already normalized output SCALE control')
 raw=json.dumps(allg,separators=(',',':')).encode()
 result=dict(executed_checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),status='PASS_INDEPENDENT_ONE_PROVIDER_TWO_NORM_ENVELOPE',head='3348fccea855082786d5f0fc5558b73d4974e745',source_files=pins,groups=rows,total_max_field_l2_exponent=total_max,total_joint_field_l2_exponent=total_joint,author_stated_max_field_exponent=author,author_declared_geometry='maximum over fields of field Euclidean norms',copy_count=copies,abstract_scalar_unitary_transcript_sha256=sha256(raw).hexdigest(),native_records=dict(record),square_clifford_contract='All fields are square ambient2^(9f) address arrays. Normalized signed C gates, canonical frames/conjugates, invertible address warps and literal monomial wrappers are unitary for every positive width f. Physical phase/adapter binding is inherited/audited separately; free-group invertibility alone would not establish this premise.',uniform_contiguous_intervals=True,uniform_suffixes=True,error_inequality='For either stated norm and its exponent L: ||e_out|| <= 2^L (||e_in|| + sum_j ||local_residual_j||). Residuals use that same whole-field geometry, at one fixed width. No implicit coordinatewise-to-field or width-independent injection conversion is claimed.',scope='One raw provider only. Not recursive precision, caller error allocation, tape routing/movement, machine storage, compiler or outer funding.',controls=['upward_rational_logarithm','COPY_norm_geometry','emitted_output_scale_used_directly'],runtime={'seconds':time.monotonic()-start,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
 need(not args.output.exists(),'immutable output already exists');args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'max_field_exponent':total_max,'joint_field_exponent':total_joint,'runtime':result['runtime']}))
if __name__=='__main__':main()
