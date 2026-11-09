#!/usr/bin/env python3
"""Exact field-level root and commutant checks; standard library, no writes."""
import copy,json,hashlib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from linear import *
from generate import dual_word,coupled_chain,jsonable,parse_root


def check_root(root, masks=True):
    n,N=root['n'],root['N'];X=root['X'];Y=root['Y'];p=root['dual_p'];q=root['dual_q']
    require(N==n+2,'corank must be two')
    require(len(root['full'])>=2,'at least two full blocks')
    require(len(X)==len(Y)==len(p)==len(q)==N,'unit counts')
    require(all(len(row)==n for row in X+Y),'primal dimensions')
    require(all(len(row)==2 for row in p+q),'dual dimensions')
    indices=[u for block in root['full'] for u in block]+root['thin']
    require(sorted(indices)==list(range(N)),'full/thin partition')
    require(root['full']==sorted(root['full']) and root['thin']==sorted(root['thin']),'chronological metadata')
    for a,b in root['full']:
        require(b==a+1,'full pairs must be consecutive')
        require(dot(Y[a],X[b])==dot(Y[b],X[a])==0,'full pair orthogonality')
    primal=identity(n);dual=identity(2);prefix=[primal]
    for k in range(N):
        require(any(X[k]) and any(Y[k]),'nonzero primal units')
        require(dot(Y[k],X[k])==0,'primal isotropy')
        require(dot(p[k],q[k])==1,'dual reflection')
        primal=left_transvection(primal,X[k],Y[k]);prefix.append(primal)
        dual=left_transvection(dual,q[k],p[k])
    require(primal==scale(identity(n),-1),'primal product minus identity')
    require(dual==scale(identity(2),-1),'dual product minus identity')
    for i in range(N):
        for j in range(N):
            expected=Q((i>j)-(i<j))*dot(p[i],q[j])
            require(dot(Y[i],X[j])==expected,'signed dual Gram identity')
    if masks and 'stages' in root:
        require([st['units'] for st in root['stages']]==root['full'],'stage/full matching')
        for stage in root['stages']:
            mask=set(stage['mask']);require(all(0<=j<n for j in mask),'mask range')
            for u in stage['units']:
                require(all(not X[u][j] and not Y[u][j] for j in range(n) if j not in mask),'inside-mask support')
            for k in [stage['units'][0],stage['units'][-1]+1]:
                require(all(not prefix[k][i][j] for i in range(n) for j in range(n)
                            if (i in mask)!=(j in mask)),'prefix-mask commutation')
    return True


def operators(root, grouped=True):
    X,Y=root['X'],root['Y']
    if not grouped:return [outer(x,y) for x,y in zip(X,Y)]
    return [add(outer(X[a],Y[a]),outer(X[b],Y[b])) for a,b in root['full']]+[outer(X[s],Y[s]) for s in root['thin']]


def normalize(root):
    out=copy.deepcopy(root)
    for a,b in root['full']:
        qi=transpose([root['dual_q'][a],root['dual_q'][b]])
        x=transpose([root['X'][a],root['X'][b]]);y=[root['Y'][a],root['Y'][b]]
        xx=transpose(multiply(x,inverse(qi)));yy=multiply(qi,y)
        require(multiply(x,y)==multiply(transpose(xx),yy),'grouped operator preserved by pair gauge')
        out['X'][a],out['X'][b]=xx;out['Y'][a],out['Y'][b]=yy
        out['dual_q'][a],out['dual_q'][b]=identity(2)
        out['dual_p'][a],out['dual_p'][b]=identity(2)
    check_root(out,masks=False)
    for i,(a,b) in enumerate(out['full']):
        for j,(c,d) in enumerate(out['full']):
            block=[[dot(out['Y'][u],out['X'][v]) for v in [c,d]] for u in [a,b]]
            require(block==scale(identity(2),(i>j)-(i<j)),'full block normal form')
    return out


def lift(root,a):
    n,N=root['n'],root['N'];x=transpose(root['X']);y=root['Y'];d=[[Q(0)]*N for _ in range(N)]
    for block in root['full']:
        for i,u in enumerate(block):
            for j,v in enumerate(block):d[u][v]=a[i][j]
    for s in root['thin']:
        p,q=root['dual_p'][s],root['dual_q'][s]
        lam=dot(p,[dot(row,q) for row in a])
        require([dot(row,q) for row in a]==[lam*v for v in q],'dual column eigenline')
        require([dot(p,col) for col in transpose(a)]==[lam*v for v in p],'dual row eigenline')
        d[s][s]=lam
    _,pivots=rref(x);basis=[[row[j] for j in pivots] for row in x];xd=multiply(x,d)
    s=multiply([[row[j] for j in pivots] for row in xd],inverse(basis))
    require(multiply(s,x)==xd and multiply(y,s)==multiply(d,y),'explicit quotient intertwiner')
    return s


