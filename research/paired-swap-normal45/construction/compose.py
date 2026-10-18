"""Pure, source-pinned composition of PR2957's declared rewrites onto PR2942's normal45 words.

Apache-2.0. Credit Marius-Paul Dumitrean / PR2942, Jeremy Kothe / PR2957,
Mason Hale / PR2917 and Jeremy Diviney / PR2908, with the retained upstream lineage.
The first two R-retimes coincide with this campaign's independently found commuting
pair and are applied exactly once. No claim of broad-method novelty is made.
"""
import copy,hashlib,json
PINS={'base': {'normal45': {'compressed_sha256': '54ca34c749e3228d7e2df3d8dbf7aa1568c2872490166997c5962f12fd03da35', 'canonical_sha256': 'ac76f19e387829367acd1ed09e68a202759b503273099cc2b9f4d7c7653df08a'}, 'parent2917': {'compressed_sha256': 'fec3c120db1a35022944628d34b56a36f2456248c274c2eaba1a325cdc690ce8', 'canonical_sha256': 'a12f573f321757976cd754f70ad395a981592dfc47e1c9b22f73ef4988a10492'}}, 'extra': {'normal45': {'compressed_sha256': 'eded756dfe8f411c3d1f80a3ac16516f0ea5dd6f9866728b2179b157630fa7b6', 'canonical_sha256': '87dd650a58659ce31d38567f171eb4e421e84ca880b24722921495cdd1795f33'}, 'parent2917': {'compressed_sha256': 'e4d0c617df85bf8a824ff68310ca3373dc017c1ebf9ea733056a3ee4a784b36f', 'canonical_sha256': '346914b627b0340adf904c2abc5858368a488cbc2105c1973c44d02089f7e0f4'}}}
REWRITES_SHA='4606e169e5af85a2187d0aeeb8ffca01634cfadf4ed8a16b881d1394e09c55d4'
CLASSES=('R-retime','A3779-cut-start-read','PM-carrier-lender-entry','B-carrier-retime','A-commuting-swap')
PM_SHA='c8fda4674644fcd5cbf39b6645ce148a21daa90a998b678cbe51f970b78b0044'
AUDIT_SHA='a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90'
def require(ok,why):
 if not ok:raise ValueError(str(why))
