# SPDX-License-Identifier: Apache-2.0
"""Test one additional ingress into the two retimed Type A host blocks."""
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import runpy
import sys


N = 36
J8, J9 = 1423, 3058
A, B = (8, 0, 18, 26), (9, 0, 18, 27)
DEMOTED = (1580, 1659)
ROOTS = (0, 18)
SOURCES = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/full_body.py": "352c7d594f357333f027dc46eef0e82226b9552ab31d6890b1695fe994e8c3b4",
}


def identity():
    return [[Fraction(row == column) for column in range(N)] for row in range(N)]


def multiply(left, right):
    columns = list(zip(*right, strict=True))
    return [
        [sum((a * b for a, b in zip(row, column, strict=True) if a and b), Fraction())
         for column in columns]
        for row in left
    ]


def difference(left, right):
    return [[x - y for x, y in zip(a, b, strict=True)]
            for a, b in zip(left, right, strict=True)]


def add_row(matrix, dest, source, scale):
    matrix[dest] = [a + scale * b for a, b in zip(matrix[dest], matrix[source], strict=True)]


def rational_word(events, clocks, phase, demote=False, invert=False):
    """Replay exact real phases with all body values fixed to one."""
    rows = identity()
    orientation = -1 if invert else 1
    for clock in reversed(clocks) if invert else clocks:
        event = events[clock]
        if event[0] == "B":
            continue
        if event[0] == "J":
            x, y, u, v = event[2]
            add_row(rows, y, x, orientation * phase)
            add_row(rows, u, v, -orientation * phase)
            continue
        assert event[0] == "A"
        op, dest, *args = event[1:]
        if op == "ADD":
            add_row(rows, dest, args[0], orientation * Fraction(args[1]))
        elif op == "QUERY":
            assert args[1] == -1
            scale = 1 if demote and clock in DEMOTED else phase
            add_row(rows, dest, args[0], orientation * scale)
        elif op == "SWAP":
            rows[dest], rows[args[0]] = rows[args[0]], rows[dest]
        elif op == "SCALE":
            rows[dest] = [a * Fraction(args[0])**orientation for a in rows[dest]]
        else:
            assert op == "IDLE_ONE" or (op == "LAMBDA" and args[0] in (-1, 1))
    return rows


def retiming(events):
    omit = set()
    hoist = []
    assert events[J8][:3] == ["J", 8, list(A)]
    assert events[J9][:3] == ["J", 9, list(B)]
    assert all(events[k] == ["A", "QUERY", 0, 1, -1] for k in DEMOTED)
    def touches(event, role):
        if event[0] == "J":
            return role in event[2]
        if event[0] == "A":
            return role in event[2:4 if event[1] in ("ADD", "QUERY", "SWAP") else 3]
        return False

    def writes(event, role):
        if event[0] == "A" and event[1] != "SWAP":
            return event[2] == role
        return touches(event, role)

    for clock in range(1448, 1488, 3):
        kind, op, role, mask = events[clock]
        assert (kind, op) == ("A", "IDLE_ONE") and role not in A and 8 in mask
        donor = 0 if role < 18 else 18
        early, late = [k for k in range(J8, clock) if touches(events[k], role)]
        assert events[early] == ["A", "ADD", role, donor, "2"]
        assert events[late] == ["A", "ADD", role, donor, "-2"]
        assert not any(writes(events[k], donor) for k in range(early + 1, late))
        omit.update((clock, early, late))
        hoist.append(clock)
    assert len(hoist) == 14 and len(omit) == 42
    return (
        list(range(J8)) + hoist,
        [k for k in range(J8 + 1, J9) if k not in omit],
        list(range(J9 + 1, len(events))),
    )


def rank(matrix):
    pivots = {}
    for row in matrix:
        row = list(row)
        for column, pivot in sorted(pivots.items()):
            if factor := row[column]:
                row = [a - factor * b for a, b in zip(row, pivot, strict=True)]
        for column, factor in enumerate(row):
            if factor:
                pivots[column] = [a / factor for a in row]
                break
    return len(pivots)


def restrict(matrix, rows, columns):
    return [[matrix[i][j] for j in columns] for i in rows]


def at(row, vector):
    return sum((x * y for x, y in zip(row, vector, strict=True)), Fraction())


