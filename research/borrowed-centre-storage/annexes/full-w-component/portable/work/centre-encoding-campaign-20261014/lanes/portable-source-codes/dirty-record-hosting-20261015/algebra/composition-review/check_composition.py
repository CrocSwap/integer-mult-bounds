"""Check the interfaces and costs of the two-cut dirty-record composition.

Read frozen packets. Do not import or run a producer or reconstruct its
owner census. The literal local-word reviews remain separate premises.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path
import shutil
import tarfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
LANES = ROOT/'work/centre-encoding-campaign-20261014/lanes'
PACK = HERE.parent.parent
RESIDUAL = LANES/'residual-syndrome/physical-algebra/eight-record-review-20261015'
CONSUMER = PACK.parent/'common-f-review-20261015'
A = (0, 7, 20, 27, 36, 46, 57, 111)
PINS = {}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def read(path, expected=None):
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if expected is not None:
        need(digest == expected, 'Pin: '+str(path))
    PINS[str(path.relative_to(ROOT))] = digest
    return json.loads(raw) if path.suffix == '.json' else raw.decode()


def manifest(path, expected):
    value = read(path, expected)
    result = {}
    for name, pin in value['files'].items():
        if isinstance(pin, dict):
            pin = pin['sha256']
        result[name] = read(path.parent/name, pin)
    return result


def apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length()-1]
        vector ^= bit
    return result


def inverse_pair(columns, inverse):
    need(len(columns) == len(inverse) == 73, '73-axis matrices')
    need(all(apply(columns, inverse[i]) == 1 << i and
             apply(inverse, columns[i]) == 1 << i for i in range(73)), 'Matrix inverse')
    need(inverse == [sum(((column >> i) & 1) << j for j, column in enumerate(columns))
                     for i in range(73)], 'Orthogonal matrix transpose')


def phase(axes, translation=0):
    linear = [2*((translation >> i) & 1) for i in range(73)]
    quadratic = set()
    for vector in axes:
        support = [i for i in range(73) if (vector >> i) & 1]
        for i in support:
            linear[i] = (linear[i]+1) % 4
        for at, i in enumerate(support):
            for j in support[at+1:]:
                key = i, j
                if key in quadratic:
                    quadratic.remove(key)
                else:
                    quadratic.add(key)
    return tuple(linear), frozenset(quadratic)


def phase_add(a, b):
    return tuple((x+y) % 4 for x, y in zip(a[0], b[0])), a[1] ^ b[1]


def phase_at(value, character):
    total = sum(value[0][i] for i in range(73) if (character >> i) & 1)
    total += 2*sum(((character >> i) & 1) and ((character >> j) & 1) for i, j in value[1])
    return total % 4


def scalar_bill(events):
    counts, costs, coefficients = Counter(), Counter(), Counter()
    for event in events:
        op = event['op']
        counts[op] += 1
        if op == 'clear':
            costs[op] += 2
        elif op in ('add', 'scale'):
            coefficient = Fraction(event['c'])
            n, d = abs(coefficient.numerator), coefficient.denominator
            need(n and not n & (n-1) and not d & (d-1), 'Dyadic-unit coefficient')
            coefficients[op+':'+str(coefficient)] += 1
            if op == 'add':
                costs[op] += 2*(2+n.bit_length()+n.bit_count()+d.bit_length()-1)
            else:
                costs[op] += 2*(abs(n.bit_length()-d.bit_length())+(coefficient < 0))
    return {'event_counts': dict(sorted(counts.items())),
            'scalar_by_op': dict(sorted(costs.items())),
            'scalar_allowance': sum(costs.values()),
            'coefficients': dict(sorted(coefficients.items()))}


def add(a, b, factor=1):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0)+factor*value
        if not out[key]:
            del out[key]
    return out


def product(a, b):
    out = {}
    for left, av in a.items():
        for right, bv in b.items():
            word = left+right
            if any(word[i:i+2] == ('G', 'E') for i in range(len(word)-1)):
                continue
            out[word] = out.get(word, 0)+av*bv
    return {word: value for word, value in out.items() if value}


def matrix_product(a, b):
    return [[add(product(a[i][0], b[0][j]), product(a[i][1], b[1][j]))
             for j in range(2)] for i in range(2)]


def outer_check(outer, template, allocation, cuts, repair, cleanup):
    expected_procedures = {'capture':repair['capture'], 'repair':repair['repair'][8:],
                           'cleanup':cleanup['cleanup']}
    need(outer['procedures'] == expected_procedures, 'Exact procedures and removed E1 lifts')
    schedule, old = outer['schedule'], template['execution_schedule']
    anchors = [(i,e['old_event']) for i,e in enumerate(schedule) if 'old_event' in e]
    need([at for _,at in anchors] == list(range(482)) and anchors[0][0] == 0, 'All old events once in order')
    need(len(old) == 482 and template['private_namespace']['centers'] == [14336,14344], 'Actual old namespace')
    rows = {r:sorted((e for e in allocation['selected'] if e['role']//8 == r), key=lambda e:e['role']) for r in range(16)}
    cut_by_event = {}
    for r, cut in cuts.items():
        for name, key in [('capture','capture_after_event'),('repair','repair_after_event'),('cleanup','cleanup_after_event')]:
            need(cut[key] not in cut_by_event, 'Separate boundary anchors')
            cut_by_event[cut[key]] = r,name
    bridge_ordinals = Counter()
    protected = {}
    live = set()
    peak = 0
    active_exclusions = 0
    lease_trace = []
    levels = {(r,pair):-1 for r in range(16) for pair in range(4)}
    for at, (position, _) in enumerate(anchors):
        entry, source = schedule[position], old[at]
        end = anchors[at+1][0] if at+1 < len(anchors) else len(schedule)
        tail = schedule[position+1:end]
        kind, replica = source['kind'], source.get('replica')
        if kind == 'bridge':
            number = bridge_ordinals[replica]
            bridge_ordinals[replica] += 1
            src, dst = source['src'], source['dst']
            need(levels[replica,src] == levels[replica,dst], 'Actual bridge levels')
            if number < 6:
                need(entry == dict(op='physical_pair_swap',old_event=at,replica=replica,src_pair=src,dst_pair=dst,
                     ports=list(range(112)),ordered_scalar_word=['a+=b','b-=a','a+=b','b=-b']), 'Actual full-W swap binding')
                if protected.get(replica) in (src,dst):
                    protected[replica] = dst if protected[replica] == src else src
            else:
                need(entry == dict(op='omit_full_W_bridge',old_event=at), 'Last three bridge omissions')
        elif kind in ('terminal','terminal_Y_translations'):
            need(entry == dict(op='omit_full_W_terminal',old_event=at), 'Full-W terminal omission')
        else:
            need(entry == dict(op='retained_event',old_event=at), 'Retained old event')
        if kind == 'local_cover_sweep':
            call = template['calls'][source['time']]
            need(call['replica'] == replica and call['stage'] == source['stage'], 'Actual call identity')
            owners = [e[0] for e in call['owners'][:224]]
            need(owners == list(range(896*replica+224*call['pair'],896*replica+224*(call['pair']+1))), 'Actual data family layout')
            if replica in protected:
                kept = set(range(896*replica+224*protected[replica],896*replica+224*(protected[replica]+1)))
                need(not kept.intersection(owners), 'No later actual active owner reads protected pair')
                active_exclusions += 1
            need(call['stage'] == 0 or levels[replica,call['pair']] == call['stage']-1, 'Actual active entrance')
            levels[replica,call['pair']] = call['stage']
        elif kind == 'idle_cover_sweep':
            need(levels[replica,source['pair']] == source['from_level'], 'Actual idle entrance')
            levels[replica,source['pair']] = source['to_level']
        if at in cut_by_event:
            r, name = cut_by_event[at]
            need(r == replica, 'Boundary replica')
            if name in ('capture','repair'):
                need(kind == 'local_cover_sweep' and source['stage'] == (0 if name == 'capture' else 1), 'F0/B1 boundary')
                need(template['calls'][source['time']]['pair'] == 0, 'First-pair boundary')
                pair = 0
            else:
                need(kind == 'idle_cover_sweep' and source['pair'] == 1 and source['to_level'] == 2 and
                     protected.get(r) == 1 and source['source_event'] == 5, 'Full pair parked at completed U2 cut')
                pair = 1
            donor_rows = rows[r]
            call_positions = [i for i,e in enumerate(tail) if e['op'] == 'call_procedure']
            need(len(call_positions) == 1, 'One complete local procedure at boundary')
            call_at = call_positions[0]
            invocation = tail[call_at]
            expected_bindings = {side+str(p):896*r+224*pair+112*s+p for s,side in enumerate(('X','Y')) for p in range(112)}
            expected_bindings.update({'R'+str(p):row['family'] for p,row in zip(A,donor_rows)})
            expected_bindings['C'] = 14336
            need(invocation == dict(op='call_procedure',name=name,bindings=expected_bindings), 'Actual procedure owner binding')
            need(len(set(expected_bindings.values())) == 233, 'No alias among data, donors and old C0')
            gather = [dict(op='donor_cover_map',field=row['family'],columns=row['U_inverse_columns']) for row in donor_rows]
            returns = [dict(op='donor_cover_map',field=row['family'],columns=row['U_columns']) for row in donor_rows]
            def adapters(index):
                return [dict(op='native_adapter',field=row['family'],recipe=row['adapters'][index]) for row in donor_rows
                        if row['adapters'][index]['axes'] or row['adapters'][index]['translation']]
            before = ([] if name == 'capture' else adapters(0 if name == 'repair' else 1))+gather
            after = returns+(adapters(2) if name == 'cleanup' else [])
            need(tail[:call_at] == before, 'Adapter before gather and exact inverse cover direction')
            need(tail[call_at+1:] == after, 'Return before A3 and restoration before next old event')
            if name == 'capture':
                live.add(r)
                peak = max(peak,8*len(live))
            elif name == 'repair':
                need(r in live, 'Repair within donor lease')
                protected[r] = 0
            else:
                need(r in live, 'Erase within donor lease')
                live.remove(r)
            lease_trace.append({'old_event':at,'replica':r,'boundary':name,'live_donors_after':8*len(live)})
        elif at == 480:
            need(kind == 'bank_padding_cover_sweep' and old[481]['kind'] == 'translate_every_live_family', 'Actual final endpoint placement')
            need(tail == [dict(op='positive_X_lines',replicas=list(range(16)),pair=0,ports=list(range(112)),rank=1)], 'Endpoint after tail and before common translation')
            need(not live and protected == {r:0 for r in range(16)}, 'Restored first pairs before final lines')
        else:
            need(tail == [], 'No unpriced or late operation between old events')
    need(not live and peak == 48 and bridge_ordinals == Counter({r:9 for r in range(16)}), 'All leases and bridge instances')
    return {'old_events':len(anchors),'local_calls':len(template['calls']), 'procedure_calls':48,
            'protected_active_owner_exclusions':active_exclusions, 'peak_live_borrowed_donors':peak,
            'restoration_deadline':'Each cleanup block returns donors and applies A3 before the next original event.',
            'owned_scratch_family':14336,'lease_trace':lease_trace}


def main():
    need(shutil.disk_usage(HERE).free >= 3*1024**3, 'Three GiB free')
    donors = manifest(PACK/'TWO-CUT-MANIFEST.json',
                      'bae5f1cb0f3738b7246be3e26f88c8c872a0e17cf4054b527dc74d25cf2837b0')
    local = manifest(PACK/'EIGHT-RECORD-MANIFEST.json',
                     '6ff0c36e99b09cd475e970436819a177c3d82e365c9a1d63904ce05e4388113f')
    own = manifest(HERE.parent/'MANIFEST.json',
                   '4c834b51aae5cbaedbf61fe9b8c1939047fbc0271a6bef667c1a203e70220c64')
    cleanup = read(RESIDUAL/'DELAYED-CLEANUP-ONE-C-WORD.json',
                   'bddba461c6f06213c7ab938d24993ac6d5ea44169f9705594227acfdc5b6e880')
    read(RESIDUAL/'DELAYED-CLEANUP.md',
         'de6c40e4b2f8280dd5406e7ccfbe8a8adbe476b379404403b5b0d8dd73224d04')
    local_review = read(RESIDUAL/'REVIEW.json',
                        '17b03e51d1a3ca9a8628bfcebc4e8b52208a77741ce2d7ed8c62cf89d57605b4')
    need(local_review['status'] == 'PASS_INDEPENDENT_EIGHT_RECORD_REPAIR' and
         local_review['files']['producer/eight-records/EIGHT-RECORD-WORDS.json'] ==
         '8dcb0f29d2b0275e5d5395511d10451b8675c9ffe37ebdbd452c0132a17b15f4', 'Independent local repair review')
    cleanup_review = read(LANES/'residual-syndrome/physical-algebra/review-gauss/delayed-dirty-cleanup/REVIEW.json',
                          '74f7f7e2dd1eb4c36762b315f32b8a2462a9ab5dcd44d7378adea5a5a29ed993')
    need(cleanup_review['status'] == 'PASS_INDEPENDENT_CONDITIONAL_DELAYED_DIRTY_RECORD_CLEANUP', 'Independent cleanup review')
    need(cleanup_review['producer_words']['DELAYED-CLEANUP-ONE-C-WORD.json'] ==
         'bddba461c6f06213c7ab938d24993ac6d5ea44169f9705594227acfdc5b6e880', 'Reviewed cleanup word binding')
    outer_files = manifest(PACK/'DIRTY-CONSUMER-MANIFEST.json',
                           'a83988bfbef25e613391af95fd5f4829994b327b8b10cd62277d31f9df751213')
    outer = outer_files['consumer/DIRTY-CONSUMER-WORD.json']
    archive_path = ROOT/'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
    archive_hash = sha256(archive_path.read_bytes()).hexdigest()
    need(archive_hash == 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6', 'Selected archive pin')
    PINS[str(archive_path.relative_to(ROOT))] = archive_hash
    with tarfile.open(archive_path) as archive:
        compressed = archive.extractfile('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz').read()
    need(sha256(compressed).hexdigest() == '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760', 'Actual global template pin')
    template = json.loads(gzip.decompress(compressed))
    consumer = read(CONSUMER/'CONSUMER.word.json',
                    'dcab2956719da84a4284f03bbc02ea02d121998582261b0a3fde50dc56e5f13a')
    consumer_review = read(PACK.parent/'common-f-independent-review-20261015/REVIEW.json',
                           'a930a9cda3f573f16b59d4538bc2920d9d22a8ba0e74e4a0e5ad6ce926a16fef')
    need(consumer_review['status'] == 'PASS_INDEPENDENT_COMMON_F_FOLLOWTHROUGH_REVIEW', 'Independent full-W consumer review')
    need(own['ALGEBRA.json']['status'] == 'PASS_EIGHT_DIRTY_DONOR_ECHO_ALGEBRA', 'Frozen dirty algebra')
    packet = donors['TWO-CUT-DONORS.json']
    allocation = packet['allocations']['all']
    selected = allocation['selected']
    need(sorted(row['role'] for row in selected) == list(range(128)), 'All record roles')
    need(len({row['family'] for row in selected}) == 128, 'Distinct donors')
    cuts = {row['replica']: row for row in packet['rows']}
    profile, cut_profiles = Counter(), [Counter(), Counter(), Counter()]
    translations = standalone = wrapper_count = 0
    reversed_map = premature_adapter = None
    for row in selected:
        need(0 <= row['family'] < 14336, 'An old donor family')
        interval = cuts[row['role']//8]
        bounds = [interval[name] for name in ('capture_after_event', 'repair_after_event', 'cleanup_after_event')]
        need(bounds[0] < bounds[1] < bounds[2], 'Three ordered cuts')
        axes, shifts = [], []
        for index, path in enumerate(row['paths']):
            need(all(bounds[index] < entry['event'] <= bounds[index+1] for entry in path), 'Path lies within cuts')
            axes.append([v for entry in path for v in entry['axes']])
            shift = 0
            for entry in path:
                shift ^= entry['translation']
            shifts.append(shift)
        need(len(set(axes[0]+axes[1])) == len(axes[0]+axes[1]), 'Disjoint old native axes')
        wanted = row['desired_axes']
        need(len(wanted[0]) == len(wanted[1]) == 8 and not set(wanted[0]) & set(wanted[1]), 'Disjoint desired blocks')
        U, Uinv = row['U_columns'], row['U_inverse_columns']
        inverse_pair(U, Uinv)
        need(U[9:17] == wanted[0] and U[17:25] == wanted[1], 'Same forward map at both cuts')
        native = [phase(axes[i], shifts[i]) for i in range(2)]
        desired = [phase(wanted[i]) for i in range(2)]
        adapters = []
        for index, adapter in enumerate(row['adapters']):
            rank = len(adapter['axes'])
            adapters.append(phase(adapter['axes'], adapter['translation']))
            translations += bool(adapter['translation'])
            standalone += bool(adapter['translation'] and not rank)
            if rank:
                profile[rank] += 1
                cut_profiles[index][rank] += 1
                wrapper_count += 2
                need(adapter['left_columns'][:rank] == adapter['axes'], 'Wrapper native block')
                inverse_pair(adapter['left_columns'], adapter['right_columns'])
        need(all(phase_add(adapters[i], native[i]) == desired[i] for i in range(2)), 'Both complete cut phases')
        need(phase_add(adapters[2], phase_add(*desired)) == phase_add(*native), 'Exact baseline restoration phase')
        if reversed_map is None and set(Uinv[9:17]) != set(wanted[0]):
            reversed_map = {'role': row['role'], 'family': row['family'],
                            'expected_D1': wanted[0], 'wrong_D1': Uinv[9:17]}
        adapter = row['adapters'][2]
        conjugated = phase([apply(Uinv, v) for v in adapter['axes']], apply(Uinv, adapter['translation']))
        if premature_adapter is None and adapters[2] != conjugated:
            characters = [1 << i for i in range(73)]
            characters += [(1 << i) | (1 << j) for i in range(73) for j in range(i+1, 73)]
            character = next(c for c in characters if phase_at(adapters[2], c) != phase_at(conjugated, c))
            premature_adapter = {'role': row['role'], 'family': row['family'], 'character': character,
                                 'physical_adapter_phase': phase_at(adapters[2], character),
                                 'required_gathered_adapter_phase': phase_at(conjugated, character)}
    need(profile == Counter({1:200, 2:7}), 'All three adapter profiles')
    need(wrapper_count == 414 and translations == 107 and standalone == 0, 'All adapter maps and translations')
    need(reversed_map is not None and premature_adapter is not None, 'Direction controls')

    repair = local['eight-records/EIGHT-RECORD-WORDS.json']['dirty_eight_A_before_cleanup']
    need(repair['capture'] == [dict(op='add', dst='R'+str(p), src='X'+str(p), c='1') for p in A], 'Dirty capture has no CLEAR')
    expected_lifts = [dict(op='stage', field='R'+str(p), rank=8, sign=1, stage=1) for p in A]
    need(repair['repair'][:8] == expected_lifts, 'Exactly eight replaced record lifts')
    local_events = repair['capture']+repair['repair'][8:]
    need(not any(e['op'] == 'stage' for e in local_events), 'No double record advance')
    need(all(e['field'] == 'C' for e in local_events if e['op'] == 'clear'), 'No data or donor CLEAR')
    local_bill = scalar_bill(local_events)
    cleanup_bill = scalar_bill(cleanup['cleanup'])
    need(local_bill['scalar_allowance'] == 20322 and local_bill['event_counts']['map'] == 240, 'Repair subtotal')
    need(cleanup_bill['scalar_allowance'] == 23780 and cleanup_bill['event_counts']['map'] == 224, 'Cleanup subtotal')
    need(cleanup['cleanup'] == cleanup['alias_shear']+cleanup['current_stage2_query']+
         cleanup['inverse_alias_shear']+cleanup['selected_error_correction'], 'Complete cleanup order')
    need(all(e['field'] == 'C' for e in cleanup['cleanup'] if e['op'] == 'clear'), 'Owned cleanup scratch only')

    I, E, G = {():1}, {('E',):1}, {('G',):1}
    B = [[I,E],[G,I]]
    inverse = [[add(I,product(E,G)),{('E',):-1}],[{('G',):-1},I]]
    identity = [[I,{}],[{},I]]
    need(matrix_product(inverse,B) == identity and matrix_product(B,inverse) == identity,
         'Two-sided Schur inverse under G E=0')

    full = consumer['variants']['whole_pair_112']
    need(full['retired_ports'] == list(range(112)) and full['return_after_repair'] == [], 'Full-W consumer')
    need(consumer['final_three_bridges_on_retired_ports'] == [] and consumer['terminal_on_retired_ports'] == [], 'Late omitted events')
    bridge = full['port_swap_each_first_six_bridge']
    fields = [side+'_'+bank+':'+str(p) for p in range(112) for side in ('X','Y') for bank in ('src','dst')]
    values = {field: {field:1} for field in fields}
    for event in bridge:
        if event['op'] == 'add':
            values[event['dst']] = add(values[event['dst']], values[event['src']], Fraction(event['c']))
        elif event['op'] == 'scale':
            values[event['field']] = {key: Fraction(event['c'])*value for key,value in values[event['field']].items()}
        else:
            raise ValueError('Physical swap event')
    for p in range(112):
        for side in ('X','Y'):
            for bank, other in [('src','dst'),('dst','src')]:
                need(values[side+'_'+bank+':'+str(p)] == {side+'_'+other+':'+str(p):1}, 'Arbitrary physical swap')
    bridge_bill = scalar_bill(bridge)
    need(6*bridge_bill['scalar_allowance'] == 34944, 'Full nine-bridge replacement subtotal')
    endpoint = full['final_pair0_X_correction']
    need(endpoint == [dict(field='X'+str(p),op='line',port=p,rank=1,sign=1) for p in range(112)], 'Positive endpoint lines')
    line_count = sum(e['op'] == 'line' for e in local_events)
    need(line_count == 112, 'Positive Y repair lines')
    need([e for e in local_events if e['op'] == 'line'] ==
         [dict(field='Y'+str(p),op='line',port=p,rank=1,sign=1) for p in range(112)], 'Literal positive Y lines')
    schedule_check = outer_check(outer,template,allocation,cuts,repair,cleanup)
    schedule_controls = {}
    for mutation in ('reverse_capture_cover','A3_before_return','keep_synthetic_record_lift','partial_W_swap'):
        changed = deepcopy(outer)
        events = changed['schedule']
        if mutation == 'reverse_capture_cover':
            index = next(i for i,e in enumerate(events) if e['op'] == 'donor_cover_map')
            events[index]['columns'] = selected[0]['U_columns']
        elif mutation == 'A3_before_return':
            cleanup_at = cuts[3]['cleanup_after_event']
            start = next(i for i,e in enumerate(events) if e.get('old_event') == cleanup_at)
            end = next(i for i in range(start+1,len(events)) if 'old_event' in events[i])
            call_at = next(i for i in range(start+1,end) if events[i]['op'] == 'call_procedure')
            adapter_at = next(i for i in range(call_at+1,end) if events[i]['op'] == 'native_adapter')
            events.insert(call_at+1,events.pop(adapter_at))
        elif mutation == 'keep_synthetic_record_lift':
            changed['procedures']['repair'].insert(0,repair['repair'][0])
        else:
            event = next(e for e in events if e['op'] == 'physical_pair_swap')
            event['ports'] = list(A)
        try:
            outer_check(changed,template,allocation,cuts,repair,cleanup)
        except ValueError as error:
            schedule_controls[mutation] = str(error)
        else:
            raise ValueError('Ineffective outer-word control: '+mutation)
    total_profile = profile+Counter({1:16*(line_count+len(endpoint))})
    totals = {'native_profile': dict(sorted(total_profile.items())),
              'native_mass': sum(rank*count for rank,count in total_profile.items()),
              'native_wrappers': wrapper_count+2*16*(line_count+len(endpoint)),
              'cover_maps': 16*(240+224)+6*128,
              'local_scalar_allowance': 16*(20322+23780),
              'bridge_scalar_allowance': 16*34944,
              'scalar_total_before_native_and_address_costs': 16*(20322+23780+34944),
              'standalone_adapter_translations': standalone}
    need(totals['native_mass'] == 3798 and totals['native_wrappers'] == 7582 and
         totals['cover_maps'] == 8192, 'Global component invoice')
    outer_invoice = outer_files['consumer/DIRTY-CONSUMER.json']['component_invoice']
    for reported,actual in [('added_native_profile','native_profile'),('added_native_mass','native_mass'),
        ('added_native_wrappers','native_wrappers'),('ordinary_and_donor_cover_maps','cover_maps'),
        ('local_scalar_allowance','local_scalar_allowance'),('full_modified_bridge_scalar_allowance','bridge_scalar_allowance')]:
        expected = totals[actual]
        if isinstance(expected,dict):
            expected = {str(k):v for k,v in expected.items()}
        need(outer_invoice[reported] == expected, 'Outer receipt subtotal: '+reported)
    result = {'status':'PASS_ORDERED_DIRTY_RECORD_COMPOSITION', 'source_pins':PINS,
              'coverage':'Actual 482-event outer word, boundary owner bindings, exact adapter phases, arbitrary-input block composition, physical swaps, and literal scalar counts. No donor census or local-word replay.',
              'donor_roles':128, 'donor_views':'At each cut gather with U^-1 and return with U. Apply A3 after return.',
              'adapter_profiles_by_cut':[dict(sorted(c.items())) for c in cut_profiles],
              'adapter_translations':translations, 'local_bill':local_bill, 'cleanup_bill':cleanup_bill,
              'one_bridge_bill':bridge_bill, 'totals':totals,
              'negative_controls':{'reverse_cover_direction':reversed_map,'A3_before_donor_return':premature_adapter},
              'outer_word_checks':schedule_check,'outer_word_negative_controls':schedule_controls,
              'outstanding_review_inputs':['Independent actual donor-path review','Separate all-output dirt audit']}
    path = HERE/'CHECK.json'
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'receipt_sha256':sha256(path.read_bytes()).hexdigest(),'totals':totals},sort_keys=True))


if __name__ == '__main__':
    main()
