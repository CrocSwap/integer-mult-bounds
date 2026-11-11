"""Test the two chart-local source banks for the #7314 donor-1355 fusion."""

from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from tempfile import NamedTemporaryFile
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
PRICE = '25205ad2cf4230bd2b2b704eec9f96ec4a5486fd575b5599861b28ffdd15b00b'
WORD = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
CORE = 'fd7a1a7f9cb8f71caa5e0d89ed16ea056503fa283bc05f655eb0da7e8d5fc6e0'
WORD_PATH = 'round63/price-inputs/inputs/7314/WORD.json.gz'
CUTS = {48182: 739, 48185: 127}
PROTECTED = {863, 1355, 1568}
TARGET = {863: Fraction(1)}


class DeadlineReached(Exception):
    pass


def checked(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f'Changed input {path.name}')
    return raw


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('Duplicate JSON key')
    return result


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def encode(value):
    return (dumps(value, indent=2, sort_keys=True) + '\n').encode()


def check_time(deadline):
    if monotonic() >= deadline:
        raise DeadlineReached


def axpy(dst, src, factor):
    for key, coefficient in src.items():
        new = dst.get(key, 0) + factor*coefficient
        if new:
            dst[key] = new
        else:
            dst.pop(key, None)


def dot(left, right):
    return sum(v*right.get(k, 0) for k, v in left.items())


def linear_combination(weights, rows):
    value = {}
    for role, coefficient in weights.items():
        axpy(value, rows[role], coefficient)
    return value


def solve(target, donors, deadline):
    basis, nullspace = {}, []
    for role, donor in donors.items():
        check_time(deadline)
        row, weights = donor.copy(), {role: Fraction(1)}
        for pivot in sorted(basis):
            if pivot in row:
                scale = -row[pivot]
                old, coefficients = basis[pivot]
                axpy(row, old, scale)
                axpy(weights, coefficients, scale)
        if row:
            pivot = min(row)
            factor = row[pivot]
            basis[pivot] = ({k: v/factor for k,v in row.items()},
                            {k: v/factor for k,v in weights.items()})
        else:
            assert not linear_combination(weights, donors)
            nullspace.append(weights)
    assert len(basis) + len(nullspace) == len(donors)
    residual, solution = target.copy(), {}
    for pivot, (row, coefficients) in sorted(basis.items()):
        if pivot in residual:
            factor = residual[pivot]
            axpy(residual, row, -factor)
            axpy(solution, coefficients, factor)
    if not residual:
        assert linear_combination(solution, donors) == target
        return 'span', len(basis), solution, nullspace
    free = min(residual)
    dual = {free: Fraction(1)}
    assert free not in basis
    for pivot, (row, _) in sorted(basis.items(), reverse=True):
        coefficient = -dot(row, dual)
        if coefficient:
            dual[pivot] = coefficient
    assert all(dot(donor, dual) == 0 for donor in donors.values())
    assert dot(target, dual) == residual[free] != 0
    return 'separating_dual', len(basis), dual, nullspace


def legal_add(coefficient):
    denominator = coefficient.denominator
    for prime in (2, 3, 5):
        while denominator % prime == 0:
            denominator //= prime
    return (bool(coefficient) and denominator == 1 and abs(coefficient) + 1 < 2**16
            and abs(coefficient.numerator).bit_length() <= 24)


def serialized(row):
    return {str(k): str(v) for k,v in sorted(row.items())}


def inspect_bank(cut, frame, rows, charts, public, deadline):
    eligible = [r for r, chart in enumerate(charts) if chart == frame and r not in PROTECTED]
    donors = {r: {k: Fraction(v, rows[r][0]) for k,v in rows[r][1].items()}
              for r in eligible}
    kind, rank, witness, nullspace = solve(TARGET, donors, deadline)
    injections = {r: -2*q for r,q in witness.items()} if kind == 'span' else {}
    legal = bool(injections) and all(legal_add(q) for q in injections.values())
    if legal:
        assert linear_combination(injections, donors) == {863: Fraction(-2)}
    return {
        'cut': cut, 'chart': frame, 'rank': rank, 'nullity': len(nullspace),
        'eligible_roles': eligible, 'eligible_owned_roles': [r for r in eligible if r >= public],
        'nonzero_roles': [r for r, row in donors.items() if row],
        'donor_rows_sha256': sha256(encode({str(r): serialized(row) for r,row in donors.items()})).hexdigest(),
        'disposition': 'exact_legal_adds' if legal else 'rational_only_unresolved' if kind == 'span' else kind,
        'witness': serialized(witness), 'nullspace_basis': [serialized(v) for v in nullspace],
        'dual_target_value': str(dot(TARGET, witness)) if kind == 'separating_dual' else None,
        'literal_adds': [['ADD', 1355, r, str(q), frame] for r,q in sorted(injections.items())] if legal else [],
    }


