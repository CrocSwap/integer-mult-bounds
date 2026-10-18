"""Exact selected HPE helper-boundary fault atlas; Apache-2.0."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import copy,gzip,hashlib,json,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
SOURCE='research/two-accumulator-saved-arms/evidence/selected1094-CANONICAL-WORD.json.gz'
def need(x,m):
    if not x:raise ValueError(m)
def rank(rows):
    piv={}
    for x in rows:
        while x:
            bit=x.bit_length()-1
            if bit not in piv:piv[bit]=x;break
            x^=piv[bit]
    return len(piv)
def apply_rows(g,rows):
    if g[0]=='scale':
        _,d,a,b,*_=g;rows[d]={j:v*Q(a,b) for j,v in rows[d].items()}
    else:
        _,d,s,a,b,*_=g;need(d!=s,'distinct ADD operands')
        for j,v in list(rows[s].items()):
            z=rows[d].get(j,Q(0))+v*Q(a,b)
            if z:rows[d][j]=z
            else:rows[d].pop(j,None)
def apply_column(g,state):
    # Independent scalar arithmetic path; no row map or outer-product formula.
    if g[0]=='scale':state[g[1]]=state[g[1]]*g[2]/g[3]
    else:state[g[1]]=state[g[1]]+state[g[2]]*g[3]/g[4]
def replay_column(program,n,j,omit=None):
    x=[Q(0)]*n;x[j]=Q(1)
    for i,g in enumerate(program):
        if i!=omit:apply_column(g,x)
    return x
def run():
    for pin in json.loads((H/'SOURCES.json').read_text())['files']:
        if pin['usage']=='input':need(hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'source hash')
    payload=gzip.decompress((ROOT/SOURCE).read_bytes());w=json.loads(payload);n=len(w['start']);v=w['v']
    need(hashlib.sha256(payload).hexdigest()=='4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c','selected source payload')
    prefix=sum((w[s] for s in ('precondition','compensation','A','cut','B')),[]);tail=w['tail'];cleanup=w['cleanup'];program=prefix+tail+cleanup
    proper=[i for i in range(2*v,n) if rank(w['frames'][w['final'][i]])<w['h']]
    rows=[{i:Q(1)} for i in range(n)]
    for g in prefix:apply_rows(g,rows)
    atlas=[];types=Counter()
    for k,g in enumerate(tail):
        d=g[1];source=g[2] if g[0]=='add' else d
        coefficient=-Q(g[3],g[4]) if g[0]=='add' else 1-Q(g[2],g[3])
        row=dict(rows[source]);column=[Q(0)]*n;column[d]=coefficient
        for later in tail[k+1:]+cleanup:apply_column(later,column)
        need(row and any(column),'nonzero exact rank-one omission')
        rowbad=[i for i in proper if column[i]]
        colbad=[j for j in proper if row.get(j) and any(i!=j and x for i,x in enumerate(column))]
        input_index=min(row);output_index=next(i for i,x in enumerate(column) if x)
        clean=replay_column(program,n,input_index);faulty=replay_column(program,n,input_index,len(prefix)+k)
        need(all(faulty[i]-clean[i]==column[i]*row[input_index] for i in range(n)),'literal column vs exact syndrome')
        need(faulty!=clean,'independent omission detection')
        category=('row' if rowbad else '')+('column' if colbad else '') or 'neither';types[category]+=1
        atlas.append({'tail_index':k,'operation':g,'row_failures':rowbad,'column_failures':colbad,'input':input_index,'output':output_index,'delta':str(faulty[output_index]-clean[output_index])})
        apply_rows(g,rows)
    for g in cleanup:apply_rows(g,rows)
    expected=[{i:Q(1)} for i in range(n)]
    for i in range(v):expected[v+i][i]=Q(1)
    need(rows==expected,'complete original arbitrary-dirty scalar endpoint')
    need(all(rows[i]=={i:Q(1)} for i in proper),'all proper helpers have unit rows')
    need(all(not rows[j].get(i) for i in proper for j in range(n) if i!=j),'all proper helpers have zero off-diagonal columns')
    return {'status':'PASS_SELECTED_HPE_TAIL_FAULT_ATLAS','source_content_sha256':hashlib.sha256(payload).hexdigest(),'registers':n,'proper_helpers':proper,'proper_widths':dict(sorted(Counter(rank(w['frames'][w['final'][i]])-rank(w['frames'][w['start'][i]]) for i in proper).items())),'tail_operations':len(tail),'tail_types':dict(Counter(g[0] for g in tail)),'detection_classes':dict(types),'faults':atlas,'literal_fault_columns_checked':len(atlas),'new_kappa':False}
if __name__=='__main__':
    result=json.loads(json.dumps(run()));path=H/'CERTIFICATE.json'
    if '--write' in sys.argv:path.write_text(json.dumps(result,indent=2)+'\n')
    else:need(result==json.loads(path.read_text()),'receipt mismatch')
    print(result['status'],'helpers='+str(len(result['proper_helpers'])),'faults='+str(result['tail_operations']),result['detection_classes'])
