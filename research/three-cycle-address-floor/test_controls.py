#!/usr/bin/env python3
"""Real isolated optimized-CLI corruptions; no new scientific search.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def run():
    cases=('missing_generator','wrong_target','wrong_upper_word','receipt_count','receipt_minimum','receipt_hash')
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='three-cycle-control-') as directory:
            copied=Path(directory)/'package';shutil.copytree(HERE,copied)
            script='verify.py'
            if case=='missing_generator':
                p=copied/script;s=p.read_text();old='if i!=j]\n    words=';new='if i!=j and (i,j)!=(0,1)]\n    words='
                need(s.count(old)==1,'exact alphabet mutation site');p.write_text(s.replace(old,new))
            elif case=='wrong_target':
                p=copied/script;s=p.read_text();old='target=(2,4,1,8)';need(s.count(old)==1,'exact target mutation site');p.write_text(s.replace(old,'target=identity(4)'))
            elif case=='wrong_upper_word':
                script='independent.py';p=copied/script;s=p.read_text();old='(1,2),(2,1),(1,2)];table=IDENTITY';new='(1,2),(2,1),(0,2)];table=IDENTITY'
                need(s.count(old)==1,'exact witness mutation site');p.write_text(s.replace(old,new))
            else:
                p=copied/'RESULT.json';receipt=json.loads(p.read_text())
                if case=='receipt_count':receipt['ball_three']+=1
                elif case=='receipt_minimum':receipt['minimum']=5
                else:receipt['ball_three_sha256']='0'*64
                p.write_text(json.dumps(receipt));script='independent.py'
            result=subprocess.run([sys.executable,'-I','-O','-B',str(copied/script)],cwd=copied,
                                  capture_output=True,text=True,timeout=30)
            need(result.returncode!=0 and 'ValueError:' in result.stderr,'mutation accepted or unrelated failure: '+case)
    print('PASS_THREE_CYCLE_CONTROLS optimized_cli_mutations=6')
if __name__=='__main__':run()
