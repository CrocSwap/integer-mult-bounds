from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from sandwich_sources import opened,need

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suite',choices=['leaves','full'],default='leaves');args=parser.parse_args()
    started=time.monotonic()
    with opened():
        from cardinal_counts import Count
        from check_composed import encode
        from check_support import no_decode
        from crt_converter import Converter
        from expansion_check_block import packet_bytes
        from records import Tape
        from ring_check_words import tape,word_bits
        from router_metadata import owned
        from session import initialize_marker,erase_marker,sealed_constructors
        from tensor_engine import Tensor
        from tensor_fixture import finite_chirp,literal_native,p48_setup
        from tensor_router import FullRouter
        from tensor_catalogue import Catalogue
        from tensor_records import bounded_record_io
        from sandwich import Sandwich
        from words import BLANK
        raw=(HERE/'inputs/p48-5x7.bin').read_bytes()
        need(hashlib.sha256(raw).hexdigest()=='7dd7adbe9e8f6d5ffbecd425a72827b31d7222ee51bcd67a4148ebfd03420381','real producer packet')
        catalogue=tape(raw)
        tensor=Tensor(finite_chirp(),FullRouter(literal_native()))
        converter=Converter(FullRouter(literal_native()))
        from entry_controls import construction
        construction(Sandwich,tensor,converter,initialize_marker,erase_marker,need)
        machine=Sandwich(tensor,converter)
        from entry_controls import check
        controls=check(machine,tape,raw,Count,owned,initialize_marker,erase_marker,need)
        if args.suite=='full':
            from sandwich_reference import sandwich
            firstdigits,seconddigits=[127,80,11],[93,28,7]
            expected=sandwich(firstdigits,seconddigits,raw)
            observed=[];original=tensor.run
            def observe(*a,**kw):
                result=original(*a,**kw);observed.append(packet_bytes(result));return result
            tensor.run=observe
            first=tape(b''.join(word_bits(x,8) for x in firstdigits))
            second=tape(b''.join(word_bits(x,8) for x in seconddigits))
            snapshots=[packet_bytes(t) for t in (first,second,catalogue)]
            with owned(Count.literal(8),Count.literal(3)) as (b,q):
                try:machine.run(first,second,catalogue,b,q)
                except ValueError as error:need('production coefficient' in str(error),'finite mode recovery rejection')
                else:raise ValueError('finite mode claimed exact recovery')
                with p48_setup(),no_decode():result=machine.run(first,second,catalogue,b,q,require_recovery=False)
                actual=packet_bytes(result)
                need(observed==[encode(v,50) for v in expected['transforms']],'all three actual Tensor outputs')
                value=sum(v*(256**i) for i,v in enumerate(expected['coefficients']))
                expected_bits=bytes((value>>i)&1 for i in reversed(range(48)))
                need(actual==expected_bits,'literal scaling inverse CRT carry output')
                need([packet_bytes(t) for t in (first,second,catalogue)]==snapshots,'borrowed inputs preserved')
                need(machine.last_counts==dict(conversions=3,transforms=3,pointwise_products=1),'complete call schedule')
                need(machine.closed and not machine.pool.live,'closed full caller')
                receipt=dict(suite='full',source_shape=[5,7],target_shape=[8,8],coefficient_sha256=hashlib.sha256(raw).hexdigest(),output_sha256=hashlib.sha256(actual).hexdigest(),transform_sha256=[hashlib.sha256(v).hexdigest() for v in observed],nonzero_transform_coordinates=[sum(a!=0 or b!=0 for a,b in v) for v in expected['transforms']],counts=machine.last_counts,staged_integer=value,true_integer=sum(v*256**i for i,v in enumerate(firstdigits))*sum(v*256**i for i,v in enumerate(seconddigits)),production_recovery_claim=False)
                machine.consume()
        else:
            from types import SimpleNamespace
            for precision,admitted in ((88,False),(89,True)):
                gamma=2*(8+(32*precision-1).bit_length()+1)
                with owned(*(Count.literal(v) for v in (precision,gamma,2,3,35,1,8))) as (pp,gg,dd,outer,ss,mode,bb):
                    guard=SimpleNamespace(p=pp,gamma=gg,dimensions=dd,outer_bits=outer,source_product=ss,mode=mode)
                    try:machine.admit(guard,bb)
                    except ValueError:need(not admitted,"scalar guard should pass")
                    else:need(admitted,"scalar guard should reject")
            book=Catalogue(catalogue,Tape);plan=book.plan
            # Literal high-precision leaf, supplied dyadic values; no numerical producer claim.
            from types import SimpleNamespace
            with owned(Count.literal(96),Count.literal(98),Count.literal(35),Count.literal(8),Count.literal(132),Count.literal(3)) as (p,component,S,b,width,q):
                leaf=SimpleNamespace(p=p,component_bits=component,source_product=S)
                coefficients=[11811,17506,9658,868,77]+[0]*30
                scale=35*35*(1<<20)
                numerators=[(c*(1<<96)+scale//2)//scale for c in coefficients]
                need(all(2*abs(v*scale-c*(1<<96))<=scale for v,c in zip(numerators,coefficients)),"supplied approximation enclosure")
                need(scale < (1<<96),"strict supplied rounding margin")
                need(any((v*(35*(1<<20))+(1<<95))//(1<<96)!=c for v,c in zip(numerators,coefficients)),"missing one S discriminator")
                need(crt_order(coefficients)!=coefficients,"wrong CRT orientation discriminator")
                values=tape(encode([(v,0) for v in crt_order(numerators)],98))
                for t in (*machine.pool.tapes,machine.output):initialize_marker(t)
                with bounded_record_io(),sealed_constructors(),machine.scope.installed(),no_decode():
                    recovered=machine.recover(values,leaf,b,width)
                    # Independently supplied natural-order expected coefficients exercise carries.
                    recovered_raw=packet_bytes(recovered)
                    need(recovered_raw==b''.join(word_bits(v,132) for v in crt_order(coefficients)),'physical two-S nearest integer')
                    recovered.clear()
                    ordinary=machine.pool.acquire()
                    for bit in b''.join(word_bits(v,132) for v in coefficients):ordinary.append(bit)
                    ordinary.rewind();machine.carries(ordinary,leaf,b,q,width);ordinary.clear()
                    expected=sum(v*256**i for i,v in enumerate(coefficients))
                    need(packet_bytes(machine.output)==bytes((expected>>i)&1 for i in reversed(range(48))),'physical carry bit return')
                    machine.pool.empty()
                machine.output.clear()
                for t in (*machine.pool.tapes,machine.output):erase_marker(t)
                receipt=dict(suite='leaves',precision=96,source_product=35,coefficients=35,physical_two_S=True,physical_carry=True,supplied_approximation=True)
            book.close()
        receipt['entry_controls']=controls
        receipt['seconds']=round(time.monotonic()-started,6)
        print(json.dumps(receipt,sort_keys=True));print('PASS_PHYSICAL_TENSOR_CRT_'+args.suite.upper())

def crt_order(values):
    out=[0]*35
    for k,v in enumerate(values):out[(k%5)*7+(3*k%7)]=v
    return out
if __name__=='__main__':main()
