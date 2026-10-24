"""Self-contained finite/input/Lean-log checker for the recursive query gate.
intqwq; substantial OpenAI Codex assistance. Apache-2.0.
No toolchain installation is required for the source/log and finite checks.
"""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()


def rank(matrix):
    a=[list(map(Q,row)) for row in matrix]
    if not a:return 0
    k=0
    for j in range(len(a[0])):
        pivot=next((i for i in range(k,len(a)) if a[i][j]),None)
        if pivot is None:continue
        a[k],a[pivot]=a[pivot],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
        for i in range(len(a)):
            if i!=k:
                v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
        k+=1
    return k


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--require-object',action='store_true')
    args=parser.parse_args()
    need(sys.version_info>=(3,12),'Python 3.12 or later')
    sources=json.loads((HERE/'SOURCE-MANIFEST.json').read_text())
    for row in sources['files']:
        need(digest(HERE/row['copy'])==row['sha256'],'Pinned input '+row['copy'])
    run=subprocess.run([sys.executable,'-I','-B',str(HERE/'star_relations.py')],
                       stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False,cwd=HERE)
    need(run.returncode==0,run.stdout.decode(errors='replace'))
    packet=json.loads(gzip.decompress((HERE/'inputs/sources/certificate.json.gz').read_bytes()))
    phases=json.loads((HERE/'inputs/sources/DATA-PHASES.json').read_bytes())
    R=[{int(k):Q(x) for k,x in row.items()} for row in packet['R_rows']]
    selected=[0,7,20,27,36,46,57,111]
    c,r=120,8
    U=[[-R[k].get(p,0)/2 for k in range(r)] for p in range(112)]
    U += [[Q(12*int(i==j)) for j in range(r)] for i in range(r)]
    V=[[R[k].get(p,0)/2 for p in range(112)]+[Q(int(k==j)) for j in range(r)] for k in range(r)]
    need(all(sum(V[i][p]*U[p][j] for p in range(c))==-2*int(i==j)
             for i in range(r) for j in range(r)),'All 64 literal VU entries')
    owners=list(range(112))+selected
    groups=defaultdict(list)
    for p,owner in enumerate(owners):groups[phases['recipes'][owner]['q']].append(p)
    row_counts=[rank([[V[k][p] for p in ps] for k in range(r)]) for ps in groups.values()]
    col_counts=[rank([U[p] for p in ps]) for ps in groups.values()]
    need(len(groups)==112 and sum(row_counts)==sum(col_counts)==120,'Direct per-direction query factorization')
    # Rank8 output does not license an eight-head invoice in this actual
    # direct implementation. This is not a lower bound on new algorithms.
    need(sum(row_counts)!=8 and sum(col_counts)!=8,'False eight-head direct invoice rejected')
    receipt=json.loads((HERE/'LEAN-VERIFICATION.json').read_text())
    need(receipt['author']=='intqwq' and receipt['new_kappa'] is False,'Authorship/scope')
    for key,path in [('source_sha256','QueryProducer.lean'),('log_sha256','QueryProducer.log'),
                     ('replay_sha256','replay_lean.py')]:
        need(digest(HERE/path)==receipt[key],'Lean receipt '+path)
    helper=HERE/'inputs/verify_lean.py'
    need(digest(helper)==receipt['auditor_sha256'],'Lean auditor binding')
    spec=importlib.util.spec_from_file_location('round8_source_log_auditor',helper)
    audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    expected=audit.audit_source(HERE/'QueryProducer.lean')
    reports=audit.parse_axioms(HERE/'QueryProducer.log',expected)
    need(len(reports)==5 and reports==receipt['actual_reports'],'Actual five axiom reports')
    need(sorted(audit.ALLOW)==receipt['allowed_axioms'],'Allowed axioms')
    for path,pin in receipt['runtime_configurations_sha256'].items():
        need(digest(HERE/'lean-runtime'/path)==pin,'Runtime configuration '+path)
    obj=HERE/'QueryProducer.olean'
    if args.require_object:need(obj.is_file(),'Fresh local object is required')
    if obj.exists():need(digest(obj)==receipt['object_sha256'],'Local compiled object hash')
    result=dict(status='PASS_SCOPED_RECURSIVE_QUERY_ADMISSION_GATE',author='intqwq',new_kappa=False,
                input_manifest_sha256=digest(HERE/'SOURCE-MANIFEST.json'),script_sha256=digest(__file__),
                lean_receipt_sha256=digest(HERE/'LEAN-VERIFICATION.json'),actual_lean_reports=5,
                star_stdout_sha256=sha256(run.stdout).hexdigest(),literal_VU_entries=64,
                source_fields=c,query_rows=r,distinct_query_directions=len(groups),
                direct_row_heads=sum(row_counts),direct_column_heads=sum(col_counts),
                four_shear_direct_heads=2*sum(row_counts)+2*sum(col_counts),
                shared_pre_post_query_heads=2*c,
                normalized_split_recurrence='p(f)<=p(a)+2*c*g(b)+movement, f=a+b, c=120; likewise column jobs',
                admission='NO_EIGHT_ROW_GAUSSIAN_PRICE_ADMITTED',
                scope='Exact new all-input producer/split algebra and new scalar TL counterexamples. '
                      'Direct-factorization ranks are an invoice, not a universal algorithmic lower bound.')
    path=HERE/'RESULT.json'
    if args.write:
        result['authoring_python_version']=sys.version
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:
        previous=json.loads(path.read_text());previous.pop('authoring_python_version',None)
        need(result==previous,'Committed recursive gate result')
    print(result['status'],'5 Lean reports; row/column heads120/120; no new kappa',flush=True)


if __name__=='__main__':main()
