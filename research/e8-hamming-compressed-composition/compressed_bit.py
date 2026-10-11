"""Fresh R822 compressed m64/T8 replay with explicitly charged signed repair.

Uses the freshly completed frozen helper-reuse parent, never cached records.
Native PR386 geometry and global template are dimension/profile adaptations;
all retained compiler/bit/precision obligations remain conditional.
OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,os,shutil,subprocess,sys,gzip,struct,zlib
if not __debug__:raise RuntimeError('Assertions required')
sha=lambda p:sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
SIGNED_SHA='00af20d9f6fdc5e05e3856e1a1fb92e5defce6950d207193f88781edad2e1fe1'
WORD_RAW='9974db5500941456e49030a5e5f374f34c707f76a40904fe1833df4f893a1c69'
EDITS={
 'geometry.py':[("bitE8-r865.json.gz","bitE8-r822.json.gz"),("(8,120,865,'<x,y>/2')","(8,120,822,'<x,y>/2')")],
 'global_word.py':[
 ('H,V,R,L,K,T,M=8,120,865,9,4,8,64','H,V,R,L,K,T,M=8,120,822,9,4,8,64'),('bitE8-r865.json.gz','bitE8-r822.json.gz'),("'452036410121261/500000000000000000'","'247970809397543/250000000000000000'"),("formal_columns_checked']==1345","formal_columns_checked']==1542"),('14603','14689'),('==8672','==8328'),('{1:2076,2:942,3:448,4:418,5:308,6:2,8:18}','{1:2157,2:902,3:505,4:333,5:274,6:1,8:18}'),('==62280','==59184'),('{1:149472,2:67824,3:32256,4:30096,5:22176,6:144,7:5760,8:1296,14:3840,28:3840,42:3840}','{1:155304,2:64944,3:36360,4:23976,5:19728,6:72,7:5760,8:1296,14:3840,28:3840,42:3840}'),('stage*865','stage*822'),('865*replica','822*replica'),('banks_per_stage=865','banks_per_stage=822')],
 'audit.py':[('15465','15078'),('15464','15077'),('1105','1062'),('865','822'),('7785','7398')],
}
NATIVE={'geometry.py':'36eeda3184bd009e89462b65c8725d10860c444f8da8f1f87e5f6e50120011ca','global_word.py':'2c438be46213e014170e607a745185e45e33c7b7240b833efc86a2330de0d1f6','audit.py':'75811327b0d6cbd56aae8e28d72abd42d57c7f3f3630781d045efee2d36446e9'}
def stored_gzip(data):
 result=bytearray(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff')
 for i in range(0,max(1,len(data)),65535):
  block=data[i:i+65535];result.append(int(i+65535>=len(data)));result.extend(struct.pack('<HH',len(block),len(block)^65535));result.extend(block)
 result.extend(struct.pack('<II',zlib.crc32(data)&0xffffffff,len(data)&0xffffffff));assert gzip.decompress(result)==data;return bytes(result)
def run(package,native386,bit370,bit_replay,signed_package,output):
 package,native386,bit370,bit_replay,signed_package,output=map(lambda p:Path(p).resolve(),(package,native386,bit370,bit_replay,signed_package,output))
 assert not output.exists()and not output.is_relative_to(package)and not output.is_relative_to(native386)
 prior=read(bit_replay/'RECEIPT.json');assert prior['status']=='PASS_SOURCE_BOUND_CONDITIONAL_E8_HELPER_REUSE_AND_ASSEMBLY';assert prior['helper_reuses']==43 and prior['frame_changes']==128
 raw=gzip.decompress((bit_replay/'word.json.gz').read_bytes());assert sha256(raw).hexdigest()==prior['word_sha256']==WORD_RAW
 assert sha(signed_package/'signed_source.py')==SIGNED_SHA
 source_before={n:sha(native386/n)for n in NATIVE};assert source_before==NATIVE
 parent_files=['RECEIPT.json','word.json.gz','records/249-records.bin','records/249-states.json','records/frames.json','kappa.json','columns-k3-r822','parent/bin/legality','parent/bin/legality_ncopy_h']
 parent_before={n:sha(bit_replay/n)for n in parent_files};output.mkdir(parents=True);checks=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
 def command(name,args):
  print('COMPRESSED',name,flush=True)
  with (output/(name+'.log')).open('w')as f:subprocess.run(list(map(str,args)),env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  checks.append(name)
 def py(name,script,*args):command(name,[sys.executable,'-B',script,*args])
 (output/'word.json.gz').write_bytes(stored_gzip(raw));(output/'source/data/bit').mkdir(parents=True);shutil.copyfile(output/'word.json.gz',output/'source/data/bit/bitE8-r822.json.gz')
 py('fresh-export',bit370/'code/bit/export_records.py',output/'word.json.gz',output/'records')
 assert {f:sha(output/'records'/f)for f in prior['records']}==prior['records']
 for f in prior['records']:assert (output/'records'/f).read_bytes()==(bit_replay/'records'/f).read_bytes()
 (output/'local').mkdir();shutil.copytree(output/'records',output/'local/records');shutil.copyfile(bit_replay/'kappa.json',output/'local/kappa.json')
 py('word',bit370/'code/bit/independent/checkword.py',output/'word.json.gz',bit370/'code/pricing')
 py('word-controls',bit370/'code/bit/independent/mutate.py',output/'word.json.gz',bit370/'code/pricing')
 py('stage',bit370/'code/bit/regression/stage_cohort.py',output/'records',output/'records',output/'local/cin',output/'local/cout')
 command('legality',[bit_replay/'parent/bin/legality',output/'local/cin',output/'local/cout',output/'local/cout/legality.json'])
 command('columns',[bit_replay/'columns-k3-r822',output/'local/cout/COHORT249-RECORDS.bin',output/'local/cout/columns.json'])
 py('record-controls',bit370/'code/bit/mutate_records.py',output/'records',output/'local/cin',output/'local/cout',bit_replay/'parent/bin/legality',bit_replay/'columns-k3-r822',bit_replay/'parent/bin/legality_ncopy_h')
 py('gram',bit370/'code/bit/checkers/gram_frames.py',output/'records','--gram','e8ham','--h','8','--positive')
 shutil.copyfile(signed_package/'signed_source.py',output/'signed_source.py');py('signed',output/'signed_source.py')
 adaptation={}
 for name,edits in EDITS.items():
  text=(native386/name).read_text();changes=[]
  for old,new in edits:
   count=text.count(old);assert count>0;(changes.append([old,new,count]));text=text.replace(old,new)
  (output/name).write_text(text);adaptation[name]=dict(source_sha256=NATIVE[name],derived_sha256=sha(output/name),literal_replacements=changes)
 (output/'ADAPTATION.json').write_text(json.dumps(adaptation,sort_keys=True,indent=2)+'\n')
 py('geometry',output/'geometry.py','--source',output/'source','--out',output/'full')
 py('global',output/'global_word.py','--source',output/'source','--local-check',output/'local','--out',output/'full')
 gp=output/'full/GLOBAL-TEMPLATE.json.gz';payload=gzip.decompress(gp.read_bytes());gp.write_bytes(stored_gzip(payload));assert sha256(payload).hexdigest()==read(output/'full/GLOBAL.json')['template_sha256']
 py('audit',output/'audit.py','--local-check',output/'local','--out',output/'full')
 py('signed-finite-price',package/'compressed_price.py',output,bit370)
 assert {n:sha(native386/n)for n in NATIVE}==source_before and {n:sha(bit_replay/n)for n in parent_files}==parent_before
 w=json.loads(raw);old=json.loads(gzip.decompress((bit370/'data/bit/bitE8-r865.json.gz').read_bytes()));assert w['lines']==old['lines']and w['h']==old['h']==8 and w['v']==old['v']==120
 supplier=read(output/'full/SUPPLIER.json');assert supplier['bit_coarse']=='1084538480613107696451/1000000000000000000000000'
 # Preserve all scientific fields; replace only timing-bearing receipt hashes
 # by hashes of the same complete scientific payload. Native receipts remain.
 def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
 def projected(path,drop):
  obj=read(path);return {k:v for k,v in obj.items()if k not in drop}
 signed_science=projected(output/'RESULT.json',{'seconds','input_sha256','source_pr376_candidate_sha256'})
 signed_science['word_raw_sha256']=WORD_RAW
 geometry_science=projected(output/'full/GEOMETRY.json',{'seconds','word_sha256'});geometry_science['word_raw_sha256']=WORD_RAW
 gh=sha256(canon(geometry_science)).hexdigest()
 template=json.loads(payload);assert template['geometry_sha256']==sha(output/'full/GEOMETRY.json');template['geometry_sha256']=gh
 th=sha256(canon(template)).hexdigest()
 global_science=projected(output/'full/GLOBAL.json',{'seconds','word_sha256','geometry_sha256','template_sha256'});global_science.update(word_raw_sha256=WORD_RAW,geometry_science_sha256=gh,template_science_sha256=th)
 audit_science=projected(output/'full/AUDIT.json',{'seconds','template_sha256'});audit_science['template_science_sha256']=th
 science=dict(status='PASS_CANONICAL_COMPRESSED_R822_SCIENTIFIC_PROJECTION',word_raw_sha256=WORD_RAW,records=prior['records'],signed=signed_science,geometry=geometry_science,global_word=global_science,audit=audit_science,supplier={k:v for k,v in supplier.items()if k!='inputs'},complete_template_science_sha256=th,projection_rule='Only elapsed seconds, runtime input provenance and compressed/timing-bearing receipt hashes are excluded or replaced by full decoded scientific payload hashes. No operator, geometry, owner, schedule, scalar, profile, cost or constraint fields are removed.')
 (output/'SCIENCE.json').write_text(json.dumps(science,sort_keys=True,indent=2)+'\n')
 receipt=dict(status='PASS_PORTABLE_FRESH_R822_COMPRESSED_SIGNED_SUPPLIER',checks=checks,word_raw_sha256=WORD_RAW,records=prior['records'],source_before_after=source_before,parent_before_after=parent_before,signed_source_sha256=SIGNED_SHA,bit_coarse=supplier['bit_coarse'],supplier_sha256=sha(output/'full/SUPPLIER.json'),science_sha256=sha(output/'SCIENCE.json'),adaptation_sha256=sha(output/'ADAPTATION.json'),scope='K3 native replay supplies local checks only; all nine-stage scalar, owner and signed-prefix checks freshly generated. Deterministic stored-deflate transport changes no decoded word/template. Defining integer decoder J mod2=I, not unsigned integer identity; common-grid/conditional compiler/bank/precision and C_full obligations retained.')
 (output/'RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');return output/'full/SUPPLIER.json',receipt
if __name__=='__main__':
 assert len(sys.argv)==7
 print(run(*sys.argv[1:])[0])
