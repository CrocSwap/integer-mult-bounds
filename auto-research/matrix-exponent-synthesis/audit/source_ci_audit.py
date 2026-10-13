import sys as _checked_runtime
if _checked_runtime.flags.optimize:
    raise SystemExit('Checked audit requires Python without -O')
from pathlib import Path
import json,hashlib,re,sys
base=Path(sys.argv[1]);dest=Path(sys.argv[2])
m=json.loads((base/'lean/final_source_manifest.json').read_text());ci=json.loads((base/'evidence/github_ci/37675264184/actual_reproduction.json').read_text())
source_checks=[]
for item in m['sources_in_build_order']:
 raw=(base/'lean'/item['file']).read_bytes();h=hashlib.sha256(raw).hexdigest()
 assert h==item['sha256'],item['module']
 c=next(s for s in ci['sources'] if s['module']==item['module']);assert c['source_sha256']==h and c['exit_code']==0
 source_checks.append(item['module'])
assert len(source_checks)==11
allowed={'propext','Classical.choice','Quot.sound'}
assert len(ci['selected_axioms'])==45
assert all(set(ax)<=allowed for ax in ci['selected_axioms'].values())
js=json.loads((base/'input/outer48_exact_rational_and_integer_data.json').read_text())['minimal_integer_certificate']
src=(base/'lean/Outer48Data.lean').read_text()
for name,jkey in [('alphaInteger','alpha_integer'),('betaInteger','beta_integer'),('gammaNumerator','gamma_numerator')]:
 segment=src.split('def '+name+' :',1)[1].split('\ndef ',1)[0]
 rows=[[int(x) for x in row.split(',')] for row in re.findall(r'!\[([\d,\s-]+)\]',segment)]
 assert rows==js[jkey],name
result={'status':'PASS','source_pin':'7203497dc990e47c2391bff1b9863408d817faeb','all11_local_sources_match_final_manifest_and_CI_receipt':source_checks,'recorded_standard_axiom_selected_endpoints':45,'all3_Lean_outer48_tables_match_freshly_checked_JSON':True,'recorded_toolchain':(base/'lean/lean-toolchain').read_text().strip(),'fresh_local_full_Lean_compile':False,'qualification':'Source/hash binding and exact outer coefficient identity freshly checked; recorded CI kernel compilation is historical evidence, not rerun locally. New Std quotient modules are separately freshly compiled on4.31.'}
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
