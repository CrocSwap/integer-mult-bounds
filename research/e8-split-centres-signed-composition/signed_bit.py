"""Fresh signed source, primitive records, rational routes and exact bit invoice.

Consumes one completed native PR433 replay. Only the source-basis branch of the
pinned signed defining-source supplement and two geometry literals are adapted.
OpenAI Codex assistance; Apache-2.0. Original source notices remain applicable.
"""
from pathlib import Path
from hashlib import sha256
import copy,difflib,gzip,importlib.util,json,os,shutil,struct,subprocess,sys,zlib
if not __debug__:raise RuntimeError('Signed validation requires assertions enabled')
sys.dont_write_bytecode=True
ORIGINAL_SIGNED='00af20d9f6fdc5e05e3856e1a1fb92e5defce6950d207193f88781edad2e1fe1'
ADAPTED_SIGNED='1d9809aefb51cbb8f0cac64d6f0b3087cffc6553f78dcda2c177a5be360627b8'
SIGNED_MANIFEST='636b41161a8cc647ab046460af76d1c78112341e43cb50e914c4c3d4f0f2906a'
GEOMETRY_SOURCE='36eeda3184bd009e89462b65c8725d10860c444f8da8f1f87e5f6e50120011ca'
WORD='015811014644ed62acba1da590d9cf6ebdfe834d89867f8ce2b68722609072ea'
sha=lambda b:sha256(b).hexdigest()
def digest(p):return sha(Path(p).read_bytes())
def read(p):return json.loads(Path(p).read_bytes())
def dump(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()+b'\n'
def semantic(x):return sha(canon(x))
def tree(path):
 path=Path(path);assert path.is_dir()and not any(p.is_symlink()for p in path.rglob('*'))
 return {p.relative_to(path).as_posix():digest(p)for p in path.rglob('*')if p.is_file()}
def check_signed(path):
 path=Path(path);assert digest(path/'MANIFEST.sha256')==SIGNED_MANIFEST
 raw=(path/'MANIFEST.sha256').read_text().splitlines();pairs=[line.split(None,1)for line in raw];expected={n:h for h,n in pairs}
 assert len(expected)==len(pairs)==9 and 'MANIFEST.sha256'not in expected and all(Path(n).name==n and n not in('.','..')for n in expected)
 assert tree(path)==dict(expected,**{'MANIFEST.sha256':SIGNED_MANIFEST})and digest(path/'signed_source.py')==ORIGINAL_SIGNED
 return tree(path)
def check_native(path,manifest_sha):
 assert digest(path/'MANIFEST.json')==manifest_sha
 m=read(path/'MANIFEST.json');m=m.get('files',m)
 assert tree(path)==dict(m,**{'MANIFEST.json':manifest_sha});return tree(path)
def stored_gzip(raw):
 # RFC1952 + stored RFC1951 blocks, independent of platform/zlib encoders.
 out=bytearray(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff')
 pieces=[raw[i:i+65535]for i in range(0,len(raw),65535)]or[b'']
 for i,b in enumerate(pieces):out.extend(bytes([int(i==len(pieces)-1)])+struct.pack('<HH',len(b),65535-len(b))+b)
 out.extend(struct.pack('<II',zlib.crc32(raw)&0xffffffff,len(raw)&0xffffffff));assert gzip.decompress(out)==raw;return bytes(out)
def run(package,native433,native386,fresh433,signed_package,output):
 package,native433,native386,fresh433,signed_package,output=map(lambda p:Path(p).resolve(),(package,native433,native386,fresh433,signed_package,output))
 assert not output.exists()and not any(output.is_relative_to(p)for p in(package,native433,native386,fresh433,signed_package))
 assert all(not any(c.isspace()for c in str(p))for p in(package,native433,native386,fresh433,signed_package,output)),'Inherited subprocess paths require no whitespace'
 source_before=check_native(native433,'3129eb4321f706542470f8443f66a6b4351a12a9ceec85e7f76aa19db1e1e32f')
 geometry_before=check_native(native386,'93aadcc9a94e6a8e84ec4b8379c6c021115aa6621d462d5982b1795e42b1e637');assert digest(native386/'geometry.py')==GEOMETRY_SOURCE
 signed_before=check_signed(signed_package)
 owned=('signed_bit.py','signed_source.py','global_bound.py');own_before={n:digest(package/n)for n in owned}
 assert own_before['signed_source.py']==ADAPTED_SIGNED
 bit=fresh433/'bit426-source-centres';word=bit/'bit-source-centres.json'
 assert digest(word)==WORD and read(bit/'bit-source-centres-receipt.json')['output_sha256']==WORD
 global_=read(bit/'global/GLOBAL.json');audit=read(bit/'global/AUDIT.json');old_geo=read(bit/'global/GEOMETRY.json')
 template_raw=gzip.decompress((bit/'global/GLOBAL-TEMPLATE.json.gz').read_bytes());template=json.loads(template_raw)
 assert global_['template_sha256']==audit['template_sha256']==sha(template_raw)
 assert global_['geometry_sha256']==template['geometry_sha256']==digest(bit/'global/GEOMETRY.json')
 assert global_['source_records_sha256']==template['source_record_sha256']==digest(bit/'records/249-records.bin')
 assert global_['word_sha256']==WORD and global_['all_scalar_columns_restored']
 assert (global_['m'],global_['R'],global_['replicas'],global_['live'])==(64,758,8,14502)
 required=[word,bit/'bit-source-centres-receipt.json',fresh433/'BIT-PRICE.json']+[bit/'global'/n for n in('GLOBAL.json','AUDIT.json','GEOMETRY.json','GLOBAL-TEMPLATE.json.gz')]+[bit/'records'/n for n in('249-records.bin','249-states.json','frames.json')]
 native_inputs={p.relative_to(fresh433).as_posix():digest(p)for p in required}
 output.mkdir(parents=True)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
 def execute(name,cmd):
  with(output/(name+'.log')).open('w')as log:r=subprocess.run([sys.executable,'-B',*map(str,cmd)],env=env,stdout=log,stderr=subprocess.STDOUT)
  if r.returncode:raise RuntimeError((name,r.returncode,(output/(name+'.log')).read_text()[-4000:]))
 execute('fresh_export',[native433/'vendor/export_records.py',word,output/'records'])
 assert {p.name:digest(p)for p in(output/'records').iterdir()}=={p.name:digest(p)for p in(bit/'records').iterdir()}
 (output/'word.json.gz').write_bytes(stored_gzip(word.read_bytes()))
 for name in('signed_source.py','global_bound.py'):shutil.copyfile(package/name,output/name)
 original=(signed_package/'signed_source.py').read_bytes();adapted=(package/'signed_source.py').read_bytes()
 adaptation=dict(original_signed_sha256=sha(original),derived_signed_sha256=sha(adapted),source_word_uncompressed_sha256=WORD,source_basis_gates_each_direction=559,
  unified_diff=''.join(difflib.unified_diff(original.decode().splitlines(True),adapted.decode().splitlines(True),fromfile='signed-validation/signed_source.py',tofile='signed_source.py')),
  scope='Explicit mutable-source branch only: the forward source basis is an integer plus-shear lift, its B prefix is the negative reversed inverse. All other full-column/adjoint/cleanup/compensation/frame checks remain. The defining decoder is J mod2I, not integer I.')
 dump(output/'ADAPTATION.json',adaptation)
 execute('signed',[output/'signed_source.py'])
 result=read(output/'RESULT.json')
 assert result['source_basis']['all_X_rows_restored_forward_and_inverse']and result['source_basis']['literal_negative_reverse_is_integer_inverse']
 assert result['source_pr433_candidate_sha256']==digest(output/'word.json.gz')
 assert result['input_sha256']=={str(output/n):digest(output/n)for n in('word.json.gz','records/249-records.bin','records/249-states.json','records/frames.json')}
 assert result['exported_F2_record_sha256']==global_['source_records_sha256']and result['forward_and_reflected_ledgers'][0]['histogram']==global_['local_checks']['forward']['profile']
 # Native-source geometry remains untouched; only two displayed literals vary.
 geometry=(native386/'geometry.py').read_bytes();derived=geometry;edits=[('bitE8-r865.json.gz','bitE8-r758.json.gz'),("(8,120,865,'<x,y>/2')","(8,120,758,'<x,y>/2')")]
 for a,b in edits:assert derived.count(a.encode())==1;derived=derived.replace(a.encode(),b.encode())
 (output/'geometry.py').write_bytes(derived)
 data=output/'geometry-input/data/bit';data.mkdir(parents=True);(data/'bitE8-r758.json.gz').write_bytes(stored_gzip(word.read_bytes()))
 execute('geometry',[output/'geometry.py','--source',output/'geometry-input','--out',output/'geometry'])
 fresh_geo=read(output/'geometry/GEOMETRY.json')
 assert fresh_geo['word_sha256']==digest(data/'bitE8-r758.json.gz')
 ignored={'seconds','word_sha256','inherited_geometry_sha256','reuse_scope'}
 geometry_math={k:v for k,v in fresh_geo.items()if k not in ignored}
 assert geometry_math=={k:v for k,v in old_geo.items()if k not in ignored}
 assert fresh_geo['route_checks']==1080 and fresh_geo['exact_bit_endpoint_operator_checks']==240 and fresh_geo['missing_route_factor_controls']==120 and fresh_geo['duplicate_bank_slot_rejected']
 dump(output/'GEOMETRY-ADAPTATION.json',dict(source_sha256=sha(geometry),derived_sha256=sha(derived),literal_edits=edits,word_uncompressed_sha256=WORD,mathematical_equality_with_native_geometry=True,excluded_transport_and_timing_fields=sorted(ignored)))
 execute('global_bound',[output/'global_bound.py',native433,fresh433,native386,output/'geometry/GEOMETRY.json'])
 bound=read(output/'GLOBAL-BOUND.json')
 roots={'source':native433,'native':fresh433,'geometry-source':native386,'signed':output}
 for name,h in bound['source_inputs'].items():prefix,rel=name.split('/',1);assert digest(roots[prefix]/rel)==h
 signed_math=copy.deepcopy(result);signed_math.pop('seconds');signed_math.pop('input_sha256');signed_math['source_pr433_candidate_sha256']=WORD
 bound_math=copy.deepcopy(bound);bound_math.pop('source_inputs')
 gmath=copy.deepcopy(global_);gmath.pop('seconds');amath=copy.deepcopy(audit);amath.pop('seconds')
 # Complete template and its native provenance remain bound; fresh geometry is
 # included in full separately. No frame, routing, ownership or rank is removed.
 science=dict(signed=signed_math,global_bound=bound_math,geometry=geometry_math,native_global=gmath,native_audit=amath,
  template=template,template_uncompressed_sha256=sha(template_raw),source_word_uncompressed_sha256=WORD,
  projection='Only elapsed seconds and named input provenance are omitted. The compressed word hash is replaced by the pinned decoded payload hash. All mathematical, compiler-interface, finite and scope fields are retained.')
 dump(output/'SCIENCE.json',science)
 assert source_before==tree(native433)and geometry_before==tree(native386)and signed_before==tree(signed_package)
 assert own_before=={n:digest(package/n)for n in owned}and native_inputs=={p.relative_to(fresh433).as_posix():digest(p)for p in required}
 receipt=dict(status='PASS_FRESH_PR433_SIGNED_DECODER_GEOMETRY_COMPLETE_PREFIX_AND_COMPENSATED_INVOICE',source_word_uncompressed_sha256=WORD,
  native_manifest_sha256=digest(native433/'MANIFEST.json'),geometry_source_sha256=GEOMETRY_SOURCE,signed_validation_manifest_sha256=SIGNED_MANIFEST,
  package_modules=own_before,native_inputs=native_inputs,outputs={n:digest(output/n)for n in('ADAPTATION.json','RESULT.json','GLOBAL-BOUND.json','GEOMETRY-ADAPTATION.json','geometry/GEOMETRY.json','SCIENCE.json','signed-records.bin','decoder-and-dirt.json')},
  source_unchanged=True,original_unsigned_integer_identity_claimed=False,finite=bound['finite'],scope=bound['scope'])
 dump(output/'RECEIPT.json',receipt)
 return output/'GLOBAL-BOUND.json',receipt
if __name__=='__main__':
 assert len(sys.argv)==7
 _,r=run(*sys.argv[1:]);print(r['status'])
