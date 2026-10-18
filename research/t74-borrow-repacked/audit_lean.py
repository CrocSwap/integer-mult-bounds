"""Fresh standalone nine-theorem kernel and transitive-axiom audit.
Run inside a compatible Mathlib checkout: lake env python /path/to/audit_lean.py --out /unused/external/audit
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,time
HERE=Path(__file__).resolve().parent
def need(ok,msg):
    if not ok:raise ValueError(msg)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--lean',default='lean');a=ap.parse_args()
    need(not a.out.resolve().is_relative_to(HERE),'external audit directory required');a.out.mkdir(parents=True,exist_ok=False)
    source=HERE/'ProfileGain.lean';raw=source.read_bytes();expected=json.loads((HERE/'PROFILE-GAIN-AUDIT.json').read_bytes());names=list(expected['theorems'])
    need(hashlib.sha256(raw).hexdigest()==expected['source_sha256'],'proof source differs');need(len(names)==9 and all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*',n)for n in names),'nine ordinary names required')
    suffix='''
open Lean Elab Command in
run_cmd do
  let targets : Array Lean.Name := #[TARGETS]
  let mut rows : Array Lean.Json := #[]
  for target in targets do
    let info ← Lean.getConstInfo target
    match info with
    | .thmInfo _ => pure ()
    | _ => throwError "Expected theorem: {target}"
    let axs ← Lean.collectAxioms target
    rows := rows.push (Lean.Json.mkObj [("name", Lean.toJson target.toString),
      ("axioms", Lean.toJson (axs.map Lean.Name.toString))])
  IO.FS.writeFile OUTPUT (Lean.Json.arr rows).compress
'''.replace('TARGETS',', '.join('`'+n for n in names)).replace('OUTPUT',json.dumps((a.out.resolve()/'axioms.json').as_posix()))
    driver=a.out.resolve()/'Audit.lean';driver.write_text('import Lean\n'+raw.decode('utf-8').replace('\r\n','\n')+'\n'+suffix,encoding='utf-8')
    start=time.monotonic()
    with (a.out/'lean.log').open('wb')as log:proc=subprocess.run([a.lean,str(driver)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    need(proc.returncode==0,'Lean rejected source; inspect external lean.log');actual=json.loads((a.out/'axioms.json').read_bytes());allowed={'propext','Classical.choice','Quot.sound'}
    need([r['name']for r in actual]==names and all(set(r['axioms'])<=allowed for r in actual),'unexpected name or axiom')
    need(source.read_bytes()==raw,'source changed during audit')
    result=dict(status='PASS_FRESH_STANDALONE_NINE_THEOREM_KERNEL_AND_AXIOM_AUDIT',source_sha256=hashlib.sha256(raw).hexdigest(),exports=actual,allowed_axioms=sorted(allowed),seconds=round(time.monotonic()-start,3))
    (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
if __name__=='__main__':main()
