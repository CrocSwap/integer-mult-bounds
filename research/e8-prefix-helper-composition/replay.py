"""Source-bound PR377 replay for PR390 target-prefix rewrites plus two aliases and two frame reductions.
All primary source bytes are checked before copying. Every derived file and
literal source edit is recorded; upstream packages are never modified.
Packaging transport uses deterministic stored DEFLATE gzip blocks;
the frozen research replay used gzip.compress(mtime=0).
Prepared with OpenAI Codex assistance; inherited notices apply.
"""
from pathlib import Path
import argparse,copy,difflib,gzip,hashlib,json,os,shutil,subprocess,sys,time
assert __debug__
sys.set_int_max_str_digits(0)

import candidate,importlib.util
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
ap=argparse.ArgumentParser();ap.add_argument('source377',type=Path);ap.add_argument('source378',type=Path);ap.add_argument('far_package',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();src=a.source377.resolve();src378=a.source378.resolve();out=a.out.resolve();assert not out.exists() and src not in out.parents
assert sha(src/'MANIFEST.json')=='3743f954b5a652e51fa9ae5101318345d79f4c897ff9a29d5c54387b92118458'
assert sha(src378/'MANIFEST.sha256')=='f88d7300aeb8aa4bfef95c3571d0cc57d9726abfd75caee364e83ff211316a4a'
for line in (src378/'MANIFEST.sha256').read_text().splitlines():
 digest,name=line.split(None,1);assert sha(src378/name)==digest,name
assert sha(a.far_package/'two_alias.py')=='5046a050e168266aff6488d27ca6525469c844118fbaced9af2b3dde8e13065c'
assert sha(a.far_package/'transport.py')=='264f6fc385532a25ae7f99774c2cb33e6ff6943fdbca546cfa000fb9e551fafb'
manifest=read(src/'MANIFEST.json');actual={p.relative_to(src).as_posix():sha(p)for p in src.rglob('*')if p.is_file()and p!=src/'MANIFEST.json'};assert actual==manifest['files'];assert not any(p.is_symlink()for p in src.rglob('*'))
out.mkdir();raw,_=candidate.build(src378,a.far_package.resolve(),out/'prefix-native');assert hashlib.sha256(raw).hexdigest()=='468460de3bb2ebf6c89b3156fdd332623596f7f6ae74324362862324cf71a98c'
c=json.loads(raw);assert (c['h'],c['v'],c['R'],c['cst'])==(9,120,781,72)
source_transport=candidate.native_sources(out/'prefix-roundtrip-control');assert all((out/'prefix-native'/name).read_bytes()==(out/'prefix-roundtrip-control'/name).read_bytes()for name in source_transport['files'])
dump(out/'PREFIX-SOURCE.json',source_transport)
can=out/'candidate.json';can.write_bytes(raw);shutil.copytree(src/'work',out/'work');(out/'logs').mkdir();steps=[];changes=[]
def run(name,cmd,env=None):
 print('RUN',name,flush=True);t=time.monotonic()
 with (out/'logs'/f'{name}.log').open('w')as f:subprocess.run(list(map(str,cmd)),cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 steps.append(dict(stage=name,log_sha256=sha(out/'logs'/f'{name}.log')));print('PASS',name,round(time.monotonic()-t,2),flush=True)
py=[sys.executable,'-B']
run('frozen-source-integrity',py+['-c',"import runpy; x=runpy.run_path('work/native358/vendor/complex-reserve/verify.py'); print(x['integrity']())"])
# The copied work tree is now explicitly a derived input tree, not an unchanged upstream.
def changed(path,new,why):
 p=out/path;old=p.read_bytes();data=new.encode()if isinstance(new,str)else new;p.write_bytes(data)
 changes.append(dict(path=path,before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=sha(p),reason=why,unified_diff=''.join(difflib.unified_diff(old.decode().splitlines(True),data.decode().splitlines(True),fromfile='upstream/'+path,tofile='derived/'+path))if not path.endswith('.gz')else None))
def edits(path,pairs):
 s=(out/path).read_text()
 for old,new,count in pairs:assert s.count(old)==count,(path,old,s.count(old),count);s=s.replace(old,new)
 changed(path,s,'Source-derived R781 metadata and counts; all structural assertions retained')
CX='work/native358/vendor/complex-reserve/upstream/pr352/code/complex';ODD='work/odd-stages';raw=can.read_bytes();transport=candidate.load('frozen_transport',a.far_package.resolve()/'transport.py');zipdata=transport.deterministic_gzip(raw);assert gzip.decompress(zipdata)==raw
cp=read(out/CX/'inputs/complex/source-pins.json');certpath=CX+'/'+cp['certificate']['path'];original_cert=copy.deepcopy(cp['certificate'])
changed(certpath,zipdata,'PR390 target-prefix rewrites, two helper aliases and two nested frame reductions')
changed('work/pr361/complex/gcert1-e8-r783.json.gz',zipdata,'Same derived certificate used by every geometry, Clifford and template checker')
cp['certificate'].update(compressed_sha256=hashlib.sha256(zipdata).hexdigest(),uncompressed_sha256=sha(can),upstream='derived/R781-PR378',source_pin='sha256:'+sha(can));cp['certificate'].pop('url',None);cp['certificate']['derived_from']=original_cert
changed(CX+'/inputs/complex/source-pins.json',json.dumps(cp,indent=2,sort_keys=True)+'\n','Bind actual derived certificate and preserve original attribution')
seed=dict(H=c['h'],V=c['v'],R=c['R'],cst=c['cst'],N=c['N'],frames=len(c['frames']))
dump(out/'pins-seed.json',seed)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',CX_PINS=str(out/'pins-seed.json'),CX_RECORD=str(out/'pins-recorded.json'))
for x in ['CX_SOURCE_PINS','PYTHONOPTIMIZE']:env.pop(x,None)
# Source-bound explicit frozen K and original cleanup; extend only the main target reads.
oldraw=candidate.old_response(src378,a.far_package.resolve());assert hashlib.sha256(oldraw).hexdigest()=='d14ea8bf581d9f5ea8f3261e614199386d71ea4cbc8bc48d6bec371954669daf'
oldpath=CX+'/code/prefix_old.json';(out/oldpath).write_bytes(oldraw)
changes.append(dict(path=oldpath,before_sha256=None,after_sha256=sha(out/oldpath),reason='Explicit original no-target-read R781 dirty response and cleanup source',unified_diff=None))
ext=Path(__file__).with_name('prefix_extension.py').read_text()
changed(CX+'/code/complex_scalars.py',(out/CX/'code/complex_scalars.py').read_text()+'\n'+ext,'Frozen original K and cleanup with exact full-column identity check; allow main Y-to-Y only')
p=CX+'/code/complex_splice.py';s=(out/p).read_text()
a="need(t!=s and role(s)!='Y' and (role(s),role(t))!=('S','X'),'scalar projection shape')"
b="need(t!=s and (role(s),role(t))!=('S','X') and (role(s)!='Y' or role(t)=='Y'),'main target-only read extension')"
assert s.count(a)==1;s=s.replace(a,b)
a="A=list(flat(c['A']));B=list(flat(c['B']));cur=c['start'].copy()"
b="from complex_scalars import PREFIX_OLD_CERT, prefix_validate\n    prefix_validate(c)\n    A=list(flat(PREFIX_OLD_CERT['A']));B=list(flat(PREFIX_OLD_CERT['B']));cur=c['start'].copy()"
assert s.count(a)==1;s=s.replace(a,b)
changed(p,s,'Emit frozen original K and cleanup, but every main frame/scalar event comes from the new prefix certificate')

run('derive-local-metadata',py+[CX+'/portable_complex.py'],env)
pins=seed|read(out/'pins-recorded.json')
changed(CX+'/pins-e8.json',json.dumps(pins,indent=2,sort_keys=True)+'\n','Fresh checked local pin metadata, then reused frozen for admission')
edits('work/native358/vendor/complex-reserve/finite_guard.py', [('assert (h,v,R)==(9,120,783)','assert (h,v,R)==(9,120,781)',1)])
edits(ODD+'/complex_candidate.py',[('(9,120,783,72)','(9,120,781,72)',1),('banks=783','banks=R',1)])
edits(ODD+'/global_nine.py',[
 ('h,v,R=9,120,783;k,L,T,m=4,9,8,73;live=14727;physical=live+R+h+1',"h,v,R=c['h'],c['v'],c['R'];assert (h,v,R)==(9,120,781);k,L,T,m=4,9,8,73;live=2*k*v*T+L*R;physical=live+R+h+1;assert (live,physical)==(14709,15500)",1),
 ("local_children=raw['label_checks']['invocation_calls'];assert local_children==3974","local_children=raw['label_checks']['invocation_calls'];assert local_children==sum(sum(block.values()) for block in c['blocks'].values())",1)])
# Independent read-back uses source parameters rather than the producer's reported live count.
p=ODD+'/audit_nine_template.py';s=(out/p).read_text();needle="c=json.load(gzip.open('work/pr361/complex/gcert1-e8-r783.json.gz'))";assert s.count(needle)==1
s=s.replace(needle,needle+"\nassert (c['h'],c['v'],c['R'],c['cst'])==(9,120,781,72)\nR=c['R'];N=2*c['v']+R;LIVE=8*c['v']*8+9*R;PHYSICAL=LIVE+R+c['h']+1\nassert (N,LIVE,PHYSICAL)==(1021,14709,15500)")
for old,new,count in [('14727','LIVE',11),('15520','PHYSICAL',1),('1023','N',2),('r*783','r*R',1),('s*783','s*R',1),('Q(999240641319551,10**18)','Q(1002626448253123,1000000000000000000)',1)]:
 assert s.count(old)==count,(old,s.count(old),count);s=s.replace(old,new)
changed(p,s,'Independent template decoder derives helper count, owner cardinalities, live/physical stock and expected exact price')
dump(out/'SOURCE-DIFFS.json',dict(source377_commit='d0a620fcc99ba012468d61d01f5bb14007076d50',source378_commit='c248962c3cf641d4f6226d63d86843f2c096a7d0',source390_commit='0e790f2dfb64e17bdee154aee151bb0c1dddb28e',source390_certificate_sha256='ba159f566568627d8459960500b9c285e9c9d69368f1b60fa27ae83f0a84c39a',source_manifest_sha256=sha(src/'MANIFEST.json'),candidate_sha256=sha(can),derived_files=changes))
run('fresh-local-admission',py+['work/native358/vendor/complex-reserve/admit.py','--source','work/native358/vendor/complex-reserve/upstream/pr352','--output','work/complex-nine-native/local-admission'])
control_code="import sys,json;sys.path.insert(0,"+repr(str(out/CX/'code'))+");import complex_scalars as C;c=json.load(open('candidate.json'));print(json.dumps(C.prefix_controls(c),sort_keys=True,indent=2))"
control_env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',CX_PINS=str(out/CX/'pins-e8.json'));control_env.pop('CX_RECORD',None)
run('target-read-extension-controls',py+['-c',control_code],control_env)
dump(out/'EXTENSION.json',read(out/'logs/target-read-extension-controls.log'))

for name,script in [('finite-data-banks-profile','complex_candidate.py'),('exact-clifford-recipes','verify_clifford_frames.py'),('exact-data-and-cover-phases','data_phases.py'),('global-template-and-invoice','global_nine.py'),('independent-template-two-moments','audit_nine_template.py'),('fixed-bit-outer-check','outer_fixed.py')]:run(name,py+[ODD+'/'+script])
z=out/'work/complex-nine-native';price=read(z/'INDEPENDENT-TEMPLATE-AUDIT.json');invoice=read(z/'GLOBAL-REVIEW.json');dirty=read(z/'local-admission/INDEPENDENT-AUDIT.json');cliff=read(z/'CLIFFORD-REVIEW.json')
assert price['coarse_complex']=='1002626448253123/1000000000000000000';assert (invoice['live'],invoice['physical'],invoice['cover_correction_calls'])==(14709,15500,14709);assert invoice['finite_invoice']['halving_degree']==2
assert all(q['independent_live_columns']==1021 and q['all_private_work_restored_zero']for q in dirty['scalar_words'].values());assert cliff['frames']==len(c['frames'])
assert {p.relative_to(src).as_posix():sha(p)for p in src.rglob('*')if p.is_file()and p!=src/'MANIFEST.json'}==manifest['files']
result=dict(status='PASS_SOURCE_BOUND_PR390_PREFIX_TWO_ALIAS_TWO_FRAMES_ORDINARY_NINE_STAGE',source377_manifest_sha256=sha(src/'MANIFEST.json'),candidate_sha256=sha(can),source_diffs_sha256=sha(out/'SOURCE-DIFFS.json'),stages=steps,complex_b=price['coarse_complex'],live=14709,physical=15500,local_columns=1021,frames=len(c['frames']),row=invoice['finite_invoice']['physical_row_coefficient'],proof_scope='Finite main-only target-to-target scalar extension with frozen original dirty response and cleanup; complete raw rational map and retained totals equality checked. PR377 compressed windows, exact phases, arbitrary correlated bank dirt, owner bijections and all finite guards freshly rechecked for the source-bound derived local word. Inherited local, compiler, complete-stream, precision, restored-row and analytic interfaces remain conditional; no new Lean kernel proof or final multiplication exponent claimed.')
dump(out/'VERIFICATION.json',result);print(json.dumps(result,indent=2),flush=True)
