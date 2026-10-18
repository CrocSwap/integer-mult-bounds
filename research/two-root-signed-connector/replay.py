#!/usr/bin/env python3
"""Portable local replay; Apache-2.0; substantial OpenAI Codex assistance."""
import argparse,hashlib,json,pathlib,shutil,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);args=p.parse_args()
 pins=json.loads((HERE/'SOURCES.json').read_text())
 for rel,h in pins['local_sources'].items():
  if hashlib.sha256((HERE/'inputs'/rel).read_bytes()).hexdigest()!=h:raise ValueError('changed source '+rel)
 if hashlib.sha256((HERE/'PR1526-README.md').read_bytes()).hexdigest()!=pins['pr1526_readme_sha256']:raise ValueError('changed PR1526 source')
 args.out.mkdir(parents=True,exist_ok=False)
 for name in ['two_root_verify.py','two_root_invoice.py','two_root_expanded.py','two_root_head_formula.py','two_root_machine.py']:shutil.copy2(HERE/name,args.out/name)
 for name,extra in [('two_root_verify.py',['--out',str(args.out/'short.json')]),('two_root_invoice.py',[]),('two_root_expanded.py',[]),('two_root_head_formula.py',[]),('two_root_machine.py',[])]:
  result=subprocess.run([sys.executable,'-I','-O','-B',str(args.out/name),*extra],capture_output=True,text=True,timeout=45)
  (args.out/(name+'.log')).write_text(result.stdout+result.stderr)
  if result.returncode:raise RuntimeError(name+': '+result.stderr)
 r=json.loads((args.out/'short.json').read_text());q=json.loads((args.out/'two_root_expanded.json').read_text());h=json.loads((args.out/'two_root_head_formula.json').read_text())
 if r['complete_child_queries']!=12 or r['root_passes']!=6 or q['checks']['two_root12']['factor_calls']!=300 or h['delta_against_compact13']!=[0,476,12,148,-8]:raise ValueError('receipt mismatch')
 m=json.loads((args.out/'two_root_machine.json').read_text())
 if m['fixtures']!=36 or len(r['controls'])+len(q['omission_controls'])+len(m['controls'])!=28:raise ValueError('coverage mismatch')
 for name in ['short.json','two_root_invoice.json','two_root_expanded.json','two_root_head_formula.json','two_root_machine.json']:
  actual=json.loads((args.out/name).read_text());expected=json.loads((HERE/'expected'/name).read_text())
  for record in [actual,expected]:
   for field in ['sys_version','sys_executable']:record.pop(field,None)
  if actual!=expected:raise ValueError('semantic receipt mismatch '+name)
 print('PASS_TWO_ROOT_LOCAL_REPLAY queries=12 roots=2 root_passes=6 factor_calls=300 controls=28 machine_fixtures=36; no supplier admission')
if __name__=='__main__':main()
