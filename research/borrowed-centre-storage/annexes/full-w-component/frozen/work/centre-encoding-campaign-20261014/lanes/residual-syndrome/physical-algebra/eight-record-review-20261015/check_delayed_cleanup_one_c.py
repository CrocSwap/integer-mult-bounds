"""Check the delayed cleanup with the existing one-array owned scratch.

Do not change the zero-work cleanup word. Keep all borrowed inputs.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location('local_cleanup', HERE / 'check_delayed_cleanup.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    m = old.load_engine()
    certificate = json.loads(gzip.decompress(m.pinned(
        m.BASE / 'base/research/joint-query/certificate.json.gz',
        'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7')))
    programs = json.loads(m.pinned(m.INPUT / 'eight-records/EIGHT-RECORD-WORDS.json',
                                   '8dcb0f29d2b0275e5d5395511d10451b8675c9ffe37ebdbd452c0132a17b15f4'))
    r = [[Fraction(row.get(str(p), 0)) for p in m.ALL] for row in certificate['R_rows']]
    routes = m.parse_routes(certificate)
    _, _, query, correction = old.build(m, programs, r, routes)
    full2 = tuple((v, 1) for v in m.AXES[:25])

    def alias(sign):
        word = [dict(op='add', dst='Y' + str(p), src='X' + str(p), c=str(sign)) for p in m.U + m.T]
        word.append(dict(op='private_begin'))
        for k in range(8):
            word.append(dict(op='clear', field='C', frame='common_F_U2'))
            for p in m.ALL:
                if r[k][p]:
                    word.append(dict(op='add', dst='C', src='X' + str(p), c=str(r[k][p])))
            for p in m.U + m.T:
                if r[k][p]:
                    word.append(dict(op='add', dst='Y' + str(p), src='C', c=str(-sign * r[k][p] / 4)))
        word += [dict(op='clear', field='C', frame='identity'), dict(op='private_end')]
        return word

    def run(events, rows, frames):
        counts = Counter()
        private = False
        for event in events:
            op = event['op']
            if op == 'add':
                dst, src = event['dst'], event['src']
                m.require(m.phase(frames[dst]) == m.phase(frames[src]) or not rows[src],
                          'An ADD uses one actual common frame')
                rows[dst] = m.plus(rows[dst], rows[src], Fraction(event['c']))
                counts['physical_ADD_checks'] += 1
            elif op == 'map':
                m.require(not private, 'Complete map before or after the private sweep')
                stage, p = event['letter']
                g, shift, _ = routes[stage, p]
                m.require(tuple(event['g']) == g and event['shift'] in (shift, m.act(g, shift)),
                          'An actual stage2 view')
                field = event['field']
                rows[field] = m.route(rows[field], stage, p)
                frames[field] = m.transport(frames[field], g, event['shift'])
                counts['physical_map_checks'] += 1
            elif op == 'clear':
                m.require(private and event['field'] == 'C', 'Clear only the owned local scratch')
                rows['C'] = {}
                frames['C'] = full2 if event['frame'] == 'common_F_U2' else ()
            elif op == 'private_begin':
                m.require(not private, 'One owner body at a time')
                private = True
            elif op == 'private_end':
                m.require(private and not rows['C'] and m.phase(frames['C']) == m.phase(()),
                          'Scratch is zero/identity before the next owner')
                private = False
            else:
                raise ValueError('Unexpected cleanup event: ' + op)
        m.require(not private, 'Complete private sweep')
        return counts

    forward, backward = alias(1), alias(-1)
    word = forward + query + backward + correction
    _, initial = m.case(programs['dirty_eight_A_before_cleanup'], r, routes, True)
    rows = {field: value.copy() for field, value in initial.items()}
    # Allow a new arbitrary scratch input at the cleanup cut.
    rows['C'] = m.symbol(232)
    frames = {field: (full2 if field[0] in ('X', 'Y', 'R') else ()) for field in rows}
    checks = run(word, rows, frames)
    for p in m.ALL:
        m.require(rows['X' + str(p)] == m.symbol(p), 'Every original X input restored')
        m.require(rows['Y' + str(p)] == m.symbol(112 + p), 'Every original Y input restored')
    for at, p in enumerate(m.A):
        m.require(rows['R' + str(p)] == m.symbol(224 + at), 'Every arbitrary donor restored')
    m.require(not rows['C'], 'Owned scratch ends at zero')
    m.require(all(rows[field] == value for field, value in initial.items() if field.startswith('H')),
              'All 480 borrowed helpers are unchanged')
    for field in rows:
        if field[0] in ('X', 'Y', 'R'):
            m.require(m.phase(frames[field]) == m.phase(full2), 'Common F_U2 endpoint')
    # The alias is checked separately on arbitrary data.
    bare = {'X' + str(p): m.symbol(p) for p in m.ALL}
    bare.update({'Y' + str(p): m.symbol(112 + p) for p in m.ALL})
    bare['C'] = m.symbol(232)
    bare_frames = {field: full2 for field in bare}
    run(forward, bare, bare_frames)
    f = m.read_query({p: m.symbol(p) for p in m.ALL}, m.ALL, 0, r)
    pf = m.response(f, m.U + m.T, 0, r)
    for p in m.U + m.T:
        want = m.plus(m.plus(m.symbol(112 + p), m.symbol(p)), pf[p], -1)
        m.require(bare['Y' + str(p)] == want, 'The actual Y1 off-A alias')
    run(backward, bare, bare_frames)
    m.require(all(bare['X' + str(p)] == m.symbol(p) and bare['Y' + str(p)] == m.symbol(112 + p)
                  for p in m.ALL), 'The alias shear restores every data column')
    bill = m.invoice(word)
    m.require(bill['scalar_allowance'] == 23780 and bill['native_mass'] == 0
              and bill['cover_maps'] == 224, 'One-C cleanup invoice')
    m.require(m.invoice(forward)['scalar_allowance'] == 9426, 'Each alias direction invoice')
    controls = {}
    bad = {field: value.copy() for field, value in initial.items()}
    run(forward + query + backward, bad, {field: full2 for field in bad})
    controls['omitting_E_correction_changes_data'] = any(bad['X' + str(p)] != m.symbol(p) for p in m.ALL)
    m.require(controls['omitting_E_correction_changes_data'], 'Dirty baseline remains a real obligation')
    bad_frames = {field: (m.FULL if field.startswith('R') else full2) for field in initial}
    try:
        run(word, {field: value.copy() for field, value in initial.items()}, bad_frames)
    except ValueError as error:
        controls['missing_second_record_advance'] = str(error)
    m.require('missing_second_record_advance' in controls, 'The required donor advance is checked')
    packet = {'contract': 'common F_U2 with aligned arbitrary donors; one reused owned C',
              'alias_shear': forward, 'current_stage2_query': query, 'inverse_alias_shear': backward,
              'selected_error_correction': correction, 'cleanup': word}
    payload = HERE / 'DELAYED-CLEANUP-ONE-C-WORD.json'
    payload.write_text(json.dumps(packet, sort_keys=True, separators=(',', ':')) + '\n')
    result = {'status': 'PASS_CONDITIONAL_ONE_C_DELAYED_CLEANUP', 'source_pins': m.PINS,
              'word_sha256': sha256(payload.read_bytes()).hexdigest(), 'invoice': bill,
              'source_algebra_sha256': old.ENGINE_PIN,
              'data_columns': 224, 'arbitrary_donor_columns': 8, 'arbitrary_owned_scratch_columns': 1,
              'unchanged_helper_columns': 480, 'physical_checks': dict(checks),
              'one_C_reused_from_local_repair': True, 'additional_owned_work_fields': 0,
              'negative_controls': controls,
              'scalar_parts': {'each_alias_direction': 9426, 'stage2_query': 4160, 'E_correction': 768},
              'premises': ['Park the full coded pair through F2, then reach common F_U2',
                          'Align each donor at both repair and cleanup by its separately priced two-cut views',
                          'No donor active use or untracked data change before cleanup'],
              'excluded': ['Donor allocation', 'Boundary view cost', 'Stream invoice',
                           'Rounding and recursive precision', 'Complete supplier']}
    output = HERE / 'DELAYED-CLEANUP-ONE-C.json'
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])
    print(sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
