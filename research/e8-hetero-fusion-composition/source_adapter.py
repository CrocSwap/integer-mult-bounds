"""Build a minimal pinned-source runtime; no recovered unpublished tree required.

Six PR390 leaves and three PR394 leaves use readable LF transport. The exact
per-line CRLF pattern and terminal state are restored (removing one transport
LF only for a source with no terminal LF) and original hashes
checked before execution. Regenerated PR390 preconditioning is compared with
canonical projections of its original four arrays, not called byte-identical
JSON. Original source provenance is recorded separately from generated inputs.
"""
from pathlib import Path
import gzip,hashlib,importlib.util,json,os,shutil
from transport import deterministic_gzip
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def leaves(meta,out):
 pins=read(HERE/meta);files={}
 for name,p in pins['files'].items():
  carrier=(HERE/name).read_bytes();assert b'\r'not in carrier and sha(HERE/name)==p['carrier_sha256']
  if not p['terminal_lf']:
   assert carrier.endswith(b'\n')and not carrier.endswith(b'\n\n')
   carrier=carrier[:-1] # only the single publication-transport LF; original SHA remains mandatory
  rows=carrier.splitlines(keepends=True);assert p['crlf_lines']==sorted(set(p['crlf_lines']))
  assert all(1<=i<=len(rows)and rows[i-1].endswith(b'\n')for i in p['crlf_lines'])
  native=b''.join(x[:-1]+b'\r\n'if i in p['crlf_lines']else x for i,x in enumerate(rows,1))
  assert hashlib.sha256(native).hexdigest()==p['source_sha256'] and len(native)==p['source_bytes']
  assert native.count(b'\n')==p['lf_count'] and native.endswith(b'\n')==p['terminal_lf']
  dest=out/p['source_path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(native)
  files[p['source_path']]=dict(original_sha256=p['source_sha256'],carrier_sha256=p['carrier_sha256'],crlf_lines=p['crlf_lines'])
 return dict(commit=pins['commit'],files=files)
def inventory(out):return {p.relative_to(out).as_posix():sha(p)for p in out.rglob('*')if p.is_file()and p.name!='INPUTS.json'}
def prepare(parent,bit_parent,ordinary,ordinary_complex,far,far_composition,out):
 parent,bit_parent,ordinary,ordinary_complex,far,far_composition,out=map(Path,[parent,bit_parent,ordinary,ordinary_complex,far,far_composition,out])
 assert not out.exists();out.mkdir(parents=True)
 # The top-level wrapper separately checks complete pinned ancestor inventories.
 assert sha(parent/'MANIFEST.json')=='3743f954b5a652e51fa9ae5101318345d79f4c897ff9a29d5c54387b92118458'
 assert sha(bit_parent/'MANIFEST.sha256')=='c945d6c1fa1a469ef73e48519921589926f7c7a9cf19eb51842255d2c0ef2d8e'
 pr=out/'pr390';pr.mkdir();provenance=leaves('PR390-SOURCE.json',pr)
 dest=pr/'public/381/source/research/e8-nine-stage-kappa'
 shutil.copytree(parent,dest/'complex377')
 inc=dest/'code/bit/checkers';inc.mkdir(parents=True)
 header=bit_parent/'code/bit/checkers/json.hpp';shutil.copyfile(header,inc/'json.hpp')
 candidate=load('source_adapter_ordinary',ordinary/'candidate.py')
 candidate.native_sources(out/'prefix-native')
 os.environ['OUTPUT_SHEAR_BASE']=str(far.resolve())
 prefix=load('source_adapter_prefix',out/'prefix-native/prefix_source.py')
 c=prefix.transform(json.loads(gzip.decompress((far/'data/gcert1-e8-r783-far.json.gz').read_bytes())),read(out/'prefix-native/prefix_selection.json'))
 raw=candidate.raw(c);assert hashlib.sha256(raw).hexdigest()=='ba159f566568627d8459960500b9c285e9c9d69368f1b60fa27ae83f0a84c39a'
 (pr/'data/prefix18.json.gz').write_bytes(deterministic_gzip(raw))
 gen=load('source_adapter_hetero',HERE/'hetero_replay.py')
 pre,audit=gen.generate(c,read(pr/'data/sink-audit.json'))
 pins=read(HERE/'PR390-SOURCE.json');arrays={}
 for key,pin in pins['prewhite']['lists'].items():
  encoded=(json.dumps(pre[key],sort_keys=True,separators=(',',':'))+'\n').encode()
  assert len(pre[key])==pin['count']and hashlib.sha256(encoded).hexdigest()==pin['sha256']
  arrays[key]=pin
 assert [x['cut_group']for x in audit['accepted']]==[x['cut_group']for x in read(pr/'data/sink-audit.json')['accepted']]
 write(pr/'data/prewhite.json',pre)
 assert sha(ordinary_complex/'candidate.json')=='468460de3bb2ebf6c89b3156fdd332623596f7f6ae74324362862324cf71a98c'
 receipt=dict(status='PASS_EXACT_SOURCE_LEAVES_AND_CANONICAL_REGENERATED_PREWHITE',original_source=provenance,
  original_prewhite_source_sha256=pins['prewhite']['source_sha256'],canonical_prewhite_lists=arrays,
  prefix_raw_sha256=hashlib.sha256(raw).hexdigest(),parent377_manifest_sha256=sha(parent/'MANIFEST.json'),
  bit_parent_manifest_sha256=sha(bit_parent/'MANIFEST.sha256'),json_header_sha256=sha(header),files=inventory(pr),
  scope='Exact original code leaves and sink witness. Prefix and preconditioning JSON are regenerated; canonical array hashes bind the four original arrays. This is a minimal dependency reconstruction, not an unchanged PR390 full package or a reproduction of its heterogeneous headline.')
 write(pr/'INPUTS.json',receipt)
 pr394=out/'pr394';pr394.mkdir();prov394=leaves('PR394-SOURCE.json',pr394)
 write(pr394/'INPUTS.json',dict(status='PASS_EXACT_PR394_LEAVES',original_source=prov394,files=inventory(pr394)))
 write(out/'SOURCES.json',dict(pr390_input_sha256=sha(pr/'INPUTS.json'),pr394_input_sha256=sha(pr394/'INPUTS.json')))
 return pr,pr394
