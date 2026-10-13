"""Resume terminal PR543 replay after correcting SSD-relative symlink adaptation.
No mathematical check is changed; successful native/emission stages are retained.
"""
from pathlib import Path
import os,json,subprocess,sys,time
R=Path(__file__).resolve().parent;W=R/'pr543-independent314-retry';H=R/'pr543-run-layout/research/e8-bit-r420';P=H.parent/'e8-bit-carrier-skeleton';C=H/'code';V=H/'vendor/pr510/e8-r480-nine-stage';K=V/'vendor/e8-r715-eleven-stage-whole/code';PC=P/'code';repairs=[]
for link,target in [(W/'root/code',PC),(W/'v9/records',W/'records'),(W/'c480/v9/records',W/'c480/records')]:
 assert link.is_symlink()and not link.exists();repairs.append(dict(link=str(link.relative_to(R)),old=os.readlink(link),new=str(target)));link.unlink();link.symlink_to(target)
(W/'PATH-REPAIRS.json').write_text(json.dumps(repairs,indent=2)+'\n')
f=R/'verify_r420_ssd_paths.sh';old=f.read_text();(W/'INITIAL-SSD-ADAPTER.sh').write_text(old);f.write_text(old.replace('ln -sfn $PC $WD/root/code','ln -sfn "$(cd "$PC" && pwd)" "$WD/root/code"').replace('ln -sfn $lc/records $o/v9/records','ln -sfn "$(cd "$lc/records" && pwd)" "$o/v9/records"'))
steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(R))
def run(name,script,*args):
 start=time.monotonic()
 with (W/(name+'.resume.log')).open('w')as out:r=subprocess.run([sys.executable,'-E','-s','-B',str(script),*map(str,args)],cwd=R,env=env,stdout=out,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,exit=r.returncode,seconds=time.monotonic()-start));(W/'RESUME-STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
 if r.returncode:print((W/(name+'.resume.log')).read_text());raise SystemExit(name+' failed')
 print('PASS',name,flush=True)
for name,dest,sup in [('r420',W,'pr535,pr531'),('control480',W/'c480','pr535,pr531,pr484,pr471,pr458')]:
 run(name+'-hosted-audit',K/'audit_hosted_k.py',dest/'v9',dest/'v9/hosted',dest/'v9/hosted/AUDIT.json')
 run(name+'-assemble9',V/'code/assemble9.py',dest/'v9',dest/'v9/hosted',dest/'v9/hosted/AUDIT.json',W/'root',dest/'RESULT9.json',sup)
word=H/'data/bitE8mut-r420.json.gz';run('eleven-hosting-rediscovery',P/'discovery/host_select.py',word,W/'hosting11.json')
run('eleven-audit-adaptation',C/'adapt11.py',P,word,420,W/'adapted11')
run('eleven-emission',PC/'eleven/emit.py','--word',word,'--local-check',W,'--out',W/'bit','--isometries',P/'data/eleven/residual-isometries.json','--hosting',H/'data/hosting11-r420.json')
run('eleven-audit',W/'adapted11/audit.py',W,W/'nine',W/'bit')
run('eleven-assembly',PC/'eleven/assemble.py',W/'bit',420,W/'root',W/'RESULT11.json','pr535,pr531')
run('control489-assembly',PC/'eleven/assemble.py',W/'c489/bit',489,W/'root',W/'c489/RESULT11.json','pr535,pr531,pr484,pr471,pr458')
run('complete-summary',C/'summary.py',H,W)
(W/'COMPLETED.json').write_text(json.dumps(dict(status='PASS_PR543_ALL_CHECKS_WITH_SSD_PATH_REPAIR',steps=steps,original_log='pr543-independent314-retry.log',scope='Fresh author pipeline mathematical checks completed; independent workspace path adaptation repaired symlinks. No supplier source/check modified. Source and all-size interface assumptions remain conditional.'),indent=2)+'\n')
