"""Fresh dyadic B4 geometry using the frozen reviewed B3 matrix audit."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,gzip,sys
SOURCE,BIT,LIB,OUT=map(lambda x:Path(x).resolve(),sys.argv[1:])
assert not OUT.exists();OUT.mkdir()
digest=lambda p:sha256(p.read_bytes()).hexdigest()
assert digest(LIB)=='36dbfc8a0823cfd68252c6775f7a24d65b06d2601eef8086f260b9e19ded236d'
assert digest(SOURCE/'MANIFEST.json')=='5ff08a6c7b051d227fcd516542b56718ae65bca93615acfe09cb8785d8e3f43c'
check=SOURCE/'vendor/bit/code/bit/checkers'
spec=importlib.util.spec_from_file_location('geometry_b4_exact',check/'geometry_k.py');geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
sp=geo.sp;bridged=geo.bridged
c=json.loads(gzip.decompress((BIT/'word.json.gz').read_bytes()))
assert sha256(gzip.decompress((BIT/'word.json.gz').read_bytes())).hexdigest()=='9974db5500941456e49030a5e5f374f34c707f76a40904fe1833df4f893a1c69'
text=LIB.read_text();text=text[text.index('# Exact rational construction:'):text.index("print('PASS unsplit exact geometry',flush=True)")]
changes=[]
for old,new in [
 ('geo.Geo(h,G,L[0],7)','geo.Geo(h,G,L[0],9)'),('geo.expected(3,h)','geo.expected(4,h)'),
 ('GEO.check_port(3,','GEO.check_port(4,'),('range(7)','range(9)'),('(2,3)','(2,3,4)'),
 ('==34','==50'),('stage_boundaries=6','stage_boundaries=8'),('m=56,maxchild=34','m=72,maxchild=50')]:
 count=text.count(old);assert count>0,old;text=text.replace(old,new);changes.append(dict(old=old,new=new,count=count))
(OUT/'geometry_adapted.py').write_text(text)
dump=lambda p,x:Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
ns=dict(geo=geo,sp=sp,c=c,v=120,m=72,lay=bridged.check(4,8),OUT=OUT,dump=dump)
import hashlib,time
ns.update(hashlib=hashlib,time=time)
exec(compile(text,str(OUT/'geometry_adapted.py'),'exec'),ns)
r=json.loads((OUT/'geometry.json').read_text());assert r['m']==72 and r['maxchild']==50 and r['matrix_count']==12360
assert r['computed_denominators']==[1,2,4]
dump(OUT/'RECEIPT.json',dict(status='PASS_FRESH_ALL_PORT_DYADIC_NINE_STAGE_UNSPLIT_GEOMETRY',
 source_manifest_sha256=digest(SOURCE/'MANIFEST.json'),inherited_matrix_audit_sha256=digest(LIB),
 native_geometry_source_sha256=digest(check/'geometry_k.py'),literal_substitutions=changes,
 adapted_source_sha256=digest(OUT/'geometry_adapted.py'),geometry_sha256=digest(OUT/'geometry.json'),
 matrix_count=12360,denominators=[1,2,4],depth_inequality=[72**2,2*50**2],internal_rows=2*(72**2+1),
 scope='Exact rational self-adjoint idempotent gaps and dyadic actual matrices at every port. Rank after reduction agrees for odd q above72; geometric admission is distinct from the all-size chart/compiler and restored-row theorem.'))
print('PASS_FRESH_ALL_PORT_DYADIC_NINE_STAGE_UNSPLIT_GEOMETRY',digest(OUT/'RECEIPT.json'))
