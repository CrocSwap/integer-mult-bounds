"""Fresh context-bound stage-private m-coordinate completed bank admission (m = 5h = 100 at p = 10).

No saved chart, receipt, physical census or old source tree is consumed.
The fraction-free inverse routine derives from the retained PR197/PR200 bank
checker. Inherited attribution/notices apply. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
p = 10 port (DreamingOfClouds, Anthropic Claude assistance): h, m and the 60 replicas from the cube size and the
plan; the G^-1 residual rows (h-9)a - sum(a) (15a - sum(a) at h = 24); word counts pinned in word-pins.json.
"""
from collections import Counter
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import hashlib,json,struct,time
from bank_template import BankPlan
from word_pins import expect,shape

assert __debug__, 'Do not run bank admission under -O.'
HERE=Path(__file__).resolve().parent

def inverse_integer(a):
    """Fraction-free Gauss-Jordan, returning C,d with aC=Ca=dI."""
    n=len(a);m=[list(row)+[int(i==j)for j in range(n)]for i,row in enumerate(a)]
    previous=1;factors=[]
    for k in range(n):
        pivot=next((i for i in range(k,n)if m[i][k]),None)
        assert pivot is not None,'singular actual bank chart'
        m[k],m[pivot]=m[pivot],m[k]
        if pivot!=k:factors.append(('swap',k,pivot,1,1))
        p=m[k][k]
        if p!=previous:
            ratio=Q(previous,p);factors.append(('scale',k,k,ratio.numerator,ratio.denominator))
        for i in range(n):
            if i==k:continue
            u=m[i][k]
            if u:
                ratio=Q(-u,previous);factors.append(('add',i,k,ratio.numerator,ratio.denominator))
            for j in range(2*n):
                if j==k:continue
                value=p*m[i][j]-u*m[k][j];assert value%previous==0;m[i][j]=value//previous
            m[i][k]=0
        previous=p
    d=m[0][0];assert d and all(m[i][j]==d*int(i==j)for i in range(n)for j in range(n))
    c=[row[n:]for row in m];common=abs(d)
    for row in c:
        for x in row:common=gcd(common,x)
    d//=common;c=[[x//common for x in row]for row in c]
    if d<0:d=-d;c=[[-x for x in row]for row in c]
    return c,d,factors

