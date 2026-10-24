"""Independent literal caller/Laurent check and factored recursive ledger.

No invoice tables or producer pricing/replay engines are used. Target arities
come from the extracted diagonal; local helper ownership comes from native
conformance. This is a source-protocol check, not a physical phase proof.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
import re


def need(ok,message):
    if not ok:raise ValueError(message)


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def integer(x,lo,hi):return type(x) is int and lo<=x<=hi


def rational(value):
    need(type(value) in (int,str) and len(str(value))<=256,'Bounded exact rational')
    need(re.fullmatch(r'[+-]?[0-9]+(?:/[1-9][0-9]*)?',str(value),flags=re.ASCII) is not None,
         'Rational must use bounded integer or integer/positive-integer spelling')
    return Q(value)


def accumulate(dst,src,factor=Q(1),shift=None):
    for key,value in src.items():
        if shift is not None:key=tuple(a+b for a,b in zip(key,shift))
        result=dst.get(key,Q(0))+factor*value
        if result:dst[key]=result
        else:dst.pop(key,None)
    need(len(dst)<=32768,'Supported Laurent row term budget')


def boundary(data,side,n):
    rows=[[Q(i==j) for j in range(n)] for i in range(n)]
    program=data[side+'_program']
    need(type(program) is list and len(program)<=4096,'Supported boundary program')
    for index,event in enumerate(program):
        try:
            op=event[0];i=event[1];need(integer(i,0,n-1),'Boundary destination')
            if op=='SWAP':
                need(len(event)==3 and integer(event[2],0,n-1),'Boundary SWAP shape')
                rows[i],rows[event[2]]=rows[event[2]],rows[i]
            elif op=='SCALE':
                need(len(event)==3,'Boundary SCALE shape');q=rational(event[2]);need(q!=0,'Nonzero boundary SCALE')
                rows[i]=[q*x for x in rows[i]]
            else:
                need(op=='ADD' and len(event)==4 and integer(event[2],0,n-1) and event[2]!=i,'Boundary ADD shape')
                q=rational(event[3]);rows[i]=[a+q*b for a,b in zip(rows[i],rows[event[2]])]
        except (ValueError,IndexError,TypeError,ZeroDivisionError) as error:
            raise ValueError(f'boundary {side} event {index}: {error}') from error
    declared=data[side]
    need(type(declared) is list and len(declared)==n and all(type(row) is list and len(row)==n for row in declared),'Boundary matrix shape')
    need(rows==[[rational(q) for q in row] for row in declared],f'Boundary {side} program/matrix mismatch')
    return rows


def extract(controller,native):
    need(type(controller) is dict and controller.get('kind')=='complex','Supported complex caller schema')
    pairs=controller['pairs'];need(integer(pairs,1,32),'Supported caller pair count')
    n=2*pairs;stages=n+1;width=stages+1;zero=(0,)*width
    left=boundary(controller['boundaries'],'left',n);right=boundary(controller['boundaries'],'right',n)
    rows=[[({zero:q} if q else {}) for q in row] for row in right]
    physical=controller['physical_events'];need(type(physical) is list and len(physical)<=16384,'Supported caller event count')
    used_stages=set();calls=[];outer_paid=[];ordinary=[];events=Counter()
    v=native['v'];h=native['h'];need(integer(v,1,4096) and integer(h,2,16),'Supported native dimensions')
    for index,event in enumerate(physical):
        try:
            need(type(event) is list and event,'Caller event record');kind=event[0];events[kind]+=1
            if kind in ('LOCAL','QUERY_SHEAR'):
                need(len(event)==4,'Call event shape');_,stage,pair,back=event
                need(integer(stage,0,stages-1) and stage not in used_stages,'Exactly one occurrence of each stage')
                need(integer(pair,0,pairs-1) and type(back) is bool,'Pair and literal orientation')
                used_stages.add(stage);x,y=2*pair,2*pair+1
                if back:x,y=y,x
                shift=(1 if back else -1,)+(0,)*stages
                for dst,src in zip(rows[y],rows[x]):accumulate(dst,src,Q(-1 if back else 1),shift)
                if kind=='LOCAL':
                    direction='backward' if back else 'forward'
                    calls.append({'id':f'caller:{index}','event':index,'stage':stage,'pair':pair,'orientation':direction})
                    shift=(0,)+tuple(int(j==stage) for j in range(stages))
                    for role in (x,y):
                        rows[role]=[{tuple(a+b for a,b in zip(term,shift)):q for term,q in cell.items()} for cell in rows[role]]
                else:outer_paid.append({'id':f'caller:{index}:query','event':index,'kind':'query','rank':1,'count':v})
            elif kind=='IDLE':
                need(len(event)==3 and integer(event[1],0,pairs-1),'Idle shape')
                subset=event[2]
                need(type(subset) is list and subset and all(integer(j,0,stages-1) for j in subset) and len(set(subset))==len(subset),'Idle exact distinct stage subset')
                shift=(0,)+tuple(int(j in subset) for j in range(stages))
                for role in (2*event[1],2*event[1]+1):
                    rows[role]=[{tuple(a+b for a,b in zip(term,shift)):q for term,q in cell.items()} for cell in rows[role]]
                outer_paid.append({'id':f'caller:{index}:idle','event':index,'kind':'idle','rank':(h-1)*len(subset),'count':2*v})
            elif kind=='ADD':
                need(len(event)==4 and integer(event[1],0,n-1) and integer(event[2],0,n-1) and event[1]!=event[2],'Caller ADD shape')
                for dst,src in zip(rows[event[1]],rows[event[2]]):accumulate(dst,src,rational(event[3]))
                ordinary.append({'event':index,'operation':event})
            else:
                need(kind in ('SWAP','SIGNED_SWAP') and len(event)==3 and integer(event[1],0,n-1) and integer(event[2],0,n-1) and event[1]!=event[2],'Known caller opcode')
                a,b=event[1:];old=rows[a];rows[a]=rows[b]
                rows[b]=[{key:(-q if kind=='SIGNED_SWAP' else q) for key,q in cell.items()} for cell in old]
                ordinary.append({'event':index,'operation':event})
        except (ValueError,IndexError,TypeError,KeyError,ZeroDivisionError) as error:
            raise ValueError(f'caller event {index}: {error}') from error
    need(used_stages==set(range(stages)),'Every caller stage is present exactly once')
    result=[[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k,q in enumerate(left[i]):
            if q:
                for j in range(n):accumulate(result[i][j],rows[k][j],q)
    diagonal=[]
    for i in range(n):
        for j in range(n):
            cell=result[i][j]
            if i!=j:need(not cell,f'Caller off-diagonal residual {i},{j}')
            else:
                need(len(cell)==1 and next(iter(cell.values()))==1,f'Caller non-unit diagonal {i}')
                term=next(iter(cell));need(term[0] in (-1,1) and all(x in (0,1) for x in term[1:]),'Whole Gaussian target exponents')
                diagonal.append(list(term))
    need(diagonal==controller['diagonal'],'Caller literal/declared diagonal mismatch')
    main=[{'id':f'caller:main:{i}','role':i,'rank':1+(h-1)*sum(term[1:]),'count':v,'exponents':term}
          for i,term in enumerate(diagonal)]
    paid=Counter();targets=Counter();orientations=Counter(c['orientation'] for c in calls)
    local_groups=[]
    for direction in ('forward','backward'):
        local=native['orientations'][direction];call_ids=[c['id'] for c in calls if c['orientation']==direction]
        for record in local['paid_events']:
            rank=record['rank'];paid[rank]+=len(call_ids)
            local_groups.append({'side':'paid','orientation':direction,'native_event':record['event'],'rank':rank,'count':len(call_ids),'call_ids':call_ids})
        for record in local['helper_targets']:
            rank=record['target_rank']
            if record['credited']:targets[rank]+=len(call_ids)
            local_groups.append({'side':'targets' if record['credited'] else 'surrendered_targets',
                                 'orientation':direction,'native_role':record['role'],
                                 'rank':rank,'count':len(call_ids),'call_ids':call_ids})
    for record in outer_paid:paid[record['rank']]+=record['count']
    for record in main:targets[record['rank']]+=record['count']
    ambient=controller['ambient_rank']
    need(integer(ambient,1,10**9) and max((*paid.keys(),*targets.keys()))<=ambient,'Ranks within caller ambient')
    histogram=lambda counter:{str(r):n for r,n in sorted(counter.items()) if n}
    invoice={'schema':'integer-mult-recursive-invoice/v1',
        'contract':{'model':'mixed-target-unnormalized-power-v1',
                    'rank_semantics':'H_r has raw tariff r^(1-C), with surrendered productive fields debited',
                    'ambient_rank':ambient,'boundary':'complete p16/a7 unit before the retained mixed-target compiler'},
        'paid':histogram(paid),'targets':histogram(targets)}
    # The supported caller is the actual p16/a7 interface. Other grammars need
    # their own tariff/ownership adapter instead of inheriting this label.
    need(pairs==16 and controller['prefix_pairs']==7 and h==9 and v==112 and ambient==145,
         'Supported source-certified p16/a7 tariff binding')
    return {'schema':'source-caller-invoice/v1','controller_sha256':sha256(canonical(controller)).hexdigest(),
            'invoice':invoice,'orientations':dict(orientations),'calls':calls,
            'local_groups':local_groups,'outer_paid':outer_paid,'main_targets':main,
            'caller_event_counts':dict(events),'ordinary_caller_events':ordinary,
            'ordinary_boundary_events':[{'id':f'boundary:{side}:{index}','side':side,'event':index,'operation':operation}
                                        for side in ('left','right')
                                        for index,operation in enumerate(controller['boundaries'][side+'_program'])],
            'boundary_operation_counts':{side:len(controller['boundaries'][side+'_program']) for side in ('left','right')},
            'totals':{'paid':sum(paid.values()),'targets':sum(targets.values()),
                      'rank_surplus':sum(r*n for r,n in targets.items())-sum(r*n for r,n in paid.items())}}
