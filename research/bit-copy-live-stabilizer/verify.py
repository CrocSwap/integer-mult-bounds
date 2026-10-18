"""Live COPY stabilizer and endpoint-only counterexamples. Apache-2.0."""
import gzip,hashlib,itertools,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
def need(x,m):
    if not x: raise ValueError(m)
def rank(rows):
    b={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k in b: x^=b[k]
            else: b[k]=x;break
    return len(b)
def execute(ops,n,strict=True):
    x=[1<<i for i in range(n)]+[0]
    for op,d,s in ops:
        if op=='add': x[d]^=x[s]
        elif op=='copy': need(x[d]==0,'dirty copy');x[d]=x[s]
        else:
            if strict: need(x[d]==x[s],'stale copy at ERASE')
            x[d]=0
    return x
def run():
    for p in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if p['usage']=='input':need(hashlib.sha256((ROOT/p['path']).read_bytes()).hexdigest()==p['sha256'],'pin '+p['path'])
    matrices=safe=assignments=0;row_counts={}
    for rows in itertools.product(range(1,16),repeat=4):
        if rank(rows)!=4:continue
        matrices+=1; criterion=rows[0]==1
        brute=all((rows[0]&x).bit_count()%2==(x&1) for x in range(16));assignments+=16
        need(criterion==brute,'stabilizer versus exhaustive dirty values')
        safe+=criterion;row_counts[rows[0]]=row_counts.get(rows[0],0)+1
    need(matrices==20160 and safe==1344 and set(row_counts.values())=={1344},'GL4 orbit count')
    w=json.loads(gzip.decompress((ROOT/'research/r439-bsection-stars-seed01/candidate.json.gz').read_bytes()))
    n=2*w['v']+w['R'];ops=[('add',d,s) for sec in ('D','A') for f,d,ss in w[sec] for s in ss]
    intervals=[]
    for j,c in enumerate(w['ret']):
        start=len(ops);ops.append(('copy',n,c));ops.extend(('add',w['v']+t,n) for t,ss in enumerate(w['scatter']) if j in ss)
        end=len(ops);ops.append(('erase',n,c));intervals.append((start,end,c))
    ops.extend(('add',d,s) for sec in ('B','C') for f,d,ss in w[sec] for s in ss)
    baseline=execute(ops,n);want=[(1<<i) ^ ((1<<(i-w['v'])) if w['v']<=i<2*w['v'] else 0) for i in range(n)]+[0]
    need(baseline==want,'original complete boundary')
    cases=[]
    for j,(start,end,c) in enumerate(intervals):
        donor=w['ret'][(j+1)%9]
        bad=ops[:start+1]+[('add',c,donor)]+ops[start+1:end+1]+[('add',c,donor)]+ops[end+1:]
        need(execute(bad,n,False)==baseline,'endpoint-only mutation must pass')
        try: execute(bad,n)
        except ValueError as e:need(str(e)=='stale copy at ERASE','precise rejection')
        else:raise ValueError('unsafe live copy accepted')
        good=ops[:start+1]+[('add',donor,c)]+ops[start+1:end+1]+[('add',donor,c)]+ops[end+1:]
        need(execute(good,n)==baseline,'safe center-fixed control')
        early=ops[:start+1]+[('add',c,donor)]+ops[start+1:end]+[('add',c,donor)]+ops[end:]
        need(execute(early,n)==baseline,'restore-before-ERASE repair')
        cases.append({'copy_index':j,'center':c,'donor':donor,'endpoint_only_pass':True,'strict_rejected':True,'safe_control':True,'early_restore':True})
    return {'status':'PASS_LIVE_COPY_STABILIZER','GL4':matrices,'safe':safe,'unsafe':matrices-safe,'dirty_assignments':assignments,'rows_per_orbit':row_counts,'columns':n,'production_intervals':cases,'unchanged_ADDs':sum(op=='add' for op,_,_ in ops),'added_ADDs_per_countercontrol':2,'copies':9,'erasures':9,'new_kappa':False}
if __name__=='__main__':
    x=json.loads(json.dumps(run()));p=HERE/'CERTIFICATE.json'
    if '--write' in sys.argv:p.write_text(json.dumps(x,indent=2)+'\n')
    else:need(x==json.loads(p.read_text()),'receipt')
    print(x['status'],'GL4=20160 safe=1344 dirty=322560 actual_intervals=9 counterexamples=9')
