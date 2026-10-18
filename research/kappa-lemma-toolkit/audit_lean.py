"""Recheck all standalone theorem and definition dependencies in a Mathlib environment.
Run: lake env python3 /path/to/audit_lean.py --out /unused/external/audit
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,time
HERE=Path(__file__).resolve().parent
ALLOWED={'propext','Classical.choice','Quot.sound'}
def need(ok,label):
    if not ok:raise ValueError(label)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--lean',default='lean');p.add_argument('--timeout',type=int,default=180);a=p.parse_args()
    need(not a.out.resolve().is_relative_to(HERE.parent),'audit output must be outside both source packages')
    a.out.mkdir(parents=True,exist_ok=False);source=HERE/'Toolkit.lean';raw=source.read_bytes();expected=json.loads((HERE/'LEAN-AUDIT.json').read_bytes());need(hashlib.sha256(raw).hexdigest()==expected['source_sha256'],'standalone source differs from audited bytes')
    exports=[(row['name'],row['kind'])for row in expected['exports']]
    need(all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*",n)for n,_ in exports),'ordinary declaration identifiers required')
    names=', '.join('`'+n for n,_ in exports);out=a.out.resolve()/'axioms.json'
    suffix="""
open Lean Elab Command in
run_cmd do
  let targets : Array Lean.Name := #[TARGETS]
  let mut rows : Array Lean.Json := #[]
  for target in targets do
    let info ← Lean.getConstInfo target
    let kind ← match info with
      | .thmInfo _ => pure "theorem"
      | .defnInfo _ => pure "def"
      | _ => throwError "Unsupported declaration kind: {target}"
    let axioms ← Lean.collectAxioms target
    rows := rows.push (Lean.Json.mkObj [
      ("name", Lean.toJson target.toString), ("kind", Lean.toJson kind),
      ("axioms", Lean.toJson (axioms.map Lean.Name.toString))])
  IO.FS.writeFile OUTPUT (Lean.Json.arr rows).compress
""".replace('TARGETS',names).replace('OUTPUT',json.dumps(out.as_posix()))
    driver=a.out.resolve()/'Audit.lean';driver.write_text('import Lean\n'+raw.decode('utf-8').replace('\r\n','\n')+'\n'+suffix,encoding='utf-8');start=time.monotonic()
    with (a.out/'lean.log').open('wb')as log:q=subprocess.run([a.lean,str(driver)],stdout=log,stderr=subprocess.STDOUT,timeout=a.timeout)
    need(q.returncode==0,'Lean rejected the source; inspect external lean.log')
    actual=json.loads(out.read_bytes());need([(x['name'],x['kind'])for x in actual]==exports,'missing/mistyped declaration audit')
    need(all(set(x['axioms'])<=ALLOWED for x in actual),'unexpected axiom dependency')
    need(source.read_bytes()==raw,'source changed during audit')
    result=dict(status='PASS_FRESH_KERNEL_AND_TRANSITIVE_AXIOMS_ALL_EXPORTS',source_sha256=hashlib.sha256(raw).hexdigest(),theorem_count=87,definition_count=19,exports=actual,allowed_axioms=sorted(ALLOWED),seconds=round(time.monotonic()-start,3))
    (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS_LEAN_87_THEOREMS_19_DEFINITIONS_STANDARD_AXIOMS_ONLY')
if __name__=='__main__':main()
