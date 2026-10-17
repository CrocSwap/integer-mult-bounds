#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), substantial OpenAI Codex assistance.
"""Additional composition controls and unchanged independent bridge recount.

Does not import the composition constructor. Uses exact set subspaces, runs
retained transport/emission, and invokes the shipped bridge's independent
frame/COPY recount. This is not a fresh full native phase admission.
"""
import copy,gzip,hashlib,importlib.util,json,os,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
CASE=HERE.parents[1]
ORIGINAL_BRIDGE=CASE/'global-admission/owners/build_bridge.py'
CODE=CASE.parent/'anticipatory-stage-evidence/interface/pr2269'

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def span(a):
 s={0}
 for v in a:s|={x^v for x in s.copy()}
 return s

def main():
 baseline=read(HERE/'COMPOSITION-CHECK.json');baseline_sha=sha(HERE/'COMPOSITION-CHECK.json')
 spec=importlib.util.spec_from_file_location('unchanged_four_bridge',ORIGINAL_BRIDGE);bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
 result={}
 for tag in ['base','extra']:
  wordpath=HERE/f'COMPOSED-{tag}.json.gz';word=read(wordpath);prior=baseline['providers'][tag]
  assert sha(wordpath)==prior['composed_word_sha256']
  with tempfile.TemporaryDirectory(prefix='composition2435-controls-') as temp:
   td=Path(temp);out=td/'native'
   commands=[[sys.executable,'-B',str(CASE/'transport_lifted.py'),str(wordpath),str(out)],
             [sys.executable,'-B',str(CODE/'bw_emit.py'),str(out)]]
   for command in commands:
    run=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);assert run.returncode==0,run.stdout[-3000:]
   canonical=read(out/'CANONICAL-WORD.json.gz');programs=read(out/'LOCAL-PROGRAMS.json.gz')
   audit=bridge.recount(canonical,programs)
   assert audit['profile']==prior['local_profile']
   from collections import Counter
   assert dict(Counter(audit['widths']))=={int(k):v for k,v in prior['width_inventory'].items()}
   assert len(audit['widths'])==428 and len(canonical['zero_buffers'])==76
   controls=[]
   for label in ['omit_B_frame_adaptation','fake_dimension_three_entrance']:
    mutant=copy.deepcopy(word)
    if label=='omit_B_frame_adaptation':
     edit=next(x for x in prior['frame_edits'] if x['part']=='B');mutant['B'][edit['four_index']][-1]=edit['old']
    else:
     r=str(prior['starts'][0]['original']);frame=mutant['start_extra'][r];extra=next(v for v in range(1,512) if v not in span(frame));mutant['start_extra'][r]=frame+[extra];assert len(span(mutant['start_extra'][r]))==8
    path=td/(label+'.json.gz');path.write_bytes(gzip.compress(json.dumps(mutant,separators=(',',':')).encode(),mtime=0))
    run=subprocess.run([sys.executable,'-B',str(CASE/'transport_lifted.py'),str(path),str(td/label)],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    assert run.returncode!=0 and 'AssertionError' in run.stdout and 'nonmonotone' in run.stdout,run.stdout[-2000:]
    controls.append(dict(label=label,rejection=run.stdout.strip().splitlines()[-1]))
   result[tag]=dict(word_sha256=sha(wordpath),independent_recount=audit,controls=controls,all_literal_program_paid_children_recounted=True,native_columns=652)
 assert sha(HERE/'COMPOSITION-CHECK.json')==baseline_sha,'original receipt changed'
 report=dict(status='PASS_ADDITIONAL_COMPOSITION_CONTROLS_AND_UNCHANGED_BRIDGE_RECOUNT_NO_PHASE_ADMISSION',constructor_receipt_sha256=baseline_sha,original_bridge_sha256=sha(ORIGINAL_BRIDGE),checker_sha256=sha(Path(__file__)),providers=result,scope='All emitted climb/COPY children and endpoint frames independently recounted; omitted B frame and fake entrance dimension rejected for both providers. Full physical phases, global hosting/invoice and outer transfer remain separate.')
 (HERE/'BRIDGE-AND-CONTROLS.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
