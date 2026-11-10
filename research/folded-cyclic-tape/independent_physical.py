"""Independent exact original-order diagonal systems and ownership controls.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The expected answer uses d_i*y_i=x_i, not the author's fold or stage oracle.
Host observers and fixture construction remain outside the production call.
"""
from pathlib import Path
import ast, hashlib, json, sys, time

PACKAGE=(Path(sys.argv[1]).resolve() if len(sys.argv)>1
         else Path(__file__).resolve().parent)
sys.path[:0]=[str(PACKAGE),str(PACKAGE.parent/'physical-gaussian-core')]
import gaussian_sources

def need(condition,message):
    if not condition:raise ValueError(message)

with gaussian_sources.opened():
    from folded_consumer import FoldedSolve
    from cardinal_counts import Count
    from records import Tape
    from router_metadata import owned
    from check_support import no_decode
    from session import erase_marker
    from words import BLANK

    def snapshot(tapes):return tuple((bytes(t.cells),t.head) for t in tapes)
    def blank(owner):
        need(owner.closed and not owner.pending and not owner.pool.live,'closed parent')
        need(owner.solver.closed and not owner.solver.pool.live,'closed child')
        for tape in owner.private_tapes():
            need(tape.head==1 and all(x==BLANK for x in tape.cells),'all retained cells erased')
    def write(tape,values,width):
        for value in values:
            need(-(1<<(width-1))<=value<(1<<(width-1)),'fixture signed width')
            raw=value%(1<<width)
            for bit in range(width):tape.append((raw>>bit)&1)
        tape.rewind()
    def read(tape,n,width):
        result=[]
        for _ in range(n):
            raw=0
            for bit in range(width):
                value=tape.read();need(value in (0,1),'binary return')
                raw|=value<<bit;tape.step(1)
            result.append(raw-(1<<width) if raw&(1<<(width-1)) else raw)
        need(tape.read()==BLANK,'complete protected return');return tuple(result)
    def rejected(function,message):
        try:function()
        except ValueError as error:
            need(str(error)==message,('unexpected rejection',str(error),message));return
        raise ValueError('missing rejection: '+message)

    owner=FoldedSolve();receipts=[];controls=[];started=time.monotonic()
    for n,count in ((1,3),(2,2),(3,2),(4,3),(5,2),(8,2),(9,3),(1,1)):
        width,precision,band=12,4,1;unit=1<<precision
        permutation=tuple(i//2 if i%2==0 else n-1-i//2 for i in range(n))
        diagonal=tuple(1<<(i%3) for i in range(n))
        rhs=tuple(((-1 if (i+r)%2 else 1)*(r+1)*(i+1)*4)
                  for r in range(count) for i in range(n))
        lower=(0,)*n
        upper=tuple(value for i in reversed(permutation) for value in (0,unit//diagonal[i]))
        tapes=[Tape() for _ in range(3)]
        for tape,values in zip(tapes,(lower,upper,rhs)):write(tape,values,width)
        with owned(*(Count.literal(v) for v in (n,count,band,width,precision))) as meta:
            inputs=(*tapes,*(c.tape for c in meta));before=snapshot(inputs)
            with no_decode():result=owner.run(*tapes,*meta)
            actual=read(result,n*count,width)
            need(all(diagonal[i%n]*v==x for i,(v,x) in enumerate(zip(actual,rhs))),
                 'direct original diagonal equation')
            need(snapshot(inputs)==before,'borrowed byte/head preservation')
            # The output head is now on its trailing blank; pending ownership
            # must reject reuse independently of that local blank symbol.
            with no_decode():
                rejected(lambda:owner.run(*tapes,*meta),'consume prior folded output')
            need(snapshot(inputs)==before,'pending rejection preserves inputs')
            with no_decode():owner.consume()
            blank(owner)
            if n==2:
                with no_decode():
                    rejected(lambda:owner.run(*tapes,meta[0],meta[0],*meta[2:]),
                             'distinct external folded ports')
                need(snapshot(inputs)==before,'alias rejection preserves inputs')
                controls.append('aliased descriptors rejected')
                deep=owner.solver.word.product.twiddles.pool.tapes[-1]
                private_before=snapshot(owner.private_tapes())
                with no_decode():
                    rejected(lambda:owner.run(tapes[0],tapes[1],deep,*meta),
                             'distinct external folded ports')
                counterfeit=object.__new__(Count);counterfeit.tape=deep
                with no_decode():
                    rejected(lambda:owner.run(*tapes,counterfeit,*meta[1:]),
                             'distinct external folded ports')
                need(snapshot(inputs)==before and snapshot(owner.private_tapes())==private_before,
                     'deep-role alias rejection preserves all physical state')
                controls.append('inactive descendant payload/count aliases rejected')
                tapes[2].step(1);shifted=snapshot(inputs)
                with no_decode():
                    rejected(lambda:owner.run(*tapes,*meta),'canonical folded input origin')
                need(snapshot(inputs)==shifted,'origin rejection preserves shifted head')
                tapes[2].rewind();controls.append('shifted borrowed head rejected')
            receipts.append(dict(n=n,right_hand_sides=count,records=len(actual),
                                 output_sha256=hashlib.sha256(repr(actual).encode()).hexdigest()))
        for tape in tapes:tape.clear();erase_marker(tape)
    controls.append('pending output rejected with head on blank')
    with no_decode():rejected(owner.consume,'one pending folded output')
    controls.append('double consumption rejected');blank(owner)
    successful_calls=dict(owner.solver.word.calls)
    for cause in ('short_rhs','zero_reciprocal'):
        n,count,width,precision,band=3,2,12,4,1;unit=1<<precision
        lhs=(0,)*n;upper=(0,unit)*n;rhs=(4,-8,12,-4,8,-12)
        if cause=='short_rhs':rhs=rhs[:-1]
        else:upper=(0,0,*upper[2:])
        tapes=[Tape() for _ in range(3)]
        for tape,values in zip(tapes,(lhs,upper,rhs)):write(tape,values,width)
        with owned(*(Count.literal(v) for v in (n,count,band,width,precision))) as meta:
            inputs=(*tapes,*(c.tape for c in meta));before=snapshot(inputs)
            reason=('complete opaque binary payload' if cause=='short_rhs'
                    else 'positive rounded boundary pivot reciprocal')
            with no_decode():rejected(lambda:owner.run(*tapes,*meta),reason)
            need(snapshot(inputs)==before,'failed invocation preserves borrowed ports')
            blank(owner);controls.append(cause+' rejected with retained erasure')
        for tape in tapes:tape.clear();erase_marker(tape)
    source=(PACKAGE/'folded_consumer.py').read_text()
    need(not any(isinstance(node,ast.Attribute) and node.attr in ('head','cells','meter')
                 for node in ast.walk(ast.parse(source))),
         'no direct backend state in folded control source')
    receipt=dict(status='PASS_INDEPENDENT_FOLDED_DIAGONAL',fixtures=receipts,
                 controls=controls,seconds=time.monotonic()-started,
                 source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                 successful_scalar_word_calls=successful_calls,
                 all_scalar_word_calls=owner.solver.word.calls,parent_pool_peak=owner.pool.peak)
    print(json.dumps(receipt,sort_keys=True))
