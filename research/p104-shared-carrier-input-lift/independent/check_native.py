"""Independent exact adjoint and chronological audit of the helper368 split
and of the shared-carrier input lift applied to it.

No constructor, primary interpreter or primary arithmetic code is imported.
run_split: Jerry Chen / @CubeJerry, substantial OpenAI assistance. Apache-2.0.
run_lift and the combined run: DreamingOfClouds with Claude Opus 5.5
(Anthropic), via Claude Code. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def word(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def combination_add(target, source, factor):
    for index, coefficient in source.items():
        value = target.get(index, 0) + factor * coefficient
        if value:
            target[index] = value
        else:
            target.pop(index, None)


def subspace(basis):
    values = {0}
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512,
                'binary vector in nine axes')
        require(vector not in values, 'independent frame basis')
        values.update([value ^ vector for value in values.copy()])
    return values


def chronology(data):
    public, owned = data['public'], data['owned_fields']
    total = public + owned
    require(len(data['initial']) == len(data['final']) == public, 'boundaries')
    frames = [subspace(vectors) for vectors in data['frames']]
    current = data['initial'].copy() + [None] * owned
    alive, maximum, lifetimes, scalar = set(), 0, 0, 0
    paid, monitors, opcodes = Counter(), [], Counter()
    for index, event in enumerate(data['program']):
        operation, target = event[:2]
        opcodes[operation] += 1
        require(type(target) is int and 0 <= target < total, 'target index')
        if operation == 'MOVE':
            require(len(event) == 5, 'MOVE format')
            before, after, private = event[2:]
            require(current[target] == before, 'MOVE incoming chart')
            require(private == (target in alive), 'MOVE owner type')
            require(frames[after] < frames[before] if private
                    else frames[before] < frames[after], 'strict nested MOVE')
            paid[abs(len(data['frames'][after])-len(data['frames'][before]))] += 1
            current[target] = after
        elif operation == 'INIT':
            require(len(event) == 3 and target >= public and target not in alive,
                    'fresh owned INIT')
            alive.add(target)
            current[target] = event[2]
            lifetimes += 1
            maximum = max(maximum, len(alive))
            scalar += 2
        elif operation == 'CLEAR':
            require(len(event) == 3 and target in alive and
                    current[target] == event[2], 'owned CLEAR')
            monitors.append((index, operation, target, event[2]))
            current[target] = None
            alive.remove(target)
            scalar += 2
        elif operation in ('ADD', 'COPY', 'SCALE'):
            coefficient = Fraction(event[-2])
            chart = event[-1]
            require(coefficient != 0 and current[target] == chart,
                    'scalar coefficient/chart')
            numerator, denominator = abs(coefficient.numerator), coefficient.denominator
            require(denominator & (denominator-1) == 0, 'dyadic denominator')
            require(abs(coefficient)+1 < 2**16, 'fixed coefficient bound')
            if operation == 'SCALE':
                require(len(event) == 4 and numerator & (numerator-1) == 0,
                        'dyadic-unit SCALE')
                scalar += 2*(abs(numerator.bit_length()-denominator.bit_length()) +
                             int(coefficient < 0))
            else:
                require(len(event) == 5, 'ADD/COPY format')
                source = event[2]
                require(source != target and 0 <= source < total and
                        current[source] == chart, 'scalar common chart')
                if operation == 'COPY':
                    require(target in alive, 'COPY into owned field')
                    monitors.append((index, operation, target, chart))
                scalar += 2*(3+numerator.bit_length()-1+numerator.bit_count()+
                             denominator.bit_length()-1)
        else:
            raise ValueError('Unknown opcode ' + operation)
    require(not alive and current[:public] == data['final'], 'complete exits')
    require(all(chart is None for chart in current[public:]), 'owned exits')
    main = set(data['live']) | {r+112 for r in data['live']}
    require(len(main) == 208 and len(data['live']) == len(data['ports']) == 104,
            'main interface count')
    helpers = Counter()
    for role in range(public):
        if role not in main:
            before, after = data['initial'][role], data['final'][role]
            require(frames[before] < frames[after], 'productive helper endpoint')
            helpers[len(data['frames'][after])-len(data['frames'][before])] += 1
    return dict(public=public, owned=owned, total=total, events=len(data['program']),
                paid=dict(sorted(paid.items())), helpers=dict(sorted(helpers.items())),
                scalar=scalar, peak=maximum, lifetimes=lifetimes,
                opcodes=dict(opcodes), monitors=monitors)


def adjoint(data, metadata):
    """Reverse all endpoint coefficients and all pre-COPY/CLEAR functionals."""
    n, public = metadata['total'], metadata['public']
    columns = [{r: Fraction(1)} for r in range(n)]
    monitor_at = {entry[0]: (n+j, entry) for j, entry in enumerate(metadata['monitors'])}
    for index in range(len(data['program'])-1, -1, -1):
        event = data['program'][index]
        operation, target = event[:2]
        if operation in ('INIT', 'CLEAR'):
            columns[target] = {}
        elif operation == 'SCALE':
            factor = Fraction(event[2])
            columns[target] = {row: factor*value for row, value in columns[target].items()}
        elif operation in ('ADD', 'COPY'):
            source, factor = event[2], Fraction(event[3])
            combination_add(columns[source], columns[target], factor)
            if operation == 'COPY':
                columns[target] = {}
        if index in monitor_at:
            row, _ = monitor_at[index]
            columns[target][row] = Fraction(1)
    for source, column in enumerate(columns):
        actual = {r: c for r, c in column.items() if r < n}
        expected = {source: Fraction(1)} if source < public else {}
        if source in data['live']:
            expected[source+112] = Fraction(1)
        require(actual == expected, 'complete endpoint column ' + str(source))
    monitor_rows = []
    for j, entry in enumerate(metadata['monitors']):
        row = {source: column[n+j] for source, column in enumerate(columns)
               if n+j in column}
        require(all(source < public for source in row), 'owned initial values disappear')
        if entry[1] == 'COPY':
            require(not row, 'COPY destination exactly zero at ' + str(entry[0]))
        monitor_rows.append((entry, row))
    return monitor_rows


def audit(data):
    metadata = chronology(data)
    monitors = adjoint(data, metadata)
    metadata.pop('monitors')
    metadata['all_coefficients'] = metadata['total'] ** 2
    metadata['copy_zero_checks'] = sum(entry[1] == 'COPY' for entry, row in monitors)
    metadata['clear_nonzero'] = sum(entry[1] == 'CLEAR' and bool(row) for entry, row in monitors)
    return metadata, monitors


def delta(after, before):
    return {r: after.get(r, 0)-before.get(r, 0)
            for r in sorted(set(after)|set(before)) if after.get(r, 0) != before.get(r, 0)}


def decode_witness(value):
    return {int(k): Fraction(v) for k, v in value.items()}


def scalar_response(data, vector, events):
    """One forward vector, used only to bind the independently stated cut."""
    values = [Fraction(0)] * (data['public']+data['owned_fields'])
    for index, coefficient in vector.items():
        values[index] = coefficient
    for event in events:
        operation, target = event[:2]
        if operation in ('INIT', 'CLEAR'):
            values[target] = Fraction(0)
        elif operation == 'SCALE':
            values[target] *= Fraction(event[2])
        elif operation == 'ADD':
            values[target] += Fraction(event[3])*values[event[2]]
        elif operation == 'COPY':
            require(values[target] == 0, 'witness suffix preserves COPY-zero')
            values[target] = Fraction(event[3])*values[event[2]]
    return {i: value for i, value in enumerate(values) if value}


def pullback(functional, events):
    """One reverse functional; independent of the parent search's prefix rows."""
    values = dict(functional)
    for event in reversed(events):
        operation, target = event[:2]
        coefficient = values.get(target, Fraction(0))
        if operation in ('INIT', 'CLEAR'):
            values.pop(target, None)
        elif operation == 'SCALE':
            if coefficient:
                values[target] = coefficient*Fraction(event[2])
        elif operation in ('ADD', 'COPY'):
            if coefficient:
                source = event[2]
                value = values.get(source, 0)+coefficient*Fraction(event[3])
                if value:
                    values[source] = value
                else:
                    values.pop(source, None)
            if operation == 'COPY':
                values.pop(target, None)
    return values


