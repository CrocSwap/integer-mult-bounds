"""Check the phase-covariant provider at the complete retained consumer.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from fractions import Fraction
import hashlib
import importlib.util
from itertools import product
import json
from math import isqrt
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from kernel import pair,layer,call,partner,need
from ports import port
from oracle import add,sub,norm2,phase,ideal_call,ideal_port


def authenticate():
    rows=json.loads((HERE/'ORIGINS.json').read_text())
    for row in rows:
        raw=(HERE/row['path']).read_bytes()
        need(len(raw)==row['size'] and hashlib.sha256(raw).hexdigest()==row['sha256'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'Source bytes')
    spec=importlib.util.spec_from_file_location('retained_rounded',HERE/'predecessor/rounded.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    return old,rows


def squared(values):return sum(norm2(z) for z in values)
def conjugate(z):return z[0],-z[1]


def radial(a,b,f,n):
    # abs(sqrt(b)-sqrt(a)) <= f*sqrt(n)/2, by positive squaring.
    low,high=sorted((a,b));r=4*(high-low)-f*f*n
    return r<=0 or r*r<=16*f*f*n*low


def exact_pair_error(x,y,out,sign):
    sx,sy=add(x,y);dx,dy=sub(x,y)
    target=(sx-sign*dy,sy+sign*dx,sx+sign*dy,sy-sign*dx)
    return sum((2*a-b)**2 for a,b in zip((*out[0],*out[1]),target))


def fibers(values,f,axis):
    mask=sum(1<<(3*j+axis) for j in range(f));out={}
    for i,value in enumerate(values):
        key=i&~mask;out[key]=add(out.get(key,(0,0)),value)
    return out


def port_envelope(out,x,y,f,kind,reverse):
    n=len(x);scale=10**60
    # Lower bounds on the right and an upper bound on the left suffice.
    left=isqrt(squared(out)*scale*scale)+1
    rhs=isqrt(squared(y)*scale*scale)+3*isqrt(squared(x)*scale*scale)
    coefficient=kind-1 if reverse else kind+2
    rhs+=coefficient*f*isqrt(n*scale*scale)//2
    need(left<=rhs,'Full y-bank radial envelope')


def refusal(function):
    try:function()
    except ValueError:return
    raise ValueError('Rejected control was accepted')


def verify():
    old,pins=authenticate()
    # The runtime pair uses only division by the literal two.
    tree=ast.parse((HERE/'kernel.py').read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Div,ast.FloorDiv,ast.Mod)):
            need(isinstance(node.right,ast.Constant) and node.right.value==2,'No variable data division')
    ring_checks=0
    for r in range(1,130,2):
        cycle=[];x,y=r,r
        for dx,dy in [(-2,0),(0,-2),(2,0),(0,2)]:
            for _ in range(r):cycle.append((x,y));x+=dx;y+=dy
        for j,u in enumerate(cycle):
            v=partner(u,{})
            need(v==cycle[j^1],'Retained individual-ring matching')
            need(partner((u[0],-u[1]),{})==(v[0],-v[1]),'Horizontal reflection')
            need(partner((-u[0],-u[1]),{})==(-v[0],-v[1]),'Half turn')
            ring_checks+=1
    pair_count=phase_count=0
    for values in product(range(-4,5),repeat=4):
        x,y=values[:2],values[2:]
        for sign in (-1,1):
            out=pair(x,y,16,sign)
            need(add(*out)==add(x,y),'Exact sum')
            need(exact_pair_error(x,y,out,sign)==4*(sum(values)%2),'Pointwise least Gaussian error')
            need(pair(*out,16,-sign)==(x,y),'Pair inverse')
            need(pair(conjugate(x),conjugate(y),16,sign)==tuple(map(conjugate,pair(x,y,16,-sign))),'Conjugate inverse')
            need(pair(y,x,16,sign)==out[::-1],'Pair exchange')
            need(pair(add(x,(3,-2)),add(y,(3,-2)),16,sign)==tuple(add(z,(3,-2)) for z in out),'Common translation')
            need(radial(norm2(x)+norm2(y),squared(out),1,2),'Sharp pair radial bound')
            for q in range(4):
                need(pair(phase(x,q),phase(y,q),16,sign)==tuple(phase(z,q) for z in out),'All Gaussian phases');phase_count+=1
            pair_count+=1
    widths={}
    for width in (2,3,4):
        limit=1 << (width-1);fitting=rejected=0
        for z in product(range(-limit,limit),repeat=4):
            for sign in (-1,1):
                wide=pair(z[:2],z[2:],width+6,sign)
                fits=all(-limit<=v<limit for a in wide for v in a)
                if fits:
                    need(pair(z[:2],z[2:],width,sign)==wide,'All fitting signed outputs')
                    fitting+=1
                else:
                    refusal(lambda:pair(z[:2],z[2:],width,sign));rejected+=1
        widths[str(width)]={'fitting':fitting,'rejected':rejected}
    sharp=[]
    for k in list(range(1,65))+[2**b+7 for b in [64,256,1024,4096]]:
        w=k.bit_length()+6
        need(pair((0,-k),(1,k),w)==((k+1,0),(-k,0)),'Forward sharpness')
        need(pair((1,-k),(0,k),w,-1)==((-k,0),(k+1,0)),'Inverse sharpness')
        sharp.append(k.bit_length())
    rng=random.Random(370104)
    calls=observables=port_cases=aligned=actual_cuts=0
    work={'butterflies':0,'stored_range_checks':0,'nonzero_roundings':0}
    maximum_error=Fraction(0)
    for f in (1,2,3):
        n=8**f
        for axis,adj,trial in product((0,2),(False,True),range(2)):
            values=[(rng.randrange(-13,14),rng.randrange(-13,14)) for _ in range(n)]
            before=list(values);expected=ideal_call(before,f,axis,adj)
            call(values,f,axis,64,adj)
            need(squared([sub(a,b) for a,b in zip(values,expected)])<=f*f*n//2,'Complete-call Euclidean error')
            need(radial(squared(values),squared(before),f,n),'Complete-call radial envelope')
            need(fibers(values,f,axis)==fibers(before,f,axis),'Every spectator-fiber sum')
            observables+=4**f
            call(values,f,axis,64,not adj);need(values==before,'Complete-call inverse')
            calls+=1
        for kind,reverse in product((2,3),(False,True)):
            g=old.request_bits(4,f,kind,reverse);width=old.signed_width(4,4,f,kind,reverse)
            for trial in range(2):
                x=[(rng.randrange(-11,12),rng.randrange(-11,12)) for _ in range(n)]
                y=[(rng.randrange(-11,12),rng.randrange(-11,12)) for _ in range(n)]
                expected=ideal_port(x,y,f,kind,reverse)
                ax,ay,trace,cuts=port(list(x),list(y),f,kind,reverse,width,call,old,capture=True)
                need(len(cuts)==kind,'All actual paid calls')
                for axis,adj,before,after in cuts:
                    ideal=ideal_call(before,f,axis,adj)
                    need(max(norm2(sub(a,b)) for a,b in zip(after,ideal))<4*(2**f),'Actual-input source tolerance')
                    need(radial(squared(after),squared(before),f,n),'Actual-cut radial envelope')
                    need(fibers(before,f,axis)==fibers(after,f,axis),'Actual-cut fiber sums')
                    actual_cuts+=1
                error=max(norm2(sub(a,b)) for v,w in zip((ax,ay),expected) for a,b in zip(v,w));maximum_error=max(maximum_error,error)
                need(error<=1 << (2*(g-4)),'Retained complete coordinate request')
                need(radial(squared(ax),squared(x),f,n),'Full x-bank radial envelope')
                port_envelope(ay,x,y,f,kind,reverse)
                xx,yy=list(x),list(y);bx,by,t,no_cuts=port(xx,yy,f,kind,reverse,width,call,old)
                need(bx is xx and by is yy and (bx,by)==(ax,ay) and no_cuts==[],'In-place complete port')
                rx,ry,_,_=port(bx,by,f,kind,not reverse,width,call,old)
                need((rx,ry)==(x,y),'Both arbitrary dirty banks return')
                px,py,_,_=port([phase(z) for z in x],[phase(z) for z in y],f,kind,reverse,width,call,old)
                need((px,py)==([phase(z) for z in ax],[phase(z) for z in ay]),'Full-port phase covariance')
                need(trace['butterflies']==kind*f*n//2 and trace['stored_range_checks']==8*trace['butterflies'],'Complete indexed pair count')
                for key in work:work[key]+=trace[key]
                port_cases+=1
            scale=1 << (kind*f)
            x=[(scale*rng.randrange(-3,4),scale*rng.randrange(-3,4)) for _ in range(n)]
            y=[(scale*rng.randrange(-3,4),scale*rng.randrange(-3,4)) for _ in range(n)]
            need(port(list(x),list(y),f,kind,reverse,width,call,old)[:2]==old.port(list(x),list(y),f,kind,reverse,width)[:2]==ideal_port(x,y,f,kind,reverse),'Aligned predecessor port')
            aligned+=1
    witnesses={}
    for z in product(range(-1,2),repeat=4):
        values=[(a,0) for a in z];a=list(values);b=list(values)
        layer(a,0,32);layer(a,1,32);layer(b,1,32);layer(b,0,32)
        if a!=b:
            witnesses['noncommuting_layers']={'input':values,'order_01':a,'order_10':b};break
    need('noncommuting_layers' in witnesses,'Tensor limitation witness')
    z=witnesses['noncommuting_layers']['input'];values=[(0,0)]*64
    for j,index in enumerate([0,1,8,9]):values[index]=z[j]
    initial=list(values);call(values,2,0,32);layer(values,0,32,-1);layer(values,3,32,-1)
    need(values!=initial,'Wrong inverse stage order rejected')
    witnesses['wrong_inverse_stage_order']=z
    x,y=(0,-1),(1,1);fourth=(x,y)
    for _ in range(4):fourth=pair(*fourth,16)
    need(fourth!=(x,y),'Fourth power not promised');witnesses['fourth_power']={'input':[x,y],'output':fourth}
    need(any(not -8<=v<8 for z in pair((7,7),(7,-8),16) for v in z),'Overflow fixture')
    refusal(lambda:pair((7,7),(7,-8),4))
    refusal(lambda:pair((True,0),(0,0),16))
    refusal(lambda:pair((0,0),(0,0),16,True))
    refusal(lambda:call([(0,0)]*8,1,1,16))
    same=[(0,0)]*8;refusal(lambda:port(same,same,1,2,False,16,call,old))
    # A phase-independent matching is the known failed predecessor contract.
    need(pair((0,1),(0,0),16)!=((0,1),(0,0)),'Parity-selected matching is used')
    result={'status':'PASS_PHASE_COVARIANT_RADIAL_PORTS','pair_cases':pair_count,'phase_cases':phase_count,'complete_ring_points':ring_checks,'signed_width_censuses':widths,'sharpness_indices':len(sharp),'largest_input_bits':max(sharp),'complete_call_cases':calls,'exact_fiber_observables':observables,'complete_port_cases':port_cases,'actual_paid_cuts':actual_cuts,'exact_dirty_roundtrips':port_cases,'aligned_predecessor_ports':aligned,'primary_port_work':work,'largest_port_error_squared':str(maximum_error),'source_files':len(pins),'controls':['signed output overflow','Boolean data','Boolean sign','wrong axis','aliased dirty banks','wrong inverse order','phase-independent matching','excluded finite order'],'limitation_witnesses':witnesses,'scope':'Sharp radial phase/conjugate provider and indexed retained ports; no accelerated native or tape admission'}
    return json.loads(json.dumps(result))


if __name__=='__main__':
    result=verify();need(result==json.loads((HERE/'RESULT.json').read_text()),'Retained receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
