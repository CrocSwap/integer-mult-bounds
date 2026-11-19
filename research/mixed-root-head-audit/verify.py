"""Check sixteen exact caller views and their charged occurrences. Apache-2.0."""

from collections import Counter
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

from geometry import apply, difference, native_boundaries, native_route, phase, translation, transpose

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    raw = (ROOT / 'retained' / name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def authenticate():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    for pin in pins:
        raw = (ROOT / pin['path']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'], 'source SHA-256')
        require(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'],
                'source Git blob')
    return len(pins)


def collect():
    source_files = authenticate()
    sys.path[:0] = [str(ROOT / 'retained'), str(ROOT / 'retained/vendor')]
    from construction import build, digest
    from mixed_caller import instructions, layout_bindings, place_roots, split_templates
    from mixed_geometry import central_contact
    from binding16 import contact_phase
    from mixed_application import ordinary_for_batch

    graph, layout, _ = build()
    graph_hash = digest(graph)
    require(graph_hash == 'c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84',
            'scientific source graph')
    caller, phases = read('data/CALLER.json.gz'), read('data/CALLER-PHASE-BASES.json')['by_q']
    words = split_templates(caller)
    roots = place_roots(caller, 1024)
    root = ('mixed', 0)
    visits = roots[root]
    require(visits == [(t, 15 if t in (9, 10) else 0) for t in range(2, 18)], 'actual first mixed root')
    bound, offsets, _ = layout_bindings(words, roots, layout, 1024)
    host_events = [row for row in words['mixed'][0] if row[0].startswith('HOST_')]
    require(len(host_events) == 16 and {t % 16 for t, _ in visits} == set(range(16)), 'all root colors')
    central = [(1 << j, 1) for j in range(9)]
    atlas, endpoint_checks, head_checks = {}, 0, 0
    omission_controls = []
    for port in sorted({p for _, p in visits}):
        head = layout['ports'][port]
        frame = [head, *phases[str(head)]]
        inverse = transpose(frame)
        require(all((a & b).bit_count() % 2 == (i == j)
                    for i, a in enumerate(frame) for j, b in enumerate(frame)), 'orthogonal central basis')
        shift = translation(difference(central, central, frame), 9)
        back = translation(difference(central, central, inverse), 9)
        require(back == apply(inverse, shift), 'inverse affine translation')
        require(frame == inverse and shift == back, 'the two actual views are involutions')
        for value in range(512):
            require(apply(inverse, apply(frame, value) ^ shift) ^ back == value, 'all central index returns')
        full = [*frame, *[1 << j for j in range(9, 137)]]
        require(all(apply(full, 1 << j) == 1 << j for j in range(9, 137)), 'all 128 spectators fixed')
        for power in (0, -1):
            canonical = [*central, (1, power)]
            local = [*central, (head, power)]
            for before, after, columns, tau in ((canonical, local, frame, shift),
                                                 (local, canonical, inverse, back)):
                delta = difference(before, after, columns)
                require(translation(delta, 9) == tau, 'same X/Y endpoint translation')
                for character in range(512):
                    require(phase(delta, character) == 2 * ((tau & character).bit_count() % 2),
                            'all central character phases')
                    endpoint_checks += 1
        for power in (1, -1, 2):
            for character in range(512):
                require(phase([(head, power)], character) == phase([(1, power)], apply(inverse, character)),
                        'signed head conjugation')
                head_checks += 1
        require((frame, shift, back) == central_contact(head, phases[str(head)]), 'source central cross-check')
        witness = shift & -shift
        require(witness and phase(difference(central, central, frame), witness) == 2,
                'missing entry translation detected')
        require(phase(difference(central, central, inverse), back & -back) == 2,
                'missing return translation detected')
        omission_controls.append(dict(port=port, entry_character=witness, exit_character=back & -back,
                                      wrong_phase=2))
        atlas[port] = dict(port=port, head=head, columns=frame, shift=shift, inverse_shift=back)
    require((atlas[0]['head'], atlas[0]['shift'], atlas[15]['head'], atlas[15]['shift']) == (11, 15, 81, 83),
            'two exact physical heads and shifts')
    wrong_head_character = (11 ^ 81) & -(11 ^ 81)
    require(phase([(11, 1)], wrong_head_character) != phase([(81, 1)], wrong_head_character),
            'wrong B head detected')
    second = dict(zip(layout['hosted']['Dports'], zip(layout['hosted']['X2'], layout['hosted']['Y2'], strict=True), strict=True))
    record, charges = [], []
    native_phase_checks = 0
    for slot, ((call, port), event) in enumerate(zip(visits, host_events, strict=True)):
        color = call % 16
        kind, local_slot, *owners = event
        require(local_slot == slot and kind == ('HOST_B' if slot in (7, 8) else 'HOST_A'), 'actual contact kind')
        require(bound[call][port] == [offsets[root] + owner for owner in owners], 'all actual owner bindings')
        first = layout['live'][port]
        native_slots = (first, first + 112, *second.get(port, ()))
        require(len(native_slots) == len(owners), 'actual native main slots')
        head = atlas[port]['head']
        columns = native_route(atlas[port]['columns'], color)
        require(all(apply(columns, image) == 1 << j for j, image in enumerate(columns)), 'full native route inverse')
        require(apply(columns, head) == head, 'native head preserved')
        body_mask = 255 << (9 + 8 * color)
        require(all(columns[j] == 1 << j for j in range(137) if not (511 | body_mask) & (1 << j)),
                'native spectators fixed')
        shifts = []
        for before, after in native_boundaries(head, color):
            shift = translation(difference(before, after, columns), 137)
            back = translation(difference(after, before, columns), 137)
            require(back == apply(columns, shift), 'native inverse phase')
            shifts.append(shift)
            native_phase_checks += 2
        source_shifts, _ = contact_phase(head, phases[str(head)], color + 1, 137)
        require(shifts == source_shifts, 'all four source boundary shifts')
        for owner in owners:
            for side in ('ENTER', 'EXIT'):
                for operation in ('PERMUTE', 'TRANSLATE'):
                    charges.append([call, slot, owner, side, operation])
        record.append(dict(slot=slot, call=call, color=color, port=port, head=head,
                           local_owners=owners, native_slots=list(native_slots),
                           native_shifts=[hex(v) for v in shifts]))
    require(len(charges) == len({tuple(row) for row in charges}) == 240, '240 distinct additional view traversals')
    require(Counter(row[4] for row in charges) == {'PERMUTE': 120, 'TRANSLATE': 120}, 'both view costs')
    roots32 = place_roots(caller, 32)
    require(roots32[root] == visits, 'same first root in the bounded emitted batch')
    bound32, offsets32, _ = layout_bindings(words, roots32, layout, 32)
    by_call = dict(visits)
    projection, event_count = [], 0
    for event in instructions(words, roots32, bound32, offsets32):
        event_count += 1
        if event[0] == 'PORT_VIEWS':
            _, side, call, ports = event
            if call in by_call:
                projection.append([call, side, [owner - offsets32[root] for owner in ports[by_call[call]]]])
        elif event[0] == 'NATIVE':
            _, call, color, ports = event
            if call in by_call:
                require(color == call % 16, 'emitted native color')
                projection.append([call, 'NATIVE', [owner - offsets32[root] for owner in ports[by_call[call]]]])
    expected_projection = [[row['call'], side, row['local_owners']] for row in record
                           for side in ('ENTER', 'NATIVE', 'EXIT')]
    require(projection == expected_projection, 'ordered entry/native/return records')
    omitted_exit = [row for row in projection if row[1] != 'EXIT']
    require(omitted_exit != expected_projection, 'missing exit records detected')
    receipt = read('results/application.json')
    physical = receipt['physical']
    ordinary = ordinary_for_batch(physical['native'], receipt['caller'], physical['components']['coefficient_bits'])
    require(ordinary == physical['ordinary'], 'unchanged ordinary tariff on retained native counts')
    require((ordinary['port_view_permutations'], ordinary['port_view_translations'], ordinary['port_view_routing_legs'])
            == (819200, 819200, 1638400), 'complete source view allocation includes both sides')
    require(ordinary['ordinary_elementary_record_upper'] == ordinary['ordinary_map_slots'] * 4 * 154**2,
            'source uses its conservative ambient-153 map allowance')
    return dict(schema_version=1, source_files=source_files, source_graph_sha256=graph_hash,
                root=['mixed', 0], calls=1024, root_global_offset=offsets[root],
                central_maps=list(atlas.values()), central_endpoint_character_checks=endpoint_checks,
                signed_head_character_checks=head_checks, native_phase_identities=native_phase_checks,
                characters_per_degree_two_identity=1 + 137 + 137 * 136 // 2,
                visits=record, additional_view_charges=charges, additional_view_traversals=240,
                missing_translation_controls=omission_controls, wrong_B_head_character=wrong_head_character,
                emitted32_events_inspected=event_count, emitted_root_projection=projection,
                missing_exit_control=True, source_batch_permutations=819200, source_batch_translations=819200,
                source_map_allowance_ambient=153, source_tariff_receipt='PASS')


def main():
    require(collect() == json.loads((ROOT / 'RESULT.json').read_text()), 'complete root certificate')
    print('PASS_MIXED_ROOT_HEAD_AUDIT')
    print('16 visits; heads 11 and 81; exact translations 15 and 83; all 128 spectators fixed')
    print('4096 central endpoint characters; 3072 signed-head characters; 128 native phase identities')
    print('60 owner visits; 120 permutations plus 120 translations; both entry and return charged')


if __name__ == '__main__':
    main()
