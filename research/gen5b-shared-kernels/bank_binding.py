"""Exact shared-stock binding between role-level allocation and priced inventory."""
from fractions import Fraction as F


def check(banks, pricing, replicas=60, stages=5, width=120):
    assert replicas == 60 and stages == 5 and width == 120
    counts = {int(r): n for r, n in banks['family_counts'].items()}
    demand = {int(r): n for r, n in pricing['packing']['demand'].items()}
    assert demand == {r: replicas*n for r, n in counts.items()}
    assert sum(counts.values()) == banks['helper_roles'] == 15427
    rank = sum(r*n for r, n in counts.items())
    assert rank == banks['residual_rank_per_replica']
    assert width*banks['banks_per_stage'] == replicas*rank
    assert banks['banks_per_stage'] == pricing['packing']['feasible_bins']
    assert banks['total_banks'] == stages*banks['banks_per_stage']
    assert banks['literal_data_stock'] == 422400
    assert banks['literal_stock'] == banks['literal_data_stock'] + banks['total_banks']
    assert banks['literal_stock'] == pricing['literal_stock']
    assert F(banks['unreplicated_stock']) == F(pricing['unreplicated_stock']) == F(banks['literal_stock'], replicas)
    assert banks['checked_role_replica_assignments_per_stage'] == replicas*banks['helper_roles']
    assert banks['total_stage_assignments'] == stages*banks['checked_role_replica_assignments_per_stage']
    assert width*banks['literal_stock'] - replicas*pricing['rank_mass'] == replicas*F(pricing['deficit'])
    assert banks['all_banks_full'] and banks['stages_have_disjoint_bank_namespaces']
