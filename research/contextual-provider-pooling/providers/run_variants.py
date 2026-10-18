"""Reconstruct selected local providers and replay every changed physical program."""
from pathlib import Path
import argparse,json,subprocess,sys
if not __debug__:raise RuntimeError('Assertions required')
p=Path(__file__).resolve().parent;root=p.parent;v=root/'complex-global/vendor531';g=root/'complex-local/static44/gk';launch=root/'complex-local/code/run_portable.py'
a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a=a.parse_args();old=a.source.resolve();out=a.out.resolve();assert not out.exists();out.mkdir(parents=True)
def run(script,*args):subprocess.run([sys.executable,'-B',str(launch),str(script),*map(str,args)],check=True)
run(p/'build_providers.py','--input',old/'epoch/FULL-WORD.json.gz','--gk-dir',g,'--out',out/'raw','--audit')
locations={'n0':str(old/'local')}
for k in [2,6,8]:
 local=out/f'n{k}/local';base=old/'local'
 run(v/'code/audit_and_transport.py','--raw',out/f'raw/p{k}/FULL-WORD.json.gz','--routing',base/'CANONICAL-WORD.json.gz','--out',local)
 run(v/'code/phases_delta.py','--local',local,'--baseline',base,'--compiler',v/'vendor/clifford')
 run(v/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
 run(v/'code/emit_local.py',local);run(v/'code/audit_local.py',local)
 locations[f'n{k}']=str(local)
(out/'PROVIDERS.json').write_text(json.dumps(locations,indent=2)+'\n',encoding='utf8',newline='\n')
print('PASS selected provider source, omitted-pivot, phase and full-column audits')
