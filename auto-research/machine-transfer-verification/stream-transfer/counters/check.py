#!/usr/bin/env python3
"""Fresh isolated kernel rebuild and complete theorem axiom audit. Installs nothing."""
import argparse,hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
AUDIT=re.compile(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",re.M)
DECL=re.compile(r'^\s*(?:@\[[^\]]*\]\s*)?theorem\s+(\w+)\b',re.M)
def require(ok,msg):
 if not ok:raise SystemExit(msg)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--lake-project',required=True,type=Path)
 p.add_argument('--tapes-dir',type=Path,default=HERE.parents[1]/'transfer-proof'/'tapes')
 p.add_argument('--output',type=Path,default=HERE/'verification')
 a=p.parse_args();project=a.lake_project.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 m=json.loads((HERE/'theorem-manifest.json').read_text())
 require((project/'lean-toolchain').read_text().strip()==m['lean_toolchain'],'Wrong Lean project pin')
 pkgs=json.loads((project/'lake-manifest.json').read_text())['packages'];ml=[x for x in pkgs if x['name']=='mathlib']
 require(len(ml)==1 and ml[0]['rev']==m['mathlib_revision'],'Wrong Mathlib pin')
 dep=a.tapes_dir.resolve()/m['dependency']['file']
 require(digest(dep)==m['dependency']['sha256'],'Changed TapeStack dependency')
 sources=[dep]+[HERE/name for name in m['files']]
 inventories={}
 for src in sources:
  s=src.read_text();names=[src.stem+'.'+n for n in DECL.findall(s)]
  prints=[n if '.' in n else src.stem+'.'+n for n in re.findall(r'^#print axioms (\S+)\s*$',s,re.M)]
  require(len(names)==len(set(names)) and len(prints)==len(names) and set(prints)==set(names),'Missing theorem audit: '+src.name)
  require(not re.search(r'\b(sorry|admit|native_decide)\b|^\s*(axiom|constant)\s',s,re.M),'Proof escape: '+src.name)
  if src!=dep:
   require(digest(src)==m['files'][src.name]['sha256'] and names==m['files'][src.name]['theorems'],'Source/declaration hash: '+src.name)
  inventories[src.name]=names
 env=os.environ.copy();env.pop('LEAN_PATH',None)
 lakeenv=json.loads(subprocess.check_output(['lake','env','python3','-c','import os,json;print(json.dumps(dict(os.environ)))'],cwd=project,env=env,text=True))
 version=subprocess.check_output(['lean','--version'],cwd=project,env=lakeenv,text=True).strip()
 require(re.search(r'version 4\.21\.0(?:,|\s)',version),'Wrong actual compiler')
 allowed={'propext','Quot.sound','Classical.choice'}
 require(set(m['allowed_axioms'])==allowed,'Unexpected axiom policy')
 report={'status':'PASS','compiler':version,'mathlib_revision':m['mathlib_revision'],'files':{}}
 with tempfile.TemporaryDirectory(prefix='ripple-kernel-') as d:
  tmp=Path(d);lakeenv['LEAN_PATH']=str(tmp)+os.pathsep+lakeenv.get('LEAN_PATH','')
  for src in sources:
   local=tmp/src.name;shutil.copy2(src,local)
   r=subprocess.run(['lean','--root='+str(tmp),'-o',str(local.with_suffix('.olean')),str(local)],cwd=project,env=lakeenv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
   (out/(src.stem+'.log')).write_text(r.stdout)
   require(r.returncode==0,'Compile failed: '+src.name+'; inspect log')
   entries=AUDIT.findall(r.stdout)
   require(len(entries)==len(inventories[src.name]) and {n for n,_ in entries}==set(inventories[src.name]),'Incomplete axiom receipt: '+src.name)
   axs={n:sorted({x.strip() for x in a.split(',') if x.strip()}) for n,a in entries}
   require(all(set(v)<=allowed for v in axs.values()),'Nonstandard axiom: '+src.name)
   report['files'][src.name]={'sha256':digest(src),'theorems':axs}
   print('PASS',src.name,len(entries),'audits',flush=True)
 report['new_declaration_count']=sum(len(v['theorems']) for k,v in report['files'].items() if k!=dep.name)
 report['dependency_declaration_count']=len(report['files'][dep.name]['theorems'])
 (out/'axiom-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS',report['new_declaration_count'],'new +',report['dependency_declaration_count'],'dependency audits')
if __name__=='__main__':main()
