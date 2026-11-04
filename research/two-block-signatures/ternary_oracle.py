"""Count all 3+3 complementary space pairs over F3, quotienting the first space by monomial symmetries."""
from array import array
from collections import Counter
from itertools import combinations, product


def geometry(n):
    size = 3**n
    digits = [tuple((v//(3**j))%3 for j in range(n)) for v in range(size)]
    add = []
    for x in range(size):
        row = array("H", (0 for _ in range(size)))
        add.append(row)
        for y in range(size):
            row[y] = (x%3+y%3)%3 + 3*add[x//3][y//3]
    negative = [add[v][v] for v in range(size)]
    reps = [v for v in range(1,size) if v < negative[v]]
    point = {v:i for i,u in enumerate(reps) for v in (u,negative[u])}
    generators = []
    for move in range(n):
        mapping = []
        for v in reps:
            coord = list(digits[v])
            if move == n-1:
                coord[0] = -coord[0] % 3
            else:
                coord[move], coord[move+1] = coord[move+1], coord[move]
            target = sum(x*3**j for j,x in enumerate(coord))
            mapping.append(1 << point[target])
        generators.append(mapping)
    return digits, add, negative, point, generators


def enumerate_spaces(n, d, digits, add, negative, point):
    out = {}
    for pivots in combinations(range(n),d):
        cells = [(i,3**j) for i,p in enumerate(pivots) for j in range(p+1,n) if j not in pivots]
        for values in product(range(3),repeat=len(cells)):
            basis = [3**j for j in pivots]
            for (i,power),value in zip(cells,values,strict=True):
                basis[i] += value*power
            words = [0]
            for row in basis:
                words += [add[row][x] for x in words] + [add[negative[row]][x] for x in words]
            lines = tuple(sorted({point[word] for word in words if word}))
            bits = sum(1 << x for x in lines)
            support = sum(any(digits[row][j] for row in basis) << j for j in range(n))
            axes = sum(bool(bits & (1 << point[3**j])) << j for j in range(n))
            if bits in out:
                raise ValueError("duplicate ternary RREF space")
            out[bits] = (lines,support,axes)
    return out


def orbit_representatives(spaces, generators):
    seen = set()
    for start in spaces:
        if start in seen:
            continue
        seen.add(start)
        orbit = [start]
        for v in orbit:
            lines = spaces[v][0]
            for mapping in generators:
                child = sum(mapping[j] for j in lines)
                if child not in spaces:
                    raise ValueError("monomial image missing")
                if child not in seen:
                    seen.add(child)
                    orbit.append(child)
        yield start, len(orbit)


def census(n=6, d=3):
    if n != 2*d or n not in (4,6):
        raise ValueError("ternary exhaustive oracle is bounded to 2+2 and 3+3")
    digits, add, negative, point, generators = geometry(n)
    spaces = enumerate_spaces(n,d,digits,add,negative,point)
    # The finite oracle uses only projective-point intersections and elementary
    # coordinate incidence. The algebraic feasibility criterion is not imported.
    total = Counter()
    orbit_sizes = []
    symbols = (5,7,13,10,11,14,15)
    for a, weight in orbit_representatives(spaces,generators):
        orbit_sizes.append(weight)
        sa, ea = spaces[a][1:]
        complement_count = 0
        per_rep = Counter()
        for b, (_,sb,eb) in spaces.items():
            if a & b:
                continue
            complement_count += 1
            masks = tuple(4*(((sa>>j)&1) + 2*((sb>>j)&1)) +
                          (1-((eb>>j)&1)) + 2*(1-((ea>>j)&1)) for j in range(n))
            per_rep[tuple(masks.count(s) for s in symbols)] += 1
        if complement_count != 3**(d*d):
            raise ValueError("ternary complement multiplicity")
        for key, count in per_rep.items():
            total[key] += weight*count
    if sum(orbit_sizes) != len(spaces):
        raise ValueError("incomplete monomial partition")
    if sum(total.values()) != len(spaces)*3**(d*d):
        raise ValueError("ternary total pair count")
    return {"spaces":len(spaces), "first_space_orbits":len(orbit_sizes),
            "orbit_size_histogram":dict(sorted(Counter(orbit_sizes).items())),
            "ordered_pairs":sum(total.values())}, total
