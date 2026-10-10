"""Reconstruct the unchanged156 relations with explicit PR306 provenance."""
import hashlib,json
from context306 import OUTPUT,HEAD
import witness
SHA='fc38ee603065d80c84ac5fa3d699126b2b124fbc1b5cbb180666d3d8137b73c4'
def build():
 prior=witness.write_case('156');raw=prior.read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='aaf9eb2f324c05dc534ecb047f70724042d6c0515e6ae9c8440bbcc2ca6f3ba1'
 d=json.loads(raw);d['source_head']=HEAD;d['selection']='pr306_transport156'
 d['scope']='Same156 relations transported through the pinned306 suffix reorders; inherited306 raw crossing/full-word admission is explicit.'
 d['ported_from_head']='a17c42903bbe8d9d26c4bc712d7216a7176237e9';d['predecessor156_sha256']=hashlib.sha256(raw).hexdigest()
 raw=(json.dumps(d,indent=2)+'\n').encode();assert hashlib.sha256(raw).hexdigest()==SHA
 OUTPUT.mkdir(parents=True,exist_ok=True);p=OUTPUT/'candidate156.json';p.write_bytes(raw);return p
