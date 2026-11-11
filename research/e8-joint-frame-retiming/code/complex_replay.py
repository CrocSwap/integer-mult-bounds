# Adapted for heterogeneous centres by icekylinx with Codex assistance.
"""Independent read-back of the serialized local/global instruction stream."""
import copy,gzip,hashlib,importlib.util,json,math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

OUT=Path('split-centres');P=OUT/'GLOBAL-TEMPLATE.json.gz'
ir=json.load(gzip.open(P));c=json.load(gzip.open(OUT/'CANONICAL-WORD.json.gz'))
integration=json.loads((OUT/'INTEGRATION.json').read_text())
assert hashlib.sha256(gzip.decompress(P.read_bytes())).hexdigest()==integration['global_template_sha256']
assert c['ports']==json.load(gzip.open('work/higher-stage-e8/verified/gcert1-e8-retimed.json.gz'))['ports']
v,R,h=c['v'],c['R'],c['h'];n=2*v+R;frames=c['frames']
def contains(a,b):
    for x in a:
        for y in b:
            if x>>(y.bit_length()-1)&1:x^=y
        if x:return False
    return True
def local(events,back):
    rows={('L',r):{r:Q(1)} for r in range(n)}
    norm={('L',r):Q(1) for r in range(n)};prefix=Q(1);cur=c['start'].copy();private={}
    hist=Counter();phases=[];entry=[];exit=[];centers=[];matrix_hash=hashlib.sha256()
    allowed=['zero_frame_precondition','entry_adapters','A','centers','B','final','exit_adapters','full_frame_cleanup','done']
    for event in events:
        tag=event[0]
        if tag=='phase':
            phases.append(event[1]);assert phases==allowed[:len(phases)]
            if event[1]=='A':assert entry==list(enumerate(c['start']))
            if event[1]=='centers':assert all(cur[r]==0 for r in range(v,2*v))
            if event[1]=='full_frame_cleanup':assert cur==c['final'] and exit==list(enumerate(c['final']))
            assert not private
        elif tag=='adapter':
            assert event[3]==(c['start'] if event[1]=='old_to_new' else c['final'])[event[2]]
            (entry if event[1]=='old_to_new' else exit).append((event[2],event[3]))
        elif tag=='climb':
            _,part,r,a,b,rank=event
            assert not private and phases[-1]==part and cur[r]==a
            assert contains(frames[a],frames[b]) and rank==len(frames[b])-len(frames[a])>0
            hist[rank]+=1;cur[r]=b
        elif tag=='center':
            _,k,a,b,rank=event
            assert phases[-1]=='centers' and private=={('C',k):a}
            cf=c['center_frames'][k];cr=len(frames[cf])
            assert (a,b,rank)==((0,cf,cr) if back else (cf,0,cr))
            private['C',k]=b;hist[rank]+=1;centers.append(k)
        elif tag=='scalar':
            _,e,f=event;op=e[0];target=tuple(e[1]);source=tuple(e[2]) if op in ('copy','add') else None
            if target[0]=='C' and op=='clear':
                assert private.get(target,f)==f
                private.pop(target,None)
            else:
                for r in (target,source):
                    if r is None:continue
                    if r[0]=='L':assert cur[r[1]]==f,('common frame',r,cur[r[1]],f)
                    else:
                        if r==target and r not in private:private[r]=f
                        assert private[r]==f
            if op=='clear':rows[target]={};norm[target]=Q(0)
            elif op=='copy':rows[target]=dict(rows[source]);norm[target]=norm[source]
            elif op=='scale':
                q=Q(e[2],e[3]);a,b=abs(q.numerator),q.denominator
                assert a&(a-1)==0 and b&(b-1)==0
                rows[target]={j:q*x for j,x in rows[target].items()};norm[target]*=abs(q)
            else:
                q=Q(e[3],e[4]);a,b=abs(q.numerator),q.denominator
                assert source!=target and b&(b-1)==0
                # Independent symbolic replay of the cleared coefficient work.
                w=0
                for bit in bin(a)[2:]:w=2*w+int(bit)
                assert Q(w,b)*(1 if q>0 else -1)==q
                prefix=max(prefix,Q(a)*norm[source])
                norm[target]=norm.get(target,Q(0))+abs(q)*norm[source]
                row=rows.setdefault(target,{})
                for j,x in list(rows[source].items()):
                    z=row.get(j,Q(0))+q*x
                    if z:row[j]=z
                    else:row.pop(j,None)
            prefix=max(prefix,norm[target])
        else:raise AssertionError(tag)
    assert phases==allowed and centers==list(range(len(c['centers']))) and not private
    assert all(not row for reg,row in rows.items() if reg[0]=='C')
    for r in range(n):
        expected={r:Q(1)}
        if back and r<v:expected[v+r]=Q(-1)
        elif not back and v<=r<2*v:expected[r-v]=Q(1)
        assert rows['L',r]==expected
    # A 192-bit local payload allowance vastly dominates even coefficient work.
    assert prefix<2**192
    return hist,{'all_exact_columns':n,'prefix_l1_upper':str(prefix),
                 'prefix_bits_upper':prefix.numerator.bit_length()-prefix.denominator.bit_length()+1,
                 'charged_payload_bits':192,'private_work_erased':True}

profiles={};checks={}
for name in ('forward','backward'):
    profiles[name],checks[name]=local(ir['local_programs'][name],name=='backward')
    assert dict(profiles[name])=={int(r):z for r,z in c['local_profile'].items()}
    print('independent emitted replay PASS',name,flush=True)
