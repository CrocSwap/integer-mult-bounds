"""Focused exact setup controls; physical execution is checked separately.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q

def need(condition, message):
    if not condition:
        raise ValueError(message)

def run(producer, reference):
    primary = producer.make_window(reference)
    guard = producer.make_window(reference, block=2)
    need(primary.I == (1, 2, 3, 4) and primary.J == (0, 5, 6, 7)
         and primary.E == (0, 1, 4, 5, 6, 7)
         and primary.j_mask == (1, 0, 0, 1, 1, 1), 'actual current Reference mask')
    need(primary.total_error <= Q(1, 1024) and guard.total_error <= Q(1, 1024),
         'both finite complete complex error certificates')
    need(primary.root_record_radius < 128 and guard.root_record_radius < 128,
         'both finite signed carrier certificates')
    values = tuple(tuple(Q(((i+2)*(j+3)) % 11-5, 16) for j in range(4))
                   for i in range(len(primary.E)))
    need(all(abs(row[j])+abs(row[j+1]) <= 1 for row in values for j in (0, 2)),
         'two admitted complex fixture columns')
    rounded = primary.rounded_action(values)
    exact = primary.exact_action(values)
    observed_error = max(abs(rounded[i][j]-exact[i][j])+abs(rounded[i][j+1]-exact[i][j+1])
                         for i in range(len(values)) for j in (0, 2))
    need(observed_error <= primary.total_error, 'completed four-pass exact-reference error')
    need(all(bit or rounded[i] == values[i] for i, bit in enumerate(primary.j_mask)),
         'E minus J values remain exactly unchanged')
    wrong_j = producer.rounded_solve(primary.f_lower, primary.f_upper,
                                    [values[i] for i, bit in enumerate(primary.j_mask) if bit],
                                    primary.block, primary.P)
    need(wrong_j != tuple(rounded[i] for i, bit in enumerate(primary.j_mask) if bit),
         'omitting the current-input C shear is detected')
    controls = ['omitted C shear']
    cases = ((dict(block=3), 'positive dyadic window geometry and grid', 'non-dyadic block'),
             (dict(precision=8, width=32), 'funded full first-window error', 'underfunded grid'),
             (dict(width=28), 'funded signed scalar record carrier', 'underfunded carrier'),
             (dict(origin=28), 'interior stays inside one original phase cell', 'phase-crossing interior'),
             (dict(interior_blocks=((1, 2), (2, 3))), 'disjoint increasing interiors', 'overlapping interiors'))
    for changes, message, label in cases:
        try:
            producer.make_window(reference, **changes)
        except ValueError as error:
            need(str(error) == message, 'specific source rejection: '+label+': '+str(error))
        else:
            raise ValueError('accepted source mutation: '+label)
        controls.append(label)
    allocation = producer.sufficient_allocation(reference, band=1, radius=Q(3, 2),
                                                target=20, largest_descriptor=reference.target_size)
    funded = producer.make_window(reference, radius=Q(3, 2), target=20,
                                  **{key: value for key, value in allocation.items() if key != 'pbar'})
    need(funded.total_error <= Q(1, 1 << 20), 'universal allocation instantiates exact budget')
    return dict(primary=primary.receipt(), guard=guard.receipt(), controls=controls,
                observed_complex_l1_error=str(observed_error), universal_allocation=allocation,
                exact_source_setup_only=True, physical_prepare_pages_is_separate_required_check=True)
