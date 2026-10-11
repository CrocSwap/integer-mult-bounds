"""Source-bound signed witness, complete B4 prefix and reconstructed finite bill.

Usage: signed9.py SOURCE401 FRESH_BIT9 SIGNED7_REPLAY SIGNED7_PACKAGE OUT
Fresh BIT9 is the unchanged source401 bit-compose-replay output. SIGNED7_REPLAY
supplies the same local signed defining witness, not a seven-stage bound.
"""
from pathlib import Path
from hashlib import sha256
import json,sys,importlib.util,types
assert __debug__
sys.dont_write_bytecode=True
SOURCE,BIT,SIGNED,PACKAGE,OUT=map(lambda x:Path(x).resolve(),sys.argv[1:])
assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(Path(p).read_text())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
write=lambda n,x:(OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
assert digest(SOURCE/'MANIFEST.json')=='5ff08a6c7b051d227fcd516542b56718ae65bca93615acfe09cb8785d8e3f43c'
assert {p.relative_to(SOURCE).as_posix():digest(p)for p in SOURCE.rglob('*')if p.is_file()and p!=SOURCE/'MANIFEST.json'}==read(SOURCE/'MANIFEST.json')['files']
assert digest(PACKAGE/'MANIFEST.sha256')=='636b41161a8cc647ab046460af76d1c78112341e43cb50e914c4c3d4f0f2906a'
for line in(PACKAGE/'MANIFEST.sha256').read_text().splitlines():
 h,n=line.split(None,1);assert digest(PACKAGE/n)==h
assert read(SIGNED/'RECEIPT.json')['status']=='PASS_FULL_FRESH_COMPOSITION_AND_SIGNED_BIT_SUPPLEMENT'
assert read(BIT/'BIT-COMPOSITION-RECEIPT.json')['status']=='PASS_NEW_PR376_R822_PR381_B4_COMPOSITION'
assert digest(BIT/'records/249-records.bin')=='9d40536b6cbbedbf11ff3eaa051482db5f2e7a1774ac05bb3ae5e3bbedda44bf'
assert digest(SIGNED/'validation/signed-work/signed-records.bin')=='58082e94b4627d2a0012f5c31d2fc3ad68aa4412fe96b7e0e631df36aaf67509'
changes={}
def adapt(name,substitutions):
 p=PACKAGE/(name+'.py');raw=p.read_bytes();text=raw.decode();log=[]
 for old,new in substitutions:
  count=text.count(old);assert count>0,old
  text=text.replace(old,new);log.append(dict(old=old,new=new,count=count))
 changed=OUT/(name+'_k4.py');changed.write_text(text)
 changes[name]=dict(source_sha256=digest(p),adapted_sha256=digest(changed),literal_substitutions=log)
 module=types.ModuleType('signed9_'+name);module.__file__=str(changed)
 exec(compile(text,str(changed),'exec'),module.__dict__);return module
prefix=adapt('prefix',[
 ('module.check(3,8)','module.check(4,8)'),
 ("checked['stages']==checked['invocations']==7 and checked['gates']==12 and checked['m']==56","checked['stages']==checked['invocations']==9 and checked['gates']==18 and checked['m']==72"),
 ('assert stage==6','assert stage==8'),('range(1,4)','range(1,5)'),
 ('v,R,K,S,T=120,822,3,7,7','v,R,K,S,T=120,822,4,9,3'),
 ('bridged.check(3,8)','bridged.check(4,8)'),('seven-stage','nine-stage'),('SEVEN_STAGE','NINE_STAGE'),('seven replicas','three replicas')])
template_path=SOURCE/'vendor/bit/code/complex/code/bridged.py'
assert digest(template_path)=='5fe7174cd3a6580a74e4c1bf8fa7b426e8673f1c285603bf3076d4e758d70731'
template,binding=prefix.source_template(template_path,digest(template_path))
write('SCHEDULE.json',dict(template=template,binding=binding))
actual=prefix.run(BIT/'records/249-records.bin',template,binding)
witness=prefix.run(SIGNED/'validation/signed-work/signed-records.bin',template,binding)
assert actual['payload_prefix']==2133914541865385324329415661
assert witness['payload_prefix']==2322527544491781479390103469
write('PREFIX.json',actual);write('SIGNED-PREFIX.json',witness)
invoice=adapt('invoice',[
 ('(8,120,822,56,7,10794,3)','(8,120,822,72,3,5346,4)'),
 ('==1512','==936'),('==6274','==10370'),('max(H)==34','max(H)==50'),
 ('(14,7,28,7,34,20,6)','(50,14,7,36,28,7,22,42,7,8)'),
 ('56223565806031','71903549469403'),('56223565818967','71903549476531'),
 ('12936','7128'),('==46','==47'),('.bit_length()==71','.bit_length()==91'),('bits=71','bits=91'),
 ('SEVEN_STAGE','NINE_STAGE'),('seven stages and seven replicas','nine stages and three replicas'),
 ('B3 geometry','B4 geometry')])
priced=read(BIT/'kappa.json');native=read(BIT/'columns.json')
assert [(x['stage'],x['signed_inverse'])for x in native['stages']]==list(enumerate(template['reverse']))
assert template['checked_idle']['blocks_per_role_pair']==priced['idle_blocks_per_role_pair']
finite=invoice.run(priced,read(BIT/'finite.json'),read(BIT/'finite-input.json'),
 BIT/'records/249-records.bin',SIGNED/'validation/signed-work/signed-records.bin',
 read(SIGNED/'validation/SIGNED.json'),actual,witness)
assert finite['coefficient']==71903549476531<2**80
assert finite['row_reserve']['internal_coefficient']==10370
assert finite['payload_prefix_bits']==finite['signed_witness_payload_bits']==91
write('FINITE.json',finite);write('ADAPTATIONS.json',changes)
result=dict(status='PASS_SOURCE_BOUND_R822_NINE_STAGE_SIGNED_WITNESS_COMPLETE_PREFIX_AND_FINITE_BILL',
 source_commit='7844f72c6051a4408284c3092490687061675c1a',source_manifest_sha256=digest(SOURCE/'MANIFEST.json'),
 fresh_native_bit_receipt_sha256=digest(BIT/'BIT-COMPOSITION-RECEIPT.json'),
 signed_witness_replay_sha256=digest(SIGNED/'RECEIPT.json'),local_signed_proof_sha256=digest(SIGNED/'validation/SIGNED.json'),
 bit_coarse=priced['bit_coarse'],K=4,stages=9,T=3,m=72,W=5346,maxchild=50,halving_degree=2,
 internal_restored_rows=10370,local_invocations=27,weighted_compensation_per_invocation=112,unit_compensation_per_invocation=264,
 original_counted_coefficient=71903549469403,corrected_signed_coefficient=finite['coefficient'],
 output_sha256={n:digest(OUT/n)for n in ['SCHEDULE.json','PREFIX.json','SIGNED-PREFIX.json','FINITE.json','ADAPTATIONS.json']},
 scope='The source401 native geometry/bank/route replay is required and bound; signed Z-restoration is the same local defining witness. Global endpoint proof is F2 and scalar prefix is source-template-derived, not separately emitted global IR. Dyadic chart/compiler, all-size ordinary/restored rows and dominating C_full cutoffs remain inherited obligations.')
write('RECEIPT.json',result);print(result['status'],result['bit_coarse'],finite['coefficient'])
