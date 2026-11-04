"""Independent source-bound P104 application checks, not a native scalar replay.

No author interpreter, native phase routine, constructor or price is imported.
Exact character phases are checked by parity evaluations on weights zero/one/two;
these determine the Z/4 quadratic character of commuting C_v factors. The
retained native scalar identity and its 2,939 internal maps are NOT reproved.
thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256,sha1
import argparse
import gzip
import json

HERE=Path(__file__).resolve().parent
SLOTS={'ADD':(1,2),'SWAP':(1,2),'SCALE':(1,),'LAMBDA':(1,),'Q_POWER':(1,),
       'QUERY':(1,2),'LOCAL':(2,3),'IDLE':(1,2),'IDLE_ONE':(1,)}


def need(ok,why):
    if not ok: raise ValueError(why)


def read(name):
    b=(HERE/'inputs'/name).read_bytes()
    return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)


def authenticate():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for pin in pins['files']:
        b=(HERE/pin['copy']).read_bytes()
        need(len(b)==pin['bytes'] and sha256(b).hexdigest()==pin['sha256'], 'source SHA '+pin['copy'])
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==pin['git_blob'], 'source blob '+pin['copy'])
    outer=read('SOURCE-RETAINED.json')
    record=next(x for x in outer['files']if x['path'].endswith('/RETAINED.json'))
    need(sha256((HERE/'inputs/NATIVE-RETAINED.json').read_bytes()).hexdigest()==record['sha256'],
         'nested manifest is byte-pinned by original6702 source inventory')
    retained=read('NATIVE-RETAINED.json')['native']
    pin=next(x for x in retained['files'] if x['path'].endswith('/WORD.json.gz'))
    need(sha256((HERE/'inputs/NATIVE.json.gz').read_bytes()).hexdigest()==pin['sha256'], 'nested exact native pin')
    need(retained['source_head']=='44b0d0e8961201ac1656490b4384a7752e1cd9c5','nested native head')
    return len(pins['files'])


def span(basis):
    values={0}
    for v in basis:
        need(isinstance(v,int) and 0<v<512 and v not in values,'independent nine-axis flag')
        values|={x^v for x in tuple(values)}
    return frozenset(values)


def native_contract(w):
    public,owned=w['public'],w['owned_fields']
    need((public,owned)==(771,29),'exact native public/owned inventory')
    flags=[span(b)for b in w['frames']]
    state=list(w['initial'])+[None]*owned
    zero=[False]*public+[True]*owned
    active=set();lifetimes=[];starts={};peak=0;paid=Counter()
    for i,e in enumerate(w['program']):
        op,r=e[:2];need(0<=r<public+owned,'native role range')
        if op=='INIT':
            need(r>=public and state[r] is None,'owned lifetime entry is inactive')
            state[r]=e[2];zero[r]=True;active.add(r);starts[r]=i;peak=max(peak,len(active))
        elif op=='CLEAR':
            need(r in active and state[r]==e[2],'declared owned exit chart')
            lifetimes.append([r,starts.pop(r),i]);active.remove(r);state[r]=None;zero[r]=True
        elif op=='MOVE':
            _,r,a,b,private=e
            need(state[r]==a and (r in active)==private,'native transport ownership and source')
            need(flags[b]<flags[a] if private else flags[a]<flags[b],'strict actual flag transport')
            paid[abs(len(w['frames'][a])-len(w['frames'][b]))]+=1;state[r]=b
        elif op in ('ADD','COPY','SCALE'):
            need(state[r]==e[-1] and F(e[-2])!=0,'scalar destination chart')
            if op!='SCALE':
                src=e[2];need(src!=r and state[src]==state[r],'both scalar payloads use actual same chart')
                if op=='COPY':
                    need(r in active and zero[r],'literal COPY target known zero since INIT')
                    zero[r]=zero[src]
                elif not zero[src]: zero[r]=False
        else: raise ValueError('native event outside contract')
    need(not active and state[:public]==w['final'],'all public charts and owned lifetimes return')
    main=set(w['live'])|{x+112 for x in w['live']}
    need(len(main)==208 and len(w['ports'])==len(w['live'])==104,'complete actual main port pairs')
    helpers=Counter()
    for r in range(public):
        if r not in main:
            need(flags[w['initial'][r]]<flags[w['final'][r]],'strict productive helper flag')
            helpers[len(w['frames'][w['final'][r]])-len(w['frames'][w['initial'][r]])]+=1
    need(len(lifetimes)==47 and peak==14 and sum(helpers.values())==563,'exact owned/helper census')
    return {'paid':dict(sorted(paid.items())),'helpers':dict(sorted(helpers.items())),
            'public':public,'owned_labels':owned,'owned_lifetimes':len(lifetimes),'peak_owned':peak,
            'lifetime_sha256':sha256(json.dumps(lifetimes,separators=(',',':')).encode()).hexdigest()}


def normalized(terms):
    c=Counter()
    for v,k in terms: c[v]+=k
    return tuple((v,k%4)for v,k in sorted(c.items())if v and k%4)


def character(terms,frequency):
    return sum(k*((v&frequency).bit_count()%2) for v,k in terms)%4


def phase_equal(left,right,constant=0):
    """All-frequency equality follows since parity mod4 has degree at most2."""
    diff=normalized([*left,*[(v,-k)for v,k in right]])
    need(constant%4==0,'absolute phase at zero Fourier frequency')
    support=0
    for v,_ in diff:support|=v
    bits=[1<<i for i in range(support.bit_length())if support>>i&1]
    for i,a in enumerate(bits):
        need(character(diff,a)==0,'weight-one absolute Fourier phase')
        for b in bits[i+1:]:need(character(diff,a|b)==0,'weight-two absolute Fourier phase')


def route_value(v,basis,fresh):
    out=v
    for b,t in zip(basis,fresh):
        if (v&(b^t)).bit_count()%2:out^=b^t
    return out


def contact(old,new,basis,fresh):
    moved=normalized((route_value(v,basis,fresh),k)for v,k in old)
    diff=normalized([*new,*[(v,-k)for v,k in moved]])
    support=0
    for v,_ in diff:support|=v
    shift=0
    for i in range(support.bit_length()):
        k=character(diff,1<<i);need(k in (0,2),'contact repair is an ordinary translation')
        if k==2:shift|=1<<i
    phase_equal([*moved,(shift,2)],new)
    inverse=route_value(shift,basis,fresh)
    phase_equal([*((route_value(v,basis,fresh),k)for v,k in new),(inverse,2)],old)
    return {'translation':shift,'inverse_translation':inverse}


def physical(word,native,phases):
    axes=[1<<i for i in range(word['ambient_rank'])]
    recipes={r['q']:r for r in phases['recipes']}
    contacts=[];targets=Counter();idles=Counter();plain=0
    for e in word['events']:
        if e[0]=='LOCAL':
            stage=e[1];fresh=axes[9+8*(stage-1):9+8*stage]
            before=normalized((v,1)for v in axes[:9+8*(stage-1)])
            after=normalized((v,1)for v in axes[:9+8*stage])
            spectator=[(v,1)for v in axes[9:9+8*stage]]
            for q in native['ports']:
                basis=recipes[q]['idle_children'][0]['orthogonal_axes'][:8]
                need(q.bit_count()%2==1 and len(basis)==8,'actual nonisotropic central port')
                need(all((a&b).bit_count()%2==int(i==j)for i,a in enumerate(basis)for j,b in enumerate(basis)),'actual orthonormal source block')
                need(all((b&q).bit_count()%2==0 for b in basis),'central port orthogonal to source block')
                need(route_value(q,basis,fresh)==q,'physical route fixes actual central direction')
                need(all(route_value(b,basis,fresh)==t and route_value(t,basis,fresh)==b for b,t in zip(basis,fresh)),'actual two blocks exchanged without spectators')
                rawy=normalized([*before,(q,-1)])
                entryx=normalized([*spectator,(q,1)]);entryy=normalized(spectator)
                exitx=normalized([*spectator,*[(v,1)for v in axes[:9]]])
                exity=normalized([*exitx,(q,-1)]);outy=normalized([*after,(q,-1)])
                maps=[contact(a,b,basis,fresh)for a,b in [(before,entryx),(rawy,entryy),(exitx,after),(exity,outy)]]
                for old,new in [(before,after),(rawy,outy)]:
                    phase_equal([*new,*[(v,-k)for v,k in old]],[(v,1)for v in fresh])
                phase_equal([*outy,*[(v,-k)for v,k in before]],[(v,1)for v in fresh]+[(q,-1)])
                contacts.append([stage,q,maps])
        elif e[0]in ('IDLE','IDLE_ONE'):
            stages=e[3]if e[0]=='IDLE'else e[2]
            need(len(set(stages))==len(stages) and all(1<=s<=18 for s in stages),'actual complete disjoint fresh idle blocks')
            rank=8*len(stages)
            positive=[v for s in stages for v in axes[9+8*(s-1):9+8*s]]
            need(len(set(positive))==rank,'whole idle has all independent physical axes')
            idles[rank]+=(2 if e[0]=='IDLE'else 1)*len(native['ports'])
    for term in word['diagonal']:
        qp,*selected=term
        need(selected[0]==0 and qp in (-1,0,1),'new central/plain target alphabet')
        fresh=[v for s,yes in enumerate(selected[1:],1)if yes for v in axes[9+8*(s-1):9+8*s]]
        for q in native['ports']:
            raw=[(q,qp),*[(v,1)for v in fresh]]
            positive=([(q,1)]if qp else[])+[(v,1)for v in fresh]
            phase_equal([*raw,(q,2 if qp==-1 else 0)],positive)
            targets[len(fresh)+bool(qp)]+=1
            plain+=int(qp==0)
    return {'ports':104,'full_calls':len(contacts)//104,'physical_contacts':4*len(contacts),
            'main_targets':dict(sorted(targets.items())),'whole_idle_jobs':dict(sorted(idles.items())),
            'route_payload_sha256':sha256(json.dumps(contacts,separators=(',',':')).encode()).hexdigest(),
            'plain_target_port_endpoints':plain,'ordinary_normalizations':sum(e[0]=='LAMBDA'for e in word['events'])}


def mm(a,b):return [[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]
def inv(a):
    n=len(a);m=[list(row)+[F(i==j)for j in range(n)]for i,row in enumerate(a)]
    for j in range(n):
        k=next(k for k in range(j,n)if m[k][j]);m[j],m[k]=m[k],m[j]
        z=m[j][j];m[j]=[x/z for x in m[j]]
        for k in range(n):
            if k!=j:
                z=m[k][j];m[k]=[x-z*y for x,y in zip(m[k],m[j])]
    return [r[n:]for r in m]


def changed_boundary(base,word,root,witness):
    c=[[F(x)for x in r]for r in root['bases']['1']];ci=inv(c)
    for site,ij,sign in [(1,(0,1),1),(2,(1,0),-1)]:
        r=[[F(x)for x in row]for row in root['queries'][site]]
        desired=[[F(sign if (i,j)==ij else 0)for j in range(8)]for i in range(8)]
        need(mm(mm(ci,r),c)==desired,'same actual ordinary basis for both adjacent queries')
        mask=root['masks'][root['full_sites'].index(site)]
        p=[[F(i==j and bool(mask>>i&1))for j in range(8)]for i in range(8)]
        need(mm(mm(ci,p),c)==[[F(i==j and i<4)for j in range(8)]for i in range(8)],'same actual four-dimensional source projector')
    i=next(i for i,e in enumerate(base['events'])if e[:3]==['IDLE',2,3])
    stages=base['events'][i][3];need(stages==[5,6,7,8,9],'exact fused B+C stage union')
    j=i-1
    while j>=0 and not any(base['events'][j][k]in (2,3)for k in SLOTS[base['events'][j][0]]):j-=1
    need(sorted(e[1]for e in base['events'][j+1:i]if e[0]=='LOCAL')==stages,'all B and C children occur without either idle packet being read or overwritten')
    need([e for e in base['events']if e[0]=='IDLE_ONE']==[['IDLE_ONE',2,[10,11,12,13]]],'single remaining individual idle has true rank32')
    cutoff=witness['handoff_after'];fresh=witness['fresh'];pivot=witness['pivot']
    need((witness['cut_after'],cutoff,fresh,pivot)==(353,362,34,4),'actual literal cut and ownership handoff')
    need(all(e[k]!=fresh for e in word['events'][:cutoff+1]for k in SLOTS[e[0]]),'all-original fresh field34 untouched before suffix ownership')
    after=[(k,e)for k,e in enumerate(word['events'][cutoff+1:],cutoff+1)if any(e[t]==pivot for t in SLOTS[e[0]])]
    need(len(after)==1 and after[0][1]==['LAMBDA',4,-1],'completed pivot never consumed by a subsequent Gaussian or cross-field read')
    need(word['diagonal'][fresh][0]==0 and sum(word['diagonal'][fresh][1:])==4,'fresh independent input has only paid rank32 continuation')
    need(word['diagonal'][pivot]==[-1]+[0]*19,'original pivot earns only its actual rank1 completion')
    return {'common_idle_unretired_event':i,'untouched_packet_window':[j+1,i-1],
            'two_independent_packets':[2,3],'union_stages':stages,'paid_jobs_per_port':2,'rank_each':40,
            'individual_idle':{'owner':2,'stages':[10,11,12,13],'rank':32},
            'cut_after':353,'handoff_after':362,'fresh_first_access':next(i for i,e in enumerate(word['events'])if any(e[k]==34 for k in SLOTS[e[0]])),
            'retired_pivot_only_late_action':after}


def allocation_and_bill(word,native,contract,geometry):
    ports=len(native['ports']);main=set(range(word['roles']*ports))
    helpers=set();owned=set();calls=[]
    native_main=set(native['live'])|{r+112 for r in native['live']}
    helper_roles=[r for r in range(native['public'])if r not in native_main]
    hbase=len(main);obase=hbase+18*len(helper_roles);mapping_payload=[]
    stage_seen=set()
    for index,e in enumerate(word['events']):
        if e[0]!='LOCAL':continue
        _,stage,src,dst=e;need(stage not in stage_seen and src!=dst,'separate native stage and arbitrary two-input service')
        stage_seen.add(stage);mapping={}
        for i,r in enumerate(native['live']):mapping[r]=src*ports+i;mapping[r+112]=dst*ports+i
        for i,r in enumerate(helper_roles):
            mapping[r]=hbase+(stage-1)*len(helper_roles)+i;helpers.add(mapping[r])
        need(len(mapping)==len(set(mapping.values()))==771,'all native public arbitrary inputs mapped injectively')
        for r in range(771,800):owned.add(obase+(stage-1)*29+r-771)
        mapping_payload.append([stage,[mapping[r]for r in range(771)]])
        calls.append([index,stage,src,dst])
    need(stage_seen==set(range(1,19)) and len(helpers)==18*563,'every native helper independently retained')
    query_owned=set(range(obase+18*29,obase+18*29+ports))
    need(not(main&helpers or helpers&owned or owned&query_owned),'no productive/owned alias')
    paid=Counter({int(r):v*18 for r,v in contract['paid'].items()})
    paid[1]+=ports*sum(e[0]=='QUERY'for e in word['events'])
    paid.update(geometry['whole_idle_jobs'])
    target=Counter({int(r):v*18 for r,v in contract['helpers'].items()});target.update(geometry['main_targets'])
    return {'productive_main_fields':len(main),'independent_native_helpers':len(helpers),
            'conservative_native_owned_slots':len(owned),'disjoint_query_owned_slots':len(query_owned),
            'native_lifetimes_total':18*contract['owned_lifetimes'],'native_peak_live_owned':contract['peak_owned'],
            'global_field_slots_upper':len(main)+len(helpers)+len(owned)+len(query_owned),
            'raw_all_lifetime_storage_envelope':{'productive_W':len(main)+len(helpers),
                'native_lifetime_slots':18*contract['owned_lifetimes'],
                'thin_lifetime_slots':ports*sum(e[0]=='QUERY'for e in word['events']),
                'W_plus_all_raw_lifetime_O':len(main)+len(helpers)+18*contract['owned_lifetimes']+ports*sum(e[0]=='QUERY'for e in word['events']),
                'interpretation':'Compatibility with the published W+O definition only; this is a new conservative integer allocation construction, not a verified literal tape/compiler slot assignment.'},
            'native_call_map_sha256':sha256(json.dumps(calls,separators=(',',':')).encode()).hexdigest(),
            'native_public_integer_map_sha256':sha256(json.dumps(mapping_payload,separators=(',',':')).encode()).hexdigest(),
            'paid':dict(sorted(paid.items())),'targets':dict(sorted(target.items())),
            'paid_jobs':sum(paid.values()),'productive_jobs':sum(target.values()),
            'paid_rank_mass':sum(r*n for r,n in paid.items()),'target_rank_mass':sum(r*n for r,n in target.items())}


def rejected(fn):
    try:fn()
    except (ValueError,KeyError):return True
    raise ValueError('negative control accepted')


def central_normalization():
    one=(F(1),F(0));zero=(F(0),F(0));a=(F(1,2),F(1,2));b=(F(1,2),F(-1,2))
    def mul(z,w):return(z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0])
    def add(z,w):return(z[0]+w[0],z[1]+w[1])
    need(add(mul(a,a),mul(b,b))==zero and add(mul(a,b),mul(b,a))==one,
         'actual two-address C kernel squares to translation with phase+1')
    roots=[one,(F(0),F(1)),(-F(1),F(0)),(F(0),-F(1))]
    signs=[]
    for exponent,q in enumerate(roots):
        x=mul(q,q);lam=add(a,mul(b,x));li=add(b,mul(a,x))
        need(mul(lam,lam)==x and mul(lam,li)==one,'ordinary global Lambda pair and square')
        s=mul(lam,(q[0],-q[1]));need(mul(s,s)==one,'actual normalized central involution')
        signs.append(int(s[0]));need(s[1]==0,'real involution character')
    # For f=2 and two odd column characters, Lambda_f=1 while Lambda_1^tensor2=-1.
    need(signs==[1,1,-1,-1],'global scalar coefficients stay outside tensor powers')
    return {'kernel_square':'X_q with absolute phase +1','Q4':'I',
            'Lambda_eigencharacters_at_Q_i_powers':[1,'i',1,'i'],
            'normalized_S_eigencharacters':signs,
            'tensorized_Lambda_counterexample':{'columns':2,'odd_columns':2,'correct_global_Lambda':1,'incorrect_tensor_Lambda':-1},
            'rule':'Lambda_f=a I+b Q_f^2; coefficients a,b occur once, outside the tensor power.'}


def run():
    pins=authenticate();word,base,root,wit,native,phases=[read(x)for x in ['WORD.json','BASE.json','ROOT.json','WITNESS.json','NATIVE.json.gz','PHASES.json']]
    contract=native_contract(native);central=central_normalization()
    sourceword=read('SOURCE-WORD.json');source=physical(sourceword,native,phases)
    geometry=physical(word,native,phases)
    for actual,saved in [(source,read('SOURCE-PRIMARY.json')['candidate']['physical']),
                         (geometry,read('PRIMARY.json')['candidate']['physical'])]:
        for k in ['ports','full_calls','physical_contacts','main_targets','whole_idle_jobs','route_payload_sha256','ordinary_normalizations']:
            expected=saved[k]
            if isinstance(expected,dict):expected={int(k):v for k,v in expected.items()}
            need(actual[k]==expected,'independent physical application equals exact frozen original/candidate '+k)
    boundary=changed_boundary(base,word,root,wit)
    bill=allocation_and_bill(word,native,contract,geometry)
    primary=read('PRIMARY.json')['candidate']['complete_cost']
    for name in ['targets','paid']:need(bill[name]=={int(k):v for k,v in primary[name].items()},'complete actual event bill '+name)
    controls={}
    controls['absolute_phase_only']=rejected(lambda:phase_equal([],[],2))
    controls['missing_central_square_translation']=rejected(lambda:phase_equal([(11,-1)],[(11,1)]))
    bad=json.loads(json.dumps(word));bad['events'][0]=['ADD',0,34,'1']
    controls['fresh_input_read_before_handoff']=rejected(lambda:changed_boundary(base,bad,root,wit))
    bad=json.loads(json.dumps(base));bad['events'][164][3]=[5,6,7,8,8]
    controls['fused_duplicate_or_lost_axis']=rejected(lambda:changed_boundary(bad,word,root,wit))
    bad=json.loads(json.dumps(word));bad['diagonal'][34][0]=-1
    controls['unearned_fresh_central_target']=rejected(lambda:changed_boundary(base,bad,root,wit))
    return {'schema':'independent-p104-application-delta/1','status':'PASS_SOURCE_BOUND_PHASES_ALLOCATION_AND_NEW_DELTA',
            'authenticated_inputs':pins,'native_contract':contract,'original_6702_physical_positive_control':source,
            'actual_central_and_global_normalization':central,
            'candidate_physical':geometry,'changed_boundary':boundary,'allocation_and_exact_bill':bill,
            'negative_controls':controls,'scope':'Independent caller phase/route/whole-idle/target and chronological owner application checks. No import of author replay/native/physical/price. Native scalar endpoints, 2939 internal maps and five all-size framework assumptions remain inherited, not newly proved. All evidence is author-side, not scientific admission.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    result=run();raw=json.dumps(result,sort_keys=True,indent=2)+'\n';path=HERE/'APPLICATION.json'
    if a.write:path.write_text(raw)
    else:need(path.read_text()==raw,'read-only exact application receipt')
    print(json.dumps({'status':result['status'],'contacts':result['candidate_physical']['physical_contacts'],
                     'paid_jobs':result['allocation_and_exact_bill']['paid_jobs'],
                     'productive_jobs':result['allocation_and_exact_bill']['productive_jobs']},sort_keys=True))