def audit(word, core, deadline, inspect=inspect_bank):
    public, owned = word['public'], word['owned_fields']
    assert (public, owned, len(word['program'])) == (1501, 68, 76461)
    expected = [['MOVE',1355,739,240,False], ['ADD',1355,1568,'-2',240],
                ['MOVE',1355,240,127,False]]
    assert word['program'][48182:48185] == expected
    spans = [core['frame_space'](frame) for frame in word['frames']]
    assert spans[739] < spans[240] < spans[127]
    assert [len(word['frames'][f]) for f in (739,240,127)] == [3,4,9]
    charts = word['initial'] + [None]*owned
    rows = [(1,{r:1}) for r in range(public)] + [None]*owned
    fresh, records = set(), []
    visited = copies = 0
    try:
        for clock in range(48186):
            if clock % 64 == 0:
                check_time(deadline)
            if clock in CUTS:
                assert charts[1355] == CUTS[clock]
                records.append(inspect(clock, CUTS[clock], rows, charts, public, deadline))
                if clock == 48185:
                    break
            op, dest, *args = word['program'][clock]
            if op == 'INIT':
                frame, = args
                assert dest >= public and charts[dest] is None and rows[dest] is None
                charts[dest], rows[dest] = frame, (1,{})
                fresh.add(dest)
            elif op == 'CLEAR':
                frame, = args
                assert dest >= public and charts[dest] == frame and rows[dest] is not None
                charts[dest] = rows[dest] = None
                fresh.discard(dest)
            elif op == 'MOVE':
                old, new, own = args
                assert own == (dest >= public) and charts[dest] == old and rows[dest] is not None
                assert spans[old] < spans[new] or own and spans[new] < spans[old]
                charts[dest] = new
                fresh.discard(dest)
            elif op == 'SCALE':
                q, frame = args
                assert charts[dest] == frame and rows[dest] is not None and Fraction(q)
                rows[dest] = core['scaled'](rows[dest], Fraction(q))
            else:
                source, q, frame = args
                assert op in {'ADD','COPY'} and dest != source and Fraction(q)
                assert charts[dest] == charts[source] == frame and rows[dest] is not None and rows[source] is not None
                if op == 'COPY':
                    assert dest >= public and dest in fresh and not rows[dest][1]
                    rows[dest] = core['scaled'](rows[source], Fraction(q))
                    copies += 1
                else:
                    if clock == 48183:
                        assert rows[1568] == (1,{863:1})
                    rows[dest] = core['plus'](rows[dest], rows[source], Fraction(q))
                fresh.discard(dest)
            visited = clock + 1
    except DeadlineReached:
        pass
    return records, visited, copies


def controls():
    f = Fraction
    deadline = float('inf')
    donors = {5:{863:f(2),1:f(3)}, 6:{1:f(-1)}, 7:{863:f(2),1:f(3)}}
    kind, rank, solution, nullspace = solve(TARGET, donors, deadline)
    assert kind == 'span' and rank == 2 and len(nullspace) == 1
    assert linear_combination({r:-2*q for r,q in solution.items()}, donors) == {863:f(-2)}
    assert all(legal_add(-2*q) for q in solution.values())
    kind, _, dual, _ = solve(TARGET, {5:donors[5]}, deadline)
    assert kind == 'separating_dual' and dot(donors[5], dual) == 0 and dot(TARGET, dual) != 0
    kind, _, illegal, _ = solve(TARGET, {5:{863:f(7)}}, deadline)
    assert kind == 'span' and not legal_add(-2*illegal[5])
    kind, _, _, _ = solve(TARGET, {}, deadline)
    assert kind == 'separating_dual'
    return ['signed_sparse_adds', 'dependent_donor_nullspace', 'exact_separating_dual',
            'forbidden_denominator_is_unresolved', 'empty_bank']


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--out', type=Path)
    gate = parser.add_mutually_exclusive_group(required=True)
    gate.add_argument('--controls-only', action='store_true')
    gate.add_argument('--support', action='store_true')
    args = parser.parse_args()
    if not __debug__:
        parser.error('Run with proof assertions enabled')
    started = monotonic()
    result = {'controls': controls()}
    if args.support:
        price = read(checked(args.root/'price.json', PRICE))
        assert price['head'] == HEAD and price['word_sha256'] == WORD
        assert price['paid_delta'] == {'1':-17,'5':-17,'6':17} and price['target_delta'] == {}
        assert price['input_sha256'][WORD_PATH] == WORD
        core_path = args.root/'inputs/replay_core.py'
        checked(core_path, CORE)
        core = run_path(str(core_path))
        raw_word = checked(args.root/'price-inputs'/WORD_PATH, WORD)
        word = read(decompress(raw_word))
        records, visited, copies = audit(word, core, started + 13)
        seen = {row['cut'] for row in records}
        result.update({
            'head': HEAD, 'price_sha256': PRICE, 'word_sha256': WORD,
            'input_sha256': {'price.json': PRICE, 'inputs/replay_core.py': CORE,
                             f'price-inputs/{WORD_PATH}': WORD},
            'eligible_cuts': list(CUTS), 'records': records, 'visited_prefix_events': visited,
            'checked_copies': copies, 'unvisited_cuts': [clock for clock in CUTS if clock not in seen],
            'case_cap': 2, 'hard_seconds': 15, 'cooperative_seconds': 13,
            'first_unvisited_literal_event': visited if visited < 48185 else None,
        })
    raw = encode(result)
    if args.out is None:
        print(raw.decode(), end='')
    else:
        with NamedTemporaryFile(mode='wb', dir=args.out.parent, prefix='source-span-', delete=False) as output:
            output.write(raw)
        temp = Path(output.name)
        temp.chmod(0o644)
        temp.replace(args.out)


if __name__ == '__main__':
    main()
