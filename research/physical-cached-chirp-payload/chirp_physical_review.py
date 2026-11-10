"""Separate original-angle and completed-product checks of physical chirp output.

Expected phases use one common-denominator exponent, not the cached suffix
program, its coefficient pages, or the producer's pi/Taylor implementation.
Prepared for @CubeJerry with separate source-aware OpenAI verification.
"""
from fractions import Fraction
from pathlib import Path
from hashlib import sha256
from math import prod
from types import ModuleType,FunctionType,MethodType,BuiltinFunctionType
import importlib.util


def need(value,message):
    if not value:raise ValueError(message)


def oracle_module():
    spec=importlib.util.spec_from_file_location('physical_half_angle_oracle',
        Path(__file__).with_name('dyadic_chirp_oracle.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def power_enclosure(oracle,radix,exponent,bits):
    unit=1<<bits;exponent%=2*radix
    if (4*exponent)%(2*radix)==0:
        pair=((unit,0),(0,-unit),(-unit,0),(0,unit))[(2*exponent//radix)%4]
        return pair[0],pair[0],pair[1],pair[1]
    base=oracle.primitive(radix,bits);result=(unit,unit,0,0)
    while exponent:
        if exponent&1:result=oracle.multiply(result,base,bits)
        exponent>>=1
        if exponent:base=oracle.multiply(base,base,bits)
    return result


def original_angle_check(radices,slopes,inputs,outputs,precision,bound,conjugate=False):
    """Enclose each exact original pointwise output independently of all caches."""
    oracle=oracle_module();need(len(inputs)==len(outputs)==prod(radices),'original full tensor')
    need(radices[0]==max(radices),'original common dyadic denominator')
    common=radices[0];bits=precision+4*(common.bit_length()-1)+48
    shift=bits-precision;maximum=Fraction(0)
    for index,(source,actual) in enumerate(zip(inputs,outputs)):
        quotient=index;exponent=0
        for radix,slope in zip(radices,slopes):
            coordinate=quotient%radix;quotient//=radix
            need(common%radix==0,'nested dyadic original denominator')
            exponent+=slope*coordinate*coordinate*(common//radix)
        need(quotient==0,'complete original mixed-radix coordinate')
        if conjugate:exponent=-exponent
        phase=power_enclosure(oracle,common,exponent,bits)
        a,b=source;data=(a<<shift,a<<shift,b<<shift,b<<shift)
        expected=oracle.multiply(data,phase,bits)
        error=Fraction(max(abs((actual[0]<<shift)-expected[0]),
                           abs((actual[0]<<shift)-expected[1]))+
                       max(abs((actual[1]<<shift)-expected[2]),
                           abs((actual[1]<<shift)-expected[3])),1<<bits)
        maximum=max(maximum,error)
    need(maximum<=bound,'original-angle complex output bound')
    return dict(method='single original exponent plus half-angle root intervals',
        records=len(inputs),conjugate=conjugate,oracle_bits=bits,
        error_numerator=maximum.numerator,error_denominator=maximum.denominator,
        bound_numerator=Fraction(bound).numerator,bound_denominator=Fraction(bound).denominator)


def snapshot(tapes):
    return tuple((bytes(tape.cells),tape.head) for tape in tapes)


def independent_inventory(owner):
    """Read-only observer: discover reachable roles without using forbidden()."""
    from records import Tape
    seen=set();tapes={};pending=[owner]
    while pending:
        value=pending.pop();identity=id(value)
        if identity in seen:continue
        seen.add(identity)
        if isinstance(value,Tape):tapes[identity]=value;continue
        if isinstance(value,(str,bytes,bytearray,int,float,bool,type(None),type,
                             ModuleType,FunctionType,MethodType,BuiltinFunctionType)):
            continue
        if isinstance(value,dict):pending.extend(value.keys());pending.extend(value.values());continue
        if isinstance(value,(tuple,list,set,frozenset)):pending.extend(value);continue
        if hasattr(value,'__dict__'):pending.extend(vars(value).values())
        for cls in type(value).__mro__:
            slots=cls.__dict__.get('__slots__',())
            if isinstance(slots,str):slots=(slots,)
            for name in slots:
                if name not in ('__dict__','__weakref__') and hasattr(value,name):
                    pending.append(getattr(value,name))
    need(set(tapes)=={id(tape) for tape in owner.forbidden()},
         'independent reachable role inventory equals declared inventory')
    return tuple(tapes.values())


def physical_call(owner,radices,tables,precision,width,values,conjugate=False):
    """Independent fixture harness; body decoding uses literal bit reads."""
    from chirp_tapes import EncodedChirpTables,emit_pairs
    from records import Tape
    from session import erase_marker
    from check_support import no_decode
    from words import BLANK
    with EncodedChirpTables(radices,tables,width,precision) as pages:
        data=Tape();emit_pairs(values,data,pages.width);data.rewind()
        ports=(data,*pages.ports());before=snapshot(ports)
        old_products=owner.arithmetic.products
        try:
            with no_decode():
                result=owner.run(data,pages.shape,pages.tables,pages.width,pages.precision,conjugate)
            need(snapshot(ports)==before,'independent borrowed body and origin preservation')
            actual=[]
            for _ in values:
                row=[]
                for _ in range(2):
                    integer=0
                    for position in range(width):
                        bit=result.read();need(bit in(0,1),'independent physical output binary')
                        integer+=bit<<position;result.step(1)
                    row.append(integer-(1<<width) if integer&(1<<(width-1)) else integer)
                actual.append(tuple(row))
            need(result.read()==BLANK,'independent physical output extent')
            owner.consume();owner.idle()
            need(owner.closed and not owner.pending and not owner.pool.live,
                'independent closed chirp owner')
            roles=independent_inventory(owner)
            need(all(tape.head==1 and all(x==BLANK for x in tape.cells) for tape in roles),
                'independent full retained role erasure')
            return tuple(actual),dict(owned_roles=len(roles),
                scalar_products=owner.arithmetic.products-old_products,
                retained_cells=sum(len(tape.cells) for tape in roles),
                output_sha256=sha256(repr(tuple(actual)).encode()).hexdigest())
        finally:
            if owner.pending:owner.consume()
            data.clear();erase_marker(data)


def run(bundle):
    """Call inside the authenticated physical runtime, after source certification."""
    from chirp_consumer import CachedChirp
    from ring_words import truncate,add,difference
    from router_metadata import owned
    plan=bundle.plan;unit=1<<plan.f;count=prod(plan.radices)
    values=tuple((((i%11)-5)*unit//16,(((2*i)%13)-6)*unit//16) for i in range(count))
    need(all(a*a+b*b<=unit*unit for a,b in values),'independent radius-one actual payload')
    owner=CachedChirp();receipts=[];controls=[]
    for conjugate in (False,True):
        actual,physical=physical_call(owner,plan.radices,bundle.tables,plan.f,plan.W,values,conjugate)
        analytic=original_angle_check(plan.radices,plan.slopes,values,actual,
            plan.f,plan.payload_l1_error,conjugate)
        try:original_angle_check(plan.radices,plan.slopes,values,actual,
                plan.f,plan.payload_l1_error,not conjugate)
        except ValueError as error:
            need(str(error)=='original-angle complex output bound','decisive conjugate angle control')
            controls.append('wrong original conjugation '+str(conjugate))
        else:raise ValueError('wrong original conjugation escaped')
        receipts.append(dict(physical=physical,original_angle=analytic))

    # A completed exact complex sum differs from separately truncated products.
    # This fixture obeys the admitted unit-disk/zero-entry page contract.
    table=(((4,0),(2,-2),(-4,0),(2,-2)),)
    payload=((0,0),(1,1),(0,0),(0,0))
    correct,rounding_receipt=physical_call(owner,(4,),table,2,6,payload)
    need(correct==((0,0),(1,0),(0,0),(0,0)),'completed complex product exact witness')
    class PrematureProducts(CachedChirp):
        def rounded_product(self,left,right,width,precision):
            with owned(self.arithmetic.multiply(left[0],right[0],width),
                       self.arithmetic.multiply(left[1],right[1],width)) as (ac,bd):
                with owned(truncate(ac,precision),truncate(bd,precision)) as (first,second):
                    real=difference(first,second)
            try:
                with owned(self.arithmetic.multiply(left[0],right[1],width),
                           self.arithmetic.multiply(left[1],right[0],width)) as (ad,bc):
                    with owned(truncate(ad,precision),truncate(bc,precision)) as (first,second):
                        imaginary=add(first,second)
                return real,imaginary
            except BaseException:real.close();raise
    wrong,wrong_receipt=physical_call(PrematureProducts(),(4,),table,2,6,payload)
    need(wrong==((0,0),(0,0),(0,0),(0,0)) and wrong!=correct,
        'executed premature-product mutation differs')
    controls.append('executed premature component products')
    return dict(passes=receipts,controls=controls,rounding_control=dict(
        correct=correct,wrong=wrong,physical=rounding_receipt,mutant_physical=wrong_receipt))
