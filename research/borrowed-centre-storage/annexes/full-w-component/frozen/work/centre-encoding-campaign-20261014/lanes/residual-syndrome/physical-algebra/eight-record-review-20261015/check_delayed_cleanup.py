"""Emit a conditional common-F25 cleanup for eight dirty A records.

Use the independent local review algebra. Do not import a producer module.
The separate owner condition must match both native intervals.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ENGINE = HERE / 'review_eight_records.py'
ENGINE_PIN = '51cb8354f817ca877583b6982bb553a7472ac21a34bfa0cf90f701b3bdc491d4'


def load_engine():
    if sha256(ENGINE.read_bytes()).hexdigest() != ENGINE_PIN:
        raise ValueError('Independent algebra pin')
    spec = importlib.util.spec_from_file_location('independent_eight_record_algebra', ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inverse(word):
    answer = []
    for event in reversed(word):
        result = dict(event)
        coefficient = Fraction(event['c'])
        if event['op'] == 'add':
            result['c'] = str(-coefficient)
        elif event['op'] == 'scale':
            result['c'] = str(1 / coefficient)
        else:
            raise ValueError('The scalar content word has an unsupported event')
        answer.append(result)
    return answer


def build(m, programs, r, routes):
    retained = programs['owned_eight_A']['repair']
    end = len(retained) - len(m.A + m.T)
    start = end
    while start:
        event = retained[start - 1]
        fields = [event[key] for key in ('field', 'src', 'dst') if key in event]
        if event['op'] not in ('add', 'scale') or not all(f.startswith('X') for f in fields):
            break
        start -= 1
    source_inverse = retained[start:end]
    m.require(start == 1459 and end == 2429, 'The pinned F0 source inverse slice')
    f0 = [dict(op='add', dst='Y' + str(p), src='X' + str(p), c='1') for p in m.A + m.T]
    f0 += inverse(source_inverse)
    f0 += [dict(op='add', dst='Y' + str(p), src='X' + str(p), c='1') for p in m.U]
    f0 += [dict(op='add', dst='Y' + str(p), src='X' + str(p), c='-1') for p in m.A + m.T]
    query = []
    for prefix, ports in (('Y', m.U + m.T), ('R', m.A)):
        for p in ports:
            g, shift, _ = routes[2, p]
            query.append(dict(op='map', field=prefix + str(p), letter=[2, p],
                              g=list(g), shift=shift))
    for a in m.A:
        for p in m.U + m.T:
            c = -sum(r[k][a] * r[k][p] for k in range(8)) / 4
            if c:
                query.append(dict(op='add', dst='R' + str(a), src='Y' + str(p), c=str(c)))
    for prefix, ports in (('R', m.A), ('Y', m.U + m.T)):
        for p in ports:
            g, shift, _ = routes[2, p]
            query.append(dict(op='map', field=prefix + str(p), letter=[2, p],
                              g=list(g), shift=m.act(g, shift)))
    correction = []
    for a in m.A:
        correction += [dict(op='add', dst='X' + str(a), src='R' + str(a), c='1'),
                       dict(op='add', dst='Y' + str(a), src='R' + str(a), c='-1')]
    for t in m.T:
        for a in m.A:
            c = sum(r[k][t] * r[k][a] for k in range(8)) / 4
            if c:
                correction += [dict(op='add', dst='X' + str(t), src='R' + str(a), c=str(-c)),
                               dict(op='add', dst='Y' + str(t), src='R' + str(a), c=str(c))]
    return source_inverse, f0, query, correction


def main():
    m = load_engine()
    import gzip
    certificate = json.loads(gzip.decompress(m.pinned(
        m.BASE / 'base/research/joint-query/certificate.json.gz',
        'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7')))
    programs = json.loads(m.pinned(m.INPUT / 'eight-records/EIGHT-RECORD-WORDS.json',
                                   '8dcb0f29d2b0275e5d5395511d10451b8675c9ffe37ebdbd452c0132a17b15f4'))
    r = [[Fraction(row.get(str(p), 0)) for p in m.ALL] for row in certificate['R_rows']]
    routes = m.parse_routes(certificate)
    sinv, f0, query, correction = build(m, programs, r, routes)
    cleanup = f0 + query + inverse(f0) + correction
    _, start_rows = m.case(programs['dirty_eight_A_before_cleanup'], r, routes, True)
    full2 = tuple((v, 1) for v in m.AXES[:25])
    frames = {field: (full2 if field[0] in ('X', 'Y', 'R') else ()) for field in start_rows}
    rows = {field: value.copy() for field, value in start_rows.items()}
    counters = Counter()
    m.execute(cleanup, rows, frames, routes, True, counters)
    for p in m.ALL:
        m.require(rows['X' + str(p)] == m.symbol(p), 'All final X columns')
        m.require(rows['Y' + str(p)] == m.symbol(112 + p), 'All final Y columns')
    for at, p in enumerate(m.A):
        m.require(rows['R' + str(p)] == m.symbol(224 + at), 'All original donor columns restored')
    for field in rows:
        if field[0] in ('X', 'Y', 'R'):
            m.require(m.phase(frames[field]) == m.phase(full2), 'Complete common-F25 endpoint')
        else:
            m.require(rows[field] == start_rows[field], 'No scratch or helper use')
    # Check the scalar source code without any dirty-state restriction.
    ordinary = {'X' + str(p): m.symbol(p) for p in m.ALL}
    ordinary.update({'Y' + str(p): m.symbol(112 + p) for p in m.ALL})
    fframes = {field: full2 for field in ordinary}
    m.execute(f0, ordinary, fframes, routes, True, Counter())
    expected_x, expected_y = m.source_forward(
        {p: m.symbol(p) for p in m.ALL}, {p: m.symbol(112 + p) for p in m.ALL}, r)
    m.require(all(ordinary['X' + str(p)] == expected_x[p] and ordinary['Y' + str(p)] == expected_y[p]
                  for p in m.ALL), 'Literal scalar F0 content on all 224 arbitrary columns')
    # The query must be the actual future row. It is unchanged by E h.
    query_support = Counter(e['c'] for e in query if e['op'] == 'add')
    m.require(sum(query_support.values()) == 416, 'Actual N2 support')
    bill = m.invoice(cleanup)
    m.require(bill['scalar_allowance'] == 25152 and bill['cover_maps'] == 224,
              'Exact delayed-cleanup invoice')
    m.require(bill['native_mass'] == 0 and 'clear' not in bill['event_counts'],
              'No native child, owned CLEAR, or discarded input')
    bad_frames = {field: (m.FULL if field.startswith('R') else full2) for field in start_rows}
    controls = {}
    try:
        m.execute(cleanup, {field: value.copy() for field, value in start_rows.items()},
                  bad_frames, routes, True, Counter())
    except ValueError as error:
        controls['unadvanced_donor_is_rejected'] = str(error)
    m.require('unadvanced_donor_is_rejected' in controls, 'The second donor advance is needed')
    short = f0 + query + inverse(f0)
    bad_rows = {field: value.copy() for field, value in start_rows.items()}
    m.execute(short, bad_rows, {field: full2 for field in bad_rows}, routes, True, Counter())
    controls['omitted_baseline_data_correction_is_not_identity'] = any(
        bad_rows['X' + str(p)] != m.symbol(p) for p in m.ALL)
    m.require(controls['omitted_baseline_data_correction_is_not_identity'], 'Baseline debt is real')
    literal = {'contract': 'common F_U2; aligned arbitrary donors; exact parked data z+E h',
               'scalar_F0_content': f0, 'current_stage2_query': query,
               'inverse_scalar_F0_content': inverse(f0), 'data_error_correction': correction,
               'cleanup': cleanup}
    word_path = HERE / 'DELAYED-CLEANUP-WORD.json'
    word_path.write_text(json.dumps(literal, sort_keys=True, separators=(',', ':')) + '\n')
    result = {'status': 'PASS_CONDITIONAL_DELAYED_DIRTY_A_CLEANUP', 'source_pins': m.PINS,
              'independent_local_engine_sha256': ENGINE_PIN,
              'cleanup_word_sha256': sha256(word_path.read_bytes()).hexdigest(),
              'invoice': bill, 'checks': dict(counters), 'query_coefficients': dict(query_support),
              'scalar_parts': {'source_code_inverse': m.invoice(sinv)['scalar_allowance'],
                               'each_F0_content_direction': m.invoice(f0)['scalar_allowance'],
                               'N2_read': m.invoice(query)['scalar_allowance'],
                               'selected_error_correction': m.invoice(correction)['scalar_allowance']},
              'data_columns': 224, 'arbitrary_donor_columns': 8, 'unchanged_helper_columns': 480,
              'additional_owned_work_fields': 0, 'negative_controls': controls,
              'premises': ['Park the entire coded pair through F2 and advance it to common F_U2',
                          'A consistent donor view matches F_E1 by repair and then F_E2 by cleanup',
                          'No active donor use before cleanup; whole arbitrary-input helper jobs are allowed'],
              'excluded': ['A two-cut donor allocation', 'Donor boundary view cost',
                           'Complete stream cost', 'Rounding and recursive precision', 'Supplier claim']}
    output = HERE / 'DELAYED-CLEANUP.json'
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])
    print(sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
