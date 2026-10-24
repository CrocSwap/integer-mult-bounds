"""Portable current p16 candidate composition, not an upstream baseline cold replay.

Separates decoded11400 columns, every physical main polynomial coefficient,
and rational local/port/independent-helper job proofs. Streams literal events.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime,timezone
import argparse,gzip,json,time

# All sources and all outputs are supplied explicitly; no research-run paths.
N,V,R,P=11400,111,436,16


def need(v,m):
    if not v:raise ValueError(m)


def digest(data):return sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def polyadd(a,b):
    c=dict(a)
    for k,v in b.items():
        v^=c.get(k,0)
        if v:c[k]=v
        else:c.pop(k,None)
    return c


def shift(a,s):return {k^s:v for k,v in a.items()}


def formal_main(controller):
    rows=[{0:1<<i} for i in range(32)]
    def scalar(program):
        for op,d,s in program:
            if op=='ADD':rows[d]=polyadd(rows[d],rows[s])
            else:
                need(op=='SWAP','binary boundary opcode');rows[d],rows[s]=rows[s],rows[d]
    scalar(controller['boundaries']['right_program'])
    for event in controller['physical_events']:
        op=event[0]
        if op in('LOCAL','QUERY_SHEAR'):
            _,stage,pair,reverse=event;x,y=2*pair,2*pair+1
            if reverse:x,y=y,x
            rows[y]=polyadd(rows[y],shift(rows[x],1))
            if op=='LOCAL':
                s=1<<(stage+1);rows[x]=shift(rows[x],s);rows[y]=shift(rows[y],s)
        elif op=='IDLE':
            _,pair,stages=event;s=sum(1<<(i+1) for i in stages)
            for i in(2*pair,2*pair+1):rows[i]=shift(rows[i],s)
        elif op=='ADD':rows[event[1]]=polyadd(rows[event[1]],rows[event[2]])
        else:
            need(op=='SWAP','actual BIT controller opcode');x,y=event[1:];rows[x],rows[y]=rows[y],rows[x]
    scalar(controller['boundaries']['left_program'])
    expected=[{int(t):1<<i} for i,t in enumerate(controller['diagonal'])]
    need(rows==expected,'all actual main group-polynomial coefficients, not character samples')
    return dict(status='PASS_ALL_MAIN_PHYSICAL_COEFFICIENTS',rows=[{str(k):v for k,v in row.items()} for row in rows],
                coefficient_digest=digest([{str(k):v for k,v in row.items()} for row in rows]),
                scope='Per-port commuting P_q and retained disjoint B_s only; helperP4 jobs are proved separately and not assumed to commute with them.')


def events(records,reverse=False):
    for op,d,s,c,f,z in reversed(records) if reverse else records:
        if op==0:yield [0,d,c if reverse else s,s if reverse else c,f]
        elif op==1:yield [1,d,s,-c if reverse else c,f]
        elif op==(3 if reverse else 2):yield [2,d,s,c,f]
        else:
            need(op==(2 if reverse else 3),'literal COPY inverse opcode')
            yield [3,d,s,c,f]


def matrix_inverse(A):
    n=len(A);w=[list(row)+[Q(i==j) for j in range(n)] for i,row in enumerate(A)]
    for j in range(n):
        p=next(i for i in range(j,n) if w[i][j]);w[j],w[p]=w[p],w[j];a=w[j][j];w[j]=[x/a for x in w[j]]
        for i in range(n):
            if i!=j and w[i][j]:
                a=w[i][j];w[i]=[x-a*y for x,y in zip(w[i],w[j])]
    return [row[n:] for row in w]


def mm(A,B):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]


def port_and_helper_proofs(word,frames,reference):
    I=eye(8);ports=[]
    def project(f):
        B=[[Q(x) for x in row] for row in frames[str(f)]['B']]
        if not B:return [[Q(0)]*8 for _ in range(8)]
        T=list(map(list,zip(*B)));return mm(mm(T,matrix_inverse(mm(B,T))),B)
    for i,ray in enumerate(reference['lines']):
        q=list(map(Q,ray));need(sum(x*x for x in q)==4,'ordered SOURCE rootnorm4')
        p=[[x*y/4 for y in q] for x in q];k=[[I[a][b]-p[a][b] for b in range(8)] for a in range(8)]
        need(project(word['start'][i])==p and project(word['final'][i])==I,'actual candidate SOURCE entranceP/exitI')
        need(not any(any(row) for row in project(word['start'][V+i])) and project(word['final'][V+i])==k,'actual TARGET entrance0/exitK')
        u=[Q(a==0)-q[a]/2 for a in range(8)];norm=sum(x*x for x in u)
        G=I if not norm else [[Q(a==b)-2*u[a]*u[b]/norm for b in range(8)] for a in range(8)]
        A=[row[1:] for row in G];AT=list(map(list,zip(*A)))
        need(mm(list(map(list,zip(*G))),G)==I and [2*row[0] for row in G]==q,'exact orthogonal unchanged mainportchart')
        need(mm(A,AT)==k and mm(AT,A)==eye(7),'typed rank7 complement')
        rho=[p[a]+A[a] for a in range(8)]+[row+[Q(0)]*7 for row in AT]
        local8=[[Q(a==b and a<8) for b in range(15)] for a in range(15)]
        expected=[[p[a][b] if a<8 and b<8 else Q(a==b and a>=8) for b in range(15)] for a in range(15)]
        need(mm(rho,rho)==eye(15) and mm(mm(rho,local8),rho)==expected,'same finite15D wholefiber route, no free dense currentview')
        ports.append(dict(port=i,root=[str(x) for x in q],chart_sha256=digest([[str(x) for x in row] for row in rho])))
    jobs={'independent_roles':[dict(role=i,initial_frame=word['start'][i],job_frame=word['final'][i],rank=frames[str(word['final'][i])]['dim']) for i in range(222,658)]}
    need(all(row['initial_frame']==0 for row in jobs['independent_roles']),'all helpers cold ordinary originals')
    need(len(jobs['independent_roles'])==436,'alloriginal helper roles')
    matchers={}
    for f in sorted({row['job_frame'] for row in jobs['independent_roles']}):
        H=project(f);rank=frames[str(f)]['dim']
        need(mm(H,H)==H and sum(H[i][i] for i in range(8))==rank,'exact helperoutput idempotent rank')
        if rank==8:
            need(H==I,'fullhelpers');continue
        B=[[Q(x) for x in row] for row in frames[str(f)]['B']];A=[[Q(x) for x in row] for row in frames[str(f)]['A']]
        need(rank==4 and len(B)==len(A)==4,'actual image/kernel rank4 basis')
        S=list(map(list,zip(*(B+A))));SI=matrix_inverse(S)
        Q4=[[Q(i==j and i<4) for j in range(8)] for i in range(8)]
        need(mm(mm(S,Q4),SI)==H,'explicit image+kernel output job matcher')
        matchers[str(f)]=dict(rank=rank,projector=[[str(x) for x in row] for row in H],S=[[str(x) for x in row] for row in S],S_inverse=[[str(x) for x in row] for row in SI])
    need(len(matchers)==3,'three distinct actual rank4 helperjobs')
    return dict(ports=ports,matchers=matchers,all_f='Every head projector/matcher embeds in one final ambient and tensorsI_f; use retained C_Nf for the reversed tail, not a runtime relabeling.',
                helper_cover='Helpers are independent fields at the localinvocation cover rowh, not per-port-routed main fields. No rho_q is silently applied to a helperjob.',
                matcher_direction='Stored S satisfies S Q4 S^-1=H4. To use childH4 as canonicalparentQ4, route input wholefiber g->g S^-1, finish wholeunit, undo route. For arbitrary parentP use B_P B_H4^-1.',
                partial_job_routes='72 output roles need wholefiber matcher/inverse when used by the finite compiler:144 positive fixed routes, no extra input/output credit.')


def build(repo_root, local_dir, out):
    repo_root,local_dir,out=map(Path,(repo_root,local_dir,out))
    out.mkdir(parents=True,exist_ok=True)
    need(not any(out.iterdir()),'fresh GLOBAL output directory required')
    SOURCE,LOCAL,HERE=repo_root,local_dir,out
    started=time.process_time();cp=SOURCE/'research/query-thinned-controllers/BIT-CONTROLLER.json'
    need(sha256(cp.read_bytes()).hexdigest()=='39ac84fb848b908f7ba051fae4556d507900c421dc5d23501a9c0cb1d61fd08d','exact current p16controller pin')
    controller=json.loads(cp.read_bytes());thick=controller['invoice']['thick_stages']
    need(len(thick)==18 and len(set(thick))==18,'actual thickstage roster')
    active_embedding=[dict(stage=s,kind='central K_q=I8-P_q' if j==0 else 'fresh orthogonal rank7 B_s',
                           active_block=j,axes=list(range(8)) if j==0 else list(range(8+7*(j-1),8+7*j))) for j,s in enumerate(thick)]
    need(max(a for row in active_embedding for a in row['axes'])==126,'actual127-axis injective thin-stage deletion')
    wpath=LOCAL/'WORD.json.gz';need(sha256(gzip.decompress(wpath.read_bytes())).hexdigest()=='6f8516694bd0067897e91311fb16a749eea8fdd2eb3761bfa3f8eb2740d5c6a6','actual partialLOCAL canonical content pin')
    word=json.loads(gzip.decompress(wpath.read_bytes()));fpath=SOURCE/'research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json'
    need(sha256(fpath.read_bytes()).hexdigest()=='d006b3bfe0c04afecfea7aecfa59dfe4298b99501c70da3938e40289bc2f5010','exact current frame source')
    refpath=SOURCE/'research/kappa-rebuild/bit/sources/pr589-regenerated/WORD.json.gz'
    need(sha256(refpath.read_bytes()).hexdigest()=='e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f','exact current reference WORD')
    frames=json.loads(fpath.read_bytes())['frames'];reference=json.loads(gzip.decompress(refpath.read_bytes()))
    formal=formal_main(controller);binding=port_and_helper_proofs(word,frames,reference)
    values=[1<<i for i in range(N)]+[0];versions=[0]*(N+1);norm=[1]*N+[0]
    peak=1;calls=[];owners=[];profile=Counter();counts=Counter();private_episodes=[];event_index=0
    private=N;stage_index={s:i for i,s in enumerate(thick)}
    need(32*V+18*R==N,'no ghost or unallocated helper columns')
    stream_hash=sha256();zstream=gzip.GzipFile(filename=str(HERE/'EXPANDED-PROGRAM.jsonl.gz'),mode='wb',mtime=0)
    def emit(e):
        nonlocal event_index
        data=(json.dumps(e,separators=(',',':'))+'\n').encode();stream_hash.update(data);zstream.write(data);event_index+=1;counts[e[0]]+=1
    def add(d,s,c=1,kind='ADD',meta=None):
        nonlocal peak
        need(d!=s and 0<=d<=N and 0<=s<=N,'global owner ADD')
        values[d]^=values[s];versions[d]+=1;norm[d]+=abs(c)*norm[s];peak=max(peak,norm[d])
        emit([kind,d,s,c,meta])
    def swap(d,s,meta=None):
        # True F2 swap, three paid aligned XORs, no free FIELD/INDEX exchange.
        add(d,s,meta=meta);add(s,d,meta=meta);add(d,s,meta=meta)
    def boundary(program,label):
        for op,d,s in program:
            for port in range(V):
                if op=='ADD':add(d*V+port,s*V+port,meta=label)
                else:need(op=='SWAP','boundarytype');swap(d*V+port,s*V+port,meta=label)
    boundary(controller['boundaries']['right_program'],'RIGHT_BOUNDARY')
    for event in controller['physical_events']:
        op=event[0]
        if op=='LOCAL':
            _,stage,pair,reverse=event;need(stage in stage_index,'no helpers at thin stage')
            base=32*V+stage_index[stage]*R
            fields=list(range(base,base+R));need(all(values[i]==1<<i for i in fields),'fresh arbitrary helperbank, not zeros')
            owners.append(dict(stage=stage,begin=base,end=base+R,original_fields=R,cover='independent wholefiber at localh',helper_jobs={'4':4,'8':432}))
            x,y=2*pair,2*pair+1
            if reverse:x,y=y,x
            sx=[values[x*V+i] for i in range(V)];sy=[values[y*V+i] for i in range(V)]
            def owner(r):
                if r==658:return private
                if r<222:
                    bank=x if r<V else y;return bank*V+r%V
                return base+r-222
            # Actual fixed route symbols, not merely an invoice count. Their
            # lowering is the inherited paid wholefiber route, not a dense
            # transform of an uncovered ARRAY. No lease crosses either route.
            if stage:
                for bank in(x,y):
                    for port in range(V):
                        role=bank*V+port;versions[role]+=1
                        emit(['PAID_PORT_ROUTE',stage,role,port,'ENTRY',stage_index[stage]])
            state=list(word['final'] if reverse else word['start'])+[None];opened=None;begin=None;localprofile=Counter();qcount=0
            for e in events(word['records'],reverse):
                kind,d,s,c,f=e;gd=owner(d)
                if kind==0:
                    need(opened is None and state[d]==s,'wholecall MOVE/liveprivate history')
                    state[d]=c;profile[f]+=1;localprofile[f]+=1;versions[gd]+=1;qcount+=1
                    emit(['LOCAL_QUERY',stage,gd,s,c,f,reverse])
                elif kind==1:
                    gs=owner(s);need(state[d]==state[s]==f and d!=opened,'actualcallee commonFRAME ADD')
                    need(s!=658 or opened is not None,'liveprivate READ')
                    add(gd,gs,c,'LOCAL_ADD',[stage,f,reverse])
                elif kind==2:
                    need(s==658 and opened is None and not values[private] and state[658] is None,'one ownedprivate zero')
                    need(state[d]==c and f==0 and frames[str(c)]['dim']==7,'proper COPYcurrentSOURCE frame7')
                    values[private]=values[gd];norm[private]=norm[gd];state[658]=0;opened=d;begin=event_index
                    snapshot=versions[gd];profile[7]+=1;localprofile[7]+=1
                    emit(['LOCAL_COPY_QUERY',stage,gd,private,c,0,7,reverse])
                else:
                    need(kind==3 and s==658 and opened==d and state[d]==c and state[658]==f,'ownedERASE currentframe')
                    need(values[private]==values[gd] and versions[gd]==snapshot,'actualoriginal immutable throughERASE')
                    private_episodes.append(dict(kind='LOCAL',stage=stage,source=gd,source_version=snapshot,begin=begin,end=event_index))
                    values[private]=norm[private]=0;state[658]=None;opened=None
                    emit(['LOCAL_PAID_CLEAR',stage,gd,private,c,f,reverse])
            need(opened is None and not values[private] and state[:658]==list(word['start'] if reverse else word['final']),'completecall returnsall endpoints/private')
            need(all(values[x*V+i]==sx[i] and values[y*V+i]==sy[i]^sx[i] for i in range(V)),'actual main scalarinterface, arbitrary current inputs')
            need(all(values[i]==1<<i for i in fields),'all436 helperinitialDIRTY columns independent at output')
            if stage:
                for bank in(x,y):
                    for port in range(V):
                        role=bank*V+port;versions[role]+=1
                        emit(['PAID_PORT_ROUTE',stage,role,port,'INVERSE_RETURN',stage_index[stage]])
            calls.append(dict(stage=stage,pair=pair,reverse=reverse,helper_owner_begin=base,profile=dict(sorted(localprofile.items())),MOVE_queries=qcount,COPY_episodes=9))
        elif op=='QUERY_SHEAR':
            _,stage,pair,reverse=event;x,y=2*pair,2*pair+1
            if reverse:x,y=y,x
            need(stage not in stage_index,'thin has no allocatedhelper job')
            for port in range(V):
                src,dst=x*V+port,y*V+port;need(not values[private],'thin ownedstreamzero')
                before=versions[src];values[private]=values[src];norm[private]=norm[src];begin=event_index
                emit(['THIN_COPY',stage,src,private,port,before]);profile[1]+=1
                emit(['THIN_PAID_QUERY',stage,private,port,1,reverse])
                add(dst,private,1,'THIN_ADD',[stage,port,reverse])
                need(versions[src]==before,'currentphysical SOURCE snapshot notwritten')
                values[private]=norm[private]=0;emit(['THIN_PAID_CLEAR',stage,private])
                private_episodes.append(dict(kind='THIN',stage=stage,source=src,source_version=before,begin=begin,end=event_index))
        elif op=='IDLE':
            _,pair,stages=event;need(set(stages)<=set(thick),'no credit/query for deletedthin multiplier')
            rank=7*len(stages)
            for bank in(2*pair,2*pair+1):
                for port in range(V):
                    role=bank*V+port;profile[rank]+=1;versions[role]+=1
                    emit(['PAID_WHOLE_IDLE',role,stages,rank,port])
        elif op=='ADD':
            for port in range(V):add(event[1]*V+port,event[2]*V+port,meta='BRIDGE')
        else:
            need(op=='SWAP','global actualword opcode')
            for port in range(V):swap(event[1]*V+port,event[2]*V+port,meta='FINAL_SWAP')
    boundary(controller['boundaries']['left_program'],'LEFT_BOUNDARY');zstream.close()
    need(values==[1<<i for i in range(N)]+[0],'all11400 independent decodedRAW columns restored, privatezero')
    need(len(owners)==18 and len({i for o in owners for i in range(o['begin'],o['end'])})==7848,'injective actual helperownership')
    need(len(private_episodes)==18*9+15*111==1827,'every local+thin private episode charged')
    targets=Counter({8:432*18,4:4*18})
    for term in controller['diagonal']:
        need(term&1,'true central SOURCE factor retained')
        targets[1+7*(int(term)>>1).bit_count()]+=V
    expected_paid={1: 25407, 2: 24156, 3: 1404, 4: 702, 5: 1836, 6: 180, 7: 324, 14: 444, 21: 444, 28: 444, 35: 444, 42: 444, 49: 444, 56: 444, 63: 222}
    expected_targets={4: 72, 8: 7776, 15: 444, 22: 444, 29: 444, 36: 444, 43: 444, 50: 444, 57: 444, 64: 222, 127: 222}
    need(dict(sorted(profile.items()))==expected_paid,'actualexpandedpaid ledger')
    need(dict(sorted(targets.items()))==expected_targets,'every actual independent helper/main outputcredit')
    need(max(profile)<127 and sum(targets.values())==N,'proper requests, no private orghost Wcredit')
    result=dict(status='PASS_CURRENT_PARTIAL436_THIN_CONTROLLER_ALL11400_RAW_AND_INDEPENDENT_JOBS',at_utc=datetime.now(timezone.utc).isoformat(),
                raw_scalar_columns=N,main_original_fields=3552,helper_original_fields=7848,
                raw_column_scope='Inline all11400 decodedF2 columns plus exact per-LOCAL frame/function invariant, rational mainportcharts and every physical main polynomial coefficient. Not only coefficient-row SOURCE projection.',
                paid=dict(sorted(profile.items())),targets=dict(sorted(targets.items())),query_count=sum(profile.values()),
                rank_surplus=sum(r*n for r,n in targets.items())-sum(r*n for r,n in profile.items()),
                helper_full8=7776,helper_partial4=72,private_original_credit=0,private_peak=1,private_episodes=len(private_episodes),
                nonidentity_mainport_routes=counts['PAID_PORT_ROUTE'],additional_partial_outputmatcher_routes=144,
                event_counts=dict(counts),expanded_event_count=event_index,expanded_event_sha256=stream_hash.hexdigest(),
                expanded_gzip_sha256=sha256((HERE/'EXPANDED-PROGRAM.jsonl.gz').read_bytes()).hexdigest(),
                cancellation_free_integer_majorant=peak,cancellation_free_majorant_bits=peak.bit_length(),
                raw_scalar_record_bound=10**9,source_type_lift='Single delayed wholeGL ambient, common externalweight independent of freshroles/cover, allfixed projectors tensorI_f and retained C_Nf tail. No free dense reframe or inherited changedROWconstants.',
                fee_scope='All localCOPY/clear,thinCOPY/query/clear,bridge/swaps,wholeidle retained;144 new wholefiber matcher routes plus newrow/stock/normalizer/precision constants must be charged in root strictification.',
                complete_ordinary_or_whole_claim=False,CPU_seconds=time.process_time()-started,
                sourcepins=[dict(path=str(p),sha256=sha256(p.read_bytes()).hexdigest()) for p in [cp,wpath,fpath,refpath]])
    need(event_index+2*sum(profile.values())+2*N+144<10**9,'conservative finite rawrecord/route accounting fits declared bound')
    for name,data in [('RESULT.json',result),('MAIN-PHYSICAL-COEFFICIENTS.json',formal),('OWNERS.json',owners),('CALLS.json',calls),('PRIVATE-EPISODES.json',private_episodes),('RATIONAL-BINDING.json',binding),('ACTIVE-AXES.json',active_embedding)]:
        (HERE/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--local-dir',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();result=build(args.repo_root,args.local_dir,args.out)
    print(json.dumps({k:result[k] for k in ['status','raw_scalar_columns','query_count','rank_surplus','helper_full8','helper_partial4','expanded_event_count','cancellation_free_majorant_bits','CPU_seconds']}))


if __name__=='__main__':main()
