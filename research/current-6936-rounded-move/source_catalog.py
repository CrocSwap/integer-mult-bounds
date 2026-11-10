"""Typed occurrence binding for the exact proposed #6936 raw native word.

All tokens carry this word's hash. The selected #6030 catalogue is unchanged.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from dataclasses import replace
from functools import lru_cache
from hashlib import sha256
import gzip,json
from port_sources import HERE,base,need

B=base();S=B.catalog.S
WORD_SHA='273e81f176f001684b1fa3eb857992bf58b54748004fcfe806b83adb48d2cc00'
NAMESPACE='proposal-6936'

def checked_word(raw):
    need(type(raw) is bytes and sha256(raw).hexdigest()==WORD_SHA,'exact proposed source word')
    return json.loads(gzip.decompress(raw))

def span(basis):
    out={0}
    for value in basis:
        need(type(value) is int and 0<value<512 and value not in out,'independent typed frame basis')
        out|={x^value for x in tuple(out)}
    return frozenset(out)

def source_scan(word):
    """Independent chart/lifetime scan, without scalar endpoint algebra."""
    frames=word['frames'];spaces=[span(x) for x in frames]
    public,owned=word['public'],word['owned_fields'];current=list(word['initial'])+[None]*owned
    need(len(current)==public+owned and len(word['final'])==public,'complete boundary')
    live={};lifetimes=[];paid=Counter();rises=[];peak=0
    for pc,row in enumerate(word['program']):
        op,r=row[:2];need(type(r) is int and 0<=r<public+owned,'typed role')
        if op=='INIT':
            need(r>=public and r not in live and current[r] is None,'exclusive owned birth')
            current[r]=row[2];live[r]=pc;peak=max(peak,len(live))
        elif op=='CLEAR':
            need(r in live and current[r]==row[2],'matching owned return chart')
            lifetimes.append((r,live.pop(r),pc));current[r]=None
        elif op=='MOVE':
            need(len(row)==5 and type(row[4]) is bool,'typed owned MOVE flag')
            a,b,private=row[2:]
            need(type(a) is type(b) is int and 0<=a<len(frames) and 0<=b<len(frames),
                 'typed frame indices')
            need(current[r]==a and (r in live)==private and (r<public or r in live),
                 'actual source chart and owner lifetime')
            up,down=spaces[a]<spaces[b],spaces[b]<spaces[a]
            need(up or down,'strict nested chart transition')
            need(private or up,'public MOVE ascends')
            rank=abs(len(frames[b])-len(frames[a]));need(1<=rank<=8,'positive source rank')
            paid[rank]+=1
            if private and up:rises.append(pc)
            current[r]=b
        else:
            need(op in ('SCALE','COPY','ADD') and current[r] is not None
                 and current[r]==row[-1],'actual scalar destination chart')
            if op!='SCALE':
                s=row[2];need(type(s) is int and 0<=s<len(current) and s!=r
                              and current[s]==current[r],'scalar contact uses same current chart')
    need(not live and all(x is None for x in current[public:]) and current[:public]==word['final'],
         'complete owned lifetimes and public final charts')
    return dict(paid=dict(sorted(paid.items())),lifetimes=lifetimes,peak=peak,owned_rises=rises)

@lru_cache(maxsize=1)
def catalog():
    word=checked_word((HERE/'data/word.json.gz').read_bytes());scan=source_scan(word)
    events,stats=S.ir.current_local(word);entries={}
    for i,event in enumerate(events):
        if event.op!='PAID':continue
        need(type(event.token) is tuple and len(event.token)==3 and event.token[0]=='local',
             'retained raw source lifting only')
        pc,raw=event.token[1:];need(tuple(word['program'][pc])==raw,'literal raw operand')
        token=(NAMESPACE,WORD_SHA,pc,raw)
        left,child,right=events[i-1:i+2]
        need(left.op==right.op=='SERVICE' and left.fields==right.fields==child.fields
             and left.token==('move-in',)+child.token and right.token==('move-out',)+child.token,
             'complete original chronological triple')
        entries[pc]=(replace(left,token=('move-in',)+token),replace(child,token=token),
                     replace(right,token=('move-out',)+token))
    moves={i for i,row in enumerate(word['program']) if row[0]=='MOVE'}
    pairs=sorted({tuple(word['program'][pc][2:4]) for pc in entries})
    need(set(entries)==moves and len(entries)==6323 and len(pairs)==2961
         and len(word['program'])==71144 and len(word['frames'])==1095,'exact complete proposed source census')
    need(stats['paid']==scan['paid'] and sorted(stats['episodes'])==sorted(scan['lifetimes'])
         and stats['peak_live']==scan['peak']==43,'two source/lifetime scans agree')
    report=dict(word_sha256=WORD_SHA,source_events=71144,frames=1095,raw_moves=6323,
                directed_pairs=2961,rank_occurrences=scan['paid'],owned_lifetimes=len(scan['lifetimes']),
                peak_owned=scan['peak'],owned_rises=len(scan['owned_rises']),
                lifetime_sha256=sha256(json.dumps(sorted(scan['lifetimes'])).encode()).hexdigest(),
                source_word='proposed #6936',selected_frontier_changed=False,
                owned_erase_or_scalar_endpoint_claim=False)
    return word,entries,pairs,report

@lru_cache(maxsize=None)
def frame(index):return S.clifford.canonical_frame(9,tuple(catalog()[0]['frames'][index]))

@lru_cache(maxsize=None)
def chart(start,stop):
    original=frame(start).adjoint().then(frame(stop));record,_compiled=S.clifford.lower_child(original)
    frames=catalog()[0]['frames'];rank=abs(len(frames[stop])-len(frames[start]))
    need(record['rank']==rank and 1<=rank<=8,'actual proposed source Fourier rank')
    return original,record

def bind_paid(event):
    token=event.token
    need(type(token) is tuple and len(token)==4 and token[0]==NAMESPACE and token[1]==WORD_SHA
         and type(token[2]) is int,'exact word-namespaced raw source token')
    word,entries,_pairs,_report=catalog();need(token[2] in entries,'actual proposed paid position')
    triple=entries[token[2]];need(S.core.same_event(event,triple[1]),'typed proposed owner/rank/source')
    row=word['program'][token[2]];original,record=chart(row[2],row[3])
    return triple,original,record

def bind_move(triple):
    need(len(triple)==3,'complete proposed source triple')
    actual,original,record=bind_paid(triple[1])
    need(all(S.core.same_event(a,b) for a,b in zip(triple,actual)),'exact proposed entrance/child/exit')
    return actual,original,record
