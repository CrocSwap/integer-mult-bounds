"""Replay PR1193's pinned integer-flow constructor against the final native interfaces.
Only filesystem configuration is supplied; all mathematical construction code is unchanged.
"""
import argparse,importlib.util,sys,json,gzip
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--word3',type=Path,required=True);ap.add_argument('--word4',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();source=P/'vendor/pr1193';sys.path.insert(0,str(source));import construct as C
C.ROOT=P/'original-main'
parent=C.read(a.parent);mix=C.read(source/'data/MIX.json');order=C.read(source/'data/ORDER.json');roles,receipt=C.construct(parent,{'demote3':C.read(a.word3),'demote4':C.read(a.word4)},C.read(source/'data/FLOW.json.gz'),order,mix)
assert roles==C.read(source/'data/OWNERS.json.gz'),'frozen owner reconstruction'
m=C.load(C.ROOT/'research/complex-t21-owners/vendor/pr870/t16/build_parent.py','windows_again');windows,_=m.actual_windows(parent,order);used=Counter()
for z in roles:used[z['owner_replica'],z['child'],z['port']]+=z['width']
idle=Counter()
for k,(cap,ts) in windows.items():
 r,ch=map(int,k.split(','))
 for port in range(112):
  rem=cap-used[r,ch,port];assert rem>=0
  if rem:idle[rem]+=1
receipt['idle']=dict(idle);assert not a.out.exists();a.out.mkdir(parents=True);C.dump(a.out/'OWNERS.json.gz',roles);C.dump(a.out/'DISPATCH.json',[[s,r,{'demote3':'gauge44','demote4':'extra'}[pid]] for pid,s,r in mix]);C.dump(a.out/'CONSTRUCTION.json',receipt);print(receipt['status'],dict(idle),flush=True)

import controls
flow_controls=controls.check(parent,{'demote3':C.read(a.word3),'demote4':C.read(a.word4)},a.out/'FLOW-CONTROLS.json');assert len(flow_controls['rejected'])==8;print(flow_controls['status'],flush=True)
