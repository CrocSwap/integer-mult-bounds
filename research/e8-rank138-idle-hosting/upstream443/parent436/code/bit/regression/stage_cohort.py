"""Stage a PR249-format word for PR266's official cohort checkers (empty kernel selection, no source owners/donors)."""
import json, os, shutil, sys
base, word, IN, OUT = sys.argv[1:5]
os.makedirs(IN, exist_ok=True); os.makedirs(OUT, exist_ok=True)
st = json.load(open(word + '/249-states.json')); st.setdefault('source_owned_roles', []); st.setdefault('regs', [])
json.dump(st, open(IN + '/249-states.json', 'w'))
bf = json.load(open(base + '/frames.json')); wf = json.load(open(word + '/frames.json'))
json.dump(bf, open(IN + '/frames.json', 'w')); json.dump({'donor_keys': []}, open(IN + '/249-DONOR-OWNERSHIP.json', 'w'))
json.dump({k: v for k, v in wf['frames'].items() if k not in bf['frames']}, open(OUT + '/COHORT249-FRAMES.json', 'w'))
json.dump({k: int(v) for k, v in st['initial'].items()}, open(OUT + '/COHORT249-INITIAL.json', 'w'))
json.dump([], open(OUT + '/COHORT249-SELECTION.json', 'w'))
shutil.copy(word + '/249-records.bin', OUT + '/COHORT249-RECORDS.bin')
