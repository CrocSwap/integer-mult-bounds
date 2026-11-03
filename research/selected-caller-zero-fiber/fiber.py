"""Certify the complete caller's first-access zero fiber and its exact code."""

from fractions import Fraction as Q
from hashlib import sha256


def need(ok, label):
    if not ok:
        raise ValueError(label)


def census_forward(word):
    seen, first = set(), {}
    for j,e in enumerate(word['program']):
        op,r=e[:2]
        need(op in {'INIT','CLEAR','MOVE','ADD','COPY','SCALE'},'known source opcode')
        operands=[r]
        if op=='ADD' or op=='COPY':
            operands.append(e[2])
        for field in operands:
            if field not in seen:
                if field<word['public']:
                    first[field]=(j,op)
                seen.add(field)
    cohort=[]
    for field,(j,op) in sorted(first.items(),key=lambda item:item[1][0]):
        if op=='SCALE':
            q=Q(word['program'][j][2])
            if q.denominator>1:
                need(q.denominator==2 and abs(q.numerator)==1,'selected first-access division class')
                cohort.append({'event':j,'field':field,'sign':q.numerator,'frame':word['program'][j][3]})
    return first,cohort


def census_by_field(word):
    first,cohort={},[]
    for role in range(word['public']):
        for j,e in enumerate(word['program']):
            used=e[1]==role
            if e[0] in ('COPY','ADD') and e[2]==role:
                used=True
            if used:
                first[role]=(j,e[0])
                if e[0]=='SCALE':
                    q=Q(e[2])
                    if q.denominator>1:
                        need(q.denominator==2 and abs(q.numerator)==1,'independent division class')
                        cohort.append({'event':j,'field':role,'sign':q.numerator,'frame':e[3]})
                break
    return first,sorted(cohort,key=lambda row:row['event'])


def certify(word,cohort):
    """Track unread independent labels; only their declared halves remove them."""
    secret={x['field']:x for x in cohort}
    state={r:(r if r in secret else None) for r in range(word['public'])}
    frames=dict(enumerate(word['initial']))
    owned=set();consumed=set();coverage=sha256();moves=0;peak_live=len(state)
    for j,e in enumerate(word['program']):
        op,r=e[:2]
        if op=='INIT':
            need(r>=word['public'] and r not in state,'owned allocation')
            state[r]=None;frames[r]=e[2];owned.add(r)
        else:
            need(r in state,'live destination')
            if op=='SCALE' and state[r] is not None:
                row=secret[r]
                need(row['event']==j and Q(e[2])==Q(row['sign'],2),'secret first half')
                need(frames[r]==e[3],'half frame')
                consumed.add(r);state[r]=None
            else:
                need(state[r] is None,'unread input used before its half')
                if op=='MOVE':
                    need(frames[r]==e[2] and bool(e[4])==(r in owned),'native frame and ownership')
                    frames[r]=e[3];moves+=1
                elif op=='CLEAR':
                    need(r in owned and frames[r]==e[2],'owned clear')
                    del state[r];del frames[r];owned.remove(r)
                elif op in ('ADD','COPY'):
                    source=e[2]
                    need(source in state and state[source] is None,'no prior source read')
                    need(r!=source and frames[r]==frames[source]==e[-1],'scalar frames')
                    q=Q(e[-2]);need(q and q.denominator & (q.denominator-1)==0,'dyadic scalar')
                    if op=='COPY':
                        need(q==1 and r in owned,'selected exact COPY')
                elif op=='SCALE':
                    q=Q(e[2]);need(q and q.denominator & (q.denominator-1)==0 and frames[r]==e[3],'ordinary scale')
                else:
                    raise ValueError('unknown instruction')
        remaining={r for r,v in state.items() if v is not None}
        need(remaining==set(secret)-consumed,'every unconsumed label stays private to its input field')
        peak_live=max(peak_live,len(state))
        coverage.update(f'{j}:{op}:{r}:{len(remaining)}:{len(state)};'.encode())
    need(consumed==set(secret) and not owned,'all independent labels removed')
    need(frames==dict(enumerate(word['final'])) and all(v is None for v in state.values()),'complete label-independent endpoint')
    return {'events':len(word['program']),'native_zero_calls':moves,'peak_live_fields':peak_live,
            'all_event_causal_sha256':coverage.hexdigest(),'last_secret_cut':1+max(x['event'] for x in cohort)}


