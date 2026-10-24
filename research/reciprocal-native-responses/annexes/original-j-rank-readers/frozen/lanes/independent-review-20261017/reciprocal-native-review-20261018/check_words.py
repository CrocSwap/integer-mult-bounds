#!/usr/bin/env python3
"""Review reciprocal words by reverse columns and division observables."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / 'reciprocal-centre-20261018'
PINS = {
    'reciprocal-centre-20261018/FREEZE.json':
        'b0a396e5582d723dbf99e0199792031b47562d62039d6a2983b3aff2f9e772fd',
    'reciprocal-centre-20261018/RECIPROCAL-CENTRE-NATIVE.md':
        '322026cad321521b10f8a6d0626a6c3191943971be7f9eba186bb60d2dc83737',
    'reciprocal-centre-20261018/emit_reciprocal_centres.py':
        'cf420eb592c45823ef78fabe2bed07512b2467684589ccbec38d254103215abc',
    'reciprocal-centre-20261018/producer-final/RECIPROCAL-CENTRE-RECEIPT.json':
        'aafaa8b17be476d521fe4c8eb3cf3af59c72351c3aba60a9413cd2aa0baafdfc',
    'independent-review-20261017/NEW-CORE-NATIVE-REVIEW.json':
        '924b898621dd25ea9d3330563fdf7acf6c3b63dc99526e15faaee682f4bdd94d',
    'independent-review-20261017/check_new_native.py':
        '937543157459e5c0eee788feefcf2107acf6bdf660a1209cdecece1ca1f26d01',
    'new-native-recipes-20261017/base/CLIFFORD-RECIPES.json':
        '580dee1ca6d0a2971bc1dbe93558b8331bfa61662ce1736b24d944a55127b4f0',
    'new-native-recipes-20261017/extra/CLIFFORD-RECIPES.json':
        'f3c678f44ac8c116376d707b088516b0c17744a8508f2863843b912738d2024e',
}
PAYLOAD_PIN = '8b3d6fbba7d7221a82927475bc38d479798f776fa27c22ef9a447c7a9a1d5013'
CLEAN_PIN = 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'


def need(test, label):
    if not test:
        raise ValueError(label)


def read_gzip(path, pin):
    raw = gzip.decompress(path.read_bytes())
    need(sha256(raw).hexdigest() == pin, 'Compressed source pin '+str(path))
    return json.loads(raw)


def accumulate(target, source, scale=F(1)):
    for key, value in source.items():
        updated = target.get(key, F(0))+scale*value
        if updated:
            target[key] = updated
        else:
            target.pop(key, None)


def parse(op):
    tag, target = op[0], tuple(op[1])
    need(tag in ('add', 'copy', 'clear', 'scale'), 'Scalar grammar')
    source = tuple(op[2]) if tag in ('add', 'copy') else None
    value = F(*op[-2:]) if tag in ('add', 'scale') else F(1)
    need(source is None or source != target, 'Distinct scalar operands')
    return tag, target, source, value


def price(op):
    tag, _, _, value = parse(op)
    if tag in ('clear', 'copy'):
        return 2
    a, b = abs(value.numerator), value.denominator
    need(a > 0 and b & (b-1) == 0, 'Dyadic old primitive')
    if tag == 'scale':
        need(a & (a-1) == 0, 'Power-of-two SCALE')
        return 2*(abs(a.bit_length()-b.bit_length())+int(value < 0))
    return 2*(1+a.bit_length()+a.bit_count()+b.bit_length())


def pullback(events, fields, backward=False):
    columns = {field: {(field, ()): F(1)} for field in fields}
    division_positions = []
    for position in range(len(events)-1, -1, -1):
        event = events[position]
        tag = event[0]
        if tag == 'scalar':
            kind, target, source, value = parse(event[1])
            if kind == 'add':
                accumulate(columns[source], columns[target], value)
            elif kind == 'scale':
                columns[target] = {key: value*x for key, x in columns[target].items()}
            elif kind == 'copy':
                accumulate(columns[source], columns[target])
                columns[target] = {}
            else:
                columns[target] = {}
        elif tag == 'divide_odd':
            field = tuple(event[1])
            columns[field] = {key: x/F(event[2]) for key, x in columns[field].items()}
            accumulate(columns[field], {(('D', position), ()): F(1)})
            division_positions.append(position)
        elif tag == 'warp':
            field = tuple(event[1])
            letter = ('dual_K' if backward else 'K', event[2])
            inverse = (letter[0], -letter[1])
            columns[field] = {(output, word[:-1] if word and word[-1] == inverse else word+(letter,)): value
                              for (output, word), value in columns[field].items()}
        elif tag == 'zero_buffer':
            if event[1] == 'alloc':
                columns['Z', event[2]] = {}
            else:
                need(event[1] == 'free', 'Zero-buffer grammar')
        else:
            need(tag in ('center', 'climb', 'phase', 'adapter', 'residual_adapter'),
                 'Complete native grammar')
    queries = {pos: {} for pos in sorted(division_positions)}
    complete = {field: {} for field in fields}
    for field, column in columns.items():
        for (output, word), value in column.items():
            if output[0] == 'D':
                queries[output[1]][field, word] = value
            else:
                complete[field][output, word] = value
    return complete, queries


def expected(fields, R, selected, backward):
    result = {f: {} if f[0] == 'Z' or f == ('C', 0) else {(f, ()): F(1)} for f in fields}
    sign = F(-1 if backward else 1)
    for p in range(112):
        source = ('L', 112+p if backward else p)
        target = ('L', p if backward else 112+p)
        accumulate(result[source], {(target, ()): sign})
        for j, row in enumerate(R):
            weight = -F(1, 52) if j in selected else -F(1, 4)
            for q, value in row.items():
                target = ('L', q if backward else 112+q)
                accumulate(result[source], {(target, ()): sign*weight*value*row.get(p, F(0))})
    return result


def types(events, c):
    frames = {('L', i): f for i, f in enumerate(c['start'])}
    frames.update({('C', i): 0 for i in range(8)})
    active, allocated, released = set(), set(), set()
    bill, divisions = 0, 0
    profile, native = Counter(), Counter()
    warp_edges = set(map(tuple, c['warp_edges']))
    for pos, event in enumerate(events):
        tag = event[0]
        if tag == 'scalar':
            kind, target, source, value = parse(event[1])
            need(target in frames and (source is None or source in frames), 'Live scalar access')
            need(all(f[0] != 'C' or f[1] == 0 for f in (target, source) if f is not None),
                 'Only C0 is used')
            if kind == 'clear':
                need(target == ('C', 0), 'No borrowed clear')
                frames[target] = event[2]
            else:
                need(frames[target] == event[2] and (source is None or frames[source] == event[2]),
                     'Scalar common frame at '+str(pos))
                need(kind != 'copy' or target == ('C', 0), 'Only an owned copy target')
            bill += price(event[1])
        elif tag == 'divide_odd':
            need(event == ['divide_odd', ['C', 0], 13, 0] and frames['C', 0] == 0,
                 'Odd division has a legal I-frame query')
            divisions += 1
        elif tag in ('climb', 'center'):
            if tag == 'climb':
                field, old, new, width = ('L', event[2]), *event[3:]
            else:
                field, old, new, width = ('C', event[1]), *event[2:]
                need(field == ('C', 0) and width == 8, 'Serial C0 centre child')
            need(frames[field] == old, 'Native frame at '+str(pos))
            need(abs(len(c['frames'][new])-len(c['frames'][old])) == width, 'Native rank')
            frames[field] = new
            profile[width] += 1
            native[tag] += 1
        elif tag == 'warp':
            field, symbol, old, new = tuple(event[1]), *event[2:]
            need(field in frames and frames[field] == old, 'Warp input frame')
            need((1 if symbol > 0 else -1, abs(symbol), old, new) in warp_edges, 'Warp class')
            frames[field] = new
            native[tag] += 1
        elif tag == 'zero_buffer':
            field = ('Z', event[2])
            if event[1] == 'alloc':
                need(field not in frames and field not in allocated, 'Unique private allocation')
                frames[field] = 1
                allocated.add(field)
                active.add(field)
            else:
                need(event[1] == 'free' and field in active and frames[field] == 1,
                     'Private release at FULL')
                active.remove(field)
                released.add(field)
                del frames[field]
        elif tag == 'adapter':
            _, side, field, frame = event
            need(side in ('old_to_new', 'new_to_old'), 'Adapter direction')
            need(frame == c['start' if side == 'old_to_new' else 'final'][field], 'Adapter endpoint')
            native[tag] += 1
        elif tag == 'residual_adapter':
            _, side, field, old, *tail = event
            need(side in ('pre', 'post') and old == c['start'][field]
                 and (tail[0] if tail else 1) == c['final'][field], 'Residual wrapper endpoints')
            native[tag] += 1
        else:
            need(tag == 'phase', 'Event grammar')
    need(not active and allocated == released == {('Z', x) for x in c['zero_buffers']},
         'All private lifetimes')
    need([frames['L', i] for i in range(632)] == c['final'], 'All live exit frames')
    need(all(frames['C', i] == 0 for i in range(8)), 'All owned exit frames')
    need(profile == Counter({1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 4}), 'Child profile')
    need(native == Counter(climb=3507, center=4, warp=240, adapter=978, residual_adapter=390),
         'Complete native inventory')
    need(divisions == 8, 'Eight complex odd divisions')
    return {'dyadic_real_primitives': bill, 'complex_odd_divisions': divisions,
            'real_odd_scans': 2*divisions, 'native_profile': dict(sorted(profile.items())),
            'native_mass': sum(k*v for k, v in profile.items()), 'native_children': sum(profile.values())}


def source_binding(word, clean, canonical, selected, backward, recipes):
    events = word['program']
    split = events.index(['phase', 'zero_frame_precondition'])
    need(split == 836 and word['weighted_prefix_events'] == split, 'Weighted prefix size')
    old_split = clean['programs'][backward].index(['phase', 'zero_frame_precondition'])
    prefix = [deepcopy(e) for e in events[:split] if e[0] != 'divide_odd']
    prefix[0] = clean['programs'][backward][0]
    need(prefix == clean['programs'][backward][:old_split], 'No other entrance edits')
    row, active, divided, divisions = -1, False, False, []
    for event in events[1:split]:
        if event[0] == 'scalar' and event[1][0] == 'clear':
            if not active:
                row, active, divided = row+1, True, False
            else:
                need(divided == (row in selected), 'Exactly the selected entrance rows divide')
                active = False
        elif event[0] == 'divide_odd':
            need(active and not divided, 'One division per selected query')
            divided = True
            divisions.append(row)
        else:
            target, source = tuple(event[1][1]), tuple(event[1][2])
            if target == ('C', 0):
                need(not divided, 'Query finishes before division')
            else:
                need(source == ('C', 0) and divided == (row in selected), 'Scatter follows selected division')
    need(row == 7 and not active and divisions == sorted(selected), 'All eight entrance rows')
    start = events.index(['phase', 'centers'])+1
    end = events.index(['phase', 'B'], start)
    need(end-start == 108 and word['centre_block_events'] == 108, 'Four complete centre blocks')
    stripped = events[split:start]+events[end:]
    need(stripped == clean['programs'][backward][old_split:], 'Every retained core event is unchanged')
    original = clean['removed_centre_blocks'][backward]
    need(len(original) == 208 and len(word['centre_bindings']) == 4, 'Source centre inventory')
    for i, j in enumerate(sorted(selected)):
        block = events[start+27*i:start+27*(i+1)]
        source = original[26*j:26*(j+1)]
        actual = [deepcopy(e) for e in block if e[0] != 'divide_odd']
        need(len(actual) == 26, 'One added division in each centre block')
        for k, event in enumerate(actual):
            old = source[k]
            if event[0] == 'center':
                need(event == ['center', 0, *old[2:]], 'Only the owned child target changes')
                event[1] = j
            else:
                op = event[1]
                for entry in op:
                    if isinstance(entry, list) and entry[0] == 'C':
                        need(entry == ['C', 0], 'Serial owned field')
                        entry[1] = j
                if op[0] == 'add' and event[2] == 0:
                    need(F(*op[-2:]) == 12*F(*old[1][-2:]), 'Weighted original quarter ADD')
                    op[-2:] = old[1][-2:]
                if backward == 'backward' and k == 25:
                    need(event[2] == 0, 'Final empty C0 resets to I')
                    event[2] = old[2]
            need(event == old, 'Every retained centre scalar has its source')
        binding = word['centre_bindings'][i]
        pos = binding['position']
        call = events[pos]
        need(binding['centre'] == j and binding['event'] == call, 'Occurrence centre label')
        need(binding['source_event'] == next(e for e in source if e[0] == 'center'), 'Original centre binding')
        pair = tuple(call[2:4])
        need(tuple(binding['recipe_key']) == pair and recipes[pair]['rank'] == 8, 'Exact child class')
        digest = sha256((json.dumps(recipes[pair], sort_keys=True, separators=(',', ':'))+'\n').encode()).hexdigest()
        need(binding['recipe_sha256'] == digest, 'Exact source recipe hash')
        division_pos = pos-1 if backward == 'backward' else pos+1
        need(events[division_pos] == ['divide_odd', ['C', 0], 13, 0], 'Division is on the I side of the child')


for path, pin in PINS.items():
    need(sha256((LANES/path).read_bytes()).hexdigest() == pin, 'Source pin '+path)
payload = read_gzip(SOURCE/'producer-final/RECIPROCAL-CENTRE-PROGRAMS.json.gz', PAYLOAD_PIN)
clean = read_gzip(LANES/'new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz', CLEAN_PIN)
need(payload['R'] == clean['R'] and payload['H'] == clean['H'], 'Actual centre and helper matrices')
R = [{int(k): F(v) for k, v in row.items()} for row in clean['R']]
report = {'status': 'PASS_INDEPENDENT_RECIPROCAL_NATIVE_WORDS', 'providers': {},
          'source_pins': PINS, 'payload_decompressed_sha256': PAYLOAD_PIN,
          'clean_payload_decompressed_sha256': CLEAN_PIN}
for name in ('base', 'extra'):
    provider = payload['providers'][name]
    c = provider['canonical']
    need(c == clean['providers'][name]['canonical'], 'Complete canonical source binding')
    phases = json.loads((LANES/'new-native-recipes-20261017'/name/'CLIFFORD-RECIPES.json').read_bytes())
    recipes = {(r['old'], r['new']): r for r in phases['children']}
    centre_pairs = {(a, b) for f in c['center_frames'] for a, b in ((f, 0), (0, f))}
    need(len(centre_pairs) == 16, 'Sixteen source centre directions')
    carried = {(r['old'], r['new']): r for r in provider['centre_recipes']}
    need(set(carried) == centre_pairs and all(carried[key] == recipes[key] for key in carried),
         'Every carried centre recipe was covered by the prior complete independent phase review')
    fields = [('L', i) for i in range(632)]+[('C', i) for i in range(8)]+[('Z', z) for z in c['zero_buffers']]
    report['providers'][name] = {}
    for response, selected in (('E', set(range(4))), ('G', set(range(4, 8)))):
        for orientation in ('forward', 'backward'):
            key = response+'_'+orientation
            word = provider['words'][key]
            need(word['selected_centres'] == sorted(selected), 'Chosen four actual rows')
            source_binding(word, clean['providers'][name], c, selected, orientation, recipes)
            bill = types(word['program'], c)
            need(bill['dyadic_real_primitives'] == (165618 if orientation == 'backward' else 165594),
                 'Complete dyadic scalar price')
            actual, queries = pullback(word['program'], fields, orientation == 'backward')
            want = expected(fields, R, selected, orientation == 'backward')
            need(actual == want, 'Complete reverse-column response '+name+' '+key)
            need(all(output[0] != 'Z' for col in actual.values() for output, _ in col), 'All private return outputs are zero')
            query_report = []
            for pos, row in queries.items():
                need(row, 'Nonzero completed query')
                need(all(value.denominator & (value.denominator-1) == 0 for value in row.values()),
                     'Every completed division query is dyadic on every formal input')
                query_report.append({'position': pos, 'formal_terms': len(row), 'new_13_height': 0})
            need(len(query_report) == 8, 'All eight pre-division observables')
            bill.update(events=len(word['program']), arbitrary_inputs=640, logical_helpers=408,
                        private_zero_returns=91, C0_exit='zero at I', C1_to_C7='arbitrary identity at I',
                        division_queries=query_report, local_prefix_13_height_bound=1,
                        ordered_warp_algebra='free K or dual_K words; adjacent inverse cancellation only')
            report['providers'][name][key] = bill
            print(name, key, 'PASS_640_COLUMNS_AND_8_QUERY_OBSERVABLES', flush=True)

provider = payload['providers']['base']
word = provider['words']['E_forward']
c = provider['canonical']
fields = [('L', i) for i in range(632)]+[('C', i) for i in range(8)]+[('Z', z) for z in c['zero_buffers']]
want = expected(fields, R, set(range(4)), False)
controls = {}
changed = deepcopy(word['program'])
changed.pop(next(i for i, e in enumerate(changed) if e[0] == 'divide_odd'))
controls['omitted_weighted_entrance_division'] = pullback(changed, fields)[0] != want
changed = deepcopy(word['program'])
changed[word['centre_bindings'][0]['position']+2][1][3] *= -1
controls['changed_centre_scatter_sign'] = pullback(changed, fields)[0] != want
changed = deepcopy(word['program'])
changed.append(['scalar', ['clear', ['C', 1]], 0])
controls['erased_untouched_arbitrary_owned_input'] = pullback(changed, fields)[0] != want
changed = deepcopy(word['program'])
changed[word['centre_bindings'][0]['position']][2] = 0
try:
    types(changed, c)
except ValueError as error:
    controls['changed_centre_input_frame'] = 'Native frame' in str(error)
else:
    controls['changed_centre_input_frame'] = False
need(all(controls.values()), 'Every negative control fails the intended contract')
report['negative_controls'] = controls
report['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
report['phase_scope'] = 'Exact byte binding to the prior independent all-3036-edge review, including all 32 centre directions and literal backward dual warps. No second compiler or phase interpreter is claimed in this run.'
report['scope'] = 'Complete local rational maps, arbitrary logical helper restoration, typed native occurrences, scalar and native invoices, and one new 13-denominator level. No global controller, new recursive provider, owner layout, or kappa claim.'
(HERE/'CHECKS.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
print(report['status'])
