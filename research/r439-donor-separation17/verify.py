"""Two-coordinate certificates for known R439 single-write exclusions."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
WORD='research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
REQUIRED={WORD,'research/r439-bsection-survey/README.md',
          'research/r439-bsection-survey/search.py','research/r439-bsection-survey/CANDIDATES.json',
          'research/r439-bsection-survey/CERTIFICATE.json'}
BLOCKS=((509,283,314),(521,314,361))


def need(ok,message):
    if not ok:raise ValueError(message)


def canon(x):
    return json.dumps(json.loads(json.dumps(x)),sort_keys=True,separators=(',',':'),allow_nan=False)


def sha(path):
    data=path.read_bytes()
    if path.suffix!='.gz':data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()


def sources():
    pins=json.loads((P/'SOURCES.json').read_text())
    need(set(pins['files'])==REQUIRED,'source inventory')
    need(pins['base_commit']=='abdc6a7002abdbcd9e21bfc5e1a795784deacfdf','base')
    for name,h in pins['files'].items():need(sha(ROOT/name)==h,'source hash: '+name)
    need(sha(P/'BASE-SELECTED.json')==pins['selected_snapshot_sha256'],'selected snapshot')
    return json.loads(gzip.decompress((ROOT/WORD).read_bytes()))


def block(word,frame,lo,hi):
    ops=word['B'][lo:hi]
    need(len(ops)==hi-lo and all(f==frame and len(ss)==1 and t!=ss[0] for f,t,ss in ops),'block structure')
    regs=sorted({t for f,t,ss in ops}|{s for f,t,ss in ops for s in ss})
    index={r:i for i,r in enumerate(regs)};n=len(regs)
    matrix=[[int(i==j) for j in range(n)] for i in range(n)]
    for f,t,ss in ops:
        d,s=index[t],index[ss[0]]
        matrix[d]=[a+b for a,b in zip(matrix[d],matrix[s])]
    return regs,matrix


def choices(matrix,dst):
    n=len(matrix);goal=[matrix[dst][j]-int(j==dst) for j in range(n)]
    need(min(goal)>=0,'nonnegative goal')
    donors=[]
    for j in range(n):
        if j==dst:continue
        options=[]
        for kind,v in [('entry',[int(k==j) for k in range(n)]),('final',matrix[j])]:
            fits=all(a<=b for a,b in zip(v,goal))
            options.append(dict(kind=kind,row=v,fits=fits))
        donors.append(dict(donor=j,options=options))
    return goal,donors


def inequality(goal,donors,weights):
    need(len(weights)==len(goal) and all(type(w) is int for w in weights),'integer functional')
    demand=sum(a*b for a,b in zip(goal,weights))
    contributions=[]
    for donor in donors:
        values=[sum(a*b for a,b in zip(option['row'],weights))
                for option in donor['options'] if option['fits']]
        contributions.append(max([0]+values))
    return dict(weights=weights,demand=demand,supply=sum(contributions),donor_caps=contributions)


def all_functionals(n):
    for size in (1,2):
        for support in itertools.combinations(range(n),size):
            for signs in itertools.product((-1,1),repeat=size):
                weights=[0]*n
                for j,s in zip(support,signs):weights[j]=s
                yield weights


def run():
    word=sources();results=[];controls=[]
    previous=json.loads((ROOT/'research/r439-bsection-survey/CANDIDATES.json').read_text())
    for frame,lo,hi in BLOCKS:
        regs,matrix=block(word,frame,lo,hi);rows=[];n=len(regs)
        record=next(x for x in previous['blocks'] if x['frame']==frame)
        need(record['class_covered'] is False and record['supply_witness'] is None,'predecessor scope')
        need(regs==record['registers'],'source registers')
        need(hashlib.sha256(canon(matrix).encode()).hexdigest()==record['forward_sha256'],'source integer map')
        for dst in range(n):
            goal,donors=choices(matrix,dst)
            old=[sum(option['row'][k] for d in donors for option in d['options'] if option['fits']) for k in range(n)]
            need(all(a<=b for a,b in zip(goal,old)),'old coordinate test unexpectedly excludes row')
            matches=[];count=0
            for weights in all_functionals(n):
                result=inequality(goal,donors,weights);count+=1
                if result['demand']>result['supply']:matches.append(result)
            rows.append(dict(destination=dst,wire=regs[dst],goal=goal,donors=donors,
                             old_coordinate_supply=old,functionals_tested=count,
                             separating_functionals=len(matches),witness=matches[0] if matches else None))
        results.append(dict(frame=frame,slice=[lo,hi],registers=regs,matrix=matrix,rows=rows))
    witness_rows=[(b['frame'],r['wire']) for b in results for r in b['rows'] if r['witness']]
    need(witness_rows==[(509,468),(521,32),(521,34),(521,107)],'four separated rows')
    def reject(name,fn):
        try:fn()
        except ValueError:controls.append(name)
        else:raise ValueError('accepted mutation: '+name)
    a=results[0]['rows'][-1];w=a['witness']
    reject('dual_sign_reversed',lambda: need(inequality(a['goal'],a['donors'],[-x for x in w['weights']])['demand']>inequality(a['goal'],a['donors'],[-x for x in w['weights']])['supply'],'not separating'))
    reject('allow_both_donor_versions',lambda: need(w['demand']>a['old_coordinate_supply'][2],'exclusive donor requirement'))
    b=results[1]['rows'][2]
    wrong=[0]*len(b['goal']);wrong[5]=1
    v=inequality(b['goal'],b['donors'],wrong)
    reject('omit_negative_coordinate',lambda:need(v['demand']>v['supply'],'two-coordinate requirement'))
    reject('equal_is_not_strict',lambda:need(w['supply']>w['supply'],'strict inequality'))
    reject('float_weight',lambda:inequality(a['goal'],a['donors'],[float(x) for x in w['weights']]))
    mutated=json.loads(json.dumps(word));mutated['B'][283][0]=0
    reject('wrong_frame',lambda:block(mutated,509,283,314))
    return dict(schema=1,status='passed',blocks=results,separated_rows=witness_rows,
                rows_checked=sum(len(b['rows']) for b in results),
                functionals_checked=sum(r['functionals_tested'] for b in results for r in b['rows']),
                mathematical_controls=controls,new_kappa=False,new_circuit=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--write-certificate',type=Path);args=p.parse_args()
    result=run()
    if args.write_certificate:
        with args.write_certificate.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    else:need(canon(result)==canon(json.loads((P/'EXPECTED.json').read_text())),'certificate mismatch')
    print('PASS_DONOR_SEPARATION17 rows=%d functionals=%d separated=4 controls=%d' %
          (result['rows_checked'],result['functionals_checked'],len(result['mathematical_controls'])))


if __name__=='__main__':main()
