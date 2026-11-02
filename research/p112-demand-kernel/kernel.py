"""Exact nonnegative demand reduction. New material: Nick Petalas, Apache-2.0."""

from itertools import combinations

MAX_VERTICES = 120
MAX_CLIQUES = 300_000
MAX_FACTORS = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bits(mask):
    require(type(mask) is int and 0 <= mask < 1 << MAX_VERTICES, "invalid mask")
    for _ in range(MAX_VERTICES):
        if not mask:
            break
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def adjacency(model):
    roots, live = model["lines"], model["live"]
    require(len(roots) == MAX_VERTICES and len(live) == 112, "fixed geometry size")
    require(all(len(row) == 8 for row in roots), "eight root coordinates")
    require(len(set(live)) == len(live), "unique live vertices")
    require(all(type(i) is int and 0 <= i < MAX_VERTICES for i in live), "live index")
    return {i: sum(1 << j for j in live if j > i and
                   sum(a * b for a, b in zip(roots[i], roots[j], strict=True)) == 0)
            for i in live}


def all_cliques(model):
    """Increasing-prefix DFS, with an explicit finite node budget."""
    later = adjacency(model)
    pending = [(0, sum(1 << i for i in model["live"]))]
    found = []
    for _ in range(MAX_CLIQUES + 1):
        if not pending:
            return sorted(found)
        chosen, candidates = pending.pop()
        for i in bits(candidates):
            child = chosen | 1 << i
            require(child.bit_count() <= 8, "orthogonal dimension bound")
            found.append(child)
            require(len(found) <= MAX_CLIQUES, "clique capacity exhausted")
            pending.append((child, candidates & later[i]))
    raise ValueError("clique iteration budget exhausted")


def alphabet(model, examples):
    """Stable first occurrence: saved layouts, then puncture coordinates."""
    roots, live = model["lines"], model["live"]
    live_mask = sum(1 << i for i in live)
    stars = [sum(1 << i for i in live if
                 sum(a * b for a, b in zip(root, roots[i], strict=True)))
             for root in roots]
    supports = [part for a, star in enumerate(stars)
                for part in (star, star & ~(1 << a))]
    require(len(examples) == 2, "two saved layouts")
    factors = []
    for example in examples:
        require(len(example["terms"]) == 9, "nine caps per saved layout")
        for a, b, encoded in example["terms"]:
            require(0 <= a < 240 and 0 <= b < 240, "star index")
            cut = int(encoded, 16)
            require(0 <= cut and cut & ~supports[a] == 0, "cut outside parent")
            pair = (supports[a] & ~cut, supports[b])
            require((pair[0] | pair[1]) & ~live_mask == 0, "nonlive cap")
            if pair not in factors:
                factors.append(pair)
    coordinates = []
    require(len(model["punctured_frame"]) == 8, "eight coordinate rectangles")
    for a in model["punctured_frame"]:
        pair = (stars[a], stars[a])
        if pair not in factors:
            factors.append(pair)
        coordinates.append(factors.index(pair))
    require(len(factors) <= MAX_FACTORS, "alphabet capacity")
    return factors, coordinates


def hit_signature(clique, factors):
    require(len(factors) <= MAX_FACTORS, "alphabet capacity")
    return sum(1 << k for k, (left, right) in enumerate(factors)
               if left & clique and right & clique)


def quotient(cliques, factors):
    require(len(cliques) <= MAX_CLIQUES, "clique capacity")
    rows = {}
    for clique in cliques:
        mask = hit_signature(clique, factors)
        candidate = (clique.bit_count(), -clique)
        if mask not in rows or candidate > rows[mask]:
            rows[mask] = candidate
    return {mask: (rank, -witness) for mask, (rank, witness) in rows.items()}


def reduce_rows(rows):
    require(len(rows) <= 1 << MAX_FACTORS, "signature capacity")
    ordered = sorted(rows, key=lambda mask: (-rows[mask][0], mask.bit_count(), mask))
    kept = {}
    for mask in ordered:
        rank, witness = rows[mask]
        if not any(other & mask == other and demand >= rank
                   for other, (demand, _) in kept.items()):
            kept[mask] = (rank, witness)
    return dict(sorted(kept.items()))


def domination(rows, kept):
    """Return an explicit dominating retained row for every quotient row."""
    mapping = {}
    for mask, (rank, _) in rows.items():
        choices = [other for other, (demand, _) in kept.items()
                   if other & mask == other and demand >= rank]
        require(bool(choices), "omitted demand has no retained dominator")
        mapping[mask] = min(choices)
    return mapping


def accepts(rows, multiplicities):
    require(len(multiplicities) <= MAX_FACTORS, "multiplicity dimension")
    require(all(type(x) is int and x >= 0 for x in multiplicities),
            "nonnegative integer multiplicities")
    require(all(0 <= mask < 1 << len(multiplicities) for mask in rows), "row width")
    return all(sum(multiplicities[k] for k in range(len(multiplicities))
                   if mask >> k & 1) >= rank for mask, (rank, _) in rows.items())


def tuple_cliques(model):
    """Separate level enumeration using literal coordinate dot products."""
    roots = model["lines"]
    live = sorted(model["live"])
    level = [(i,) for i in live]
    result = set()
    for _ in range(8):
        following = []
        for group in level:
            result.add(sum(1 << i for i in group))
            for j in live:
                if j > group[-1] and all(
                    sum(roots[i][a] * roots[j][a] for a in range(8)) == 0
                    for i in group
                ):
                    following.append(group + (j,))
        require(len(result) + len(following) <= MAX_CLIQUES, "oracle capacity")
        level = following
    require(not level, "ninth orthogonal vector")
    return result


def check_witnesses(rows, factors, cliques):
    domain = set(cliques)
    for mask, (rank, witness) in rows.items():
        require(witness in domain, "row witness outside clique domain")
        require(rank == witness.bit_count(), "row witness has wrong demand")
        require(mask == hit_signature(witness, factors), "row witness has wrong hits")
    for a, b in combinations(rows, 2):
        require(not (a & b == a and rows[a][0] >= rows[b][0]), "dominated kernel row")
        require(not (a & b == b and rows[b][0] >= rows[a][0]), "dominated kernel row")
