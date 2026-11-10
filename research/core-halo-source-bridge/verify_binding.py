"""Actual immutable Reference/partition/layout/halo binding and independent guards."""
from dataclasses import replace
from fractions import Fraction as Q
import json
from types import SimpleNamespace

from bridge_allocation import Axis, allocation, core_layout, match_sources
from bridge_sources import HERE, core_source, load


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    source = core_source()
    controls = []
    with source.numerical() as runtime:
        from admitted_context import AdmittedPartition
        Layout = load('bridge_core_layout', source.COHORT / 'core_layout.py').Layout
        M = load('shrinking_halo_engine', HERE / 'retained/halo/shrinking-reference-halo/engine.py')
        T = load('bridge_binding_tensor', HERE / 'retained/halo/shrinking-reference-halo/tensor.py')
        references = tuple(runtime.reference.Reference(runtime.raw, 15, 1, alpha, 1, 3, 128)
                           for alpha in (2, 3))
        axes = []
        for ref in references:
            gap = min(Q(3, 4), ref.narrow_gap)
            u = 0
            while (1 << u) * gap < 1:
                u += 1
            axes.append(Axis(4, 4, 1, gap, u))
        axes = tuple(axes)
        shape = core_layout(axes, 3, 1)
        layout = Layout(**shape)
        family = []
        for c in range(layout.labels):
            row = []
            for ref, start in zip(references, reversed(layout.core_starts(c))):
                inside = next(i for i in range(8) if ref.source_at.get(start + i) is not None)
                row.append(AdmittedPartition(runtime, ref, 'narrow', start, 8, 1, ((inside,),)))
            family.append(tuple(row))
        bill = M.Bill()
        def tables():
            for axis, ref in zip(axes, references):
                plan = M.Plan(16, axis.bandwidth, 24, axis.terms, axis.normalizer_bits, axis.gap, 1)
                table, _ = M.prepare_table(plan,
                    lambda r, c, ref=ref: Q(r == c) - ref.entry('narrow', r, c).value,
                    ref.description_hash, bill)
                yield table
        archive = T.pack_tables(tables(), bill)
        binding = match_sources(axes, 3, 1, references, layout, family, archive)
        admission = allocation(axes, 3, 1, 1, 1, 24, 20)
        need(admission['next_group_radius'] == 2,
             'the actual source binding has a funded next-group radius')

        # Independent natural-coordinate enumeration. No Layout address routine
        # computes the reference values in this oracle.
        checked = 0
        gather = layout.gather
        for key in range(1 << layout.n):
            spectator = key >> 8
            high = (key >> 4) & 15
            low = key & 15
            packed = key
            for old, new in gather.items():
                packed = (packed & ~(1 << new)) | (((key >> old) & 1) << new)
            c, local = divmod(packed, 64)
            high_local, low_local = divmod(local, 8)
            row = family[c]
            need(row[0].first + high_local == high and row[1].first + low_local == low,
                 'source-axis/original-coordinate mapping differs from natural oracle')
            need((layout.original_base(c) >> 8) == spectator, 'spectator reassignment')
            checked += 1

        def reject(name, thunk):
            try:
                thunk()
            except (ValueError, AssertionError):
                controls.append(name)
            else:
                raise ValueError('adverse binding accepted: ' + name)

        common = (axes, 3, 1, references)
        reject('missing_context', lambda: match_sources(*common, layout, family[:-1], archive))
        swapped = [tuple(reversed(row)) for row in family]
        reject('wrong_source_axis', lambda: match_sources(*common, layout, swapped, archive))
        wrong = list(family); wrong[0] = family[1]
        reject('wrong_original_origin', lambda: match_sources(*common, layout, wrong, archive))
        reject('wrong_dense_axis_order', lambda: match_sources(*common,
            Layout(layout.lengths, (1, 0), 3), family, archive))
        bad_archive = SimpleNamespace(plans=archive.plans, source_ids=archive.source_ids[:-1])
        reject('missing_archive_source', lambda: match_sources(*common, layout, family, bad_archive))
        bad_archive = SimpleNamespace(plans=archive.plans, source_ids=('wrong', archive.source_ids[1]))
        reject('foreign_halo_reference', lambda: match_sources(*common, layout, family, bad_archive))
        bad_archive = SimpleNamespace(plans=(replace(archive.plans[0], normalizer_shift=3), archive.plans[1]),
                                      source_ids=archive.source_ids)
        reject('normalizer_mismatch', lambda: match_sources(*common, layout, family, bad_archive))
        bad_archive = SimpleNamespace(plans=(replace(archive.plans[0], bits=25), archive.plans[1]),
                                      source_ids=archive.source_ids)
        reject('grid_mismatch', lambda: match_sources(*common, layout, family, bad_archive))
        clones = tuple(runtime.reference.Reference(runtime.raw, 15, 1, alpha, 1, 3, 128)
                       for alpha in (2, 3))
        reject('separately_instantiated_reference', lambda: match_sources(axes, 3, 1, clones,
                                                                        layout, family, archive))

        # The omitted whole-field radius and complex component conversion each
        # have exact rational counterexamples, independent of the allocation code.
        norm_squared = Q(1 << layout.n)
        declared_squared = Q(1 << (2 * admission['source_radius_bits']))
        need(norm_squared <= declared_squared and norm_squared > 1,
             'omitted volume negative control')
        controls.append('omitted_whole_field_radius_detected')
        need(Q(3, 10) ** 2 + Q(4, 10) ** 2 == Q(1, 4)
             and Q(3, 10) + Q(4, 10) > Q(1, 2), 'complex norm negative control')
        controls.append('missing_complex_norm_factor_detected')

        # Unequal axes, zero bandwidth, unit gap and large spectator volume are
        # separate exact arithmetic domains. They do not invoke huge source words.
        allocations = 0
        for g in (1, 2, 3):
            for spectator in (0, 1, 9):
                for radius in (1, 2, 3, 7, 8):
                    aa = tuple(Axis(5 + i % 2, i % 2, 2,
                                    Q(1) if i % 2 == 0 else Q(1, 2), i % 2)
                               for i in range(g))
                    a = allocation(aa, 4, 2, spectator, radius, 20, 18)
                    n = spectator + sum(x.coordinate_bits for x in aa)
                    need(radius * radius * (1 << n) <= 1 << (2 * a['source_radius_bits']),
                         'actual global norm funded')
                    need(a['records'] == a['core_contexts'] * 16 ** g, 'full context volume')
                    if all(x.gap == 1 for x in aa):
                        need(a['halo_error_bound'] == sum(((2*x.bandwidth+1)*radius+2)*Q(1,1<<20)/x.gap
                                                        for x in aa), 'zero-tail case')
                    allocations += 1
        receipt = {'status': 'PASS_CORE_HALO_SOURCE_BINDING', 'actual_source_binding': binding,
                   'canonical_coordinates_checked': checked, 'actual_original_partitions': len(family) * len(axes),
                   'exact_allocation_cases': allocations, 'controls': controls,
                   'actual_source_gap': [str(r.narrow_gap) for r in references],
                   'source_archive_preparation': bill.record(),
                   'admission': {k: str(v) if isinstance(v, Q) else v for k,v in admission.items()},
                   'scope': 'actual immutable References, admitted finite partitions and exact original-coordinate binding; no physical Core invocation or production carve claim',
                   'no_new_kappa': True}
        print(json.dumps(receipt, sort_keys=True))
        print('PASS_CORE_HALO_SOURCE_BINDING')


if __name__ == '__main__':
    main()
