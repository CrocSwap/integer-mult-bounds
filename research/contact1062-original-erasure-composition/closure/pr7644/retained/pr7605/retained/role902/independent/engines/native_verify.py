"""Check native operators with exact Gaussian dyadic arithmetic.

The interpreter is adapted from the independent campaign native review.
It does not import the source-code producer or the Clifford compiler.
Research used OpenAI Codex under the user's direction.
"""

from functools import lru_cache


def require(condition, label):
    if not condition:
        raise ValueError(label)


def parity(value):
    return value.bit_count() % 2


def mul(matrix, vector):
    return sum(parity(row & vector) << i for i, row in enumerate(matrix))


def transpose(matrix):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(matrix)) for j in range(len(matrix)))


def inverse(matrix):
    n = len(matrix)
    rows = [row | (1 << (n+i)) for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i] >> j & 1), None)
        require(pivot is not None, 'singular binary chart')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    require([row & ((1 << n)-1) for row in rows] == [1 << i for i in range(n)], 'binary inverse')
    return tuple(row >> n for row in rows)


def extend(vectors, n):
    columns, pivots = [], {}
    for value in tuple(vectors) + tuple(1 << i for i in range(n)):
        reduced = value
        while reduced:
            j = reduced.bit_length()-1
            if j not in pivots:
                pivots[j] = reduced
                columns.append(value)
                break
            reduced ^= pivots[j]
    require(len(columns) == n, 'frame basis extension')
    return tuple(columns)


def adjoint(circuit):
    out = []
    for gate in reversed(circuit):
        if gate[0] == 'P':
            out.append(('P', inverse(gate[1])))
        elif gate[0] == 'D':
            out.append(('D', gate[1], tuple(-a % 4 for a in gate[2])))
        elif gate[0] == 'C':
            out.append(('C', gate[1], -gate[2]))
        elif gate[0] == 'phase':
            out.append(('phase', -gate[1] % 4))
        else:
            require(gate[0] == 'X', 'adjoint gate type')
            out.append(gate)
    return tuple(out)


def fourier(rank):
    return tuple(('C', 1 << i, 1) for i in range(rank))


def frame(vectors, n):
    rank = len(vectors)
    if rank == 0:
        return ()
    if rank == n:
        return fourier(n)
    matrix = transpose(extend(vectors, n))
    columns = transpose(inverse(matrix))
    quadratic = tuple((1 << i) ^ sum(parity(a & b) << j for j, b in enumerate(columns)) for i, a in enumerate(columns))
    diagonal = tuple((row >> i) & 1 for i, row in enumerate(quadratic))
    chart = (('P', matrix), ('D', quadratic, diagonal))
    return adjoint(chart) + fourier(rank) + chart


def monomial(record):
    matrix = tuple(record['matrix_rows'])
    quadratic = tuple(record['quadratic_rows'])
    linear = tuple(record['linear_Z4'])
    require(transpose(quadratic) == quadratic, 'quadratic symmetry')
    require(len(matrix) == len(quadratic) == len(linear) == 9, 'monomial dimension')
    require(all(a % 2 == (quadratic[i] >> i) & 1 for i, a in enumerate(linear)), 'diagonal parity')
    inverse(matrix)
    return (('D', quadratic, linear), ('P', matrix), ('X', record['offset']), ('phase', record['phase']))


def recipe(record):
    rank = record['rank']
    require(isinstance(rank, int) and 0 <= rank <= 9, 'child rank')
    if rank == 0:
        require(record['right'] is None, 'rank zero right factor')
        return monomial(record['left'])
    return monomial(record['right']) + fourier(rank) + monomial(record['left'])


def tableau(circuit, n=9):
    rows = [(1 << i, 0, 0) for i in range(n)] + [(0, 1 << i, 0) for i in range(n)]
    for gate in circuit:
        tag = gate[0]
        out = []
        inverse_transpose = transpose(inverse(gate[1])) if tag == 'P' else None
        for x, z, phase in rows:
            if tag == 'P':
                x, z = mul(gate[1], x), mul(inverse_transpose, z)
            elif tag == 'X':
                phase += 2 * parity(z & gate[1])
            elif tag == 'C':
                if parity(z & gate[1]):
                    x ^= gate[1]
                    phase += 3 * gate[2]
            elif tag == 'D':
                quadratic, linear = gate[1:]
                phase += sum(linear[i] for i in range(n) if x >> i & 1)
                phase += 2 * sum(parity((quadratic[i] >> (i+1)) & (x >> (i+1))) for i in range(n) if x >> i & 1)
                z ^= mul(quadratic, x)
            else:
                require(tag == 'phase', 'tableau gate type')
            out.append((x, z, phase % 4))
        rows = out
    return tuple(rows)


@lru_cache(maxsize=512)
def action(gate):
    if gate[0] == 'P':
        return tuple(mul(gate[1], x) for x in range(512))
    require(gate[0] == 'D', 'state action type')
    quadratic, linear = gate[1:]
    return tuple((sum(linear[i] for i in range(9) if x >> i & 1)
                  + 2 * sum(parity((quadratic[i] >> (i+1)) & (x >> (i+1))) for i in range(9) if x >> i & 1)) % 4 for x in range(512))


