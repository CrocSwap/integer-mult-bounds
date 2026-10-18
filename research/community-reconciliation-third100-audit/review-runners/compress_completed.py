from pathlib import Path
import subprocess,hashlib,os,json,time
P=Path('/tmp/reconciliation-third100-20261013');O=P/'disk-retry-309-out';log=P/'filesystem-compression.json';receipts=[]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def compress(root):
 for p in sorted(root.rglob('*')):
  if not p.is_file()or p.stat().st_size<2_000_000 or p.suffix in ('.gz','.zip'):continue
  st=p.stat()
  if st.st_blocks*512<st.st_size//2:continue
  sha=digest(p);q=p.with_name(p.name+'.review-compression-tmp');assert not q.exists()
  subprocess.run(['/usr/bin/ditto','--hfsCompression',str(p),str(q)],check=True)
  assert digest(q)==sha
  now=p.stat();assert(st.st_ino,st.st_mtime_ns,st.st_size)==(now.st_ino,now.st_mtime_ns,now.st_size),'File changed while compressing'
  if q.stat().st_blocks>=st.st_blocks:q.unlink();continue
  os.replace(q,p);assert digest(p)==sha
  row=dict(path=str(p.relative_to(O)),sha256=sha,bytes=st.st_size,allocated_before=st.st_blocks*512,allocated_after=p.stat().st_blocks*512);receipts.append(row);log.write_text(json.dumps(receipts,indent=2)+'\n')
 print('COMPRESSED',root, sum(r['allocated_before']-r['allocated_after']for r in receipts),flush=True)
# Each marker is printed only after the earlier stage has returned successfully.
steps=[
 ('base-replay/logs/complex-source-native.log','PASS stronger complex admission',['base-replay/public-replay']),
 ('logs/full-inherited-base-source.log','rank-modular159-fresh-source-and-controls',['base-replay/posttarget','base-replay/trade']),
 ('logs/full-inherited-base-source.log','actual51-source-span-frame-refinement',['base-replay/kernel-replay']),
 ('logs/full-inherited-base-source.log','dual-engine-fixed-prime-and47',['base-replay/rank-modular-replay','base-replay/retiming51','base-replay/inventory','base-replay/actual-guard']),
 ('logs/frozen-reorder-2.log','',[]),
]
# The outer driver exposes subsequent stage starts in its own stdout.
start=time.monotonic();done=set()
while time.monotonic()-start<3600:
 for i,(rel,marker,dirs)in enumerate(steps):
  f=O/rel
  if i not in done and f.exists()and marker in f.read_text(errors='replace'):
   for d in dirs:compress(O/d)
   done.add(i)
 outer=P/'pr309-disk-retry.txt';text=outer.read_text(errors='replace')if outer.exists()else''
 for key,marker,dirs in [(10,'response37-fresh-source-and-controls',['reorder1']), (11,'ten-local-response-transports-and-controls',['reorder2']), (12,'actual-complex304-fresh-source-and-controls',['response37-replay','transport10-replay']), (13,'all-final-global-columns',['inventory','actual-guard'])]:
  if key not in done and marker in text:
   for d in dirs:compress(O/d)
   done.add(key)
 if (P/'disk-retry-execution.json').exists():break
 time.sleep(10)
print('DONE',len(receipts),flush=True)