def commutator_unit(s,x,y):
    sx=[dot(row,x) for row in s];ys=[dot(y,col) for col in transpose(s)]
    return add(outer(sx,y),outer(x,ys),-1)


def large_primal_commutant(root):
    """Eight-dimensional full-block algebra; direct thin commutator equations."""
    n=root['n'];full=[u for pair in root['full'] for u in pair]
    kernel=nullspace([root['Y'][u] for u in full]);require(len(kernel)==2,'two-dimensional full kernel')
    b=transpose([root['X'][u] for u in full]+kernel);bi=inverse(b);candidate=[]
    for part in ('full','kernel'):
        for a in range(2):
            for c in range(2):
                m=[[Q(0)]*n for _ in range(n)]
                if part=='full':
                    for i in range(len(root['full'])):m[2*i+a][2*i+c]=1
                else:m[len(full)+a][len(full)+c]=1
                candidate.append(multiply(multiply(b,m),bi))
    columns=[]
    for s in candidate:
        for a,b in root['full']:
            z=add(commutator_unit(s,root['X'][a],root['Y'][a]),commutator_unit(s,root['X'][b],root['Y'][b]))
            require(not any(flatten(z)),'full commutant basis directly checked')
        col=[]
        for u in root['thin']:col.extend(flatten(commutator_unit(s,root['X'][u],root['Y'][u])))
        columns.append(col)
    require(rank([flatten(s) for s in candidate])==8,'full commutant basis independent')
    return 8-rank(transpose(columns))


def must_reject(fn,label):
    try:fn()
    except (ValueError,IndexError,KeyError):return label
    raise ValueError('negative control accepted: '+label)


def formal_root_invoice(root):
    from collections import Counter
    targets=Counter();paid=Counter();stages=root['stages'];X=root['X'];Y=root['Y']
    for c in range(root['n']):
        carrying=[i for i,s in enumerate(stages) if c in s['mask']]
        hosts={i for i in carrying if any(Q(Y[u][c]) for u in stages[i]['units'])}
        targets[8*len(carrying)+1]+=104
        run=0;last=None
        for i in carrying:
            if i in hosts:
                if run:paid[8*run]+=104
                run=0;last=None
            elif last is not None and i==last+1:run+=1;last=i
            else:
                if run:paid[8*run]+=104
                run=1;last=i
        if run:paid[8*run]+=104
    for st in stages:
        hosts=sum(any(Q(Y[u][c]) for u in st['units']) for c in range(root['n']))
        require(hosts==4,'inherited four-coordinate host support')
    paid[1]+=104*(root['N']-2*len(stages))
    return targets,paid


