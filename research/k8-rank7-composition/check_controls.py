# SPDX-License-Identifier: Apache-2.0
# Prepared for 1337isnot1337 with substantial OpenAI Codex assistance.
"""Semantic rejection controls using the independent point and owner checks."""
import argparse,copy,gzip,json,os,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));import point_audit as P
ap=argparse.ArgumentParser();ap.add_argument('--replay',type=Path,required=True);a=ap.parse_args();work=a.replay.resolve();root=HERE.parents[1];old=work/'sources/gauge44-slots-t16';newword=json.loads(gzip.decompress((work/'NEW-WORD.json.gz').read_bytes()));rejected=[]
assert __debug__, 'Assertions required'
for name,mutate in [
 ('missing_low_tail',lambda w:w['early_cleanup'].pop(93)),
 ('old_helper_read_frame',lambda w:w['B'][1026].__setitem__(-1,[264,137,96,24,4,3])),
 ('truncated_terminal_space',lambda w:w['helper_final']['574'].pop()),
 ('false_paid_profile',lambda w:w['report']['local_profile'].__setitem__('1',2407)),
 ('false_native_width',lambda w:w['report']['width_inventory'].__setitem__('7',31))]:
 w=copy.deepcopy(newword);mutate(w)
 try:P.recount(w)
 except P.Reject:rejected.append(name)
 else:raise RuntimeError('accepted point control '+name)
with tempfile.TemporaryDirectory(prefix='k8 owner controls ') as td:
 td=Path(td);roles=json.loads(gzip.decompress((HERE/'data/OWNERS.json.gz').read_bytes()));spec=json.load(open(work/'admission/package/data/SPEC.json'));env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',T16_EXPECTED_IDLE=json.dumps(spec['expected']['idle_remainder_profile']),T16_EXPECTED_WIDTHS=json.dumps({'4':56,'5':32,'7':32,'8':120,'9':240}))
 def run(name,rr,word,widths=None):
  pp=td/(name+'.json.gz');pp.write_bytes(gzip.compress(json.dumps(rr).encode(),mtime=0));ee=dict(env)
  if widths:ee['T16_EXPECTED_WIDTHS']=json.dumps(widths)
  c=[sys.executable,'-B',str(old/'t16/indep16.py'),'--baseline-parent',str(work/'baseline/global8/base/split-centres/GLOBAL-TEMPLATE.json.gz'),'--owners',str(pp),'--word',str(word),'--out',str(td/(name+'.receipt.json'))]
  r=subprocess.run(c,env=ee,capture_output=True,text=True)
  if r.returncode==0 or 'ValueError' not in r.stderr:raise RuntimeError('control did not reject semantically: '+name+'\n'+r.stderr)
  rejected.append(name)
 rr=copy.deepcopy(roles);rr[-1]=copy.deepcopy(rr[0]);run('duplicate_helper_role',rr,work/'new-local/CANONICAL-WORD.json.gz')
 rr=copy.deepcopy(roles);rr[0]['width']-=1;run('split_whole_helper',rr,work/'new-local/CANONICAL-WORD.json.gz')
 rr=copy.deepcopy(roles);rr[0]['offset']+=1;run('bad_residual_slice',rr,work/'new-local/CANONICAL-WORD.json.gz')
 run('restore_predecessor_ends',roles,work/'old-native/local/CANONICAL-WORD.json.gz',{'4':56,'5':32,'7':30,'8':122,'9':240})
from fractions import Fraction as Q
sys.path.insert(0,str(root/'research/complex-k492-owner-repair/vendor/multicold/engines'));import outer
asm=json.load(open(work/'admission/strict-ASSEMBLY.json'));aa=Q(asm['bootstrap'][-1]['exponent']);bb=Q(asm['complex_lower']);eta=beta=Q(1,10**24);bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
try:outer.assembly(aa,bb,bridge,Q(asm['kappa'])+Q(1,10**18),eta=eta,beta=beta)
except AssertionError:rejected.append('next_kappa_grid')
else:raise RuntimeError('accepted next grid')
print('PASS_K8_RANK7_SEMANTIC_CONTROLS',len(rejected))
(work/'NEW-CONTROLS.json').write_text(json.dumps({'status':'PASS','rejected':rejected},indent=2)+'\n')
