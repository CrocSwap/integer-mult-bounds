"""Independent reverse-barrier audit of literal T740 hosted phases.

Nick Petalas. Apache-2.0. Predecessor code is never imported or executed.
"""

from collections import Counter

OWNERS, PORTS, CHILDREN = 740, 112, 20
BASE_ROWS = 9 * 74 * 408


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integers(values, size, lower, upper):
    require(type(values) is list and len(values) == size, "integer row dimensions")
    require(
        all(type(x) is int and lower <= x < upper for x in values), "integer row domain"
    )


def barriers(template):
    """Latest stream touch before each residual site, rather than forward windows."""
    events = template["execution_schedule"]
    require(type(events) is list and len(events) <= 64, "bounded schedule")
    local = {r["stage"]: r for r in template["recipe"] if r["kind"] == "local"}
    require(set(local) == set(range(9)), "nine local definitions")
    starts, touches, sites = {}, [], {}
    for position, event in enumerate(events):
        kind = event["kind"]
        if kind == "local_cover_sweep":
            stage = event["stage"]
            require(stage not in starts, "one local event per stage")
            starts[stage] = position
            pair = local[stage]["pair"]
            touches.append((position, {2 * pair, 2 * pair + 1}))
        elif kind == "bridge":
            touched = {
                2 * event["src"],
                2 * event["src"] + 1,
                2 * event["dst"],
                2 * event["dst"] + 1,
            }
            touches.append((position, touched))
        elif kind == "terminal":
            touches.append((position, set(range(8))))
        elif kind == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                require(
                    type(child) is int and child not in sites, "unique residual child"
                )
                sites[child] = position, 2 * event["pair"] + side
        else:
            require(
                kind
                in {
                    "terminal_Y_translations",
                    "bank_padding_cover_sweep",
                    "translate_every_live_family",
                },
                "classified schedule event",
            )
    require(
        set(starts) == set(range(9)) and set(sites) == set(range(20)), "complete events"
    )
    require(list(starts.values()) == sorted(starts.values()), "ordered stages")
    intervals = {}
    for child, (stop, stream) in sites.items():
        previous = -1
        for position, rows in reversed(touches):
            if position < stop and stream in rows:
                previous = position
                break
        intervals[child] = previous, stop, stream
    return starts, intervals


def chronology(order, dispatch):
    require(type(order) is list and len(order) == 666, "base order coverage")
    expanded, times = [], [[] for _ in range(OWNERS)]
    for stage, owner in order:
        require(type(stage) is int and type(owner) is int, "strict order integers")
        require(0 <= stage < 9 and 0 <= owner < 74, "base order domain")
        for copy in range(10):
            target = owner + 74 * copy
            require(stage == len(times[target]), "owner stage sequence")
            times[target].append(len(expanded))
            expanded.append((stage, target))
    require(all(len(t) == 9 for t in times), "all owner times")
    require(type(dispatch) is list and len(dispatch) == 666, "dispatch dimensions")
    tags = {(stage, owner): tag for stage, owner, tag in dispatch}
    require(
        set(tags) == {(s, o) for s in range(9) for o in range(74)}, "dispatch coverage"
    )
    return expanded, times, tags


def lift(row, copy):
    integers(row, 6, 0, 1_000_000)
    time, helper, owner, child, port, offset = row
    return [10 * time + copy, helper, owner + 74 * copy, child, port, offset]


def corrections(base, journal):
    require(type(base) is list and len(base) == BASE_ROWS, "base rows")
    require(type(journal["copies"]) is int and journal["copies"] == 10, "ten copies")
    edits = journal["edits"]
    require(type(edits) is list and len(edits) == 145, "journal coverage")
    by_copy = [{} for _ in range(10)]
    for index, before, after in edits:
        require(type(index) is int and 0 <= index < 10 * BASE_ROWS, "journal index")
        copy, row = divmod(index, BASE_ROWS)
        require(row not in by_copy[copy], "unique journal index")
        integers(before, 6, 0, 1_000_000)
        integers(after, 6, 0, 1_000_000)
        require(before == lift(base[row], copy), "journal preimage")
        require(after[:2] == before[:2], "call and helper unchanged")
        by_copy[copy][row] = after
    return by_copy


