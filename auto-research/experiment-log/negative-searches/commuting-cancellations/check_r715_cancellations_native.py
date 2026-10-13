from pathlib import Path
import subprocess,os,json,sys,time
r=Path.cwd();out=r/'r715-cancellations-native311';assert not out.exists();out.mkdir();B=r/'source454-review/e8-r740-replica32/parent436/code/bit';word=r/'r715-commuting-cancellations/WORD.json';bins=r/'r715-replica84-complete311/bin';p=r/'pr472-delivery-publication/research/r715-factor-replica84';env=dict(os.environ,PYTHONPATH=os.pathsep.join([str(r/'source454-review/e8-r740-replica32/code'),str(r/'source454-review/idle-axis-hosting')]))
steps=[]
def run(name,cmd):
 with (out/(name+'.log')).open('w') as f:q=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
 assert q.returncode==0,(name,q.returncode);steps.append(name);print('PASS',name,flush=True)
def py(name,path,*args):run(name,[sys.executable,'-B',path,*args])
try:
 py('export',B/'export_records.py',word,out/'records')
 py('labels',p/'code/labels.py',out/'records')
 py('mixing',r/'source454-review/e8-target-mixing-whole/upstream450/mix_check.py',word,out/'records','--controls',p/'data/base.json.gz')
 py('stage',B/'regression/stage_cohort.py',out/'records',out/'records',out/'cin',out/'cout')
 run('legality',[bins/'legality',out/'cin',out/'cout',out/'cout/legality.json'])
 for name,file in [('columns_h','columns.json'),('columns_k5','columns_k5.json')]:run(name,[bins/name,out/'cout/COHORT249-RECORDS.bin',out/'cout'/file])
 py('mutations',p/'code/mutate_records.py',out/'records',out/'cin',out/'cout',bins/'legality',bins/'columns_k5',bins/'legality_ncopy_h')
 py('gram',B/'checkers/gram_frames.py',out/'records','--gram','e8ham','--h',8,'--positive')
 (out/'RECEIPT.json').write_text(json.dumps(dict(status='PASS_CHANGED_CANCELLATION_WORD_NATIVE_CHECKS_GLOBAL_PENDING',steps=steps),indent=2)+'\n')
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
