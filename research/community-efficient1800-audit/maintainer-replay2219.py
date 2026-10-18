from pathlib import Path
import json,os,subprocess,sys
root=Path(__file__).resolve().parent
pkg=root/'research/p104-private-descent-reuse-seed915fa969'
kind=sys.argv[1]
commands={'scalar':('research/p104-interleaved-search/fanout.py','FANOUT-RESULT.json'),'cost':('research/p104-private-descent-reuse-seed915fa969/price_reuse.py','COST-RESULT.json'),'native':('research/p104-private-descent-reuse-seed915fa969/verify_native.py','NATIVE-RESULT.json')}
script,receipt=commands[kind]
env=os.environ.copy();env['P104_REPLAY_ROOT']=str(root)
raw=subprocess.check_output([sys.executable,'-I','-B',str(root/script)],cwd=root,env=env,text=True)
actual=json.loads(raw);expected=json.loads((pkg/receipt).read_text())
if actual!=expected:raise ValueError('Complete receipt mismatch: '+kind)
print(raw,flush=True)
print('PASS_PR2219_COMPLETE_RECEIPT',kind,flush=True)
