"""Actual Core RHS and exact-reference two-pass fast-kernel integration checks.
Fixture loading/observers are separate from the physical online consumer.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256


def need(ok,message):
    if not ok:raise ValueError(message)


def body(tape):
    from session import borrowed_tape
    raw=bytes(borrowed_tape(tape).cells)
    end=raw.find(bytes((4,)),1)
    if end<0:end=len(raw)
    need(all(x==4 for x in raw[end:]),'erased observer suffix')
    return raw[1:end]


def decoded(raw,width,precision):
    need(len(raw)%width==0,'whole boundary observer records')
    return [Q(sum(v<<i for i,v in enumerate(raw[j:j+width]))
              -(raw[j+width-1]<<width),1<<precision)
            for j in range(0,len(raw),width)]


def snapshots(tapes):
    from session import borrowed_tape
    return tuple((bytes(borrowed_tape(t).cells),borrowed_tape(t).head) for t in tapes)


def erased(roles):
    from words import BLANK
    need(all(t.head==1 and all(v==BLANK for v in t.cells) for t in roles),
         'all fast-boundary reachable roles erased')


def fixture_pack(streams,rows,block,width,pool):
    """Finite fixture setup: physically interleave actual computed RHS streams.
    Host loop bounds are fixture descriptors, not part of the online theorem.
    """
    from compact_counts import copy_bits
    from router_metadata import indices
    from words import BLANK
    out=pool.acquire();count=len(streams);extent=((rows+block-1)//block)*block
    try:
        for start in range(0,count,block):
            for row in range(extent):
                for column in range(start,start+block):
                    if row<rows and column<count:copy_bits(streams[column],out,width)
                    else:
                        for _ in indices(width):out.append(0)
        need(all(t.read()==BLANK for t in streams),'complete actual RHS input streams')
        for t in streams:t.rewind()
        out.rewind();return out
    except BaseException:out.clear();raise


def case(length=8,block_size=4,column_count=6):
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_core import Core
    from gaussian_matrix import Matrix
    from gaussian_rationals import Rational
    from records import Tape
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    from session import initialize_marker,erase_marker,sealed_constructors,borrowed_tape
    from words import BLANK
    from boundary_pages import BoundaryPages,prepare_pages
    from fast_boundary import FastBoundaryPages
    from caller_fixture import fixture
    from source_pair import first_pass_pair
    from boundary_fraction_oracle import oracle
    need(1<=column_count<=6,'bounded actual caller fixture columns')
    all_tapes=[];original_init=Tape.__init__
    def tracked(t):original_init(t);all_tapes.append(t)
    Tape.__init__=tracked
    try:
        core=Core();offset=len(all_tapes);baseline=BoundaryPages();base_roles=tuple(all_tapes[offset:])
        offset=len(all_tapes);fast=FastBoundaryPages();fast_roles=tuple(all_tapes[offset:])
        need({id(t) for t in fast_roles}=={id(t) for t in fast.forbidden()},
             'constructor census equals full forbidden role set')
        samples=[fixture(length,index) for index in range((column_count+1)//2)]
        lower,upper=samples[0][2:4];n=len(lower);width_int,P=samples[0][-2:]
        need(all(sample[2]==lower and sample[3]==upper for sample in samples),'same exact supplied LU reference')
        dirty=Tape()
        for value in (1,0,1,1,0,1):dirty.append(value)
        dirty.rewind();protected=tuple(t for sample in samples for t in sample[:2])+(dirty,)
        protected_snapshot=snapshots(protected)
        for t in core.pool.tapes:initialize_marker(t)
        rhs=[];pages=();matrices=[];packed=None
        def meter():return tuple(sum(getattr(t.meter,k) for t in all_tapes) for k in ('reads','writes','moves'))
        def delta(before):return tuple(a-b for a,b in zip(meter(),before))
        with owned(Count.literal(n),Count.literal(column_count),Count.literal(block_size),
                   Count.literal(width_int),Count.literal(P)) as (rows,columns,block,width,precision):
            try:
                with sealed_constructors(),core.scope.installed():
                    before=meter();expected_rhs=[]
                    for sample in samples:
                        page,source=sample[:2]
                        with no_decode():pair,header=first_pass_pair(core,page,source)
                        try:
                            need([decoded(body(t),width_int,P) for t in pair]==sample[4],
                                 'actual Core first-pass independent expectation')
                            rhs.extend(pair);expected_rhs.extend(sample[4])
                        finally:header.close()
                    first_pass=delta(before)
                    active_rhs=rhs[:column_count];expected_rhs=expected_rhs[:column_count]
                    def make(value):
                        return Rational(Signed(Count.literal(abs(value.numerator)),value<0),
                                        Count.literal(value.denominator))
                    matrices=[Matrix(rows,rows,core.pool,
                        lambda i,j,data=data:make(data[decode(i)][decode(j)])) for data in (lower,upper)]
                    before=meter()
                    with no_decode():pages=prepare_pages(*matrices,block,width,precision,core.pool)
                    setup=delta(before);before=meter()
                    packed=fixture_pack(active_rhs,n,block_size,width,core.pool)
                    packing=delta(before)
                    metadata=(rows,columns,block,width,precision)
                    ports=(*pages,packed,*(c.tape for c in metadata));saved=snapshots(ports)
                    args=(*pages,packed,*metadata)
                    def execute(owner,roles,is_fast):
                        before=meter();products=owner.products
                        arithmetic=owner.kernel.arithmetic if is_fast else owner.arithmetic
                        scalar=arithmetic.products
                        with core.scope.suspended(),no_decode():
                            returned=owner.run(*args)
                            raw=body(returned)
                            while returned.read()!=BLANK:returned.step(1)
                            if is_fast:
                                pending=snapshots((returned,))
                                try:owner.run(*args)
                                except ValueError as error:
                                    need(str(error)=='consume prior fast-boundary output','specific pending return guard')
                                else:raise ValueError('moved pending output accepted')
                                need(snapshots((returned,))==pending,'pending bytes/head retained')
                                owner.consume()
                            else:returned.clear();erase_marker(returned);owner.idle()
                        bill=delta(before)
                        need(snapshots(ports)==saved and snapshots(protected)==protected_snapshot,
                             'all caller inputs and dirty spectators preserved')
                        erased(roles)
                        return raw,dict(action_scope='checked transaction: run, output head scan, pending guard when fast, consume',
                            reads_writes_moves=bill,total=sum(bill),matrix_products=owner.products-products,
                            scalar_products=arithmetic.products-scalar,owned_roles=len(roles),
                            retained_owned_cells=sum(len(t.cells) for t in roles))
                    old,old_bill=execute(baseline,base_roles,False)
                    actual,new_bill=execute(fast,fast_roles,True)
                    expected=oracle(lower,upper,[list(row) for row in zip(*expected_rhs)],block_size,P)
                    need(actual==old and decoded(actual,width_int,P)==expected,
                         'complete inherited rounded page function')
                    K=(n+block_size-1)//block_size;J=(column_count+block_size-1)//block_size
                    products=2*(2*K-1)*J;ell=block_size.bit_length()-1
                    need(new_bill['matrix_products']==old_bill['matrix_products']==products
                         and old_bill['scalar_products']==products*block_size**3
                         and new_bill['scalar_products']==products*7**ell,
                         'complete fast boundary matrix and scalar census')
                    reused,reuse_bill=execute(fast,fast_roles,True)
                    need(reused==actual and reuse_bill==new_bill,'exact same-owner transaction reuse')
                    controls=[]
                    def reject(arguments,message,label):
                        before=snapshots(ports)
                        try:
                            with core.scope.suspended(),no_decode():fast.run(*arguments)
                        except ValueError as error:need(str(error)==message,'specific boundary guard: '+label)
                        else:raise ValueError('accepted boundary control: '+label)
                        need(snapshots(ports)==before and snapshots(protected)==protected_snapshot,
                             'failed boundary call preserves inputs')
                        fast.idle();erased(fast_roles);controls.append(label)
                    for replacement,label in ((pages[1],'duplicate source'),
                            (width.tape,'metadata as source'),
                            (fast.kernel.word.product.word.pool.tapes[-1],'inactive kernel descendant'),
                            (fast.word.product.twiddles.pool.tapes[-1],'inactive inherited descendant')):
                        reject((replacement,*args[1:]),'external distinct fast-boundary ports',label)
                    with owned(Count.literal(3)) as (three,):
                        reject((*args[:7],three,*args[8:]),'dyadic fast-boundary block size','non-dyadic entry')
                    if n%block_size or column_count%block_size:
                        # Fixture control only: literal movement to a known zero pad.
                        location=(n*block_size if n%block_size else n*block_size*(J-1)+column_count%block_size)*width_int
                        packed.rewind()
                        for _ in range(location):packed.step(1)
                        need(packed.read()==0,'known zero padding control bit');packed.write(1);packed.rewind()
                        altered=snapshots(ports)
                        try:
                            with core.scope.suspended(),no_decode():fast.run(*args)
                        except ValueError as error:need(str(error)=='zero incomplete row/RHS padding','specific nonzero padding guard')
                        else:raise ValueError('accepted nonzero caller padding')
                        need(snapshots(ports)==altered,'bad padding input preserved');fast.idle();erased(fast_roles)
                        for _ in range(location):packed.step(1)
                        packed.write(0);packed.rewind();controls.append('nonzero incomplete padding')
                    if K>1:
                        short=pages[1];extent=len(body(short));short.rewind()
                        for _ in range(extent-1):short.step(1)
                        last=short.read();need(last in (0,1),'last coupling bit');short.write(BLANK);short.rewind()
                        altered=snapshots(ports);completed=fast.kernel.calls
                        try:
                            with core.scope.suspended(),no_decode():fast.run(*args)
                        except ValueError as error:need(str(error)=='complete opaque binary payload','specific truncated coupling guard')
                        else:raise ValueError('accepted truncated coupling')
                        need(fast.kernel.calls==completed+1,'failure follows one completed matrix child')
                        need(snapshots(ports)==altered,'truncated input preserved');fast.idle();erased(fast_roles)
                        need(fast.closed and not fast.pending and not fast.pool.live,'failed outer transaction closed')
                        for _ in range(extent-1):short.step(1)
                        short.write(last);short.rewind();controls.append('short coupling after completed child')
                    need(snapshots(ports)==saved,'all control inputs restored')
                    return dict(reference='exact LU(round_P(S)) from inherited supplied Core fixture; no original-S bridge',
                        source_rows=length,boundary_rows=n,columns=column_count,block=block_size,
                        precision=P,width=width_int,actual_first_pass=first_pass,physical_page_setup=setup,
                        actual_rhs_packing=packing,baseline=old_bill,fast=new_bill,reuse=reuse_bill,
                        full_output_sha256=sha256(actual).hexdigest(),controls=controls,
                        output=[str(value) for value in decoded(actual,width_int,P)])
            finally:
                for t in (*rhs,*pages):t.clear()
                if packed is not None:packed.clear()
                for matrix in matrices:matrix.close()
                core.pool.empty()
                for t in core.pool.tapes:erase_marker(t)
                for t in protected:t.clear();erase_marker(t)
    finally:Tape.__init__=original_init
