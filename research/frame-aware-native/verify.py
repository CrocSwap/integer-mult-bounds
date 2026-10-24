"""Self-contained exact construction checks. Apache-2.0; OpenAI assistance."""
from pathlib import Path
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

def run():
    inventory=json.loads((P/'CONTENT-HASHES.json').read_text(encoding='utf-8'))['files']
    for name,digest in inventory.items():
        target=P/name
        need(target.resolve().is_relative_to(P),'External content path')
        need(hashlib.sha256(target.read_bytes()).hexdigest()==digest,'Content drift: '+name)
    anchor=json.loads((P/'owned-C-source.json').read_text(encoding='utf-8'))
    need(hashlib.sha256((P/'full_identity_rebuild.py').read_bytes()).hexdigest()==anchor['sha256'],'Center source anchor')
    results=[]
    for script in ['noncommuting-controller/verify.py','verify_lazy_response.py']:
        out=subprocess.run([sys.executable,'-I','-O','-B',str(P/script)],capture_output=True,text=True,encoding='utf-8',check=True,timeout=90)
        results.append(json.loads(out.stdout))
    need(results[0]['status']=='PASS_NONCOMMUTATIVE_STAGE_P16_IDENTITY','Free-algebra check')
    need(results[1]['status']=='PASS_EIGHT_RESPONSE_DEFERRAL_SUFFICIENT_PRECONDITIONS','Response check')
    need(all(x['new_kappa'] is False for x in results),'Scope changed')
    print(json.dumps({'status':'PASS_FRAME_AWARE_NATIVE_CONSTRUCTION_TOOLS','new_kappa':False,'checks':results},indent=2))
if __name__=='__main__':run()
