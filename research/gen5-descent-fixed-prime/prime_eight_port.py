#!/usr/bin/env python3
"""Chen: fixed-prime/eight-leaf transfer on actual gen5/291 literal costs.

Arithmetic method: Nespoli PR235, Arun PR243, sennemmi PR253.
This is a compatible recomputation, not an additive combination of exponents.
"""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util,json,hashlib,sys,time,argparse
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];SOURCE=P/'source';RUN=ROOT/'.research-cache/gen5-291/run'
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 sys.path.insert(0,str(SOURCE))
 assert __debug__;start=time.monotonic()
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,default=RUN);ap.add_argument('--admission',type=Path,default=P/'receipt.json');ap.add_argument('--output',type=Path,default=P/'prime-eight-certificate.json');args=ap.parse_args();run=args.run.resolve()
 accepted=json.loads(args.admission.read_text());assert accepted['inputs_unchanged'] and accepted['status'].startswith('PASS')
 base=json.loads((run/'certificate.json').read_text());finite=json.loads((run/'finite.json').read_text());primes=json.loads((run/'primes.json').read_text());banks=json.loads((run/'banks.json').read_text())['banks']
 old=json.loads((P/'prime-proof.json').read_text());q=old['prime']['q'];assert q==2**127-1
 funcs=[SOURCE/'moment.py',SOURCE/'base_two_moment.py',SOURCE/'outer.py',SOURCE/'finite_check.py',P/'methods/fixed_prime_math.py']
 cost,other,outer,cutoff,fixed=[load('gen5prime'+str(i),p)for i,p in enumerate(funcs)]
 bp=base['bit_profile'];m=int(bp['m']);W=int(bp['W']);H={int(r):n for r,n in bp['histogram'].items()};E=sum(H.values());mass=sum(r*n for r,n in H.items())
 assert (m,W,mass,m*W-mass,max(H))==(120,248903,29815560,52800,50)
 assert bp['physical_replicas']==60 and bp['literal_stock']==1244515==5*W and bp['literal_children']==5*E and bp['literal_rank_mass']==5*mass
 inv=finite['paid_inventory'];coef=finite['q_power_bound']['coefficient'];selector=inv['extra_bank_selector_calls']
 assert inv['physical_replicas']==60 and inv['literal_stock']==1244515 and inv['positive_rank_children']==5*E and inv['rank_mass']==5*mass
 assert banks['assignments']==4765800 and banks['charts']==545 and inv['normalizer_factor_bound']==815
 assert selector==932937188400==2*5*60*((1244515-1)+15886*120*815)<2**40
 assert primes['all_remaining_factors_below_2_power_80'] and q>2**primes['maximum_determinant_bits']
 assert inv['fallback_per_child']==32*m*m and coef<2**80<q and finite['row_reserve']['internal_coefficient']==14401
 assert fixed.RHO==Q(3456000,q) and fixed.PRIME==q and fixed.ETA==Q(1,10**24) and fixed.GRID==10**27
 c,excluded=fixed.certify_coarse(H,m,W,cost)
 pa=fixed.fixed_moment(H,m,W,c,cost);pe=fixed.fixed_moment(H,m,W,excluded,cost)
 ia=fixed.second_engine_with_fallback(H,m,W,c,other);ie=fixed.second_engine_with_fallback(H,m,W,excluded,other)
 assert pa[1]<1<pe[0] and ia[1]<1<ie[0]
 assert cost.moment(H,m,W,c,True)[0]>1,'old fallback density must not certify this point'
 literal={r:5*n for r,n in H.items()};assert cost.moment(literal,m,1244515,c,False)==cost.moment(H,m,W,c,False)
 assert Q(32*m*sum(literal.values()),1244515)==Q(32*m*E,W)
 delta_linear=1-Q(mass,m*W)-fixed.RHO*Q(32*m*E,W);assert delta_linear>0
 chain=[Q(384599,10**10)];steps=[]
 def predecessor(level,pred):assert level>=1 and pred==level-1
 for j in range(1,9):
  predecessor(j,j-1);prev=chain[-1];a=(1-c)*c+c*prev;gaps=dict(atom=c-a,borrowing=1-a-c,remainder=1-a-c*(1-prev),stock=1-c)
  assert prev<a<c and min(gaps.values())>0 and a==c-c**j*(c-chain[0])
  delta=min(gaps.values());L=cutoff.cutoff_log2(delta,coef);assert L*delta**2>=36 and L*delta>=2*(4+(coef-1).bit_length())
  steps.append(dict(level=j,predecessor=j-1,gaps=gaps,cutoff_log2_at_actual_coefficient=L,full_rule='C_full(q,j) pays the actual gen5 coefficient, all inherited primitives, prime-table, wrapper and predecessor constants.'))
  chain.append(a)
 b=Q(base['complex_coarse']);assert b==Q(747454944651775,10**18)
 bridge=base['finite_bridge'];bridge['rows']['degree_gap']=Q(bridge['rows']['degree_gap'])
 k=fixed.grid_kappa(chain[-1]);assembly=outer.assembly(chain[-1],b,bridge,k,eta=fixed.ETA,beta=fixed.BETA)
 assert len(assembly['strict_constraints'])==47 and len(assembly['margins'])==7
 previous=Q(base['kappa']);assert k>previous
 controls=['adjacent coarse rejected by both engines','old density rejected at new rate']
 for label,a in [('actual eighth leaf',chain[-1]),('unattained coarse cap',c)]:
  try:outer.assembly(a,b,bridge,k+Q(1,fixed.GRID),eta=fixed.ETA,beta=fixed.BETA)
  except AssertionError:controls.append('adjacent final rejected at '+label)
  else:raise AssertionError('adjacent final admitted at '+label)
 def feecheck(T,S,K,N):assert (T,S,K,N)==(60,1244515,932937188400,815)
 for bad in [(40,1244515,932937188400,815),(60,869195,932937188400,815),(60,1244515,626938189600,815),(60,1244515,932937188400,423)]:
  try:feecheck(*bad)
  except AssertionError:controls.append('wrong copies/stock/selector/normalizer rejected: '+str(bad))
  else:raise AssertionError('foreign fee admitted')
 try:predecessor(8,8)
 except AssertionError:controls.append('cyclic eighth level rejected')
 else:raise AssertionError('cyclic recurrence admitted')
 inputs=funcs+[Path(__file__),args.admission,run/'certificate.json',run/'finite.json',run/'primes.json',run/'banks.json',P/'prime-proof.json']
 def label(p):return str(p.relative_to(ROOT))if p.is_relative_to(ROOT)else str(p)
 out=dict(status='PASS actual gen5/291 fixed-prime eight finite levels and outer assembly',kappa=k,previous_published_kappa=previous,gain=k-previous,coarse=c,excluded_coarse=excluded,public_accepted=pa,public_excluded=pe,independent_accepted=ia,independent_excluded=ie,bit_profile=bp,complex_profile=base['complex_profile'],complex_saving=b,rare_density=fixed.RHO,prime=old['prime'],prime_positive_replayed=False,ordinary_chain=chain,steps=steps,delta_linear=delta_linear,assembly=assembly,eta=fixed.ETA,beta=fixed.BETA,selector=selector,normalizer=815,coefficient=coef,q_power_bound='complete coefficient and inherited constants bounded via q^14401 and explicit C_full(q,j)',controls=controls,seconds=time.monotonic()-start,physical_supplier_replayed=False,own_captured_bank_gain_included=False,source_authors='Chafik Boukhalfa, DreamingOfClouds, Rohan Arun, eumemic and inherited NOTICE authors; fixed-prime method Gabriele Nespoli/Rohan Arun/sennemmi; exact current-cost transfer Zhihao Chen',input_pins={label(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputs})
 args.output.write_text(json.dumps(fixed.serial(out),indent=2)+'\n');print(json.dumps({k:fixed.serial(out[k])for k in ['status','kappa','gain','coarse','coefficient','seconds']}),flush=True)
if __name__=='__main__':main()
