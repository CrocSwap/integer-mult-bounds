import datetime,hashlib,json,os,pathlib,platform,signal,subprocess,sys,time
ROOT=pathlib.Path.cwd();OUT=ROOT/'docs/research/pr-intake-evidence/pr7000-application';OUT.mkdir(parents=True,exist_ok=True)
commands={
 'native-catalogue-0':(360,['-I','-B','docs/research/pr-intake-evidence/pr7000-application/check_native_catalogue.py','--start','0','--stop','1000']),
 'native-catalogue-1':(360,['-I','-B','docs/research/pr-intake-evidence/pr7000-application/check_native_catalogue.py','--start','1000','--stop','2000']),
 'native-catalogue-2':(420,['-I','-B','docs/research/pr-intake-evidence/pr7000-application/check_native_catalogue.py','--start','2000','--stop','3057']),
 'native-catalogue':(600,['-I','-B','docs/research/pr-intake-evidence/pr7000-application/check_native_catalogue.py']),
 'application':(180,['-I','-B','docs/research/pr-intake-evidence/pr7000-application/check_application.py']),
 'application-optimized':(180,['-I','-O','-B','docs/research/pr-intake-evidence/pr7000-application/check_application.py']),
 'scalar':(60,['-I','-B','docs/research/pr-intake-evidence/pr7000-application/check_exact_scalar.py']),
 'scalar-optimized':(60,['-I','-O','-B','docs/research/pr-intake-evidence/pr7000-application/check_exact_scalar.py'])}

def inventory():
 d={}
 pins=json.loads((OUT/'SOURCES.json').read_text())
 for entry in pins['files']:
  p=ROOT/entry['path']
  raw=p.read_bytes() if p.is_file() else subprocess.check_output(['git','show',pins['base']+':'+entry['path']])
  d[entry['path']]=hashlib.sha256(raw).hexdigest()
  if d[entry['path']]!=entry['sha256']:raise ValueError('source drift: '+entry['path'])
 for p in OUT.glob('*.py'):d[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 return d

before=inventory()
for name in sys.argv[1:]:
 timeout,args=commands[name];args=[sys.executable,*args];start=time.monotonic();peak=0;stop=None;log=OUT/(name+'.log');stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with log.open('w') as f:
  p=subprocess.Popen(args,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  while p.poll() is None:
   rows=[list(map(int,line.split())) for line in subprocess.check_output(['ps','-axo','pid=,ppid=,rss='],text=True).splitlines() if line.strip()];ids={p.pid}
   while True:
    new={pid for pid,ppid,rss in rows if ppid in ids}-ids
    if not new:break
    ids|=new
   peak=max(peak,sum(rss for pid,ppid,rss in rows if pid in ids))
   if peak>1048576 or time.monotonic()-start>timeout:
    stop='sampled_descendant_memory' if peak>1048576 else 'wall_timeout'
    if p.poll() is None:
     try:os.killpg(p.pid,signal.SIGKILL)
     except ProcessLookupError:pass
    p.wait();break
   time.sleep(.2)
 after=inventory();result=dict(name=name,command=args,base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),started_at=stamp,exit_code=p.returncode,wall_seconds=time.monotonic()-start,peak_sampled_descendant_kib=peak,stop=stop,limits=dict(seconds=timeout,descendant_kib=1048576,sampling_seconds=.2,serial=True),python=sys.version,platform=platform.platform(),source_sha256=before,source_unchanged=before==after,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest());(OUT/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(name,p.returncode,round(result['wall_seconds'],2),peak,stop,'unchanged',before==after,flush=True)
 if p.returncode or before!=after:
  print(log.read_text()[-3000:],flush=True)
  raise SystemExit(p.returncode or 1)