def canon(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def compose(normal45,parent2917,rewrites,pm,classes=None):
 """Pure function. Inputs and metadata remain immutable; returns actual word and full literal ledger."""
 matches=[v for v in PINS if canon(normal45)==PINS[v]['normal45']['canonical_sha256'] and canon(parent2917)==PINS[v]['parent2917']['canonical_sha256']]
 mode='normal45'
 if not matches:
  matches=[v for v in PINS if canon(normal45)==PINS[v]['parent2917']['canonical_sha256'] and canon(parent2917)==PINS[v]['parent2917']['canonical_sha256']];mode='parent2917'
 require(len(matches)==1,'exact normal45/common-parent or parent-only source pins');variant=matches[0]
 require(len(rewrites)==14 and {r['cls'] for r in rewrites}==set(CLASSES),'exact fourteen declared rewrites/five classes')
 require(hashlib.sha256(json.dumps(rewrites,separators=(',',':')).encode()).hexdigest()=='4606e169e5af85a2187d0aeeb8ffca01634cfadf4ed8a16b881d1394e09c55d4','exact declared rewrite content')
 chosen=set(CLASSES if classes is None else classes);require(chosen<=set(CLASSES),'declared class subset')
 n=parent2917['prelude_events'];shift=len(normal45['A'])-len(parent2917['A'])
 require(n==84 and normal45['prelude_events']==n and shift==(122 if mode=='normal45' else 0),'exact shared-parent index shift')
 require(normal45['A'][:n]==parent2917['A'][:n],'all84prelude events identical')
 require([g[:-1] for g in normal45['A'][n+shift:]]==[g[:-1] for g in parent2917['A'][n:]],'entire old A scalar chronology preserved after122normal45input gates')
 require(normal45['B']==parent2917['B'] and normal45['warps']==parent2917['warps'],'common B/warp source')
 require(normal45['restore'][:len(parent2917['restore'])]==parent2917['restore'],'exact old restore prefix before normal45output gates')
 x=copy.deepcopy(normal45);edits=[];ledger=[]
 for rw in rewrites:
  if rw['cls'] not in chosen:continue
  for e in rw['edits']:
   sec=e['section'];a=e['start'];b=e['stop'];require(sec in ['A','B','restore'],'declared section')
   require(parent2917[sec][a:b]==e['old'],'original PR2917 literal preimage')
   if sec=='A':require(a>=n,'no prelude change');a+=shift;b+=shift
   require(normal45[sec][a:b]==e['old'],('normal45 mapped exact preimage',variant,rw['id'],sec,a,b))
   edits.append((sec,a,b,copy.deepcopy(e['new'])))
   ledger.append({'rewrite_id':rw['id'],'class':rw['cls'],'section':sec,'source2917_start':e['start'],'source2917_stop':e['stop'],'normal45_start':a,'normal45_stop':b,'old':copy.deepcopy(e['old']),'new':copy.deepcopy(e['new'])})
 for sec in ['A','B','restore']:
  es=sorted((a,b,new) for s,a,b,new in edits if s==sec);out=[];pos=0
  for a,b,new in es:require(a>=pos,'nonoverlapping mapped hunks');out+=x[sec][pos:a]+new;pos=b
  out+=x[sec][pos:];x[sec]=out
 bedits=[(a,b,len(new)-(b-a)) for sec,a,b,new in edits if sec=='B'];warpmapping=[]
 for op,rec in enumerate(x['warps'],1):
  before=copy.deepcopy(rec);p=rec[0];require(not any(a<p<b for a,b,d in bedits),'no warp hidden in deleted span')
  rec[0]=p+sum(d for a,b,d in bedits if b<=p and a<p)
  require(rec[1:]==before[1:],'operator/lender/frame fields unchanged')
  warpmapping.append({'operator_id':op,'old_position':p,'new_position':rec[0],'old_record':before,'new_record':copy.deepcopy(rec)})
 profile,inventory=pm.frame_report(x);require(inventory==normal45['report']['width_inventory'],'ordered helper widths remain normal45 inventory')
 x['report']['local_profile']=profile;z=copy.deepcopy(x);z['A']=z['A'][n:];x['cleanup']=pm.derive_cleanup(z,set(map(int,x['helper_final'])))
 require(x['A'][:84]==normal45['A'][:84],'all84prelude events unchanged after composition')
 require({a for a in x if x[a]!=normal45[a]}<={'A','B','restore','warps','report','cleanup'},'only declared scalar/frame chronology and derived metadata changed')
 for key in ['helper_final','compensation','precondition','start_extra','removed','centers','center_frames','ports','target_levels','cut','initial_corrections','prelude_events']:
  require(x[key]==normal45[key],('all normal45 source/target/cold/dirty ABI fields unchanged',key))
 return x,{'variant':variant,'base_mode':mode,'normal45_canonical_sha256':canon(normal45),'parent2917_canonical_sha256':canon(parent2917),'classes':sorted(chosen),'mapped_edits':ledger,'warp_position_mapping':warpmapping,'local_profile':profile,'width_inventory':inventory,'buffers':len(x['helper_final']),'source_heads':{'normal45':'a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf','rewrites':'b74b25f3ccc84c16e1a801d73b2f47e5ea764c78','common_parent':'224bd5e56041c40078ff6b5fa7393733a215de5c'}}

def main():
 import argparse,gzip,types,sys,os,io,contextlib,time
 from pathlib import Path
 sys.dont_write_bytecode=True
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--normal45',type=Path,required=True);p.add_argument('--rewrites-package',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--ablations',action='store_true');a=p.parse_args()
 lock=Path(str(a.out)+'.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
 try:
  require(not a.out.exists(),'fresh output directory');a.out.mkdir();started=time.time()
  def loadmodule(name,path,pin):
   b=path.read_bytes();require(hashlib.sha256(b).hexdigest()==pin,'pinned implementation source '+name);m=types.ModuleType(name);exec(compile(b,str(path),'exec'),m.__dict__);return m
  pm=loadmodule('pm',a.normal45/'vendor/preload_move.py',PM_SHA);aud=loadmodule('aud',a.normal45/'vendor/audit_local.py',AUDIT_SHA)
  rawrw=(a.rewrites_package/'rewrite/REWRITES.json').read_bytes();require(hashlib.sha256(rawrw).hexdigest()==REWRITES_SHA,'rewrite file source SHA');rw=json.loads(rawrw);result={'status':'PASS_COMBINED_2942_2957_EXACT_WORDS','variants':{},'scope':'Exact forward/dual free-operator/frame audits; all phases/native/owner/global/outer admission remain separate'}
  for v in ['base','extra']:
   nr=(a.normal45/('data/WORD-'+v+'.json.gz')).read_bytes();pr=(a.rewrites_package/('data/WORD-'+v+'.json.gz')).read_bytes();require(hashlib.sha256(nr).hexdigest()==PINS[v]['normal45']['compressed_sha256'],'normal45 file SHA');require(hashlib.sha256(pr).hexdigest()==PINS[v]['parent2917']['compressed_sha256'],'parent file SHA');N=json.loads(gzip.decompress(nr));P=json.loads(gzip.decompress(pr));variants=[('combined',None,N)]
   if a.ablations:variants += [('normal45-only',[],N),('rewrites-only',None,P),('both-off',[],P)]+[(cl,[cl],N) for cl in CLASSES]+[('PM-plus-B',['PM-carrier-lender-entry','B-carrier-retime'],N)]
   reports={}
   for tag,cls,baseword in variants:
    try:x,ledger=compose(baseword,P,rw,pm,cls)
    except ValueError as error:
     if tag=='combined':raise
     reports[tag]={'status':'REJECTED_ABLATION','reason':str(error)};print(v,tag,'REJECTED_ABLATION',str(error),flush=True);continue
    name=('WORD-'+v) if tag=='combined' else (tag+'-'+v);path=a.out/(name+'.json.gz');path.write_bytes(gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0))
    with contextlib.redirect_stdout(io.StringIO()):report=aud.run(path,a.out/(name+'-AUDIT.json'))
    ledger['word_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();ledger['exact_audit_status']=report['status'];(a.out/(name+'-EDITS.json')).write_text(json.dumps(ledger,indent=2),encoding='utf8');reports[tag]={'word':path.name,'sha256':ledger['word_sha256'],'profile':ledger['local_profile'],'exact_audit_status':report['status']}
    print(v,tag,ledger['local_profile'],ledger['word_sha256'],flush=True)
   result['variants'][v]=reports
   require(hashlib.sha256((a.normal45/('data/WORD-'+v+'.json.gz')).read_bytes()).hexdigest()==PINS[v]['normal45']['compressed_sha256'],'normal45 source unchanged')
  result['elapsed_seconds']=time.time()-started;(a.out/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(result['status'],result['elapsed_seconds'],flush=True)
 finally:os.close(fd);lock.unlink()
if __name__=='__main__':main()
