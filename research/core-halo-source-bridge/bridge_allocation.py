"""Exact source-contract allocation for the native Core / first-face seam.

No numerical callee is simulated here. Written proofs bind these inequalities
to the actual source programs. Prepared for @CubeJerry, OpenAI assistance,
Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction as Q


def require(ok, message):
    if not ok:
        raise ValueError(message)


def power2(exponent):
    require(type(exponent) is int, "integer dyadic exponent")
    return Q(1 << exponent) if exponent >= 0 else Q(1, 1 << -exponent)


@dataclass(frozen=True)
class Axis:
    coordinate_bits: int
    bandwidth: int
    terms: int
    gap: Q
    normalizer_bits: int

    def __post_init__(self):
        ints = (self.coordinate_bits, self.bandwidth, self.terms, self.normalizer_bits)
        require(all(type(x) is int for x in ints), "integer axis fields")
        require(type(self.gap) in (int, Q), "exact rational source gap")
        require(self.coordinate_bits > 0 and 0 <= self.bandwidth < (1 << (self.coordinate_bits - 1)),
                "unique cyclic band offsets")
        require(self.terms >= 1 and self.normalizer_bits >= 0 and 0 < self.gap <= 1,
                "positive row-gap/degree and dyadic normalization")
        require(power2(self.normalizer_bits) * self.gap >= 1,
                "normalized exact inverse is a contraction")

    @property
    def halo(self):
        return (self.terms - 1) * self.bandwidth

    @property
    def tail(self):
        return (1 - self.gap) ** self.terms / (power2(self.normalizer_bits) * self.gap)


def allocation(axes, local_bits, boundary, spectator_bits, radius, output_grid,
               core_target):
    require(axes and all(isinstance(a, Axis) for a in axes), "nonempty axis inventory")
    require(all(type(x) is int for x in (local_bits, boundary, spectator_bits,
                                        radius, output_grid, core_target)),
            "integer complete shape and precision")
    require(local_bits >= 1 and spectator_bits >= 0 and radius >= 1,
            "positive common core side and actual input radius")
    require(output_grid >= max(a.normalizer_bits for a in axes) and core_target >= 0,
            "funded halo source shift and Core target")
    side = 1 << local_bits
    halo = max(a.halo for a in axes)
    require(0 <= halo < boundary and side > 4 * boundary,
            "same first-face kept/copy geometry")
    require(all(a.coordinate_bits >= local_bits + 1 for a in axes),
            "at least two complete dyadic cores per active axis")
    require(all((1 << a.coordinate_bits) - side >= a.bandwidth for a in axes),
            "ordinary principal sections at period cut")
    n = spectator_bits + sum(a.coordinate_bits for a in axes)
    u = sum(a.normalizer_bits for a in axes)
    rbits = (radius - 1).bit_length() + (n + 1) // 2
    core_error = power2(-core_target - u)
    rounding = power2(1 - output_grid)
    tail = sum((a.tail for a in axes), Q())
    kept = core_error + rounding + 2 * radius * tail
    halo_error = sum(((2 * a.bandwidth + 1) * radius + 2) * power2(-output_grid) / a.gap
                     + radius * a.tail for a in axes)
    return {
        'field_bits': n,
        'records': 1 << n,
        'core_contexts': 1 << (n - len(axes) * local_bits),
        'source_radius_bits': rbits,
        'normalizer_bits': u,
        'external_component_bits': output_grid + radius.bit_length() + 1,
        'core_component_error_bound': core_error,
        'new_final_rounding_bound': rounding,
        'kept_error_bound': kept,
        'halo_error_bound': halo_error,
        'complete_error_bound': max(kept, halo_error),
        'actual_output_radius_bound': Q(radius) + max(kept, halo_error),
        'next_group_radius': 2 * radius if max(kept, halo_error) <= radius else None,
    }


def core_layout(axes, local_bits, spectator_bits):
    """Retained Layout is low-axis-first; first-face keys are high-axis-first."""
    lengths = tuple(a.coordinate_bits for a in reversed(axes))
    if spectator_bits:
        lengths += (spectator_bits,)
    return {'lengths': lengths, 'selected': tuple(range(len(axes))),
            'local_bits': local_bits}


def match_sources(axes, local_bits, spectator_bits, references, layout, family, archive):
    """Input-independent binding; all exact source/page production stays paid.

    Identity of the actual immutable Reference object is deliberately stronger
    than a matching tag. It prevents independently rounded/transplanted windows.
    The archive must have been made by its pinned original prepare_table path.
    """
    expected = core_layout(axes, local_bits, spectator_bits)
    require(layout.lengths == expected['lengths'] and layout.selected == expected['selected']
            and layout.local_bits == expected['local_bits'], 'same canonical original bit layout')
    require(len(references) == len(axes) == len(archive.plans), 'one actual Reference per halo axis')
    require(len(archive.source_ids) == len(axes), 'complete archive source identities')
    require(len({p.bits for p in archive.plans}) == len({p.radius for p in archive.plans}) == 1,
            'common external data grid and actual-input radius')
    require(len(family) == layout.labels, 'all original coarse contexts')
    for axis, reference, plan, source_id in zip(axes, references, archive.plans, archive.source_ids):
        require(reference.target_size == plan.period == 1 << axis.coordinate_bits,
                'same full original period')
        require(reference.description_hash == source_id, 'halo archive from same original source')
        require(plan.halfwidth == axis.bandwidth and plan.terms == axis.terms
                and plan.gap == axis.gap and plan.normalizer_shift == axis.normalizer_bits,
                'same halo source and normalization parameters')
        require(axis.gap <= reference.narrow_gap, 'certified original global row gap')
        require(axis.bandwidth >= 2 * reference.spec.source_halfwidth + 2,
                'original Reference support covers every nonzero cyclic entry')
    for coarse, row in enumerate(family):
        require(len(row) == len(axes), 'all source axes in every context')
        starts = tuple(reversed(layout.core_starts(coarse)))
        for partition, reference, start in zip(row, references, starts):
            require(partition.reference is reference and partition.kind == 'narrow',
                    'literal same immutable narrow Reference at every Core')
            require(partition.first == start and partition.size == 1 << local_bits,
                    'original ordinary principal section, without rebasing')
            partition.validate()
    return {'field_bits': layout.n, 'contexts': layout.labels, 'axes': len(axes),
            'source_ids': tuple(archive.source_ids), 'normalizer_bits': sum(a.normalizer_bits for a in axes),
            'source_axis_order': 'halo and family high-first; retained dense layout low-first'}