def run_split(base_path, candidate_path, witness_path, controls):
    baseline, candidate = word(base_path), word(candidate_path)
    require(sha256(base_path.read_bytes()).hexdigest() ==
            'e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d',
            'pinned #6702 source word')
    base, old_monitors = audit(baseline)
    new, new_monitors = audit(candidate)
    require(candidate['frames'] == baseline['frames'] and
            candidate['live'] == baseline['live'] and candidate['ports'] == baseline['ports'],
            'unchanged frames and main ports')
    require(candidate['public'] == baseline['public']+1 and
            candidate['owned_fields'] == baseline['owned_fields'], 'one fresh public field')
    require(candidate['initial'] == baseline['initial']+[243], 'initial boundary')
    final = baseline['final'].copy()
    final[368] = 243
    require(candidate['final'] == final+[127], 'only declared final boundaries')
    paid_delta = delta(new['paid'], base['paid'])
    target_delta = delta(new['helpers'], base['helpers'])
    require(paid_delta == {1: 1, 5: 1, 6: -1}, 'exact paid delta')
    require(target_delta == {4: 1, 5: 1, 9: -1}, 'exact target delta')
    require(new['lifetimes'] == base['lifetimes'] == 47 and
            new['peak'] == base['peak'] == 14, 'owned lifetime and peak unchanged')
    old_clears = [(entry, row) for entry, row in old_monitors if entry[1] == 'CLEAR']
    new_clears = [(entry, row) for entry, row in new_monitors if entry[1] == 'CLEAR']
    require(len(old_clears) == len(new_clears) == 47, 'same CLEAR count')
    for (old_event, old_row), (new_event, new_row) in zip(old_clears, new_clears):
        require(old_event[2]+1 == new_event[2] and old_event[3] == new_event[3],
                'unchanged owned CLEAR labels and charts')
        require(bool(old_row) == bool(new_row), 'no newly nonzero owned erasure')
    # Prepare the paid path directly from the supplied old event/cut, not from
    # the parent constructor, then audit its old endpoint and bind the witness.
    require(baseline['program'][14088] == ['MOVE',80,749,127,False], 'old MOVE')
    for event in baseline['program'][12372:14088]:
        require(event[1] != 80 and not(event[0] in ('ADD','COPY') and event[2] == 80),
                'role80 inactive throughout advanced-MOVE interval')
    prepared = deepcopy(baseline)
    prepared['program'] = (baseline['program'][:12372]+[['MOVE',80,749,243,False]]+
                           [['MOVE',80,243,127,False]]+
                           baseline['program'][12372:14088]+baseline['program'][14089:])
    prepared_metadata, _ = audit(prepared)
    require(delta(prepared_metadata['paid'], base['paid']) == paid_delta,
            'prepared MOVE invoice')
    h = json.loads(witness_path.read_text())['split']
    a,b,c,d = (decode_witness(h[key]) for key in ('a','b','c','d'))
    prefix = prepared['program'][:12373]
    suffix = prepared['program'][12373:]
    require(pullback(a, prefix) == c, 'complete prefix functional')
    require(scalar_response(prepared,b,suffix) == d, 'complete suffix direction')
    require(sum(value*b.get(i,0) for i,value in a.items()) ==
            sum(value*d.get(i,0) for i,value in c.items()) == 1, 'unit pairings')
    main = set(baseline['live'])|{r+112 for r in baseline['live']}
    require(all(i not in main and baseline['initial'][i] == 3 and
                baseline['final'][i] == 127 for i in set(c)|set(d)), 'one helper group')
    changed_pairs = set((e[2],e[3]) for e in candidate['program'] if e[0] == 'MOVE') - set(
        (e[2],e[3]) for e in baseline['program'] if e[0] == 'MOVE')
    failures = []
    if controls:
        # Each mutation reaches this independent full-word interpreter.
        mutation_indices = [0,12,12385,12386,12394,12395,12404,18609,18621]
        for index in mutation_indices:
            mutant = deepcopy(candidate)
            del mutant['program'][index]
            try:
                audit(mutant)
            except ValueError as error:
                failures.append(dict(kind='omission',index=index,rejected=str(error)))
            else:
                raise ValueError('omission accepted at '+str(index))
        mutant = deepcopy(candidate)
        mutant['final'][368] = 127
        try:
            audit(mutant)
        except ValueError as error:
            failures.append(dict(kind='unearned old target',rejected=str(error)))
        else:
            raise ValueError('wrong target accepted')
    return dict(status='PASS_INDEPENDENT_PAID_HELPER368_SPLIT',
                source_sha256=sha256(base_path.read_bytes()).hexdigest(),
                candidate_sha256=sha256(candidate_path.read_bytes()).hexdigest(),
                base=base,candidate=new,paid_delta=paid_delta,target_delta=target_delta,
                new_native_chart_pairs=sorted(changed_pairs),
                exact_pairings=True,copy_zero_guard_checked=True,
                zero_clear_pattern_preserved=True,controls=failures,
                limitations=['Native phase/all-column replay not performed here.',
                             'Complete caller/outer invoice and uniform admission not performed here.',
                             'Exact rational normalized word and chronological interface audited.'])


