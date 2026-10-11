"""Checked literal adapter above the unchanged frozen one-frame runtime.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import difflib,importlib.util,json,shutil
HERE=Path(__file__).resolve().parent
OLD='4e84f869ce94f67d3d3419428d21117759a9e7482483786d79930a3d2e1a358b'
NEW='c146daa0153a81f4050bc16bb607288233ee95085dd006688717ea2ecce2f79a'
OLD_STATUS='PASS_SOURCE_BOUND_PR395_SIGNED_PREFIX_TWO_ALIAS_THREE_FRAMES_ORDINARY_NINE_STAGE'
NEW_STATUS='PASS_SOURCE_BOUND_SIX_EDIT_UNION_ORDINARY_NINE_STAGE'
def prepare(frame,parent,ordinary,fusion,out):
 frame,parent,ordinary,fusion,out=map(Path,[frame,parent,ordinary,fusion,out])
 s=importlib.util.spec_from_file_location('frozen_oneframe_adapter',frame/'adapt.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 previous=m.prepare(parent,ordinary,fusion,out);records={}
 def derive(name,pairs):
  before=(out/name).read_bytes();text=before.decode();changes=[]
  for old,new,count in pairs:
   assert text.count(old)==count,(name,old,text.count(old),count);text=text.replace(old,new);changes.append(dict(old=old,new=new,count=count))
  after=text.encode();(out/name).write_bytes(after)
  records[name]=dict(source_sha256=sha256(before).hexdigest(),derived_sha256=sha256(after).hexdigest(),literal_replacements=changes,
    unified_diff=''.join(difflib.unified_diff(before.decode().splitlines(True),text.splitlines(True),fromfile='one-frame/'+name,tofile='six-edit/'+name)))
 derive('replay.py',[(OLD,NEW,1),(OLD_STATUS,NEW_STATUS,1),('1003541032710437,1000000000000000000','1003708110639863,1000000000000000000',1),('1003541032710437/1000000000000000000','1003708110639863/1000000000000000000',1)])
 derive('hetero_replay.py',[(OLD,NEW,2),(OLD_STATUS,NEW_STATUS,1),('==1234179','==1233603',1),('Q(1003563678931709,10**18)','Q(1003730764356247,10**18)',1),('1002557547588352932020557/1000000000000000000000000000','1002724298127324779876329/1000000000000000000000000000',1)])
 derive('fusion_replay.py',[(OLD,NEW,1),(OLD_STATUS,NEW_STATUS,1),('04a35b8659059dd578d6de3d22bd034ecaf80657a552bed47d5cdac208725644','9e55e5ffb38418ac2f872a77341acfcb60af2cc3486aad22fdd967939cffc23b',2),('==1233315','==1232739',1),('Q(1003730480532223,10**18)','Q(20077952432153,2*10**16)',1),('501362007436105050379299/500000000000000000000000000','501445410447465306780471/500000000000000000000000000',1)])
 shutil.copyfile(out/'candidate.py',out/'frame_candidate.py');shutil.copyfile(HERE/'candidate.py',out/'candidate.py')
 records['candidate.py']=dict(parent_source_sha256=sha256((out/'frame_candidate.py').read_bytes()).hexdigest(),wrapper_sha256=sha256((out/'candidate.py').read_bytes()).hexdigest(),rule='Execute unchanged one-frame reconstruction, four proven commuting same-target triple permutations with frame changes, and two target-read upper-frame changes; assert source/final hashes and all nested labels.')
 result=dict(parent_adapter=previous,six_edit_adapter=records)
 (out/'ADAPTATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result
