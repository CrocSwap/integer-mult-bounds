"""New-profile-only exact outer assembly, adapted from PR387; no public replay.
PR387's six-level wrapper is credited to its PR185 bootstrap sources. The
balanced 47-constraint engine retains eumemic/icekylinx/Zhihao Chen/RaD credits.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json,hashlib,sys
sys.dont_write_bytecode=True
ENGINE=Path(__file__).resolve().parent/'engines'
assert ENGINE.is_dir(), 'Bundled engines directory missing'
BIT=Q(255384852701747,250000000000000000)
def module(name):
 p=ENGINE/(name+'.py');s=importlib.util.spec_from_file_location('newprofile_'+name,p);o=importlib.util.module_from_spec(s);s.loader.exec_module(o);return o

def ceil(q):return -(-q.numerator//q.denominator)
def cutoff(delta,ell):
 assert delta>0 and isinstance(ell,int) and ell>=1
 L=ceil(max(Q(1),36/delta**2,2*(4+ell)/delta))
 assert L*delta**2>=36 and L*delta>=2*(4+ell)
 return L

def coarse(profile,m,stock):
 H={int(k):int(v) for k,v in profile.items() if v};assert all(0<r<m and n>0 for r,n in H.items())
 M=module('moment');B=module('base_two_moment');z=M.certify(H,m,stock,True);lo=Q(z['lower']);hi=Q(z['upper'])
 assert hi-lo==Q(1,10**24)
 lv=M.moment(H,m,stock,lo,True);hv=M.moment(H,m,stock,hi,True)
 f=32*m*m*sum(H.values());density=Q(1,10**16)
 _,bu=B.moment(m,stock,list(H.items()),lo);_,bf=B.moment(m,stock,[(1,f)],lo)
 bl,_=B.moment(m,stock,list(H.items()),hi);bfl,_=B.moment(m,stock,[(1,f)],hi)
 assert lv[1]<1<hv[0] and bu+density*bf<1<bl+density*bfl
 return dict(lower=str(lo),upper=str(hi),m=m,stock=stock,profile=H,deficit=m*stock-sum(r*n for r,n in H.items()),density=str(density),fallback_rank_one_calls=f,first_lower_residual=str(lv[1]-1),first_upper_residual=str(hv[0]-1),second_lower_residual=str(bu+density*bf-1),second_upper_residual=str(bl+density*bfl-1),scope='Exact moment on supplied paid counts; count realization and finite supplier admission are separate hypotheses.')

def assemble(b,bridge,c=BIT,depth=6,eta=Q(1,10**18),beta=Q(1,10**18),backoff=Q(1,10**24),grid=Q(1,10**18)):
 b,c=Q(b),Q(c);assert 0<eta<Q(1,4) and 0<beta<1 and 0<b<Q(1,32) and 1<=depth<=12
 # User must supply the changed construction's bridge, not old PR-specific constants.
 assert set(('semantic','rows')).issubset(bridge)
 assert Q(bridge['semantic']['strict_literal_gap'])>0 and Q(bridge['rows']['degree_gap'])>0
 bridge=json.loads(json.dumps(bridge));bridge['rows']['degree_gap']=Q(bridge['rows']['degree_gap'])
 s=min(c,(1-beta)*b)-backoff;initial=Q(384599,10**10)
 assert 0<initial<s<min(c,(1-beta)*b)
 chain=[initial];stages=[]
 for j in range(depth):
  old=chain[-1];a=(1-s)*s+s*old
  assert old<a<s<1-a and a==s-s**(j+1)*(s-initial)
  gaps=dict(atom=s-a,borrowing=1-a-s,remainder=1-a-s*(1-old),stock=1-s);d=min(gaps.values());assert d>0
  stages.append(dict(level=j+1,ordinary_calls_only_to_level=j,gaps={k:str(v) for k,v in gaps.items()},cutoff_rule='For any fixed C<2^ell use e0=2^ceil(max(1,36/delta^2,2*(4+ell)/delta))',cutoff_example_constant_bits80=str(cutoff(d,80))))
  chain.append(a)
 a=chain[-1];q=a*(1-2*eta);margin=(1-eta)*q/(1+q);z=margin/grid;k=grid*((z.numerator-1)//z.denominator)
 asm=module('outer').assembly(a,b,bridge,k,eta=eta,beta=beta)
 assert len(asm['strict_constraints'])==47 and asm['minimum_margin']==margin
 controls=[]
 for name,kk,ee,bb in [('grid_at_or_above_margin',k+grid,eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0))]:
  try:module('outer').assembly(a,b,bridge,kk,eta=ee,beta=bb)
  except AssertionError:controls.append(name)
  else:raise AssertionError('accepted '+name)
 return dict(status='PASS_EXACT_NEW_PROFILE_CONDITIONAL_OUTER',kappa=str(k),kappa_float=float(k),complex_coarse=str(b),bit_coarse=str(c),saving=str(s),bootstrap_depth=depth,eta=str(eta),beta=str(beta),backoff=str(backoff),chain=list(map(str,chain)),stages=stages,strict_constraints={k:str(v) for k,v in asm['strict_constraints'].items()},margins={k:str(v) for k,v in asm['margins'].items()},minimum_margin=str(margin),absorption_gap=str(margin-k),bridge=json.loads(json.dumps(bridge,default=str)),controls_rejected=controls,outer_engine_sha256=hashlib.sha256((ENGINE/'outer.py').read_bytes()).hexdigest(),scope='Conditional supplier assembly. Requires the supplied bridge to dominate changed supplier constants/rows, completed arbitrary-width ordinary calls with restored borrowed rows and finite tapes, plus inherited compressed-window, arbitrary-dirty-bank, Clifford/compiler, precision and analytic contracts. Exact inequalities alone do not prove these interfaces or an unconditional multiplication exponent.')

if __name__=='__main__':
 import argparse
 assert __debug__
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('input',nargs='?',type=Path,help='JSON containing bridge and complex_coarse, or profile,m,stock')
 ap.add_argument('output',nargs='?',type=Path)
 ap.add_argument('--b',help='Exact certified new complex coarse saving')
 ap.add_argument('--bridge',type=Path,help='Changed supplier bridge JSON, required with --b')
 ap.add_argument('--bit',default=str(BIT),help='Exact bit coarse saving, default inherited value')
 ap.add_argument('--out',type=Path)
 args=ap.parse_args()
 if args.b:
  assert args.bridge is not None and args.input is None
  x=dict(complex_coarse=args.b,bit_coarse=args.bit,bridge=json.loads(args.bridge.read_text(encoding='utf-8-sig')))
  input_digest=hashlib.sha256(args.bridge.read_bytes()).hexdigest()
 else:
  assert args.input is not None
  x=json.loads(args.input.read_text(encoding='utf-8-sig'));input_digest=hashlib.sha256(args.input.read_bytes()).hexdigest()
 out=args.out or args.output;assert out is not None and not out.exists()
 if 'profile' in x:
  r=coarse(x['profile'],x['m'],x['stock']);b=r['lower']
 else:r=None;b=x['complex_coarse']
 a=assemble(b,x['bridge'],x.get('bit_coarse',str(BIT)))
 if r:a['coarse_receipt']=r
 a['input_sha256']=input_digest
 if 'supplier_receipt_sha256' in x:a['supplier_receipt_sha256']=x['supplier_receipt_sha256']
 a['engine_sha256']={n:hashlib.sha256((ENGINE/(n+'.py')).read_bytes()).hexdigest() for n in ('outer','moment','base_two_moment')}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(a,indent=2)+'\n',encoding='utf-8');print(a['kappa'],a['kappa_float'])