def main():
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for item in sources['retained']:
        require(hashlib.sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256'],'retained source SHA256')
    small=None;large=None
    for g in (1,9):
        generated=coupled_chain(g,g)
        stored=json.loads((HERE/'data'/('root-%d.json'%generated['n'])).read_text())
        require(jsonable(generated)==stored,'fixture regeneration')
        check_root(generated)
        require(all(v.denominator&(v.denominator-1)==0 for row in generated['X']+generated['Y'] for v in row),'dyadic witness coefficients')
        if g==1:small=generated
        else:large=generated
        print('PASS exact witness',generated['n'],'fields',generated['N'],'units',flush=True)

    full_bases=[identity(2),[[Q(1),Q(1)],[Q(0),Q(1)]],[[Q(1),Q(0)],[Q(1),Q(1)]]]
    zero=dual_word(3,[],[],full_bases);check_root(zero);normal=normalize(zero)
    require(direct_commutant_dimension(operators(zero))==4,'zero-thin grouped commutant dimension four')
    require(direct_commutant_dimension(operators(zero,False))==1,'individual summands differ from grouped operators')
    graph=[[bool(dot(y,x)) for x in zero['X']] for y in zero['Y']]
    for start in range(zero['N']):
        seen={start};todo=[start]
        while todo:
            u=todo.pop()
            for v in range(zero['N']):
                if graph[u][v] and v not in seen:seen.add(v);todo.append(v)
        require(len(seen)==zero['N'],'strong Gram graph despite decomposable grouped stages')
    elementary=[];lifted=[]
    for a in range(2):
        for b in range(2):
            m=[[Q(0)]*2 for _ in range(2)];m[a][b]=1;elementary.append(m);lifted.append(lift(normal,m))
    require(rank([flatten(s) for s in lifted])==4,'four independent lifted matrices')
    for i,a in enumerate(elementary):
        for j,b in enumerate(elementary):
            require(multiply(lifted[i],lifted[j])==lift(normal,multiply(a,b)),'algebra multiplication preserved')
    print('PASS zero-thin normal form, full M2 algebra, strong graph and grouped/summand distinction',flush=True)

    case_count=0
    for length in (2,3,4):
        q1=[Q(2),Q(2)];p1=[Q(1,4),Q(1,4)]
        if length%2==0:q2=[Q(-1,2),Q(1,2)];p2=[Q(-1),Q(1)]
        else:q2=[Q(-1,2),Q(-1,2)];p2=[Q(-1),Q(-1)]
        for positions in ([0,length],[1,1]):
            bases=[full_bases[i%3] for i in range(length)]
            root=dual_word(length,[(q1,p1),(q2,p2)],positions,bases);check_root(root);nr=normalize(root)
            projection=outer(q1,p1);s=lift(nr,projection)
            require(multiply(s,s)==s,'lifted idempotent')
            expected=length if length%2==0 else length+1
            require(rank(s)==expected and rank(add(identity(root['n']),s,-1))==root['n']-expected,'summand dimensions')
            require(direct_commutant_dimension(operators(root))==2,'two-thin direct primal commutant dimension two')
            case_count+=1
    print('PASS two-thin cases',case_count,'with both parities, separated/coincident gaps and scaled thin vectors',flush=True)

    require(direct_commutant_dimension(operators(small))==1,'four-thin direct full primal equations')
    require(large_primal_commutant(large)==1,'38-field direct primal equations in eight-dimensional full algebra')
    a=([1,0],[1,0]);b=([1,1],[Q(1,2),Q(1,2)])
    odd=dual_word(3,[a,b,b,a],[0,1,2,3]);check_root(odd)
    require(direct_commutant_dimension(operators(odd))==1,'odd-length four-thin direct primal control')
    six=dual_word(2,[a,b,a,b,a,a],[0,0,1,1,2,2]);check_root(six)
    require(direct_commutant_dimension(operators(six))==1,'six-thin direct primal control')
    print('PASS scalar commutants: even/odd four-thin roots, 38-field root, and six-thin root',flush=True)

    predecessor=json.loads((HERE/'data/root-6902.json').read_text())
    require(predecessor['n']==40 and predecessor['N']==42,'predecessor shape')
    mapping=list(range(19))+list(range(20,39))
    for new,old in zip(large['stages'],predecessor['stages']):
        require(new['mask']==[mapping.index(c) for c in old['mask']],'exact surviving predecessor masks')
        for u,v in zip(new['units'],old['units']):
            require(large['X'][u]==[Q(predecessor['X'][v][c]) for c in mapping],'exact inherited full columns')
            require(large['Y'][u]==[Q(predecessor['Y'][v][c]) for c in mapping],'exact inherited full rows')
    tn,pn=formal_root_invoice(large);to,po=formal_root_invoice(predecessor)
    expected_t=to.copy();expected_p=po.copy();expected_t[1]-=208;expected_p[1]-=208
    require(+tn==+expected_t and +pn==+expected_p,'thin/empty-target exact cancellation')
    require(all(tn[r]-pn[r]==to[r]-po[r] for r in set(tn)|set(pn)|set(to)|set(po)),'all signed coefficients identical')
    print('PASS formal invoice: target and paid rank-one counts both decrease by208; no new kappa',flush=True)

    controls=[]
    broken=copy.deepcopy(small);broken['X'][0][0]+=1
    controls.append(must_reject(lambda:check_root(broken),'wrong primal entry'))
    broken=copy.deepcopy(small);broken['full']=[[0,1],[2,3],[6,7]];broken['thin']=[4,5]
    controls.append(must_reject(lambda:check_root(broken),'nonorthogonal reclassification with only two thin units'))
    broken=copy.deepcopy(small);broken['full']=[[0,6],[1,7]]
    controls.append(must_reject(lambda:check_root(broken),'nonconsecutive full pairs'))
    broken=copy.deepcopy(small);broken['stages'][0]['mask'].remove(0)
    controls.append(must_reject(lambda:check_root(broken),'missing support in mask'))
    controls.append(must_reject(lambda:lift(normalize(small),[[Q(1),Q(0)],[Q(0),Q(0)]]),'noncommuting dual matrix'))
    print('PASS negative controls:',', '.join(controls),flush=True)
    print('PASS_PAIRED_ROOT_COMMUTANT')


if __name__=='__main__':main()
