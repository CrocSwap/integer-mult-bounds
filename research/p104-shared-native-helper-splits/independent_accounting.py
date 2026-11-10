"""Independent complete supplier inventory, scalar height and ordinary charge.

@CubeJerry with substantial OpenAI assistance. Apache-2.0.
This is the portable numerical core of the separately recorded frozen46 review.
It imports no construction, endpoint, pricing or interval producer code.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json

def need(value, message):
    if not value:
        raise ValueError(message)


def space(basis):
    found = {0}
    for value in basis:
        need(type(value) is int and 0 < value < 512 and value not in found, 'valid independent frame')
        found |= {old ^ value for old in found}
    return found


def ceil_log2(value):
    k = 0
    while (1 << k) * value.denominator < value.numerator:
        k += 1
    return k


def check_accounting(word,source,caller,expected,bit_data,baseline_caller):
    canonical = lambda data: json.dumps(data,sort_keys=True,separators=(',',':')).encode()
    need(sha256(canonical(word)).hexdigest()==expected['word_payload_sha256'],'word matches expected immutable scientific payload')
    for key in ('frames','ports','live','hosted'):
        need(word[key]==source[key],'unchanged native geometry and hosted contract')
    mains=set(source['live'])|{x+112 for x in source['live']}|set(source['hosted']['X2'])|set(source['hosted']['Y2'])
    need(len(mains)==416,'four disjoint main sets')
    need(all((word['initial'][x],word['final'][x])==(source['initial'][x],source['final'][x]) for x in mains),'exact main endpoint charts')
    edges=lambda value: Counter(tuple(event[2:]) for event in value['program'] if event[0]=='MOVE')
    need(edges(word)==edges(source),'same paid operators with multiplicity')
    dimensions = [len(frame) for frame in word['frames']]
    spans = [space(frame) for frame in word['frames']]
    n = len(word['initial']); total = n + word['owned_fields']
    current = word['initial'][:] + [None] * word['owned_fields']
    active = set(); peak = births = 0
    paid = Counter(); scalar_allowance = scalar_upper = height = 0
    maxq = Q(0); denom_bits = 0
    for index, event in enumerate(word['program']):
        op, target = event[:2]
        need(type(target) is int and 0 <= target < total, 'actual field id')
        if op in ('INIT','CLEAR'):
            need(target >= n, 'only owned reset')
            if op == 'INIT':
                need(target not in active and current[target] is None, 'exclusive birth')
                active.add(target); current[target] = event[2]; births += 1; peak = max(peak,len(active))
            else:
                need(target in active and current[target] == event[2], 'clear current owned frame')
                active.remove(target);current[target] = None
            scalar_allowance += 2
        elif op == 'MOVE':
            old,new,owned = event[2:]
            need(type(owned) is bool and owned == (target in active) and current[target] == old,'actual current owner/frame')
            need(spans[old] < spans[new] or (owned and spans[new] < spans[old]),'legal nested job')
            paid[abs(dimensions[new]-dimensions[old])] += 1
            current[target] = new
        else:
            need(op in ('ADD','COPY','SCALE'),'ordinary scalar alphabet')
            q = Q(event[-2]);frame=event[-1];a,d=abs(q.numerator),q.denominator
            need(q and d & (d-1) == 0 and current[target] == frame,'dyadic scalar at exact current chart')
            maxq=max(maxq,abs(q));denom_bits=max(denom_bits,d.bit_length())
            if op == 'SCALE':
                need(a & (a-1) == 0,'unit dyadic SCALE')
                scalar_allowance += 2*(abs(a.bit_length()-d.bit_length())+int(q<0))
                scalar_upper += 4*(a.bit_length()+d.bit_length()+1)
                height += ceil_log2(max(Q(1),abs(q))) + d.bit_length()-1
            else:
                src=event[2]
                need(type(src) is int and 0<=src<total and src!=target and current[src] == frame,'same exact chart on distinct scalar fields')
                need(op!='COPY' or target in active,'COPY target owned')
                scalar_allowance += 2*(a.bit_length()+a.bit_count()+d.bit_length()+1)
                scalar_upper += 4*(a.bit_length()+a.bit_count()+d.bit_length()+1)
                height += ceil_log2(1+abs(q)) + d.bit_length()-1
    need(not active and current[:n] == word['final'],'complete owned lifetime return and public frames')
    helpers = Counter()
    for role,(old,new) in enumerate(zip(word['initial'],word['final'])):
        if role not in mains:
            need(spans[old] < spans[new],'strict helper job')
            helpers[dimensions[new]-dimensions[old]] += 1
    need(scalar_upper >= scalar_allowance and scalar_upper >= height,'fresh scalar and height envelopes')
    target = Counter(); child = Counter(); calls = lambda_events = queries = 0
    caller_height = 0
    for event in caller['events']:
        op = event[0]
        if op == 'HOST2':
            need(len(set(event[2:])) == 4,'four actual caller fields at each shared native call')
            target.update(helpers);child.update(paid);calls += 1
        elif op == 'QUERY':
            child[1]+=104;queries+=1;caller_height+=16
        elif op == 'IDLE_ONE':
            child[8*len(event[2])]+=104
        elif op == 'LAMBDA':
            need(event[2] in (-1,1),'global LAMBDA orientation')
            lambda_events += 1;caller_height += 8
        elif op in ('ADD','SCALE'):
            q=Q(event[-1]);d=q.denominator
            caller_height += ceil_log2(max(Q(1),abs(q)) if op=='SCALE' else 1+abs(q))+d.bit_length()-1
        else:
            need(op == 'SWAP','known caller scalar opcode');caller_height += 4
    for q,zero,*mask in caller['diagonal']:
        target[int(q%2)+8*sum(mask)] += 104
    need(calls==18 and lambda_events==124 and queries==6,'unchanged caller events')
    need(dict(sorted(target.items())) == {int(k):v for k,v in expected['T'].items()},'complete target invoice')
    need(dict(sorted(child.items())) == {int(k):v for k,v in expected['P'].items()},'complete paid invoice')
    swap_count = lambda selected: len(set(selected)-set(range(len(selected))))
    out_maps=idle_maps=query_maps=0
    for q,zero,*mask in caller['diagonal']:
        axes=([0] if q else [])+[axis for j,on in enumerate(mask,1) if on for axis in range(9+8*(j-1),9+8*j)]
        out_maps += 104*(2*swap_count(axes)+2*bool(q)+int(q==-1))
    for event in caller['events']:
        if event[0]=='IDLE_ONE':
            axes=[axis for j in event[2] for axis in range(9+8*(j-1),9+8*j)]
            idle_maps += 208*swap_count(axes)
        elif event[0]=='QUERY':query_maps += 104*(2+int(event[3]==-1))
    route_count=sum(paid.values())+2*sum(helpers.values())+416+832+4*births
    rest=32*40*104*len(caller['events'])+queries*16*104+40*104*26+(out_maps+idle_maps+query_maps)*1000
    raw=18*(scalar_upper+1000*route_count)+rest
    normalizer_debit=lambda_events*104*1000
    baseline=baseline_caller
    event_saving=len(baseline['events'])-len(caller['events'])
    expected_raw=expected['ordinary']['raw_reviewed_upper']-32*40*104*event_saving
    need(raw==expected_raw and raw+normalizer_debit<10**9,'fresh complete ordinary charge including every LAMBDA translation')
    bit=json.loads(bit_data)
    need(sha1(b'blob '+str(len(bit_data)).encode()+b'\0'+bit_data).hexdigest()=='482f9525d4b75b704018c8d8eba5a00af423dac5','exact #6726 BIT blob verified through GitHub metadata')
    need(Q(bit['ordinary_admitted'])==Q('0.00376669'),'open ordinary BIT pin')
    need(all(Q(item['atom'])==Q(1,250) for item in bit['ordinary_bootstrap']),'actual retuned stock atom')
    k,test=Q(expected['claim']['kappa']),Q(expected['claim']['tested']);gap=(test-k)/7
    need(gap==Q(1,10**11),'fresh exact outer gap')
    uniform,b,a,q=k+6*gap,k+5*gap,k+4*gap,k+3*gap
    eps,beta=1-gap,1-3*gap
    margins=dict(bit_effective=Q(bit['ordinary_admitted'])-a,bit_tested=Q(bit['ordinary_admitted'])-test,
                 main=eps*q-k,leaf=(1-gap)*b-a,semantic_precision=1-eps,
                 actual_bit_stock=beta*(1-Q(1,250)),complex_stock=1-beta)
    need(all(value>0 for value in margins.values()) and 0<q<a<b<uniform<test,'independently derived key precision/stock/outer margins')
    step=gap.denominator;logpower=expected['claim']['logarithm_power']
    wins=lambda j:(step*j+1)**logpower < 1<<j
    lo,hi=1,2
    while not wins(hi):lo,hi=hi,2*hi
    while hi-lo>1:
        mid=(lo+hi)//2
        if wins(mid):hi=mid
        else:lo=mid
    need(wins(hi) and not wins(hi-1),'exact winning compiler-grid threshold')
    report=dict(caller_sha256=sha256(canonical(caller)).hexdigest(),caller_events=len(caller['events']),word_payload_sha256=sha256(canonical(word)).hexdigest(),events=len(word['program']),public=n,helpers=sum(helpers.values()),
                paid_calls_per_native=sum(paid.values()),paid_mass_per_native=sum(r*c for r,c in paid.items()),
                peak_native_owned=peak,native_lifetimes=births,full_productive_fields=sum(target.values()),full_paid_calls=sum(child.values()),
                complete_paid_rank_mass=sum(r*c for r,c in child.items()),complete_target_rank_mass=sum(r*c for r,c in target.items()),
                max_scalar=str(maxq),denominator_bits=denom_bits,scalar_allowance=scalar_allowance,scalar_upper=scalar_upper,
                native_log_height_charge=height,caller_log_height_charge_per_port=caller_height,
                complete_raw_log_height_charge=18*height+104*caller_height,
                route_groups_per_native=route_count,reviewed_raw=raw,lambda_translation_debit=normalizer_debit,
                complete_ordinary_upper=raw+normalizer_debit,ordinary_headroom=10**9-raw-normalizer_debit,
                margins={key:str(value) for key,value in margins.items()},compiler_grid=hi,uniform_rank_log2=step*hi,
                endpoint_scope='This checker verifies typing, source identity, inventory, cost and key margins. Full endpoint/cut algebra and all outer inequalities are separately reviewed source obligations.')
    return report
