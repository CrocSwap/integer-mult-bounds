"""Mutation controls for checkword.py: each mutated word must be rejected."""
import json, gzip, subprocess, copy, sys, random, os, tempfile
HERE=os.path.dirname(os.path.abspath(__file__))
src=sys.argv[1]
c=json.load(gzip.open(src,'rt'))
rng=random.Random(3)
muts=[]
def m1(c):  # drop one phase-B delivery gate
    c['B'].pop(len(c['B'])//2); return 'drop a phase-B gate'
def m2(c):  # deliver a junk sum at a frame outside the cap: move a B gate to the full frame
    g=c['B'][-1]; g[0]=c['final'][0]; return 'phase-B gate at the full frame (y beyond its cap)'
def m3(c):  # remove one dirt compensation source
    c['D'][0][2].pop(); return 'drop a dirt compensation read'
def m4(c):  # skip a cleanup gate
    c['C'].pop(10); return 'drop a cleanup gate'
def m5(c):  # wrong scatter row
    c['scatter'][5]=c['scatter'][5][1:]; return 'wrong scatter row'
def m6(c):  # an A gate at a smaller frame than one operand already reached
    for g in c['A']:
        if len(c['frames'][g[0]])>3:
            g[0]=c['start'][0]; break
    return 'phase-A gate frame not nested'
for f in (m1,m2,m3,m4,m5,m6):
    cc=copy.deepcopy(c); name=f(cc)
    tmp=os.path.join(tempfile.mkdtemp(),'mut.json.gz')
    with gzip.open(tmp,'wt') as fh: json.dump(cc,fh)
    r=subprocess.run([sys.executable,'-B',os.path.join(HERE,'checkword.py'),tmp,sys.argv[2]],capture_output=True,text=True)
    ok=r.returncode!=0
    assert ok, 'mutant accepted: '+name
    print(('REJECTED ' if ok else 'ACCEPTED!! ')+name+' :: '+(r.stderr.strip().splitlines()[-1][:100] if ok else ''))
print('PASS all 6 word-level negative controls rejected')
