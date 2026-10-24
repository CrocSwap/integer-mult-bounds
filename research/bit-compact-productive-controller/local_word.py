"""Requalify published compact436 at the productive LOCAL interface.

Only new candidate artifacts are written. No upstream cold replay/import.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime,timezone
import argparse,gzip,json,time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OLD=ROOT/'research/bit-compact-carrier-retirement/provider'
SOURCE=ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated'
N,V,R=658,111,436
EXPECTED={1:1319,2:1342,3:78,4:43,5:102,6:10,7:18}


def need(v,m):
    if not v:raise ValueError(m)


def matrix_inverse(A):
    n=len(A);w=[[Q(x) for x in row]+[Q(i==j) for j in range(n)] for i,row in enumerate(A)]
    for j in range(n):
        pivot=next(i for i in range(j,n) if w[i][j]);w[j],w[pivot]=w[pivot],w[j]
        d=w[j][j];w[j]=[x/d for x in w[j]]
        for i in range(n):
            if i!=j and w[i][j]:
                d=w[i][j];w[i]=[x-d*y for x,y in zip(w[i],w[j])]
    return [row[n:] for row in w]


def mm(A,B):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]


def project(frame):
    B=[[Q(x) for x in row] for row in frame['B']]
    if not B:return [[Q(0)]*8 for _ in range(8)]
    T=list(map(list,zip(*B)))
    return mm(mm(T,matrix_inverse(mm(B,T))),B)


def events(records,reverse=False):
    for op,d,s,c,f,z in reversed(records) if reverse else records:
        if op==0:yield [0,d,c if reverse else s,s if reverse else c,f]
        elif op==1:yield [1,d,s,-c if reverse else c,f]
        elif op==(3 if reverse else 2):yield [2,d,s,c,f]
        else:
            need(op==(2 if reverse else 3),'COPY inverse opcode')
            yield [3,d,s,c,f]


def replay(word,frames,reverse=False,initial_signed=None,expected_profile=None):
    state=list(word['final'] if reverse else word['start'])+[None]
    bits=[1<<i for i in range(N)]+[0]
    rows=[{i:1} for i in range(N)]+[{}] if initial_signed is None else [dict(row) for row in initial_signed]
    need(len(rows)==N+1 and not rows[N],'literal private zero')
    opened=None;profile=Counter();queries=copies=adds=0;peak=1;peak_coeff=1;copy_windows=[]
    majorant=[sum(abs(v) for v in row.values()) for row in rows];positive_peak=max(majorant)
    begin=None;unique_pairs=set()
    for time_index,e in enumerate(events(word['records'],reverse)):
        op,d,s,c,f=e
        need(0<=d<N,'ordinary destination namespace')
        if op==0:
            need(opened is None and state[d]==s,'actual MOVE state, no liveCOPY MOVE')
            before,after=frames[str(s)],frames[str(c)]
            low,high=(after,before) if reverse else (before,after)
            need(high['dim']-low['dim']==f and 0<f<8,'proper paid rank, including completions')
            need(all(sum(x*y for x,y in zip(u,v))==0 for u in low['B'] for v in high['A']),'exactQQ nested subspaces')
            state[d]=c;profile[f]+=1;queries+=1;unique_pairs.add((min(s,c),max(s,c),f))
        elif op==1:
            need(0<=s<=N and d!=s and c in(-1,1),'literal signedADD')
            need(state[d]==state[s]==f,'same actual FRAME, no virtual transport')
            need(d!=opened and (s!=N or opened is not None),'SOURCEimmutable/private lifetime')
            bits[d]^=bits[s]
            majorant[d]+=abs(c)*majorant[s];positive_peak=max(positive_peak,majorant[d])
            for col,value in rows[s].items():
                new=rows[d].get(col,0)+c*value
                if new:rows[d][col]=new
                else:rows[d].pop(col,None)
            peak=max(peak,sum(abs(x) for x in rows[d].values()));peak_coeff=max(peak_coeff,max(map(abs,rows[d].values()),default=0));adds+=1
        elif op==2:
            need(s==N and opened is None and state[N] is None and bits[N]==0 and not rows[N],'fresh ownedcenter only')
            need(state[d]==c and f==0 and frames[str(c)]['dim']==7,'actual COPY source/receiver/frame7 charge')
            opened=d;state[N]=f;bits[N]=bits[d];rows[N]=dict(rows[d]);majorant[N]=majorant[d];copies+=1;profile[7]+=1;begin=time_index
        else:
            need(op==3 and s==N and opened==d and state[d]==c and state[N]==f,'ERASEsource/currentframe/lifetime')
            need(bits[N]==bits[d] and rows[N]==rows[d],'allRAW copied original remains unchanged throughERASE')
            copy_windows.append(dict(original=d,source_frame=c,receiver_frame=f,begin=begin,end=time_index))
            opened=None;state[N]=None;bits[N]=0;rows[N]={};majorant[N]=0
    expected=[(1<<i)^((1<<(i-V)) if V<=i<2*V else 0) for i in range(N)]+[0]
    need(bits==expected and opened is None,'all658 independent Boolean columns, not SOURCE-only')
    need(state==list(word['start'] if reverse else word['final'])+[None],'allendpointframes andzero private')
    need(copies==9 and profile==Counter(EXPECTED if expected_profile is None else expected_profile),'complete paid profile incl9COPY')
    identity=[{i:1} for i in range(N)]+[{}]
    if initial_signed is None:
        for i in list(range(V))+list(range(2*V,N)):
            need(rows[i]==identity[i],'integer source andall436 DIRTYhelpers restored')
        for i in range(V,2*V):
            need({j for j,v in rows[i].items() if v%2}=={i,i-V},'integer public lift has required Boolean shear')
    return rows,dict(direction='reverse' if reverse else 'forward',columns=N,helpers=R,private_peak=1,
                     paid_profile=dict(sorted(profile.items())),recursive_MOVE_queries=queries,COPY_queries=9,ERASE_queries=0,
                     scalar_ADDs=adds,signed_row_l1_peak=peak,signed_coefficient_peak=peak_coeff,
                     cancellation_free_majorant_peak=positive_peak,cancellation_free_majorant_bits=positive_peak.bit_length(),
                     unique_nested_pairs=len(unique_pairs),copy_windows=copy_windows)


def build(repo_root, out, partial=True):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    oldbase=OLD if repo_root is None else repo_root/'research/bit-compact-carrier-retirement/provider'
    source=SOURCE if repo_root is None else repo_root/'research/kappa-rebuild/bit/sources/pr589-regenerated'
    start=time.process_time();old_word=oldbase/'inputs/WORD.json.gz';old_geom=oldbase/'inputs/GEOMETRY.json.gz'
    raw=old_word.read_bytes();need(sha256(raw).hexdigest()=='69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b','published compact inputbytepin')
    need(sha256(old_geom.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','published exact geometry pin')
    word=json.loads(gzip.decompress(raw));geometry=json.loads(gzip.decompress(old_geom.read_bytes()))
    frame_path=source/'records/frames.json';frames=json.loads(frame_path.read_bytes())['frames']
    need(sha256(frame_path.read_bytes()).hexdigest()=='d006b3bfe0c04afecfea7aecfa59dfe4298b99501c70da3938e40289bc2f5010','exact current reference frame bank')
    need(sha256((source/'WORD.json.gz').read_bytes()).hexdigest()=='e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f','exact current reference WORD')
    old_source=json.loads(gzip.decompress((source/'WORD.json.gz').read_bytes()))
    need(geometry['lines']==old_source['lines'],'exact ordered111 SOURCE ports')
    need(word['start'][:222]==old_source['start'][:222] and word['final'][:222]==old_source['final'][:222],'unchanged SOURCE/Y physical entrance/exits')
    need(len(word['start'])==len(word['final'])==N and all(x==0 for x in word['start'][222:]),'all436 helpers arbitrary coldoriginals')
    found=[(i,f) for i,f in enumerate(word['final']) if i>=222 and f!=1]
    need(found==[(462,506),(463,506),(466,508),(468,509)],'four genuine rank4 partialendpoints')
    completion=[]
    for role,f in found:
        P=project(frames[str(f)]);I=[[Q(i==j) for j in range(8)] for i in range(8)]
        C=[[I[i][j]-P[i][j] for j in range(8)] for i in range(8)]
        need(mm(P,P)==P and mm(C,C)==C and sum(C[i][i] for i in range(8))==4,'actual rational rank4 completion projector')
        completion.append(dict(role=role,from_frame=f,to_frame=1,rank=4,projector=[[str(x) for x in row] for row in C]))
        if not partial:
            word['records'].append([0,role,f,1,4,0]);word['final'][role]=1
    if partial:
        word['format']='compact436-productive-partial/1'
        word['productive_interface']=dict(SOURCE_ports=111,TARGET_ports=111,independent_helpers=436,helper_job_ranks={'4':4,'8':432},private_index=658,old_word_sha256=sha256(raw).hexdigest(),paid_completion_count=0)
    else:
        word['format']='compact436-productive-full8/1'
        word['productive_interface']=dict(SOURCE_ports=111,TARGET_ports=111,independent_helpers=436,helper_job_rank=8,private_index=658,old_word_sha256=sha256(raw).hexdigest(),paid_completion_count=4)
    expected_profile=dict(EXPECTED)
    if partial:expected_profile[4]-=4
    forward,fw=replay(word,frames,expected_profile=expected_profile)
    reverse,rv=replay(word,frames,True,expected_profile=expected_profile)
    # Signed full inverse uses actual output expressions, not just modulo2.
    back,_=replay(word,frames,True,forward,expected_profile)
    forth,_=replay(word,frames,False,reverse,expected_profile)
    identity=[{i:1} for i in range(N)]+[{}]
    need(back==forth==identity,'both exact signed inverse orders onall658 independent RAW')
    job_frames=sorted(set(word['final'][222:]))
    helper_jobs=dict(projectors={str(f):[[str(x) for x in row] for row in project(frames[str(f)])] for f in job_frames},
                     independent_roles=[dict(role=i,initial_frame=0,job_frame=word['final'][i],rank=frames[str(word['final'][i])]['dim']) for i in range(222,N)],
                     physical_law='Forward D_final*D_initial^-1 on own RAW; reverse uses inverse but idempotent-job involution equals itself. All helper starts0, independent own signedrow, no SOURCE/TARGET contamination.',
                     cover_lift='Embed exact8x8 P in local first8 ambient axes and tensor I_f; reverse tail uses retained C_Nf convention. No free coordinate adapter.')
    (out/'HELPER-ENDPOINTS.json').write_text(json.dumps(helper_jobs,indent=2)+'\n',encoding='utf-8')
    (out/'COMPLETIONS.json').write_text(json.dumps(completion,indent=2)+'\n',encoding='utf-8')
    packed=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
    (out/'WORD.json.gz').write_bytes(gzip.compress(packed,mtime=0))
    (out/'SIGNED-ENDPOINTS.json').write_text(json.dumps(dict(forward=forward,reverse=reverse),indent=2)+'\n',encoding='utf-8')
    result=dict(status='PASS_PARTIAL_PRODUCTIVE_LOCAL_ALL658_RAW_NATIVE_AND_SIGNED' if partial else 'PASS_FULL8_PRODUCTIVE_LOCAL_ALL658_RAW_NATIVE_AND_SIGNED',at_utc=datetime.now(timezone.utc).isoformat(),
                word_sha256=sha256((out/'WORD.json.gz').read_bytes()).hexdigest(),content_sha256=sha256(packed).hexdigest(),
                ordinary_columns=N,independent_helper_columns=R,all_helper_physical_jobs='432 D_I8 and4 actual D_P4, arbitraryindependent initialdata' if partial else 'D_I8, arbitraryinitialdata, no free promotions',
                SOURCE_Y_interface_identical_to_current589=True,ordered_SOURCE_lines_identical=True,
                forward=fw,reverse=rv,signed_inverse_both_orders=True,
                completion_count=0 if partial else 4,complete_LOCAL_rankmass=5089 if partial else 5105,published_partial_LOCAL_rankmass=5089,
                productive_helper_ranks={'4':4,'8':432} if partial else {'8':436},
                attribution='Reuses our published compact436/GL464 and credited public boundary/delayed retirement lineage; new mixed productive-helper ABI/current-controller requalification only.',
                current_global_not_yet_executed=True,
                sourcepins=[dict(path=str(p),sha256=sha256(p.read_bytes()).hexdigest()) for p in [old_word,old_geom,source/'WORD.json.gz',frame_path]],CPU_seconds=time.process_time()-start)
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--completed',action='store_true',help='Paid full-rank fallback; not the submitted partial ABI')
    args=p.parse_args()
    result=build(ROOT,args.out,not args.completed)
    print(json.dumps({k:result[k]for k in ('status','content_sha256','ordinary_columns','productive_helper_ranks')}))

if __name__=='__main__':main()
