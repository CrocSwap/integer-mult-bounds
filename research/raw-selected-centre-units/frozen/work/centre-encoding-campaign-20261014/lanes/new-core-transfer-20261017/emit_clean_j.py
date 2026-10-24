#!/usr/bin/env python3
"""Lower the PR3133 centre deletion and its entrance correction."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
INTERFACE = HERE / 'INTERFACE.json'
INPUT_PINS = {'native-original-base/CANONICAL-WORD.json.gz': 'bd6f84f6e7be075064f04e6141568d295631a3feab1efa75ff0326e6efa4f472', 'native-original-base/LOCAL-PROGRAMS.json.gz': '4048b4494793f31c6c9ce85a7de584c53cafae0cd5c119eb1084b221cfe04ad9', 'native-original-base/FULL-WORD.json.gz': '49bdc172f1f53253c15fa4bf5be2d5741701d2fe9d18943f8b79c3ded0b96a3e', 'native-original-extra/CANONICAL-WORD.json.gz': '1cf1714fc2a26c18b2b380827054246550c1402fde379745f626ff61f4ee6224', 'native-original-extra/LOCAL-PROGRAMS.json.gz': '4048b4494793f31c6c9ce85a7de584c53cafae0cd5c119eb1084b221cfe04ad9', 'native-original-extra/FULL-WORD.json.gz': '34af6f955bf8d95f68868cc282fa739532a5a6117df50d753fd996d44cea6731'}
INTERFACE_PIN = 'c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746'


def require(test, message):
    if not test:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_gzip(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def scalar_cost(op):
    if op[0] in ('clear', 'copy'):
        return 2
    q = Q(*op[-2:])
    a, b = abs(q.numerator), q.denominator
    require(b & (b - 1) == 0, 'Dyadic coefficient')
    if op[0] == 'scale':
        require(a & (a - 1) == 0, 'Unit SCALE')
        return 2 * (abs(a.bit_length() - b.bit_length()) + int(q < 0))
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def prefix(R, H, original_to_compact, backward):
    result = [['phase', 'clean_J_input_helper_debt_correction']]
    C = ['C', 0]
    def add(target, source, coefficient):
        q = Q(coefficient)
        result.append(['scalar', ['add', target, source, q.numerator, q.denominator], 0])
    for k in range(8):
        result.append(['scalar', ['clear', C], 0])
        if backward:
            for p, value in sorted(R[k].items()):
                add(C, ['L', 112 + p], value / 4)
            for h, value in sorted(H[k].items()):
                add(['L', original_to_compact[h]], C, -value)
        else:
            for h, value in sorted(H[k].items()):
                add(C, ['L', original_to_compact[h]], value)
            for p, value in sorted(R[k].items()):
                add(['L', 112 + p], C, value / 4)
        result.append(['scalar', ['clear', C], 0])
    return result


def add_row(dst, src, q):
    for key, value in src.items():
        value = dst.get(key, 0) + q * value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def replay(program, canonical, backward, R, clean=True):
    n = 224 + canonical['R']
    fields = [('L', i) for i in range(n)] + [('C', i) for i in range(8)]
    rows = {field: {(field, ()): Q(1)} for field in fields}
    frames = {('L', i): f for i, f in enumerate(canonical['start'])}
    frames.update({('C', i): 0 for i in range(8)})
    zero_live = set()
    prefix_end = next(i for i, event in enumerate(program) if event == ['phase', 'zero_frame_precondition'])
    for position, event in enumerate(program):
        tag = event[0]
        if tag == 'scalar':
            op, frame = event[1:]
            field = tuple(op[1])
            if op[0] == 'clear':
                rows[field] = {}
                frames[field] = frame
            elif op[0] == 'copy':
                other = tuple(op[2])
                require(frames[field] == frames[other] == frame, ('COPY frame', position))
                rows[field] = dict(rows[other])
            elif op[0] == 'add':
                other = tuple(op[2])
                require(frames[field] == frames[other] == frame, ('ADD frame', position))
                require(field != other, 'Distinct ADD fields')
                add_row(rows[field], rows[other], Q(op[3], op[4]))
            elif op[0] == 'scale':
                require(frames[field] == frame, ('SCALE frame', position))
                q = Q(op[2], op[3])
                rows[field] = {key: q * v for key, v in rows[field].items()}
            else:
                raise ValueError(op[0])
        elif tag == 'climb':
            field = ('L', event[2])
            require(frames[field] == event[3], ('Native input frame', position))
            require(len(canonical['frames'][event[4]]) - len(canonical['frames'][event[3]]) == event[5], 'Native rank')
            frames[field] = event[4]
        elif tag == 'warp':
            field = tuple(event[1])
            require(frames[field] == event[3], ('Warp frame', position))
            frames[field] = event[4]
            symbol = event[2]
            if backward:
                symbol = (abs(symbol) + 1000) * (1 if symbol > 0 else -1)
            rows[field] = {(source, word[:-1] if word and word[-1] == -symbol else word + (symbol,)): value for (source, word), value in rows[field].items()}
        elif tag == 'zero_buffer':
            field = ('Z', event[2])
            if event[1] == 'alloc':
                require(field not in zero_live, 'Zero buffer allocated once')
                zero_live.add(field)
                rows[field] = {}
                frames[field] = 1
            else:
                require(field in zero_live and not rows[field], 'Zero buffer returned to zero')
                zero_live.remove(field)
        elif tag in ('phase', 'adapter', 'residual_adapter'):
            pass
        else:
            raise ValueError(('Unexpected event', event))
    require(not zero_live, 'No live zero buffer at exit')
    for field in fields:
        kind, index = field
        goal = {(field, ()): Q(1)}
        if kind == 'C':
            if index == 0:
                goal = {}
        elif index < 224:
            is_target = index < 112 if backward else index >= 112
            if is_target:
                p = index if backward else index - 112
                source = ('L', 112 + p if backward else p)
                add_row(goal, {(source, ()): Q(1)}, -1 if backward else 1)
                for k in range(8):
                    value = R[k].get(p, Q(0))
                    for j, coefficient in R[k].items():
                        src = ('L', 112 + j if backward else j)
                        add_row(goal, {(src, ()): coefficient}, value / 4 if backward else -value / 4)
        require(rows[field] == goal, ('Complete map mismatch', backward, field))
    require([frames['L', i] for i in range(n)] == canonical['final'], 'All live endpoint frames')
    return {'live_input_columns': n, 'arbitrary_C_input_columns': 8, 'C0_exit': 'zero', 'C1_to_C7_exit': 'physical identity by non-use', 'zero_buffers_returned': len(canonical['zero_buffers']), 'prefix_events': prefix_end, 'events': len(program)}


def native_record(event):
    return event[0] in ('climb', 'center', 'warp', 'adapter', 'residual_adapter')


def main():
    require(digest(INTERFACE.read_bytes()) == INTERFACE_PIN, 'Pinned derived interface')
    for name, pin in INPUT_PINS.items():
        require(digest(gzip.decompress((HERE / name).read_bytes())) == pin, 'Pinned source: ' + name)
    interface = json.loads(INTERFACE.read_text())
    R = [{int(k): Q(v) for k, v in row.items()} for row in interface['R']]
    H = [{int(k): Q(v) for k, v in row.items()} for row in interface['H']]
    payload = {'schema': 'pr3133-clean-J-native-transfer-v1', 'providers': {}, 'R': interface['R'], 'H': interface['H'], 'source_interface_sha256': digest(INTERFACE.read_bytes())}
    receipt = {'status': 'PASS_PR3133_CLEAN_J_LOCAL_NATIVE_TRANSFER', 'providers': {}}
    for name in ('base', 'extra'):
        folder = HERE / ('native-original-' + name)
        canonical = read_gzip(folder / 'CANONICAL-WORD.json.gz')
        old = read_gzip(folder / 'LOCAL-PROGRAMS.json.gz')
        original = read_gzip(folder / 'FULL-WORD.json.gz')
        kept = list(range(224)) + canonical['helper_origin']
        mapping = {r: i for i, r in enumerate(kept)}
        require(len(mapping) == 632, 'Complete compact live namespace')
        require(all(canonical['start'][mapping[h]] == 0 and canonical['final'][mapping[h]] == 1 for row in H for h in row), 'All H roles are I to FULL')
        result = {'canonical': canonical, 'programs': {}, 'removed_centre_blocks': {}, 'source_program_payload_sha256': digest(gzip.decompress((folder / 'LOCAL-PROGRAMS.json.gz').read_bytes()))}
        result_receipt = {}
        for orientation in ('forward', 'backward'):
            backward = orientation == 'backward'
            source = old[orientation]
            left = source.index(['phase', 'centers'])
            right = source.index(['phase', 'B'], left)
            deleted = source[left + 1:right]
            require(all(e[0] in ('center', 'scalar') for e in deleted), 'Only centre block is removed')
            require(Counter(e[4] for e in deleted if e[0] == 'center') == {8: 8}, 'Exact deleted native profile')
            start = prefix(R, H, mapping, backward)
            target = start + source[:left + 1] + source[right:]
            require([e for e in target if native_record(e)] == [e for e in source if native_record(e) and e[0] != 'center'], 'All retained native records equal the source')
            check = replay(target, canonical, backward, R)
            profile = Counter(e[5] for e in target if e[0] == 'climb')
            require(profile == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}, 'Clean profile')
            bill = sum(scalar_cost(e[1]) for e in target if e[0] == 'scalar')
            require(bill == 164514, 'Complete scalar bill')
            result['programs'][orientation] = target
            result['removed_centre_blocks'][orientation] = deleted
            check.update(native_profile=dict(sorted(profile.items())), native_rank_mass=sum(r * c for r, c in profile.items()), native_children=sum(profile.values()), scalar_real_primitives=bill, scalar_added=sum(scalar_cost(e[1]) for e in start if e[0] == 'scalar'), scalar_removed=sum(scalar_cost(e[1]) for e in deleted if e[0] == 'scalar'), scalar_original=sum(scalar_cost(e[1]) for e in source if e[0] == 'scalar'), retained_native_records=sum(native_record(e) for e in target), native_record_counts=dict(Counter(e[0] for e in target if native_record(e))), zero_buffer_event_positions=[i for i, e in enumerate(target) if e[0] == 'zero_buffer'], C0_scalar_positions=[i for i, e in enumerate(target) if e[0] == 'scalar' and ['C', 0] in e[1]])
            result_receipt[orientation] = check
        result['helper_endpoint_roles'] = [{'compact': i, 'original': original_role, 'entry_frame': canonical['start'][i], 'exit_frame': canonical['final'][i], 'width': len(canonical['frames'][canonical['final'][i]]) - len(canonical['frames'][canonical['start'][i]])} for i, original_role in enumerate(kept) if i >= 224]
        payload['providers'][name] = result
        receipt['providers'][name] = result_receipt
    raw = (json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'CLEAN-J-PROGRAMS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt.update(payload_sha256=digest(raw), emitter_sha256=digest(Path(__file__).read_bytes()), scope='Complete literal scalar/native-record transfer on both 632-live-input providers, plus all eight arbitrary C inputs. Native phase lowering is inherited by exact record equality from the pinned provider. No new physical phase sweep, T9 owner admission, recursive private hosting, precision guard or global moment calculation.')
    (HERE / 'CLEAN-J-TRANSFER.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], receipt['payload_sha256'])


if __name__ == '__main__':
    main()
