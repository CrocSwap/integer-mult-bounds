#!/usr/bin/env python3
"""Check the exact rational split optimum on the pinned eight flags."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha1, sha256
import importlib.util
from itertools import product
import json
from math import gcd
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_module():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        raw = (ROOT / pin['retained']).read_bytes()
        blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == pin['git_blob'] and sha256(raw).hexdigest() == pin['sha256'],
                'source pin')
    path = ROOT / 'retained/source7748/verify.py'
    spec = importlib.util.spec_from_file_location('source7748', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def affine_column(s, labels, arrivals, deadlines, weights, column):
    active = [k for k in range(8) if any(weights[k][column])]
    variables = [(k, j) for k in active for j in range(1, deadlines[k][column] + 1)
                 if any(arrivals[k][t] == j and weights[k][column][t] for t in range(104))]
    forms = []
    groups = Counter()
    forced = 0
    for t in range(104):
        constant = sum(weights[k][column][t] for k in active
                       if arrivals[k][t] > deadlines[k][column])
        row = tuple(weights[k][column][t] if arrivals[k][t] == j else 0
                    for k, j in variables) + (constant,)
        forms.append(row)
        if t == column or s.dot(labels[t], labels[column]):
            require(not any(row[:-1]) and row[-1] == (2 if t == column else 0),
                    'required entry depends on a free prefix')
        elif not any(row[:-1]):
            forced += bool(row[-1])
        else:
            divisor = gcd(*row)
            normalized = tuple(x // divisor for x in row)
            if next(x for x in normalized if x) < 0:
                normalized = tuple(-x for x in normalized)
            groups[normalized] += 1
    return active, variables, forms, sorted(groups.items()), forced


def solve(rows, dimension):
    """Return one rational solution, or None for an inconsistent system."""
    matrix = [list(map(Fraction, row)) for row in rows]
    pivot_rows = []
    for column in range(dimension):
        level = len(pivot_rows)
        pivot = next((i for i in range(level, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[level], matrix[pivot] = matrix[pivot], matrix[level]
        value = matrix[level][column]
        matrix[level] = [x / value for x in matrix[level]]
        for i in range(len(matrix)):
            if i != level:
                factor = matrix[i][column]
                matrix[i] = [x - factor * y for x, y in zip(matrix[i], matrix[level], strict=True)]
        pivot_rows.append(column)
    if any(not any(row[:-1]) and row[-1] for row in matrix):
        return None
    answer = [Fraction(0)] * dimension
    for i, column in enumerate(pivot_rows):
        answer[column] = -matrix[i][-1]
    return answer


def conflict_bound(groups, conflicts):
    """Use integer contradiction certificates and finite subset coverage."""
    masks = []
    for conflict in conflicts:
        mask = conflict['mask']
        require(type(mask) is int and 0 < mask < 1 << len(groups), 'conflict mask')
        indices = [i for i in range(len(groups)) if mask >> i & 1]
        multipliers = conflict['lambda_']
        require(len(indices) == len(multipliers) and
                all(type(x) is int and x for x in multipliers), 'conflict coefficients')
        combination = [sum(a * groups[i][0][j] for a, i in zip(multipliers, indices, strict=True))
                       for j in range(len(groups[0][0]))]
        require(not any(combination[:-1]) and combination[-1] != 0, 'false contradiction')
        masks.append(mask)
    require(len(set(masks)) == len(masks), 'duplicate conflict')
    feasible = []
    for mask in range(1 << len(groups)):
        if not any(mask & bad == bad for bad in masks):
            feasible.append(mask)
    maximum = max(sum(weight for i, (_, weight) in enumerate(groups) if mask >> i & 1)
                  for mask in feasible)
    return sum(weight for _, weight in groups) - maximum, set(feasible)


def schedule_from_prefixes(variables, values, active, deadlines, column):
    chosen = dict(zip(variables, values, strict=True))
    schedule = {}
    for k in active:
        limit = deadlines[k][column]
        cumulative = [Fraction(0)]
        for j in range(1, limit + 1):
            cumulative.append(chosen.get((k, j), Fraction(0)))
        cumulative.append(Fraction(1))
        schedule[k] = [(j, cumulative[j + 1] - cumulative[j]) for j in range(limit + 1)
                       if cumulative[j + 1] != cumulative[j]]
    return schedule


def direct_column(schedule, column, arrivals, weights):
    """Accumulate each individual gather into every later reader."""
    output = [Fraction(0)] * 104
    for k, pieces in schedule.items():
        for level, amount in pieces:
            for t in range(104):
                if arrivals[k][t] > level:
                    output[t] += amount * weights[k][column][t]
    return output


def reject(call, message):
    try:
        call()
    except ValueError as error:
        require(str(error) == message, 'wrong rejection')
    else:
        raise ValueError('fault passed')


def verify():
    s = source_module()
    data = json.loads((ROOT / 'retained/source7748/WITNESS.json').read_text())
    labels = data['labels']
    gram = s.reconstruct_gram(data)
    arrivals, deadlines, weights = s.model(data, gram)
    certificate = json.loads((ROOT / 'RESULT.json').read_text())
    require([r['column'] for r in certificate] == list(range(104)), 'column coverage')
    totals = Counter()
    models = []
    for row in certificate:
        column = row['column']
        active, variables, forms, groups, forced = affine_column(
            s, labels, arrivals, deadlines, weights, column)
        require(row['variables'] == [list(v) for v in variables] and
                row['groups'] == [[list(form), weight] for form, weight in groups] and
                row['forced'] == forced, 'affine certificate')
        extra, consistent_masks = conflict_bound(groups, row['conflicts'])
        require(row['minimum'] == forced + extra, 'minimum bound')
        linear_masks = set()
        for mask in range(1 << len(groups)):
            selected = [form for i, (form, _) in enumerate(groups) if mask >> i & 1]
            if solve(selected, len(variables)) is not None:
                linear_masks.add(mask)
        require(linear_masks == consistent_masks and len(linear_masks) == row['feasible_subsets'],
                'independent subset elimination')
        values = list(map(Fraction, row['witness']))
        schedule = schedule_from_prefixes(variables, values, active, deadlines, column)
        serialized = {str(k): [[j, str(v)] for j, v in pieces] for k, pieces in schedule.items()}
        require(serialized == row['schedule'], 'schedule certificate')
        output = s.run_column(column, schedule, arrivals, deadlines, weights)
        require(output == direct_column(schedule, column, arrivals, weights), 'direct piece replay')
        require(output == [sum(a * b for a, b in zip(form[:-1], values, strict=True)) + form[-1]
                           for form in forms], 'affine replay')
        totals['odd'] += s.check_required_entries(column, output, labels)
        require(s.junk(column, output, labels) == row['minimum'], 'matching optimum witness')
        singles = []
        for levels in product(*(range(deadlines[k][column] + 1) for k in active)):
            single = {k: [(level, 1)] for k, level in zip(active, levels, strict=True)}
            output = s.run_column(column, single, arrivals, deadlines, weights)
            s.check_required_entries(column, output, labels)
            singles.append(s.junk(column, output, labels))
        require(len(singles) == row['unsplit_schedules'] and min(singles) == row['unsplit_minimum'],
                'single-gather optimum')
        for numerator, denominator in [(-3, 2), (1, 3), (5, 2), (7, 3)]:
            trial = [Fraction(numerator + i, denominator) for i in range(len(variables))]
            pieces = schedule_from_prefixes(variables, trial, active, deadlines, column)
            output = direct_column(pieces, column, arrivals, weights)
            require(output == s.run_column(column, pieces, arrivals, deadlines, weights),
                    'rational source replay')
            require(output == [sum(a * b for a, b in zip(form[:-1], trial, strict=True)) + form[-1]
                               for form in forms], 'rational affine replay')
        for key, value in dict(minimum=row['minimum'], unsplit=row['unsplit_minimum'],
                               forced=forced, subsets=1 << len(groups),
                               conflicts=len(row['conflicts']), singles=len(singles),
                               active=len(active), pieces=sum(len(v) for v in schedule.values()),
                               improved=int(row['minimum'] < row['unsplit_minimum'])).items():
            totals[key] += value
        models.append((variables, groups, active))
    expected = dict(odd=5720, minimum=4745, unsplit=4814, forced=4715, subsets=1400,
                    conflicts=23, singles=1242, active=416, pieces=490, improved=44)
    require(dict(totals) == expected, 'global totals')
    variables, groups, active = models[4]
    require(certificate[4]['minimum'] == 43 and certificate[4]['unsplit_minimum'] == 45,
            'source column optimum')
    broken = deepcopy(certificate[4]['conflicts'])
    broken[0]['lambda_'][0] *= -1
    reject(lambda: conflict_bound(groups, broken), 'false contradiction')
    missing = certificate[4]['conflicts'][1:]
    require(conflict_bound(groups, missing)[0] == 1, 'missing conflict control')
    values = list(map(Fraction, certificate[4]['witness']))
    values[-1] = Fraction(1)
    wrong = schedule_from_prefixes(variables, values, active, deadlines, 4)
    output = s.run_column(4, wrong, arrivals, deadlines, weights)
    require(s.junk(4, output, labels) == 44, 'lost gain control')
    late = deepcopy(wrong)
    late[6] = [(2, 1)]
    reject(lambda: s.run_column(4, late, arrivals, deadlines, weights), 'gather after cutoff')
    bad_total = deepcopy(wrong)
    bad_total[6] = [(0, 2)]
    reject(lambda: s.run_column(4, bad_total, arrivals, deadlines, weights),
           'gather coefficients must sum to one')
    mode = ['-O'] if sys.flags.optimize else []
    result = subprocess.run([sys.executable, '-W', 'error', *mode, '-B',
                             str(ROOT / 'retained/source7748/verify.py')],
                            capture_output=True, text=True, timeout=30)
    require(result.returncode == 0 and 'PASS_P104_C56_SPLIT_GATHER_WITNESS' in result.stdout,
            'unchanged source replay')
    print('PASS_P104_FIXED_FLAG_SPLIT_OPTIMUM')
    print('104 columns: exact rational split optimum 4745; single-gather optimum 4814')
    print('4715 forced cells and 23 contradiction certificates force 30 more; 1400 subsets agree')
    print('490 gather pieces; 104 diagonals and 5720 odd zeros; source column 4 improves 44 to 43')


if __name__ == '__main__':
    verify()
