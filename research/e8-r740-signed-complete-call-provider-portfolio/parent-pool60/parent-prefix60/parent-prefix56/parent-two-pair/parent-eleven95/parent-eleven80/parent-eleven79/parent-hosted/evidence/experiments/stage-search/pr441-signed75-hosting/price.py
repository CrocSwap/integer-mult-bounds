from pathlib import Path
import importlib.util,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[2];engines=ROOT/'experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines';spec=importlib.util.spec_from_file_location('hostmoment',engines/'moment.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
for name,file,key,m in [('bit','GLOBAL.json','profile',64),('complex','HOSTED.json','global_profile',73)]:
 d=P/('hosted'if name=='bit'else'complex-hosted');g=json.loads((d/file).read_text());H={int(k):v for k,v in g[key].items()};cert=M.certify(H,m,g['live'],True);result=dict(status='EXACT_PROFILE_MOMENT_ONLY_REQUIRES_HOSTING_OPERATOR_ADMISSION',lower=cert['lower'],upper=cert['upper'],profile_sha256=hashlib.sha256(json.dumps(H,sort_keys=True).encode()).hexdigest(),parent_receipt_sha256=hashlib.sha256((d/file).read_bytes()).hexdigest());(d/'PRICE.json').write_text(json.dumps(result,indent=2)+'\n');print(name,cert['lower'])
