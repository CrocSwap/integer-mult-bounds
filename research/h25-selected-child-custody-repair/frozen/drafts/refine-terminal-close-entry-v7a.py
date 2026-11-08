# Bounded passive source correction for three real close-helper-entry catches.
from pathlib import Path
import ast,hashlib,datetime,json
r=Path('/workspace/scratch/35c1441288db/h25-selected-child-construction-20261108T203610Z')
p=r/'implementation/supervisor_family_v3.py';s=p.read_text()
(r/'drafts/supervisor_family_v3-intermediate-v6.py.txt').write_text(s)
s=s.replace("close_error=None, sequence=None) for unused in range(32)]", "close_error=None, close_entry_error=None, sequence=None) for unused in range(32)]")
s=s.replace("slot.update(path=name, working=None, close_error=None, sequence=None)", "slot.update(path=name, working=None, close_error=None, close_entry_error=None, sequence=None)")
def block(pad,obj):
 return '\n'.join([
  pad+"slot['close_entry_error'] = error",
  pad+obj+".last_error = error",
  pad+"if "+obj+".first_error is None:",
  pad+"    "+obj+".first_error = error",
  pad+"if "+obj+".guard['primary'][0] is None:",
  pad+"    "+obj+".guard['primary'][0] = error",
  pad+"if "+obj+".error_count < 1024:",
  pad+"    "+obj+".error_events["+obj+".error_count][0] = 'metadata-close-helper-entry'",
  pad+"    "+obj+".error_events["+obj+".error_count][1] = error",
  pad+"    "+obj+".error_count = "+obj+".error_next["+obj+".error_count]",
  pad+"else:",
  pad+"    "+obj+".unknown = True",
 ])+'\n'
old="                    owner.close_fd(slot)\n                except BaseException as error:\n                    close_error = error\n"
new=old+block('                    ','owner')
assert s.count(old)==2
s=s.replace(old,new)
old="                except BaseException as error:\n                    if primary is None:\n                        primary = error\n        if primary is not None:\n"
new="                except BaseException as error:\n"+block('                    ','self')+"                    if primary is None:\n                        primary = error\n        if primary is not None:\n"
assert s.count(old)==1
s=s.replace(old,new)
ast.parse(s)
p.write_text(s)
b=s.encode();row={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path':'implementation/supervisor_family_v3.py','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'supersedes':'TERMINAL-SOURCE-FREEZE.json v6 retained unchanged','validation':'AST only; no target import/execution','source_hard_stop':'2026-11-08T21:36:10Z'}
(r/'proofs/TERMINAL-SOURCE-FREEZE-v7.json').write_text(json.dumps(row,indent=2)+'\n')
print(row)