def residual_rows(C,frame,h):
    """Integer bases (residual, source, outside) of a chart: residual = image of P_end - P_sigma, outside = E-perp.
    G^-1 a is taken up to the positive scalar h-9 (G = I - J/9), as for the plain charts."""
    def perp(a):
        row=[(h-9)*x-sum(a)for x in a];d=gcd(*row);assert d;return [x//d for x in row]
    if not isinstance(frame,tuple):return [perp(a)for a in C.A[frame]],[list(b)for b in C.B[frame]],[]
    sigma,E=frame;Gs=[[Q((h-9)*x-sum(a))for x in a]for a in C.A[sigma]]
    # Solve for combinations of the G-complement of sigma lying in E (A_E . r = 0), exactly over Q.
    M=[[sum(Q(y)*x for y,x in zip(e,g))for g in Gs]for e in C.A[E]];k=len(Gs);piv={}
    for row in M:
        row=list(row)
        for p,b in piv.items():
            if row[p]:c=row[p];row=[x-c*y for x,y in zip(row,b)]
        p=next((i for i,x in enumerate(row)if x),None)
        if p is None:continue
        row=[x/row[p]for x in row]
        for q in list(piv):
            if piv[q][p]:c=piv[q][p];piv[q]=[x-c*y for x,y in zip(piv[q],row)]
        piv[p]=row
    out=[]
    for fr in [i for i in range(k)if i not in piv]:
        lam=[Q(int(i==fr))for i in range(k)]
        for p,b in piv.items():lam[p]=-b[fr]
        r=[sum(l*g[j]for l,g in zip(lam,Gs))for j in range(h)];den=1
        for x in r:den=den*x.denominator//gcd(den,x.denominator)
        r=[int(x*den)for x in r];d=gcd(*r);out.append([x//d for x in r])
    assert len(out)==C.dimf[E]-C.dimf[sigma]
    assert all(sum(x*y for x,y in zip(e,r))==0 for e in C.A[E]for r in out),'residual inside E'
    return out,[list(b)for b in C.B[sigma]],[perp(a)for a in C.A[E]]

def census(context):
    W,C,roles=context['W'],context['C'],context['regs'];h=W.h;assert h==shape()['h']
    assert len(roles)==len(set(roles))==expect('final_physical_R',len(roles)) and roles==sorted(roles)
    assert set(roles)==set(W.phys.values())-set(context['borrow'])-context['removed']
    assert not(set(roles)&set(context['borrow']))
    gauge_frames={role:W.gauge[role]['frame']for role in roles if role in W.gauge}
    expect('final_entrance_ranks',Counter(C.dimf[f]for f in gauge_frames.values()))
    # Early-restored helpers end at E: residual P_E - P_sigma; the chart key is the pair (sigma, E).
    ends=dict(context.get('restored_endpoints',{}))
    assert set(ends)<=set(gauge_frames)
    for role,E in ends.items():
        assert C.sub(gauge_frames[role],E) and C.dimf[E]<h and C.nondeg(E);gauge_frames[role]=(gauge_frames[role],E)
    families={}
    for role in roles:
        f=gauge_frames.get(role)
        rank=h if f is None else C.dimf[f[1]]-C.dimf[f[0]] if isinstance(f,tuple) else h-C.dimf[f]
        families.setdefault(rank,[]).append(role)
    expect('residual_families',{r:len(xs)for r,xs in families.items()})
    return families,gauge_frames

class BankLowerer:
    """Final full-address lowering of the already checked logical IR.

    Scalar/projection/geometry fields are retained byte-for-byte; only stream
    operands change to the proven bank namespaces. Completion discharge is
    checked separately by run(), and no completion opcode is emitted.
    """
    def __init__(self,context,lower):
        families,gauges=census(context)
        self.plan=BankPlan(families,gauges,context['regs']);self.lower=lower
    def iter_stage(self,stage,replica):
        for row in self.lower.iter_stage(stage):yield self.plan.map_stage_row(stage,replica,row)
    def iter_idle(self,which,replica):
        for row in self.lower.iter_idle(which):yield self.plan.map_boundary_row(replica,row)
    def iter_bridges(self,which,replica):
        for row in self.lower.iter_bridges(which):yield self.plan.map_boundary_row(replica,row)
    def iter_exchanges(self,replica):
        for row in self.lower.iter_exchanges():yield self.plan.map_boundary_row(replica,row)
    def phases(self):
        """Each iterator is expanded over all cover classes before next phase."""
        T=self.plan.replicas
        for stage in range(5):
            for replica in range(T):
                yield('helper',stage,replica,lambda s=stage,r=replica:self.iter_stage(s,r))
            if stage in(1,2,4):
                which={1:0,2:1,4:2}[stage]
                for replica in range(T):
                    yield('idle',which,replica,lambda i=which,r=replica:self.iter_idle(i,r))
                    yield('bridge',which,replica,lambda i=which,r=replica:self.iter_bridges(i,r))
        for replica in range(T):yield('terminal_exchange',0,replica,lambda r=replica:self.iter_exchanges(r))

def bind(context,lower):return BankLowerer(context,lower)

def run(context,global_result,lower,progress=lambda text:None):
    begun=time.monotonic();W,C=context['W'],context['C']
    api_pin=hashlib.sha256((HERE/'bank_template.py').read_bytes()).hexdigest()
    families,gauge_frames=census(context);bound=bind(context,lower);plan=bound.plan
    assert lower.W is W and lower.C is C
    h,m,T=W.h,plan.m,plan.replicas;assert plan.h==h and m==5*h and T==60
    # Derive all actual chart bases and exact inverse/factor programs afresh.
    charts=[];maxops=maxnum=maxden=0
    for frame,count in sorted(Counter(gauge_frames.values()).items(),key=lambda x:(isinstance(x[0],tuple),x[0])):
        # G^-1 a up to the positive scalar h-9, G = I - J/9 (15a - sum(a) at h = 24); E-perp rows for restored endpoints
        residual,source,outside=residual_rows(C,frame,h);rank=len(residual)
        sigma=frame[0]if isinstance(frame,tuple)else frame
        assert rank+len(source)+len(outside)==h and len(source)==C.dimf[sigma]
        G=lambda a,b:9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
        assert all(G(a,b)==0 for a in residual for b in source)
        assert all(G(a,b)==0 for a in outside for b in residual+source),'E-perp is orthogonal to E'
        B=list(map(list,zip(*(residual+list(source)+outside))));A,d,ops=inverse_integer(B)
        for L,R in((A,B),(B,A)):
            assert all(sum(x*y for x,y in zip(row,col))==d*int(i==j)for i,row in enumerate(L)for j,col in enumerate(zip(*R)))
        P=[[sum(B[i][k]*A[k][j]for k in range(rank))for j in range(h)]for i in range(h)]
        assert sum(P[i][i]for i in range(h))==d*rank
        assert all(sum(P[i][k]*B[k][j]for k in range(h))==(d*B[i][j]if j<rank else 0)for i in range(h)for j in range(h))
        replay=[list(map(Q,row))for row in B]
        for op,i,j,a,b in ops:
            if op=='swap':replay[i],replay[j]=replay[j],replay[i]
            elif op=='scale':replay[i]=[Q(a,b)*x for x in replay[i]]
            else:
                assert op=='add';replay[i]=[x+Q(a,b)*y for x,y in zip(replay[i],replay[j])]
        assert all(x==int(i==j)for i,row in enumerate(replay)for j,x in enumerate(row))
        maxops=max(maxops,len(ops));maxnum=max(maxnum,max(abs(op[3])for op in ops));maxden=max(maxden,d,max(op[4]for op in ops))
        charts.append(dict(frame=list(frame)if isinstance(frame,tuple)else frame,count=count,residual_rank=rank,basis=B,inverse_numerator=A,inverse_denominator=d,factors=ops))
    assert len(charts)==expect('final_charts',len(charts)) and max(maxnum,maxden)<2**80 and maxops==expect('max_chart_factors',maxops)
    progress('Rebuilt '+str(len(charts))+' exact actual gauge charts')
    # Match each consumed completion to one actual independent entrance.
    expected=[];ends=context.get('restored_endpoints',{});endrows=[]
    for j,role in enumerate(context['regs']):
        f=gauge_frames.get(role,lower.ZERO);end=lower.FULL
        if isinstance(f,tuple):f,end=f
        assert lower.initial[2*W.v+j]==f
        if role in gauge_frames:expected.append((4*W.v+j,f,C.dimf[f]));endrows.append(end)
    assert list(lower.entrances)==expected and len(expected)==expect('final_entrances',len(expected))
    completions=list(lower.iter_completions())
    assert completions==[(6,family,-1,end,5*(a+h-C.dimf[end]),f,-1,0)for(family,f,a),end in zip(expected,endrows)]
    assert sum(end!=lower.FULL for end in endrows)==len(ends)
    removed=Counter(row[4]for row in completions)
    expect('final_entrance_ranks',Counter(a for _,_,a in expected));expect('removed_completion_histogram',dict(removed))
    H=Counter({int(r):n for r,n in global_result['paid_histogram'].items()})
    assert sum(H.values())==global_result['paid_calls']
    for r,n in removed.items():
        assert H[r]>=n;H[r]-=n
        if not H[r]:del H[r]
    assert max(H)==shape()['idle'][2] and sum(H.values())==expect('banked_calls',sum(H.values())) and sum(r*n for r,n in H.items())==expect('banked_rank_mass',sum(r*n for r,n in H.items()))
    literal=Counter({r:T*n for r,n in H.items()})
    assert m*plan.live_families-sum(r*n for r,n in literal.items())==T*shape()['deficit']
    # Independently enumerate each physical role/replica/stage slot.
    incidence=hashlib.sha256();assignments=0;normalizers_checked=set();endpoint_controls=[]
    for stage in range(5):
        used=Counter();bank=0;assigned=set()
        outside=next(j for j in range(m)if not h*stage<=j<h*(stage+1))
        for pattern,(widths,count)in enumerate(plan.patterns):
            offset=0;witnesses=[]
            for block,rank in enumerate(widths):
                original=list(range(h*stage,h*stage+rank));target=list(range(offset,offset+rank))
                src=original+[j for j in range(m)if j not in original];dst=target+[j for j in range(m)if j not in target];pi=dict(zip(src,dst))
                witnesses.append((pi[outside],block+1));offset+=rank
            assert len(set(witnesses))==len(widths)
            if stage==0:
                offsets=[sum(widths[:b])for b in range(len(widths))]
                def endpoint(blocks):
                    state=list(range(2*m))
                    for b in blocks:
                        for j in range(offsets[b],offsets[b]+widths[b]):state[j],state[m+j]=state[m+j],state[j]
                    return state
                blocks=list(range(len(widths)));full=list(range(m,2*m))+list(range(m))
                assert endpoint(blocks)==full and endpoint(blocks+blocks[::-1])==list(range(2*m))
                assert endpoint(blocks[:-1])!=full and endpoint(blocks+[0])!=full
                endpoint_controls.append(dict(pattern=pattern,forward_columns=2*m,inverse_columns=2*m,omitted_rejected=True,repeated_rejected=True))
            for b in range(bank,bank+count):
                offset=0
                for block,rank in enumerate(widths):
                    q=used[rank];role=families[rank][q//T];replica=q%T;used[rank]+=1
                    assert(role,replica)not in assigned;assigned.add((role,replica))
                    a=plan.assignment(stage,replica,role);frame=gauge_frames.get(role)
                    assert a==dict(family=plan.data_families+stage*plan.banks_per_stage+b,stage_bank=b,pattern=pattern,block=block,offset=offset,rank=rank,frame=frame,scalar=block+1)
                    key=stage,pattern,block,frame
                    if key not in normalizers_checked:
                        N=plan.normalizer(stage,replica,role)
                        assert N['unit_column_witness']==witnesses[block]and N['inverse_chart_frame']==frame and N['chart_window']==stage
                        assert N['permutation'][h*stage:h*stage+rank]==tuple(range(offset,offset+rank))
                        normalizers_checked.add(key)
                    incidence.update(f'{stage},{pattern},{role},{replica},{b},{block},{offset},{rank}\n'.encode())
                    assignments+=1;offset+=rank
                assert offset==m
            bank+=count
        assert bank==plan.banks_per_stage and len(assigned)==T*len(context['regs'])and used=={r:T*len(xs)for r,xs in families.items()}
    assert assignments==5*T*len(context['regs'])
    progress('Matched all '+str(assignments)+' literal bank assignments')
    namespace=hashlib.sha256();collisions=0
    for stage in range(5):
        for replica in range(T):
            addresses=[plan.local_address(stage,replica,i)for i in range(plan.local_work+1)]
            assert len(set(addresses))==len(addresses)and addresses[-1]==(plan.work_family,('external_work',0))
            assert all(f<plan.live_families for f,route in addresses[:-1])
            collisions+=len(addresses)-len({f for f,route in addresses})
            for f,route in addresses:namespace.update(f'{stage},{replica},{f},{route}\n'.encode())
    expect('family_collisions',collisions)
    # Bind every actual logical operand and mathematical field to the callable
    # address substitution once per stage. The300 injective namespace maps
    # above then instantiate all sixty replicas without replaying scalar algebra.
    stream=struct.Struct('<8i');stage_checks=[];actual_helper_uses=set();paid=Counter()
    for stage in range(5):
        digest=hashlib.sha256();rows=0;stage_paid=Counter();kinds=Counter()
        # Full addresses indexed by the original logical family; wrappers use
        # exactly this tested local inverse and namespace construction.
        addresses={}
        for local in range(plan.local_work+1):
            family=4*W.v+len(context['regs'])if local==plan.local_work else plan.active[stage][0]*W.v+local if local<W.v else plan.active[stage][1]*W.v+local-W.v if local<2*W.v else 4*W.v+local-2*W.v
            assert plan.local_from_logical_family(stage,family)==local
            addresses[family]=plan.local_address(stage,0,local)
        for row in lower.iter_stage(stage):
            op,a,b,c,f,z,s,rev=row;assert s==stage and rev==int(stage in(1,3))
            mapped=plan.map_stage_row(stage,0,row)
            assert mapped==(op,addresses[a],addresses[b]if op in(1,2)else b,c,f,z,s,rev)
            for family in([a,b]if op in(1,2)else[a]):
                if 4*W.v<=family<4*W.v+len(context['regs']):actual_helper_uses.add(family-4*W.v)
            if op==0 and f:stage_paid[f]+=1
            digest.update(stream.pack(*row));rows+=1;kinds[op]+=1
        assert stage_paid==Counter({int(r):n for r,n in lower.ns['result']['paid_histogram'].items()})
        paid.update(stage_paid)
        stage_checks.append(dict(stage=stage,records=rows,logical_operand_binding_sha256=digest.hexdigest(),opcode_counts=dict(kinds),all_actual_operands_mapped=True))
    assert actual_helper_uses==set(range(len(context['regs'])))
    for which in range(3):
        for row in lower.iter_idle(which):
            mapped=plan.map_boundary_row(0,row);assert mapped[0]==4;paid[row[4]]+=1
        for row in lower.iter_bridges(which):assert plan.map_boundary_row(0,row)[0]==5
    exchanges=sum(1 for row in lower.iter_exchanges()if plan.map_boundary_row(0,row)[0]==7)
    assert exchanges==2*W.v and paid==H
    phases=[(kind,stage,replica)for kind,stage,replica,fn in bound.phases()]
    assert len(phases)==12*T and sum(kind=='helper'for kind,s,r in phases)==5*T
    assert all(phases.index(('idle',which,r))<phases.index(('bridge',which,r))for which in range(3)for r in range(T))
    controls=[]
    try:plan.map_boundary_row(0,completions[0])
    except AssertionError:controls.append('silent completion discharge')
    else:raise AssertionError('completion passed address mapper')
    assert hashlib.sha256((HERE/'bank_template.py').read_bytes()).hexdigest()==api_pin
    factors=maxops+(m-1)+m;K=2*5*T*((plan.live_families-1)+len(context['regs'])*m*factors)
    assert factors==expect('normalizer_factor_bound',factors) and K==expect('extra_selector_calls',K)<2**40
    result=dict(status='PASS_FRESH_CONTEXT_BOUND_COMPLETE_BANKS_AND_CALLABLE_LOWERING',
        all_assignments_match=True,all_logical_helpers_bound=True,independent_completions_removed=len(completions),
        removed_completion_histogram=dict(removed),literal_paid_histogram=dict(sorted(literal.items())),literal_stock=plan.live_families,
        normalized_stock=str(Q(plan.live_families,T)),physical_replicas=T,bank_families=5*plan.banks_per_stage,data_families=plan.data_families,
        assignments=assignments,incidence_sha256=incidence.hexdigest(),charts=len(charts),
        chart_sha256=hashlib.sha256(json.dumps(charts,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        max_chart_factors=maxops,max_factor_numerator=maxnum,max_denominator=maxden,normalizer_factor_bound=factors,
        conservative_extra_selector_calls=K,distinct_actual_normalizers=len(normalizers_checked),
        full_namespaces_checked=5*T,namespace_sha256=namespace.hexdigest(),intentional_family_collisions=collisions,bank_patterns=[[list(w),c]for w,c in plan.patterns],
        local_instruction_bindings=stage_checks,endpoint_checks=endpoint_controls,phase_schedule=phases,
        completions_discharged_by='Each stage-private bank partitions all '+str(m)+' coordinates; all '+str(2*m)+' arbitrary-dirty address columns and inverse checked.',
        inherited_geometry='Helper originalclass d*tau_i maps to bank d*tau_i*N^-1. N conjugates its actual residual in H_i into the assigned coordinate block. Data routes and boundary projectors remain PR234s.',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),api_sha256=api_pin,
        rejected_controls=controls,seconds=time.monotonic()-begun)
    bank_keys=('literal_stock','normalized_stock','physical_replicas','bank_families','data_families','assignments',
        'incidence_sha256','charts','chart_sha256','max_chart_factors','max_factor_numerator','max_denominator',
        'normalizer_factor_bound','conservative_extra_selector_calls','distinct_actual_normalizers','endpoint_checks')
    banks={k:result[k]for k in bank_keys};banks['status']='PASS_FRESH_ACTUAL_CHARTS_AND_COMPLETE_BANKS'
    banks.update(physical_roles=len(context['regs']),banks_total=5*plan.banks_per_stage)
    return dict(banks=banks,banked_result=result)
