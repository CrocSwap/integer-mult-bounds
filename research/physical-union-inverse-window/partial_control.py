"""Independent padded/partial batch and post-completed-batch failure check.
Finite dyadic support fixture, not an actual Reference instance. Apache-2.0.
Prepared for @CubeJerry with separate source-aware OpenAI AI verification.
"""
from fractions import Fraction as Q


def run(engine, oracle):
    from types import SimpleNamespace
    from cardinal_counts import Count
    from check_support import no_decode
    from records import Tape
    from ring_words import Signed
    from ring_check_words import decode
    from gaussian_matrix import Matrix
    from gaussian_rationals import Rational
    from boundary_pages import prepare_pages
    from scratch_pool import ScratchPool
    from session import OuterScope,initialize_marker,erase_marker,sealed_constructors,borrowed_tape
    from words import BLANK,need

    def raw(bits):
        tape=Tape()
        for bit in bits:tape.append(int(bit))
        tape.rewind();return tape

    def body(tape):
        data=tuple(tape.cells[1:])
        return data[:data.index(BLANK)] if BLANK in data else data

    def snapshot(tapes):
        return tuple((bytes(borrowed_tape(t).cells),borrowed_tape(t).head) for t in tapes)

    def word(value):return tuple((value>>i)&1 for i in range(8))

    identity=oracle.identity(3)
    upper=((Q(1),Q(1,4),Q(0)),(Q(0),Q(1),Q(0)),(Q(0),Q(0),Q(1)))
    fixture=SimpleNamespace(length=3,E=(0,1,2),j_mask=(1,0,0),block=4,P=2,
        shear_lower=identity,shear_upper=upper,f_lower=((Q(1),),),f_upper=((Q(1),),))
    points=tuple((x,y) for x in range(3) for y in range(3))
    pairs=tuple((i*7%19-9,i*11%23-11) for i in range(9))
    expected={}
    for x in range(3):
        for y,pair in enumerate(oracle.window_action(fixture,pairs[3*x:3*x+3])):
            expected[x,y]=pair
    raw_bits=tuple(bit for (x,y),pair in zip(points,pairs)
        for bit in (*map(int,'01'+format(x,'02b')+format(y,'02b')+'11'
                         +format(x,'02b')+format(y,'02b')+'1001'),
                    *word(pair[0]),*word(pair[1])))
    source=raw(raw_bits);etable=raw(bit for y in range(3) for bit in format(y,'02b'))
    mask=raw((1,0,0))
    metadata=tuple(Count.literal(x) for x in (2,2,2,1,1,3,1,4,8,2))
    axes,h,tb,axis,round_index,length,selected,block,width,precision=metadata
    pool=ScratchPool(128);scope=OuterScope(pool)
    for tape in pool.tapes:erase_marker(tape);initialize_marker(tape)
    matrices=[];pages=[]
    def rational(value):
        return Rational(Signed(Count.literal(abs(value.numerator)),value<0),Count.literal(value.denominator))
    try:
        with sealed_constructors(),scope.installed():
            for extent,left,right in ((length,identity,upper),(selected,fixture.f_lower,fixture.f_upper)):
                pair=[]
                for data in (left,right):
                    matrix=Matrix(extent,extent,pool,
                        lambda i,j,data=data:rational(data[decode(i)][decode(j)]))
                    matrices.append(matrix);pair.append(matrix)
                with no_decode():pages.append(prepare_pages(*pair,block,width,precision,pool))
        borrowed=(source,etable,mask,*pages[0],*pages[1],*(c.tape for c in metadata))
        before=snapshot(borrowed);products=engine.child.products;leaves=engine.child.kernel.leaves
        batches=engine.batches
        with no_decode():returned=engine.run(source,etable,mask,*pages,*metadata)
        oracle.check_record_return(raw_bits,body(returned),expected,2,2,2,8)
        with no_decode():engine.consume()
        need(snapshot(borrowed)==before,'partial-batch borrowed preservation')
        need(engine.batches-batches==2 and engine.child.products-products==8
             and engine.child.kernel.leaves-leaves==392,'two batches including one partial complex line')
        source.clear()
        for bit in raw_bits[:-1]:source.append(bit)
        source.rewind()
        before=snapshot(borrowed);products=engine.child.products;leaves=engine.child.kernel.leaves
        batches=engine.batches;calls=engine.calls
        try:
            with no_decode():engine.run(source,etable,mask,*pages,*metadata)
        except ValueError as error:
            need('complete' in str(error),'truncated second-batch payload rejection')
        else:raise ValueError('truncated second batch accepted')
        need(engine.batches-batches==1 and engine.child.products-products==4
             and engine.child.kernel.leaves-leaves==196 and engine.calls==calls,
             'failure occurs after exactly one completed batch and two consumed children')
        need(snapshot(borrowed)==before,'post-completed-batch failure preserves borrowed input')
        engine.idle()
        need(engine.closed and not engine.pending and not engine.pool.live
             and all(t.head==1 and all(x==BLANK for x in t.cells) for t in engine.forbidden()),
             'failure erases completed output plus every owned role')
        return dict(scope='dyadic ownership control, not an actual Reference',
                    rows=3,selected=1,block=4,complex_lines=3,positive_batches=2,
                    final_batch_complex_lines=1,positive_scalar_products=392,
                    failed_call_completed_batches=1,failed_call_scalar_products=196,
                    all_owned_roles_erased=len(engine.forbidden()),immutable_headers=True)
    finally:
        if engine.pending:engine.consume()
        for bank in pages:
            for tape in bank:tape.clear()
        for matrix in matrices:matrix.close()
        for count in metadata:count.close();erase_marker(count.tape)
        for tape in (source,etable,mask):tape.clear();erase_marker(tape)
        pool.empty()
        for tape in pool.tapes:erase_marker(tape)
