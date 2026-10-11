"""Stage the immutable parent and incremental sources; never publish."""
from pathlib import Path
import argparse,json,shutil,hashlib,gzip,os
P=Path(__file__).resolve().parent;R=P.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('--out',type=Path);a.add_argument('--parent-binding',type=Path);a=a.parse_args();m=json.loads((P/'INVENTORY.json').read_text());par=R/m['parent_transport']
if not a.out:
 print('DESIGN_READY_PARENT_HEAD_PENDING',m['parent_count'],len(m['incremental_sources']));raise SystemExit
if not a.parent_binding:raise SystemExit('Root connector-readback parent binding required before staging')
b=json.loads(a.parent_binding.read_text());assert b['repository']=='applecrusher/integer-mult-bounds'and b['connector_readback_verified']is True
assert len(b['commit'])==len(b['tree'])==40 and b['transport_manifest_sha256']==m['parent_transport_manifest_sha256']
assert not a.out.exists(),'Use a fresh isolated output directory';a.out.mkdir(parents=True);parent=a.out/'parent-pool60';parent.mkdir()
for name,z in m['preserved_parent_files'].items():
 src=par/name;assert sha(src)==z['sha256'];dst=parent/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(dst)==z['sha256'];assert('100755'if dst.stat().st_mode&0o111 else'100644')==z['mode']
for dest,z in m['incremental_sources'].items():
 src=R/z['source'];assert sha(src)==z['sha256'];dst=a.out/dest;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
compressed={}
for dest,z in m['lossless_transport_materializations'].items():
 src=R/z['source'];assert sha(src)==z['raw_sha256'];dst=a.out/z['transport_path'];dst.parent.mkdir(parents=True,exist_ok=True)
 with src.open('rb')as reader,dst.open('wb')as writer:
  with gzip.GzipFile(fileobj=writer,mode='wb',mtime=0,filename='')as comp:shutil.copyfileobj(reader,comp)
 compressed[dest]={**z,'compressed_sha256':sha(dst),'compressed_bytes':dst.stat().st_size}
for name in ['INVENTORY.json','VERIFY-DESIGN.md','PATH-ADAPTER-DESIGN.json','build_packet.py','verify.py','apply_adapters.py','materialize_incremental.py','LICENSE','NOTICE.md','README.md']:
 shutil.copy2(P/name,a.out/name)
(a.out/'PARENT-BINDING.json').write_text(json.dumps(b,indent=2)+'\n');(a.out/'INCREMENTAL-TRANSPORT.json').write_text(json.dumps(compressed,indent=2)+'\n')
# This is staging, not a science/default/publication claim. Root owns adapters,
# manifest freeze, independent relocation gate and bot publication after readback.
r={'status':'STAGED_PENDING_PORTABLE_DEFAULT_AND_INDEPENDENT_RELOCATION_GATE','parent_preserved_files':1134,'parent_commit':b['commit'],'parent_tree':b['tree'],'frozen69_raw_sources_bound':69,'parent_materialize_and_verify_not_run':True,'source_inventory_sha256':sha(P/'INVENTORY.json'),'compressed_incremental_sources':compressed}
(a.out/'PREPARED.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
