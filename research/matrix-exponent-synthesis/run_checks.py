"""Run the delivered Python reference checks and exact certificate replays.

Network/profile certification is a separate, fully specified candidate replay.
"""
from pathlib import Path
from hashlib import sha256
import argparse,datetime,json,subprocess,sys

ROOT=Path(__file__).resolve().parent
def main():
    if sys.flags.optimize:raise SystemExit('Run without -O')
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,default=ROOT/'work')
    ap.add_argument('--include-lean',action='store_true');ap.add_argument('--lake',default='lake')
    args=ap.parse_args();args.work=args.work.resolve();args.work.mkdir(parents=True,exist_ok=True)
    base=ROOT/'openmath-source/personal-matrix-hybrid-2026-10-07'
    circuit=base/'circuit/flat16_2208_integer_circuit.json'
    outer=base/'input/outer48_exact_rational_and_integer_data.json'
    commands=[
        ['audit/independent_matrix_check.py',base,args.work/'matrix.json'],
        ['audit/bilinear_projection.py',base,args.work],
        ['audit/matrix_two_adic_lift.py',base,args.work/'lift.json'],
        ['audit/phase_operator_audit.py',base,args.work/'operators.json'],
        ['audit/phase_child_closure.py',args.work/'closure.json'],
        ['audit/source_ci_audit.py',base,args.work/'historical-source-binding.json'],
        ['verify_gaussian_matrix.py','--circuit',circuit],
        ['verify_hierarchical_gaussian.py','--circuit',circuit,'--outer',outer],
        ['catalogue/audit_catalogue.py',args.work/'catalogue.json'],
        ['catalogue/assignment_certificate.py','--edges','catalogue/inputs/matching/h23-even-edges.txt',
         '--verify','catalogue/fixed-dag-h23-dual-final.json'],
        ['catalogue/all_cardinality_certificate.py','--verify','catalogue/all-cardinality-h25-certificate.json'],
    ]
    results=[]
    for index,command in enumerate(commands):
        with (args.work/f'check-{index:02}.log').open('w',encoding='utf-8') as log:
            run=subprocess.run([sys.executable,*map(str,command)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        if run.returncode:raise SystemExit(f'Failed check {command[0]}; inspect check-{index:02}.log')
        results.append(dict(check=command[0],status='passed'))
    if args.include_lean:
        with (args.work/'lake-build.log').open('w',encoding='utf-8') as log:
            subprocess.run([args.lake,'build'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        results.append(dict(check='lake build',status='passed'))
    receipt=dict(status='passed',verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 checks=results,full_network_replay='Inherited PR58 construction verification; fresh parameter replay is candidate/verify_refinement.py')
    (args.work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
