#!/usr/bin/env python3
"""Source-bound actual rank-eight child through sequential return boundaries."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import HERE, load, need
import oracle


def result():
    recipe, frame, pins = load()
    import pipeline as physical
    columns = oracle.canonical_columns(frame)
    need(all(oracle.circuit_column(recipe, x) == columns[x] for x in range(512)), 'all canonical frame columns')
    controls = {}
    for name, change in [('right_phase', lambda r:r['right'].__setitem__('phase',(r['right']['phase']+1)%4)),
                         ('right_translation', lambda r:r['right'].__setitem__('offset',r['right']['offset']^1)),
                         ('swapped_adapters', lambda r:r.update(right=r['left'],left=r['right']))]:
        mutant = copy.deepcopy(recipe)
        change(mutant)
        need(any(oracle.circuit_column(mutant,x) != columns[x] for x in range(512)), 'reject ' + name)
        controls[name] = 'REJECT'
    need(any(oracle.circuit_column(recipe,x,tuple(range(1,9))) != columns[x] for x in range(512)), 'wrong child axes')
    controls['wrong_child_axes'] = 'REJECT'
    outer_rows, spectators, coefficients = 3, 2, 2
    bits, fractional = 40, 16
    values = [(((i*7+3)%15-7)*4096, ((i*11+1)%15-7)*4096)
              for i in range(outer_rows*spectators*512*coefficients)]
    raw = physical.encode(values,bits)
    dirty = [bytearray((i*3+i//7)%2 for i in range(37)),
             bytearray((i+i//11)%2 for i in range(40960))]
    ancestor = bytes((i+i//3)%2 for i in range(71))
    meter = physical.Meter()
    grid = physical.Grid(bits,fractional)
    active = physical.TrackingTape(meter,raw)
    inactive = [physical.TrackingTape(meter,x) for x in dirty]
    parked = physical.Park(meter,ancestor)
    output, restored = physical.invoke(active,inactive,parked,recipe,grid,outer_rows,coefficients)
    expected = oracle.apply_columns(values,columns,outer_rows,spectators,coefficients)
    need(physical.decode(output.data,bits) == expected, 'whole forward packet operator')
    need([x.data for x in restored] == dirty and all(x.head==0 for x in restored), 'dirty caller packet return')
    need(parked.cells == ancestor and parked.minimum_head == len(ancestor), 'opaque ancestor untouched')
    output_hash = hashlib.sha256(output.data).hexdigest()
    output, restored = physical.invoke(output,restored,parked,recipe,grid,outer_rows,coefficients,inverse=True)
    need(output.data == raw and [x.data for x in restored] == dirty, 'literal inverse complete return')
    positive = physical.report(meter,grid,parked,recipe)
    # A real extra rounding operation at the child return destroys exactness.
    rounding_meter = physical.Meter()
    rounded = physical.child(physical.TrackingTape(rounding_meter,raw),recipe,
                             physical.Grid(bits,fractional),outer_rows,coefficients,round_child=True)
    need(physical.decode(rounded.data,bits) != expected, 'child return rounding mutation')
    controls['child_return_rounding'] = 'REJECT'
    small = physical.Grid(8,4)
    try:
        small.divide(bytearray([1]+[0]*7),1)
    except ValueError as error:
        need(str(error)=='division discards only reserved zero bits', 'wrong division rejection')
    else:
        raise ValueError('unreserved division accepted')
    controls['unreserved_division'] = 'REJECT'
    # Test the actual same LIFO primitive with unequal dirty packet lengths.
    wrong_meter=physical.Meter()
    wrong_park=physical.Park(wrong_meter,ancestor)
    sizes=[wrong_park.push(physical.TrackingTape(wrong_meter,x)) for x in dirty]
    wrong=[wrong_park.pop(n).data for n in sizes]
    need(wrong != dirty and wrong_park.cells == ancestor, 'wrong pop ordering')
    controls['wrong_parking_order']='REJECT'
    try:
        wrong_park.pop(1)
    except ValueError as error:
        need(str(error)=='opaque ancestor boundary', 'wrong stack floor rejection')
    else:
        raise ValueError('ancestor read allowed')
    controls['ancestor_boundary']='REJECT'
    return {'schema_version':1,'source_child_index':1522,'source_event_index':12553,
            'old_frame':415,'new_frame':0,'rank':8,'columns':1,
            'canonical_frame_basis':frame,'exact_operator_columns':512,
            'exact_nonzero_coefficients':sum(len(c) for c in columns),
            'complete_operator_entries':512*512,'operator_denominator':256,
            'outer_rows':outer_rows,'complete_spectator_values':spectators,
            'address_records':outer_rows*spectators*512,'coefficients_per_record':coefficients,
            'word_bits':bits,'fractional_bits':fractional,'initial_fractional_bits':4,
            'packet_bits':len(raw),'dirty_caller_bits':[len(x) for x in dirty],
            'ancestor_bits':len(ancestor),'forward_output_sha256':output_hash,
            'exact_inverse':True,'dirty_packets_restored':True,'scratch_closed':True,
            'positive_forward_and_inverse':positive,'rejected_controls':controls,
            'selected_member_sha256':pins,
            'scope':'Actual f=1 selected leaf child and its return boundary; no compact f>1 or all-depth supplier admission.'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',type=Path)
    args=parser.parse_args()
    receipt=result()
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as target:
            target.write(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else:
        need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==
             json.dumps(receipt,sort_keys=True),'receipt mismatch')
    print('PASS_SELECTED_CHILD_STREAM_RETURN child=1522 rank=8 columns=512 records=3072 controls=8')


if __name__=='__main__':
    main()
