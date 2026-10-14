"""Independent closed-form audit of the outer bootstrap refinement.
No circuit/native claims: checks the saved witness and controls only.
"""
import argparse,copy,hashlib,json
from fractions import Fraction as Q
from pathlib import Path

def require(ok,message):
 if not ok:raise ValueError(message)
def read(p):return json.loads(p.read_text())
def seed_from_legacy(old):
 b=Q(old['complex_lower']);c=Q(old['bit_lower']);s=min(c,(1-Q(1,10**24))*b)-Q(1,10**27)
 seed=(Q(old['bootstrap'][0]['exponent'])-(1-s)*s)/s
 require(0<seed<s,'legacy seed')
 for i,row in enumerate(old['bootstrap'],1):require(Q(row['exponent'])==s-(s-seed)*s**i,'legacy closed form')
 return seed
def check(asm,old,options,payload):
 require(asm['complex_lower']==old['complex_lower'] and asm['bit_lower']==old['bit_lower'],'unchanged endpoints')
 require(asm['complex_profile']==old['complex_profile'],'unchanged paid profile')
 seed=seed_from_legacy(old);eta=beta=Q(1,10**options['margin_digits']);step=Q(1,10**options['grid_digits']);backoff=eta/1000
 b=Q(asm['complex_lower']);c=Q(asm['bit_lower']);s=min(c,(1-beta)*b)-backoff
 require(0<seed<s<c and s<(1-beta)*b,'strict target slack')
 require(len(asm['bootstrap'])==options['bootstrap_steps'],'bootstrap count')
 prev=seed
 for i,row in enumerate(asm['bootstrap'],1):
  a=s-(s-seed)*s**i;gap=min(s-a,1-a-s,1-a-s*(1-prev),1-s);cut=int(row['cutoff_log2'])
  require(Q(row['exponent'])==a and Q(row['gap'])==gap,'closed form or gap')
  require(prev<a<s<1-a and gap>0,'strict bootstrap')
  require(cut*gap*gap>=36 and cut*gap>=2*(4+payload),'cutoff')
  prev=a
 q=prev*(1-2*eta);margin=(1-eta)*q/(1+q);k=Q(asm['kappa']);require(k<margin<k+step,'strict last grid bracket')
 require(k>Q(old['kappa']),'strict predecessor gain')
 # All seven outer work margins, computed from q, eta and a.
 eps=(1-eta)/(1+q);delta=eta/8;r=((eps*q)+(1-eps))/2
 margins=[1-eps,prev,eps*q,prev,min(1-eps-delta,r-delta),1-eps-delta,eps]
 require(all(x>k for x in margins),'all seven work margins')
 require(len(asm['outer'])==47 and all(Q(x)>0 for x in asm['outer'].values()),'retained 47 positive slacks')
 return dict(kappa=str(k),absolute_gain=str(k-Q(old['kappa'])),bootstrap_steps=options['bootstrap_steps'],closed_form='a_n = s - (s-a_0)*s^n',grid=str(step),minimum_margin=str(min(margins)),absorption_gap=str(margin-k))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--assembly',type=Path,required=True);ap.add_argument('--legacy',type=Path,required=True);ap.add_argument('--spec',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();asm=read(a.assembly);old=read(a.legacy);spec=read(a.spec);opts=spec['outer_refinement'];payload=spec['geometry']['charged_prefix_bits'];result=check(asm,old,opts,payload);controls=[]
 def reject(name,obj):
  try:check(obj,old,opts,payload)
  except ValueError:controls.append(name)
  else:raise ValueError('accepted mutant '+name)
 bad=copy.deepcopy(asm);bad['kappa']=str(Q(asm['kappa'])+Q(1,10**opts['grid_digits']));reject('next_grid',bad)
 bad=copy.deepcopy(asm);bad['bootstrap'][0]['exponent']=str(Q(bad['bootstrap'][0]['exponent'])+Q(1,10**opts['grid_digits']));reject('altered_bootstrap_exponent',bad)
 bad=copy.deepcopy(asm);bad['bootstrap'][-1]['cutoff_log2']='0';reject('missing_cutoff',bad)
 bad=copy.deepcopy(asm);bad['bootstrap']=bad['bootstrap'][:-1];reject('omitted_bootstrap_step',bad)
 bad=copy.deepcopy(asm);bad['complex_lower']=str(Q(bad['complex_lower'])+Q(1,10**24));reject('changed_inherited_endpoint',bad)
 out=dict(status='PASS_INDEPENDENT_CLOSED_FORM_BOOTSTRAP_AND_GRID',**result,rejected=controls,inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [a.assembly,a.legacy,a.spec]},scope='Independent closed-form bootstrap and seven work margins; retained assembly supplies the 47-slack replay. No new construction, native replay or unconditional theorem.')
 require(not a.out.exists(),'output already exists');a.out.write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['kappa'])
if __name__=='__main__':main()
