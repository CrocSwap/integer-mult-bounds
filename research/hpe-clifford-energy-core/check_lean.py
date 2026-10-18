"""Fresh kernel replay, exact axiom inventory and four false-statement controls."""
from pathlib import Path
import argparse,json,re,subprocess,tempfile
HERE=Path(__file__).resolve().parent
EXPECTED={'cg_pair_energy','cg_fixed_energy','perm_energy','phases_energy','cmapped_energy','step_energy','run_energy','column_squared_bound'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def run(lean,path):
    return subprocess.run([str(lean),'-j1',str(path)],capture_output=True,text=True,encoding='utf-8',timeout=90)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True,type=Path);a=ap.parse_args()
    version=subprocess.check_output([str(a.lean),'--version'],text=True).strip()
    need('version 4.34.1,' in version,'Lean4.34.1 required')
    source=(HERE/'Energy.lean').read_text(encoding='utf-8')
    bare=re.sub(r'/-.*?-/','',source,flags=re.S);bare=re.sub(r'--[^\n]*','',bare)
    need(not re.search(r'\b(sorry|admit|axiom|native_decide|implemented_by|unsafe)\b',bare),'forbidden source')
    with tempfile.TemporaryDirectory(prefix='hpe-energy-') as tmp:
        path=Path(tmp)/'Energy.lean';path.write_text(source,encoding='utf-8')
        result=run(a.lean,path);need(result.returncode==0,result.stdout+result.stderr)
        reports=re.findall(r"'HPEEnergy\.([^']+)' depends on axioms: \[([^\]]*)\]",result.stdout)
        need(len(reports)==len(EXPECTED) and {n for n,_ in reports}==EXPECTED,'exact theorem inventory')
        for name,ax in reports:need({v.strip() for v in ax.split(',')}<={'propext','Classical.choice','Quot.sound'},'axioms '+name)
        mutations={
            'pair_factor':('= 4*(norm2 a + norm2 b)','= 2*(norm2 a + norm2 b)'),
            'fixed_factor':('norm2 (cg s a a) = 4*norm2 a','norm2 (cg s a a) = norm2 a'),
            'free_C_stage':('mapped.Perm w → Step 1 v w','mapped.Perm w → Step 0 v w'),
            'zero_column_bound':('z.1*z.1 ≤ (4:Int)^k ∧ z.2*z.2 ≤ (4:Int)^k','z.1*z.1 ≤ 0 ∧ z.2*z.2 ≤ 0')}
        for name,(old,new) in mutations.items():
            need(source.count(old)==1,'mutation target '+name)
            path.write_text(source.replace(old,new),encoding='utf-8');failed=run(a.lean,path)
            need(failed.returncode!=0 and 'error' in failed.stdout,'false theorem accepted '+name)
    print(json.dumps({'status':'PASS_HPE_ENERGY_LEAN','version':version,'theorems':len(EXPECTED),'false_statements_rejected':len(mutations)}))
if __name__=='__main__':main()
