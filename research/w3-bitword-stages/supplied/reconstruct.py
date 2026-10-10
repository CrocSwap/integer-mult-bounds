#!/usr/bin/env python3
"""Rebuild full working directories from the package: work/base (PR249 snapshot) and work/w3 (the new word),
plus work/lead (official cohort layout). Usage: python3 reconstruct.py <workdir>"""
import gzip, json, os, shutil, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'work')
def gunzip(src, dst):
    with gzip.open(src, 'rb') as f, open(dst, 'wb') as g: shutil.copyfileobj(f, g)
base, w3, lead = (os.path.join(out, x) for x in ('base', 'w3', 'lead'))
for d in (base, w3, lead): os.makedirs(d, exist_ok=True)
for f in ('249-states.json', 'frames.json', '249-records.bin'):
    gunzip(os.path.join(HERE, 'base', f + '.gz'), os.path.join(base, f))
shutil.copy(os.path.join(HERE, 'base', '249-DONOR-OWNERSHIP.json'), base)
print('[1/3] base PR249 snapshot unpacked', flush=True)
for f in ('COHORT249-RECORDS.bin', 'COHORT249-FRAMES.json', 'COHORT249-INITIAL.json'):
    gunzip(os.path.join(HERE, 'word', f + '.gz'), os.path.join(lead, f))
shutil.copy(os.path.join(HERE, 'word', 'COHORT249-SELECTION.json'), lead)
print('[2/3] official cohort layout unpacked', flush=True)
shutil.copy(os.path.join(lead, 'COHORT249-RECORDS.bin'), os.path.join(w3, '249-records.bin'))
gunzip(os.path.join(HERE, 'word', 'w3-249-states.json.gz'), os.path.join(w3, '249-states.json'))
gunzip(os.path.join(HERE, 'word', 'w3-frames.txt.gz'), os.path.join(w3, 'frames.txt'))
gunzip(os.path.join(HERE, 'word', 'w3-states.txt.gz'), os.path.join(w3, 'states.txt'))
fj = json.load(open(os.path.join(base, 'frames.json')))
new = json.load(open(os.path.join(lead, 'COHORT249-FRAMES.json')))
assert not set(new) & set(fj['frames']), 'new frame ids collide with base'
fj['frames'].update(new)
json.dump(fj, open(os.path.join(w3, 'frames.json'), 'w'))
# consistency: initial states in cohort layout == w3 states
st = json.load(open(os.path.join(w3, '249-states.json')))
ini = json.load(open(os.path.join(lead, 'COHORT249-INITIAL.json')))
assert {k: int(v) for k, v in st['initial'].items()} == {k: int(v) for k, v in ini.items()}
sha = hashlib.sha256(open(os.path.join(w3, '249-records.bin'), 'rb').read()).hexdigest()
print('[3/3] w3 word assembled: records sha256', sha, flush=True)
