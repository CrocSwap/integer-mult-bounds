#!/usr/bin/env python3
"""Optional SciPy search; acceptance is always the separate literal verifier."""
import argparse,os,shutil,subprocess,sys
from pathlib import Path
from build import HERE,prepare,read,write,need
from generate import mod
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();work=a.work.resolve();work.mkdir(parents=True,exist_ok=False)
p=prepare(work/'pr2462');d=read(HERE/'evidence/order-screen.json.gz')
B=mod('source_windows',p/'vendor/build_parent.py');windows,_=B.actual_windows(read(p/'inputs/GLOBAL-TEMPLATE.json.gz'),d['order']);need(windows==d['windows'],'literal diagonal windows')
word=read(HERE/'evidence/eight-alias-base.json.gz');need({int(k):v for k,v in d['inventory'].items()}=={int(k):v for k,v in word['report']['width_inventory'].items()},'native inventory')
write(work/'order-screen.json',d);shutil.copy2(HERE/'evidence/eight-alias-base.json.gz',work/'eight-alias-base.json.gz')
env=dict(os.environ,SOURCE_PARTNER_SEARCH_WORK=str(work))
for name in ['interval_pack.py','realize_pack.py']:subprocess.run([sys.executable,'-B',str(HERE/'search'/name)],env=env,check=True)
print('NOMINATED',work/'eight-fill.json.gz','; run literal reconstruction and complete admission before claiming a result')
