#!/usr/bin/env python3
"""Check every common-frame incidence of the selected full forward local wrapper.

This is a frame/phase check, not another Boolean scalar replay. Local labels
0,U,I denote the ambient tensor frames D0,DU,D1; embedding and all-size costs
remain external. The independently reconstructed paid auxiliary transitions
must equal the actual pinned CRT profiler input byte for byte.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path
import struct


def require(ok, message):
    if not ok:
        raise ValueError(message)


def audit(word_path, manifest_path, receipt_path, binary_path):
    raw = gzip.decompress(word_path.read_bytes())
    word = json.loads(raw)
    manifest, receipt = json.loads(manifest_path.read_text()), json.loads(receipt_path.read_text())
    h, v, R = word['h'], word['v'], word['R']
    digest = sha256(raw).hexdigest()
    require(digest == manifest['words'][str(h)]['word_sha256'] == receipt['word_sha256'], 'Selected word hash')
    triples = list(combinations(range(h), 3))
    require(len(triples) == v, 'Source dimension')
    frames = [tuple(frame) for frame in word['frames']]
    require(len(set(frames)) == len(frames), 'Unique frame IDs')
    for c, u in frames:
        require(type(c) is int and type(u) is int and 0 < c <= u < (1 << h) and not c & ~u, 'Frame support domain')
        require((c == u and c.bit_count() == 3) or (c.bit_count() in (1, 2) and c != u), 'Frame family domain')
    ranks = [1 if c == u else u.bit_count() - c.bit_count() for c, u in frames]
    catalog = [(0, 0, 0), (0, 0, h)] + [(c, u, r) for (c, u), r in zip(frames, ranks)]
    lookup = {frame: i + 2 for i, frame in enumerate(frames)}
    require(set(word['sources']) == {str(i) for i in range(v)}, 'Complete source keys')
    require(len(set(word['sources'].values())) == v, 'Source alias')
    source_frames = [lookup[(mask, mask)] for t in triples for mask in [sum(1 << i for i in t)]]
    aux, source, target = [0] * R, source_frames.copy(), [0] * v
    paid, phases, data_moves = Counter(), {}, Counter()
    side_singletons = 0
    scatter_expected, output_slots, centers, sides = [], set(), [], [[] for _ in triples]
    phase = ''

    def begin(name):
        nonlocal phase
        phase = name
        phases[name] = Counter()

    def same(left, right, context):
        require(left == right, 'Unequal current gauges: ' + context)

    def xor_aux(a, b, frame):
        require(type(a) is int and type(b) is int and 0 <= a < R and 0 <= b < R and a != b, 'XOR role domain')
        same(aux[a], frame, phase + ': destination')
        same(aux[b], frame, phase + ': source')
        phases[phase]['literal_xors'] += 1

    def raise_aux(slot, frame):
        require(type(slot) is int and 0 <= slot < R and type(frame) is int and 0 <= frame < len(catalog), 'Auxiliary frame domain')
        old = aux[slot]
        require(type(old) is int, 'Unexpected outstanding side flag')
        if old == frame:
            return
        require(old != 1 and catalog[frame][2] > catalog[old][2], 'Non-increasing auxiliary transport')
        if old >= 2 and frame != 1:
            c, u, _ = catalog[old]
            cc, uu, _ = catalog[frame]
            require(not (cc & ~c) and not (u & ~uu), 'Non-nested auxiliary transport')
        paid[old, frame] += 1
        aux[slot] = frame
        phases[phase]['auxiliary_transports'] += 1

    for record in word['outputs']:
        slot, frame, common, triple = record
        require(type(slot) is int and 0 <= slot < R and slot not in output_slots, 'Terminal role alias')
        require(type(frame) is int and 0 <= frame < len(frames) and 0 <= common < h, 'Terminal frame domain')
        output_slots.add(slot)
        if len(triple) == 1:
            require(triple == [common], 'Center target')
            centers.append(record)
            destinations = [i for i, t in enumerate(triples) if common in t]
        else:
            require(len(triple) == 3 and triple == sorted(triple) and common in triple, 'Side target')
            destinations = [triples.index(tuple(triple))]
            sides[destinations[0]].append(record)
        scatter_expected.extend([v + i, 2 * v + slot] for i in destinations)
    require(len(centers) == h and {r[2] for r in centers} == set(range(h)), 'Complete distinct centers')
    require(word['scatter'] == scatter_expected, 'Literal scatter/output binding')
    require(all(len(records) == 3 for records in sides), 'Three distinct side reads per target')

    begin('1_early_L_at_D0')
    for a, b, _ in word['ops']:
        xor_aux(a, b, 0)
    begin('2_early_J_at_D0')
    for t, s in word['scatter']:
        same(aux[s - 2 * v], target[t - v], phase)
        same(target[t - v], 0, phase)
        phases[phase]['literal_xors'] += 1
    begin('3_early_inverse_L_at_D0')
    for a, b, _ in reversed(word['ops']):
        xor_aux(a, b, 0)
    begin('4_source_V_at_triple_lines')
    for i, slot in word['sources'].items():
        frame = source_frames[int(i)]
        raise_aux(slot, frame)
        same(aux[slot], source[int(i)], phase)
        phases[phase]['literal_xors'] += 1
    begin('5_middle_L_at_recorded_DU')
    for a, b, frame in word['ops']:
        raise_aux(a, frame + 2)
        raise_aux(b, frame + 2)
        xor_aux(a, b, frame + 2)
    # Terminal output incidence belongs to the actual middle path, as in the
    # emitted profile. No later mixer consumer occurs before the final inverse.
    for slot, frame, _, _ in word['outputs']:
        raise_aux(slot, frame + 2)

    begin('6a_center_first_J_with_one_fresh_copy_each')
    late_scatter = []
    for slot, frame, common, _ in centers:
        frame += 2
        require(catalog[frame] == (1 << common, (1 << h) - 1, h - 1), 'Center interface')
        same(aux[slot], frame, phase)
        # A new complete stream, initially blank, is physically copied ONCE.
        # Its original is never cleared; payload preservation is the Lean
        # copied_fanout_correct theorem. Only the temporary is later discarded.
        phases[phase]['fresh_blank_allocations'] += 1
        phases[phase]['complete_stream_copies'] += 1
        temporary_frame = frame
        same(temporary_frame, aux[slot], phase + ': copy')
        temporary_frame = 0
        paid[0, frame] += 1  # inverse partial swap is the SAME involution
        phases[phase]['paid_copy_transports'] += 1
        for i, triple in enumerate(triples):
            if common in triple:
                same(temporary_frame, target[i], phase + ': copied read')
                late_scatter.append([v + i, 2 * v + slot])
                phases[phase]['literal_xors'] += 1
        phases[phase]['fresh_stream_erasures'] += 1
        raise_aux(slot, 1)

    begin('6b_target_grouped_side_J_with_three_rank_one_steps')
    flag_certificates = []
    for i, triple in enumerate(triples):
        require(target[i] == 0, 'Target advanced before center reads finished')
        perpendicular = ('target_perp', i)
        target[i] = perpendicular
        data_moves['D0_to_target_perp'] += 1
        phases[phase]['data_transports'] += 1
        require({r[2] for r in sides[i]} == set(triple), 'Side common points')
        for slot, frame, common, _ in sides[i]:
            frame += 2
            a, b = [j for j in triple if j != common]
            cover = ((1 << h) - 1) ^ (1 << a) ^ (1 << b)
            require(catalog[frame] == (1 << common, cover, h - 3), 'Side envelope')
            same(aux[slot], frame, phase)
            # ACTUAL rational rank-one flag, not an arbitrary rank label:
            # E has orthogonal basis b_j=e_common+2e_j, j not in T.
            # For G=I-J/9: <b_j,b_k>=4 delta_jk; w=e_a-e_b
            # has norm2 and is orthogonal to E and t_T. Thus
            # E -> E+<w> -> t_T^perp -> F has THREE rank-one steps.
            require(h != 9 and common not in (a, b) and a != b, 'Metric/flag domain')
            outside = [j for j in range(h) if j not in triple]
            require(len(outside) == h - 3, 'Flag dimension')
            # Sparse integer vectors bind every checked identity to this
            # actual terminal's indices. dot9 is exactly 9*u^t G_h*v.
            def dot9(left, right):
                return 9 * sum(value * right.get(j, 0) for j, value in left.items()) - sum(left.values()) * sum(right.values())
            basis = [{common: 1, j: 2} for j in outside]
            t_vector, w_vector = {j: 1 for j in triple}, {a: 1, b: -1}
            for j, vector in enumerate(basis):
                require(set(vector) <= {k for k in range(h) if cover >> k & 1}
                        and sum(vector.values()) == 3 * vector[common], 'Basis in literal envelope')
                require(dot9(vector, t_vector) == 0, 'Basis-target orthogonality')
                require(dot9(vector, w_vector) == 0, 'Basis-flag orthogonality')
                for k, other in enumerate(basis):
                    require(dot9(vector, other) == (36 if j == k else 0), 'Basis Gram matrix')
            require(dot9(w_vector, w_vector) == 18 and dot9(w_vector, t_vector) == 0
                    and dot9(t_vector, t_vector) == 18, 'Flag/target norm and orthogonality')
            flag_certificates.append([i, slot, common, a, b])
            aux[slot] = ('E_plus_ea_minus_eb', slot)
            phases[phase]['side_rank_one_transports'] += 1
            aux[slot] = perpendicular
            phases[phase]['side_rank_one_transports'] += 1
            same(aux[slot], target[i], phase + ': side read')
            late_scatter.append([v + i, 2 * v + slot])
            phases[phase]['literal_xors'] += 1
            aux[slot] = 1
            phases[phase]['side_rank_one_transports'] += 1
            side_singletons += 3
    require(Counter(map(tuple, late_scatter)) == Counter(map(tuple, word['scatter'])),
            'Late scatter does not preserve every original literal incidence')

    begin('7a_remaining_auxiliary_cleanup_to_D1')
    for slot in range(R):
        raise_aux(slot, 1)
    begin('7b_late_inverse_L_at_D1')
    for a, b, _ in reversed(word['ops']):
        xor_aux(a, b, 1)
    begin('8_final_V_at_D1')
    for i, slot in word['sources'].items():
        i = int(i)
        require(source[i] == source_frames[i], 'Source gauge changed before final cancellation')
        source[i] = 1
        data_moves['source_line_to_D1'] += 1
        phases[phase]['data_transports'] += 1
        same(aux[slot], source[i], phase)
        phases[phase]['literal_xors'] += 1
    require(aux == [1] * R and source == [1] * v and
            target == [('target_perp', i) for i in range(v)], 'Final local stage gauges')
    literal_xors = sum(p.get('literal_xors', 0) for p in phases.values())
    require(literal_xors == 4 * len(word['ops']) + 2 * len(word['scatter']) + 2 * v, 'Full wrapped literal XOR count')
    mass = side_singletons + sum((catalog[b][2] - catalog[a][2]) * n for (a, b), n in paid.items())
    require(mass == h * R + h * (h - 1) == receipt['profile']['rank_sum'], 'Complete local auxiliary mass')
    require(side_singletons == receipt['transitions']['singles'], 'Side singleton charge')
    encoded = bytearray(struct.pack('<6I2Q', h, v, R, len(catalog), len(paid), side_singletons, mass, h * (h - 1)))
    for c, u, rank in catalog:
        encoded.extend(struct.pack('<2QI', c, u, rank))
    for (a, b), n in sorted(paid.items()):
        encoded.extend(struct.pack('<2Iq', a, b, n))
    require(bytes(encoded) == binary_path.read_bytes(), 'FULL phase auxiliary charges differ from actual CRT input')
    return dict(status='PASS', h=h, v=v, R=R, word_sha256=digest,
                binary_profiler_input_sha256=sha256(encoded).hexdigest(),
                phase_checker_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                phases={name:dict(counts) for name,counts in phases.items()},
                full_wrapper_literal_xors=literal_xors,
                fresh_clone_xor_equivalents=h, wrapper_plus_clone_xor_equivalents=literal_xors+h,
                copy_cost_convention='full_wrapper_literal_xors counts the scalar wrapper after eliminating fresh-copy macros. Each of h complete-stream clones adds one XOR-equivalent pass on a fresh blank temporary; copying and erasing also have separately charged linear stream cost. Erasure is not an XOR or an operation on arbitrary original dirty roles.',
                receipt_sha256=sha256(receipt_path.read_bytes()).hexdigest(),
                source_manifest_sha256=sha256(manifest_path.read_bytes()).hexdigest(),
                selected_upstream_pin=manifest['upstream_pin'],
                receipt_recorded_clearing_xors_per_L=receipt['compiled']['stats']['clearing_xors'],
                receipt_recorded_clearing_xors_across_four_L_sweeps=4*receipt['compiled']['stats']['clearing_xors'],
                side_rank_one_steps=side_singletons,
                side_flag_count=len(flag_certificates),
                side_flag_records_sha256=sha256(json.dumps(flag_certificates,separators=(',',':')).encode()).hexdigest(),
                local_auxiliary_mass=mass, paid_auxiliary_transition_types=len(paid),
                complete_crt_input_byte_equality=True,
                extra_data_transitions=dict(data_moves), extra_data_rank=2 * v * (h - 1),
                data_profile_obligation='Each displayed data transition has inherited profile (1,h-2); not recomputed here. Ambient data fronts/exteriors and endpoint copies remain external.',
                final_gauges=dict(auxiliary='D1', source='D1', target='D_(triple perpendicular)'),
                scope='Full forward LOCAL invocation common-frame/phase/charge check on selected PR64 words, with explicit rational side flags and one paid fresh center copy. Scalar correctness comes from separately verified literal words and Lean copy/scatter lemmas. This does not emit a Lean Trace, instantiate ambient tensor backgrounds, check the full reverse copy schedule or prove tape cost/global machine transfer.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word',required=True,type=Path)
    parser.add_argument('--manifest',required=True,type=Path)
    parser.add_argument('--receipt',required=True,type=Path)
    parser.add_argument('--binary',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    report=audit(args.word,args.manifest,args.receipt,args.binary)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS full forward phase/common-frame/charge binding',report['h'],report['full_wrapper_literal_xors'])


if __name__=='__main__':main()
