"""Independently authored shared-donor validation; upstream is inert JSON only.

The all-column comparison is a compositional F2 matrix certificate using the
inherited old complete-word decoder, not a replay of the upstream producer.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import base64,gzip,hashlib,json,time
HERE=Path(__file__).resolve().parent
import source_data as sd
import check_coretime
import kernel_witness
CANDIDATE=kernel_witness.PATH

def verify_inputs():
    sd.verify_all()
    kernel_witness.load()

def read(name):
    if name=='coretime-candidate12.json':
        return check_coretime.run(minimal=True)
    aliases={'graph.json':'gen5bit/selected/bit/graph_p12.json'}
    return sd.read_json(aliases.get(name,name.replace('__','/').removesuffix('.base64')))

def echelon(A):
    A=[[Q(x)for x in row]for row in A];rank=0;piv=[]
    for j in range(24):
        p=next((i for i in range(rank,len(A))if A[i][j]),None)
        if p is None:continue
        A[rank],A[p]=A[p],A[rank];d=A[rank][j];A[rank]=[x/d for x in A[rank]]
        for i in range(len(A)):
            if i!=rank and A[i][j]:
                d=A[i][j];A[i]=[x-d*y for x,y in zip(A[i],A[rank])]
        piv.append(j);rank+=1
    return A[:rank],piv

def nullspace(B):
    R,piv=echelon(B);out=[]
    for j in range(24):
        if j in piv:continue
        v=[Q(0)]*24;v[j]=1
        for i,k in enumerate(piv):v[k]=-R[i][j]
        out.append(v)
    return out

def run(mutation=None, selection="union34"):
    verify_inputs();start=time.monotonic();w=read('gen5bit__selected__bit__word_p12.json.gz.base64')
    f={int(k):v for k,v in read('gen5bit__selected__bit__frames_p12.json.gz.base64')['frames'].items()}
    graph=read('graph.json');ks=read('kernel-selection.json');desc=read('descent-selection.json')
    oldrest=read('restore-selection.json')['entries'];sinks=read('sink-selection.json')['sinks'];core=read('coretime-candidate12.json')['candidates']
    candidates=json.loads(CANDIDATE.read_text())['best_candidates']
    lines={'union34':[[6,7],[2,3]],'union72':[[6,7],[16,17],[2,3]],'line6':[[6,7]],'line16':[[16,17]],'line2':[[2,3]]}[selection]
    chosen=[z for z in candidates if z['line']in lines]
    assert len(chosen)==len(lines)
    families=[dict(z,line=c['line'])for c in chosen for z in c['relations']if not(selection=='union72' and c['line']==[6,7] and z['pivot']in(10859,10861))]
    if mutation=='bad_relation':families[0]=dict(families[0],donors=families[0]['donors'][1:])
    P={z['pivot']for z in families};D={d for z in families for d in z['donors']};M=P|D
    counts={'union34':(34,43),'union72':(72,93),'line6':(28,37),'line16':(40,50),'line2':(6,6)}
    assert (len(P),len(D))==counts[selection] and not P&D
    removed={b for a,b in w['pairs']};reused={a for a,b in w['pairs']};regs=sorted(set(range(17160))-removed)
    physical={r:3520+i for i,r in enumerate(regs)};sid=lambda r:physical[r]
    assert not M&(removed|reused|{z['role']for z in w['gauges']}|{z['role']for z in sinks}|set(w['sources'].values()))
    oldentries=[dict(pivot=z['a'],donors=[z['b']])for z in ks['pairs']]+[dict(pivot=z['pivot'],donors=z['donors'])for z in ks['families']]
    oldmembers={s for z in oldentries for s in[z['pivot']]+z['donors']}
    assert not {sid(r)for r in M}&oldmembers
    assert not {sid(r)for r in M}&{s for z in desc['entries']for s in z['scalar'][:2]}
    assert not M&{z[k]for z in core for k in('helper','donor','blocker')}
    assert not {sid(r)for r in M}&{z['helper']for z in oldrest}
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase]
    # Integer adjoint coefficients, reduced only at the declared bit interface.
    adj=[{}for _ in range(17160)]
    for root,r in zip(graph['roots'],w['rootroles']):
        for t in root['targets']:adj[r][t]=adj[r].get(t,0)+1
    for index in reversed(order):
        a,b,_=w['ops'][index]
        for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
    response=[sum(1<<t for t,c in row.items()if c%2)for row in adj]
    # Independent cross-check against every frozen source relation.
    inverse={s:r for r,s in physical.items()}
    for z in oldentries:
        value=response[inverse[z['pivot']]]
        for d in z['donors']:value^=response[inverse[d]]
        assert not value
    for z in families:
        value=response[z['pivot']]
        for d in z['donors']:value^=response[d]
        assert not value,('response relation fails',z['pivot'])
        assert response[z['pivot']]
    # Independently bind the common prefix and existing content-addressed cuts.
    gauge_roles={z['role']for z in w['gauges']};lastread={};read_count=0;lastglobal=None
    for r in range(17160):
        if r in gauge_roles:continue
        for t,c in adj[r].items():
            if c%2:
                lastread[r]=(read_count,[1760+t,sid(r),-c]);read_count+=1;lastglobal=lastread[r]
    assert read_count==648088 and lastglobal==(648087,[3503,16719,-1])
    cut_checks=0
    for z in ks['pairs']+ks['families']:
        p=z.get('pivot',z.get('a'));ds=z.get('donors',[z.get('b')])
        expected=max((lastread[inverse[r]]for r in[p]+ds),key=lambda x:x[0])[1]
        assert expected==z['cut_read'];cut_checks+=1
    target_cut=read('target-selection.json')['cut_record'];assert target_cut==696719 and read_count<target_cut
    portable=kernel_witness.load()['portable']
    assert portable['last_plain_read']==dict(record=lastglobal[0],scalar=lastglobal[1])
    if selection in('union34','union72'):
        variant=portable['variants']['two_lines'if selection=='union34'else'three_lines_trimmed']
        assert {(z['pivot'],tuple(z['donors']))for z in variant['entries']}=={(sid(z['pivot']),tuple(sid(d)for d in z['donors']))for z in families}
        for z in variant['entries']:
            roles=[inverse[r]for r in[z['pivot']]+z['donors']]
            last=max((lastread[r]for r in roles),key=lambda x:x[0])
            assert z['cut_read']==last[1]and z['base_prefix_cut_record']==last[0]
    # New common entrances and old required chronological frames.
    line_of={}
    for z in families:
        for r in[z['pivot']]+z['donors']:
            assert r not in line_of or line_of[r]==z['line'];line_of[r]=z['line']
    anns={};checked=set()
    def ann(frame):
        if frame not in anns:
            data=f[frame];anns[frame]=data['a']if'a'in data else nullspace(data['b'])
        return anns[frame]
    def sub(a,b):
        if a==b:return True
        if(a,b)not in checked:
            assert len(echelon(ann(a)+ann(b))[1])==len(ann(a)),('old nonnested',a,b)
            checked.add((a,b))
        return True
    paths={r:[]for r in M}
    def use(r,frame):
        if r in M and(not paths[r]or paths[r][-1]!=frame):paths[r].append(frame)
    for index in order:
        a,b,_=w['ops'][index];use(a,w['op_frame'][index]);use(b,w['op_frame'][index])
    for index,(root,r)in enumerate(zip(graph['roots'],w['rootroles'])):
        if r in M:assert root['kind']=='side'
        use(r,w['root_frame'][index])
    oldrestore_donors=[]
    for z in oldrest:
        if z['donor']in inverse and inverse[z['donor']]in M:
            r=inverse[z['donor']];oldrestore_donors.append(r)
            # The only inserted path here is a proper join after every root;
            # validate it from the actual old restoration basis.
            frame=('REST',z['helper']);anns[frame]=nullspace(z['basis'])
            f[frame]={'dim':z['rank']};use(r,frame)
    for r in M:use(r,w['full_frame'])
    H=Counter();pathrows=[]
    for r,frames in sorted(paths.items()):
        assert frames;d=f[frames[0]]['dim'];i,j=line_of[r]
        v=[int(k==i)-int(k==j)for k in range(24)]
        if mutation=='bad_entrance' and r==min(M):v=[int(k==0)for k in range(24)]
        assert all(sum(a*b for a,b in zip(row,v))==0 for row in ann(frames[0])),('entrance outside first frame',r)
        # v^T(9I-J)v =18, so nondegenerate over Q and each retained large prime.
        gram=9*sum(x*x for x in v)-sum(v)**2;assert gram==18
        for a,b in zip(frames,frames[1:]):sub(a,b)
        H[d]-=1
        if d>1:H[d-1]+=1
        if r in D:H[1]+=1
        pathrows.append(dict(role=r,stream=sid(r),kind='pivot'if r in P else'donor',line=[i,j],first_dimension=d,old_frames=frames,
            old_dimensions=[f[z]['dim']for z in frames],new_initial_dimension=1 if r in P else 0,
            new_paid_entrance_dimensions=[d-1]if r in P else[1,d-1]))
    H={r:c for r,c in sorted(H.items())if c}
    expected={'union34':{1:43,2:75,3:-75,5:2,6:-2},'union72':{1:93,2:144,3:-144,4:19,5:-17,6:-2}}
    if selection in expected:assert H==expected[selection],H
    assert sum(r*c for r,c in H.items())==-len(P)
    # Full formal matrix composition. Q is precisely the selected dirty-column
    # part of the common prefix. All other prefix operations commute with the
    # selected shear by the checked no-touch/disjoint-support hypotheses.
    n=3520+len(regs)
    def prefix(skip):
        out=[]
        for r in sorted(M-skip):
            for t,c in adj[r].items():
                if c%2:out.append((1760+t,sid(r)))
        return out
    setup=[(sid(d),sid(z['pivot']))for z in families for d in z['donors']]
    oldprefix=prefix(set());newprefix=prefix(P)
    # Baseline remainder is U*Q^{-1}, where U is the inherited exact decoder.
    # U adds source[t] to target[t] and fixes every dirty helper, so it commutes
    # with setup. This explicit all-column representative proves the identity.
    U=[(1760+t,t)for t in range(1760)]
    tail=list(reversed(oldprefix))+U
    def evaluate(events):
        rows=[1<<i for i in range(n)]
        for a,b in events:rows[a]^=rows[b]
        return rows
    old=oldprefix+tail;new=newprefix+setup+tail+list(reversed(setup))
    if mutation=='omit_restore':new=newprefix+setup+tail+list(reversed(setup))[1:]
    if mutation=='omit_setup':new=newprefix+setup[1:]+tail+list(reversed(setup))
    assert evaluate(old)==evaluate(new),'formal all-column composition failed'
    assert evaluate(list(reversed(old)))==evaluate(list(reversed(new)))
    # Since K^2=0 all setup factors commute, and inverse order is harmless.
    assert evaluate(setup+list(reversed(setup)))==[1<<i for i in range(n)]
    indegree=Counter(d for z in families for d in z['donors'])
    return dict(status='PASS_SHARED_DONOR_CHANGED_STAGE_COMPOSITION',source_head='5f6bd3fbc0e6796dd31263cef1f06dc968186f64',
        selection=selection,chosen_lines=[c['line']for c in chosen],pivots=len(P),distinct_donors=len(D),members=len(M),setup_adds=len(setup),restore_adds=len(setup),
        donor_multiplicity_histogram=dict(Counter(indegree.values())),max_donor_multiplicity=max(indegree.values()),
        frozen_response_relations_reproduced=len(oldentries),frozen_literal_cut_read_triples_reproduced=cut_checks,
        common_prefix_plain_reads=read_count,last_plain_read=lastglobal[1],target_prefix_setup_record=target_cut,
        common_cut='Immediately before first source injection, after all plain compensation reads and all old kernel setups',
        all_column_dimension=n,field='F2',
        arbitrary_source_target_dirty_inputs=True,formal_forward_and_inverse_equal=True,
        prefix_compensation_reads_removed=sum(response[r].bit_count()for r in P),
        source_compensation_integer_coefficient_max=max(abs(c)for r in P for c in adj[r].values()),
        common_line_gram=18,exact_containments=len(checked),old_restoration_donor_overlaps=oldrestore_donors,
        local_paid_histogram_delta=H,residual_family_delta={24:-len(P),23:len(P)},paths=pathrows,
        candidate_sha256=hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),seconds=time.monotonic()-start,
        scope='Compositional changed-stage proof assuming the inherited complete bit decoder and a literal common prefix before any selected helper non-compensation use. The independently checked response matrix, disjoint supports and rational helper paths certify the algebra and paid demand changes. The literal common-cut witness is independently reproduced. Bank allocation and global inherited compiler hypotheses are separate obligations; the scalar payload bound is checked by the companion checker. No upstream code executed.')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    import sys
    selection=sys.argv[1]if len(sys.argv)>1 else'union34'
    result=run(selection=selection)
    print(json.dumps({k:v for k,v in result.items()if k!='paths'},indent=2))