PINNED_6805 = '292b3ab3afb74e87deffd7770e5627e94debd610459221686c05ca04b8885d3f'
LIFTED = (556, 664)
SIGMA = {664: {664: Fraction(1)}, 665: {665: Fraction(1), 664: Fraction(1)}}


def payload(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode()


def forward_rows(data, stop):
    """Exact linear form of every register after the first stop events."""
    total = data['public']+data['owned_fields']
    rows = [{r: Fraction(1)} if r < data['public'] else {} for r in range(total)]
    for event in data['program'][:stop]:
        operation, target = event[:2]
        if operation in ('INIT', 'CLEAR', 'COPY'):
            rows[target] = {}
        if operation == 'SCALE':
            rows[target] = {k: v*Fraction(event[2]) for k, v in rows[target].items()}
        elif operation in ('ADD', 'COPY'):
            combination_add(rows[target], rows[event[2]], Fraction(event[3]))
    return rows


def clear_rows(data):
    """Exact forward value of the owned register at each CLEAR, in event order."""
    total = data['public']+data['owned_fields']
    rows = [{r: Fraction(1)} if r < data['public'] else {} for r in range(total)]
    seen = []
    for event in data['program']:
        operation, target = event[:2]
        if operation == 'CLEAR':
            seen.append((target, dict(rows[target])))
        if operation in ('INIT', 'CLEAR', 'COPY'):
            rows[target] = {}
        if operation == 'SCALE':
            rows[target] = {k: v*Fraction(event[2]) for k, v in rows[target].items()}
        elif operation in ('ADD', 'COPY'):
            combination_add(rows[target], rows[event[2]], Fraction(event[3]))
    return seen


def substituted(row):
    """Old-coordinate form evaluated at x664=y664, x665=y665+y664."""
    out = {}
    for key, value in row.items():
        combination_add(out, SIGMA.get(key, {key: Fraction(1)}), value)
    return out


def event_key(event):
    return json.dumps(event)


def run_lift(intermediate_path, candidate_path, edit_path, controls):
    old, new = word(intermediate_path), word(candidate_path)
    require(sha256(payload(old)).hexdigest() == PINNED_6805, 'pinned #6805 intermediate word')
    old_meta, _ = audit(old)
    new_meta, monitors = audit(new)          # complete endpoint identity for arbitrary inputs
    for key in ('frames', 'live', 'ports', 'final', 'public', 'owned_fields'):
        require(new[key] == old[key], 'lift leaves '+key+' unchanged')
    changed = [r for r in range(old['public']) if old['initial'][r] != new['initial'][r]]
    require(changed == list(LIFTED), 'exactly the two lifted helpers change birth frame')
    require(all(old['initial'][r] == 3 and new['initial'][r] == 105 for r in changed) and
            old['final'][556] == 246 and old['final'][664] == 127, 'births Z->105 with full exits')
    require(set(old['live']) | {r+112 for r in old['live']}
            == set(new['live']) | {r+112 for r in new['live']} and
            not set(LIFTED) & (set(old['live']) | {r+112 for r in old['live']}),
            'lifted roles are independent helpers')
    paid_delta = delta(new_meta['paid'], old_meta['paid'])
    target_delta = delta(new_meta['helpers'], old_meta['helpers'])
    require(paid_delta == {1: 2, 3: -1, 4: 1, 5: -1}, 'exact lift paid delta')
    require(target_delta == {7: 1, 9: -1}, 'exact lift target delta')
    require(new_meta['lifetimes'] == old_meta['lifetimes'] == 47 and
            new_meta['peak'] == old_meta['peak'] == 14, 'owned lifetime and peak unchanged')
    # The edit list, applied by an independent routine, produces the candidate exactly.
    edit = json.loads(edit_path.read_text())
    program, position = [], 0
    for item in edit['edits']:
        at, gone = item['at'], item['delete']
        require(at >= position and old['program'][at:at+len(gone)] == gone, 'bound deleted events')
        following = old['program'][at+len(gone)] if at+len(gone) < len(old['program']) else None
        require(following == item['next'], 'bound following event')
        program += old['program'][position:at]+item['insert']
        position = at+len(gone)
    program += old['program'][position:]
    require(program == new['program'], 'edit list reproduces the candidate program')
    removed = Counter(map(event_key, old['program']))-Counter(map(event_key, new['program']))
    added = Counter(map(event_key, new['program']))-Counter(map(event_key, old['program']))
    require(sum(removed.values()) == 9 and sum(added.values()) == 9, 'nine events replaced as a multiset')
    # Defects and cancellation, in the actual events.  First the deleted events:
    cut_old, cut_new = 9341, 9343
    require(old['program'][cut_old] == ['ADD', 179, 663, '1/2', 105] and
            new['program'][cut_new-1] == ['ADD', 665, 664, '1', 1051], 'lift block boundary events')
    first = next(i for i in edit['edits'] if i['insert'] and i['at'] > 5000)
    shift = sum(len(i['insert'])-len(i['delete']) for i in edit['edits'] if i['at'] < first['at'])
    before_old = forward_rows(old, first['at'])
    before_new = forward_rows(new, first['at']+shift)
    defect = {}
    for r, row in enumerate(before_new):
        d = dict(row)
        combination_add(d, substituted(before_old[r]), Fraction(-1))
        if d:
            defect[r] = d
    require(set(defect) == {120, 179, 665}, 'defects live in the carrier, one recipient and the partner helper')
    require(defect[665] == {664: Fraction(-1)} and defect[179] == {664: Fraction(1)} and
            defect[120] == {664: Fraction(1), 556: Fraction(-1, 2)}, 'literal defects before delivery')
    after_old, after_new = forward_rows(old, cut_old), forward_rows(new, cut_new)
    require(all(substituted(a) == b for a, b in zip(after_old, after_new)),
            'after the delivery block every register equals the old register at x=sigma(y)')
    suffix_old = [e for e in old['program'][cut_old:] if e not in (['MOVE', 665, 3, 1051, False], ['MOVE', 664, 3, 1051, False], ['MOVE', 120, 3, 430, False], ['MOVE', 556, 3, 755, False])]
    suffix_new = [e for e in new['program'][cut_new:-1] if e not in (['MOVE', 556, 105, 755, False],)]
    require(suffix_old == suffix_new, 'identical events after the delivery block apart from the four re-framed moves')
    require(new['program'][-1] == ['ADD', 665, 664, '-1', 127] and
            forward_rows(old, len(old['program']))[664] == {664: Fraction(1)}, 'final repair removes y664 from role 665')
    old_clears, new_clears = clear_rows(old), clear_rows(new)
    require(len(old_clears) == len(new_clears) == 47 and
            all(o[0] == n[0] and substituted(o[1]) == n[1] for o, n in zip(old_clears, new_clears)),
            'all 47 erased owned values are unchanged at x=sigma(y); in particular the zero pattern')
    failures = []
    if controls:
        inserted = [(i, e) for i, e in enumerate(new['program']) if e in sum((x['insert'] for x in edit['edits']), []) and e[0] == 'ADD']
        for index, event in inserted:
            mutant = deepcopy(new)
            mutant['program'][index] = event[:3]+[str(Fraction(event[3])*2)]+event[4:]
            try:
                audit(mutant)
            except ValueError as error:
                failures.append(dict(kind='wrong coefficient', index=index, rejected=str(error)))
            else:
                raise ValueError('wrong lift coefficient accepted at '+str(index))
        for index in (len(new['program'])-1, inserted[0][0], inserted[2][0]):
            mutant = deepcopy(new)
            del mutant['program'][index]
            try:
                audit(mutant)
            except ValueError as error:
                failures.append(dict(kind='omission', index=index, rejected=str(error)))
            else:
                raise ValueError('omission accepted at '+str(index))
        mutant = deepcopy(new)
        mutant['initial'][664] = 3
        try:
            audit(mutant)
        except ValueError as error:
            failures.append(dict(kind='birth frame restored without the edit', rejected=str(error)))
        else:
            raise ValueError('inconsistent birth accepted')
        mutant = deepcopy(new)
        for event in mutant['program']:
            if event[1] == 665:
                event[1] = 664
            if event[0] == 'ADD' and event[2] == 665:
                event[2] = 664
        try:
            audit(mutant)
        except ValueError as error:
            failures.append(dict(kind='aliased lifted helpers', rejected=str(error)))
        else:
            raise ValueError('aliased helpers accepted')
    return dict(status='PASS_INDEPENDENT_SHARED_CARRIER_LIFT', intermediate_sha256=PINNED_6805,
                candidate=new_meta, paid_delta=paid_delta, target_delta=target_delta,
                erased_values_unchanged=47, removed_events=sum(removed.values()), added_events=sum(added.values()),
                defects_before_delivery={str(r): {str(k): str(v) for k, v in d.items()} for r, d in sorted(defect.items())},
                controls=failures)


def run(base_path, intermediate_path, candidate_path, witness_path, edit_path, controls):
    split = run_split(base_path, intermediate_path, witness_path, controls)
    lift = run_lift(intermediate_path, candidate_path, edit_path, controls)
    cumulative_paid = Counter(split['paid_delta'])
    cumulative_paid.update(lift['paid_delta'])
    cumulative_target = Counter(split['target_delta'])
    cumulative_target.update(lift['target_delta'])
    return dict(status='PASS_INDEPENDENT_SHARED_CARRIER_INPUT_LIFT',
                source_sha256=sha256(base_path.read_bytes()).hexdigest(),
                intermediate_sha256=PINNED_6805,
                candidate_sha256=sha256(candidate_path.read_bytes()).hexdigest(),
                base=split['base'], candidate=lift['candidate'],
                paid_delta={r: v for r, v in sorted(cumulative_paid.items()) if v},
                target_delta={r: v for r, v in sorted(cumulative_target.items()) if v},
                split=split, lift=lift,
                limitations=split['limitations'])


if __name__ == '__main__':
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument('--base',type=Path,default=here/'retained/native/PR6702-WORD.json.gz')
    parser.add_argument('--intermediate',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--lift',type=Path,default=here/'LIFT.json')
    parser.add_argument('--witness',type=Path,default=here/'WITNESS.json')
    parser.add_argument('--output',type=Path,default=Path(__file__).with_name('RESULT.json'))
    parser.add_argument('--controls',action='store_true')
    args = parser.parse_args()
    result = run(args.base,args.intermediate,args.candidate,args.witness,args.lift,args.controls)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
    print(json.dumps({key:result[key] for key in ('paid_delta','target_delta','new_native_chart_pairs')},sort_keys=True))
