"""Apply one common internal integer grid to the three matched applications."""

import argparse
import json
from math import lcm, prod
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from compiler import need
from qualify import CALLER_PIN, E40B_APP_PIN, RECIPIENT, check_sources, checked_json


def audit(args):
    check_sources(args.cache, args.package)
    sys.path.insert(0, str(args.cache/'parent'))
    from qualify_complex import historical_checker
    reference = historical_checker(args.cache/'peer')
    sys.path.insert(0, str(args.cache/'source/research/p104-dual-supplier-lift/complex'))
    import supplier

    e40b_path = args.e40b_receipt or args.package/'evidence/application.json'
    guard = checked_json(e40b_path, E40B_APP_PIN, compressed=False)['caller_guard']
    pins = json.loads((HERE / "CLAIM.json").read_bytes())["receipts"]
    names = {"original_7781": "7781.json", "current_7786": "e40b.json", "continued": "application.json"}
    receipts = {tag: checked_json(args.receipts / name, pins[name], compressed=False)
                for tag, name in names.items()}
    need(all(r['caller'] == CALLER_PIN and r['caller_census']['calls'] == 48 for r in receipts.values()),
         'identical ordinary caller bytes and call count')
    physical = supplier.physical
    minima = {tag: r['native']['minimum_product_grid'] for tag, r in receipts.items()}
    common = lcm(*minima.values())
    odd, height = physical.grid_parts(common)
    factors = reference.factor_odd(odd)
    need(prod(factors) == odd and all(0 < f < 2**24 for f in factors), 'short exact common conversions')
    out = {}
    contexts = {}
    for tag, receipt in receipts.items():
        native = receipt['native']
        scale, residue = divmod(common, minima[tag])
        need(residue == 0 and scale > 0, 'scale multiple of exact application grid')
        contexts[tag] = dict(native, path_grid=common, path_grid_odd=odd, path_grid_height=height)
        base_ordinary = receipt['application']['ordinary']
        slots = dict(base_ordinary['raw_scalar_incidence_allowance_before_factor_32'])
        slots['additional_odd_factor_steps'] = (len(factors)-1)*base_ordinary['odd_conversions']
        services = 32 * sum(slots.values())
        out[tag] = dict(word=receipt['word_sha256'], exact_minimum=minima[tag], grid_multiple=scale,
                        conversion_round_trips=supplier.verify_conversions(native['public'], common, factors),
                        ordinary_scalar_slots=slots, ordinary_scalar_services=services,
                        scalar_services_delta=services-base_ordinary['scalar_services'])
    root = physical.root_envelope(contexts, guard)
    for tag, receipt in receipts.items():
        out[tag]['depth_guard'] = physical.check_depth_guard(root, int(receipt['application']['compiler']['H']))
    return dict(status='PASS_SHARED_NATIVE_OPERATIONAL_GRID', common_grid=common, odd_factors=factors,
                common_root=root, native=out,
                closure='Each integral basis donor and separate term prefix scales by the positive integer grid multiple. The common mass and height guard bounds every installed magnitude on the same root tape.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--package', type=Path, default=RECIPIENT)
    parser.add_argument('--e40b-receipt', type=Path)
    parser.add_argument('--receipts', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], result['common_grid'], result['odd_factors'])
