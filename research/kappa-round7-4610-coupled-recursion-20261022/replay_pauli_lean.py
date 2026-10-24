"""Fresh Lean compilation and exact axiom receipt for PauliHole only.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    runtime = ROOT/'research/kappa-lean-verification-20261022'
    helper = runtime/'verify_lean.py'
    spec = importlib.util.spec_from_file_location('pauli_hole_lean_auditor',helper)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    lake = runtime/'.toolchain/lean-4.21.0-windows/bin/lake.exe'
    lean,env,versions = audit.environment(str(lake))
    assert sha256(Path(lean).read_bytes()).hexdigest()=='fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab'
    paths=[]
    for entry in env['LEAN_PATH'].split(os.pathsep):
        if entry:
            path=Path(entry)
            paths.append(str(path if path.is_absolute() else (runtime/path).resolve()))
    env['LEAN_PATH']=os.pathsep.join([str(HERE),*paths])
    source=HERE/'PauliHole.lean'
    source_hash=sha256(source.read_bytes()).hexdigest()
    expected=audit.audit_source(source)
    assert len(expected)==2
    obj=HERE/'PauliHole.olean'
    logpath=HERE/'PauliHole.log'
    command=[lean,'--root='+str(HERE),'-o',str(obj),str(source)]
    with logpath.open('wb') as output:
        result=subprocess.run(command,cwd=HERE,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=120)
    assert result.returncode==0,logpath.read_text()
    assert sha256(source.read_bytes()).hexdigest()==source_hash
    axioms=audit.parse_axioms(logpath,expected)
    receipt=dict(status='PASS_LEAN_PAULI_HOLE_COEFFICIENT_OBSTRUCTION',source=source.name,
                 source_sha256=source_hash,object_sha256=sha256(obj.read_bytes()).hexdigest(),
                 log=logpath.name,log_sha256=sha256(logpath.read_bytes()).hexdigest(),
                 output=logpath.read_text(),exit_code=result.returncode,axioms=axioms,
                 expected_reports=expected,allowed_axioms=sorted(audit.ALLOW),runtime=versions,
                 auditor_sha256=sha256(helper.read_bytes()).hexdigest(),
                 script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                 scope='Two incompatible binary coefficients and arbitrary complex Pauli-sector amplitudes. Python separately binds those coefficients to actual ports/routes. No native word, all-f physical tape theorem or recursive supplier theorem is formalized.')
    (HERE/'LEAN-PAULI-HOLE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(receipt['status'],len(expected),'reports')


if __name__=='__main__':main()
