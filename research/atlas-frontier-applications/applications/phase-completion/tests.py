# SPDX-License-Identifier: Apache-2.0
"""Exact prime-phase fixtures and independent positive/negative checks."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,subprocess,uuid
HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
repair=load('repair');checker=load('check')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,b):
    if p.exists():
        if p.read_bytes()!=b:raise ValueError('existing fixture differs: '+p.name)
        return
    p.parent.mkdir(parents=True,exist_ok=True);lock=p.with_name(p.name+'.lock')
    with lock.open('x') as h:
        h.write('Exclusive phase fixture\n');h.flush()
        with p.open('xb') as o:o.write(b)
    lock.unlink()
def full(p):
    a=2 if p!=2 else 1;b=3 if p!=3 else 2
    return [[(((a*r+1)%p)*((b*c+2)%p)+r*r+4*r+1+3*c*c+2*c+6)%p for c in range(p)] for r in range(p)]
def reject(name,fn,message,controls):
    try:fn()
    except ValueError as e:
        if message not in str(e):raise AssertionError((name,str(e),message))
        controls.append(dict(name=name,reason=str(e)))
    else:raise AssertionError('invalid case accepted: '+name)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,default=HERE/'TEST-REPORT.json');a=ap.parse_args()
    if a.report.exists():raise ValueError('fresh report required')
    scripts=[HERE/n for n in ['repair.py','check.py','tests.py']];pins={p.name:sha(p) for p in scripts}
    work=HERE/'validation'/('run-'+uuid.uuid4().hex[:12]);work.mkdir(parents=True)
    cases=[];fixtures=[];cli=[]
    for p in [2,3,5,7,11,13]:
        matrix=full(p)
        for erased in range(p):
            received=[[v for j,v in enumerate(row) if j!=erased] for row in matrix]
            output,cert=repair.complete(received);result=checker.verify(received,output)
            expected=[(row[erased]-matrix[0][erased])%p for row in matrix]
            assert [row[-1] for row in output]==expected
            assert all(row[:-1]==original for row,original in zip(output,received))
            cases.append(dict(order=p,erased_column=erased,checked_pairs=result['column_pairs']))
            if p==11:
                fi=HERE/'fixtures'/('p11-received-%02d.csv'%erased);fo=HERE/'fixtures'/('p11-completed-%02d.csv'%erased)
                put(fi,repair.encode(received));put(fo,repair.encode(output));fixtures.extend([str(fi.relative_to(HERE)),str(fo.relative_to(HERE))])
                co=work/('completed-%02d.csv'%erased);ce=work/('certificate-%02d.json'%erased)
                run=subprocess.run([sys.executable,'-B',str(HERE/'repair.py'),'--input',str(fi),'--output',str(co),'--certificate',str(ce)],capture_output=True,text=True,check=True)
                assert co.read_bytes()==fo.read_bytes()
                verified=subprocess.run([sys.executable,'-B',str(HERE/'check.py'),'--received',str(fi),'--completed',str(co)],capture_output=True,text=True,check=True)
                rc=json.loads(run.stdout);vc=json.loads(verified.stdout);assert rc['order']==vc['order']==11
                cli.append(dict(erased_column=erased,repair_status=rc['status'],checker_status=vc['status'],input_sha256=sha(fi),output_sha256=sha(co)))
    put(HERE/'fixtures/p11-full.csv',repair.encode(full(11)));fixtures.append('fixtures/p11-full.csv')
    controls=[];matrix=full(5);received=[row[:-1] for row in matrix];good,_=repair.complete(received)
    bad=[row[:] for row in received];bad[0][0]=(bad[0][0]+1)%5
    reject('one_changed_received_phase',lambda:repair.complete(bad),'incoming columns are not orthogonal',controls)
    reject('composite_four_row_input',lambda:repair.complete([[r*c%4 for c in range(3)]for r in range(4)]),'prime row count',controls)
    reject('empty_input',lambda:repair.complete([]),'prime row count',controls)
    reject('order_one_input',lambda:repair.complete([[]]),'prime row count',controls)
    reject('wrong_column_count',lambda:repair.complete([row[:-1] for row in received]),'shape',controls)
    badshape=[row[:] for row in received];badshape[1].pop()
    reject('ragged_input',lambda:repair.complete(badshape),'shape',controls)
    wrongtype=[row[:] for row in received];wrongtype[0][0]=0.5
    reject('noninteger_phase',lambda:repair.complete(wrongtype),'integer phase code',controls)
    reject('floating_CSV_token',lambda:repair.parse(b'0,0.5\n0,1\n'),'integer phase code',controls)
    altered=[row[:] for row in good]
    for row in altered:row[0]=(row[0]+1)%5
    reject('orthogonal_output_with_changed_received_column',lambda:checker.verify(received,altered),'received columns changed',controls)
    duplicate=[row[:] for row in good]
    for i,row in enumerate(duplicate):row[-1]=(received[i][0]-received[0][0])%5
    reject('duplicate_added_ray',lambda:checker.verify(received,duplicate),'full column orthogonality',controls)
    gauge=[row[:] for row in good]
    for row in gauge:row[-1]=(row[-1]+1)%5
    reject('noncanonical_added_column_phase',lambda:checker.verify(received,gauge),'first new phase',controls)
    reject('output_row_missing',lambda:checker.verify(received,good[:-1]),'output shape',controls)
    # Exponent representatives need not be canonical; preserve them literally.
    signed=[[v+5*(i-j-2) for j,v in enumerate(row)]for i,row in enumerate(received)]
    repaired,_=repair.complete(signed);checker.verify(signed,repaired);assert all(row[:-1]==old for row,old in zip(repaired,signed))
    fi=HERE/'fixtures/p11-received-00.csv';before=sha(fi)
    blocked=subprocess.run([sys.executable,'-B',str(HERE/'repair.py'),'--input',str(fi),'--output',str(fi),'--certificate',str(work/'bad.json')],capture_output=True,text=True)
    assert blocked.returncode!=0 and 'distinct input and output' in blocked.stderr and sha(fi)==before
    controls.append(dict(name='CLI_input_overwrite',reason='distinct input and output paths required'))
    assert pins=={p.name:sha(p)for p in scripts}
    result=dict(status='PASS_EXACT_PRIME_PHASE_PILOT_FIXTURES',orders=[2,3,5,7,11,13],positive_erasure_cases=cases,positive_case_count=len(cases),signed_exponent_preservation=True,p11_CLI_erasure_cases=cli,negative_controls=controls,source_sha256=pins,fixtures=sorted(fixtures),independent_checker_imports_repair=False,scope='Exact finite orthogonality and literal received-column preservation; no empirical communication/noise or performance result.')
    put(a.report,(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps(dict(status=result['status'],positive_erasure_cases=len(cases),p11_CLI_cases=len(cli),negative_controls=len(controls),report_sha256=sha(a.report))))
if __name__=='__main__':main()
