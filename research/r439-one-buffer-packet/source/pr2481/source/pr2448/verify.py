#!/usr/bin/env python3
"""Carry-aware finite packet routing of PR2407's live snapshot window.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
The finite adjacent-record program is not a uniform GL64 compiler.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q, MOD = 3, 9
IDENTITY = (1, 0, 0, 1)
HIGH = tuple(itertools.product(range(Q), repeat=4))
HI_INDEX = {h:i for i,h in enumerate(HIGH)}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def sha(x):
    return hashlib.sha256(x).hexdigest()


def mul(a, b, modulus=MOD):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2)) % modulus
                 for i in range(2) for j in range(2))


def inv(a):
    z = pow((a[0]*a[3]-a[1]*a[2]) % MOD, -1, MOD)
    return tuple(z*v % MOD for v in (a[3], -a[1], -a[2], a[0]))


def join(low, high):
    return tuple(a+Q*b for a,b in zip(low,high))


def split(g):
    return tuple(x % Q for x in g), tuple(x//Q for x in g)


LOW = tuple(a for a in itertools.product(range(Q), repeat=4)
            if (a[0]*a[3]-a[1]*a[2]) % Q)
ROWS = tuple(join(l,h) for l in LOW for h in HIGH)
ROW_INDEX = {g:i for i,g in enumerate(ROWS)}


def pin_check():
    pins = json.loads((HERE/'SOURCES.json').read_text())['files']
    for pin in pins:
        if pin['usage'] == 'input':
            data = (ROOT/pin['path']).read_bytes()
            require(sha(data) == pin['sha256'], 'source SHA256: '+pin['path'])
            blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            require(blob == pin['git_blob'], 'source Git blob: '+pin['path'])
    for pin in json.loads((HERE/'PREDECESSORS.json').read_text())['files']:
        data = (HERE/pin['local_path']).read_bytes()
        require(sha(data) == pin['sha256'], 'predecessor SHA256: '+pin['local_path'])
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                == pin['git_blob'], 'predecessor Git blob: '+pin['local_path'])


def source_window():
    """Reuse, with authentication, the credited PR2407 constructor."""
    spec = importlib.util.spec_from_file_location('credited_pr2407',HERE/'sources/pr2407/verify.py')
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    parent.ROOT = ROOT
    data = parent.inputs()
    word = json.loads(gzip.decompress(data[parent.WORD]))
    witness = json.loads((parent.HERE/'WITNESS.json').read_text())
    split_word, undo, matrix, _ = parent.decompose(word,witness)
    with tempfile.TemporaryDirectory(prefix='packet-routing-') as tmp:
        records,_ = parent.export(split_word,data,Path(tmp)/'split')
        raw = parent.interleave(records,word,undo,matrix,witness)
    digest = sha(b''.join(struct.pack('<6i',*r) for r in raw))
    old = json.loads((parent.HERE/'RESULT.json').read_text())
    require(digest == old['schedules']['interleaved88']['record_sha256'], 'literal RAW6 binding')
    start = next(i for i,r in enumerate(raw) if r[0]==2 and r[1]==472)
    end = next(i for i in range(start+1,len(raw)) if raw[i][0]==3)
    require(raw[start]==(2,472,661,510,0,7) and raw[end]==(3,472,661,510,0,0),
            'snapshot boundary transports')
    events=[]
    for op,d,s,c,f,phase in raw[start+1:end]:
        require(op==1 and c==1 and f==0 and 111<=d<222 and
                (111<=s<222 or s==661) and d!=s, 'interior event contract')
        events.append((d-111,111 if s==661 else s-111))
    require(len(events)==313 and sum(s==111 for d,s in events)==10, 'window inventory')
    baseline=[(i,111) for i,row in enumerate(matrix) if row&1]
    baseline += [(d-111,s[0]-111) for _,d,s in undo]
    require(len(baseline)==319, 'split baseline inventory')
    require(columns(events)==columns(baseline), 'independent split endpoint')
    return events,baseline,{'RAW6_sha256':digest,'start':start,'end':end,
                           'window_sha256':sha(canonical(events))}


def columns(events):
    """Logical 112-column linear map; no address-routing implementation."""
    out=[1<<i for i in range(112)]
    for d,s in events:
        require(0<=d<111 and 0<=s<=111 and d!=s, 'logical role domain')
        out[d] ^= out[s]
    return out


def chart(role):
    # Fixed nonidentity, generally nonorthogonal unit charts. This is a
    # reduced GL2 fixture, NOT the selected 64-dimensional owner chart.
    upper=(1,1+role%8,0,1)
    lower=(1,0,1+(role//8)%8,1)
    scale=(2 if role%2 else 4,0,0,1)
    a=mul(mul(upper,lower),scale)
    require(a!=IDENTITY and mul(a,inv(a))==IDENTITY, 'fixture chart')
    return a


def digit_route(low,high,a,omit_carry=False):
    """Separate low/high digit arithmetic, not full-ring multiplication."""
    target_low=[];target_high=[]
    for i in range(2):
        for j in range(2):
            low_sum=sum(low[2*i+k]*a[2*k+j] for k in range(2))
            high_sum=sum(high[2*i+k]*a[2*k+j] for k in range(2))
            target_low.append(low_sum%Q)
            target_high.append((high_sum+(0 if omit_carry else low_sum//Q))%Q)
    return tuple(target_low),tuple(target_high)


def compile_route(low,a,omit_carry=False):
    destinations=[];result_low=None
    for h in HIGH:
        lo,hi=digit_route(low,h,a,omit_carry)
        if result_low is None: result_low=lo
        require(result_low==lo, 'route leaves one complete low packet')
        destinations.append(HI_INDEX[hi])
    require(sorted(destinations)==list(range(81)), 'route not bijective')
    # Compile the fixed permutation to adjacent record swaps. Planning is
    # finite control work; the table size is NOT uniformly bounded in w.
    desired=[0]*81
    for source,destination in enumerate(destinations): desired[destination]=source
    current=list(range(81));swaps=[]
    for target,wanted in enumerate(desired):
        position=current.index(wanted,target)
        while position>target:
            swaps.append(position-1)
            current[position-1],current[position]=current[position],current[position-1]
            position-=1
    require(current==desired, 'adjacent compiler')
    return result_low,tuple(swaps),tuple(destinations)


def execute_route(packet,program,meter):
    lo,swaps,_=program
    values=packet[1];head=0
    meter['route_actions']+=1
    for pos in swaps:
        # Declared record-level swap path p,p+1,p,p+1. This is a record
        # tariff, not measurement of bit-level head movement or control work.
        meter['route_head_record_steps']+=abs(pos-head)+3
        meter['adjacent_record_swaps']+=1
        meter['route_record_reads']+=2;meter['route_record_writes']+=2
        values[pos],values[pos+1]=values[pos+1],values[pos]
        head=pos+1
    meter['route_head_record_steps']+=head
    meter['route_head_returns']+=1
    return lo,values


def select_packet(family,low,meter):
    # Literal full-family selector scan, preserving unselected records.
    values=[]
    for row,g in enumerate(ROWS):
        meter['selection_record_reads']+=1
        if split(g)[0]==low:
            values.append(family[row]);meter['selection_record_writes']+=1
    meter['selection_scans']+=1
    meter['selection_head_record_steps']+=2*len(ROWS)
    require(len(values)==81, 'complete packet selection')
    return low,values


def replace_packet(family,packet,meter,write_unowned=False):
    low,values=packet;k=0
    for row,g in enumerate(ROWS):
        meter['replacement_record_reads']+=1
        if split(g)[0]==low:
            family[row]=values[k];k+=1
        meter['replacement_record_writes']+=1
    if write_unowned:
        row=next(i for i,g in enumerate(ROWS) if split(g)[0]!=low)
        family[row]=frozenset()
    meter['replacement_scans']+=1
    meter['replacement_head_record_steps']+=2*len(ROWS)
    require(k==81, 'complete packet replacement')


def discard_packet(packet,meter):
    # Charged logical deletion of redundant fresh copies, not a reversible
    # dirty-ancilla operation. Explicitly clear every finite buffer record.
    values=packet[1]
    for i in range(len(values)):
        values[i]=frozenset()
        meter['fresh_packet_records_erased']+=1
    meter['fresh_packet_head_record_steps']+=2*len(values)
    meter['fresh_packet_head_returns']+=1
    require(not any(values), 'fresh work did not close')


def execute(events,baseline,mutation=None):
    common=IDENTITY
    charts=[chart(r) for r in range(111)]
    lows=[mul(common,inv(a),Q) for a in charts]
    forward=[compile_route(l,a,mutation=='carry') for l,a in zip(lows,charts)]
    backward=[compile_route(common,inv(a)) for a in charts]
    # Atom (role,row) is an arbitrary complete spectator/payload record.
    # A symmetric difference is exact for every assignment of ALL its bits.
    families=[[frozenset(((r,i),)) for i in range(len(ROWS))] for r in range(111)]
    snapshot=[frozenset(((111,i),)) for i in range(81)]
    original_snapshot=tuple(snapshot)
    meter=Counter()
    for event_index,(dst,src) in enumerate(events):
        target=select_packet(families[dst],lows[dst],meter)
        target=execute_route(target,forward[dst],meter)
        require(target[0]==common, 'target alignment')
        if src==111:
            values=snapshot
            if mutation=='snapshot' and event_index==0:
                snapshot[0]=snapshot[0]^frozenset(((999,0),))
        else:
            source=select_packet(families[src],lows[src],meter)
            source=execute_route(source,forward[src],meter)
            require(source[0]==common, 'source alignment')
            values=source[1]
        for i in range(81):
            target[1][i] ^= values[i]
        meter['xor_record_updates']+=81
        meter['xor_record_reads']+=162
        meter['xor_record_writes']+=81
        meter['xor_head_record_steps']+=324
        meter['xor_stream_head_returns']+=2
        if src==111: meter['snapshot_read_head_returns']+=1
        if mutation=='return' and event_index==0:
            # Relabel the packet without actually applying its inverse route.
            target=(lows[dst],target[1])
        else:
            target=execute_route(target,backward[dst],meter)
        require(target[0]==lows[dst], 'target return low class')
        replace_packet(families[dst],target,meter,mutation=='unowned' and event_index==0)
        discard_packet(target,meter)
        if src!=111: discard_packet(source,meter)
        if mutation=='snapshot' and event_index==0:
            snapshot[0]=snapshot[0]^frozenset(((999,0),))
    require(tuple(snapshot)==original_snapshot, 'immutable snapshot exit')
    # Oracle: baseline split word, full-ring owner multiplication, no
    # low/high route code and no reuse of compiled permutations.
    expected_columns=columns(baseline)
    checked=0;changed=0
    for r,family in enumerate(families):
        for row,g in enumerate(ROWS):
            if split(g)[0]!=lows[r]:
                expected=frozenset(((r,row),))
            else:
                d=mul(g,charts[r]);require(split(d)[0]==common,'oracle common packet')
                terms=[]
                for role in range(112):
                    if expected_columns[r]>>role&1:
                        if role==111: terms.append((111,HI_INDEX[split(d)[1]]))
                        else: terms.append((role,ROW_INDEX[mul(d,inv(charts[role]))]))
                expected=frozenset(terms)
            require(family[row]==expected, f'physical endpoint role={r} row={row}')
            changed+=expected!=frozenset(((r,row),));checked+=1
    # Guarded local clear in aligned coordinates; rank-seven physical ERASE
    # transport is outside this fragment and is not simulated here.
    cleared=[a^b for a,b in zip(snapshot,original_snapshot)]
    require(not any(cleared), 'aligned snapshot clear')
    return dict(meter= dict(sorted(meter.items())),checked_target_records=checked,
                changed_target_records=changed,protected_snapshot_records=81,
                unowned_records_checked=111*47*81,
                peak_outer_fresh_packet_records=162,retained_snapshot_records=81,
                adjacent_swap_auxiliary_records=1,
                full_stream_merge_buffer='separate charged stream if replacement is not in-place',
                scope='fixed GL2(Z/9) row-route interpreter; no uniform w or GL64 compiler')


def route_controls():
    cases=0;carry_difference=0
    for low in LOW:
        for a in {chart(r) for r in range(111)}:
            lo,swaps,dest=compile_route(low,a)
            for i,h in enumerate(HIGH):
                actual=join(lo,HIGH[dest[i]])
                require(actual==mul(join(low,h),a), 'independent full-ring route oracle')
                bad_lo,bad_hi=digit_route(low,h,a,True)
                carry_difference+=join(bad_lo,bad_hi)!=actual;cases+=1
            values=list(range(81));expected=list(values);meter=Counter()
            routed=execute_route((low,values),(lo,swaps,dest),meter)
            back=execute_route(routed,compile_route(lo,inv(a)),meter)
            require(back==(low,expected), 'literal forward/inverse route')
    require(carry_difference>0, 'carry mutation has no witness')
    return {'full_ring_route_comparisons':cases,'carry_omission_mismatches':carry_difference}


def run(controls=True):
    pin_check()
    events,baseline,binding=source_window()
    require(columns(events)!=columns(events[:-1]), 'deleted event control')
    result=execute(events,baseline)
    require(result['meter']['route_actions']==929, 'full fragment route ledger')
    result.update(source=binding,route_control=route_controls(),
                  events={'target_undo':303,'snapshot_taps':10},
                  baseline_routes=303*3+16*2,
                  conditional_route_action_difference=12,
                  proof_scope='conditional written packet implication; finite symbolic fixture; no formal kernel',
                  no_new_kappa=True)
    result['inverse_fragment']=execute(list(reversed(events)),list(reversed(baseline)))
    first_seven=list(reversed(events[:7]))+events[7:]
    require(columns(first_seven)==columns(baseline), 'commuting initial taps positive control')
    result['positive_controls']=['inverse fragment on arbitrary fresh inputs',
                                 'seven same-cut taps may be reordered']
    rejected=[]
    if controls:
        for name in ['carry','return','snapshot','unowned']:
            try: execute(events,baseline,name)
            except ValueError as exc:
                require('physical endpoint' in str(exc), name+' wrong failure')
                rejected.append({'mutation':name,'failure':str(exc)})
            else: raise ValueError('mutation accepted: '+name)
        bad=list(events);last=max(i for i,e in enumerate(bad) if e[1]==111)
        bad.insert(0,bad.pop(last))
        try: execute(bad,baseline)
        except ValueError as exc:
            require('physical endpoint' in str(exc), 'tap cut wrong failure')
            rejected.append({'mutation':'wrong tap cut with same counts','failure':str(exc)})
        else: raise ValueError('wrong tap cut accepted')
    result['semantic_controls']=rejected
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true')
    args=p.parse_args();result=run()
    path=HERE/'RESULT.json'
    if args.write: path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: require(result==json.loads(path.read_text()), 'deterministic receipt mismatch')
    print('PASS_R439_PACKET_ROUTING events=313 routes=929 dirty_records=431568 controls=5 no_new_kappa finite_GL2_only')


if __name__=='__main__':main()
