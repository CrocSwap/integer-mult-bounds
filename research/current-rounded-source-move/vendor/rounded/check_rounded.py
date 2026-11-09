"""Exact rational and bitstring oracles for literal rounded-leaf controls.

The Fraction oracle is not imported by the production provider. Checker-only
hardware implements the same read/write/unit-move rules as the retained ABI.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contextlib import ExitStack
from fractions import Fraction
from hashlib import sha256
import json
from rounded_sources import HERE,load,need,authenticate
from rounded_leaf import Provider,PaidService,RoundedOverflow,S,A,C,Count

H=load('rounded_physical_hardware',S.root/'vendor/leaf/vendor/atomic/physical_hardware.py')

class Tape(H.Tape):
    def __init__(self,origin=3):
        super().__init__(origin);self.visited_high=origin
        for j in range(origin-1):self.cells[j]=j%2
    def move(self,direction):
        super().move(direction);self.visited_high=max(self.visited_high,self.head)

def put(tape,bits):
    tape.cells[tape.origin:]=bytearray(bits);tape.head=tape.origin
    tape.high=max(tape.high,tape.origin+len(bits))
    tape.visited_high=max(tape.visited_high,tape.origin+len(bits))

def body(tape):
    values=tape.cells[tape.origin:]
    stop=values.index(6) if 6 in values else len(values)
    need(all(v==6 for v in values[stop:]),'no hidden nonblank tail')
    return bytes(values[:stop])

def encode_header(values):
    bits=[]
    for name in S.common.leaf_provider.SCHEMA:
        value=values[name];digits=[(value>>j)&1 for j in range(max(1,value.bit_length()))]
        bits += [1]*len(digits)+[0]+digits
    return bits

def decode_header(bits):
    values={};at=0
    for name in S.common.leaf_provider.SCHEMA:
        start=at
        while at<len(bits) and bits[at]==1:at+=1
        length=at-start;need(length and bits[at]==0,'header unary length');at+=1
        digits=bits[at:at+length];at+=length
        need(len(digits)==length and (length==1 or digits[-1]==1),'header canonical digits')
        values[name]=sum(x<<j for j,x in enumerate(digits))
    need(at==len(bits),'complete header');return values

def encode_components(values,h):
    bits=[]
    for value in values:
        need(-(1<<(h-1))<=value<(1<<(h-1)),'oracle signed range')
        for symbol in ([(value>>j)&1 for j in range(h)]+[2]):
            bits += [(symbol>>shift)&1 for shift in (2,1,0)]
    return bits

def decode_components(bits,h):
    need(len(bits)%(3*(h+1))==0,'whole coded components');result=[]
    for start in range(0,len(bits),3*(h+1)):
        symbols=[sum(bits[j+k]<<(2-k) for k in range(3)) for j in range(start,start+3*(h+1),3)]
        need(symbols[-1]==2 and all(x in (0,1) for x in symbols[:-1]),'signed code/delimiter')
        result.append(sum(bit<<j for j,bit in enumerate(symbols[:-1]))-symbols[-2]*(1<<h))
    return result

def descriptor(h,f=1,rank=1,a=None,K=1,rho=0,active=0,coefficients=1):
    g=rank*f;a=active+g*K if a is None else a
    b=6*coefficients*(h+1)
    return dict(outer=1,rows=1,stock=1,row_bits=(1<<a)*b,within_bits=a,record_bits=b,
                p=9*f,d=9*f,K=K,G=1,H=max(1,f-1),q0=3,qF=0,qB=0,D=9,
                f=f,rho=rho,active_start=active,back_start=a,selected_axes=9*f,
                entry_start=active,remainder=0,cutoff=f)

def bank(rank):
    provider=Provider(rank);work=[Tape(3+j%5) for j in range(provider.port_count)]
    field,context=Tape(9),Tape(11)
    provider.bind(work,A.BinaryContextPort(context))
    return provider,work,field,context

def upward(x):
    y=x+Fraction(1,2);return y.numerator//y.denominator

def exact_positive(values,a,g,K=1,rho=0,active=0):
    out=[(Fraction(re),Fraction(im)) for re,im in values]
    for j in range(g):
        bit=a-1-(active+j*K+rho)
        nxt=out[:]
        for x in range(1<<a):
            if x&(1<<bit):continue
            y=x|(1<<bit);ar,ai=out[x];br,bi=out[y]
            nxt[x]=((ar-ai+br+bi)/2,(ar+ai-br+bi)/2)
            nxt[y]=((ar+ai+br-bi)/2,(-ar+ai+br+bi)/2)
        out=nxt
    return out

def run_case(name,values,h,rank=1,f=1,a=None,K=1,rho=0,active=0,reusable=None,coefficients=1,outer=1,rows=1,source_bound=False):
    provider,work,field,context=bank(rank) if reusable is None else reusable
    source_event=None;service=None
    if source_bound:
        source_event,triple=next((pc,t) for pc,t in S.catalog.catalog()[1].items() if t[1].rank==rank)
        service=PaidService(triple[1]);provider=service.provider
        service.bind(work,{service.owner:A.CodedPort(field)},A.BinaryContextPort(context))
    header=descriptor(h,f,rank,a,K,rho,active,coefficients);header.update(outer=outer,rows=rows)
    a=header['within_bits'];N=1<<a
    need(len(values)==N*outer*rows*coefficients,'complete oracle fibres and records')
    initial=encode_components([v for pair in values for v in pair],h)
    parent=encode_header(header);put(field,initial);put(context,parent)
    exact=[None]*len(values);fibres=[]
    for row in range(outer*rows):
        for coefficient in range(coefficients):
            indices=[(row*N+j)*coefficients+coefficient for j in range(N)];fibres.append(indices)
            answer=exact_positive([values[j] for j in indices],a,rank*f,K,rho,active)
            for j,pair in zip(indices,answer):exact[j]=pair
    rounded=[upward(v) for pair in exact for v in pair]
    squared_error=max(sum((Fraction(rounded[2*j+k])-exact[j][k])**2 for j in indices for k in (0,1)) for indices in fibres)
    need(squared_error<=Fraction(1<<a,2),'one final component rounding has eta_X squared residual')
    need(sum(re*re+im*im for re,im in exact)==sum(re*re+im*im for re,im in values),
         'independent complete-fibre norm oracle')
    expected_overflow=any(not -(1<<(h-1))<=x<(1<<(h-1)) for x in rounded)
    tapes=(*work,field,context);ancestors=[bytes(t.cells[:t.origin]) for t in tapes]
    before=sum(t.actions() for t in tapes);error=None
    try:
        if service is None:provider.run(A.CodedPort(field),A.BinaryContextPort(context))
        else:service.run()
    except RoundedOverflow as caught:error=str(caught)
    need((error is not None)==expected_overflow,'true mathematical final overflow iff')
    wanted=initial if expected_overflow else encode_components(rounded,h)
    need(body(field)==bytes(wanted),'complete rational answer or protected original')
    need(body(context)==bytes(parent),'original parent and global cutoff unchanged')
    need(all(not body(t) for t in work) and all(t.head==t.origin for t in tapes),'all private roles blank at origins')
    need(all(bytes(t.cells[:t.origin])==old for t,old in zip(tapes,ancestors)),'all protected ancestors')
    need(not provider.pool.live and not provider.child.view.active
         and not provider.child.native.pool.live and not provider.child.native.engine.pool.live,'all leases and views closed')
    report=dict(name=name,rank=rank,f=f,h=h,H=h+rank*f+(rank*f+2)//2+1,records=len(values)//coefficients,
                coefficients=coefficients,outer=outer,rows=rows,
                parent_bits=len(parent),V=len(initial),ports=len(work),
                actions=sum(t.actions() for t in tapes)-before,overflow=error,
                endpoint_sha256=sha256(body(field)).hexdigest(),
                private_materialized_extents=[len(t.cells)-t.origin for t in work],
                private_visited_extents=[t.visited_high-t.origin+1 for t in work],
                exact_output=[[str(re),str(im)] for re,im in exact],rounded=rounded,
                squared_error=str(squared_error),squared_eta_X=str(Fraction(1<<a,2)),
                wrapper_live_peak=provider.pool.peak,
                actual_raw_PAID_event=source_event,
                complete_current_producer_witness=False)
    return report,(provider,work,field,context)

def numeric():
    reports=[]
    for name,values,h,rank,f,a,K,rho,active in (
        ('positive-half-ties',[(1,0),(0,0)],3,1,1,1,1,0,0),
        ('negative-half-ties',[(-1,0),(0,0)],3,1,1,1,1,0,0),
        ('two-columns-arbitrary',[(1,-2),(0,1),(-2,1),(1,1)],4,1,2,2,1,0,0),
        ('rank-two-private-cutoff',[(1,0),(0,-1),(-1,1),(2,0)],4,2,1,2,1,0,0),
        ('spectators-offset',[((j*3)%5-2,(j*7)%5-2) for j in range(16)],4,1,1,4,2,1,1),
        ('late-final-overflow',[(0,0),(3,-3),(0,0),(3,3)],3,1,1,2,1,0,0),
    ):
        report,_=run_case(name,values,h,rank,f,a,K,rho,active,source_bound=name=='positive-half-ties');reports.append(report)
    multiple,_=run_case('multiple-rows-coefficients',[((3*j)%5-2,(7*j)%5-2) for j in range(16)],
                        4,a=1,coefficients=2,outer=2,rows=2)
    reports.append(multiple)
    need(reports[0]['rounded']==[1,1,1,0] and reports[1]['rounded']==[0,0,0,1],
         'upward ties distinguish nearest-even, truncation, and odd rounding')
    need(reports[5]['overflow'] is not None and reports[5]['rounded'][:2]==[0,0],
         'late component overflow after a valid staged prefix')
    return dict(cases=reports,positive_leaf_calls=len(reports),generic_rounded_principle_novel=False,
                selected4096_packet=False,whole_MOVE=False)

if __name__=='__main__':
    from argparse import ArgumentParser
    parser=ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=numeric()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('COMPLETE_ROUNDED_POSITIVE_LEAF',json.dumps(dict(cases=len(result['cases']),
        actions=sum(x['actions'] for x in result['cases']),
        final_overflow_rejections=sum(x['overflow'] is not None for x in result['cases']),
        ports=521,whole_MOVE=False),sort_keys=True),flush=True)

