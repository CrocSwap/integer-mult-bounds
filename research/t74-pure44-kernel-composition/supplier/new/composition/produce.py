"""Portable exact PR2302-kernel + PR2309-alias composition rebuild.
Apache-2.0. Retains upstream authorship; see NOTICE.md and INPUT-SOURCES.json.
Outputs must be external. Original pure44 producer and audits remain independent.
"""
from pathlib import Path
import argparse,copy,difflib,gzip,hashlib,importlib.util,json,os,subprocess,sys,time,resource
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent.parent
sys.path.insert(0,str(HERE/'vendor'))
import word_patch as WP
spec=importlib.util.spec_from_file_location('credited_pure44_producer',HERE.parent/'borrow-extension/produce.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def key(g):return tuple(g[:-1])
def match(a,b):
 pairs={};changes=[]
 for tag,i,j,k,l in difflib.SequenceMatcher(None,[key(g)for g in a],[key(g)for g in b],autojunk=False).get_opcodes():
  if tag=='equal':pairs.update(zip(range(i,j),range(k,l)))
  else:changes.append(dict(tag=tag,a=[i,j],b=[k,l]))
 return pairs,changes
def dump(word,path):
 raw=json.dumps(word,separators=(',',':')).encode();path.write_bytes(gzip.compress(raw,mtime=0));return raw
def command(args,log,expect_success=True):
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);p=subprocess.run([sys.executable,'-B',*map(str,args)],capture_output=True,text=True,env=env,timeout=180);log.write_text(p.stdout+p.stderr)
 if expect_success and p.returncode:raise RuntimeError('Independent command failed; see '+str(log))
 if not expect_success and not p.returncode:raise RuntimeError('Mutant unexpectedly accepted: '+str(log))
 return p.returncode

