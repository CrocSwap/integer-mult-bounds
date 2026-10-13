"""Verify and retain a complete fresh platform receipt and all pinned artifacts/logs."""
from pathlib import Path
import argparse,json,hashlib,shutil
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--platform',required=True);a=ap.parse_args()
V=Path(__file__).resolve().parent;P=V.parent/'complex-k492-owner-repair';W=a.work.resolve();T=V/a.platform
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
r=load(W/'RECEIPT.json');s=load(W/'STAGES.json');z=load(W/'RESULT.json');spec=load(P/'data/SPEC.json');i=load(W/'INDEPENDENT-MAP-CHECK.json')
need(len(s)==64 and len(r['artifacts'])==51,'complete stage/artifact count')
need(all(x['exit_code']==0 for x in s)and sorted(s,key=lambda x:x['name'])==sorted(r['steps'],key=lambda x:x['name']),'complete successful logs')
need(r['manifest_sha256']==sha(P/'MANIFEST.json')and r['spec_sha256']==sha(P/'data/SPEC.json'),'frozen package pins')
need(r['source_manifest_sha256']=={name:sha(P/'vendor'/name/'MANIFEST.json')for name in spec['build']['sources']},'all source pins')
need(z['reused']=={'baseline':False,'locals':[]},'fresh replay')
need(z['kappa']==i['kappa']==spec['expected']['kappa'],'exact endpoint')
need(i['status']=='PASS_INDEPENDENT_K492_REPAIR_MAP_NATIVE_PROFILE_AND_EXACT_MOMENT','separate literal check')
need(i['profile']==spec['expected']['global_profile'],'independent native/idle profile')
for rel,h in r['artifacts'].items():need(sha(W/rel)==h,'artifact '+rel)
for x in s:need(sha(W/(x['name']+'.log'))==x['log_sha256'],'log '+x['name'])
for rel in sorted(set(['RECEIPT.json','STAGES.json','INDEPENDENT-MAP-CHECK.json',*r['artifacts'],*[x['name']+'.log'for x in s]])):
 t=T/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,t)
record=dict(status='PASS_FULL_FRESH_PLATFORM',platform=a.platform,stages=len(s),receipt_artifacts=len(r['artifacts']),seconds=z['seconds'],kappa=z['kappa'],manifest_sha256=r['manifest_sha256'],spec_sha256=r['spec_sha256'],receipt_sha256=sha(W/'RECEIPT.json'),reused=z['reused'])
(T/'VERIFIED.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
