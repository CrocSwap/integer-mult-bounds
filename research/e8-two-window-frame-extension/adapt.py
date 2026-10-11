"""Checked literal adapter above the unchanged frozen six-edit runtime.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import difflib,importlib.util,json,shutil
HERE=Path(__file__).resolve().parent
OLD='c146daa0153a81f4050bc16bb607288233ee95085dd006688717ea2ecce2f79a'
NEW='a2a1e957cec4f86fa7447037d757218d72b7f70c67391cc4dfb81ed60c0d00e6'
OLD_STATUS='PASS_SOURCE_BOUND_SIX_EDIT_UNION_ORDINARY_NINE_STAGE'
NEW_STATUS='PASS_SOURCE_BOUND_TWO_WINDOW_UNION_ORDINARY_NINE_STAGE'
def prepare(union,frame,parent,ordinary,fusion,out):
 union,frame,parent,ordinary,fusion,out=map(Path,[union,frame,parent,ordinary,fusion,out])
 s=importlib.util.spec_from_file_location('frozen_sixedit_adapter',union/'adapt.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 previous=m.prepare(frame,parent,ordinary,fusion,out);records={}
 def derive(name,pairs):
  before=(out/name).read_bytes();text=before.decode();changes=[]
  for old,new,count in pairs:
   assert text.count(old)==count,(name,old,text.count(old),count);text=text.replace(old,new);changes.append(dict(old=old,new=new,count=count))
  after=text.encode();(out/name).write_bytes(after)
  records[name]=dict(source_sha256=sha256(before).hexdigest(),derived_sha256=sha256(after).hexdigest(),literal_replacements=changes,
    unified_diff=''.join(difflib.unified_diff(before.decode().splitlines(True),text.splitlines(True),fromfile='six-edit/'+name,tofile='two-window/'+name)))
 derive('replay.py',[(OLD,NEW,1),(OLD_STATUS,NEW_STATUS,1),('1003708110639863,1000000000000000000','25094722134999,25000000000000000',1),('1003708110639863/1000000000000000000','25094722134999/25000000000000000',1)])
 derive('hetero_replay.py',[(OLD,NEW,2),(OLD_STATUS,NEW_STATUS,1),('==1233603','==1233027',1),('Q(1003730764356247,10**18)','Q(1003811542742011,10**18)',1),('1002724298127324779876329/1000000000000000000000000000','1002804914590821401398903/1000000000000000000000000000',1)])
 derive('fusion_replay.py',[(OLD,NEW,1),(OLD_STATUS,NEW_STATUS,1),('9e55e5ffb38418ac2f872a77341acfcb60af2cc3486aad22fdd967939cffc23b','cf0ce85d2dd4775ac9f59dbb5d548b6a74279416b2e50f1a1731978b490e2d10',2),('==1232739','==1232163',1),('Q(20077952432153,2*10**16)','Q(1003978426913831,10**18)',1),('501445410447465306780471/500000000000000000000000000','50148573209899728522087/50000000000000000000000000',1)])
 shutil.copyfile(out/'candidate.py',out/'union_candidate.py');shutil.copyfile(HERE/'candidate.py',out/'candidate.py')
 records['candidate.py']=dict(parent_source_sha256=sha256((out/'union_candidate.py').read_bytes()).hexdigest(),wrapper_sha256=sha256((out/'candidate.py').read_bytes()).hexdigest(),rule='Execute unchanged six-edit reconstruction, then five-gate [4,0,3,2,1] and fifteen-gate [14,0,...,13] commuting target/helper windows with new first frame940; assert both intermediate hashes and every nested label.')
 result=dict(parent_adapter=previous,two_window_adapter=records)
 (out/'ADAPTATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result
