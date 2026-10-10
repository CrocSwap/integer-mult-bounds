#!/usr/bin/env python3
"""Log every source-derived p10 parameterization; leave the vendored p11 files unchanged.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'vendor/neutral/portable-code'
changes={
'complex_labels':[
 ('need(all(c.get(k)==v for k,v in BASE.items()), "baseline parameter/count mismatch")','need(c["h"]==20 and c["v"]==960 and c["R"]>0 and c["cst"]==20*18 and c["N"]==20*c["R"]+2*960*19+20*18, "p10 parameter/count identity")'),
 ('len(c["ret"])==22','len(c["ret"])==h'),('list(range(22))','list(range(h))'),('len({x[1] for x in c["ret"]})==22','len({x[1] for x in c["ret"]})==h'),
 ('dim[f]==20','dim[f]==h-2'),('by_role["c"][20]+=1;by_phase["copy"][20]+=1','by_role["c"][h-2]+=1;by_phase["copy"][h-2]+=1'),
 ('for k in range(22)','for k in range(h)'),('"temporary_centers":22','"temporary_centers":h'),('"Cc_copy_additions":22','"Cc_copy_additions":h')],
'complex_scalars':[
 ('V,R,H=1320,9036,22','V=R=H=None\ndef configure(c):\n    global V,R,H\n    V,R,H=c["v"],c["R"],c["h"]\n    need((V,H)==(960,20) and R>0,"p10 scalar dimensions")'),
 ('("recursive_center",k,20)','("recursive_center",k,H-2)'),
 ('"68230 existing live-label transitions, unchanged; not scalar macros"','"Live-label transitions are independently recounted and charged by the label and splice checkers; not scalar macros"'),
 ('0<=k<22 and e[2]==20','0<=k<H and e[2]==H-2'),('children==22','children==H'),
 ('"moment_live_width":14316','"moment_live_width":4*V+R'),('"new_work_stock_only":9037','"new_work_stock_only":R+1'),('"1/(14316*|Orth(110,2)|)"','f"1/({4*V+R}*|Orth({5*H},2)|)"')],
'complex_splice':[
 ('V,R,H,N,W=1320,9036,22,11676,14316','V=R=H=N=W=None\ndef configure(c):\n    global V,R,H,N,W\n    V,R,H=c["v"],c["R"],c["h"]\n    N,W=2*V+R,4*V+R\n    need((V,H)==(960,20) and R>0,"p10 splice dimensions")'),
 ("0 if ori=='forward' else f,20)","0 if ori=='forward' else f,H-2)"),
 ("((f,0,20) if ori=='forward' else (0,f,20))","((f,0,H-2) if ori=='forward' else (0,f,H-2))"),
 ("counts['center']==22","counts['center']==H"),
 ("family='baseline5stageComplex',m=110,live=14316,physical=23375","family='p10FiveStageComplex',m=5*H,live=W,physical=W+R+H+1"),
 ('centers=[14316,14338],tableau=[14338,23374],coefficient=[23374,23375]','centers=[W,W+H],tableau=[W+H,W+H+R],coefficient=[W+H+R,W+H+R+1]'),
 ('recursive_volume_denominator=14316','recursive_volume_denominator=W'),('maintained_guard_changed=False','maintained_guard_changed=True'),
 ('work=list(range(14316,23375))','work=list(range(W,W+R+H+1))')],
'complex_basis':[], 'complex_gx':[]}
result={}
for name,edits in changes.items():
 raw=(SOURCE/(name+'.py')).read_bytes();text=raw.decode();log=[]
 for old,new in edits:
  assert text.count(old)==1,(name,old,text.count(old));text=text.replace(old,new);log.append(dict(old=old,new=new))
 data=text.encode();(ROOT/'code'/(name+'.py')).write_bytes(data)
 result[name]=dict(source=(SOURCE/(name+'.py')).relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(raw).hexdigest(),derived_sha256=hashlib.sha256(data).hexdigest(),parameterizations=log)
(ROOT/'DERIVATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
