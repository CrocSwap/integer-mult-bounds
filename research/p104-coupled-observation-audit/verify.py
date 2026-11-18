"""Check both exact receiver spaces and all pulse signs. Apache-2.0."""

from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    for pin in pins:
        raw = (ROOT / pin['path']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'], 'source SHA-256')
        require(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'],
                'source Git blob')
    return len(pins)


def sparse(row):
    return [[j, str(value)] for j, value in sorted(row.items()) if value]


def combination(rows, weights):
    result = {}
    for row, coefficient in zip(rows, weights, strict=True):
        for j, value in row.items():
            result[j] = result.get(j, 0) + coefficient * value
    return {j: value for j, value in result.items() if value}


def collect():
    pins = authenticate()
    from audit import construction, determinant, expand, nullspace, snapshot
    import witness

    net, event = snapshot()
    public, first = len(net.initial), net.first_output
    require(public == 1262 and event['type'] == 'grouped_puncture' and event['orientation'] == 0,
            'exact forward group 26')
    lanes = {lane['remove']: lane for lane in event['lanes']}
    pivots = (101324, 99605)
    require([net.moves[k] for k in pivots] == [(117, 834), (117, 837)], 'source pivot routes')
    impulses = [dict((j, F(value)) for j, value in lanes[k]['receive_direction']) for k in pivots]
    sources = [dict((j, F(value)) for j, value in lanes[k]['old_source_form']) for k in pivots]
    require(impulses == [{101324: F(1), 101902: F(1, 2)}, {99605: F(1), 100008: F(1, 2)}],
            'full parallel directions')
    require(sources == [{1149: F(1), 1152: F(-1, 2)}, {1151: F(-1, 2), 1152: F(1, 2)}],
            'actual source equations')
    for pulse, pivot in zip(impulses, pivots, strict=True):
        require(all(net.moves[j] == net.moves[pivot] for j in pulse), 'parallel pulse endpoints')
    charts = (144, 177)
    terminals = (130, 166)
    banks = {chart: sorted([~r for r, value in enumerate(net.initial) if value == chart]
                          + [key for key, (_, value) in net.moves.items() if value == chart])
             for chart in charts}
    require(all(len(row) == 6 for row in banks.values()), 'all local banks')
    receiver_terminals = {first + r for r, chart in enumerate(net.final) if chart in charts}
    targets = set(sum(banks.values(), [])) | receiver_terminals
    rows, stats = expand(net, targets, impulses)
    expected_response = ((F(-1, 2), F(-1, 2)), (F(-1, 2), F(1, 2)))
    output = []
    for index, (chart, terminal) in enumerate(zip(charts, terminals, strict=True)):
        require(net.final[terminal] == chart, 'terminal chart')
        bank_rows = [rows[k] for k in banks[chart]]
        columns = [{j: value for j, value in row.items() if j < public} for row in bank_rows]
        columns += [{j: -value for j, value in row.items()} for row in sources]
        matrix = [[column.get(j, F(0)) for column in columns] for j in range(public)]
        basis, pivot_columns, selected_rows = nullspace(matrix, 8)
        expected = ([F(-1, 2), F(0), F(1, 2), F(0), F(0), F(0), F(1), F(0)] if index == 0
                    else [F(-2), F(0), F(2), F(0), F(0), F(0), F(0), F(1)])
        require(basis == [expected] and len(pivot_columns) == 7, 'complete bank/source intersection')
        minor = [[matrix[r][c] for c in pivot_columns] for r in selected_rows]
        minor_determinant = determinant(minor)
        require(minor_determinant != 0, 'rank-seven determinant')
        require(all(sum(value * coefficient for value, coefficient in zip(row, expected, strict=True)) == 0
                    for row in matrix), 'all-column null relation')
        observed = combination(bank_rows, expected[:6])
        require({j: value for j, value in observed.items() if j < public} == sources[index],
                'explicit source observation')
        pulse = tuple(observed.get(public + j, F(0)) for j in range(2))
        require(pulse == expected_response[index], 'both observation pulse signs')
        affected = {str(key - first): [str(rows[key].get(public + j, F(0))) for j in range(2)]
                    for key in receiver_terminals if net.final[key - first] == chart
                    and any(rows[key].get(public + j) for j in range(2))}
        require(affected == {str(terminal): list(map(str, pulse))}, 'every terminal at the receiver chart')
        repaired = combination([rows[first + terminal], observed], [F(1), F(-1)])
        require(not any(repaired.get(public + j) for j in range(2)), 'both terminal disturbances cancel')
        output.append(dict(chart=chart, terminal=terminal, banks=banks[chart],
                           bank_rows=[sparse(row) for row in bank_rows],
                           source_observation=sparse(sources[index]),
                           bank_coefficients=list(map(str, expected[:6])),
                           complete_nullspace=[list(map(str, expected))],
                           rank_minor=dict(public_rows=selected_rows, columns=pivot_columns,
                                           matrix=[[str(v) for v in row] for row in minor],
                                           determinant=str(minor_determinant)),
                           pulse_response=list(map(str, pulse)), terminal_row=sparse(rows[first + terminal]),
                           affected_terminals=affected))
    response_matrix = [list(row) for row in expected_response]
    require(determinant(response_matrix) == F(-1, 2), 'independent two-pulse corrections')
    faults = []
    for lane, donor in ((0, 101324), (0, 101902), (1, 99605), (1, 100008)):
        altered = deepcopy(impulses)
        altered[lane][donor] *= -1
        changed, _ = expand(net, targets, altered)
        responses = [[str(changed[first + terminal].get(public + j, F(0))) for j in range(2)]
                     for terminal in terminals]
        observations = [combination([changed[k] for k in banks[chart]],
                                    list(map(F, row['bank_coefficients'])))
                        for chart, row in zip(charts, output, strict=True)]
        residuals = [[str(changed[first + terminal].get(public + j, F(0))
                          - observed.get(public + j, F(0))) for j in range(2)]
                     for terminal, observed in zip(terminals, observations, strict=True)]
        require(any(F(value) for row in residuals for value in row), 'wrong pulse sign detected')
        faults.append(dict(pulse=lane, donor=donor, terminal_responses=responses,
                           failed_repair_residuals=residuals))
    for index, chart in enumerate(charts):
        coefficients = list(map(F, output[index]['bank_coefficients']))
        coefficients[2] *= -1
        altered = combination([rows[k] for k in banks[chart]], coefficients)
        require({j: value for j, value in altered.items() if j < public} != sources[index],
                'wrong observation coefficient detected')
    author = witness.coupled_example(net, event)
    expected_author = json.loads((ROOT / 'retained/results/witness.json').read_text())['coupled_example']
    require(author == expected_author, 'unchanged author local routine and receipt')
    for row, reference in zip(output, author['receivers'], strict=True):
        require((row['chart'], row['terminal'], row['pulse_response']) ==
                (reference['chart'], reference['public_terminal'], reference['terminal_response']),
                'separate forward audit agrees with source reverse routine')
    graph = dict(initial=net.initial, final=net.final, moves=sorted(net.moves.items()),
                 forms=[[k, sparse(row)] for k, row in sorted(net.forms.items())], first_output=first)
    pin = sha256(json.dumps(graph, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return dict(schema_version=1, source_files=pins, public_fields=public, edit=26,
                graph_before_edit_sha256=pin, impulse_columns=[sparse(row) for row in impulses],
                required_dag=stats, checked_bank_columns=12 * public,
                checked_pulse_columns=2 * (12 + len(receiver_terminals)),
                receiver_terminal_count=len(receiver_terminals),
                receiver_terminals=[dict(terminal=k - first, chart=net.final[k - first],
                                         pulse=[str(rows[k].get(public + j, F(0))) for j in range(2)])
                                    for k in sorted(receiver_terminals)], receiver_certificates=output,
                response_determinant='-1/2', wrong_pulse_sign_controls=faults,
                wrong_observation_sign_controls=2, source_reverse_routine='PASS')


def main():
    result = collect()
    require(result == json.loads((ROOT / 'RESULT.json').read_text()), 'complete audit certificate')
    print('PASS_P104_COUPLED_OBSERVATION_AUDIT')
    print('1262 public fields; 12 complete bank rows; two rank-seven minors')
    print('chart 144: (-1/2,-1/2); chart 177: (-1/2,1/2); both terminal errors cancel')
    print('four pulse-sign and two observation-sign controls; unchanged local source check passes')


if __name__ == '__main__':
    main()
