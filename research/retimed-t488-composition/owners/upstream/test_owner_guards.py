# SPDX-License-Identifier: Apache-2.0
import pathlib,json,copy,subprocess,sys,tempfile,shutil,importlib.util
P=pathlib.Path(__file__).resolve().parent
def need(x,m):
 if not x:raise ValueError(m)
def main():
 count=0
 with tempfile.TemporaryDirectory()as t:
  d=pathlib.Path(t);out=d/'must-not-exist'
  for name in ('verify_owner.py','verify_candidate.py','portable_expand.py','independent_literal.py','integral_network.py','source_context.py'):
   r=subprocess.run([sys.executable,'-I','-O','-B',str(P/name),'--out',str(out)],capture_output=True,text=True)
   need(r.returncode and 'Enabled assertions required'in r.stderr and not out.exists(),'optimized gate '+name);count+=1
  q=d/'corrupt';shutil.copytree(P,q);(q/'CANDIDATE.json').write_bytes((q/'CANDIDATE.json').read_bytes()+b'x')
  r=subprocess.run([sys.executable,'-I','-B',str(q/'verify_owner.py')],capture_output=True,text=True);need(r.returncode and 'frozen owner artifact'in r.stderr,'certificate corruption');count+=1
 spec=importlib.util.spec_from_file_location('check_controls',P/'verify_candidate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);x=json.loads((P/'CANDIDATE.json').read_text());v.check(x,'concatenated')
 for field,value in [('order',x['order'][::-1]),('groups',[]),('inventory',{}),('profile',{}),('local_profile',{}),('dispatch',[]),('baseT',53)]:
  d=copy.deepcopy(x);d[field]=value
  try:v.check(d,'concatenated')
  except ValueError:count+=1
  else:raise ValueError('accepted semantic corruption '+field)
 print('PASS_OWNER_GUARDS',count)
if __name__=='__main__':main()
