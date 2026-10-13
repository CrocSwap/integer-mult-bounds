"""Test PR508's four-gauge collapse on PR507's new retimed partial-own factory.
This constructor/profile screen is not global physical admission.
"""
from pathlib import Path
from collections import Counter
import json,gzip,sys,copy
R=Path(__file__).resolve().parent;O=R/'pr507-coordinated-gauge-screen';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'source507-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
B=R/'pr507-local-replay/gauge80-kernel42';raw=json.load(gzip.open(B/'sc_base/FULL-WORD.json.gz'));full=json.load(gzip.open(B/'split-centres/FULL-WORD.json.gz'));sel=json.load(open(R/'source507-review/data/KERNEL-SELECTION.json'));n=len(full['A'])-len(raw['A']);assert [e[:-1]for e in raw['A']]==[e[:-1]for e in full['A'][n:]]and[e[:-1]for e in raw['B']]==[e[:-1]for e in full['B']];raw['A']=full['A'][n:];raw['B']=full['B'];raw['cleanup']=[G.inverse(e,G.FULL)for e in reversed(raw['A']+raw['B'])if not 120<=e[1]<240];baseline=G.build(raw,sel);assert baseline['A']==full['A']and baseline['B']==full['B']and G.profile(baseline)==G.profile(full)
(O/'BARE-RETIMED.json.gz').write_bytes(G.dump(raw));rows=[]
for name,helpers in [('single',[540]),('all-four',[540,541,542,543])]:
 s=copy.deepcopy(sel)
 for h in helpers:s['gauge'][str(h)]=[408,102]
 try:
  w=G.build(raw,s);H=w['report']['local_profile'];wc=dict(Counter(G.widths_of(w)));row=dict(label=name,status='PASS_LOCAL_CONSTRUCTOR_ONLY',profile=H,widths=wc,scope='Joint-gauge idea credited to PR508 head3213fc136270ca8372ce9f8fbb828e78ba96cecf; new partial-own factory fromPR507. Local profile only; physical and complete composition verification pending.');(O/(name+'-WORD.json.gz')).write_bytes(G.dump(w));(O/(name+'-SELECTION.json')).write_text(json.dumps(s,indent=2)+'\n')
 except AssertionError as e:row=dict(label=name,status='REJECTED_LOCAL_CONSTRUCTOR',error=repr(e))
 rows.append(row);print(row,flush=True)
(O/'RESULT.json').write_text(json.dumps(rows,indent=2)+'\n')
