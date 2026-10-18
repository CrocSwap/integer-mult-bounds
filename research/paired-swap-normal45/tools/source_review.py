"""Independent literal/operator review of PR2957 and its normal45 composition."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
import argparse,copy,gzip,hashlib,json,os,time,types

def require(c,m):
 if not c:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def load(p,n,expected):
 require(sha(p)==expected,'authenticated helper source');m=types.ModuleType(n);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m

def merge(word,edits,offset=0):
 x=copy.deepcopy(word);allh=[]
 for rw in edits:
  for e in rw['edits']:
   s=e['section'];a=e['start']+(offset if s=='A'else 0);b=e['stop']+(offset if s=='A'else 0)
   require(word[s][a:b]==e['old'],('literal preimage',rw['id'],s,a));allh.append((s,a,b,e['new']))
 for sec in('A','B','restore'):
  hunks=sorted((a,b,n)for s,a,b,n in allh if s==sec);out=[];pos=0
  for a,b,n in hunks:require(a>=pos,'ordered nonoverlap');out+=word[sec][pos:a]+copy.deepcopy(n);pos=b
  out+=word[sec][pos:];x[sec]=out
 bedits=[(a,b,len(n)-(b-a))for s,a,b,n in allh if s=='B']
 for wr in x['warps']:
  p=wr[0];require(not any(a<p<b for a,b,d in bedits),'warp lies inside hunk');wr[0]=p+sum(d for a,b,d in bedits if b<=p and a<p)
 return x

def local_matrix(gs):
 regs=sorted({r for g in gs for r in(g[1:3]if g[0]=='add'else g[1:2])});rows={r:{r:F(1)}for r in regs}
 for g in gs:
  t=g[1]
  if g[0]=='add':
   c=F(g[3],g[4])
   for j,z in rows[g[2]].items():
    z=rows[t].get(j,F(0))+c*z
    if z:rows[t][j]=z
    elif j in rows[t]:del rows[t][j]
  else:
   c=F(g[2],g[3]);rows[t]={j:c*z for j,z in rows[t].items()}
 return rows

def middle(w,aud,dual):
 live=[r for r in range(704)if r not in w['removed']];rows={r:{(r,()):F(1)}for r in live};prog=w['A'][w['prelude_events']:]+w['cut'];by=defaultdict(list)
 for op,wr in enumerate(w['warps'],1):by[wr[0]].append(['warp',wr[1],op])
 for i in range(len(w['B'])+1):
  prog+=by[i]
  if i<len(w['B']):prog.append(w['B'][i])
 prog+=w['restore']
 for g in prog:aud.walg_apply(g,rows,dual,10**6)
 return rows

def complete(x,w,pm):
 pro,inv=pm.frame_report(x);x['report']['local_profile']=pro;x['report']['width_inventory']=inv;t=copy.deepcopy(x);t['A']=t['A'][t['prelude_events']:];x['cleanup']=pm.derive_cleanup(t,pm.restored_of(w));return x,pro,inv

def main(a):
 begin=time.monotonic();manifest=a.source/'MANIFEST.json';require(sha(manifest)=='9cd226a2bf7391e7fbf4a23741bb1934afafbd596aef06f2999a935cd6e44e28','source manifest');mf=read(manifest)
 for n,h in mf.items():require(sha(a.source/n)==h,('source file',n))
 pm=load(a.preload_helper,'review2957_frames','c8fda4674644fcd5cbf39b6645ce148a21daa90a998b678cbe51f970b78b0044');aud=load(a.operator_helper,'review2957_operators','a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90')
 edits=read(a.source/'rewrite/REWRITES.json');require(len(edits)==14,'fourteen groups');swaps=[e for e in edits if e['cls']=='A-commuting-swap'];require(len(swaps)==5,'five new swaps');variants={}
 for variant in('base','extra'):
  parent=read(a.source/('data/WORD-'+variant+'.json.gz'));shipped=read(a.source/('rewrite/FINAL-WORD-'+variant+'.json.gz'));derived,pro,inv=complete(merge(parent,edits),parent,pm);require(derived==shipped,'independent full source derivation')
  require(pro=={'1':2412,'2':636,'3':276,'4':116,'5':26,'8':8},'new local profile');require(inv==parent['report']['width_inventory'],'source widths unchanged');require(len(pm.restored_of(derived))==82,'source private buffers')
  swap_rows=[]
  for rw in swaps:
   es=rw['edits'];require(all(e['section']=='A'for e in es),'A-only swap');lo=min(e['start']for e in es);hi=max(e['stop']for e in es);isolated=merge(parent,[rw]);delta_len=len(isolated['A'])-len(parent['A']);old=parent['A'][lo:hi];new=isolated['A'][lo:hi+delta_len]
   require(local_matrix(old)==local_matrix(new),('exact local matrix',rw['id']));ip,ii=pm.frame_report(isolated);d={str(k):ip.get(str(k),0)-parent['report']['local_profile'].get(str(k),0)for k in set(map(int,ip))|set(map(int,parent['report']['local_profile']))if ip.get(str(k),0)!=parent['report']['local_profile'].get(str(k),0)}
   require(d=={'1':1,'2':-1,'3':-1,'4':1},('each complete five-swap tariff',rw['id'],d));require(ii==inv,'swap inventory')
   bad=copy.deepcopy(new);bad[-1][3]=-bad[-1][3];require(local_matrix(bad)!=local_matrix(old),'sign-error control')
   swap_rows.append({'id':rw['id'],'span':[lo,hi],'old':old,'new':new,'exact_matrix_equality':True,'complete_local_delta':d,'flipped_sign_rejected':True})
  n=read(a.normal_dir/('WORD-'+variant+'.json.gz'));joint,jp,ji=complete(merge(n,edits,122),n,pm);require(jp=={'1':2430,'2':628,'3':282,'4':110,'5':26,'8':8},'actual combined profile');require(ji==n['report']['width_inventory'],'combined widths');require(len(pm.restored_of(joint))==86,'combined private buffers')
  for key in('compensation','initial_corrections','precondition','cut','helper_final','start_extra','removed','prelude_events'):require(joint[key]==n[key],('protected normal45 data',key))
  if a.combined_dir:
   actual=read(a.combined_dir/('WORD-'+variant+'.json.gz'));require(actual==joint,'actual combined word equals independent literal derivation')
  maps={}
  for dual in(False,True):
   pmap=middle(parent,aud,dual);rmap=middle(derived,aud,dual);require(pmap==rmap,('full source middle operator equality',variant,dual))
   nmap=middle(n,aud,dual);jmap=middle(joint,aud,dual);require(nmap==jmap,('full combined middle operator equality',variant,dual));maps['dual'if dual else'forward']={'source':True,'normal45_composed':True,'rows':len(pmap)}
  variants[variant]={'source_word_sha256':sha(a.source/('rewrite/FINAL-WORD-'+variant+'.json.gz')),'source_profile':pro,'normal45_word_sha256':sha(a.normal_dir/('WORD-'+variant+'.json.gz')),'combined_canonical_sha256':pm.canon(joint),'combined_word_sha256':sha(a.combined_dir/('WORD-'+variant+'.json.gz'))if a.combined_dir else None,'combined_profile':jp,'combined_inventory':ji,'private_buffers':86,'new_swap_details':swap_rows,'full_middle_maps':maps}
  print('PASS',variant,flush=True)
 out={'status':'PASS_INDEPENDENT_PR2957_LITERAL_FRAME_AND_FULL_FREE_OPERATOR_COMPOSITION','source_manifest_sha256':sha(manifest),'source_manifest_entries':len(mf),'checker_sha256':sha(Path(__file__)),'variants':variants,'seconds':time.monotonic()-begin,'scope':'All 14 literal edits independently merged with exact preimages; five new swaps checked as exact local matrices with fresh complete frame tariffs and sign controls; full 632-row middle free-operator maps compared in forward and dual orientations. Compensation, prelude, widths, buffers and normal45 protected data stay fixed. This does not replace fresh Clifford phases, actual owner roles, magnitude or outer admission.'}
 require(not a.out.exists(),'fresh output');a.out.parent.mkdir(exist_ok=True,parents=True);lk=a.out.with_name(a.out.name+'.lock');fd=os.open(lk,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
 try:require(not a.out.exists(),'fresh locked output');a.out.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 finally:lk.unlink()
 print(out['status'],sha(a.out),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--normal-dir',type=Path,required=True);ap.add_argument('--combined-dir',type=Path);ap.add_argument('--preload-helper',type=Path,required=True);ap.add_argument('--operator-helper',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);main(ap.parse_args())
