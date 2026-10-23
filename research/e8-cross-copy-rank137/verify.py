"""Fresh reconstruction. Python3.11+, SymPy, C++17 and Boost headers.
Usage: python -B verify.py NEW_OUTPUT [--parent-output FULL_PR447_OUTPUT] [--research-root RESEARCH]
Default runs the complete PR447 wrapper first. --parent-output explicitly reuses its existing full receipt.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--parent-output',type=Path);ap.add_argument('--research-root',type=Path,default=ROOT.parent);a=ap.parse_args()
out=a.output.resolve();research=a.research_root.resolve();assert not out.exists() and not out.is_relative_to(research)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 m={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts}
 assert m==read(ROOT/'MANIFEST.json')
 src=read(ROOT/'SOURCE.json');assert sha(research/'e8-eleven-hosting-selected/MANIFEST.json')==src['parent_manifest_sha256']
 assert sha(research/'e8-hosting-selected-kernel/PRECURSOR.json')==src['precursor_sha256']
integrity();out.mkdir(parents=True);steps=[];PY=sys.executable
UP=research/'e8-rank138-idle-hosting/upstream443';BIT=UP/'parent436/code/bit';CK=BIT/'checkers';C450=ROOT/'vendor450/code';C448=ROOT/'vendor448'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONPATH=os.pathsep.join(map(str,[UP/'code',C448,research/'e8-eleven-hosting-selected/code'])));env.pop('PYTHONOPTIMIZE',None)
def run(name,cmd):
 start=time.monotonic();log=out/(name+'.log');print('RUN',name,flush=True)
 with log.open('w') as f:p=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0,(name,log.read_text()[-3500:]);steps.append(dict(name=name,seconds=round(time.monotonic()-start,2),log_sha256=sha(log)));print('PASS',name,flush=True)
def py(name,path,*args):run(name,[PY,'-B',path,*args])
try:
 parent=a.parent_output.resolve() if a.parent_output else out/'parent447'
 if a.parent_output:assert read(parent/'RECEIPT.json')['status']=='PASS_FULL_ELEVEN_HOSTING_SELECTED'
 else:py('full-parent447',research/'e8-eleven-hosting-selected/verify.py',parent)
 # One exact selection deletion relative to the pinned rank138 precursor.
 sys.path.insert(0,str(UP/'code'));from replica_kernel import kernel
 from e8core import replay
 prior=read(UP/'data/selection.json');sel=read(ROOT/'data/kernel-selection.json')
 assert sel['removed_pivot']==744 and sel['entries']==[e for e in prior['entries'] if e[1]!=sel['removed_pivot']]
 w,n,rank,donors=kernel(read(research/'e8-hosting-selected-kernel/PRECURSOR.json'),sel['entries'],64)
 local=replay(w,span_mode='z');assert not local['viol'] and rank==137
 (out/'word.json').write_text(json.dumps(w,sort_keys=True,separators=(',',':')))
 py('mix',C450/'mix_target.py',out/'word.json',out/'word-mixed.json')
 assert sha(out/'word-mixed.json')==read(ROOT/'SOURCE.json')['mixed_word_sha256']
 py('export',BIT/'export_records.py',out/'word-mixed.json',out/'records')
 py('mix-check',C450/'mix_check.py',out/'word-mixed.json',out/'records','--controls',out/'word.json')
 py('cohort',BIT/'regression/stage_cohort.py',out/'records',out/'records',out/'cin',out/'cout')
 (out/'bin').mkdir();cxx=os.environ.get('CXX','c++');boost=os.environ.get('BOOST_INCLUDE','/opt/homebrew/include' if Path('/opt/homebrew/include/boost').exists() else '/usr/include')
 for name,file,defs in [('legality','legality_h.cpp',['NCOPY=9']),('legality_ncopy_h','legality_h.cpp',[]),('columns_h','columns_h.cpp',['NCOPY=9','VPORTS=120','RHELP=740']),('columns_k5','columns_k.cpp',['NCOPY=9','VPORTS=120','RHELP=740','KPAIRS=5'])]:
  run('compile-'+name,[cxx,'-O2','-std=c++17','-DHDIM=8',*['-D'+d for d in defs],'-I'+str(CK),'-I'+str(UP/'parent436/portable-include'),'-I'+boost,'-o',out/'bin'/name,CK/file])
 run('legality',[out/'bin/legality',out/'cin',out/'cout',out/'cout/legality.json'])
 for name,dest in [('columns_h','columns.json'),('columns_k5','columns_k5.json')]:run(name,[out/'bin'/name,out/'cout/COHORT249-RECORDS.bin',out/'cout'/dest])
 py('record-mutations',BIT/'mutate_records.py',out/'records',out/'cin',out/'cout',out/'bin/legality',out/'bin/columns_k5',out/'bin/legality_ncopy_h')
 py('gram',CK/'gram_frames.py',out/'records','--gram','e8ham','--h',8,'--positive')
 (out/'nine').mkdir()
 py('geometry',C450/'geometry_k.py','--source',UP/'parent436','--out',out/'nine','--stages',11,'--no-timing')
 py('global',C450/'global_k.py','--word',out/'word-mixed.json','--local-check',out,'--out',out/'nine','--isometries',UP/'data/residual-isometries.json','--stages',11,'--replicas',8,'--no-banks')
 py('parent-audit',C450/'audit_parent_k.py','--local-check',out,'--out',out/'nine','--word',out/'word-mixed.json')
 py('hosted',C450/'emit_tape_k.py',out/'nine',out,out/'hosted','--selection',ROOT/'data/hosting-selection.json','--key','bit11_tape','--host-all','--depth',3,'--redigest','--version-tag','e8-rank137-cross-copy-v1')
 py('hosted-audit',C450/'audit_tape_k.py',out,out/'hosted',out/'hosted/AUDIT.json')
 py('complex',C448/'complex_split.py',parent/'parent/changed/split-centres',out/'upstream/complex')
 py('complex-audit',ROOT/'code/audit_complex.py',parent,out/'upstream')
 py('assembly',ROOT/'code/assemble.py',out,out/'upstream',out/'hosted',out/'hosted/AUDIT.json',out/'RESULT.json','--route-extra',3,'--parent-kappa','269548909542967/200000000000000000','--label','PR450')
 actual=read(out/'RESULT.json')
 for k,v in read(ROOT/'EXPECTED.json').items():assert actual[k]==v,(k,actual[k],v)
 integrity();receipt=dict(status='PASS_COMPONENT_REPLAY_PARENT_REUSED' if a.parent_output else 'PASS_FULL_RANK137_CROSS_COPY',python=sys.version.split()[0],kappa=actual['kappa'],manifest_sha256=sha(ROOT/'MANIFEST.json'),parent_receipt_sha256=sha(parent/'RECEIPT.json'),checks=steps)
 (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
