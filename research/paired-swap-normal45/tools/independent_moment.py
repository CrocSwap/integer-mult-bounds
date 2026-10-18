"""Independent standard-library exact four-way moment and native-tariff review."""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
import argparse,json,gzip,hashlib,types,os
S=1<<192

def ceildiv(a,b):return -(-a//b)
@lru_cache(None)
def log_small(n,d):
 assert d<=n<=2*d
 u=n-d;v=n+d;t2n=u*u;t2d=v*v;pn=u;pd=v;lo=0;N=128
 for j in range(N):lo+=(2*S*pn)//((2*j+1)*pd);pn*=t2n;pd*=t2d
 # ln(x)=2 sum t^(2j+1)/(2j+1); bound the uncomputed tail by a geometric series.
 tail=ceildiv(2*S*pn*t2d,(2*N+1)*pd*(t2d-t2n))if pn else 0
 return lo,lo+N+tail
@lru_cache(None)
def log_ratio(n,d):
 k=0
 while n>=2*d:d*=2;k+=1
 a,b=log_small(n,d);c,e=log_small(2,1)
 return a+k*c,b+k*e

def exp_interval(xlo,xhi):
 assert 0<=xlo<=xhi<S
 lo=hi=S;tl=th=S;N=40
 for j in range(1,N+1):
  tl=(tl*xlo)//(S*j);th=ceildiv(th*xhi,S*j);lo+=tl;hi+=th
 # Successive exact tail ratios are < 1/2 because x < 1 and N >= 1.
 tail_next=ceildiv(th*xhi,S*(N+1));return lo,hi+2*tail_next

def moment(profile,T,b):
 low=high=0
 for r,c in profile.items():
  r=int(r);assert 0<r<73 and c>0
  L,U=log_ratio(73,r);eL,eU=exp_interval((b.numerator*L)//b.denominator,ceildiv(b.numerator*U,b.denominator))
  low+=c*r*eL;high+=c*r*eU
 den=73*896*T;return F(low,S*den),F(high,S*den)

def require(c,why):
 if not c:raise ValueError(why)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main(a):
 report=read(a.report);require(digest(a.report)=='edd6d0d0b17fdf8517f44ff414f031a77d2a48ecb7f96af08c5bba340ebf8727','frozen report')
 require(digest(a.report.parent/'MANIFEST.json')=='fc500bc30f6d252d88ff2589b75f068c83ecb5466bb07e7b3a3126354b1a4765','frozen manifest')
 manifest=read(a.report.parent/'MANIFEST.json')
 for name,sha in manifest['files'].items():require(digest(a.report.parent/name)==sha,('artifact manifest',name))
 require(digest(a.preload_helper)=='c8fda4674644fcd5cbf39b6645ce148a21daa90a998b678cbe51f970b78b0044','authenticated helper source')
 pm=types.ModuleType('reviewed_frame_rules');pm.__file__=str(a.preload_helper);exec(compile(a.preload_helper.read_bytes(),str(a.preload_helper),'exec'),pm.__dict__)
 prefixes={'B':'both-off','N':'normal45-only','R':'rewrites-only','NR':'WORD'};checks={};native={}
 for tag,sc in report['scenarios'].items():
  T=sc['T'];require(T==370 and sc['roles']==9*T*408,'actual call/role normalization');profile=read(a.report.parent/(tag+'-PROFILE.json'));require(profile==sc['profile'],'profile bytes')
  mass=sum(int(r)*c for r,c in profile.items());require(mass==65088*T,'rank mass');require(F(mass,73*896*T)==F(1017,1022),'M(0)')
  require(sc['physical']==896*T+408+8+sc['private_buffers']+2,'full stock incl buffers')
  lo,hi=F(sc['lower']),F(sc['upper']);require(F(sc['lower_decimal'])==lo and F(sc['upper_decimal'])==hi,'decimal/rational root endpoints')
  L=moment(profile,T,lo);U=moment(profile,T,hi);require(L[1]<1<U[0],('strict exact root bracket',tag))
  checks[tag]={'mass':mass,'normalization':str(F(mass,73*896*T)),'lower_moment_upper':str(L[1]),'upper_moment_lower':str(U[0]),'root_lower':str(lo),'root_upper':str(hi)}
  for variant in('base','extra'):
   wordpath=a.word_dir/(prefixes[tag]+'-'+variant+'.json.gz');rec=report['actual_native_words'][tag][variant];require(digest(wordpath)==rec['word_sha256'],'actual word SHA')
   w=json.loads(gzip.decompress(wordpath.read_bytes()));local,inv=pm.frame_report(w);buf=len(pm.restored_of(w));require(local==rec['local_profile']and inv==rec['width_inventory']and buf==rec['buffers']==sc['private_buffers'],'fresh actual local/width/buffer tariff')
   ap=a.word_dir/(prefixes[tag]+'-'+variant+'-AUDIT.json');require(digest(ap)==rec['native_audit_sha256'],'inherited exact audit SHA');ar=read(ap);require(ar['status']=='PASS_INDEPENDENT_EXACT_BORROWING_WORD'and ar['checked_columns']==632,'inherited all-column audit status')
   native[tag+'-'+variant]={'word_sha256':rec['word_sha256'],'local_profile':local,'width_inventory':inv,'buffers':buf,'audit_scope':'Inherited exact forward/dual receipt hash checked; phase chain not re-executed.'}
 B,N,R,NR=[report['scenarios'][t]for t in('B','N','R','NR')]
 gain_total_upper=F(NR['upper'])-F(B['lower']);gains={}
 for name,removed in [('normal45',R),('nine_rewrites',N)]:
  gain_lower=F(NR['lower'])-F(removed['upper']);gain_upper=F(NR['upper'])-F(removed['lower']);ratio=gain_lower/gain_total_upper;st=report['ablations'][name]
  require(gain_lower==F(st['gain_lower'])and gain_upper==F(st['gain_upper'])and ratio==F(st['fraction_of_total_gain_lower']),'exact leave-one-out arithmetic');require(ratio>F(1,10),'ten percent significance')
  gains[name]={'gain_lower':str(gain_lower),'gain_upper':str(gain_upper),'fraction_lower':str(ratio),'passes_ten_percent':True}
 # Both actual scenarios exhibit the same native rewrite delta at 9T calls.
 for old,new in [(B,R),(N,NR)]:
  ranks=set(old['profile'])|set(new['profile']);delta={r:new['profile'].get(r,0)-old['profile'].get(r,0)for r in ranks if new['profile'].get(r,0)!=old['profile'].get(r,0)}
  require(delta=={'1':-9*9*370,'2':9*370,'3':9*370,'4':9*370},'actual rewrite delta')
 claim=read(a.comparison_claim);require(digest(a.comparison_claim)==report['comparison_claim_sha256'],'current comparison claim');require(F(NR['lower'])-F(claim['kappa'])==F(report['gain_over_PR2948_full_claim_lower']),'full-claim margin')
 # Exact negative controls on the root criterion and ablation arithmetic.
 bad=dict(NR['profile']);bad['1']+=1
 rejected=[]
 for name,predicate in [('rank-mass corruption',sum(int(r)*c for r,c in bad.items())==65088*370),('altered contribution',F(report['ablations']['normal45']['gain_lower'])+F(1,10**25)==F(NR['lower'])-F(R['upper']))]:
  try:require(predicate,name)
  except ValueError:rejected.append(name)
 require(len(rejected)==2,'both negative controls rejected')
 out={'status':'PASS_INDEPENDENT_FOUR_WAY_TARIFF_NORMALIZATION_DIRECTED_MOMENT_AND_ABLATION_ARITHMETIC','source_report_sha256':digest(a.report),'checker_sha256':digest(Path(__file__)),'precision_bits':192,'scenarios':checks,'actual_native_tariffs':native,'ablations':gains,'negative_controls':rejected,'scope':'All eight actual local/width/buffer tariffs freshly recounted. Exact directed moments and ratios independently implemented with integer interval arithmetic. Complete owner roles and native phase/outer admission are separate and were not replayed by this checker.'}
 require(not a.out.exists(),'fresh review output');a.out.parent.mkdir(parents=True,exist_ok=True);lk=a.out.with_name(a.out.name+'.lock');fd=os.open(lk,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
 try:require(not a.out.exists(),'fresh locked output');a.out.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 finally:lk.unlink()
 print(out['status']);print('receipt',digest(a.out));print('ratios',gains)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,required=True);ap.add_argument('--word-dir',type=Path,required=True);ap.add_argument('--preload-helper',type=Path,required=True);ap.add_argument('--comparison-claim',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);main(ap.parse_args())
