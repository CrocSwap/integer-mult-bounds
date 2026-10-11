"""Stage a PR249-format word for PR #266's official cohort checkers (empty kernel selection, no source owners or donors).
usage: stage_official.py BASE_SNAP WORD IN_DIR OUT_DIR"""
import json,sys,shutil,os
b,w,i,o=sys.argv[1:5];os.makedirs(i,exist_ok=True);os.makedirs(o,exist_ok=True)
st=json.load(open(w+'/249-states.json'));st.setdefault('source_owned_roles',[]);st.setdefault('regs',[])
json.dump(st,open(i+'/249-states.json','w'))
bf=json.load(open(b+'/frames.json'));wf=json.load(open(w+'/frames.json'))
json.dump(bf,open(i+'/frames.json','w'));json.dump({'donor_keys':[]},open(i+'/249-DONOR-OWNERSHIP.json','w'))
new={k:dict(x,dim=len(x['B'])) for k,x in wf['frames'].items() if k not in bf['frames']}
json.dump(new,open(o+'/COHORT249-FRAMES.json','w'))
json.dump({k:int(x) for k,x in st['initial'].items()},open(o+'/COHORT249-INITIAL.json','w'))
json.dump([],open(o+'/COHORT249-SELECTION.json','w'));shutil.copy(w+'/249-records.bin',o+'/COHORT249-RECORDS.bin')
print('   staged: new frames vs base',len(new),'n',st['n'],'v',st['v'])
