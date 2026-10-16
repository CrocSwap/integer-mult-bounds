# SPDX-License-Identifier: Apache-2.0
"""Independent source-bound owner/profile/moment review for the preload-move staged words (provider registry shipped with the candidate)."""
import argparse,hashlib,json,os,types
from pathlib import Path
from fractions import Fraction as Q

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(p,m):
 if not p:raise AssertionError(m)
def code(name,path,expected):
 body=path.read_bytes();need(hashlib.sha256(body).hexdigest()==expected,'executed source bytes '+name);m=types.ModuleType(name);m.__file__=str(path);exec(compile(body,str(path),'exec'),m.__dict__);return m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--claim',type=Path);ap.add_argument('--field',default='claim');a=ap.parse_args();need(not a.out.exists(),'fresh output');here=Path(__file__).resolve().parent
 lc=code('literal_core',here/'literal_core.py','f5b36146de862c4f9f68412b1a9177409cb390ad4051b0f71483f36591e6a5d6');mc=code('moment_core',here/'moment_core.py','22290074f138fa9b902e5f6f6e8a0ec366d6f812992adb6df9b617ce952fb852');mc.BITS=512;mc.S=1<<512;mc.LOG_TERMS=220;mc.EXP_TERMS=114
 localpins=lc.rd(a.package/'LOCAL-PINS.json');sourcefiles=['PROFILE.json','CLAIM.json','ORDER.json','DISPATCH.json','words/WORD-base.json.gz','words/WORD-extra.json.gz','sources/PR2833-T37-TEMPLATE.json.gz'];pins={};candidatefiles=['FILL.json.gz','ORDER.json','DISPATCH.json','PROFILE.json','PROVIDERS.json']
 for n in sourcefiles:
  h=sha(a.package/n);need(localpins[n]==h,'actual source pin '+n);pins['source/'+n]=h
 for n in candidatefiles:pins['candidate/'+n]=sha(a.candidate/n)
 providers=lc.rd(a.candidate/'PROVIDERS.json');need(set(providers)=={'extra','gauge44'},'fixed current provider registry')
 for pid in providers:
  need(len(providers[pid]['widths'])==408,'all current helpers');need(providers[pid]['actual_paid_profile']=={'1':2404,'2':642,'3':262,'4':128,'5':26,'8':8},'actual preload-move staged local price')
 order=lc.rd(a.candidate/'ORDER.json');dispatch_list=lc.rd(a.candidate/'DISPATCH.json');dispatch={(s,r):p for s,r,p in dispatch_list};T=len(order)//9
 need(T>0 and len(order)==9*T and len(set(map(tuple,order)))==9*T and len(dispatch_list)==len(dispatch)==9*T,'full actual call partition')
 need(set(dispatch)==set(map(tuple,order))and all(pid in providers for pid in dispatch.values()),'actual selected provider per call')
 context=lc.chronology(lc.rd(a.package/'sources/PR2833-T37-TEMPLATE.json.gz'),order,T);fill=lc.rd(a.candidate/'FILL.json.gz');H,idle=lc.audit(fill,order,dispatch,providers,context,T)
 need(H=={int(r):n for r,n in lc.rd(a.candidate/'PROFILE.json').items()},'exact complete candidate profile')
 negative=[]
 def reject(name,mut):
  f=lc.copy.deepcopy(fill);mut(f)
  try:lc.audit(f,order,dispatch,providers,context,T)
  except AssertionError:negative.append(name);return
  raise AssertionError('corruption accepted '+name)
 reject('missing_helper',lambda f:f['rows'].pop());reject('noninteger_descriptor',lambda f:f['rows'][0].__setitem__(0,.5));reject('slice_capacity_overflow',lambda f:f['rows'][0].__setitem__(5,100));reject('hidden_dispatch_override',lambda f:f['dispatch_overrides'].append([0,'forged']))
 claimpath=a.claim or a.candidate/'MOMENT-RECEIPT.json';pins['claim']=sha(claimpath);alpha=mc.rational(lc.rd(claimpath)[a.field]);lo,hi,_=mc.moment(H,896*T,73,alpha);need(hi<0,'full moment not strictly certified');baseline=Q(lc.rd(a.package/'CLAIM.json')['kappa']);need(alpha>baseline,'claim not strictly above actual current frontier')
 native={}
 for c in order:
  for r,n in providers[dispatch[tuple(c)]]['actual_paid_profile'].items():native[int(r)]=native.get(int(r),0)+n
 need(all(H.get(r,0)>=n for r,n in native.items()),'all native paid ranks present')
 for n in sourcefiles:need(sha(a.package/n)==pins['source/'+n],'source changed during review')
 for n in candidatefiles:need(sha(a.candidate/n)==pins['candidate/'+n],'candidate changed during review')
 need(sha(claimpath)==pins['claim'],'claim changed during review')
 result=dict(status='PASS_INDEPENDENT_CURRENT_STAGED_OWNER_MOMENT_REVIEW',source_head='0b2e2537b368a0cade07ce3f71452ea018ebe394',input_sha256=pins,replicas=T,calls=9*T,roles=len(fill['rows']),physical=896*T+490,source_events=30*T+2,profile=H,idle_profile=idle,rank_mass=sum(r*n for r,n in H.items()),moment_interval_scaled=[str(lo),str(hi)],scale='2^512',above_complete_current_frontier=True,negative_controls_rejected=negative,scope='Independent literal chronology/windows/families/masks/prefixes/current-provider profile and exact directed moment. No constructor or solver imports. Fresh native phase/primitive and complete compiler/precision/release guards remain separate.')
 lock=a.out.with_name(a.out.name+'.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
 try:a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
 finally:lock.unlink()
 print(json.dumps(result,sort_keys=True,indent=2))
if __name__=='__main__':main()