def run(case,out,controls,expected_dir):
 start=time.process_time();caseout=out/case;caseout.mkdir();cfg=json.loads((HERE/'EXPECTED.json').read_text())[case];pure_expected=HERE/'inputs'/f'PURE44-{case}.json.gz';args=[HERE.parent/'borrow-extension/produce.py','--case',case,'--out',caseout/'pure44','--expected',pure_expected]
 if controls:args.append('--controls')
 command(args,caseout/'PURE44-REBUILD.log');purepath=caseout/'pure44/BORROW-WORD.json.gz';assert gzip.decompress(purepath.read_bytes())==gzip.decompress(pure_expected.read_bytes()),'pure44 byte payload differs'
 pre=read(HERE/'inputs'/f'PREKERNEL43-{case}.json.gz');pre['base']=cfg['upstream43_base'];refit=HERE/'inputs'/f'refit_43{case}.json'
 if refit.exists():
  rp=json.loads(refit.read_text())
  for sec,idx,fr in rp['frames']:pre[sec][idx][-1]=fr
  pre['report']['local_profile']=rp['local_profile']
 patch=json.loads((HERE/'inputs'/f'kernel_43{case}.json').read_text());patched=WP.apply_kernel(pre,patch);assert hashlib.sha256(json.dumps(patched,sort_keys=True,separators=(',',':')).encode()).hexdigest()==cfg['upstream43_canonical_payload_sha256'];assert WP.kernel_gate_edit(pre['B'],patched['B'])==patch['declared_gate_edit'];positive=caseout/f'RECOVERED43-{case}.json.gz';dump(patched,positive);command([HERE/'vendor/audit_local.py','--word',positive,'--output',caseout/'RECOVERED43-AUDIT.json'],caseout/'RECOVERED43-AUDIT.log')
 pure=read(purepath);oldnew,diff=match(pre['B'],patched['B']);oldpure,aliasdiff=match(pre['B'],pure['B']);insertions={};deletes=[]
 for entry in diff:
  a,b=entry['a'];c,d=entry['b']
  if a<b:
   assert entry['tag']=='delete';deletes.extend(oldpure[i]for i in range(a,b))
  if c<d:
   assert entry['tag']=='insert'and a in oldpure;insertions.setdefault(oldpure[a],[]).extend(copy.deepcopy(patched['B'][c:d]))
 candidate=copy.deepcopy(pure);body=[];reverse={j:i for i,j in oldpure.items()}
 for j,g in enumerate(pure['B']):
  body.extend(insertions.get(j,[]))
  if j in deletes:continue
  old=reverse.get(j)
  if old in oldnew:g=patched['B'][oldnew[old]]
  body.append(copy.deepcopy(g))
 candidate['B']=body
 for section in ['A','restore']:
  assert [key(g)for g in pre[section]]==[key(g)for g in patched[section]]==[key(g)for g in pure[section]];candidate[section]=copy.deepcopy(patched[section])
 def newcut(old):return old+sum(len(gs)for cut,gs in insertions.items()if cut<old)-sum(cut<old for cut in deletes)
 oldwarps={w[1]:w for w in patched['warps']};assert len(oldwarps)==43;warps=[]
 for rec in pure['warps']:
  rec=copy.deepcopy(rec);rec[0]=newcut(rec[0])
  if rec[1]in oldwarps:rec[2:]=copy.deepcopy(oldwarps[rec[1]][2:])
  warps.append(rec)
 candidate['warps']=warps;candidate['cleanup']=WP.derive_cleanup(candidate,WP.restored_of(pure));prof,inventory=P.recount(candidate);candidate['report']['local_profile']=prof;candidate['report']['width_inventory']=inventory;dest=out/f'BORROW-WORD-44{case}.json.gz';raw=dump(candidate,dest);assert hashlib.sha256(raw).hexdigest()==cfg['composed44_payload_sha256'],'composed byte payload differs'
 if expected_dir:assert raw==gzip.decompress((expected_dir/f'BORROW-WORD-44{case}.json.gz').read_bytes())
 command([HERE/'vendor/audit_local.py','--word',dest,'--output',caseout/'COMPOSED44-AUDIT.json'],caseout/'COMPOSED44-AUDIT.log');mutants=[]
 if controls:
  for q in [518,506]:
   m=copy.deepcopy(candidate);j=next(j for j,g in enumerate(m['B'])if g[0]=='add'and g[2]==q and 112<=g[1]<224);m['B'][j][3]*=-1;m['cleanup']=WP.derive_cleanup(m,WP.restored_of(candidate));mutants.append((f'q{q}-sign',m))
  m=copy.deepcopy(candidate);j=next(j for j,g in enumerate(m['warps'])if g[1]==530);m['warps'][j][2][0]=0;mutants.append(('alias530-singularG',m));m=copy.deepcopy(candidate);op=next(j+1 for j,g in enumerate(m['warps'])if g[1]==530);j=next(j for j,g in enumerate(m['cleanup'])if g[0]=='warp'and g[2]==-op);del m['cleanup'][j];mutants.append(('alias530-inverse-omitted',m))
 for label,m in mutants:
  path=caseout/f'MUTANT-{label}.json.gz';dump(m,path);command([HERE/'vendor/audit_local.py','--word',path,'--output',caseout/f'MUTANT-{label}-AUDIT.json'],caseout/f'MUTANT-{label}.log',False)
 result={'case':case,'status':'PASS_EXACT_PORTABLE_COMPOSITION_REBUILD','pure44_payload_exact':True,'recovered43_payload_exact':True,'composed44_payload_exact':True,'independent_full_operator_audits':True,'targeted_mutants_rejected':len(mutants),'payload_sha256':hashlib.sha256(raw).hexdigest(),'artifact_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'profile':prof,'inventory':inventory,'kernel_changes':diff,'alias_changes':aliasdiff,'own_CPU_seconds':time.process_time()-start};(caseout/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--case',choices=['base','extra','all'],default='all');ap.add_argument('--controls',action='store_true');ap.add_argument('--expected-dir',type=Path);a=ap.parse_args();out=a.out.resolve()
 if out.is_relative_to(PACKAGE.resolve()):raise ValueError('Output must be external to source package')
 out.mkdir(parents=True,exist_ok=False);begin=time.process_time();sources={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()for p in HERE.rglob('*')if p.is_file()and '__pycache__'not in p.parts};results=[run(c,out,a.controls,a.expected_dir.resolve()if a.expected_dir else None)for c in (['base','extra']if a.case=='all'else[a.case])];assert sources=={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()for p in HERE.rglob('*')if p.is_file()and '__pycache__'not in p.parts};report={'status':'PASS_PORTABLE_COMPOSED_BORROW_WORDS','results':results,'composition_inputs_unchanged':True,'source_sha256':sources,'own_CPU_seconds':time.process_time()-begin,'subprocess_CPU_seconds':resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime};(out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='source_sha256'}))
if __name__=='__main__':main()
