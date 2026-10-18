"""Fresh Lean4.34.1 compilation, live axiom audit and false-statement controls."""
import argparse,json,os,re,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from verify import authenticate,require


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True,type=Path);args=ap.parse_args()
    authenticate()
    lean=args.lean.resolve()
    version=subprocess.check_output([str(lean),'--version'],text=True).strip()
    require('version 4.34.1,' in version,'Lean4.34.1 required')
    formal=json.loads((HERE/'FORMAL.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='packed-radix-kernel-') as tmp:
        tmp=Path(tmp);env=os.environ.copy();env['LEAN_PATH']=str(tmp)
        def run(path,output=None):
            argv=[str(lean),'-j1']+(['-o',str(output)] if output else [])+[str(path)]
            return subprocess.run(argv,cwd=tmp,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
        energy=tmp/'Energy.lean';energy.write_bytes((HERE/'vendor/Energy.lean').read_bytes())
        compiled=run(energy,tmp/'Energy.olean');require(compiled.returncode==0,compiled.stdout+compiled.stderr)
        path=tmp/'PackedRadix.lean';path.write_bytes((HERE/'PackedRadix.lean').read_bytes())
        compiled=run(path,tmp/'PackedRadix.olean');require(compiled.returncode==0,compiled.stdout+compiled.stderr)
        reports=re.findall(r"'Packed\.([^']+)' depends on axioms: \[([^\]]*)\]",compiled.stdout)
        require(len(reports)==len(formal['theorems']) and {x for x,_ in reports}==set(formal['theorems']),'live theorem inventory')
        for name,axioms in reports:
            require({a.strip() for a in axioms.split(',')}<=set(formal['allowed_axioms']),'unexpected axioms: '+name)
        test=tmp/'Control.lean'
        positive='import PackedRadix\nopen Packed\nexample : pack 4 [3,-1] = -1 := by decide\nexample : scale 1 (4,0) = scale 4 (1,0) := by decide\n'
        test.write_text(positive,encoding='utf-8',newline='\n')
        ok=run(test);require(ok.returncode==0,ok.stdout+ok.stderr)
        statements={
            'nonstrict_digit_bound':'example : pack 4 [4,-1] ≠ 0 := by decide',
            'omit_imaginary_component':'example : packGaussian 4 [(0,1)] = packGaussian 4 [(0,-1)] := by decide',
            'omit_relative_C_scale':'example : scale 1 (4,0) = scale 1 (1,0) := by decide',
            'drop_final_column':'example : pack 4 [0,1] = pack 4 [0] := by decide'}
        for name,statement in statements.items():
            test.write_text('import PackedRadix\nopen Packed\n'+statement+'\n',encoding='utf-8',newline='\n')
            failed=run(test);require(failed.returncode!=0 and 'error' in failed.stdout,'false statement accepted: '+name)
    print(json.dumps({'status':'PASS_HPE_PACKED_RADIX_LEAN','version':version,'theorems':len(reports),
                      'axioms':{n:[a.strip() for a in ax.split(',')] for n,ax in reports},
                      'false_statements_rejected':list(statements),'fresh_energy_import':True},sort_keys=True))


if __name__=='__main__':main()
