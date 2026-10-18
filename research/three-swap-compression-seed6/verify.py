#!/usr/bin/env python3
"""Check all exact CNFs and every supplied DRUP proof without a SAT solver.
Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip,hashlib,itertools,json
from pathlib import Path
import time
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import cnf
from rup import Database,check_proof,slow_conflict

def require(ok,message):
    if not ok:raise RuntimeError(message)

def gadget_controls():
    for op in ('both','xor'):
        for a,b,expected in itertools.product((False,True),repeat=3):
            f=cnf.Formula();x=f.variable();y=f.variable();out=getattr(f,op)(x,y)
            actual=not slow_conflict(f.clauses,[x if a else -x,y if b else -y,out if expected else -out])
            require(actual==(expected==((a and b) if op=='both' else (a!=b))), 'Tseitin gadget equivalence failed')
    failures=0
    for clauses,proof in [([[1]],['0']),([[1,2]],['-1 0']),([[1,2],[1,-2],[-1,2],[-1,-2]],['0']),([[1],[-1]],[])]:
        try:check_proof(2,clauses,proof)
        except ValueError:failures+=1
        else:raise RuntimeError('invalid or unfinished RUP control accepted')
    check_proof(2,[[1,2],[1,-2],[-1,2],[-1,-2]],['1 0','0'])
    check_proof(1,[[1],[-1]],['0'])
    # Complete two-variable clause-set domain, compared against slow propagation.
    possible=[]
    for choices in itertools.product((-1,0,1),repeat=2):
        clause=[(i+1)*sign for i,sign in enumerate(choices) if sign]
        if clause:possible.append(clause)
    comparisons=0
    for mask in range(1<<len(possible)):
        clauses=[c for i,c in enumerate(possible) if mask>>i&1];database=Database(2,clauses)
        for choices in itertools.product((-1,0,1),repeat=2):
            assumptions=[(i+1)*sign for i,sign in enumerate(choices) if sign]
            require(database.conflict(assumptions)==slow_conflict(clauses,assumptions),'watched/slow propagation mismatch')
            comparisons+=1
    return failures,comparisons

def group_controls():
    # Independently construct the coordinate action on nonzero binary vectors.
    def action(g):
        values=[]
        for v in (1,2,3):
            x=((g&1)*(v&1)^((g>>1)&1)*((v>>1)&1))
            y=(((g>>2)&1)*(v&1)^((g>>3)&1)*((v>>1)&1))
            values.append((1,2,3).index(x+2*y))
        return tuple(values)
    groups=[g for g in range(16) if ((g&1)*((g>>3)&1)^((g>>1)&1)*((g>>2)&1))==1]
    require(set(map(action,groups))==set(cnf.GROUP),'GL2/S3 isomorphism mismatch')
    for left,right in itertools.product(groups,repeat=2):
        product=sum((sum(((left>>(2*i+k))&1)*((right>>(2*k+j))&1) for k in range(2))%2)<<(2*i+j) for i in range(2) for j in range(2))
        require(cnf.INDEX[action(product)]==cnf.MUL[cnf.INDEX[action(left)]][cnf.INDEX[action(right)]],'GL2/S3 multiplication mismatch')
    require(action(11)==cnf.GROUP[cnf.A] and action(13)==cnf.GROUP[cnf.B] and action(6)==cnf.GROUP[cnf.SWAP],'group label mismatch')
    for a,b,c in itertools.product(range(6),repeat=3):require(cnf.MUL[cnf.MUL[a][b]][c]==cnf.MUL[a][cnf.MUL[b][c]],'group associativity')
    require(cnf.MUL[cnf.MUL[cnf.A][cnf.B]][cnf.A]==cnf.SWAP,'ABA witness failed')

def main():
    started=time.monotonic();group_controls();failures,comparisons=gadget_controls()
    payload=gzip.decompress((ROOT/'CERTIFICATES.json.gz').read_bytes());d=json.loads(payload)
    require(d['format']=='CNF-and-DRUP-v1' and len(d['results'])==35,'missing pattern certificates')
    require([x['index'] for x in d['results']]==list(range(35)),'duplicate or missing pattern')
    additions=deletions=clauses=0
    for record,labels in zip(d['results'],cnf.patterns()):
        require(record['labels']==labels,'label domain mismatch');formula=cnf.encode(labels)
        require(record['variables']==formula.variables and record['clauses']==formula.clauses,'CNF differs from fresh exact encoding')
        checked=check_proof(formula.variables,formula.clauses,record['proof'])
        additions+=checked['rup_additions'];deletions+=checked['ignored_deletions'];clauses+=len(formula.clauses)
    # Full arbitrary-dirty nine-call upper bound, represented by all 24 regular columns.
    word=[{'u':1<<i,'v':1<<i,'label':label} for i in range(3) for label in ('b','a','b')]
    state=cnf.concrete(word)
    target=[[[int(i==j and h==(cnf.SWAP if i<3 else cnf.IDENT)) for j in range(4)] for i in range(4)] for h in range(6)]
    require(state==target,'nine-call formal word failed')
    positive=cnf.encode('babbabbab',pinned=word)
    assignment={1:True}
    def value(literal):return assignment[abs(literal)] if literal>0 else not assignment[abs(literal)]
    for gate,(u,v) in zip(word,positive.projectors):
        for name,literals in [('u',u),('v',v)]:
            for i,literal in enumerate(literals):
                bit=bool(gate[name]>>i&1)
                if abs(literal)==1:require(value(literal)==bit,'pinned positive constant mismatch')
                else:assignment[abs(literal)]=bit if literal>0 else not bit
    for variable,operation,a,b in positive.operations:
        assignment[variable]=(value(a) and value(b)) if operation=='and' else (value(a)!=value(b))
    require(all(any(value(x) for x in row) for row in positive.clauses),'positive construction fails the actual CNF clauses')
    corrupt=[x.copy() for x in word];corrupt[0]['label']='a';require(cnf.concrete(corrupt)!=target,'wrong paid-label control is vacuous')
    print(json.dumps({'status':'PASS_THREE_SWAP_COMPRESSION','patterns':35,'registers':4,'active_swaps':3,'excluded_calls':7,'attaining_calls':9,'cnf_clauses':clauses,'rup_additions':additions,'ignored_deletions':deletions,'rup_negative_controls':failures,'watched_vs_slow_cases':comparisons,'payload_sha256':hashlib.sha256(payload).hexdigest(),'elapsed_seconds':round(time.monotonic()-started,6)},sort_keys=True))
if __name__=='__main__':main()