def matvec(matrix, vector):
    return [at(row, vector) for row in matrix]


def sparse(vector):
    return {i: str(value) for i, value in enumerate(vector) if value}


def add_gather(matrix, dest, scale, gather):
    result = [row.copy() for row in matrix]
    result[dest] = [x + scale * y for x, y in zip(result[dest], gather, strict=True)]
    return result


def laurent_engine(path):
    engine = runpy.run_path(str(path))
    make_ops = engine["operators"]

    def word(caller, clocks, phase, demote=False):
        gates = []
        for clock in clocks:
            event = caller["events"][clock]
            make_ops.__globals__["FIRST"] = clock
            make_ops.__globals__["SECOND"] = clock
            # The pinned evaluator's endpoint assertion is specific to
            # the pair. Encode a retained QUERY by its literal exponent.
            if event[:2] == ["A", "QUERY"] and clock not in DEMOTED:
                _, _, dest, source, power = event
                gates.append(("ADD", dest, source, Fraction(1), phase * power, engine["ZERO"]))
            else:
                gates.extend(make_ops(caller, phase, demote and clock in DEMOTED))
        return gates

    def vector(gates, vector, undo=False):
        state = [{(0, engine["ZERO"]): value} if value else {} for value in vector]
        result = engine["apply"](gates, state, undo=undo)
        assert all(imag == 0 for component in result for imag, _ in component)
        return [sum(component.values(), Fraction()) for component in result]

    return word, vector


def check_static_gather(prefix, suffix, middle, h8, h9, target, residual, failure, witness):
    # Both required differences refer to the same pre-J8 coordinates.
    assert [at(row, witness) for row in prefix] == [-x for x in identity()[1]]
    assert [residual[19][j] for j in (1, 19)] == [0, 4]
    assert [middle[19][i] for i in A] == [0, 0, -2, 2]
    assert at(failure[0], witness) == 2
    exterior = [j for j in range(N) if j not in A]
    right_gather = [residual[19][j] / 4 if j in exterior else Fraction() for j in range(N)]

    # An explicitly granted right gather fixes the entire corner row but
    # leaves the left witness. A separate left gather can fix that witness.
    from_j8 = multiply(h9, middle)
    right_h8 = add_gather(h8, 18, -2, right_gather)
    right_mid = multiply(from_j8, right_h8)
    assert all(right_mid[19][j] == middle[19][j] + residual[19][j] for j in exterior)
    right_end = multiply(suffix, multiply(right_mid, prefix))
    assert at(difference(target, right_end)[0], witness) == 2
    response = multiply(suffix, from_j8)
    role = next(i for i in A if response[0][i])
    left_h8 = add_gather(h8, role, -2 / response[0][role], identity()[1])
    left_mid = multiply(from_j8, left_h8)
    left_end = multiply(suffix, multiply(left_mid, prefix))
    assert not at(difference(target, left_end)[0], witness)
    assert middle[19][19] + residual[19][19] - left_mid[19][19] == 4
    return {
        "separating_input_at_J8": {"1": "-1"},
        "corner_on_left_and_right": ["0", "4"],
        "transport_row19_on_J8_outputs": ["0", "0", "-2", "2"],
        "forced_right_gather": {j: str(x) for j, x in enumerate(right_gather) if x},
        "right_gather_control": {"corner_row_19_on_exterior": "exact", "remaining_output_0_error": "2"},
        "left_gather_control": {"J8_output_role": role, "output_0_error": "0", "remaining_corner_error": "4"},
        "verdict": "No one static linear gather, even if both hosts may read it",
    }


def enlarged_hosts(column, middle, right_gather, corrupt=False):
    """The one-plus-two read formula at the real negative phase."""
    h = at(right_gather, column)
    ell = sum((-1)**(j - 1) * column[j] for j in (*range(1, 8), *range(9, 18)))
    k = sum((-1)**(j - 19) * column[j] for j in (*range(19, 26), *range(27, 36)))
    c8 = h + column[18]
    x = column.copy()
    x[0] = column[0] - column[8]
    x[18] = column[18] + column[26]
    x[26] = -column[18] + column[26] + 2 * c8
    z = matvec(middle, x)
    r = 2 * column[8] - column[0]
    assert [z[i] for i in B] == [r + column[9], r, 0, -column[27]]
    c9a = -column[0] - 2 * ell + column[9]
    c9b = column[18] + 2 * (h if corrupt else k) - column[27] - r
    result = z.copy()
    result[9], result[0], result[18], result[27] = (
        z[18] + c9a, z[0] - z[9], z[27], z[0] + c9b,
    )
    return x, (c8, c9a, c9b), result


