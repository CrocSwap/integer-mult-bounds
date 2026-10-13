#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Charles Bethin; substantial OpenAI Codex assistance.
"""One command for the proof premises, independent model, and controls."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import controls

p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=False)
here=Path(__file__).resolve().parent
flags=['-O'] if sys.flags.optimize else []
for name,args in [('verify.py',['--out',str(a.out/'CERTIFICATE.json')]),
                  ('independent.py',['--certificate',str(a.out/'CERTIFICATE.json'),'--out',str(a.out/'INDEPENDENT.json')])]:
    subprocess.run([sys.executable,*flags,'-B',str(here/name),*args],check=True)
result=controls.run(json.loads((a.out/'CERTIFICATE.json').read_text()))
(a.out/'CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],f'negative={len(result["rejected"])} positive={len(result["positive"])}')
for name in ('CERTIFICATE.json','INDEPENDENT.json','CONTROLS.json'):
    frozen=here/'data'/name
    if frozen.exists():
        actual=json.dumps(json.loads((a.out/name).read_text()),sort_keys=True)
        expected=json.dumps(json.loads(frozen.read_text()),sort_keys=True)
        if actual!=expected:raise ValueError('committed receipt differs: '+name)
print('PASS_T37_SUPPORT_INTERVAL_REPRODUCTION')
