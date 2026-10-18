"""Checker-only integer/address oracles and physical fixture construction."""
from pathlib import Path
from types import SimpleNamespace
import json
import phase_sources
_native,compact_reference,monomial_reference = phase_sources.activate()
from cardinal_counts import Count
from macro_code import Code
from ordinary import Ordinary
from words import BLANK,need

GENERIC = dict(matrix_rows=[3,1],offset=1,phase=1,linear_Z4=[1,2],quadratic_rows=[2,0])
SELECTED_PATH = "research/selected-monomial-coordinate-refinement/RECIPE.json"
ADAPTERS_PATH = "research/selected-monomial-coordinate-refinement/sources/RESIDUAL-ADAPTERS.json"


def selected_recipe():
    recipe = json.loads((phase_sources.ROOT/SELECTED_PATH).read_text())
    adapters = json.loads((phase_sources.ROOT/ADAPTERS_PATH).read_text())
    need(recipe == adapters["recipes"]["0:1000"]["right"], "selected directed recipe binding")
    return recipe


def native_fixture(q=2):
    binding = SimpleNamespace(codes=SimpleNamespace(q=q))
    return Ordinary(q,binding,SimpleNamespace(families=0),(Code((("unreachable",),),0),),capacity=64)


def body(tape):
    tape = getattr(tape,"physical",tape)
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def encode_word(value,width):
    return bytes((value>>position)&1 for position in range(width))


def decode_word(bits):
    value = sum(bit<<index for index,bit in enumerate(bits))
    return value-(1<<len(bits)) if bits[-1] else value


def decode_address(index,fields):
    result = {}
    for name,width in reversed(fields):
        result[name],index = index%(1<<width),index>>width
    need(index == 0, "checker complete address")
    return result


def encode_address(state,fields):
    result = 0
    for name,width in fields:
        result = (result<<width)+state[name]
    return result


def oracle_phase(recipe,state,vectors,f,K,rho):
    result = f*recipe["phase"]
    for column in range(f):
        bits = [(state[name]>>(rho+column*K))&1 for name in vectors]
        result += sum(coefficient*bit for coefficient,bit in zip(recipe["linear_Z4"],bits))
        result += 2*sum(bits[i]*bits[j] for i,row in enumerate(recipe["quadratic_rows"])
                        for j in range(i+1,len(vectors)) if row>>j&1)
    return result%4


def oracle_address(recipe,state,vectors,f,K,rho):
    result = dict(state)
    for column in range(f):
        position = rho+column*K
        bits = [(state[name]>>position)&1 for name in vectors]
        for i,name in enumerate(vectors):
            value = ((recipe["offset"]>>i)&1) ^ (sum(((recipe["matrix_rows"][i]>>j)&1)*bit
                                                    for j,bit in enumerate(bits))%2)
            result[name] = (result[name]&~(1<<position)) | (value<<position)
    return result


def rotate_pair(pair,phase):
    matrices = ((1,0,0,1),(0,-1,1,0),(-1,0,0,-1),(0,1,-1,0))
    a,b,c,d = matrices[phase%4]
    x,y = pair
    return a*x+b*y,c*x+d*y


def oracle(raw,fields,vectors,recipe,f,K,rho,bits,coefficients,rows,inverse=False):
    records,record_bits = 1<<sum(width for _name,width in fields),2*bits*coefficients
    output = bytearray(len(raw))
    for row in range(rows):
        for address in range(records):
            state = decode_address(address,fields)
            destination = encode_address(oracle_address(recipe,state,vectors,f,K,rho),fields)
            phase = oracle_phase(recipe,state,vectors,f,K,rho)
            origin,target = ((destination,address) if inverse else (address,destination))
            phase = -phase if inverse else phase
            for field in range(coefficients):
                begin = (row*records+origin)*record_bits+2*bits*field
                pair = (decode_word(raw[begin:begin+bits]),decode_word(raw[begin+bits:begin+2*bits]))
                actual = rotate_pair(pair,phase)
                need(all(-(1<<(bits-1)) <= value < 1<<(bits-1) for value in actual), "checker signed headroom")
                begin = (row*records+target)*record_bits+2*bits*field
                output[begin:begin+2*bits] = b"".join(encode_word(value,bits) for value in actual)
    return bytes(output)


def closed_work(engine,include_output=False):
    from check_payload import closed_work as compact_closed
    compact_closed(engine.compact)
    tapes = [*engine.pool.tapes,engine.compact.output]
    if include_output:
        tapes.append(engine.output)
    need(engine.closed and not engine.pool.live, "closed monomial parent inventory")
    need(all(all(bit == BLANK for bit in tape.cells) for tape in tapes), "erased monomial/Compact owned work")


def snapshot(values):
    return [(bytes(getattr(value.tape,"physical",value.tape).cells),value.tape.head) for value in values]
