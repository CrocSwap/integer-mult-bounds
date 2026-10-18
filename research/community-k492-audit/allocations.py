import pathlib,subprocess,sys,time,json
p=pathlib.Path('/tmp/im-k492-replay/pr622/RECEIPT.json')
while not p.exists():time.sleep(5)
for n in sys.argv[1:]:
 with open('/tmp/im-k492-pr'+n+'.log','w')as f:
  subprocess.run([sys.executable,'/tmp/im-k492-run-reused.py',n],stdout=f,stderr=subprocess.STDOUT,check=True)
 print('PASS',n,flush=True)
