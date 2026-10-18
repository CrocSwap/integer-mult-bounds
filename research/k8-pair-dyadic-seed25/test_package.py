"""Semantic rejection controls. Hanson Sun / OpenAI Codex, Apache-2.0."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('pair_verifier', HERE / 'verify.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


def main():
    lib = v.predecessor()
    word, original, _, _ = lib.load()
    programs = json.loads(gzip.decompress((HERE / 'PROGRAMS.json.gz').read_bytes()))
    cert = json.loads((HERE / 'CERTIFICATE.json').read_bytes())
    rejected = []

    def reject(name, operation):
        try:
            operation()
        except (ValueError, KeyError):
            rejected.append(name)
        else:
            raise ValueError('incorrectly accepted control: ' + name)

    forward = programs['forward']
    for index, name in ((1, 'first_entry_omitted'), (2, 'second_entry_omitted'),
                        (-2, 'first_exit_omitted'), (-3, 'second_exit_omitted')):
        bad = copy.deepcopy(forward)
        bad.pop(index)
        reject(name, lambda bad=bad: lib.replay(bad, 'forward'))

    bad = copy.deepcopy(programs['backward'])
    bad[1][1][2:4] = [1, 4]
    reject('backward_boundary_sign_reversed', lambda: lib.replay(bad, 'backward'))

    bad = copy.deepcopy(forward)
    for event in bad:
        if event[0] == 'scalar' and event[1][0] == 'add' and ['L', 251] in event[1][1:3]:
            event[1][3] *= 2
            break
    reject('incident_coefficient_not_conjugated', lambda: lib.replay(bad, 'forward'))
    reject('candidate_digest_changed', lambda: v.need(v.sha(v.canonical(bad)) == cert['orientations']['forward']['candidate_sha256'], 'hash mismatch'))

    reject('data_register_scaled', lambda: lib.transform(original['forward'], word, 12, -2))
    reject('center_carrier_scaled', lambda: lib.transform(original['forward'], word, 224, -2))
    reject('unit_discount_omitted', lambda: v.need(lib.price(lib.Q(1)) == 3, 'unit costs two'))
    price = cert['orientations']['forward']['prices']['copy-init']
    reject('boundary_scales_unpaid', lambda: v.need(price['saving_complex'] == 592, 'eight real boundary shifts paid'))

    pins = json.loads((HERE / 'SOURCES.json').read_bytes())
    badpins = copy.deepcopy(pins)
    del badpins['vendor']['engine.py']
    reject('missing_vendor_pin', lambda: v.predecessor(badpins))
    badpins2 = copy.deepcopy(pins)
    badpins2['vendor']['engine.py'] = '0' * 64
    reject('changed_vendor_pin', lambda: v.predecessor(badpins2))
    baseline_pins = json.loads((HERE / 'vendor/pr1161/SOURCES.json').read_bytes())
    del baseline_pins['files'][next(iter(baseline_pins['files']))]
    reject('missing_original_source_pin', lambda: lib.check_sources(baseline_pins))

    # A shared unit ADD does not equal the sum of two isolated gauge prices.
    # Both registers doubled leaves its coefficient 1. Boundary shifts cost 4.
    shared = [['scalar', ['add', ['L', 251], ['L', 427], 1, 1], 0]]
    small = v.census(lib, shared, [251, 427])
    both_plus_one = small['rows'][0][2][10]
    v.need(both_plus_one == 4, 'shared-edge interaction fixture')
    reject('shared_edge_treated_as_two_independent_edges', lambda: v.need(both_plus_one == 8, 'interaction correction required'))

    # A unit shortcut can beat the lower weighted median: preserve its point dip.
    discount = [['scalar', ['add', ['L', 251], ['L', x], 1, 2], 0] for x in (0, 1)]
    exact = v.exact_census(lib, discount, [251, 427])
    v.need(exact['winner']['exponents'] == [1, 0] and exact['winner']['delta_real'] == -2,
           'nonconvex unit-discount optimum')

    # Changed physical events may leave scalar endpoints untouched, so compare
    # the complete event stream separately instead of accepting map equality.
    bad = copy.deepcopy(forward)
    for event in bad:
        if event[0] == 'climb':
            event[5] += 1
            break
    reject('paid_rank_changed', lambda: v.need(
        [e for e in bad if e[0] != 'scalar'] == [e for e in forward if e[0] != 'scalar'],
        'physical stream mismatch'))
    print(json.dumps({'status': 'PASS_PAIR_REJECTION_CONTROLS', 'rejected': rejected,
                      'positive_fixtures': ['shared_unit_edge', 'unit_discount_off_zero']}, sort_keys=True))


if __name__ == '__main__':
    main()
