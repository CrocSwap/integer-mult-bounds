#!/usr/bin/env python3
"""Independent frozen Lean boundary and actual-word count audit; no compile."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
from math import factorial,comb
import ast,gzip,json,re,shutil,subprocess,sys
if sys.flags.optimize:raise RuntimeError('Assertions must remain enabled')
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;LEAN=ROOT/'work/r12-lean';OWN=ROOT/'work/r12-audit';TERMINAL=ROOT/'work/r12-terminal/joint-expansion'
read=lambda p:json.loads(p.read_text());sha=lambda p:sha256(p.read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def no_float(x):
 if isinstance(x,float):raise ValueError('Float in formal mathematical input')
 if isinstance(x,dict):
  for y in x.values():no_float(y)
 if isinstance(x,list):
  for y in x:no_float(y)
source=LEAN/'ShrunkBirthTerminal.lean';gen=LEAN/'generate.py';inp=LEAN/'input.json';receipt=read(LEAN/'verification.json');data=read(inp);no_float(data);cert=data['certificate'];p=cert['profile']
require(sha(source)==receipt['source_sha256']=='8c69d10ece16816edaef9df72182c9eecef3b464f88c82e0b8435f09c94ad095','Frozen Lean source')
require(sha(gen)==receipt['generator_sha256'] and sha(inp)==receipt['input_sha256']=='ecd604ec8f7185e7d23f2f2671f11b8aa9c1e3420e89e597d3a958fe613e9abf','Frozen generator/input')
for path,digest in data['pins'].items():require(sha(ROOT/path)==digest,'Lean input source pin '+path)
require(cert==read(OWN/'canonical-joint-expansion/joint-expansion/certificate.json'),'Full independent arithmetic witness differs')
# Regenerate only in this audit's own scratch, without rerunning Lean.
regen=HERE/'regeneration';regen.mkdir(exist_ok=True)
for file in ('generate.py','input.json'):(regen/file).write_bytes((LEAN/file).read_bytes())
subprocess.run([sys.executable,str(regen/'generate.py')],check=True,capture_output=True)
require((regen/source.name).read_bytes()==source.read_bytes(),'Generator output not byte-identical')
# Actual role and frame-array counts from the saved literal word.
word_path=TERMINAL/'word.json.gz';word=json.loads(gzip.decompress(word_path.read_bytes()));require(sha(word_path)==data['pins']['work/r12-terminal/joint-expansion/word.json.gz'],'Word pin')
h,v=word['h'],word['v'];live=word['physical_roles'];require(len(live)==len(set(live))==p['R'],'Physical role list')
require(word['virtual_roles']==data['virtual_roles'] and len(word['birth_pairs'])==data['births'] and len(word['eliminated_terminal_roles'])==data['terminals'],'Role construction counts')
require(p['R']==data['virtual_roles']-data['births']-data['terminals'] and p['N']==v*v and p['m']==h*h and v==comb(h,3),'Dimensions')
frames=word['frames'];initial=word['initial_frames'];final=word['final_frames'];active=list(range(2*v))+[2*v+s for s in live];active_set=set(active)
init_hist=Counter(len(frames[initial[2*v+s]]) for s in live);require(dict(init_hist)=={int(t):n for t,n in data['initial_frame_dimension_histogram'].items()},'Initial auxiliary dimensions')
def rank(rows):
 piv={}
 for x in rows:
  while x:
   j=x.bit_length()-1
   if j in piv:x^=piv[j]
   else:piv[j]=x;break
 return len(piv)
checked=set();checked_pairs=set()
def validate_frame(k):
 if k in checked:return
 B=frames[k];require(all(type(x)is int and 0<x<2**h for x in B),'Invalid basis vector');require(rank(B)==len(B),'Dependent basis')
 gram=[sum(((x&y).bit_count()%2)<<j for j,y in enumerate(B))for x in B];require(rank(gram)==len(B),'Singular frame')
 checked.add(k)
def contained(A,B):
 # Exact span rank criterion, independent of the generator's projector routines.
 return rank(B+A)==len(B)
current=initial[:];hist=Counter();bank_masks=[{},{}]
for bank in range(2):
 for t in range(v):
  F=current[bank*v+t];bank_masks[bank][F]=bank_masks[bank].get(F,0)|(1<<t)
transitions=copies=0

def move(role,F):
 global transitions
 require(role in active_set and current[role] is not None,'Inactive role incidence');old=current[role]
 if old==F:return
 validate_frame(old);validate_frame(F)
 if (old,F)not in checked_pairs:require(contained(frames[old],frames[F]),'Illegal nesting');checked_pairs.add((old,F))
 r=len(frames[F])-len(frames[old]);require(r>0,'Nonpositive promotion');hist[r]+=1;transitions+=1;current[role]=F
 if role<2*v:
  bank,t=divmod(role,v);bit=1<<t;bank_masks[bank][old]^=bit;bank_masks[bank][F]=bank_masks[bank].get(F,0)|bit

def targets(bank,mask,F):
 require(bank in (0,v) and type(mask)is int and 0<=mask<2**v,'Invalid target set')
 mask &= ~bank_masks[bank//v].get(F,0)
 while mask:
  bit=mask&-mask;mask-=bit;move(bank+bit.bit_length()-1,F)
for e in word['word']:
 kind=e[0]
 if kind in ('g','d'):
  d,s,F=e[1],e[2],e[4];require(d!=s,'Aliased scalar ports');move(d,F);move(s,F)
 elif kind=='r':move(e[1],e[5]);targets(e[2],e[3],e[5])
 elif kind=='f':targets(e[1],e[2],e[3])
 elif kind=='c':
  F,T=e[5],e[6];move(e[1],F);targets(e[2],e[3],T);validate_frame(F);validate_frame(T)
  require(contained(frames[F],frames[T])or contained(frames[T],frames[F]),'Incompatible copied frame')
  r=abs(len(frames[F])-len(frames[T]));require(r==h-1,'Copied center width');hist[r]+=1;copies+=1
 else:raise ValueError('Unknown literal event')
for role in active:move(role,final[role])
require(current==final and copies==h and dict(hist)=={int(t):n for t,n in data['forward_histogram'].items()},'Full literal forward count reconstruction')
H=Counter({t:2*v*n for t,n in hist.items()})
for dim,n in init_hist.items():H[h*h-h+dim]+=2*v*n
H[(h-1)**2]+=2*v*v;H[1]+=v*v
require(dict(H)=={int(t):n for t,n in p['child_multiplicities'].items()},'All Lean child counts from actual word')
W=2*v*v+2*v*len(live);mass=sum(t*n for t,n in H.items());require(W==p['W'] and mass==p['total_rank'] and W*h*h-mass==p['deficit']==v*v-2*v*h*(h-1),'Whole profile rank/deficit')
print('PASS independent actual-word Gram/nesting/count reconstruction',transitions,len(checked),flush=True)
# Exact primitive parameter and Taylor formulas independently re-evaluated.
a,b,k,eta,beta,backoff,A=map(Q,(cert[x]for x in ('assembly_bit','complex_saving','kappa','eta','beta','backoff','actual_bit_saving')))
tau=1-a;sigma=1-b;q=a*(1-2*eta);eps=(1-eta)/(1+q);cc=q+eta/4;lp=1-q;lam=(tau+lp)/2;g=eps*q;r=(g+1-eps)/2;delta=eta/8;internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
require(a==min(A,(1-beta)*b-backoff) and 0<eta<Q(1,2),'Stopped parameters')
require(1-eps-g==eta and 1-eps-r==eta/2 and 1-eps*(1+cc)==eta-eps*eta/4,'Balanced formulas')
require(k<g<k+Q(1,10**18) and (b+Q(1,10**24))/(1+b+Q(1,10**24))<k+Q(1,10**18),'Adjacent family exclusion')
G=cert['finite_bridge']['complex']['scalar_group_upper'];E=64*(W+h*h+G+1)**3;B=mass+E;literal=2*G*W*W+8*mass+4*W+4+32*h*h
sem=cert['finite_bridge']['semantic'];require(E==sem['E'] and B==sem['B'] and literal==sem['literal_charge'] and 32*h*h*B*B==sem['C0'],'Lean semantic formulas');require(E>literal and 2*B*(h*h-574)>=mass+E and 32*h*h*B*B>2*B+18,'Finite guard')
stock=cert['assembly']['finite_bridge'];coeff=0
for name in ('bit_coarse','complex','ordinary_leaf'):
 x=stock[name];m0,d,child,bits,w0=(x[t]for t in ('m','halving_degree','maxchild','wire_bits','W'));require(m0**d>2*child**d and m0**(d-1)<=2*child**(d-1) and 2**(bits-1)<=w0<2**bits,'Stock inequalities');coeff+=d*bits
require(coeff==15561 and 32000-Q(51,25)*coeff==Q(6389,25),'All three stock contribution')
slacks={'a_positive':a,'a_below_b':b-a,'b_below_one_over32':Q(1,32)-b,'beta_positive':beta,'beta_below_one':1-beta,'phase_leaf_above_bit':(1-beta)*b-a,'q_positive':q,'q_below_internal':1-internal-q,'q_below_leaf':1-leaf-q,'c_positive':cc,'c_below_one':1-cc,'q_below_reservations':cc-q,'lambda_above_tau':lam-tau,'lambda_above_sigma':lam-sigma,'lambda_above_internal':lam-internal,'lambda_prime_above_lambda':lp-lam,'compact_leaf':lp-leaf,'compact_reservations':lp-(1-cc),'lambda_prime_below_one':q,'epsilon_positive':eps,'epsilon_below_one':1-eps,'guard_width':1-eps,'K_geometry':1-eps*(1+cc),'K_dominates_log':eps*cc,'record_suffix':1-eps,'phase_local':1-eps-delta,'phase_boundary':r-delta,'gamma_sublinear':1-eps-r,'cell_above_band':eps-(1-r)/2,'prime_interval_packing':1-eps,'alpha_positive':r,'alpha_below_one':1-r,'alpha_below_one_fourth':Q(1,4)-r,'delta_positive':delta,'delta_below_one_eighth':Q(1,8)-delta,'short_record_fallback':eps-a,'small_field_exposure':1-eps-g,'artificial_boundary':8-eps+r-delta-g,'literal_scalar_guard':Q(E-literal),'row_product_gap':Q(6389,25)}
margins=[1-eps,a,g,a,min(1-eps-delta,r-delta),1-eps-delta,eps]
slacks.update({f'g{i}_above_kappa':x-k for i,x in enumerate(margins,1)})
require(len(slacks)==47 and all(x>0 for x in slacks.values()) and slacks=={key:Q(value)for key,value in cert['assembly']['constraints'].items()},'Full independent 47 inequalities')
require(min(margins)==g and all(x>k for x in margins),'Seven controlling margins')
for label in ('accepted','rejected'):
 record=cert['independent_moment'][label];saving=b+(Q(1,10**24)if label=='rejected'else 0);require(Q(record['saving'])==saving,'Moment adjacent saving')
 require(set(map(int,record['terms']))==set(H),'Complete moment support');total=Q(0)
 for ts,x in record['terms'].items():
  t=int(ts);lo,hi=saving*Q(x['log_lower']),saving*Q(x['log_upper']);require(0<=lo<=hi<1,'Taylor domain');weight=Q(t*H[t],h*h*W);require(weight==Q(x['weight']),'Derived physical moment weight')
  if label=='accepted':val=Q(x['exp_upper']);require(sum((hi**j/factorial(j)for j in range(9)),Q())+hi**9/factorial(9)/(1-hi/10)<=val,'Accepted tail domination')
  else:val=Q(x['exp_lower']);require(val<=sum((lo**j/factorial(j)for j in range(9)),Q()),'Rejected lower domination')
  total+=weight*val
 require(total==Q(record['upper'if label=='accepted'else'lower']),'Full moment sum')
 require(total<1 if label=='accepted'else total>1,'Strict paid moment')
# Source has only scoped norm_num arithmetic, and every theorem appears in log.
s=source.read_text();clean=re.sub(r'/\-.*?\-/','',s,flags=re.S);clean=re.sub(r'--[^\n]*','',clean)
require(not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b',clean),'Unapproved proof construct')
require(re.findall(r'^import (.+)$',clean,re.M)==['Mathlib.Tactic.NormNum','Mathlib.Data.Nat.Choose.Basic'],'Import boundary')
names=re.findall(r'^theorem (\w+)\s*:',clean,re.M);prints=re.findall(r'^#print axioms KappaCheck\.ShrunkBirthTerminal\.(\w+)',clean,re.M)
require(len(names)==len(set(names))==240 and set(names)==set(prints),'Theorem/axiom print coverage')
for path,digest in receipt['compile_receipts'].items():require(sha(LEAN/path)==digest,'Compile receipt '+path)
log=(LEAN/'receipts/compile/output.log').read_text();entries=re.findall(r"'KappaCheck\.ShrunkBirthTerminal\.(\w+)' depends on axioms: \[([^]]*)\]",log)
require(len(entries)==240 and {name for name,_ in entries}==set(names),'Compiled theorem identity coverage')
allowed={'propext','Classical.choice','Quot.sound'}
for name,axioms in entries:require(set(x.strip()for x in axioms.split(',')if x.strip())<=allowed,'Extra axiom '+name)
require((LEAN/'receipts/compile/exit-code').read_text().strip()=='0' and receipt['exit_code']==0 and receipt['lean']=='4.21.0' and receipt['mathlib_commit']=='308445d7985027f538e281e18df29ca16ede2ba3','Compiler receipt identity')
require(not re.search(r'(^|\n).*error:',log),'Compiler error marker')
result=dict(status='PASS independent frozen formal-boundary and complete actual-word frame/count audit',audit_source_sha256=sha(Path(__file__)),lean_source_sha256=sha(source),generator_sha256=sha(gen),input_sha256=sha(inp),compile_verification_sha256=sha(LEAN/'verification.json'),source_regeneration_byte_exact=True,actual_word_sha256=sha(word_path),actual_forward_frame_transitions=transitions,distinct_nondegenerate_frames_checked=len(checked),distinct_nested_frame_pairs_checked=len(checked_pairs),copied_centers=copies,all_34_paid_histogram_bins_reconstructed=True,three_stocks=[9909,5400,252],exact_slacks=47,margins=7,independent_taylor_moments='accepted upper and adjacent rejected lower',theorems=240,all_axiom_entries_accounted=True,allowed_axioms=sorted(allowed),no_float_mathematical_input=True,kappa=str(k),remote_compile_repeated=False,external_limitations=['The Lean kernel proves rational inequalities on the supplied logarithm enclosures, not their analytic logarithm meaning or the real exponential enclosure theorem.','The stopped bit moment/ordinary leaf validity, all-size word/compiler and packed routing/phase interfaces, simultaneous basis, prime selection, exact recovery and fixed-tape transfer remain external.','This audit independently reconstructs exact forward binary frame containment, nonsingularity and every histogram bin from the literal word. Reflected/all-column Gaussian scalar identities remain separately bound construction evidence.','The frozen compile record is checked by hashes and all theorem/axiom entries; the remote compilation was performed by the parent and is not duplicated here.'])
no_float(result);(HERE/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('PASS formal audit',sha(HERE/'receipt.json'))
