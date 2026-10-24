import subprocess,time,os,signal,pathlib,sys,json,hashlib
D=pathlib.Path(__file__).resolve().parent
outdir=D/'review-evidence';outdir.mkdir(exist_ok=True)
name=sys.argv[1];timeout=int(sys.argv[2]);cmd=[sys.executable,'-B',*sys.argv[3:]]
out=outdir/(name+'.log');env=os.environ.copy();env.pop('LEAN_AUDIT_BIN',None);env.pop('PYTHONOPTIMIZE',None)
with out.open('w') as f:
 p=subprocess.Popen(cmd,cwd=D,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=env);start=time.monotonic();peak=0;stop=None
 while p.poll() is None:
  rows=subprocess.check_output(['ps','-axo','pid,ppid,rss']).decode().splitlines()[1:]
  procs={int(a):(int(b),int(c)) for a,b,c in (l.split() for l in rows)};ids={p.pid}
  while True:
   new={pid for pid,(ppid,rss) in procs.items() if ppid in ids};old=len(ids);ids|=new
   if old==len(ids):break
  mem=sum(procs.get(pid,(0,0))[1] for pid in ids);peak=max(peak,mem)
  if mem>1048576 or time.monotonic()-start>timeout:
   stop='memory' if mem>1048576 else 'timeout';os.killpg(p.pid,signal.SIGKILL);p.wait();break
  time.sleep(.5)
r=dict(command=cmd,exit=p.returncode,resource_stop=stop,timeout_seconds=timeout,seconds=round(time.monotonic()-start,2),peak_sampled_rss_kib=peak,log=out.name,log_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
(outdir/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
sys.exit(p.returncode or bool(stop))
