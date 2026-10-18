#!/usr/bin/env python3
"""Dense finite-field rank-one BFS and cyclic-rotation controls.

No producer implementation is imported. @woklerx / OpenAI Codex, Apache-2.0.
Both implementations are AI-written; this is not independent human review.
"""
from collections import Counter,deque
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
I=tuple(int(i==j) for i in range(4) for j in range(4))


def need(ok,message):
    if not ok:raise ValueError(message)


def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def multiply(a,b,p=2):
    return tuple(sum(a[4*i+k]*b[4*k+j] for k in range(4))%p for i in range(4) for j in range(4))


def matrix_rank(values,n,p=2):
    a=[list(values[n*i:n*i+n]) for i in range(n)]
    r=0
    for j in range(n):
        pivot=next((i for i in range(r,n) if a[i][j]%p),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r]
        inverse=pow(a[r][j],-1,p)
        a[r]=[x*inverse%p for x in a[r]]
        for i in range(r+1,n):
            q=a[i][j]
            a[i]=[(x-q*y)%p for x,y in zip(a[i],a[r])]
        r+=1
    return r


def inverse(a,p=2):
    rows=[list(a[4*i:4*i+4])+[int(i==j) for j in range(4)] for i in range(4)]
    for j in range(4):
        pivot=next(i for i in range(j,4) if rows[i][j]%p)
        rows[j],rows[pivot]=rows[pivot],rows[j]
        c=pow(rows[j][j],-1,p);rows[j]=[x*c%p for x in rows[j]]
        for i in range(4):
            if i==j:continue
            c=rows[i][j];rows[i]=[(x-c*y)%p for x,y in zip(rows[i],rows[j])]
    return tuple(x for row in rows for x in row[4:])


def shear(direction,k,p=2):
    out=list(I)
    for i in range(2):
        for j in range(2):
            r,c=(i,j+2) if direction==0 else (i+2,j)
            out[4*r+c]=k[2*i+j]%p
    return tuple(out)


def classify(a,p=2):
    need(all(a[4*i+j]==int(i==j) for i in range(4) for j in range(4) if (i<2)==(j<2)), 'not a cross shear')
    upper=tuple(a[4*i+j+2] for i in range(2) for j in range(2))
    lower=tuple(a[4*(i+2)+j] for i in range(2) for j in range(2))
    need(not(any(upper) and any(lower)),'two nonzero cross blocks')
    return (0,matrix_rank(upper,2,p)) if any(upper) else (1,matrix_rank(lower,2,p))


def exchange(a):
    return all(a[4*i+j]==0 for i in range(4) for j in range(4) if (i<2)==(j<2)) and matrix_rank(a,4)==4


def compose(gates,p=2):
    result=I
    for gate in gates:result=multiply(gate,result,p)
    return result


def rejects(action,label):
    try:action()
    except ValueError:return
    raise ValueError('invalid interface accepted: '+label)


