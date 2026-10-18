import concurrent.futures,json,pathlib,subprocess,hashlib,time
P=pathlib.Path('/tmp/pr-efficient1400');R=P/'sources/2409';PY='/tmp/pr-efficient200-venv/bin/python'
def one(pkg):
 out=P/(pkg+'-fresh.json');log=P/(pkg+'-fresh.log');cmd=[PY,'-I','-B','research/'+pkg+'/verify.py','--write-result',str(out)]
 with log.open('w') as f:r=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,timeout=240)
 result={'package':pkg,'command':cmd,'exit_code':r.returncode,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
 if r.returncode==0:
  fresh=json.load(open(out));old=json.load(open(R/'research'/pkg/'RESULT.json'))
  result['changed_top_fields']=[k for k in set(old)|set(fresh)if old.get(k)!=fresh.get(k)]
  a=old['input_sha256'];b=fresh['input_sha256'];result['input_deltas']={k:[a.get(k),b.get(k)]for k in set(a)|set(b)if a.get(k)!=b.get(k)}
  result['fresh_sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
 print(result,flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(one,['k8-hpe450-binding','k8-hpe450-forward-audit']))
(P/'combined-2409-receipt-audit.json').write_text(json.dumps({'head':json.load(open(P/'2409.json'))['headRefOid'],'checks':rows},indent=2)+'\n')
