"""Offline changed-word replay. No network and no optimizer are required."""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
TEXT={'.py','.json','.md','.txt','.sh','.lean','.cpp','.h','.hpp','.sha256','.yml','.yaml','.toml'}
def textfile(p):return p.suffix.lower()in TEXT or p.name in {'LICENSE','NOTICE','SOURCE'}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 if not __debug__:raise SystemExit('Assertions must be enabled; do not use Python -O.')
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parent;work=a.work.resolve();assert not work.exists()and root not in work.parents
 import numpy  # Required by the unchanged Clifford phase compiler.
 man=read(root/'MANIFEST.json');assert man['format']=='sha256-lf-text-v1';expect=read(root/'EXPECTED.json')
 present={x.relative_to(root).as_posix()for x in root.rglob('*')if x.is_file()and '__pycache__'not in x.parts}
 assert present==set(man['files'])|{'MANIFEST.json'},('unlisted/missing',present^(set(man['files'])|{'MANIFEST.json'}))
 for rel,z in man['files'].items():
  f=(root/rel).resolve();assert root in f.parents;b=f.read_bytes()
  if z['mode']=='lf-text':b=b.replace(b'\r\n',b'\n')
  assert hashlib.sha256(b).hexdigest()==z['sha256'],('input hash changed',rel)
 t=time.monotonic();work.mkdir(parents=True);src=work/'source';shutil.copytree(root,src,ignore=shutil.ignore_patterns('__pycache__'))
 for f in src.rglob('*'):
  if f.is_file()and textfile(f):f.write_bytes(f.read_bytes().replace(b'\r\n',b'\n'))
 stages=[];env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0')
 def run(name,script,*args):
  began=time.monotonic()
  with(work/(name+'.log')).open('w',encoding='utf-8')as log:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],stdout=log,stderr=subprocess.STDOUT,env=env)
  stages.append(dict(name=name,exit=r.returncode,seconds=time.monotonic()-began));dump(work/'STAGES.json',stages)
  if r.returncode:print((work/(name+'.log')).read_text(encoding='utf-8'),file=sys.stderr);raise SystemExit(name+' failed')
  print('PASS',name,round(stages[-1]['seconds'],2),flush=True)
 local=work/'complex-local';cg=work/'complex-global'
 run('complex-reconstruction-and-local-checks',src/'complex-local/run_local.py','--out',local,'--vendor',src/'complex-global/vendor531')
 run('complete-owner-physical-and-invoice',src/'complex-global/replay.py','--local',local/'local','--out',cg)
 run('exact-two-supplier-assembly',src/'code/assemble.py',src,cg,work/'ASSEMBLY.json')
 ans=read(work/'ASSEMBLY.json');ci=read(cg/'audit/PREFIX-AND-INVOICE.json');co=read(cg/'audit/OWNERS-AND-PROFILE.json');wave=read(local/'wave/WAVE-REVIEW.json');coset=read(local/'weighted/WEIGHTED-COSET-REPLAY.json')
 result=dict(status='PASS_FILTRATION_WAVEFRONT',kappa=ans['kappa'],kappa_decimal=ans['kappa_decimal'],bit_lower=ans['bit_lower'],complex_lower=ans['complex_lower'],complex_template_sha256=ci['template_sha256'],complex_canonical_word_sha256=ci['canonical_word_sha256'],complex_global_profile=co['paid_profile'],complex_prefix_bits=ci['global_prefix_bits'],forward_events=ci['local']['forward']['events'],backward_events=ci['local']['backward']['events'],waves=len(wave['changes']),wave_omission_controls=len(wave['controls']),coset_rewrites=len(coset['moves']),compensation_additions_saved=coset['total_saved'],outer_constraints=len(ans['outer']),bit_operator='Pinned PR543 cited dependency, not physically replayed here',stages=stages,elapsed_seconds=time.monotonic()-t,scope=ans['scope'])
 for k,x in expect.items():assert result[k]==x,('frozen result mismatch',k,result[k],x)
 assert result['outer_constraints']==47 and result['waves']==8 and result['compensation_additions_saved']==624
 dump(work/'RESULT.json',result);print(json.dumps({k:result[k]for k in ['status','kappa_decimal','elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
