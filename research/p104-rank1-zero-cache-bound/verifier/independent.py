"""Fresh exact replay, distinct-prime ROW ranks and complete circuit audit."""
from collections import defaultdict,Counter
from fractions import Fraction as F
from hashlib import sha256
from copy import deepcopy
from pathlib import Path
import gzip,json,math
P=65521
NEW=(451,746,750,769,1254,1459)
def need(ok,label):
    if not ok:raise ValueError('independent: '+label)
def axpy(a,b,q):
    for h,v in b.items():
        x=a.get(h,F(0))+q*v
        if x:a[h]=x
        else:a.pop(h,None)
def replay(source):
    raw=Path(source).read_bytes();need(sha256(raw).hexdigest()=='acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9','source bytes');w=json.loads(gzip.decompress(raw));n=w['public']
    values=[{h:F(1)} for h in range(n)]+[None]*w['owned_fields'];loc=w['initial'].copy()+[None]*w['owned_fields'];banks=defaultdict(list);lookup={};labels={};targets={}
    def observe(t,a,f):
        key=(t,a,f);row=values[a].copy();lookup[key]=row;labels[key]={'event':t,'owner':a,'frame':f,'kind':'initial' if t<0 else 'arrival'};banks[f].append((key,row))
    for a,f in enumerate(w['initial']):observe(-1,a,f)
    for t,e in enumerate(w['program']):
        op,a=e[:2]
        if op=='MOVE':need(loc[a]==e[2] and values[a] is not None,'MOVE state');targets[t]=values[a].copy();loc[a]=e[3];observe(t,a,e[3])
        elif op=='INIT':need(a>=n and loc[a] is None,'INIT');values[a]={};loc[a]=e[2]
        elif op=='CLEAR':need(a>=n and loc[a]==e[2],'CLEAR');values[a]=None;loc[a]=None
        elif op=='SCALE':need(loc[a]==e[3],'SCALE');values[a]={j:q*F(e[2]) for j,q in values[a].items()}
        else:
            b=e[2];need(op in ('ADD','COPY') and loc[a]==loc[b]==e[4],'contact')
            if op=='COPY':need(not values[a],'COPY zero')
            axpy(values[a],values[b],F(e[3]))
    need(loc==w['final']+[None]*w['owned_fields'] and len(targets)==6279,'complete source')
    mains=set(w['live'])|{a+112 for a in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2']);helpers=set(range(n))-mains
    ranks={h:abs(len(w['frames'][w['initial'][h]])-len(w['frames'][w['final'][h]])) for h in helpers};tested=tuple(sorted(h for h,r in ranks.items() if r==1));need(len(tested)==18,'fresh all18 rank-one helpers')
    need(all(values[h]=={h:F(1)} for h in tested),'fresh autonomous helper endpoint identities')
    zeros={h:sorted(e for e,row in targets.items() if set(row)=={h}) for h in tested};neutral=tuple(h for h in tested if len(zeros[h])==1 and abs(len(w['frames'][w['program'][zeros[h][0]][2]])-len(w['frames'][w['program'][zeros[h][0]][3]]))==1);other=tuple(h for h in tested if h not in neutral)
    need(len(neutral)==12 and other==NEW,'fresh12/6 partition')
    need(all(P%d for d in range(2,math.isqrt(P)+1)),'prime');inverses={};membership={h:set() for h in tested};rank_sum=0;misses=0
    def mod(q):
        if q.denominator not in inverses:need(q.denominator%P,'denominator');inverses[q.denominator]=pow(q.denominator,P-2,P)
        return q.numerator*inverses[q.denominator]%P
    for f,bank in banks.items():
        basis={}
        for key,row in bank:
            v={h:mod(q) for h,q in row.items() if mod(q)}
            while v:
                p=min(v)
                if p not in basis:
                    inv=pow(v[p],P-2,P);basis[p]={h:q*inv%P for h,q in v.items()};break
                q=v[p]
                for h,a in basis[p].items():
                    z=(v.get(h,0)-q*a)%P
                    if z:v[h]=z
                    else:v.pop(h,None)
        need(len(basis)==len(bank),'ROW rank reaches exact row-count upper bound');rank_sum+=len(basis)
        for h in tested:
            v={h:1}
            for p in sorted(basis):
                if v.get(p):
                    q=v[p]
                    for j,a in basis[p].items():
                        z=(v.get(j,0)-q*a)%P
                        if z:v[j]=z
                        else:v.pop(j,None)
            if v:misses+=1
            else:membership[h].add(f)
    need(rank_sum==7780 and len(banks)==979,'complete independent rank domain')
    return dict(w=w,banks=banks,lookup=lookup,labels=labels,targets=targets,tested=tested,neutral=neutral,other=other,zeros=zeros,membership=membership,misses=misses)
def observation(o,frame,ctx):
    need(o['frame']==frame,'observation exact coframe')
    key=(o['event'],o['owner'],o['frame']);need(key in ctx['labels'] and o==ctx['labels'][key],'exact source observation label')
    return key,ctx['lookup'][key]
def validate(data,ctx):
    need(data['helpers_tested']==list(ctx['tested']) and data['neutral_rank1_helpers']==list(ctx['neutral']) and data['nonneutral_rank1_helpers']==list(ctx['other']),'complete fresh helper partition')
    cases={c['helper']:c for c in data['cases']};need(len(cases)==len(data['cases'])==18 and set(cases)==set(ctx['tested']),'complete unique helper cases')
    units=hits_count=0;decisions=[]
    for h,c in sorted(cases.items()):
        ds={d['frame']:d for d in c['coframes']};need(len(ds)==len(c['coframes'])==979 and set(ds)==set(ctx['banks']),'complete unique coframes')
        inside={f for f,d in ds.items() if d['relation_in_final_span']};need(inside==ctx['membership'][h],'distinct-prime membership set')
        derived={};circuit_zeros=set()
        for frame in inside:
            d=ds[frame];entries={};total={}
            for item in d['unique_expression']:
                key,row=observation(item['observation'],frame,ctx);q=F(item['coefficient']);need(q and key not in entries,'unique nonzero unit-expression entries');entries[key]=q;axpy(total,row,q)
            need(total=={h:F(1)},'exact complete unit expression');units+=1
            latest=max(entries,key=lambda k:k[0])
            if latest[0]<0:need('latest_support_MOVE' not in d,'no invented initial latest MOVE');continue
            event=latest[0];need(d.get('latest_support_MOVE')==event,'exact latest nonzero observation')
            ins=ctx['w']['program'][event];need(ins[0]=='MOVE' and ins[1]==latest[1] and ins[3]==frame,'latest actual MOVE arrival')
            q=entries[latest];providers={key:-a/q for key,a in entries.items() if key!=latest}
            need(all(key[0]<event for key in providers),'strict circuit chronology');derived[event]=(frame,providers,1/q)
            if len(entries)==1:circuit_zeros.add(event)
        need(circuit_zeros==set(ctx['zeros'][h]),'complete derived zero MOVE set')
        actual={hit['event']:hit for hit in c['hits']};need(len(actual)==len(c['hits']) and set(actual)==set(derived),'complete unique enabled MOVE set')
        need(c['eligible_MOVE_events_union']==sorted(derived) and c['zero_MOVE_events']==sorted(circuit_zeros) and c['new_nonzero_cache_events']==sorted(set(derived)-circuit_zeros),'complete reported event sets')
        credit=Counter()
        for event,hit in actual.items():
            frame,expected,relation_q=derived[event];ins=ctx['w']['program'][event];rank=abs(len(ctx['w']['frames'][ins[2]])-len(ctx['w']['frames'][ins[3]]))
            need(hit['literal']==ins and hit['rank']==rank and hit['zero']==(event in circuit_zeros),'exact target event/role/rank')
            need({int(j):F(q) for j,q in hit['target_row'].items()}==ctx['targets'][event],'exact target row')
            got={};residual=ctx['targets'][event].copy()
            for item in hit['providers']:
                key,row=observation(item['observation'],frame,ctx);q=F(item['coefficient']);need(key[0]<event and key not in got and q,'strict unique provider');got[key]=q;axpy(residual,row,-q)
            need(got==expected and F(hit['relation_coefficient'])==relation_q and residual=={h:relation_q},'unique exact strict decoder identity');credit[rank]+=1;hits_count+=1
        need(credit==Counter({1:1}) and {int(r):n for r,n in c['credit_histogram'].items()}==dict(credit) and not c['native_gain_profile'],'one rank1 credit cancels target debit')
        decisions.append({'helper':h,'class':'neutral' if h in ctx['neutral'] else 'nonneutral_public_cache','zero_MOVEs':sorted(circuit_zeros),'nonzero_cached_MOVEs':sorted(set(derived)-circuit_zeros),'credit_rank':1,'lost_target_rank':1,'native_gain':0})
    need(units==36 and hits_count==18,'complete all18 circuits and credits')
    return {'status':'PASS_INDEPENDENT_ALL18_COFRAME_LATEST_COMPLETENESS','prime':P,'all18_rank1_helpers':list(ctx['tested']),'neutral12':list(ctx['neutral']),'new6':list(ctx['other']),'original_observation_rank':7780,'unit_coframe_decisions':18*979,'full_row_count_augmented_misses':ctx['misses'],'exact_Q_unit_expressions':units,'exact_complete_target_decoders':hits_count,'decisions':decisions}
def review(source,data):
    ctx=replay(source);result=validate(data,ctx);controls={}
    def reject(label,bad):
        try:validate(bad,ctx)
        except (ValueError,KeyError) as e:controls[label]=str(e);return
        raise ValueError('mutation accepted: '+label)
    def changed_case(h=451):
        bad=dict(data);bad['cases']=list(data['cases']);i=next(i for i,c in enumerate(bad['cases']) if c['helper']==h);bad['cases'][i]=deepcopy(bad['cases'][i]);return bad,bad['cases'][i]
    bad,c=changed_case();c['hits'][0]['providers'][0]['observation']['frame']=3;reject('wrong_provider_coframe',bad)
    bad,c=changed_case();d=next(d for d in c['coframes'] if d.get('latest_support_MOVE'));d['unique_expression'][0]['observation']['frame']=3 if d['frame']!=3 else 127;reject('wrong_unit_observation_coframe',bad)
    bad,c=changed_case();c['hits'].pop();reject('omitted_latest_hit',bad)
    bad,c=changed_case();d=next(d for d in c['coframes'] if d.get('latest_support_MOVE'));d['latest_support_MOVE']-=1;reject('wrong_latest_event',bad)
    bad,c=changed_case();c['hits'].append(deepcopy(c['hits'][0]));reject('duplicate_hit',bad)
    bad,c=changed_case();c['hits'][0]['providers'][0]['coefficient']=str(-F(c['hits'][0]['providers'][0]['coefficient']));reject('wrong_provider_sign',bad)
    bad,c=changed_case();hit=c['hits'][0];hit['providers']=[{'observation':ctx['labels'][(hit['event'],hit['literal'][1],hit['literal'][3])],'coefficient':'1'}];reject('self_arrival_as_provider',bad)
    bad=dict(data);bad['cases']=data['cases'][1:];reject('omitted_helper',bad)
    bad=dict(data);bad['neutral_rank1_helpers']=data['neutral_rank1_helpers'][1:];reject('wrong_12_6_partition',bad)
    result['executed_mutation_controls']=controls;need(len(controls)==9,'all actual mutations executed');return result
