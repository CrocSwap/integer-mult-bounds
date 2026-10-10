"""Fresh context-bound stage-private120-coordinate completed bank admission.

No saved chart, receipt, physical census or old source tree is consumed.
The fraction-free inverse routine derives from the retained PR197/PR200 bank
checker. Inherited attribution/notices apply. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import hashlib,json,struct,time
from bank_template import BankPlan

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

def census(context):
    W,C,roles=context['W'],context['C'],context['regs']
    assert len(roles)==len(set(roles))==15886 and roles==sorted(roles)
    assert set(roles)==set(W.phys.values())-set(context['borrow'])-context['removed']
    assert not(set(roles)&set(context['borrow']))
    gauge_frames={role:W.gauge[role]['frame']for role in roles if role in W.gauge}
    assert Counter(C.dimf[f]for f in gauge_frames.values())=={20:2182,21:354,18:16,17:2}
    families={}
    for role in roles:
        rank=24-C.dimf[gauge_frames[role]]if role in gauge_frames else 24
        families.setdefault(rank,[]).append(role)
    assert {r:len(xs)for r,xs in families.items()}=={3:354,4:2182,6:16,7:2,24:13332}
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
        for stage in range(5):
            for replica in range(60):
                yield('helper',stage,replica,lambda s=stage,r=replica:self.iter_stage(s,r))
            if stage in(1,2,4):
                which={1:0,2:1,4:2}[stage]
                for replica in range(60):
                    yield('idle',which,replica,lambda i=which,r=replica:self.iter_idle(i,r))
                    yield('bridge',which,replica,lambda i=which,r=replica:self.iter_bridges(i,r))
        for replica in range(60):yield('terminal_exchange',0,replica,lambda r=replica:self.iter_exchanges(r))

def bind(context,lower):return BankLowerer(context,lower)

def run(context,global_result,lower,progress=lambda text:None):
    begun=time.monotonic();W,C=context['W'],context['C']
    api_pin=hashlib.sha256((HERE/'bank_template.py').read_bytes()).hexdigest()
    families,gauge_frames=census(context);bound=bind(context,lower);plan=bound.plan
    assert lower.W is W and lower.C is C
    # Derive all actual chart bases and exact inverse/factor programs afresh.
    charts=[];maxops=maxnum=maxden=0
    for frame,count in sorted(Counter(gauge_frames.values()).items()):
        residual=[]
        for a in C.A[frame]:
            row=[15*x-sum(a)for x in a];d=gcd(*row);assert d;residual.append([x//d for x in row])
        source=C.B[frame];rank=len(residual)
        assert rank+len(source)==24 and len(source)==C.dimf[frame]
        assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in residual for b in source)
        B=list(map(list,zip(*(residual+list(source)))));A,d,ops=inverse_integer(B)
        for L,R in((A,B),(B,A)):
            assert all(sum(x*y for x,y in zip(row,col))==d*int(i==j)for i,row in enumerate(L)for j,col in enumerate(zip(*R)))
        P=[[sum(B[i][k]*A[k][j]for k in range(rank))for j in range(24)]for i in range(24)]
        assert sum(P[i][i]for i in range(24))==d*rank
        assert all(sum(P[i][k]*B[k][j]for k in range(24))==(d*B[i][j]if j<rank else 0)for i in range(24)for j in range(24))
        replay=[list(map(Q,row))for row in B]
        for op,i,j,a,b in ops:
            if op=='swap':replay[i],replay[j]=replay[j],replay[i]
            elif op=='scale':replay[i]=[Q(a,b)*x for x in replay[i]]
            else:
                assert op=='add';replay[i]=[x+Q(a,b)*y for x,y in zip(replay[i],replay[j])]
        assert all(x==int(i==j)for i,row in enumerate(replay)for j,x in enumerate(row))
        maxops=max(maxops,len(ops));maxnum=max(maxnum,max(abs(op[3])for op in ops));maxden=max(maxden,d,max(op[4]for op in ops))
        charts.append(dict(frame=frame,count=count,residual_rank=rank,basis=B,inverse_numerator=A,inverse_denominator=d,factors=ops))
    assert len(charts)==411 and max(maxnum,maxden)<2**80 and maxops==423
    progress('Rebuilt411 exact actual gauge charts')
    # Match each consumed completion to one actual independent entrance.
    expected=[]
    for j,role in enumerate(context['regs']):
        f=gauge_frames.get(role,lower.ZERO)
        assert lower.initial[2*W.v+j]==f
        if role in gauge_frames:expected.append((4*W.v+j,f,C.dimf[f]))
    assert list(lower.entrances)==expected and len(expected)==2554
    completions=list(lower.iter_completions())
    assert completions==[(6,family,-1,0,5*a,f,-1,0)for family,f,a in expected]
    removed=Counter(row[4]for row in completions)
    assert removed=={100:2182,105:354,90:16,85:2}
    H=Counter({int(r):n for r,n in global_result['paid_histogram'].items()})
    assert sum(H.values())==global_result['paid_calls']
    for r,n in removed.items():assert H[r]==n;del H[r]
    assert max(H)==50 and sum(H.values())==476590 and sum(r*n for r,n in H.items())==2489740
    literal=Counter({r:60*n for r,n in H.items()})
    assert 120*plan.live_families-sum(r*n for r,n in literal.items())==60*4400
    # Independently enumerate each physical role/replica/stage slot.
    incidence=hashlib.sha256();assignments=0;normalizers_checked=set();endpoint_controls=[]
    for stage in range(5):
        used=Counter();bank=0;assigned=set()
        outside=next(j for j in range(120)if not 24*stage<=j<24*(stage+1))
        for pattern,(widths,count)in enumerate(plan.patterns):
            offset=0;witnesses=[]
            for block,rank in enumerate(widths):
                original=list(range(24*stage,24*stage+rank));target=list(range(offset,offset+rank))
                src=original+[j for j in range(120)if j not in original];dst=target+[j for j in range(120)if j not in target];pi=dict(zip(src,dst))
                witnesses.append((pi[outside],block+1));offset+=rank
            assert len(set(witnesses))==len(widths)
            if stage==0:
                offsets=[sum(widths[:b])for b in range(len(widths))]
                def endpoint(blocks):
                    state=list(range(240))
                    for b in blocks:
                        for j in range(offsets[b],offsets[b]+widths[b]):state[j],state[120+j]=state[120+j],state[j]
                    return state
                blocks=list(range(len(widths)));full=list(range(120,240))+list(range(120))
                assert endpoint(blocks)==full and endpoint(blocks+blocks[::-1])==list(range(240))
                assert endpoint(blocks[:-1])!=full and endpoint(blocks+[0])!=full
                endpoint_controls.append(dict(pattern=pattern,forward_columns=240,inverse_columns=240,omitted_rejected=True,repeated_rejected=True))
            for b in range(bank,bank+count):
                offset=0
                for block,rank in enumerate(widths):
                    q=used[rank];role=families[rank][q//60];replica=q%60;used[rank]+=1
                    assert(role,replica)not in assigned;assigned.add((role,replica))
                    a=plan.assignment(stage,replica,role);frame=gauge_frames.get(role)
                    assert a==dict(family=plan.data_families+stage*plan.banks_per_stage+b,stage_bank=b,pattern=pattern,block=block,offset=offset,rank=rank,frame=frame,scalar=block+1)
                    key=stage,pattern,block,frame
                    if key not in normalizers_checked:
                        N=plan.normalizer(stage,replica,role)
                        assert N['unit_column_witness']==witnesses[block]and N['inverse_chart_frame']==frame and N['chart_window']==stage
                        assert N['permutation'][24*stage:24*stage+rank]==tuple(range(offset,offset+rank))
                        normalizers_checked.add(key)
                    incidence.update(f'{stage},{pattern},{role},{replica},{b},{block},{offset},{rank}\n'.encode())
                    assignments+=1;offset+=rank
                assert offset==120
            bank+=count
        assert bank==plan.banks_per_stage and len(assigned)==60*len(context['regs'])and used=={r:60*len(xs)for r,xs in families.items()}
    assert assignments==4765800
    progress('Matched all4765800 literal bank assignments')
    namespace=hashlib.sha256();collisions=0
    for stage in range(5):
        for replica in range(60):
            addresses=[plan.local_address(stage,replica,i)for i in range(plan.local_work+1)]
            assert len(set(addresses))==len(addresses)and addresses[-1]==(plan.work_family,('external_work',0))
            assert all(f<plan.live_families for f,route in addresses[:-1])
            collisions+=len(addresses)-len({f for f,route in addresses})
            for f,route in addresses:namespace.update(f'{stage},{replica},{f},{route}\n'.encode())
    assert collisions==90
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
    assert len(phases)==720 and sum(kind=='helper'for kind,s,r in phases)==300
    assert all(phases.index(('idle',which,r))<phases.index(('bridge',which,r))for which in range(3)for r in range(60))
    controls=[]
    try:plan.map_boundary_row(0,completions[0])
    except AssertionError:controls.append('silent completion discharge')
    else:raise AssertionError('completion passed address mapper')
    assert hashlib.sha256((HERE/'bank_template.py').read_bytes()).hexdigest()==api_pin
    factors=maxops+119+120;K=2*5*60*((plan.live_families-1)+len(context['regs'])*120*factors)
    assert factors==662 and K==757938545400<2**40
    result=dict(status='PASS_FRESH_CONTEXT_BOUND_COMPLETE_BANKS_AND_CALLABLE_LOWERING',
        all_assignments_match=True,all_logical_helpers_bound=True,independent_completions_removed=len(completions),
        removed_completion_histogram=dict(removed),literal_paid_histogram=dict(sorted(literal.items())),literal_stock=plan.live_families,
        normalized_stock=str(Q(plan.live_families,60)),physical_replicas=60,bank_families=5*plan.banks_per_stage,data_families=plan.data_families,
        assignments=assignments,incidence_sha256=incidence.hexdigest(),charts=len(charts),
        chart_sha256=hashlib.sha256(json.dumps(charts,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        max_chart_factors=maxops,max_factor_numerator=maxnum,max_denominator=maxden,normalizer_factor_bound=factors,
        conservative_extra_selector_calls=K,distinct_actual_normalizers=len(normalizers_checked),
        full_namespaces_checked=300,namespace_sha256=namespace.hexdigest(),intentional_family_collisions=collisions,
        local_instruction_bindings=stage_checks,endpoint_checks=endpoint_controls,phase_schedule=phases,
        completions_discharged_by='Each stage-private bank partitions all120 coordinates; all240 arbitrary-dirty address columns and inverse checked.',
        inherited_geometry='Helper originalclass d*tau_i maps to bank d*tau_i*N^-1. N conjugates its actual residual in H_i into the assigned coordinate block. Data routes and boundary projectors remain PR234s.',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),api_sha256=api_pin,
        rejected_controls=controls,seconds=time.monotonic()-begun)
    bank_keys=('literal_stock','normalized_stock','physical_replicas','bank_families','data_families','assignments',
        'incidence_sha256','charts','chart_sha256','max_chart_factors','max_factor_numerator','max_denominator',
        'normalizer_factor_bound','conservative_extra_selector_calls','distinct_actual_normalizers','endpoint_checks')
    banks={k:result[k]for k in bank_keys};banks['status']='PASS_FRESH_ACTUAL_CHARTS_AND_COMPLETE_BANKS'
    banks.update(gen5_roles=len(context['regs']),banks_total=5*plan.banks_per_stage)
    return dict(banks=banks,banked_result=result)
