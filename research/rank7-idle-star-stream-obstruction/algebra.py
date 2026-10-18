"""Exact Gaussian-integer replay of eight separately labelled physical streams."""

from collections import defaultdict

from source import require

ZERO = (0, 0)
ONE = (1, 0)


def dot(left, right):
    return (int(left) & int(right)).bit_count() % 2


def rotate(value, exponent):
    real, imag = value
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[exponent % 4]


def identity():
    return [[ONE if i == j else ZERO for j in range(8)] for i in range(8)]


def phase(matrix, stream, exponent):
    matrix[stream] = [rotate(value, exponent) for value in matrix[stream]]


def shear(matrix, dst, src, coefficient):
    matrix[dst] = [
        (a + coefficient * c, b + coefficient * d)
        for (a, b), (c, d) in zip(matrix[dst], matrix[src], strict=True)
    ]


def intertwines(matrix, donor, receiver, exponent=1):
    """Test E_receiver M = M E_donor for one Fourier-mode phase transfer."""
    require(0 <= donor < 8 and 0 <= receiver < 8, "physical stream index")
    require(
        len(matrix) == 8 and all(len(row) == 8 for row in matrix), "eight-stream matrix"
    )
    left = [list(row) for row in matrix]
    phase(left, receiver, exponent)
    right = [list(row) for row in matrix]
    for row in right:
        row[donor] = rotate(row[donor], exponent)
    return left == right


def stage_blocks(template):
    blocks = {}
    stage = None
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue  # Banks are separate; the all-family correction is zero at g=I.
        if kind == "local_cover_sweep":
            stage = event["stage"]
            blocks[stage] = []
        require(stage is not None, "data event precedes first local stage")
        blocks[stage].append(event)
    require(set(blocks) == set(range(9)), "nine stage blocks")
    return blocks


def host_projection(context):
    recipe, plan = context["recipe"], context["plan"]
    hosts, used = defaultdict(list), defaultdict(set)
    for time, helper, owner, child, port, offset in context["rows"]:
        require(owner == port == 0, "projected role destination")
        stage, replica = context["order"][time]
        tag = context["dispatch"][stage, replica % 74]
        width = context["providers"][tag]["widths"][helper]
        axes = list(map(int, recipe["idle_children"][child]["orthogonal_axes"]))
        require(offset >= 0 and offset + width <= len(axes), "hosted slice range")
        positions = set(range(offset, offset + width))
        require(not used[child] & positions, "hosted slice overlap")
        used[child].update(positions)
        stream = 2 * plan["pairs"][str(child)] + plan["sides"][str(child)]
        hosts[time].append((stream, axes[offset : offset + width]))
    residual = {}
    for child, entry in enumerate(recipe["idle_children"]):
        require(used[child] == set(range(len(used[child]))), "compact hosted prefix")
        residual[child] = [
            int(v)
            for i, v in enumerate(entry["orthogonal_axes"])
            if i not in used[child]
        ]
    require(all(len(residual[c]) == 48 for c in (8, 10, 12, 13)), "unhosted star bins")
    return hosts, residual


def apply_overlay(recipe, original, moves):
    final = {child: list(axes) for child, axes in original.items()}
    translations = [
        int(s[k])
        for s in recipe["stage_alignment"]
        for k in ("entry_X", "exit_X", "entry_Y", "exit_Y")
    ]
    translations.append(int(recipe["terminal_Y_translation"]))
    seen = set()
    for replica, port, donor, receiver, axes in moves:
        require(replica == port == 0 and donor != receiver, "star move group")
        require(len(axes) == len(set(axes)) == 3, "three distinct moved axes")
        terminal = [
            int(recipe["idle_children"][c]["translation_after"])
            for c in (donor, receiver)
        ]
        for axis in axes:
            require(
                axis in original[donor] and (donor, axis) not in seen, "axis ownership"
            )
            seen.add((donor, axis))
            require(
                all(
                    dot(axis, v) == 0
                    for v in original[receiver] + translations + terminal
                ),
                "declared per-axis commuting rule",
            )
            final[donor].remove(axis)
            final[receiver].append(axis)
    for axes in final.values():
        require(len(axes) <= 51, "halving rank cap")
        require(
            all(
                dot(v, w) == int(i == j)
                for i, v in enumerate(axes)
                for j, w in enumerate(axes)
            ),
            "orthonormal final axes",
        )
    require(
        sorted(v for axes in original.values() for v in axes)
        == sorted(v for axes in final.values() for v in axes),
        "unchanged axis multiset",
    )
    return final


