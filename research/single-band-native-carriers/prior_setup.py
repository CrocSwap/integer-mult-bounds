"""Count records that the preceding fixed compiler must generate."""

from collections import Counter


def compare(profiles):
    from compiler_cut import source_rule
    from periodic import Rule, forest, make_planner
    from staged_carriers import RANK_LOGS, entrance_logs

    word = source_rule().word
    targets = Counter(port.rank for port in word.targets)
    paid = Counter(port.rank for port in word.paid)
    v = word.power
    assert (word.ambient, v, word.floor, word.high_cut) == (134, 480, 16, 11)
    assert targets[8] and targets[64] and 8**320 * 64**160 == word.floor**v
    assert min(paid) > 0
    high = sum(count for rank, count in paid.items() if rank >= 14)
    assert sum(paid.values()) == 107460 and high == 3108

    ambient_log = (word.ambient**v - 1).bit_length()
    floor_log = (word.floor**v).bit_length() - 1
    block_log = (word.high_cut**v).bit_length() - 1
    high_log = (high**v).bit_length() - 1
    all_log = (sum(paid.values())**v).bit_length() - 1
    assert (ambient_log, floor_log, block_log, high_log, all_log) == (3392, 1920, 1660, 5568, 8022)

    # Count the exits of the actual predecessor on finite words with repeated ranks.
    rule = Rule(8, (4, 5), (2, 2, 3))
    for limit in (8, 31, 32, 127, 128, 512):
        plan = forest(rule, limit)
        depth = plan.height + 1
        assert len(plan.exits) == 3**depth
        assert sum(rank == 2**depth for rank in plan.exits.values()) == 2**depth

    planner = make_planner(rule)
    for rank in (8192, 32768):
        outer = planner(rank)
        places = outer.forest.height + 1
        child = planner(2**places)
        assert child.forest is not None
        assert outer.leaves >= 2**places * len(child.forest.exits)

    H = RANK_LOGS[-1]
    assert H == 236800000000000
    restricted_total = 0
    levels = []
    for _ in range(7):
        places = (H - 2 - ambient_log) // floor_log + 1
        assert places > 0
        levels.append((H, places, restricted_total + places * all_log))
        restricted_total += places * high_log
        H = places * block_log

    top_table = levels[0][-1]
    expanded_stream = levels[-1][-1]
    assert (top_table, expanded_stream) == (989379999989304, 3366293830151418)
    old_gate = entrance_logs()[-1]
    assert old_gate == 355760240964240
    ratios = {}
    for name in ("compact", "high-rate", "price-match"):
        current = profiles[name]
        setup = current["log2_all_fixed_setup_upper"]
        assert current["log2_sufficient_public_precision"] + 1 < old_gate
        ratios[name] = expanded_stream // setup
    assert ratios == {"compact": 2054622, "high-rate": 14, "price-match": 2}
    return {
        "top_exit_table_log2_lower": top_table,
        "expanded_stream_log2_lower": expanded_stream,
        "lower_to_upper_exponent_ratio_floor": ratios,
        "old_final_gate_log2": old_gate,
        "levels": levels,
    }
