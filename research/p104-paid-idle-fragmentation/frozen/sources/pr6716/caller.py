"""Changed eight-field common-idle caller, using exact ordinary bases.

Cinna Davis supplies the native query and binary supplier lineage. The
six-field root and exact coefficient-ring replay are by Ali Romman with
Codex assistance. The changed rank-(2,4,4,3,2) root, common-idle fusion and
fresh-input application are by thu-nmrc with substantial Codex assistance.
Apache-2.0. This constructor requires only the Python standard library.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
from algebra import Q,accumulate,coefficient,eye,matrix,need,shifted,zmul
HERE=Path(__file__).resolve().parent

def unit(q):
    q=Q(q)
    return q and abs(q.numerator)&(abs(q.numerator)-1)==0 and q.denominator&(q.denominator-1)==0

def construct():
    data=json.loads((HERE/'ROOT.json').read_text())
    full,masks=data['full_sites'],data['masks']
    bases={int(i):matrix(m)for i,m in data['bases'].items()}
    events,targets,nodes,cuts=[],{},[],{}
    stage,next_role=0,8
    def emit(op,*args):events.append([op,*args])
    def mix(rows):
        a=deepcopy(rows);ops=[]
        for j in range(8):
            k=next((k for k in range(j,8)if unit(a[k][j])),None)
            need(k is not None,'Declared dyadic unit pivot')
            if k!=j:a[j],a[k]=a[k],a[j];ops.append(['SWAP',j,k])
            c=1/a[j][j]
            if c!=1:a[j]=[c*x for x in a[j]];ops.append(['SCALE',j,str(c)])
            for k in range(8):
                if k!=j and a[k][j]:
                    c=-a[k][j];a[k]=[x+c*y for x,y in zip(a[k],a[j])];ops.append(['ADD',k,j,str(c)])
        need(a==eye(8),'Complete ordinary basis elimination')
        for e in reversed(ops):
            if e[0]=='ADD':e[-1]=str(-Q(e[-1]))
            elif e[0]=='SCALE':e[-1]=str(1/Q(e[-1]))
            emit(*e)
    def label(t):
        nonlocal stage
        if t==1:stage+=1;return {'stage':stage,'stages':[stage]}
        a,b=map(label,t);return {'left':a,'right':b,'stages':a['stages']+b['stages']}
    def shape(n):
        return 1 if n==1 else [shape(n//2),shape(n-n//2)]
    trees=[label(shape(n))for n in data['child_sizes']]
    need(trees==data['trees'],'Declared independent stage allocation')
    def query(x,y):
        emit('LAMBDA',x,-1);emit('QUERY',x,y,-1);emit('LAMBDA',x,1)
    def supplier(t,x,y):
        nonlocal next_role
        if 'stage'in t:
            emit('LAMBDA',x,-1);emit('LOCAL',t['stage'],y,x);emit('LAMBDA',x,1);return
        a,b=next_role,next_role+1;next_role+=2;st=t['stages'];nodes.append({'roles':[a,b],'stages':st})
        emit('SWAP',x,b);emit('SWAP',y,a);emit('SWAP',a,b)
        emit('ADD',x,a,'1');emit('ADD',b,y,'-1');query(a,b)
        cuts[tuple(st)]={'cut_after':len(events)-1,'pivot_aux':[a,b],'active':[x,y]}
        emit('ADD',b,y,'1');emit('ADD',x,a,'-1');emit('IDLE',a,b,st)
        emit('SCALE',y,'-1');supplier(t['left'],y,x);emit('SCALE',y,'-1');supplier(t['right'],x,y)
        emit('ADD',x,a,'1');emit('SCALE',a,'-1');emit('ADD',a,x,'1');emit('SWAP',y,b);emit('SCALE',b,'-1');emit('ADD',b,y,'1')
        targets[a],targets[b]=[-1,st],[-1,st]
    from algebra import inverse
    fi,i=0,0
    while i<9:
        c=bases[i];mix(inverse(c))
        if i==1:
            b,ct=trees[fi:fi+2];fi+=2
            supplier(b,0,1);emit('ADD',0,1,'-1')
            emit('SCALE',1,'-1');supplier(ct,1,0);emit('SCALE',1,'-1');emit('ADD',1,0,'1')
            emit('IDLE',2,3,b['stages']+ct['stages']);i+=2
        elif i in full:
            t=trees[fi];fi+=1;supplier(t,0,1);emit('ADD',0,1,'-1')
            for r in range(2,masks[full.index(i)].bit_count()):emit('IDLE_ONE',r,t['stages'])
            i+=1
        else:query(0,1);emit('ADD',0,1,'-1');i+=1
        mix(c)
    for r in range(8):
        targets[r]=[-1,[j for mask,t in zip(masks,trees)if mask>>r&1 for j in t['stages']]]
    for r in range(next_role):emit('LAMBDA',r,-1)
    diagonal=[[targets[r][0],0]+[int(j in targets[r][1])for j in range(1,stage+1)]for r in range(next_role)]
    need((stage,next_role)==(18,34),'Complete caller dimensions')
    return {'schema':'root8-common-idle-fusion/1','roles':next_role,'stages':stage,'ambient_rank':9+8*stage,
            'events':events,'diagonal':diagonal,'nodes':nodes}

def replay(word):
    n,width=word['roles'],word['stages']+2;zero=(0,)*width
    rows=[[{zero:coefficient(1)}if i==j else {}for j in range(n)]for i in range(n)];seen=[]
    for event in word['events']:
        op=event[0]
        if op=='ADD':
            _,dst,src,c=event
            for a,b in zip(rows[dst],rows[src]):accumulate(a,b,coefficient(c))
        elif op=='SCALE':
            _,dst,c=event;rows[dst]=[{key:zmul(coefficient(c),value)for key,value in cell.items()}for cell in rows[dst]]
        elif op=='SWAP':
            _,a,b=event;rows[a],rows[b]=rows[b],rows[a]
        elif op in ('LOCAL','QUERY'):
            if op=='LOCAL':_,stage,src,dst=event;exponent=-1;seen.append(stage)
            else:_,dst,src,exponent=event
            term=(exponent,)+(0,)*(width-1)
            for a,b in zip(rows[dst],shifted(rows[src],term)):accumulate(a,b)
            if op=='LOCAL':
                term=(0,)+tuple(int(s==stage)for s in range(width-1))
                for r in (src,dst):rows[r]=shifted(rows[r],term)
        elif op=='Q_POWER':rows[event[1]]=shifted(rows[event[1]],(event[2],)+(0,)*(width-1))
        elif op=='LAMBDA':
            _,r,sign=event;need(sign in(-1,1),'Ordinary normalization sign')
            old=rows[r];other=shifted(old,(2,)+(0,)*(width-1));rows[r]=[{}for _ in range(n)]
            for dst,a,b in zip(rows[r],old,other):
                accumulate(dst,a,(Q(1,2),Q(sign,2)));accumulate(dst,b,(Q(1,2),Q(-sign,2)))
        elif op in('IDLE','IDLE_ONE'):
            roles,stages=(event[1:3],event[3])if op=='IDLE'else([event[1]],event[2])
            need(len(stages)==len(set(stages)),'Distinct whole-idle axes')
            term=(0,)+tuple(int(s in stages)for s in range(width-1))
            for r in roles:rows[r]=shifted(rows[r],term)
        else:raise ValueError('Unknown caller opcode')
    expected=[[{(word['diagonal'][i][0]%4,)+tuple(word['diagonal'][i][1:]):coefficient(1)}if i==j else {}for j in range(n)]for i in range(n)]
    need(sorted(seen)==list(range(1,word['stages']+1)),'Every distinct native stage once')
    need(rows==expected,'Every arbitrary-input forward coefficient')
    return {'inputs':n,'coefficients':n*n,'native_stages':len(seen),'events':len(word['events']),
            'event_sha256':sha256(json.dumps(word['events'],separators=(',',':')).encode()).hexdigest()}

def controls(word):
    controls={}
    for op in('LOCAL','QUERY','IDLE','IDLE_ONE','LAMBDA','ADD'):
        bad=deepcopy(word);del bad['events'][next(i for i,e in enumerate(bad['events'])if e[0]==op)]
        try:replay(bad)
        except ValueError as error:controls['missing_'+op.lower()]=str(error)
        else:raise ValueError('Missing gate accepted: '+op)
    return controls
