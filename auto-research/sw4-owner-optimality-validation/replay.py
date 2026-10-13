from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time
ap=argparse.ArgumentParser();ap.add_argument('core',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();core=a.core.resolve();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();start=time.monotonic();stages=[]
for mode,flags in [('normal',[]),('optimized',['-O'])]:
 for name,args in [('verify',['--out',str(out/mode)]),('independent_check',['--out',str(out/mode/'INDEPENDENT.json')]),('controls',['--out',str(out/mode/'CONTROLS.json')])]:
  cmd=[sys.executable,'-I','-B',*flags,str(core/(name+'.py')),*args];begin=time.monotonic();log=out/(mode+'-'+name+'.log')
  with log.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
  stages.append(dict(name=mode+'-'+name,argv=cmd,exit_code=r.returncode,seconds=time.monotonic()-begin,log_sha256=sha(log)));(out/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n');assert r.returncode==0,log.read_text()
for name in ('RESULT.json','INDEPENDENT.json','CONTROLS.json'):assert(out/'normal'/name).read_bytes()==(out/'optimized'/name).read_bytes(),name
result=dict(status='PASS_NORMAL_OPTIMIZED_ALL_PROOFS',seconds=time.monotonic()-start,python=sys.version,platform=platform.platform(),core_manifest_sha256=sha(core/'MANIFEST.json'),files={p.relative_to(out).as_posix():sha(p)for p in out.rglob('*')if p.is_file()});(out/'RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result['seconds'])