def child_lengths(phases):
    recipes = phases["recipes"]
    require(type(recipes) is list and len(recipes) == PORTS, "112 port recipes")
    result = []
    for port, recipe in enumerate(recipes):
        require(type(recipe["port"]) is int and recipe["port"] == port, "port order")
        children = recipe["idle_children"]
        require(type(children) is list and len(children) == CHILDREN, "twenty children")
        lengths = [len(child["orthogonal_axes"]) for child in children]
        require(all(0 <= n <= 73 for n in lengths), "child axis bound")
        result.append(lengths)
    return result


def row_placement(row, prepared):
    order, times, tags, providers, starts, intervals, lengths, plan = prepared
    integers(row, 6, 0, 1_000_000)
    time, helper, owner, child, port, offset = row
    require(
        time < 6660
        and helper < 408
        and owner < OWNERS
        and child < CHILDREN
        and port < PORTS,
        "hosted row coordinates",
    )
    stage, caller = order[time]
    width = providers[tags[stage, caller % 74]]["widths"][helper]
    require(type(width) is int and 1 <= width <= 73, "actual helper width")
    require(offset + width <= lengths[port][child], "hosted slice bounds")
    cut = sum(own_time < time for own_time in times[owner])
    require(cut < 9, "host before last local stage")
    previous, stop, stream = intervals[child]
    require(previous < starts[cut] <= stop, "noncommuting stream barrier")
    pair, side = plan["pairs"][str(child)], plan["sides"][str(child)]
    require(
        type(pair) is int and type(side) is int and 0 <= pair < 4 and side in (0, 1),
        "physical plan coordinates",
    )
    require(2 * pair + side == stream, "hosted physical stream")
    return owner * PORTS + port, child, cut, offset, width


def cover_row(placement, masks, counts, histogram):
    context, child, cut, offset, width = placement
    slot = context * CHILDREN + child
    positions = ((1 << width) - 1) << offset
    require(masks[slot] & positions == 0, "overlapping hosted slices")
    masks[slot] |= positions
    counts[context] += 1
    histogram[child, cut] += 1


def summarize(masks, counts, histogram, lengths, starts, intervals):
    require(all(counts), "all 82880 contexts visited")
    profiles = Counter()
    for context in range(OWNERS * PORTS):
        rank = []
        for child in range(CHILDREN):
            mask = masks[context * CHILDREN + child]
            require(mask & (mask + 1) == 0, "compact hosted prefix")
            rank.append(lengths[context % PORTS][child] - mask.bit_count())
        profiles[tuple(rank)] += 1
    allowed = {
        str(child): [stage for stage in range(9) if before < starts[stage] <= stop]
        for child, (before, stop, _) in intervals.items()
    }
    return {
        "owners": OWNERS,
        "ports": PORTS,
        "contexts": len(counts),
        "hosted_rows": sum(counts),
        "journal_edits": 145,
        "hosted_rows_per_context": [min(counts), max(counts)],
        "allowed_stage_cuts": allowed,
        "hosted_cut_histogram": [[a, b, n] for (a, b), n in sorted(histogram.items())],
        "residual_profiles": [[list(r), n] for r, n in sorted(profiles.items())],
    }


def audit(data):
    starts, intervals = barriers(data["template"])
    order, times, tags = chronology(data["order"], data["dispatch"])
    lengths = child_lengths(data["phases"])
    base = data["base"]["rows"]
    edits = corrections(base, data["journal"])
    prepared = (
        order,
        times,
        tags,
        data["providers"],
        starts,
        intervals,
        lengths,
        data["plan"],
    )
    masks, counts = [0] * (OWNERS * PORTS * CHILDREN), [0] * (OWNERS * PORTS)
    histogram = Counter()
    for copy in range(10):
        for index, row in enumerate(base):
            hosted = edits[copy].get(index)
            if hosted is None:
                hosted = lift(row, copy)
            cover_row(row_placement(hosted, prepared), masks, counts, histogram)
    return summarize(masks, counts, histogram, lengths, starts, intervals)
