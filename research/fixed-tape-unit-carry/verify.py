#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the carry controller against an independent coordinate gather model.

Dense execution uses PR2776's independent serialized-table interpreter, which
imports no producer. A sparse execution cross-check is additional evidence.
The all-size result rests on PROOF.md, not finite case counts or saved receipts.
Substantial OpenAI Codex assistance; predecessor credit is retained in NOTICE.md.
"""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bootstrap import load
from carry import build_program


def require(ok, message):
    if not ok:
        raise ValueError(message)


def text(value):
    return json.dumps(value, indent=2) + '\n'


def serialize(program):
    return json.loads(json.dumps(dict(tapes=program.tapes, entry=program.entry,
                                     instructions=program.instructions)))


def table_text(tables):
    """Keep one microinstruction per line for review of the finite machine."""
    chunks=[]
    for name,program in tables.items():
        rows=',\n'.join('      '+json.dumps(row) for row in program['instructions'])
        chunks.append('  '+json.dumps(name)+': {\n    "tapes": 14,\n    "entry": 0,\n'
                      '    "instructions": [\n'+rows+'\n    ]\n  }')
    return '{\n'+',\n'.join(chunks)+'\n}\n'


def gather_oracle(shape, payload, direction):
    """Unrank each output address and gather its unique preimage directly.

    No split lengths, tape counters, instruction labels, or producer helpers.
    """
    p, q, g, s = shape
    output = []
    for destination in range(p*q*g*q*s):
        rest, z = divmod(destination, s)
        rest, y = divmod(rest, q)
        rest, gap = divmod(rest, g)
        prefix, x = divmod(rest, q)
        old_y = (y - direction*(x+1)) % q
        source = ((((prefix*q+x)*g+gap)*q+old_y)*s+z)
        output.append(payload[source])
    return output


def exact_steps(shape):
    p, q, g, s = shape
    v = p*q*q*g*s
    setup = sum(24*n-7*n.bit_count()+15*n.bit_length()+12 for n in shape)
    return setup+36*v+20*p*q*q*g+28*p*q*g+50*p*q+19*p+7*q+g+s+111


def exact_span(shape):
    p, q, g, s = shape
    lengths = [n.bit_length() for n in shape]
    return 3*p*q*q*g*s+p+g+s+2*q+max(lengths)+sum(lengths)+28


def check_dense(dense, table, shape, payload, direction, origins=None):
    require(all(row[1] not in dense.INPUTS for row in table['instructions']
                if row[0] == 'write'), 'static input immutability')
    bank = dense.fixtures(shape, payload, origins)
    answer = gather_oracle(shape, payload, direction)
    result = dense.execute(table, bank, 449*len(payload))
    for i in dense.INPUTS:
        require(result['tapes'][i].snapshot() == bank[i][0], 'input contents')
        require(result['tapes'][i].head == bank[i][1], 'input head return')
    expected, head = dense.marked([dense.ONE if b else dense.ZERO for b in answer], bank[1][1])
    require(result['tapes'][1].snapshot() == expected, 'coordinate endpoint')
    require(result['tapes'][1].head == head, 'output head return')
    for i in dense.WORK:
        require(not result['tapes'][i].snapshot(), 'complete scratch erasure')
        require(result['tapes'][i].head == bank[i][1], 'scratch origin return')
    require(result['steps'] == exact_steps(shape), 'exact transition ledger')
    require(sum(t.high-t.low+1 for t in result['tapes']) == exact_span(shape), 'exact span ledger')
    require(exact_span(shape) <= 41*len(payload), 'span bound')
    return result, answer


def controls(modules, tables):
    d = modules['carry_dense']
    cases = []
    shape = (2, 3, 2, 2)
    bits = [int(i % 7 in (0, 2, 3)) for i in range(72)]
    def reject(name, table, target=1, domain=shape, payload=bits):
        try:
            check_dense(d, table, domain, payload, target)
        except (ValueError, RuntimeError):
            cases.append(name)
        else:
            raise ValueError('undetected control: ' + name)
    reject('correct zero-carry predecessor is not the claimed endpoint',
           serialize(modules['shear'].build_program(False)))
    reject('opposite carry orientation', tables['inverse'])
    code = tables['forward']['instructions']
    transfers = [i for i in range(len(code)-6)
                 if code[i][:] == ['write', 11, 0]
                 and code[i+1] == ['move', 11, -1]
                 and code[i+4] == ['write', 12, 5]
                 and code[i+6] == ['write', 12, 2]]
    require(len(transfers) == 5, 'five explicit transfer sites')
    for label, site in (('missing initial carry', transfers[0]),
                        ('missing carry reset between prefixes', transfers[2]),
                        ('missing carry reset during emission', transfers[4])):
        mutant = copy.deepcopy(tables['forward'])
        mutant['instructions'][site] = ['goto', site+7]
        reject(label, mutant)
    mutant = copy.deepcopy(tables['forward'])
    site = max(i for i, row in enumerate(code) if row == ['write', 2, 0])
    mutant['instructions'][site] = ['write', 2, 1]
    reject('retained scratch origin marker', mutant)
    mutant = copy.deepcopy(tables['forward'])
    site = next(i for i,row in enumerate(code) if row[0]=='branch' and row[1]==0
                and any(pair[0]==1 for pair in row[2]))
    target = next(pair[1] for pair in code[site][2] if pair[0]==1)
    mutant['instructions'][site] = ['goto', target]
    reject('omitted source rewind', mutant)
    mutant = copy.deepcopy(tables['forward'])
    site = next(i for i,row in enumerate(code) if row==['write',1,3])
    mutant['instructions'][site] = ['write',1,4]
    reject('payload corruption', mutant)
    mutant = copy.deepcopy(tables['forward'])
    site = next(i for i,row in enumerate(code) if row[0]=='move')
    mutant['instructions'][site][2] = 2
    reject('nonlocal head movement', mutant)
    # Preserve endpoint and all heads while adding two paid movements.
    mutant=copy.deepcopy(tables['forward'])
    for row in mutant['instructions']:
        if row[0]=='goto':
            row[1]+=2
        elif row[0]=='branch':
            row[3]+=2
            for pair in row[2]:pair[1]+=2
    mutant['instructions']=[['move',13,1],['move',13,-1]]+mutant['instructions']
    try:
        check_dense(d,mutant,shape,bits,1)
    except ValueError as exc:
        require(str(exc)=='exact transition ledger','cost-only control must preserve all endpoints')
        cases.append('correct endpoints with two unbilled head moves')
    else:
        raise ValueError('undetected physical cost control')
    return cases


def run(modules, programs, tables):
    d, m = modules['carry_dense'], modules['machine']
    rng = random.Random(14)
    shapes = set(itertools.product((1,2), range(1,6), (1,2), (1,2)))
    shapes.update(((2,3,4,5), (2,7,3,2), (3,5,2,3)))
    for n in (7,8,15,16,31,32,63,64,127,128):
        for axis in (0,2,3):
            shape = [1,1,1,1]; shape[axis] = n; shapes.add(tuple(shape))
    shapes.update((1,q,1,1) for q in (7,8,15,16,31))
    fixtures = []
    for shape in sorted(shapes):
        p,q,g,s=shape; v=p*q*q*g*s
        fixtures.append((shape,[rng.randrange(2) for _ in range(v)]))
    # Exhaustive small payloads, then complete bases with all spectators present.
    fixtures.extend(((1,2,1,1),list(bits)) for bits in itertools.product((0,1),repeat=4))
    for shape in ((1,3,1,1),(2,2,2,2)):
        p,q,g,s=shape; v=p*q*q*g*s
        fixtures.extend((shape,[int(i==k) for i in range(v)]) for k in range(v))
    dense_cases = sparse_cases = old_comparisons = roundtrips = 0
    total_steps = max_volume = 0
    for index,(shape,bits) in enumerate(fixtures):
        origins=[(i*17-index*3)%41-20 for i in range(14)]
        for name,sign in (('forward',1),('inverse',-1)):
            result,answer=check_dense(d,tables[name],shape,bits,sign,origins)
            dense_cases+=1;total_steps+=result['steps'];max_volume=max(max_volume,len(bits))
            if index < len(shapes):
                old=serialize(modules['shear'].build_program(sign<0))
                baseline=d.check_case(old,shape,bits,sign<0,origins)
                require(result['steps']-baseline['steps']==7,'same-input complete cost delta')
                old_comparisons+=1
            if sparse_cases < 24 and (shape[1]>1 or index<2):
                bank=d.fixtures(shape,bits,origins)
                sparse=m.Machine(programs[name],[m.Tape(cells,head) for cells,head in bank])
                sparse.run(max_steps=449*len(bits))
                require(sparse.steps==result['steps'],'sparse/dense transition count')
                for a,b in zip(sparse.tapes,result['tapes']):
                    require(a.cells==b.snapshot() and a.head==b.head,'sparse/dense complete bank')
                sparse_cases+=1
            if roundtrips < 12 and shape[1]>1 and sign==1:
                _,restored=check_dense(d,tables['inverse'],shape,answer,-1,origins)
                require(restored==bits,'inverse composition');roundtrips+=1
    source_comparisons = 0
    qadic = modules['carry_qadic']
    for radix, width in itertools.product((3,5,7),(1,2)):
        high = radix**(width-1)
        shape = (2,high,2,1)
        payload = [rng.randrange(2) for _ in range(4*high*high)]
        for name, sign in (('forward',1),('inverse',-1)):
            low_x, low_y = radix-1, int(sign==1)
            low, carry = qadic.low_update(low_x,low_y,sign,radix)
            require(carry==sign,'actual low-digit carry')
            meter = qadic.Meter()
            source = qadic.Tape(meter,payload)
            legacy, low_result = qadic.physical_add(source,radix,width,low_x,low_y,sign,
                                                    before=2,middle=2,suffix=1)
            _, actual = check_dense(d,tables[name],shape,payload,sign)
            require(actual==legacy.bits and low_result==low,'literal high-carry specialization')
            require(not meter.ordinary,'no ordinary interchange oracle')
            source_comparisons += 1
    return dict(dense_cases=dense_cases,shapes=len(shapes),sparse_cases=sparse_cases,
                same_input_predecessor_comparisons=old_comparisons,roundtrips=roundtrips,
                actual_nonzero_carry_source_comparisons=source_comparisons,
                maximum_payload_bits=max_volume,total_new_transitions=total_steps,
                semantic_controls=controls(modules,tables))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    args=parser.parse_args()
    if args.emit:
        require(not (HERE/'TABLE.json').exists() and not (HERE/'RESULT.json').exists(),
                'explicit emission refuses existing artifacts')
    modules=load()
    programs={name:build_program(modules,inv) for name,inv in (('forward',False),('inverse',True))}
    require(all(p.tapes==14 and len(p.instructions)==552 for p in programs.values()),'finite program size')
    tables={name:serialize(p) for name,p in programs.items()}
    encoded=table_text(tables)
    if not args.emit:
        require((HERE/'TABLE.json').read_text()==encoded,'exact emitted table bytes')
    result=dict(status='PASS_FIXED_TAPE_UNIT_CARRY',physical_tapes=14,instructions_per_direction=552,
                table_sha256=hashlib.sha256(encoded.encode()).hexdigest(),
                transition_bound='449V',visited_cell_bound='41V',checks=run(modules,programs,tables),
                scope='Unit carry plus or minus one tied to the unit coefficient; all-size written proof, finite implementation evidence; no new kappa')
    if args.emit:
        (HERE/'TABLE.json').write_text(encoded);(HERE/'RESULT.json').write_text(text(result))
    else:
        require((HERE/'RESULT.json').read_text()==text(result),'exact typed receipt bytes')
    print(text(result),end='')


if __name__=='__main__':
    main()
