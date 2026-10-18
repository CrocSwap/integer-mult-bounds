#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fresh algebra/frames, four literal owner assignments, directed moments and ablation.
Retained native/outer receipts are bound separately, never called fresh by this command.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,collections,contextlib,gc,gzip,hashlib,io,json,os,sys,types
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def put(p,x):
 p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
def tree(p):
 need(not any(f.is_symlink()for f in p.rglob('*')),'no package symlinks')
 return {f.relative_to(p).as_posix():sha(f)for f in p.rglob('*')if f.is_file()and f!=p/'MANIFEST.json'}
def load(path,name):
 m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);modes=ap.add_mutually_exclusive_group();modes.add_argument('--finite-only',dest='finite_only',action='store_true');modes.add_argument('--bind-release',dest='finite_only',action='store_false');ap.set_defaults(finite_only=True);a=ap.parse_args()
 need(not sys.flags.optimize,'assertions must be enabled')
 pins=read(P/'MANIFEST.json');need(tree(P)==pins,'complete immutable package inventory')
 out=a.work.resolve();need(not out.exists()and not out.is_relative_to(P)and not P.is_relative_to(out),'fresh external work')
 lock=Path(str(out)+'.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
 try:
  out.mkdir(parents=True)
  pm=load(P/'vendor/preload_move.py','pm');aud=load(P/'vendor/audit_local.py','aud');comp=load(P/'construction/compose.py','comp');owner=load(P/'vendor/independent_owners.py','owners');root=load(P/'vendor/root.py','root');independent=load(P/'tools/independent_moment.py','independent')
  rw=read(P/'data/REWRITES.json');need(sha(P/'data/REWRITES.json')==comp.REWRITES_SHA,'exact declared rewrite source')
  plan=read(P/'vendor/PLAN.json.gz');template=read(P/'vendor/TEMPLATE.json.gz');order=read(P/'allocation/ORDER.json');dispatch={(s,r):pid for s,r,pid in read(P/'allocation/DISPATCH.json')}
  need(len(order)==3330,'all 370 replicas and 3330 calls')
  expected=read(P/'evidence/ABLATIONS.json');scenarios={};word_reports={};first_joint=None
  for scenario,normal,rewrites,fillname,buffers in [('B',False,False,'ABLATION-BASELINE-FILL.json.gz',82),('R',False,True,'ABLATION-BASELINE-FILL.json.gz',82),('N',True,False,'FILL.json.gz',86),('NR',True,True,'FILL.json.gz',86)]:
   providers={};word_reports[scenario]={}
   for v,pid in [('base','gauge44'),('extra','extra')]:
    parent=read(P/f'inputs/PARENT-{v}.json.gz');start=read(P/f'inputs/NORMAL45-{v}.json.gz')if normal else parent
    w,ledger=comp.compose(start,parent,rw,pm,None if rewrites else [])
    if scenario=='NR':
     need(w==read(P/f'data/WORD-{v}.json.gz'),'regenerated complete canonical combined word '+v)
     path=P/f'data/WORD-{v}.json.gz'
     if first_joint is None:first_joint=(w,dict(ledger))
    else:
     path=out/f'{scenario}-{v}.json.gz';path.write_bytes(gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0))
    with contextlib.redirect_stdout(io.StringIO()):report=aud.run(path,out/f'{scenario}-{v}-AUDIT.json')
    report=read(out/f'{scenario}-{v}-AUDIT.json')  # Normalize integer JSON object keys exactly as the recorded audit.
    need(report['status']=='PASS_INDEPENDENT_EXACT_BORROWING_WORD'and report['checked_columns']==632,'fresh exact all-column replay')
    need(report['orientations']=={'forward':'PASS','dual':'PASS'},'both orientations')
    pro,inv=pm.frame_report(w);need(pro==report['local_profile']==w['report']['local_profile'],'actual paid profile')
    need(inv==report['width_inventory']==w['report']['width_inventory'],'actual frame inventory')
    need(len(w['helper_final'])==buffers,'actual private buffers')
    helpers=sorted(set(range(224,704))-set(w['removed']));need(len(helpers)==408,'all live helpers')
    widths=[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[]))for h in helpers]
    providers[pid]={'widths':widths,'actual_paid_profile':{int(r):n for r,n in pro.items()}}
    word_reports[scenario][v]={'canonical_sha256':comp.canon(w),'audit_sha256':sha(out/f'{scenario}-{v}-AUDIT.json'),'profile':pro,'buffers':buffers}
   need(providers['gauge44']==providers['extra'],'provider tariff/width equivalence')
   if scenario=='NR':
    shipped=read(P/'allocation/PROVIDERS.json')
    for x in shipped.values():x['actual_paid_profile']={int(k):n for k,n in x['actual_paid_profile'].items()}
    need(providers==shipped,'registry derived from actual word')
   fill=read(P/'allocation'/fillname);result,_,_=owner.check(370,order,fill,dispatch,None,plan,template,providers)
   need(result['roles']==1358640 and result['rank_mass']==24082560,'complete roles and rank mass')
   profile={str(r):n for r,n in result['profile'].items()};need(profile==expected['scenarios'][scenario]['profile'],'exact complete profile '+scenario)
   lo,hi=root.kappa_from_profile(profile,370,digits=26)
   need(lo==Q(expected['scenarios'][scenario]['lower'])and hi==Q(expected['scenarios'][scenario]['upper']),'directed root bracket '+scenario)
   need(independent.moment(profile,370,lo)[1]<1<independent.moment(profile,370,hi)[0],'independent 192-bit integer interval root check '+scenario)
   scenarios[scenario]={'profile':profile,'root_lower':str(lo),'root_upper':str(hi),'roles':result['roles'],'physical':896*370+408+8+buffers+2}
   put(out/f'{scenario}-OWNERS.json',result);print('PASS fresh',scenario,'words, all literal owners, exact root',flush=True)
   del fill,result;gc.collect()
  # Fresh corruption controls address whole-assignment failures, not code coverage.
  fill=read(P/'allocation/FILL.json.gz');controls={}
  def reject(name,fn):
   try:fn()
   except (ValueError,AssertionError,KeyError,IndexError)as e:controls[name]=str(e)
   else:raise ValueError('accepted corruption '+name)
  reject('missing_role',lambda:owner.check(370,order,{**fill,'rows':fill['rows'][:-1]},dispatch,None,plan,template,providers))
  row=list(fill['rows'][1]);row[:2]=fill['rows'][0][:2]
  reject('duplicate_helper',lambda:owner.check(370,order,{**fill,'rows':[fill['rows'][0],row]+fill['rows'][2:]},dispatch,None,plan,template,providers))
  row2=list(fill['rows'][0]);row2[5]=49
  reject('capacity_overflow',lambda:owner.check(370,order,{**fill,'rows':[row2]+fill['rows'][1:]},dispatch,None,plan,template,providers))
  bad=read(P/'inputs/NORMAL45-base.json.gz');parent=read(P/'inputs/PARENT-base.json.gz');bad['A'][84][3]*=-1
  reject('wrong_source_preimage',lambda:comp.compose(bad,parent,rw,pm))
  jointlo=Q(scenarios['NR']['root_lower']);jointhi=Q(scenarios['NR']['root_upper']);totalupper=jointhi-Q(scenarios['B']['root_lower']);ablations={}
  for name,without in [('normal45','R'),('fourteen_rewrites','N')]:
   gain=jointlo-Q(scenarios[without]['root_upper']);need(gain>Q(1,10)*totalupper,'significant exact ablation '+name);ablations[name]={'gain_lower':str(gain),'fraction_lower':str(gain/totalupper)}
  if a.finite_only:
   need(tree(P)==pins,'immutable finite package');put(out/'RESULT.json',{'status':'PASS_FRESH_FINITE_EIGHT_WORDS_FOUR_OWNERS_MOMENTS_AND_ABLATIONS_ONLY','scenarios':scenarios,'ablations':ablations,'words':word_reports,'controls':controls,'source_files':pins,'scope':'Fresh finite algebra/frame/cleanup, literal owner and independent exact moment checks only. Native/outer release not replayed or bound by finite-only mode.'});print('PASS_FRESH_FINITE_EIGHT_WORDS_FOUR_OWNERS_MOMENTS_AND_ABLATIONS_ONLY',flush=True);return
  claim=read(P/'CLAIM.json');need(Q(claim['kappa'])<jointlo and Q(claim['kappa'])>Q(read(P/'comparators/PR2957-CLAIM.json')['kappa']),'conservative strict headline comparison')
  admission=read(P/'evidence/ADMISSION-RESULT.json');release=read(P/'evidence/RELEASE-RECEIPT.json');native=read(P/'evidence/NATIVE-RECEIPT.json')
  need(admission['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE','bound retained complete admission and release statuses')
  need(admission['release_receipt_sha256']==sha(P/'evidence/RELEASE-RECEIPT.json'),'release receipt binding')
  need(Q(admission['kappa'])==Q(release['kappa_decimal'])==Q(claim['kappa']),'headline equality')
  need(admission['source_manifest_sha256']==native['manifest_sha256']==claim['source_manifest_sha256'],'full source binding')
  need(admission['fill_sha256']==sha(P/'allocation/FILL.json.gz'),'literal fill bound into full admission')
  for v in ['base','extra']:need(native['providers'][v]['word_sha256']==sha(P/f'data/WORD-{v}.json.gz'),'native bound to actual combined word')
  need(tree(P)==pins,'read-only package drift')
  result={'status':'PASS_FRESH_EIGHT_WORDS_FOUR_FULL_OWNER_MOMENT_ABLATIONS_AND_BOUND_RELEASE','scenarios':scenarios,'ablations':ablations,'words':word_reports,'controls':controls,'kappa':claim['kappa'],'scope':'Fresh exact algebra/frames/cleanup, four complete finite owner assignments, directed roots and ablations. Stored full native/outer evidence is source-bound, not re-executed by this bounded command. Use reproduce.py for fresh native/outer admission; all-size multiplication hypotheses remain conditional.'}
  put(out/'RESULT.json',result);print(result['status'],flush=True)
 finally:os.close(fd);lock.unlink()
if __name__=='__main__':main()
