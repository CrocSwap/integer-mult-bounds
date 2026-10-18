"""Reprice finite tensor dilations of the pinned selected complex supplier.

The finite formula follows the retained PR558 -> PR552 -> PR531 invoice
and the selected PR1094 complete bill. Source notices remain in the pinned
archives. New code uses Apache-2.0 and OpenAI Codex assistance.
"""

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import sys
import importlib.util
import tempfile
import json


PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import sources


def require(value, message):
    if not value:
        raise ValueError(message)


def engine(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoice(old, owners, factor, retarget):
    m = 73 * factor
    compiler = 64 * (m + 1) ** 3
    providers = {}
    for name, row in old['providers'].items():
        macros = max(v['macros'] for v in row['local'].values())
        adapters = 16 * (macros + row['children'] + row['n'] + row['centres']) + 64 * m
        extra = 4 * row['n'] if retarget else 0
        adapters += extra
        primitive = max(v['real_component_primitives'] for v in row['local'].values())
        primitive += adapters * compiler
        providers[name] = dict(adapters=adapters, primitive_bound=primitive,
                               added_boundary_maps=extra)
    adapters = max(v['adapters'] for v in providers.values())
    primitive = max(v['primitive_bound'] for v in providers.values())
    require(old['wrapper_elementary_factors_charged'] % old['factors_per_wrapper'] == 0,
            'The source wrapper count is not integral.')
    wrappers = old['wrapper_elementary_factors_charged'] // old['factors_per_wrapper']
    wrapper_factors = wrappers * 2 * (m - 1)
    parent_live, parent_physical, parent_idle = 23408, 23922, 32256
    banks = (parent_live - 2 * 112 * 4 * 16) // 9
    bridges, shifts = 2 * 112 * 144, 4 * 112 * 16
    moves = 2 * shifts
    items = (4 * 112 * 16 * 9 + 2 * 112 * 16 * 9 + 2 * 144 * old['helpers']
             + parent_idle + 9 * banks + bridges + shifts + moves + parent_live
             + parent_physical + wrapper_factors)
    outside = 8 * items + 64 * m
    extra_global = 4 * old['physical'] if retarget else 0
    outside += extra_global
    fresh = (old['selected_real_component_primitives'] + bridges + shifts + moves
             + parent_live + (144 * adapters + outside) * compiler + 64 * parent_physical)
    rebased = fresh + 65 * (old['physical'] - parent_physical) + old['live'] - parent_live
    prior = old['retained_prior_overcharge']['previous_pervertex_allowance']
    used = max(fresh, rebased, prior + fresh)
    group = 2 ** (36 * 36)
    for i in range(1, 37):
        group *= 2 ** (2 * i) - 1
    stock = group * old['physical']
    mass = factor * owners['rank_mass']
    streamed = group * mass
    logical = group * used + 64
    router = compiler * (logical + 1) * (stock + 1) ** 2
    total_mass = streamed + 2 ** 100000
    literal = 2 * 2 ** 30000 * stock ** 2 + 8 * streamed + 4 * stock + 4 + 32 * m
    payload = 512
    row_coefficient = 2 * stock.bit_length() + 9909 + 252 + 2 * payload
    localbits = max(v['prefix_bits'] for p in old['providers'].values()
                    for v in p['local'].values())
    prefix = localbits + (m + 1) // 2 + 144 + 144 + 4
    histogram = {factor * int(r): n for r, n in owners['paid_profile'].items()}
    maxchild = max(histogram)
    checks = dict(local_primitive_bound=primitive < 2 ** 48,
                  logical=logical < 2 ** 6050,
                  router=router < 2 ** 30000,
                  literal=literal < 2 ** 100000,
                  mass=total_mass < 2 ** 100001,
                  precision=32 * m * total_mass ** 2 < 2 ** 210000,
                  tape=2 * total_mass + 18 < 2 ** 210000,
                  row=row_coefficient < 20161,
                  halving=m * m > 2 * maxchild * maxchild,
                  prefix=prefix < payload)
    report = dict(factor=factor, dimension=m, live=old['live'], physical=old['physical'],
                  diagonal_cover_order_bits=group.bit_length(), physical_stock_bits=stock.bit_length(),
                  profile=dict(sorted(histogram.items())), rank_mass=mass,
                  rank_deficit=m * old['live'] - mass,
                  maximum_child=maxchild, halving_margin=m * m - 2 * maxchild * maxchild,
                  compiler=compiler, providers=providers, local_adapters=adapters,
                  local_primitive_bound=primitive, local_primitive_bound_bits=primitive.bit_length(),
                  wrappers=wrappers, factors_per_wrapper=2 * (m - 1),
                  wrapper_elementary_factors_charged=wrapper_factors,
                  added_global_boundary_maps=extra_global,
                  unhosted_pervertex=fresh, hosted_rebased_pervertex=rebased,
                  conservative_pervertex_used=used, logical_bits=logical.bit_length(),
                  router_bits=router.bit_length(), literal_bits=literal.bit_length(),
                  required_C0_bits=(32 * m * total_mass ** 2).bit_length(),
                  local_scalar_prefix_bits=localbits, input_l2_bits=(m + 1) // 2,
                  global_prefix_bits=prefix, charged_prefix_bits=payload,
                  physical_row_coefficient=row_coefficient, retained_row_coefficient=20161,
                  strict_checks=checks)
    return report, histogram


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=PACKAGE.parents[1])
    parser.add_argument('--out', type=Path, default=PACKAGE / 'evidence')
    args = parser.parse_args()
    require(__debug__, 'Run with source assertions enabled; do not use -O.')
    args.out.mkdir(parents=True, exist_ok=True)
    source_hashes = dict(sources.INVOICE_MEMBERS)
    source_hashes.update({sources.ENGINE_ROOT + name: pin
                          for name, pin in sources.ENGINE_PINS.items()})
    old, owners = sources.load_invoice(args.repo)
    require((old['live'], old['physical'], old['helpers'], old['centres']) ==
            (14336, 14826, 480, 8), 'The selected source inventory changed.')
    require(old['template_sha256'] == owners['template_sha256'], 'The source template pins differ.')
    require(owners['rank_mass'] == sum(int(r) * n for r, n in owners['paid_profile'].items()),
            'The source profile mass is wrong.')
    baseline, old_profile = invoice(old, owners, 1, False)
    for name in ('compiler', 'local_adapters', 'local_primitive_bound', 'unhosted_pervertex',
                 'hosted_rebased_pervertex', 'conservative_pervertex_used', 'global_prefix_bits'):
        require(baseline[name] == old[name], 'The source invoice did not reproduce: ' + name)
    for name in ('physical_stock_bits', 'router_bits', 'literal_bits',
                 'physical_row_coefficient', 'required_C0_bits'):
        require(baseline[name] == old['finite'][name], 'The source finite bound did not reproduce: ' + name)
    require(all(baseline['strict_checks'].values()), 'The selected source controls failed.')

    with tempfile.TemporaryDirectory(prefix='involutive-walsh-moments-') as folder:
        engine_dir = Path(folder)
        for name in sources.ENGINE_PINS:
            (engine_dir / name).write_bytes(sources.engine_bytes(args.repo, name))
        mercator = engine(engine_dir / 'moment.py', 'dilation_mercator')
        binary = engine(engine_dir / 'base_two_moment.py', 'dilation_binary')
        accepted = Fraction(67018507072324140917, 40000000000000000000000)
        endpoints = [accepted, accepted + Fraction(1, 10 ** 24)]
        reference = []
        for point in endpoints:
            first = mercator.moment(old_profile, 73, old['live'], point, False)
            second = binary.moment(73, old['live'], list(old_profile.items()), point)
            reference.append((first, second))
        require(reference[0][0][1] < 1 and reference[0][1][1] < 1,
                'The selected complex endpoint did not pass both exact engines.')
        require(reference[1][0][0] > 1 and reference[1][1][0] > 1,
                'The next complex endpoint did not reject in both exact engines.')
        rows = []
        for factor in (2, 4):
            row, histogram = invoice(old, owners, factor, True)
            require(row['rank_deficit'] == factor * baseline['rank_deficit'], 'Rank deficit scaling failed.')
            require(row['halving_margin'] == factor ** 2 * baseline['halving_margin'],
                    'The proper-child margin scaling failed.')
            for rank, count in old_profile.items():
                require(Fraction(factor * rank, factor * 73) == Fraction(rank, 73),
                        'A normalized child rank changed.')
                require(histogram[factor * rank] == count, 'A child multiplicity changed.')
            moments = []
            for index, point in enumerate(endpoints):
                first = mercator.moment(histogram, 73 * factor, old['live'], point, False)
                second = binary.moment(73 * factor, old['live'], list(histogram.items()), point)
                require((first, second) == reference[index], 'A dilated interval moment changed.')
                moments.append(dict(exponent=str(point), mercator=[str(v) for v in first],
                                    binary=[str(v) for v in second]))
            row['exact_moments'] = moments
            if factor == 2:
                require(all(row['strict_checks'].values()), 'The doubled finite invoice failed.')
            else:
                require([k for k, ok in row['strict_checks'].items() if not ok] == ['local_primitive_bound'],
                        'The fourfold diagnostic has a different guard result.')
                require(row['local_primitive_bound'] < 2 ** 50, 'The fourfold local reserve is too small.')
            rows.append(row)
        result = dict(status='PASS_EXACT_TWOFOLD_DILATION_INVOICE_AND_MOMENT_TRANSFER',
                      source_base=sources.BASE,
                      selected_archive_sha256=sources.SELECTED_ARCHIVE_SHA256,
                      source_sha256=source_hashes,
                      checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                      selected_invoice_reproduced=True,
                      old_native_rank_profile=owners['paid_profile'],
                      old_rank_deficit=baseline['rank_deficit'],
                      old_halving_margin=baseline['halving_margin'],
                      dilations=rows,
                      overhead_scope='Same scalar word; generic monomial compiler, four extra boundary maps per local register and per physical family.',
                      not_claimed=['A closed centre controller or modified-word cost',
                                   'A complete emitted dilated supplier certificate',
                                   'A new kappa bound or discharge of inherited all-size assumptions'])
        (args.out / 'DILATION-INVOICE.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print(result['status'])
        print(json.dumps([dict(factor=r['factor'], dimension=r['dimension'],
                               prefix=r['global_prefix_bits'], local_bits=r['local_primitive_bound_bits'],
                               row=r['physical_row_coefficient'], checks=r['strict_checks']) for r in rows], sort_keys=True))


if __name__ == '__main__':
    main()
