"""Independent physical lower/diagonal/upper masked-shear control.

Finite dyadic fixture, not an actual Reference instance. Prepared for
@CubeJerry with separate OpenAI AI verification. Apache-2.0.
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

    def body(t):
        data=tuple(t.cells[1:])
        return data[:data.index(BLANK)] if BLANK in data else data

    def snapshot(tapes):
        return tuple((bytes(borrowed_tape(t).cells),borrowed_tape(t).head) for t in tapes)

    def encoded(value,width=8):
        return tuple((value>>i)&1 for i in range(width))

    n,b,p=6,2,2
    coupling=tuple(tuple(Q(1,4) if i==2 and j in (0,3,4) else Q()
                         for j in range(n)) for i in range(n))
    lower=tuple(tuple(Q(i==j)+(coupling[i][j] if i//b>j//b else 0)
                     for j in range(n)) for i in range(n))
    upper=tuple(tuple(Q(i==j)+(coupling[i][j] if i//b<=j//b else 0)
                     for j in range(n)) for i in range(n))
    fixture=SimpleNamespace(length=6,E=tuple(range(6)),j_mask=(0,0,1,0,0,0),
        shear_lower=lower,shear_upper=upper,f_lower=((Q(1),),),f_upper=((Q(1),),),block=b,P=p)
    pairs=tuple((3,-3) if i in (0,3,4) else (0,0) for i in range(n))
    expected=oracle.window_action(fixture,pairs)
    need(expected[2]==(0,0),'independent staged support result')
    raw_bits=tuple(bit for i,pair in enumerate(pairs)
                   for bit in (*map(int,'01'+format(i,'03b')+'1'+format(i,'03b')+'10'),
                               *encoded(pair[0]),*encoded(pair[1])))
    source=raw(raw_bits);etable=raw(bit for i in range(n) for bit in format(i,'03b'))
    mask=raw(fixture.j_mask)
    metadata=tuple(Count.literal(x) for x in (1,3,1,0,0,6,1,2,8,2))
    axes,h,tb,axis,round_index,length,selected,block,width,precision=metadata
    pool=ScratchPool(128);scope=OuterScope(pool)
    for t in pool.tapes:erase_marker(t);initialize_marker(t)
    matrices=[];pages=[]
    def rational(value):
        return Rational(Signed(Count.literal(abs(value.numerator)),value<0),
                        Count.literal(value.denominator))
    try:
        with sealed_constructors(),scope.installed():
            for extent,left,right in ((length,lower,upper),(selected,fixture.f_lower,fixture.f_upper)):
                pair=[]
                for data in (left,right):
                    matrix=Matrix(extent,extent,pool,
                        lambda i,j,data=data:rational(data[decode(i)][decode(j)]))
                    matrices.append(matrix);pair.append(matrix)
                with no_decode():pages.append(prepare_pages(*pair,block,width,precision,pool))
        borrowed=(source,etable,mask,*pages[0],*pages[1],*(c.tape for c in metadata))
        before=snapshot(borrowed);leaves=engine.child.kernel.leaves;products=engine.child.products
        with no_decode():returned=engine.run(source,etable,mask,*pages,*metadata)
        output=body(returned)
        oracle.check_record_return(raw_bits,output,{(i,):row for i,row in enumerate(expected)},1,3,1,8)
        with no_decode():engine.consume()
        need(snapshot(borrowed)==before,'support borrowed source/pages/counts preservation')
        need(all(t.head==1 and all(x==BLANK for x in t.cells) for t in engine.forbidden()),
             'support complete owned erasure')
        need(engine.child.products-products==12 and engine.child.kernel.leaves-leaves==84,
             'complete synthetic physical invoice')
        return dict(scope='dyadic support control, not an actual Reference',
                    block=2,rows=6,selected=1,precision=2,physical_matrix_calls=12,
                    physical_scalar_products=84,staged_numerator=0,one_round_numerator=-2,
                    exact_real_value='-9/16',immutable_headers=True)
    finally:
        if engine.pending:engine.consume()
        for bank in pages:
            for tape in bank:tape.clear()
        for matrix in matrices:matrix.close()
        for count in metadata:count.close();erase_marker(count.tape)
        for tape in (source,etable,mask):tape.clear();erase_marker(tape)
        pool.empty()
        for tape in pool.tapes:erase_marker(tape)
