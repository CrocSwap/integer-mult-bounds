"""Narrow checked adaptations of frozen portable ancestors; no source mutation.
All literal counts, before/after hashes and exact diffs are emitted for review.
Prepared with OpenAI Codex assistance; inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import difflib,json,shutil
HERE=Path(__file__).resolve().parent
OLD='468460de3bb2ebf6c89b3156fdd332623596f7f6ae74324362862324cf71a98c'
NEW='b3a4d85639801f4fa73b0e742c1e860d2e96aa43fb30daff875c5b009033df2b'
OLD_STATUS='PASS_SOURCE_BOUND_PR390_PREFIX_TWO_ALIAS_TWO_FRAMES_ORDINARY_NINE_STAGE'
NEW_STATUS='PASS_SOURCE_BOUND_PR395_SIGNED_PREFIX_TWO_ALIAS_TWO_FRAMES_ORDINARY_NINE_STAGE'
def prepare(ordinary,fusion,out):
 ordinary,fusion,out=map(Path,[ordinary,fusion,out]);assert not out.exists();out.mkdir()
 records={}
 def derive(name,source,pairs):
  before=source.read_bytes();s=before.decode();changes=[]
  for old,new,count in pairs:
   assert s.count(old)==count,(name,old,s.count(old),count);s=s.replace(old,new)
   changes.append(dict(old=old,new=new,count=count))
  after=s.encode();(out/name).write_bytes(after)
  records[name]=dict(source_package='ordinary'if source.parent==ordinary else'fusion',source_file=source.name,source_sha256=sha256(before).hexdigest(),derived_sha256=sha256(after).hexdigest(),literal_replacements=changes,
   unified_diff=''.join(difflib.unified_diff(before.decode().splitlines(True),s.splitlines(True),fromfile='upstream/'+source.name,tofile='derived/'+name)))
 derive('replay.py',ordinary/'replay.py',[
  ("ap.add_argument('out',type=Path)","ap.add_argument('ordinary_package',type=Path);ap.add_argument('sources390',type=Path);ap.add_argument('out',type=Path)",1),
  ("candidate.build(src378,a.far_package.resolve(),out/'prefix-native')","candidate.build(src378,a.far_package.resolve(),a.ordinary_package.resolve(),a.sources390.resolve(),out/'prefix-native')",1),
  ("candidate.native_sources(out/'prefix-roundtrip-control')","candidate.native_sources(out/'prefix-roundtrip-control',a.ordinary_package.resolve())",1),
  ("assert all((out/'prefix-native'/name).read_bytes()==(out/'prefix-roundtrip-control'/name).read_bytes()for name in source_transport['files'])","assert all((out/'prefix-native/e8-signed-prefix'/pin['source_path']).read_bytes()==(out/'prefix-roundtrip-control/e8-signed-prefix'/pin['source_path']).read_bytes()for pin in read(Path(__file__).with_name('PR395-SOURCE.json'))['files'].values())",1),
  (OLD,NEW,1),('1002626448253123,1000000000000000000','979981116881,976562500000000',1),('1002626448253123/1000000000000000000','979981116881/976562500000000',1),
  ("source390_commit='0e790f2dfb64e17bdee154aee151bb0c1dddb28e',source390_certificate_sha256='ba159f566568627d8459960500b9c285e9c9d69368f1b60fa27ae83f0a84c39a'","source395_commit='dcebad83e4d7e6a5643ba8edfb432b0ba0dd1826',source395_certificate_sha256='1b096c5c2c8336205172cb4733a4c36f12fffd0ad5a72e9e2bc50899075840ae'",1),
  (OLD_STATUS,NEW_STATUS,1)])
 derive('prefix_extension.py',ordinary/'prefix_extension.py',[
  ('len(target_adds)==36','len(target_adds)==50',1),('target_reading_main_adds=36','target_reading_main_adds=50',1),
  ("recover=next(i for i in target_adds if any(a>0 for _,a,_ in c['B'][i][3]))","recover=next(i for i in target_adds if i>=25)\n    signed_setup=next(i for i in target_adds if i<25 and c['B'][i][3][0][1]>0)\n    sg=c['B'][signed_setup];signed_recover=next(i for i in target_adds if i>=25 and c['B'][i][2]==sg[2] and c['B'][i][3][0][0]==sg[3][0][0]);need(c['B'][signed_recover][3][0][1]<0,'signed recovery sign')",1),
  ("'target_to_source','target_to_helper']:","'target_to_source','target_to_helper','wrong_signed_setup','wrong_signed_recovery']:",1),
  ("elif name=='changed_helper_word':","elif name in ('wrong_signed_setup','wrong_signed_recovery'):bad['B'][signed_setup if name=='wrong_signed_setup' else signed_recover][3][0][1]*=-1\n        elif name=='changed_helper_word':",1)])
 derive('hetero_replay.py',fusion/'hetero_replay.py',[(OLD,NEW,2),(OLD_STATUS,NEW_STATUS,1),('==165628','==165764',1),('==1236771','==1234467',1),('Q(501324526735289,5*10**17)','Q(100352330809581,10**17)',1),
  ('1001644754304116452673767/1000000000000000000000000000','62657328603654011240787/62500000000000000000000000',1),
  ("assert read(ORD/'EXTENSION.json')['status']=='PASS_MAIN_ONLY_TARGET_READ_EXTENSION_CONTROLS'","assert read(ORD/'EXTENSION.json')['status']=='PASS_MAIN_ONLY_TARGET_READ_EXTENSION_CONTROLS'\n  assert set(read(ORD/'EXTENSION.json')['controls_rejected'])=={'missing_initial_subtraction','missing_recovery','changed_helper_word','target_to_source','target_to_helper','wrong_signed_setup','wrong_signed_recovery'}",1)])
 derive('fusion_replay.py',fusion/'fusion_replay.py',[(OLD,NEW,1),(OLD_STATUS,NEW_STATUS,1),
  ('199b967e9cd8c1ea6b661eb355552bc3d6d255d998d1c2d51f238b42edd71cc3','1f2dc91937b12b59a110d1a37af2fe62d2292b026d1e54c333d24acb66a1d02d',2),
  ('==1235907','==1233603',1),('Q(501407775311651,5*10**17)','Q(1003690096245309,10**18)',1),
  ('50090545902704112039161/50000000000000000000000000','1002683711531694437430077/1000000000000000000000000000',1)])
 for name in ['candidate.py','PR395-SOURCE.json','pr395_construct.py','pr395_SELECTION.json','pr395_EXPECTED-DISCOVERY.json','pr395_PROOF.md']:shutil.copyfile(HERE/name,out/name)
 shutil.copyfile(fusion/'transport.py',out/'transport.py')
 records['transport.py']=dict(source_package='fusion',source_sha256=sha256((fusion/'transport.py').read_bytes()).hexdigest(),unchanged=True)
 (out/'ADAPTATION.json').write_text(json.dumps(records,sort_keys=True,indent=2)+'\n')
 return records