controls=[]
for name,mut in [
    ('wrong_scale',lambda es:next(e for e in es if e[0]=='scalar' and e[1][0]=='scale')[1].__setitem__(2,3)),
    ('missing_center',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='center'))),
    ('wrong_common_frame',lambda es:next(e for e in es if e[0]=='scalar' and e[2]!=0).__setitem__(2,0)),
    ('wrong_child_rank',lambda es:next(e for e in es if e[0]=='climb').__setitem__(5,99)),
]:
    es=copy.deepcopy(ir['local_programs']['forward']);mut(es)
    try:local(es,False)
    except (AssertionError,KeyError):controls.append(name)
    else:raise AssertionError('mutation accepted: '+name)

def global_check(t):
    assert t['live']==12720 and t['physical']==13298
    # Eight data-wire scalar columns, independently recomposed.
    matrix=[[int(i==j) for j in range(8)] for i in range(8)]
    for e in t['recipe']:
        if e['kind']=='local':
            a=2*e['pair'];b=a+1;dst,src,q=(a,b,-1) if e['reverse'] else (b,a,1)
            matrix[dst]=[x+q*y for x,y in zip(matrix[dst],matrix[src])]
        elif e['kind']=='bridge':
            i,j,q=e['dst'],e['src'],e['coefficient']
            matrix[2*i]=[x+q*y for x,y in zip(matrix[2*i],matrix[2*j])]
            matrix[2*j+1]=[x-q*y for x,y in zip(matrix[2*j+1],matrix[2*i+1])]
        else:
            assert e['kind']=='terminal';old=copy.deepcopy(matrix)
            for i in range(4):matrix[2*i]=old[2*i+1];matrix[2*i+1]=[-x for x in old[2*i]]
    assert matrix==[[int(i==j) for j in range(8)] for i in range(8)]
    seen=set();hist=Counter();pairs={e['stage']:e for e in t['recipe'] if e['kind']=='local'}
    for call in t['calls']:
        stage,rep,pair=call['stage'],call['replica'],call['pair']
        assert (stage,rep) not in seen;seen.add((stage,rep))
        assert pair==pairs[stage]['pair']
        assert call['orientation']==('backward' if pairs[stage]['reverse'] else 'forward')
        assert len(call['owners'])==800
        for r,(fam,route) in enumerate(call['owners']):
            if r<240:assert fam==rep*960+(2*pair+r//120)*120+r%120 and route==[1,stage,r%120]
            else:
                z=rep*560+r-240;assert fam==7680+stage*560+z//8 and route==[2,z%8]
        assert len(set((f,tuple(r)) for f,r in call['owners']))==800
        for r,z in profiles[call['orientation']].items():hist[r]+=z
    assert seen=={(s,r) for s in range(9) for r in range(8)}
    for child in t['idle_children']:hist[child['rank']]+=child['replicas']
    assert t['bank_padding']=={'families':list(range(7680,12720)),'axis':72,'child_rank':1}
    hist[1]+=5040
    assert t['cover_final_correction']['families']==[0,12720]
    assert t['cover_final_correction']['charged_calls_per_cover']==12720
    assert t['execution_schedule'][-1]=={'kind':'translate_every_live_family',**{k:v for k,v in t['cover_final_correction'].items() if k!='kind'}}
    assert 73*12720-sum(r*z for r,z in hist.items())==2496
    return hist
H=global_check(ir)
for name,mut in [('missing_padding',lambda t:t['bank_padding']['families'].pop()),
                 ('aliased_owner',lambda t:t['calls'][0]['owners'][241].__setitem__(1,[2,0])),
                 ('missing_cover_phase',lambda t:t['cover_final_correction'].__setitem__('charged_calls_per_cover',0))]:
    t=copy.deepcopy(ir);mut(t)
    try:global_check(t)
    except (AssertionError,KeyError):controls.append(name)
    else:raise AssertionError('global mutation accepted: '+name)
assert dict(H)=={int(r):z for r,z in integration['global_profile'].items()}

def load(name):
    sp=importlib.util.spec_from_file_location('replay_hamming_'+name,Path('work/pr361/code/engines')/(name+'.py'))
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
M,B=load('moment'),load('base_two_moment');b=Q(integration['complex_b']);grid=Q(1,10**18)
assert M.moment(H,73,12720,b,True)[1]<1<M.moment(H,73,12720,b+grid,True)[0]
def other(a):
    lo,hi=B.moment(73,12720,list(H.items()),a)
    l2,h2=B.moment(73,12720,[(1,32*73**2*sum(H.values()))],a)
    return lo+l2/10**16,hi+h2/10**16
assert other(b)[1]<1<other(b+grid)[0]
result={'status':'PASS_INDEPENDENT_NEW_STRUCTURAL_IR_REPLAY',
        'template_sha256':integration['global_template_sha256'],'local':checks,
        'mutation_controls_rejected':controls,'all_eight_global_scalar_columns':True,
        'bank_owners_and_padding_exact':True,'paid_profile':dict(sorted(H.items())),
        'two_rational_moment_engines':True,'complex_b':str(b),
        'next_b_grid_rejected':True,
        'scope':'Independent finite replay; retains the written generic scalar-interface lemma and inherited all-size/analytic assumptions.'}
(OUT/'INDEPENDENT-REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS independent local/global replay and two exact moments',flush=True)