def run():
    expected=json.loads((HERE/'EXPECTED.json').read_text())
    need(expected['base_commit']=='2921874911956718fcaaaf9396fe8267b3cfa9f0','base')
    generators=[]
    decomposition_checks=0
    for direction in (0,1):
        for code in range(1,16):
            k=tuple((code>>i)&1 for i in range(4))
            g=shear(direction,k)
            r=matrix_rank(k,2)
            if r==1:generators.append(g)
            else:
                # Split by columns: every rank-two shear is two rank-one
                # shears of the same direction and exactly the same rank cost.
                k0=(k[0],0,k[2],0);k1=(0,k[1],0,k[3])
                need(matrix_rank(k0,2)==matrix_rank(k1,2)==1,'column split ranks')
                need(multiply(shear(direction,k1),shear(direction,k0))==g,'rank-two decomposition')
                decomposition_checks+=1
    need(len(generators)==18 and decomposition_checks==12,'generator census')
    # Unweighted BFS on dense matrices independently obtains all weighted
    # distances, since rank-two calls split at equal total rank cost.
    distance={I:0};queue=deque([I])
    while queue:
        state=queue.popleft()
        for g in generators:
            nxt=multiply(g,state)
            if nxt not in distance:distance[nxt]=distance[state]+1;queue.append(nxt)
    need(len(distance)==20160,'independent group closure')
    histogram=dict(sorted(Counter(str(x) for x in distance.values()).items()))
    need(histogram==expected['distance_histogram'],'independent distances histogram')
    labels=[]
    for matrix,d in distance.items():
        rows=[sum(matrix[4*i+j]<<j for j in range(4)) for i in range(4)]
        labels.append([rows,d])
    labels.sort(key=lambda item:sum(x<<(4*i) for i,x in enumerate(item[0])))
    need(hashlib.sha256(encoded(labels)).hexdigest()==expected['distance_labels_sha256'],'every independent distance label')
    goals=[s for s in distance if exchange(s)]
    need(len(goals)==36 and min(distance[s] for s in goals)==5,'rank volume optimum')
    witness=[shear(d,tuple((k>>i)&1 for i in range(4))) for d,k,r in expected['minimum_rank_witness']]
    need(len(witness)==5 and all(classify(g)[1]==1 for g in witness),'five-call rank-one witness')
    need(exchange(compose(witness)),'witness endpoint')
    full=shear(0,(1,0,0,1));back=shear(1,(1,0,0,1))
    need(exchange(compose([full,back,full])),'three-call rank-two witness')
    deletions=0
    for i in range(5):
        need(not exchange(compose(witness[:i]+witness[i+1:])), 'omitted-call control')
        deletions+=1
    rotations=0;unconjugated_failures=0
    # Algebraic rotation checked over three fields, with nontrivial invertible
    # off-diagonal endpoints and free invertible within-bank bridges.
    for p in (2,3,5):
        up=shear(0,(1,0,0,1),p);down=shear(1,(-1,0,0,-1),p)
        bridge=(1,1,0,0,0,1,0,0,0,0,1,0,0,0,1,1)
        gates=[up,down,up,bridge]
        endpoint=compose(gates,p);ei=inverse(endpoint,p)
        for _ in range(len(gates)):
            first=gates[0];moved=multiply(multiply(endpoint,first,p),ei,p)
            if all(first[4*i+j]==0 for i in range(4) for j in range(4) if (i<2)!=(j<2)):
                need(all(moved[4*i+j]==0 for i in range(4) for j in range(4) if (i<2)!=(j<2)),'bridge class changed')
            else:
                need(classify(first,p)[1]==classify(moved,p)[1],'shear rank changed')
            rotated=gates[1:]+[moved]
            need(compose(rotated,p)==endpoint,'cyclic conjugation identity')
            unconjugated_failures+=compose(gates[1:]+[first],p)!=endpoint
            gates=rotated;rotations+=1
    need(unconjugated_failures>0,'unconjugated rotation control vacuous')
    partial=shear(0,(1,0,0,0));partial_back=shear(1,(1,0,0,0))
    partial_endpoint=compose([partial,partial_back,partial])
    rejects(lambda:need(exchange(partial_endpoint),'partial endpoint'),'partial exchange')
    rejects(lambda:need(classify(full)[1]==1,'false rank declaration'),'rank metadata')
    # An off-diagonal bridge for free would perform the entire exchange with
    # no paid call, and is expressly outside the theorem's allowed bridges.
    free_exchange=compose([full,back,full])
    rejects(lambda:need(all(free_exchange[4*i+j]==0 for i in range(4) for j in range(4) if (i<2)!=(j<2)),
                        'cross-bank bridge'),'bridge contract')
    return {'dense_rank_one_generators':18,'rank_two_decompositions':decomposition_checks,
        'dense_group_states':len(distance),'distance_histogram':histogram,
        'all_distance_labels_match':True,'rotation_fields':[2,3,5],'rotation_checks':rotations,
        'unconjugated_rotation_failures':unconjugated_failures,'omitted_call_controls':deletions,
        'other_controls':['partial exchange excluded','false rank-one metadata excluded','free cross-bank bridge excluded'],
        'pareto_witnesses':[[3,6],[5,5]]}


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    result=run();path=HERE/'INDEPENDENT.json'
    if args.write:
        with path.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    else:need(encoded(result)==encoded(json.loads(path.read_text())),'independent receipt mismatch')
    print('PASS_STAGE_RANK_INDEPENDENT dense_states=20160 decompositions=12 rotations=12 fields=2,3,5')


if __name__=='__main__':main()
