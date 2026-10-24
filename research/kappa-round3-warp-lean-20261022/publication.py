"""Byte inventory for the focused round-three positive contribution.
No caches, credentials or compiled objects are publication inputs.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
DIRS=['kappa-round3-warp-20261022','kappa-round3-warp-lean-20261022','kappa-round3-audit-20261022']
EXCLUDE={'UniformGain.lean','UniformGain.log','UniformGain.olean'}
def items():
    result=[]
    for name in DIRS:
        for p in sorted((ROOT/'research'/name).iterdir()):
            if not p.is_file() or p.name in EXCLUDE or p.name=='PUBLICATION.json':continue
            if p.suffix not in ('.py','.md','.json','.gz','.lean','.log') and p.name not in ('.gitignore','.gitattributes'):continue
            result.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()})
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    receipt=json.loads((HERE/'LEAN-VERIFICATION.json').read_text(encoding='utf-8'))
    assert receipt['status']=='PASS_SCOPED_LEAN_REPLAY','Complete Lean replay required'
    files=items();data={'status':'FOCUSED_ROUND3_PUBLICATION_INVENTORY','files':files,'count':len(files),'bytes':sum(r['bytes'] for r in files),'predecessor_pr4610_head':'4b4c75bc0fd64d3eee54029e8d2fab834251fca6','canonical_main':'f626db5c3a3d781d8f7695038776c621651f75e1','scope':'New joint helper/map construction, fresh scoped Lean proof sources/logs and independent AI audit; no selected-frontier change.'}
    target=HERE/'PUBLICATION.json'
    if args.write:target.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:assert json.loads(target.read_text(encoding='utf-8'))==data,'Published bytes differ from inventory'
    print('PASS_ROUND3_PUBLICATION',data['count'],data['bytes'])
if __name__=='__main__':main()
