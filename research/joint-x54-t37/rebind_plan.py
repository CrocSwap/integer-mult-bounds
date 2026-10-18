"""Rebind PR1148's k8-joint-entrances provider plan to a fresh native replay of the X54 word.

Every old provider identity (file sha256, semantic sha256 and orientation program sha256) is replaced by the
identity of the same-named artifact in the supplied native replay; the paid profile is read from its LOCAL-CHECKS.
No other plan field changes. Standard library only.
"""
import argparse,gzip,hashlib,importlib.util,json
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert __debug__
 ap=argparse.ArgumentParser();ap.add_argument('--layout',type=Path,required=True);ap.add_argument('--native-local',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
 L=a.layout.resolve();new=a.native_local.resolve()
 spec=importlib.util.spec_from_file_location('gi',L/'owner37-round44/source/research/r480-owner-optimum/code/generated_identity.py');gi=importlib.util.module_from_spec(spec);spec.loader.exec_module(gi)
 plan=json.loads(gzip.decompress((L/'joint1148-round45/source/research/k8-joint-entrances/PLAN.json.gz').read_bytes()));reg=plan['provider_registry']['gauge44']
 inew=gi.artifact_identities(new);cn=json.loads((new/'LOCAL-CHECKS.json').read_text());mp={}
 assert set(inew)==set(reg['artifact_semantic_sha256'])==set(reg['artifact_sha256'])
 for n,old in reg['artifact_semantic_sha256'].items():mp[old]=inew[n]
 for n,old in reg['artifact_sha256'].items():mp[old]=sha(new/n)
 for o,old in reg['orientation_program_sha256'].items():mp[old]=cn[o]['sha256']
 txt=json.dumps(plan,sort_keys=True)
 for x,y in mp.items():assert txt.count(x)>0,x;txt=txt.replace(x,y)
 plan=json.loads(txt);assert cn['backward']['paid_profile']==cn['forward']['paid_profile']
 plan['provider_registry']['gauge44']['actual_paid_profile']={str(k):v for k,v in cn['forward']['paid_profile'].items()}
 a.out.write_bytes(gzip.compress(json.dumps(plan,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 print('PASS_X54_PROVIDER_PLAN_REBOUND',len(mp),plan['provider_registry']['gauge44']['actual_paid_profile'])
if __name__=='__main__':main()
