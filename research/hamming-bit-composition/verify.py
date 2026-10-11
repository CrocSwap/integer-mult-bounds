"""Fresh complex, retimed native bit, compressed banks and finite composition."""
from pathlib import Path
from fractions import Fraction as Q
import gzip,hashlib,importlib.util,json,os,shutil,struct,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent;CX=ROOT.parent/'hamming-frame-retiming';BIT=ROOT.parent/'hamming-mutable-basis-complex/work/pr370-source/research/e8-bit/data/bit/bitE8-r865.json.gz'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 assert {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json'}==read(ROOT/'MANIFEST.json')['files']
 assert sha(CX/'MANIFEST.json')==read(ROOT/'SOURCE.json')['complex_manifest_sha256']
 for p,h in read(CX/'MANIFEST.json')['files'].items():assert sha(CX/p)==h
integrity();out=Path(sys.argv[1]).resolve();assert not out.exists() and not out.is_relative_to(ROOT.parent);out.mkdir(parents=True);checks=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
import runpy
compat=CX/'compat';runpy.run_path(str(compat/'sitecustomize.py'));env['PYTHONPATH']=str(compat)+os.pathsep+env.get('PYTHONPATH','')
def run(name,args,reject=False):
 print('RUN',name,flush=True);t=time.monotonic();log=out/(name+'.log')
 with log.open('w') as f:q=subprocess.run(list(map(str,args)),env=env,stdout=f,stderr=subprocess.STDOUT)
 assert (q.returncode!=0 if reject else q.returncode==0),(name,q.returncode)
 checks.append(dict(name=name,rejection_expected=reject,seconds=time.monotonic()-t,log_sha256=sha(log)));print('PASS',name,flush=True)
def py(name,file,*args):run(name,[sys.executable,'-B',file,*args])
try:
 py('full-complex431',CX/'verify.py',out/'complex')
 cx=read(out/'complex/RESULT.json');assert cx['status']=='PASS_FULL_HAMMING_FRAME_RETIMING_AND_SOURCE425_REPLAY'
 bit=out/'bit';bit.mkdir();sel=read(ROOT/'vendor/retiming/frame-selection.json');sp=importlib.util.spec_from_file_location('bit_frame_replay',ROOT/'vendor/retiming/frame_replay.py');F=importlib.util.module_from_spec(sp);sp.loader.exec_module(F)
 word=F.reconstruct(BIT.read_bytes(),sel);controls=F.negative_controls(BIT.read_bytes(),sel);expected=read(ROOT/'EXPECTED-BIT.json');assert sha(BIT)==expected['source_sha256'] and hashlib.sha256(word).hexdigest()==expected['retimed_sha256']
 (bit/'word.json').write_bytes(word);(bit/'source/data/bit').mkdir(parents=True);(bit/'source/data/bit/bitE8-r865.json.gz').write_bytes(gzip.compress(word,mtime=0));shutil.copyfile(ROOT/'EXPECTED-BIT.json',bit/'PRICE.json');(bit/'WITNESS-CONTROLS.json').write_text(json.dumps(controls,indent=2)+'\n')
 native=ROOT/'vendor/native';B=native/'code/bit';CK=B/'checkers';rec=bit/'records';cin=bit/'cin';cout=bit/'cout'
 py('export',B/'export_records.py',bit/'word.json',rec);py('stage',B/'regression/stage_cohort.py',rec,rec,cin,cout)
 for name,source,flags in [('columns',CK/'columns_h.cpp',['-DHDIM=8','-DNCOPY=9','-DVPORTS=120','-DRHELP=865']),('legality',CK/'legality_h.cpp',['-DHDIM=8','-DNCOPY=9'])]:
  inc=['-I'+str(CK),'-I'+str(ROOT/'vendor/compressed/portable-include')]
  if env.get('BOOST_INCLUDE'):inc+=['-I'+env['BOOST_INCLUDE']]
  run('compile-'+name,[env.get('CXX','g++'),'-O2','-std=c++17',*inc,*flags,source,'-o',bit/name])
 run('native-columns',[bit/'columns',rec/'249-records.bin',cout/'columns.json']);run('native-legality',[bit/'legality',cin,cout,cout/'legality.json'])
 rows=[list(x) for x in struct.iter_unpack('<6i',(rec/'249-records.bin').read_bytes())];phaseB=[i for i,e in enumerate(rows) if e[0]==1 and e[5]==4]
 cases=[('drop-target-add',phaseB[len(phaseB)//2],None,'columns'),('wrong-add-frame',phaseB[0],(4,0),'legality'),('undercharged-move',next(i for i,e in enumerate(rows) if e[0]==0 and e[4]>1),(4,-1),'legality'),('undercharged-copy',next(i for i,e in enumerate(rows) if e[0]==2),(5,7),'legality'),('drop-dirty-compensation',next(i for i,e in enumerate(rows) if e[0]==1 and e[5]==1),None,'columns')]
 for name,idx,change,kind in cases:
  d=bit/('mutant-'+name);shutil.copytree(cout,d);bad=[x[:] for x in rows]
  if change is None:del bad[idx]
  elif change==(4,-1):bad[idx][4]-=1
  else:bad[idx][change[0]]=change[1]
  f=d/'COHORT249-RECORDS.bin';f.write_bytes(b''.join(struct.pack('<6i',*x) for x in bad))
  run(name,[bit/'columns',f,d/'rejected.json'] if kind=='columns' else [bit/'legality',cin,d,d/'rejected.json'],reject=True)
 py('exact-gram',CK/'gram_frames.py',rec,'--gram','e8ham','--h','8','--positive')
 g=bit/'global';py('compressed-geometry',ROOT/'vendor/compressed/geometry.py','--source',bit/'source','--out',g)
 py('global-program',ROOT/'global_word.py','--source',bit/'source','--local-check',bit,'--out',g)
 py('independent-banks',ROOT/'vendor/compressed/audit.py','--local-check',bit,'--out',g)
 py('finite-and-assembly',ROOT/'certify.py','--source',bit/'source','--out',g,'--complex-check',out/'complex')
 a=read(g/'COMBINED.json');want=read(ROOT/'EXPECTED-COMBINED.json')
 assert all(Q(a[k])==Q(want[k]) for k in ('bit_coarse','complex_coarse','kappa'));assert Q(a['kappa'])>Q(cx['kappa']);integrity()
 (out/'RESULT.json').write_text(json.dumps(dict(status='PASS_FULL_HAMMING_COMPLEX_AND_RETIMED_COMPRESSED_BIT',kappa=a['kappa'],complex_b=a['complex_coarse'],bit_c=a['bit_coarse'],source_manifest_sha256=sha(ROOT/'MANIFEST.json'),checks=checks,witness_controls=controls,scope='Conditional mutable-basis complex and compressed E8 bit suppliers. Fresh finite identities, phases, banks and invoices; inherited all-size compiler, common-chart/grid, restored-row, tape/precision and analytic interfaces remain.'),indent=2)+'\n')
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),checks=checks),indent=2)+'\n');raise