def scalar_tape(word,mode):
    tape=[]
    for j,e in enumerate(word['program']):
        if e[0] in ('ADD','COPY','SCALE'):
            d=Q(e[-2]).denominator
            if mode==0:
                u=0
            elif mode==1:
                u=d-1
            else:
                u=int.from_bytes(sha256(f'zero-fiber:{mode}:{j}'.encode()).digest()[:8],'little')%d
            tape.append(u)
        else:
            tape.append(None)
    return tape


def check_half_seeds(cohort,seeds):
    need(len(seeds)==len(cohort) and all(type(u) is int and u in (0,1) for u in seeds),
         'one retained half seed per cohort field')


def decode_family(word,cohort,n,seeds,packed):
    check_half_seeds(cohort,seeds)
    bits=2*n*len(cohort)
    need(type(n) is int and n>=1 and len(packed)==(bits+7)//8,'packed family length')
    need(not bits%8 or packed[-1] >> (bits%8)==0,'packed zero padding')
    inputs=[[0]*(2*n) for _ in range(word['public'])]
    pos=0
    for item,u in zip(cohort,seeds):
        for k in range(2*n):
            bit=(packed[pos//8] >> (pos%8)) & 1
            inputs[item['field']][k]=item['sign']*(bit-u)
            pos+=1
    return inputs


def encode_family(word,cohort,n,seeds,inputs):
    check_half_seeds(cohort,seeds)
    need(len(inputs)==word['public'] and all(len(v)==2*n for v in inputs),'family input shape')
    roles={x['field'] for x in cohort}
    need(all(all(x==0 for x in row) for r,row in enumerate(inputs) if r not in roles),'outside-family inputs')
    bits=2*n*len(cohort);out=bytearray((bits+7)//8);pos=0
    for item,u in zip(cohort,seeds):
        for value in inputs[item['field']]:
            need(type(value) is int,'integer grid')
            bit=item['sign']*value+u
            need(bit in (0,1),'family bit domain')
            out[pos//8]|=bit << (pos%8);pos+=1
    return bytes(out)


def replay_zero_operands(word,initial,tape):
    """Run every scalar literally; accept a native contract only at zero input."""
    width=len(initial[0]);state={r:list(v) for r,v in enumerate(initial)}
    native_calls=0;record=[];maximum=0
    for j,e in enumerate(word['program']):
        op,r=e[:2]
        if op=='INIT':
            state[r]=[0]*width
        elif op=='CLEAR':
            need(all(v==0 for v in state.pop(r)),'zero retained CLEAR value')
        elif op=='COPY':
            need(all(v==0 for v in state[r]),'zero old COPY value')
            state[r]=state[e[2]].copy()
        elif op=='MOVE':
            need(all(v==0 for v in state[r]),'native zero-operand contract')
            native_calls+=1
        else:
            need(op in ('ADD','SCALE'),'numerical opcode')
            q=Q(e[-2]);u=tape[j]
            need(type(u) is int and 0<=u<q.denominator,'scalar seed domain')
            source=state[r] if op=='SCALE' else state[e[2]]
            divided=[divmod(q.numerator*v+u,q.denominator) for v in source]
            if op=='SCALE':
                if q.denominator>1:
                    record.append((j,[rem for value,rem in divided]))
                state[r]=[value for value,rem in divided]
            else:
                state[r]=[v+z[0] for v,z in zip(state[r],divided)]
        if r in state:
            maximum=max(maximum,max(map(abs,state[r]),default=0))
    need(set(state)==set(range(word['public'])) and all(v==0 for row in state.values() for v in row),'all public outputs zero')
    return record,{'events':len(word['program']),'native_zero_calls':native_calls,'maximum_touched_component':maximum}
