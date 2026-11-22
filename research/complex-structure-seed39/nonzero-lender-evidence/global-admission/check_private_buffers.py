#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explicit private zero-buffer allocation and conservative finite overcharge.

Prepared for Tekalign (@tekuuu) with substantial OpenAI Codex assistance.
Retains PR2269's finite envelope formulas with a separately reserved 76-family
zero-buffer arena. It never assumes that reserved tableau storage is free.
Native zero restoration is the hash-bound all-column replay obligation.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / 'anticipatory-stage-evidence'
CANDIDATE = HERE.parent


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def primitive(scalar):
    if scalar[0] in ('copy', 'clear'):
        return 2
    q = Fraction(*(scalar[3:5] if scalar[0] == 'add' else scalar[2:4]))
    a, b = abs(q.numerator), q.denominator
    require(a > 0 and b & (b-1) == 0, 'dyadic native coefficient')
    if scalar[0] == 'scale':
        require(a & (a-1) == 0, 'unit scale')
        return 2*(abs(a.bit_length()-b.bit_length())+int(q < 0))
    require(scalar[0] == 'add', 'native scalar opcode')
    return 2*(3+a.bit_length()-1+a.bit_count()+b.bit_length()-1)


def lifetimes(events, labels, arena_start, live=66304, tableau=428):
    slots = {z:arena_start+i for i,z in enumerate(sorted(labels))}
    require(len(labels) == len(slots) == 76, 'exact private zero inventory')
    require(arena_start >= live+8+tableau+2, 'zero arena overlaps inherited private reserve')
    active = set()
    intervals, max_live, occurrences = {}, 0, Counter()
    primitives, macros, warp_count = 0, 0, 0
    phase = None
    for index, event in enumerate(events):
        tag = event[0]
        if tag == 'phase':
            phase = event[1]
        elif tag == 'zero_buffer':
            _, action, label = event
            require(label in slots, 'unknown zero label')
            require(phase == 'full_frame_cleanup', 'zero arena restricted to cleanup')
            if action == 'alloc':
                require(label not in active and label not in intervals, 'duplicate zero allocation')
                active.add(label)
                intervals[label] = [index]
            else:
                require(action == 'free' and label in active, 'free of inactive zero buffer')
                active.remove(label)
                intervals[label].append(index)
            max_live = max(max_live, len(active))
            occurrences[action] += 1
        else:
            refs = []
            if tag == 'scalar':
                scalar = event[1]
                refs = [scalar[1]] + ([scalar[2]] if scalar[0] in ('add', 'copy') else [])
                primitives += primitive(scalar)
                macros += 1
            elif tag == 'warp':
                refs = [event[1]]
                warp_count += 1
            elif tag in ('adapter','residual_adapter','climb','center'):
                require(not active, 'zero lifetime overlaps phase or recursive child')
            else:
                require(tag in ('phase',), 'unrecognized emitted event')
            mapped = []
            for ref in refs:
                require(isinstance(ref, list) and len(ref) == 2, 'typed native stream reference')
                kind, number = ref
                require(type(number) is int, 'integral native stream reference')
                if kind == 'L':
                    require(0 <= number < 652, 'native L reference range')
                    # All local L streams are mapped to distinct live data/owner
                    # families by the separate whole-owner certificate.
                    mapped.append(('live', number))
                elif kind == 'C':
                    require(0 <= number < 8 and not active, 'center/zero lifetime overlap')
                    mapped.append(('private', live+number))
                else:
                    require(kind == 'Z' and number in active, 'use of unallocated zero buffer')
                    require(phase == 'full_frame_cleanup', 'zero use outside cleanup')
                    if tag == 'scalar':
                        require(event[-1] == 1, 'zero buffer scalar frame is not FULL')
                    if tag == 'warp':
                        require(event[-2:] == [1,1], 'zero buffer warp frame is not FULL')
                    mapped.append(('private', slots[number]))
            require(len(mapped) == len(set(mapped)), 'two native operands alias after allocation')
    require(not active and set(intervals) == set(labels) and all(len(v) == 2 for v in intervals.values()), 'complete zero lifetimes')
    require(occurrences == {'alloc':76, 'free':76} and max_live == 76, 'zero allocation counts')
    return dict(slots=slots, lifetimes=intervals, peak_live_buffers=max_live,
                native_scalar_macros=macros, native_real_component_primitives=primitives,
                warp_events=warp_count, clear_macros_charged=152, clear_real_components_charged=304,
                scope='All accesses bind to distinct dedicated private fields. Exact zero-before-free uses the separately hash-bound native all-column replay; allocation does not silently erase arbitrary dirty data.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--owner-receipt', type=Path, default=CANDIDATE/'budget/RESTRICTED-VERIFICATION.json')
    args = parser.parse_args()
    planfile = ROOT/'parent/new/PLAN.json'
    require(sha(planfile) == 'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2', 'frozen call plan pin')
    plan = read(planfile)
    parentfile = ROOT/'parent/GLOBAL-TEMPLATE.json.gz'
    require(sha(parentfile) == '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db', 'source envelope template pin')
    parent = read(parentfile)
    owner = read(args.owner_receipt)
    require(owner['status'] == 'PASS_428_HELPER_LITERAL_RESTRICTION_WINDOWS_AXES_PROFILE_AND_EXACT_COST', 'independent owner receipt')
    live, helpers, centers, coefficient, zeros = 66304, 428, 8, 2, 76
    old_physical = live+helpers+centers+coefficient
    physical = old_physical+zeros
    compiler = 64*74**3
    providers, controls = {}, []
    for pid, native_name in (('gauge44','base'), ('extra','extra')):
        directory = CANDIDATE/'native-evidence'/native_name
        word = read(directory/'CANONICAL-WORD.json.gz')
        programs = read(directory/'LOCAL-PROGRAMS.json.gz')
        replay = read(directory/'INDEPENDENT-LOCAL-REPLAY.json')
        checks = read(directory/'LOCAL-CHECKS.json')
        require(word['R'] == helpers and len(word['zero_buffers']) == zeros, 'native interface dimensions')
        require(replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'native scalar replay status')
        require(replay['canonical_word_sha256'] == sha(directory/'CANONICAL-WORD.json.gz') and
                replay['local_programs_sha256'] == sha(directory/'LOCAL-PROGRAMS.json.gz'), 'native zero restoration hash binding')
        require(word['local_profile'] == owner['local_profiles'][pid], 'owner native profile binding')
        actual_widths = Counter(len(word['frames'][word['final'][r]]) - len(word['frames'][word['start'][r]]) for r in range(224, 652))
        require(actual_widths == {int(k):v for k,v in owner['width_inventories'][pid].items()}, 'owner native width binding')
        local = {}
        for orientation, events in programs.items():
            require(digest(events) == checks[orientation]['sha256'], 'native checks program binding')
            q = lifetimes(events, word['zero_buffers'], old_physical)
            require(q['native_scalar_macros'] == checks[orientation]['scalar_macros'] and
                    q['native_real_component_primitives'] == checks[orientation]['real_component_primitive_bound'], 'independent scalar cost recount')
            require(replay['local'][orientation]['all_exact_columns'] == 652 and
                    replay['local'][orientation]['private_work_erased'] and
                    replay['local'][orientation]['zero_buffers_returned_to_zero'] == zeros,
                    'native exact zero restoration obligation')
            q['native_prefix_bits'] = replay['local'][orientation]['prefix_bits_upper']
            local[orientation] = q
        require(set(local) == {'forward','backward'}, 'both native orientations')
        children = sum(word['local_profile'].values())
        # Charge every explicit clear, zero field and warp in addition to the
        # inherited compiler invoice, even though clearing verified zero is free.
        local_adapters = 16*(max(q['native_scalar_macros']+152+q['warp_events'] for q in local.values())+
                            children+652+zeros+centers)+64*73
        primitive_bound = max(q['native_real_component_primitives']+304 for q in local.values())+local_adapters*compiler
        wrapped = {r for r in range(224,652) if word['start'][r] != 0 or word['final'][r] != 1}
        providers[pid] = dict(local=local, children=children, local_adapters=local_adapters,
                              local_primitive_bound=primitive_bound, wrapper_factors_per_call=2*len(wrapped)*144,
                              input_sha256={name:sha(directory/name) for name in
                                ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','INDEPENDENT-LOCAL-REPLAY.json','LOCAL-CHECKS.json')})
        if args.controls:
            events = programs['forward']
            first_alloc = next(i for i,e in enumerate(events) if e[:2] == ['zero_buffer','alloc'])
            dropped = events[:first_alloc]+events[first_alloc+1:]
            for name, action, reason in (
                ('overlap_tableau_arena', lambda:lifetimes(events, word['zero_buffers'], old_physical-1), 'zero arena overlaps inherited private reserve'),
                ('missing_allocation', lambda:lifetimes(dropped, word['zero_buffers'], old_physical), 'use of unallocated zero buffer'),
                ('missing_free', lambda:lifetimes([e for e in events if not (e[:2] == ['zero_buffer','free'] and e[2] == word['zero_buffers'][0])], word['zero_buffers'], old_physical), 'zero lifetime overlaps phase or recursive child')):
                try:
                    action()
                except ValueError as error:
                    require(str(error) == reason, 'unexpected buffer control reason: '+name+': '+str(error))
                else:
                    raise ValueError('accepted buffer control '+name)
                controls.append(pid+': '+name)
    calls = plan['provider_calls']
    require(len(calls) == 666, 'complete call invoice')
    scalar = sum(providers[c['provider']]['local'][c['orientation']]['native_real_component_primitives']+304 for c in calls)
    wrappers = sum(providers[c['provider']]['wrapper_factors_per_call'] for c in calls)
    local_adapters = max(p['local_adapters'] for p in providers.values())
    parent_live, parent_physical = parent['live'], parent['physical']
    parent_idle = sum(row['replicas'] for row in parent['idle_children'])
    require((parent_live,parent_physical,parent_idle) == (111664,112178,149184), 'source finite envelope geometry')
    require((parent_live-live) % 9 == 0, 'source bank stock integral')
    parent_banks = (parent_live-live)//9
    bridges, shifts = 2*112*666, 4*112*74
    moves = 2*shifts
    # Extra 2*calls*zeros conservatively prices explicit field binding/restoration
    # in addition to charged alloc/free scalar clears and local compiler work.
    nonlocal_items = (4*112*74*9+2*112*74*9+2*666*(helpers+zeros)+parent_idle+9*parent_banks+
                      bridges+shifts+moves+parent_live+parent_physical+wrappers)
    outside = 8*nonlocal_items+64*73
    pervertex = scalar+bridges+shifts+moves+parent_live+(666*local_adapters+outside)*compiler+64*parent_physical
    rebased = pervertex+65*(physical-parent_physical)+(live-parent_live)
    used = max(pervertex, rebased)
    old_adapters = max(16*(max(q['native_scalar_macros'] for q in p['local'].values())+
                          p['children']+652+centers)+64*73 for p in providers.values())
    old_outside = outside-8*2*666*zeros
    old_pervertex = (scalar-304*666)+bridges+shifts+moves+parent_live+(666*old_adapters+old_outside)*compiler+64*parent_physical
    group = 2**(36*36)
    for j in range(1,37):
        group *= 2**(2*j)-1
    mass, payload = owner['rank_mass'], 2048
    require(owner['live'] == live and 73*live-mass == owner['deficit'] == 23680, 'bound owner rank deficit')
    stock = group*physical
    streamed_mass = group*mass
    logical = group*used+64
    router = compiler*(logical+1)*(stock+1)**2
    literal = 2*2**30000*stock**2+8*streamed_mass+4*stock+4+32*73
    total_mass = streamed_mass+2**100000
    row = 2*stock.bit_length()+9909+252+2*payload
    prefix = max(q['native_prefix_bits'] for p in providers.values() for q in p['local'].values())+37+666+666+4
    checks = dict(local_primitive_bound=max(p['local_primitive_bound'] for p in providers.values()) < 2**48,
        logical=logical < 2**6050, router=router < 2**30000, literal=literal < 2**100000,
        mass=total_mass < 2**100001, precision=32*73*total_mass**2 < 2**210000,
        tape=2*total_mass+18 < 2**210000, row=row < 20161, prefix=prefix < payload,
        halving=73**2 > 2*max(map(int,owner['profile']))**2)
    require(all(checks.values()), 'all revised finite overcharge inequalities')
    result = dict(status='PASS_EXPLICIT_76_PRIVATE_ZERO_BUFFER_ARENA_AND_FINITE_OVERCHARGE',
        physical_namespace={'data_and_owner_families':[0,live], 'centers':[live,live+8],
            'reserved_tableau':[live+8,live+8+helpers], 'coefficient':[old_physical-2,old_physical],
            'private_zero_buffers':[old_physical,physical]},
        live=live, physical=physical, previous_428_helper_physical=old_physical,
        delta_physical_families=zeros, delta_live_recursive_families=0,
        extra_clear_scalar_macros=152*666, extra_clear_real_component_primitives=304*666,
        extra_nonlocal_field_binding_items=2*666*zeros, all_calls_serialized=True,
        concrete_zero_lowering={'allocation':['scalar','clear','mapped private Z family','FULL'],
            'free':['require hash-bound native zero restoration','scalar clear mapped private Z family at FULL','release field'],
            'local_chart':'Use the local cover chart on the first nine coordinates, identity spectators; all accesses preserve the declared FULL frame.',
            'all_other_native_events':'Preserve the pinned event order and coefficients; replace every Z reference by its declared private-family slot.'},
        providers=providers, revised_selected_real_component_primitives=scalar,
        revised_local_adapters=local_adapters, compiler=compiler,
        revised_unhosted_pervertex=pervertex, revised_hosted_rebased_pervertex=rebased,
        inherited_formula_without_explicit_zero_or_warp_overcharge=old_pervertex,
        extra_pervertex_over_inherited_formula=pervertex-old_pervertex,
        conservative_pervertex_used=used, unchanged_rank_mass=mass, unchanged_rank_deficit=23680,
        global_prefix_bits=prefix, charged_payload_bits=payload,
        finite={'physical_stock_bits':stock.bit_length(), 'router_bits':router.bit_length(),
                'literal_bits':literal.bit_length(), 'physical_row_coefficient':row,
                'required_C0_bits':(32*73*total_mass**2).bit_length()},
        strict_checks=checks, controls=controls, plan_sha256=sha(planfile), parent_template_sha256=sha(parentfile), owner_receipt_sha256=sha(args.owner_receipt),
        checker_sha256=sha(Path(__file__)),
        scope='Independent explicit private allocation/lifetime and conservative finite overcharge. Zero restoration relies on the bound fresh native all-column replay. An emitted global controller must actually use this Z mapping and 66818 physical-family reserve. This is not itself an emitted-controller or outer-bound admission.')
    if args.out:
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
    print(json.dumps({k:result[k] for k in ('physical','delta_live_recursive_families','extra_clear_real_component_primitives','finite','strict_checks','controls')},sort_keys=True))


if __name__ == '__main__':
    main()
