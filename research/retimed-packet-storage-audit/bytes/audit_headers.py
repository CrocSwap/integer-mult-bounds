"""Bind Gaussian repair bytes to the successful production Product header."""
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from byte_meter import need


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    sys.path.insert(0,str(args.runtime.resolve()))
    from upstream import install
    install()
    from band_product import Product
    from striped_tensor import spectator_layout
    from spool import Arena, Field, cold_swap
    from compact_columns import Columns
    import positive
    records = []
    for sides,b,P in (((3,5),5,30),((3,7),5,31),((5,7),6,36)):
        machine = Product(sides,b,P)
        total_bits = sum(machine.widths)
        need(total_bits <= 2*b <= 2*machine.wide, 'production header lost byte dominance')
        for selected in ((0,), (0,total_bits-1)):
            layout = spectator_layout(machine.widths,selected,(machine.p+1).bit_length()//2)
            need(layout.packed_width <= total_bits, 'stripe enlarged the bit dimension')
        arena = Arena(total_bits,machine.wide)
        field = arena.field()
        try:
            with arena.child(max(0,total_bits-2)) as child:
                copy = child.field()
                need(copy.component_bytes == machine.wide and copy.ambient_bits <= total_bits,
                     'positive child changed record width or enlarged address dimension')
                copy.retire()
        finally:
            field.retire(); arena.close()
        # The actual H entrance widens before calling its numerical cohort.
        # Its width can only strengthen the tag domination proved here.
        widened = []
        original_arena = positive.Arena
        def observed_arena(bits, component):
            widened.append((bits,component))
            return original_arena(bits,component)
        positive.Arena = observed_arena
        small = Field(3,machine.wide)
        small.write([(0,0)]*8)
        try:
            columns = Columns(1,0,1,0,0,0,0,cold_swap)
            positive.Positive(None,None,2).hadamard(small,0,1,columns)
            need(widened == [(3,machine.wide+5)], 'H component widening changed')
            need(small.component_bytes == machine.wide, 'H return changed caller record size')
        finally:
            positive.Arena = original_arena
            small.retire()
        records.append({'sides':sides,'b':b,'P':P,'address_bits':total_bits,
                        'component_bytes':machine.wide,'record_bytes':2*machine.wide,
                        'actual_stopped_H_widened_component_bytes':widened[0][1]})
    rejected = []
    for sides,b,P,reason in (((3,5),5,29,'Invalid public precision'),
                             ((5,7),5,30,'true tensor exceeds')):
        try: Product(sides,b,P)
        except ValueError as e:
            need(reason in str(e),'wrong production header rejection: '+str(e))
            rejected.append(str(e))
        else: raise AssertionError('invalid production header survived')
    checked = 0
    # Independent exact integer oracle. No Fourier, geometry or count estimate
    # is sampled: these are finite checks of the stated universal inequalities.
    for count in (1,2,4):
        for sides in product(range(2,10),repeat=count):
            b = max(5,(prod(sides)-1).bit_length())
            L = sum((s-1).bit_length() for s in sides)
            need(1 << L <= prod(sides)**2 <= 1 << (2*b),'square domination failed')
            for P in (6*b,6*b+1,6*b+31):
                component = (2*P+47)//8
                for suffix in range(L+1):
                    remaining = L-suffix
                    tag = max(1,(remaining+7)//8)
                    grouped = (2*component) << suffix
                    need(tag <= 2*component <= grouped,'repair marker exceeds grouped payload')
                    checked += 1
    result = {'status':'PASS_PRODUCTION_REPAIR_HEADER','actual_headers':records,
              'invalid_headers_rejected':rejected,'exact_parameter_cases':checked,
              'scope':'Product constructor and record-width propagation; no Fourier or mass certificate recheck'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],checked)


if __name__ == '__main__': main()
