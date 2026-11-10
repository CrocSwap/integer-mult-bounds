"""Input-independent same-Reference allocation and actual page serialization.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
from math import prod
from join_sources import need,load,FORWARD

def log2up(value):
    value=Q(value);need(value>0,'positive allocation argument')
    k=value.numerator.bit_length()-value.denominator.bit_length()
    bound=Q(1<<k) if k>=0 else Q(1,1<<-k)
    return k if bound>=value else k+1

def dyadic(value):return 1<<max(0,log2up(value))

def allocation(n,g,h,target,initial_radius_bits):
    H=h**g;R0=1<<initial_radius_bits
    td=target+log2up(10*H**4)
    R2=dyadic((H+1)**5*(R0+1))
    Rstar=dyadic(2*(h+1)**(g+1)*(R2+1))
    V2=1<<((n+1)//2)
    return dict(n=n,g=g,h=h,H=H,target=target,R0=R0,R2=R2,Rstar=Rstar,
                stage_target=td,local_target=td+log2up(V2*g*h**(g-1)),V2=V2)

def upper_matrix(window):
    return tuple(tuple(Q(i==j)-
                 (window.H[i][j] if i in window.I and j in window.J else Q())
                 for j in window.E) for i in window.E)

def build_numeric(runtime,family,*,target=2,initial_radius_bits=0,h=2,incoming=0):
    from admitted_context import prepare
    from source_window import make_window,sufficient_allocation,bandwidth,row_norm,inverse,multiply,identity
    K,g=len(family),len(family[0]);L=family[0][0].size
    n=(K.bit_length()-1)+g*(L.bit_length()-1)
    plan=allocation(n,g,h,target,initial_radius_bits)
    rb=plan['R2'].bit_length()-1;td=plan['stage_target'];q=plan['local_target'];R=plan['Rstar']
    probes=[prepare(runtime,family,direction,target=td,radius_bits=rb) for direction in (True,False)]
    descriptors=[];P=max(incoming,*(p.bits for p in probes))
    for row in family:
        line=[]
        for p in row:
            original=tuple(tuple(p.reference.entry('narrow',p.first+i,p.first+j).value
                                 for j in range(L)) for i in range(L))
            band=max(1,bandwidth(original))
            sufficient=sufficient_allocation(p.reference,band=band,radius=R,target=q,
                incoming=incoming,largest_descriptor=p.reference.target_size)
            P=max(P,sufficient['precision'])
            line.append((p,band,sufficient['block'],sufficient['width']-sufficient['precision']))
        descriptors.append(line)
    windows=[];actions=[];blocks=[];w=P+2
    for line in descriptors:
        wr=[];ar=[];br=[]
        for p,band,b,extra in line:
            window=make_window(p.reference,origin=p.first,length=L,interior_blocks=p.indices,
                band=band,cap=p.cap,block=b,precision=P,width=P+extra,radius=R,target=q)
            M=upper_matrix(window)
            bforward=dyadic(max(2,*(abs(2*i-(2*j+1)) for i,row in enumerate(M)
                                         for j,x in enumerate(row) if x)))
            # Explicit exact source row and column norm admission for all factors.
            dense=[]
            for block in (window.A,inverse(window.A)):
                full=[list(row) for row in identity(L)]
                for i0,i in enumerate(window.I):
                    for j0,j in enumerate(window.I):full[i][j]=block[i0][j0]
                dense.append(tuple(tuple(row) for row in full))
            first=[list(row) for row in identity(L)]
            FI=inverse(window.F);FC=multiply(FI,window.C)
            for i0,i in enumerate(window.J):
                for j0,j in enumerate(window.J):first[i][j]=FI[i0][j0]
                for j0,j in enumerate(window.I):first[i][j]=-FC[i0][j0]
            last=[list(row) for row in identity(L)]
            for i0,i in enumerate(window.I):
                for j0,j in enumerate(window.J):last[i][j]=-window.B[i0][j0]
            for matrix in (*dense,first,last):
                need(max(row_norm(matrix),row_norm(tuple(zip(*matrix))))<=h,
                     'actual source row and column norm bound')
            gamma=max(Q(1),row_norm(M));s=max(sum(x!=0 for x in row) for row in M)
            need(P>=q+log2up(s*R+6)+1,'funded actual forward-action grid')
            w=max(w,P+2+log2up(2*window.root_record_radius+1),
                  P+2+log2up(gamma*(R+1)),p.reference.target_size.bit_length()+2)
            wr.append(window);ar.append(M);br.append(bforward)
        windows.append(wr);actions.append(ar);blocks.append(br)
    # One exact signed carrier for both sparse services; dense widths stay sealed.
    for c,line in enumerate(descriptors):
        for a,(p,band,b,extra) in enumerate(line):
            windows[c][a]=make_window(p.reference,origin=p.first,length=L,interior_blocks=p.indices,
                band=band,cap=p.cap,block=b,precision=P,width=w,radius=R,target=q)
    programs=[prepare(runtime,family,direction,target=td,radius_bits=rb,
                      incoming=P,fractional_bits=P) for direction in (True,False)]
    plan.update(P=P,width=w,incoming=P,labels=K,side=L,radius_bits=rb,
                dense_events=[p.stages for p in programs],dense_widths=[p.data_width for p in programs],
                dense_input_widths=[p.incoming+p.radius_bits+2 for p in programs])
    return programs,windows,actions,blocks,plan

def context_key(row,axis_windows,plan,c):
    description=dict(schema='complete-core-context-v1',coarse=c,
        P=plan['P'],width=plan['width'],
        sources=[dict(reference=p.reference.description_hash,
                      spec=list(p.reference.spec.__dict__.values()),origin=p.first,
                      side=p.size,interiors=p.indices,E=w.E,J=w.J)
                 for p,w in zip(row,axis_windows)])
    raw=json.dumps(description,sort_keys=True,separators=(',',':')).encode()
    return tuple((v>>i)&1 for v in raw for i in reversed(range(8)))

def append_axis(bank,window,pages,block):
    from cardinal_counts import Count
    from router_metadata import owned
    from union_bits import PART_END,BLOCK_START,BLOCK_END,put_count,put_big,copy_until
    bank.append(BLOCK_START)
    with owned(*(Count.literal(x) for x in (len(window.E),len(window.J),block))) as counts:
        for value in counts:put_count(value,bank)
    with owned(Count.literal((window.length-1).bit_length())) as (hb,):
        for coordinate in window.E:
            with owned(Count.literal(coordinate)) as (value,):put_big(value,bank,hb)
    bank.append(PART_END)
    for flag in window.j_mask:bank.append(flag)
    bank.append(PART_END)
    for page in pages:
        if page is not None:page.rewind();copy_until(page,bank);page.rewind()
        bank.append(PART_END)
    bank.append(BLOCK_END)

def prepare_banks(family,windows,actions,blocks,plan):
    """All eight inverse pages and all four action pages are physically built."""
    from records import Tape
    from cardinal_counts import Count
    from scratch_pool import ScratchPool
    from session import OuterScope,sealed_constructors,erase_marker,initialize_marker
    from router_metadata import owned
    from boundary_pages import prepare_pages
    from source_window import physical_factors
    from check_support import no_decode
    from union_bits import PART_END
    from physical_join import FRAME_END
    forward=load('forward_page_source',FORWARD/'pages.py')
    pool=ScratchPool(192);scope=OuterScope(pool)
    for t in pool.tapes:erase_marker(t);initialize_marker(t)
    ibank,fbank,keys=Tape(),Tape(),Tape()
    matrices=[];pages=[]
    try:
        with sealed_constructors(),scope.installed():
            for c,row in enumerate(family):
                key=context_key(row,windows[c],plan,c)
                for tape in (ibank,fbank,keys):
                    for digit in key:tape.append(digit)
                    tape.append(PART_END)
                for a,window in enumerate(windows[c]):
                    with owned(*(Count.literal(x) for x in (window.block,plan['width'],plan['P']))) as (b,w,P):
                        matrices=list(physical_factors(window,pool))
                        for pair in (matrices[:2],matrices[2:]):
                            with no_decode():pages.extend(prepare_pages(*pair,b,w,P,pool))
                        for m in matrices:m.close()
                        matrices=[];append_axis(ibank,window,pages,window.block)
                        for p in pages:p.clear()
                        pages=[]
                    with owned(*(Count.literal(x) for x in (blocks[c][a],plan['width'],plan['P']))) as (b,w,P):
                        matrices=list(forward.physical_factors(actions[c][a],blocks[c][a],plan['P'],pool))
                        with no_decode():pages=list(prepare_pages(*matrices,b,w,P,pool))
                        for m in matrices:m.close()
                        matrices=[];append_axis(fbank,window,(*pages,None,None,None,None),blocks[c][a])
                        for p in pages:p.clear()
                        pages=[]
                ibank.append(FRAME_END);fbank.append(FRAME_END)
        for tape in (ibank,fbank,keys):tape.rewind()
        return ibank,fbank,keys
    finally:
        for m in matrices:m.close()
        for p in pages:p.clear()
        pool.empty()
        for t in pool.tapes:erase_marker(t)
