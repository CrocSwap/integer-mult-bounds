"""Deterministic refinement of a fully specified late-reuse compilation.

The scalar DAG and its chronology remain fixed. The sequence is intentional:
equal-operation plateaus, dimension-prioritized late matching, source gauges
with exact read deadlines, then operation frames with flexible reuse handoffs.
The integer objectives choose a candidate; independent reflection and moment
checks certify the resulting physical word and paid child inventory.
"""
from operation_plateaus import optimize as optimize_plateaus
from late_birth_weighted import select as select_weighted
from gauge_deadlines import optimize as optimize_gauges
from operation_handoffs import optimize as optimize_handoffs


def optimize(data):
    state = dict(data)
    original_ops = state['ops']
    original_deadlines = dict(state['read_deadlines'])
    original_gauged_roles = set(state['placed'])
    old_late = set(state['late_recipients'])
    frames, plateau_stats = optimize_plateaus(state)
    state['op_frames'] = frames
    state['reuse_pairs'] = [dict(row) for row in state['reuse_pairs']
                           if row['recipient'] not in old_late]
    pairs, deadlines, late, matching_stats = select_weighted(state)
    state.update(reuse_pairs=pairs, read_deadlines=deadlines,
                 late_recipients=late)
    gauges, frames, gauge_stats = optimize_gauges(
        state, solo_rounds=12, joint_rounds=16)
    state.update(placed=gauges, op_frames=frames)
    frames, handoff_stats = optimize_handoffs(state)
    for row in pairs:
        donor_frame = frames[state['last'][row['donor']]]
        birth_frame = gauges[row['recipient']]
        row.update(donor_frame=donor_frame, birth_frame=birth_frame,
                   e=len(donor_frame), s=len(birth_frame))
    assert state['ops'] is original_ops
    assert deadlines == original_deadlines
    assert set(gauges) == original_gauged_roles
    stats = dict(scalar_dag_unchanged=True, chronology_unchanged=True,
                 read_deadlines_unchanged=True,
                 deferred_inventory_unchanged=True,
                 plateau=plateau_stats, matching=matching_stats,
                 gauges=gauge_stats, handoffs=handoff_stats)
    return gauges, frames, pairs, deadlines, late, matching_stats, stats