def rotate(pair, power):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def state(circuit, basis=0):
    value, denominator = {basis: (1, 0)}, 0
    for gate in circuit:
        tag = gate[0]
        result = {}
        if tag == "C":
            direction, sign = gate[1:]
            for address, (a, b) in value.items():
                for target, pair in ((address, (a - sign*b, b + sign*a)),
                                     (address ^ direction, (a + sign*b, b - sign*a))):
                    old = result.get(target, (0, 0))
                    result[target] = (old[0] + pair[0], old[1] + pair[1])
            denominator += 1
        else:
            for address, pair in value.items():
                if tag == "P":
                    target = mul(gate[1], address)
                elif tag == "X":
                    target = address ^ gate[1]
                else:
                    target = address
                    if tag == "D":
                        pair = rotate(pair, action(gate)[address])
                    else:
                        require(tag == "phase", "Unknown Gaussian state gate")
                        pair = rotate(pair, gate[1])
                require(target not in result, "A monomial address map is not injective")
                result[target] = pair
        value = {address: pair for address, pair in result.items() if pair != (0, 0)}
    while denominator and all((a | b) % 2 == 0 for a, b in value.values()):
        denominator -= 1
        value = {address: (a//2, b//2) for address, (a, b) in value.items()}
    return value, denominator


def equal(actual, expected, label):
    require(tableau(actual) == tableau(expected), label + ": signed Pauli action")
    require(state(actual) == state(expected), label + ": exact global phase")


def verify(data, certificate):
    word = data["word"]
    original, clean = data["programs"], data["clean_programs"]
    source_recipes = data["recipes"]
    residuals = data["residuals"]["recipes"]
    native_tags = {"climb", "adapter", "residual_adapter"}
    for orientation in ("forward", "backward"):
        native = [event for event in clean[orientation] if event[0] in native_tags]
        require(native == [event for event in original[orientation] if event[0] in native_tags],
                "A retained native event changed")
        require(len(native) == 5056, "The retained native event count changed")
    frames = [frame(tuple(vectors), 9) for vectors in word["frames"]]
    used = {(event[3], event[4]) for program in clean.values()
            for event in program if event[0] == "climb"}
    children = {(record["old"], record["new"]): record for record in source_recipes["children"]}
    require(len(children) == len(source_recipes["children"]) and used <= set(children),
            "The retained child recipe coverage is incomplete")
    for old, new in sorted(used):
        record = children[old, new]
        require(record["rank"] == len(word["frames"][new]) - len(word["frames"][old]),
                "A retained child has the wrong rank")
        equal(recipe(record), adjoint(frames[old]) + frames[new], "Retained child")
    endpoints = {(record["role"], record["port"]): record
                 for record in source_recipes["endpoint_adapters"]}
    require(len(endpoints) == len(source_recipes["endpoint_adapters"])
            and set(endpoints) == {(role, p) for role in ("source", "target") for p in range(112)},
            "The endpoint adapter coverage is incomplete")
    for (role, port), record in endpoints.items():
        direction = word["ports"][port]
        conventional = (("C", direction, 1),) if role == "source" else (
            ("C", direction, -1),) + fourier(9)
        index = word["start"][port] if role == "source" else word["final"][112 + port]
        require(record["frame"] == index and record["rank"] == 0, "An endpoint frame changed")
        equal(recipe(record), adjoint(conventional) + frames[index], "Endpoint adapter")
    used_residuals = set()
    for program in clean.values():
        for event in program:
            if event[0] != "residual_adapter":
                continue
            _, position, register, entry, *tail = event
            terminal = tail[0] if tail else 1
            key = str(entry) if terminal == 1 else str(entry) + ":" + str(terminal)
            require(key in residuals and position in ("pre", "post"), "A residual binding changed")
            require(entry == word["start"][register] and terminal == word["final"][register],
                    "A residual endpoint changed")
            used_residuals.add(key)
    for key in sorted(used_residuals):
        record = residuals[key]
        equal(recipe(record), adjoint(frames[record["frame"]]) + frames[record.get("terminal", 1)],
              "Residual adapter")
    records = certificate["input_recipes"]
    ports = certificate["compensation_ports"]
    require([record["port"] for record in records] == ports and len(records) == 8,
            "The eight input recipes changed")
    columns = 0
    for item in records:
        port, label = item["port"], item["label"]
        require(label == word["ports"][port] and item["canonical_start_frame_id"] == word["start"][port],
                "An input recipe has the wrong supplier label")
        record = item["recipe"]
        require(record["rank"] == 1, "An input copy has the wrong child rank")
        for side in ("left", "right"):
            factor = record[side]
            require(factor["quadratic_rows"] == [0] * 9 and factor["linear_Z4"] == [0] * 9
                    and factor["offset"] == factor["phase"] == 0,
                    "An input factor is not an address permutation")
        actual, expected = recipe(record), (("C", label, 1),)
        equal(actual, expected, "Positive inherited input line")
        for basis in range(512):
            require(state(actual, basis) == state(expected, basis), "A complete input Gaussian column differs")
            columns += 1
        negative = monomial(record["right"]) + (("C", 1, -1),) + monomial(record["left"])
        require(tableau(negative) != tableau(expected) or state(negative) != state(expected),
                "An inverse input child was not detected")
        phased = actual + (("phase", 1),)
        require(tableau(phased) == tableau(actual) and state(phased) != state(expected),
                "An input phase-only error was not detected")
    return {"status": "PASS_EXACT_INPUT_NATIVE_FRAMES", "retained_native_events_per_orientation": 5056,
            "retained_child_recipes": len(used), "endpoint_adapter_recipes": len(endpoints),
            "residual_adapter_recipes": len(used_residuals), "new_input_recipes": len(records),
            "new_exact_gaussian_columns": columns, "inverse_input_child_controls": len(records),
            "phase_only_controls": len(records), "address_permutation_factors": 2 * len(records),
            "method": "Independent signed Pauli and exact Gaussian interpretation; no compiler import",
            "scope": "Positive inherited input frames before every retained adapter. No recursive hosting claim."}