def check_timed_gather(transport, required, inverse_prefix, gather, independent):
    axes = identity()
    u = axes[1]
    v = [a - b for a, b in zip(axes[19], axes[28], strict=True)]
    probes = (u, v)
    assert all(not any(column[i] for i in A) and not at(gather, column) for column in probes)
    transported = [matvec(transport, column) for column in probes]
    assert transported == [u, v]
    assert all(not any(column[i] for i in B) for column in transported)
    responses = [
        [a - b for a, b in zip(matvec(required, x), mx, strict=True)]
        for x, mx in zip(probes, transported, strict=True)
    ]
    assert [sparse(column) for column in responses] == [{9: "-2"}, {27: "4"}]
    for x, mx, dx in zip(probes, transported, responses, strict=True):
        assert independent(x) == (mx, [a + b for a, b in zip(mx, dx, strict=True)])
    minor = [[column[i] for column in responses] for i in (9, 27)]
    determinant = minor[0][0] * minor[1][1] - minor[0][1] * minor[1][0]
    assert determinant == -8
    first_columns = []
    for j, column in enumerate(axes):
        first, _, actual = enlarged_hosts(column, transport, gather)
        first_columns.append(first)
        assert actual == [row[j] for row in required]
    assert enlarged_hosts(v, transport, gather, corrupt=True)[2] == v
    assert enlarged_hosts(v, transport, gather)[2] != v

    # No extra read width can restore information lost at J8 when all
    # subsequent observations are functions of the original port state.
    exterior = [i for i in range(N) if i not in B]
    m_exterior = restrict(transport, exterior, A)
    t_exterior = restrict(required, exterior, A)
    r_m, r_t = rank(m_exterior), rank(t_exterior)
    assert (r_m, r_t) == (3, 2)
    m_rows = [i for i in exterior if any(transport[i][j] for j in A)]
    m_cols = next(js for js in combinations(A, 3) if rank(restrict(transport, m_rows, js)) == 3)
    m_minor_rows = next(rs for rs in combinations(m_rows, 3)
                        if rank(restrict(transport, rs, m_cols)) == 3)
    for j in A:
        independent_m, independent_t = independent(axes[j])
        assert independent_m == [row[j] for row in transport]
        assert independent_t == [row[j] for row in required]
    full_first_rank = rank(first_columns)
    lost = [a - b for a, b in zip(axes[18], axes[26], strict=True)]
    first, side_reads, final = enlarged_hosts(lost, transport, gather)
    assert full_first_rank == 35 and not any(first) and any(final)
    assert side_reads == (1, 0, 1)
    return {
        "pre_J8_probes": [sparse(x) for x in probes],
        "original_caller_probes": [sparse(matvec(inverse_prefix, x)) for x in probes],
        "transport": [sparse(mx) for mx in transported],
        "required_corrections": [sparse(dx) for dx in responses],
        "J9_response_minor": [[str(x) for x in row] for row in minor],
        "J9_response_minor_determinant": str(determinant),
        "one_extra_input_at_each_host": "Excluded even with independent clean values",
        "one_at_J8_two_at_J9": {
            "matched_required_columns": N,
            "scope": "Negative phase and unit bodies only, independently granted reads",
            "wrong_right_aggregate_control": "Second required response lost",
        },
        "no_persistent_side_state": {
            "ranks_on_exterior_J9_outputs_and_hosted_J8_inputs": [r_m, r_t],
            "transport_rank_three_minor": {
                "rows": list(m_minor_rows), "columns": list(m_cols),
                "matrix": [[str(x) for x in row] for row in restrict(transport, m_minor_rows, m_cols)],
            },
            "enlarged_J8_port_rank": full_first_rank,
            "enlarged_J8_lost_input": sparse(lost),
            "enlarged_J8_retained_side_reads": [str(x) for x in side_reads],
            "verdict": "Any admissible first host loses at least one port-state direction",
        },
    }


