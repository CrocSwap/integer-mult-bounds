"""Check output delivery, exact tape bills and unchanged source endpoints.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
for row in json.loads((P/'SOURCES.json').read_text())['files']:
    if row['usage']=='input':path=ROOT/row['path']
    elif row.get('pin'):path=P/'vendor'/Path(row['path']).name
    else:continue
    if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('source hash')
sys.path[:0]=[str(P),str(P/'vendor'),str(ROOT/'research/complex-segment-boundary/source')]
from stack import BASE, BLANK, LEFT, Counts, Stack, Tape, emit, need, rewind
from return_output import return_output
from adapter import Arena
import streams,compact,monomial


def bits(n,salt=0):return tuple((i*17+i//3+salt)%2 for i in range(n))


def snapshot(t):
    cells=t.cells[:]
    while cells and cells[-1]==BLANK:cells.pop()
    return cells,t.head


def load(t,data,head=0,marker=LEFT):
    for bit in data:emit(t,bit)
    rewind(t,marker)
    for _ in range(head):t.move(1)


def bank(k,prefix):
    m=Counts();p=[Tape(bits(prefix,i),counts=m) for i in range(k)]
    c=Tape(bits(prefix+3),BASE,m);d=Tape((),BASE,m);relay=Tape(bits(prefix+5),BASE,m)
    return m,p,c,d,relay


def expect_return(payload,c,d,relay,before,output,target):
    expected=list(before)
    old,head=expected[target];expected[target]=(old+list(output),head)
    need([snapshot(t) for t in (*payload,c,d,relay)]==expected,'complete delivered state')


def small():
    count=0
    for s in range(4):
      for h in range(s+1):
       for dlen,qlen,length,ch,extra in itertools.product(range(3),range(2),range(4),range(4),range(3)):
        if ch>length:continue
        m,p,c,d,r=bank(2,17);load(p[1],bits(s),h);load(d,bits(dlen),marker=BASE)
        before=[snapshot(t) for t in (*p,c,d,r)];start=m.total
        Stack(p,c,d).push([True,True])
        need(m.total-start==4*h+2*s+20+7*dlen+11,'exact push invoice')
        load(d,bits(qlen,1),marker=BASE)
        load(p[0],bits(length,1),ch);load(p[1],bits(extra),extra)
        # Setup and child work are excluded from the boundary-only meter.
        push=4*h+2*s+20+7*dlen+11
        start=m.total
        return_output(p,c,d,r,0,0)
        pop=9*h+2*s+28*2+11*dlen+5*qlen+2*(ch+extra)+5*(length+extra)+17*length+50
        need(m.total-start==pop,'exact return invoice')
        need(push+pop==13*h+4*s+38*2+18*dlen+5*qlen+2*(ch+extra)+5*(length+extra)+17*length+61,'matched invoice')
        expect_return(p,c,d,r,before,bits(length,1),0);count+=1
    return count


def nested(depth,prefix):
    m,p,c,d,r=bank(16,prefix);expected=[]
    for level in range(depth):
        for j in range(1,16):load(p[j],bits((j+level)%7,j),(j+level)%7//2)
        if level==0:load(d,bits(17),marker=BASE)
        else:load(d,bits(17+2*level),marker=BASE)
        expected.append([snapshot(t) for t in (*p,c,d,r)])
        Stack(p,c,d).push([True]*16)
    output=bits(43,1);load(p[0],output,17)
    for before in reversed(expected):
        return_output(p,c,d,r,0,0)
        expect_return(p,c,d,r,before,output,0)
    return m.total


def direct(raw,layout,word):
    out=bytearray(len(raw));w=layout.record_bits
    for i in range(layout.records):
        j=layout.encode(word.ideal(layout.decode(i),True));out[j*w:(j+1)*w]=raw[i*w:(i+1)*w]
    return bytes(out)


def source_case(prefix,late):
    a=Arena([bits(prefix,j) for j in range(16)],bits(prefix+3))
    relay=Tape(bits(prefix+5),BASE,a.counts)
    for mod in (streams,compact,monomial):mod.Tape=a.tape
    parents=[a.tape(streams.Meter(),b'' if j==0 else bits(j+2,j)) for j in range(16)]
    for j,role in enumerate(parents):role.read(0 if j==0 else j//2)
    a.set_descriptor(bits(43));before=[snapshot(t) for t in (*a.payloads,a.control,a.descriptor,relay)]
    a.stack.push(a.present);a.present=[False]*16;a.sizes=[0]*16;a.heads=[0]*16;a.depth+=1
    fields=(('u',1),('t',1))+((('y',2),('x',2)) if late else (('x',2),('y',2)))+(('b',1),)
    layout=compact.Layout(fields,8);word=compact.Compact(1,1,1,0,'x','y',late)
    raw=bytes(bit for i in range(layout.records) for bit in streams.bit_key(i,8))
    child=a.tape(streams.Meter(),raw);out=compact.execute(child,layout,word)
    expected=direct(raw,layout,word);need(bytes(out.data)==expected,'independent compact endpoint')
    a.set_descriptor(bits(17));start=a.counts.total
    state=return_output(a.payloads,a.control,a.descriptor,relay,out.slot,0)
    need(state==[(True,0 if j==0 else j+2,0 if j==0 else j//2) for j in range(16)],'physical parent metadata')
    expect_return(a.payloads,a.control,a.descriptor,relay,before,expected,0)
    return dict(prefix=prefix,late=late,records=layout.records,output_bits=len(expected),return_steps=a.counts.total-start,sha256=hashlib.sha256(expected).hexdigest())


def controls():
    count=0
    for fault in ('relay_dirty','relay_head','parent_nonempty','parent_head','output_symbol','frame_end'):
        m,p,c,d,r=bank(2,9)
        if fault in ('parent_nonempty','parent_head'):load(p[0],(1,),int(fault=='parent_head'))
        Stack(p,c,d).push([True,True]);load(p[1],(0,1,1),1)
        if fault=='relay_dirty':r.write(1)
        if fault=='relay_head':r.move(1)
        if fault=='output_symbol':p[1].cells[p[1].head]=BASE
        if fault=='frame_end':c.cells[c.head-1]=BLANK
        try:return_output(p,c,d,r,1,0)
        except ValueError:count+=1
        else:raise ValueError('accepted control: '+fault)
    return count


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args()
    n=small();nested_rows=[]
    for depth in (1,2,7,31):
        costs=[nested(depth,prefix) for prefix in (16,257,4096)]
        need(len(set(costs))==1,'nested locality');nested_rows.append(dict(depth=depth,steps=costs[0]))
    source=[source_case(prefix,late) for late in (False,True) for prefix in (16,257,4096)]
    for late in (False,True):need(len({r['return_steps'] for r in source if r['late']==late})==1,'source return locality')
    result=dict(status='PASS_CONTINUATION_OUTPUT_RETURN',small_cases=n,nested=nested_rows,source=source,controls=controls(),matched_boundary='13Hp+4Sp+38k+18d+5q+2A+2Hc+5W+17L+61',return_sha256=hashlib.sha256((P/'return_output.py').read_bytes()).hexdigest())
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((P/'RESULT.json').read_text()),'complete typed receipt')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
