"""Exact boundary of the grouped-repair tag-to-payload byte premise."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from byte_meter import File, Meter, need


def case(bits, suffix, component_bytes=1, good_modulus=0):
    import spool
    from compact_columns import Columns
    arena = spool.Arena(bits, component_bytes)
    field = arena.field()
    extent = field.count * field.record
    raw = bytes((19*i+i//251+7) % 256 for i in range(extent))
    field.stream.write(raw)
    remaining, grouped = bits-suffix, field.record << suffix
    width = max(1, (remaining+7)//8)
    count = 1 << remaining
    good = lambda address: bool(good_modulus and (address >> suffix) % good_modulus == 0)
    errors = sum(not good(i << suffix) for i in range(count))
    caps = [errors*(grouped+width)]*3+[(count-errors)*grouped]
    meter, original = Meter(), spool.TemporaryFile
    created = []
    def factory():
        index = len(created)
        need(index < 4, 'repair unexpectedly allocated another file')
        key = 'repair:'+str(index)
        meter.open_roles.add(key)
        tape = File(original(), meter, key, caps[index])
        created.append(tape)
        return tape
    spool.TemporaryFile = factory
    try:
        columns = Columns(1,0,1,0,0,0,suffix,spool.cold_swap)
        columns.repair(field, good, lambda address: address)
        field.stream.seek(0)
        need(field.stream.read(extent) == raw, 'repair boundary fixture changed its payload')
        need(not meter.open_roles and arena.live == 1, 'repair retained a work file or replacement')
        peaks = [meter.highs['repair:'+str(i)] for i in range(4)]
        need(peaks[0] == errors*(grouped+width), 'tagged dirty stream has wrong exact byte length')
        need(sum(peaks) <= extent+2*errors*grouped+3*errors*width, 'repair historical formula failed')
        return {'ambient_bits':bits, 'suffix_bits':suffix, 'component_bytes':component_bytes,
                'field_bytes':extent, 'groups':count, 'errors':errors,
                'good_modulus':good_modulus,'grouped_payload_bytes':grouped,
                'tag_bytes':width, 'historical_role_bytes':peaks,
                'tag_fits_payload':width <= grouped,
                'dirty_exceeds_two_field_volumes':peaks[0] > 2*extent,
                'output_sha256':sha256(raw).hexdigest()}
    finally:
        spool.TemporaryFile = original
        field.retire()
        arena.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    sys.path.insert(0, str(args.runtime.resolve()))
    from upstream import install
    install()
    # Source bytes are separately retained; refuse silently moving to a successor.
    import compact_columns, spool
    here = Path(__file__).resolve().parent
    for module in (compact_columns, spool):
        actual = Path(module.__file__).read_bytes()
        need(actual == (here/'sources'/Path(module.__file__).name).read_bytes(),
             'resolved repair source changed')
    bad, good = case(17,0), case(17,1)
    need(bad['dirty_exceeds_two_field_volumes'] and not bad['tag_fits_payload'],
         'generic ungrouped boundary was not reproduced')
    need(good['tag_fits_payload'] and not good['dirty_exceeds_two_field_volumes'],
         'one-bit grouped control did not restore the byte premise')
    mixed = case(6,1,13,3)
    need(mixed['historical_role_bytes'][3] > 0, 'mixed repair omitted the clean byte extent')
    result = {'status':'PASS_REPAIR_TAG_BOUNDARY', 'counterexample':bad, 'grouped_control':good,
              'mixed_good_and_bad':mixed,
              'scope':'generic Columns.repair API; not a production-native counterexample'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])


if __name__ == '__main__': main()