def data_event(matrix, event, context, residual, character):
    kind = event["kind"]
    recipe = context["recipe"]
    qbit = dot(character, recipe["q"])
    if kind == "local_cover_sweep":
        stage = event["stage"]
        local = next(
            e
            for e in context["template"]["recipe"]
            if e["kind"] == "local" and e["stage"] == stage
        )
        x, y = 2 * local["pair"], 2 * local["pair"] + 1
        for side, stream in enumerate((x, y)):
            before = (
                (1 - side) * qbit
                if stage == 0
                else (character & ((1 << (9 + 8 * (stage - 1))) - 1)).bit_count()
                - side * qbit
            )
            phase(matrix, stream, -before)
        if local["reverse"]:
            shear(matrix, x, y, -1)
        else:
            shear(matrix, y, x, 1)
        for side, stream in enumerate((x, y)):
            after = (character & ((1 << (9 + 8 * stage)) - 1)).bit_count() - side * qbit
            phase(matrix, stream, after)
    elif kind == "idle_cover_sweep":
        for side, child in enumerate(event["child_indices"]):
            exponent = sum(dot(character, v) for v in residual[child])
            exponent += 2 * dot(
                character, recipe["idle_children"][child]["translation_after"]
            )
            phase(matrix, 2 * event["pair"] + side, exponent)
    elif kind == "bridge":
        dst, src, coefficient = event["dst"], event["src"], event["coefficient"]
        shear(matrix, 2 * dst, 2 * src, coefficient)
        shear(matrix, 2 * src + 1, 2 * dst + 1, -coefficient)
    elif kind == "terminal_Y_translations":
        for pair in event["pairs"]:
            phase(matrix, 2 * pair + 1, 2 * qbit)
    elif kind == "terminal":
        for pair in range(event["pairs"]):
            matrix[2 * pair], matrix[2 * pair + 1] = (
                matrix[2 * pair + 1],
                [rotate(v, 2) for v in matrix[2 * pair]],
            )
    else:
        raise ValueError("unknown physical data event")


def replay(context, residual, character):
    require(type(character) is int and 0 <= character < 1 << 73, "Fourier character")
    hosts, _ = host_projection(context)
    blocks = stage_blocks(context["template"])
    matrix = identity()
    for time, (stage, replica) in enumerate(context["order"]):
        for stream, axes in hosts.get(time, ()):
            phase(matrix, stream, sum(dot(character, v) for v in axes))
        if replica == 0:
            for event in blocks[stage]:
                data_event(matrix, event, context, residual, character)
    return matrix


def intervening_events(template, donor=10, receiver=12):
    events = template["execution_schedule"]
    starts = [i for i, e in enumerate(events) if donor in e.get("child_indices", [])]
    ends = [i for i, e in enumerate(events) if receiver in e.get("child_indices", [])]
    require(
        len(starts) == len(ends) == 1 and starts[0] < ends[0], "transfer event order"
    )
    interval = events[starts[0] + 1 : ends[0]]
    local = {e["stage"]: e["pair"] for e in template["recipe"] if e["kind"] == "local"}
    for event in interval:
        kind = event["kind"]
        if kind == "bridge":
            require(
                0 not in (event["dst"], event["src"]), "X0 mixed in transfer interval"
            )
        elif kind == "local_cover_sweep":
            require(local[event["stage"]] != 0, "X0 mixed in transfer interval")
        else:
            require(kind == "idle_cover_sweep", "unproved intervening data operation")
    return interval
