"""Complete physical monomial arrays against direct Gaussian/address oracles."""
from hashlib import sha256
from pathlib import Path
from time import monotonic
import json
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import phase_sources
_native,compact_reference,monomial_reference = phase_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from gaussian_test_support import (GENERIC,body,closed_work,encode_word,native_fixture,oracle,
                                   snapshot)
from monomial_engine import MonomialEngine
from records import Tape
from session import erase_marker
from words import need


def fixture_fields(dimension,f,K,G,dirty_bits=0):
    fields = [("u",(f-1)*G),("t",(f-1)*G)]
    for index in range(dimension):
        fields.append(("v"+str(index),f*K))
        if index == dimension//2:
            fields.append(("dirty",dirty_bits))
    fields.append(("b",(f-1)*G))
    return tuple(fields)


def labelled(records,rows,bits,coefficients):
    base,half = (1<<bits)-1,(1<<(bits-1))-1
    need(coefficients >= 2 and base**(2*(coefficients-1)) >= records*rows, "unique Gaussian record labels")
    result = bytearray()
    for row in range(rows):
        for address in range(records):
            tag = row*records+address
            # The first field fixes orientation under multiplication by a unit.
            values = [(1,0)]
            for field in range(coefficients-1):
                values.append(((tag//base**(2*field))%base-half,
                               (tag//base**(2*field+1))%base-half))
            for real,imag in values:
                result.extend(encode_word(real,bits))
                result.extend(encode_word(imag,bits))
    return bytes(result)


def one_case(literal,f=2,K=1,G=1,rho=0,bits=3,coefficients=3,rows=3,dirty_bits=0,engine=None):
    dimension = len(literal["matrix_rows"])
    vectors = tuple("v"+str(index) for index in range(dimension))
    fields = fixture_fields(dimension,f,K,G,dirty_bits)
    names = tuple(name for name,_width in fields)
    if engine is None:
        engine = MonomialEngine(names,vectors,literal,native_fixture())
    need(engine.names == names, "reuse one fixed field schema")
    widths = tuple(Count.literal(width) for _name,width in fields)
    parameters = [Count.literal(value) for value in (f,K,G,rho,bits,coefficients,rows)]
    saved = snapshot((*widths,*parameters))
    records = 1<<sum(width for _name,width in fields)
    raw = labelled(records,rows,bits,coefficients)
    expected = oracle(raw,fields,vectors,literal,f,K,rho,bits,coefficients,rows)
    source,inverse_source = Tape(),Tape()
    for bit in raw:
        source.append(bit)
    source.rewind()
    before = dict(engine.compact.calls)
    def forbidden(*_args,**_kwargs):
        raise ValueError("indexed monomial oracle reached during physical execution")
    with no_decode(),patch.multiple(monomial_reference,tensor_phase=forbidden,column_phase=forbidden,
                                    column_map=forbidden,columns=forbidden,phase_pass=forbidden,execute_monomial=forbidden), \
            patch.multiple(compact_reference.Compact,execute=forbidden,offset=forbidden,ideal=forbidden,
                           bad=forbidden,select=forbidden,mask=forbidden):
        output = engine.run(source,widths,*parameters)
        need(body(output) == expected, "complete physical Gaussian monomial forward endpoint")
        need(body(source) == raw and source.head == output.head == 1 and snapshot((*widths,*parameters)) == saved,
             "forward preserves borrowed payload and encoded descriptors")
        closed_work(engine)
        for bit in body(output):
            inverse_source.append(bit)
        inverse_source.rewind()
        output.clear()
        erase_marker(output)
        output = engine.run(inverse_source,widths,*parameters,inverse=True)
        need(body(output) == raw, "complete guarded physical monomial inverse")
        need(body(inverse_source) == expected and inverse_source.head == output.head == 1 and
             snapshot((*widths,*parameters)) == saved, "inverse preserves its borrowed input and descriptors")
        closed_work(engine)
    output.clear()
    erase_marker(output)
    for tape in (source,inverse_source):
        tape.clear()
    for value in (*widths,*parameters):
        value.close()
    calls = {name:engine.compact.calls[name]-before[name] for name in before}
    need(bool(calls["ordinary"]) == (f>1 and bool(engine.recipe.word)), "correct one-column/Compact dispatch")
    return engine,dict(dimension=dimension,columns=f,K=K,G=G,rho=rho,component_bits=bits,
                       coefficient_fields=coefficients,outer_rows=rows,records_per_row=records,payload_bits=len(raw),
                       affine_gates=len(engine.recipe.word),compact_calls=calls,parent_peak=engine.pool.peak,
                       compact_peak=engine.compact.pool.peak,forward_sha256=sha256(expected).hexdigest())


def run():
    started = monotonic()
    engine,first = one_case(GENERIC)
    _engine,reuse = one_case(GENERIC,f=1,rows=2,engine=engine)
    print("physical generic monomial seconds",round(monotonic()-started,2),flush=True)
    return dict(cases=[first,reuse],scope="Complete two-column dirty monomial, then one-column reuse on the same physical inventories; exact Gaussian values")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_GAUSSIAN_MONOMIAL")