def check(caller, path):
    events = caller["events"]
    before, middle, after = retiming(events)
    timed = before + [J8] + middle + [J9] + after
    exterior_rows = [i for i in range(N) if i not in B]
    exterior_columns = [j for j in range(N) if j not in A]
    results = {}
    laurent_word, laurent_vector = laurent_engine(path)
    for phase in (1, -1):
        original = rational_word(events, list(range(len(events))), phase)
        assert original == rational_word(events, timed, phase)
        assert original == [[phase * x for x in row] for row in identity()]
        target = [row.copy() for row in original]
        for root in ROOTS:
            target[root][root] = Fraction(1)
        prefix = rational_word(events, before, phase)
        suffix = rational_word(events, after, phase)
        pi = rational_word(events, before, phase, invert=True)
        si = rational_word(events, after, phase, invert=True)
        required = multiply(si, multiply(target, pi))
        transport = rational_word(events, middle, phase, demote=True)
        residual = difference(required, transport)
        old8 = rational_word(events, [J8], phase)
        old9 = rational_word(events, [J9], phase)
        no_adapter = multiply(old9, multiply(transport, old8))
        witness = [Fraction({0: 2, 1: 1}.get(j, 0)) for j in range(N)]
        full_edit = rational_word(events, timed, phase, demote=True)
        failure = difference(target, full_edit)
        old_host8 = rational_word(events, before, phase)
        old_host9 = rational_word(events, before + [J8] + middle, phase, demote=True)
        # Relax all linear host responses; an ingress-only repair can
        # write through the original J8 columns and original J9 rows.
        basis = restrict(transport, exterior_rows, A)
        needs = restrict(residual, exterior_rows, range(N))
        combined = [a + b for a, b in zip(basis, needs, strict=True)]
        assert multiply(
            suffix, multiply(no_adapter, prefix),
        ) == full_edit
        results[phase] = {
            "pinned_input_required_minus_demoted_output_0": str(at(failure[0], witness)),
            "corner_19_19": str(residual[19][19]),
            "corner_rank": rank(restrict(residual, exterior_rows, exterior_columns)),
            "unchanged_J8_egress_rank_outside_J9": rank(basis),
            "rank_after_adding_required_exterior_columns": rank(combined),
        }
        if phase == -1:
            assert not any(at(old_host8[i], witness) for i in A)
            assert not any(at(old_host9[i], witness) for i in B)
            assert results[phase]["corner_rank"] == 1
            results[phase]["static_gather"] = check_static_gather(
                prefix, suffix, transport, old8, old9, target, residual, failure, witness,
            )
            assert laurent_vector(laurent_word(caller, before, 2), witness) == [
                at(row, witness) for row in prefix
            ]
            assert laurent_vector(laurent_word(caller, timed, 2, demote=True), witness) == [
                at(row, witness) for row in full_edit
            ]
            p, m, s = (laurent_word(caller, clocks, 2, demote=True)
                       for clocks in (before, middle, after))

            def independent(vector):
                u = laurent_vector(p, vector, undo=True)
                u = [value if i in ROOTS else -value for i, value in enumerate(u)]
                return laurent_vector(m, vector), laurent_vector(s, u, undo=True)

            for j in (1, 19):
                v, t = independent(identity()[j])
                assert [x - y for x, y in zip(t, v, strict=True)] == [row[j] for row in residual]
            results[phase]["independent_laurent_checks"] = [
                "forward old-skeleton witness", "stripped corner columns 1 and 19",
                "both timed probes and all four hosted J8 columns",
            ]
            g = results[phase]["static_gather"]["forced_right_gather"]
            gather = [Fraction(g.get(j, 0)) for j in range(N)]
            results[phase]["timed_gather"] = check_timed_gather(transport, required, pi, gather, independent)
    return results


def main():
    assert __debug__
    path = Path(sys.argv[1])
    for file, digest in SOURCES.items():
        assert sha256((path / file).read_bytes()).hexdigest() == digest, file
    caller = json.loads((path / "inputs/CALLER.json").read_bytes())
    print(json.dumps(check(caller, path / "inputs/full_body.py"), indent=2))


if __name__ == "__main__":
    main()
