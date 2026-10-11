"""Compose checked literal adapters on the unchanged signed25 runtime.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import difflib,importlib.util,json,shutil
HERE=Path(__file__).resolve().parent
OLD='b3a4d85639801f4fa73b0e742c1e860d2e96aa43fb30daff875c5b009033df2b'
NEW='4e84f869ce94f67d3d3419428d21117759a9e7482483786d79930a3d2e1a358b'
OLD_STATUS='PASS_SOURCE_BOUND_PR395_SIGNED_PREFIX_TWO_ALIAS_TWO_FRAMES_ORDINARY_NINE_STAGE'
NEW_STATUS='PASS_SOURCE_BOUND_PR395_SIGNED_PREFIX_TWO_ALIAS_THREE_FRAMES_ORDINARY_NINE_STAGE'
def prepare(parent,ordinary,fusion,out):
 parent,ordinary,fusion,out=map(Path,[parent,ordinary,fusion,out])
 s=importlib.util.spec_from_file_location('frozen_signed25_adapter',parent/'adapt.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 previous=m.prepare(ordinary,fusion,out);records={}
 def derive(name,pairs):
  before=(out/name).read_bytes();text=before.decode();changes=[]
  for old,new,count in pairs:
   assert text.count(old)==count,(name,old,text.count(old),count);text=text.replace(old,new);changes.append(dict(old=old,new=new,count=count))
  after=text.encode();(out/name).write_bytes(after)
  records[name]=dict(source_sha256=sha256(before).hexdigest(),derived_sha256=sha256(after).hexdigest(),literal_replacements=changes,
    unified_diff=''.join(difflib.unified_diff(before.decode().splitlines(True),text.splitlines(True),fromfile='signed25/'+name,tofile='one-frame/'+name)))
 derive('replay.py',[(OLD,NEW,1),(OLD_STATUS,NEW_STATUS,1),('979981116881,976562500000000','1003541032710437,1000000000000000000',1),('979981116881/976562500000000','1003541032710437/1000000000000000000',1)])
 derive('hetero_replay.py',[(OLD,NEW,2),(OLD_STATUS,NEW_STATUS,1),('==1234467','==1234179',1),('Q(100352330809581,10**17)','Q(1003563678931709,10**18)',1),('62657328603654011240787/62500000000000000000000000','1002557547588352932020557/1000000000000000000000000000',1)])
 derive('fusion_replay.py',[(OLD,NEW,1),(OLD_STATUS,NEW_STATUS,1),('1f2dc91937b12b59a110d1a37af2fe62d2292b026d1e54c333d24acb66a1d02d','04a35b8659059dd578d6de3d22bd034ecaf80657a552bed47d5cdac208725644',2),('==1233603','==1233315',1),('Q(1003690096245309,10**18)','Q(1003730480532223,10**18)',1),('1002683711531694437430077/1000000000000000000000000000','501362007436105050379299/500000000000000000000000000',1)])
 shutil.copyfile(out/'candidate.py',out/'signed_candidate.py');shutil.copyfile(HERE/'candidate.py',out/'candidate.py')
 records['candidate.py']=dict(parent_source_sha256=sha256((out/'signed_candidate.py').read_bytes()).hexdigest(),wrapper_sha256=sha256((out/'candidate.py').read_bytes()).hexdigest(),rule='Execute unchanged signed25 reconstruction, then only B1566 frame203 to942; assert source and final raw hashes, scalar identity, nesting and exact histogram delta.')
 result=dict(parent_adapter=previous,one_frame_adapter=records)
 (out/'ADAPTATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result
