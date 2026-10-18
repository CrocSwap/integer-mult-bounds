"""Independent literal-word and column-trace engine. Apache-2.0.

Sricharan Vagvala, with OpenAI Codex assistance. No predecessor imports.
"""
from fractions import Fraction


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fixture(k=53, m=5, seed=53):
    require(type(k) is int and k > 0 and type(m) is int and m > 0,
            "positive fixture dimensions")
    result = []
    for i in range(k):
        r = [[], []]
        for j in range(m):
            a = 2 * (bin(seed + i * m + j).count("1") % 2) - 1
            b = (seed + 2 * i + j) % 3 - 1
            r[0] += [a, b]
            r[1] += [0, a]
        result.append(r)
    return result


def validate_readers(readers, m):
    require(bool(readers), "nonempty reader list")
    for r in readers:
        require(len(r) == 2 and all(len(x) == 2 * m for x in r), "reader dimensions")
        require(all(type(x) is int for row in r for x in row), "integer reader")
        for j in range(m):
            require(r[1][2*j] == 0 and r[0][2*j] == r[1][2*j+1],
                    "reader intertwining")


def undo(word):
    answer = []
    for op, dst, src, num, den in reversed(word):
        if op == "ADD":
            answer.append((op, dst, src, -num, den))
        elif op == "SCALE":
            answer.append((op, dst, src, den, num))
        else:
            raise ValueError("unknown inverse instruction")
    return answer


def shear(exponent, pairs):
    require(type(exponent) is int, "integer shear exponent")
    sign = -1 if exponent < 0 else 1
    answer = []
    for dst, src in pairs:
        require(dst != src, "shear alias")
        bits, shifts = abs(exponent), 0
        while bits:
            if bits % 2:
                answer.append(("ADD", dst, src, sign, 1))
            bits //= 2
            if bits:
                answer.append(("SCALE", src, src, 2, 1))
                shifts += 1
        answer += [("SCALE", src, src, 1, 2)] * shifts
    return answer


def pairs(m):
    return [(2 + 2*m + 2*j, 3 + 2*m + 2*j) for j in range(m)]


def leaf(r, m):
    result = []
    for d in range(2):
        for j, coefficient in enumerate(r[d]):
            sign = -1 if coefficient < 0 else 1
            result += [("ADD", d, 2 + 2*m + j, sign, 1)] * abs(coefficient)
    result += [("ADD", d, s, 1, 1) for d, s in pairs(m)]
    return result


def interval(readers, a, b, m, cancel=False):
    require(type(a) is int and type(b) is int and 0 <= a < b <= len(readers),
            "interval range")
    validate_readers(readers, m)
    result = []
    for i in range(a, b):
        if i != a:
            result.append(("ADD", 0, 1, 1, 1))
        result += leaf(readers[i], m)
    result += shear(a-b, pairs(m))
    if not cancel:
        result += shear(1-(b-a), [(0, 1)])
    return result


def transfer(m, sign):
    return [("ADD", 2 + 2*m + j, 2+j, sign, 1) for j in range(2*m)]


def partition_word(readers, cuts, m, cancel=True):
    require(bool(cuts) and cuts[-1] == len(readers), "terminal cut")
    require(all(type(x) is int for x in cuts), "integer cuts")
    group, a = [], 0
    for b in cuts:
        require(a < b <= len(readers), "strict cuts")
        group += interval(readers, a, b, m, cancel and b == len(readers))
        a = b
    return transfer(m, 1) + group + transfer(m, -1) + undo(group)


def identity(n):
    # columns[basis input][current coordinate], rather than symbolic rows.
    return [[int(i == j) for i in range(n)] for j in range(n)]


def apply(word, initial):
    """Execute scalar columns and sum absolute traces at every changed row.

    Every exact-grid halving is checked, including on incoming dirty columns.
    """
    cols = [x[:] for x in initial]
    n = len(cols)
    require(n > 0 and all(len(x) == n for x in cols), "square initial operator")
    norms = [sum(abs(c[j]) for c in cols) for j in range(n)]
    peak = max(norms)
    witness = {"step": 0, "row": norms.index(peak)}
    for step, (op, d, s, num, den) in enumerate(word, 1):
        require(type(d) is int and type(s) is int and 0 <= d < n and 0 <= s < n,
                "instruction address")
        if op == "ADD":
            require(d != s and type(num) is int and num in (-1, 1) and den == 1,
                    "unit ADD alphabet")
            for c in cols:
                c[d] += num * c[s]
        elif op == "SCALE":
            require(d == s and (num, den) in ((2, 1), (1, 2)), "dyadic SCALE alphabet")
            for c in cols:
                require(num * c[d] % den == 0, "nonintegral halving")
                c[d] = num * c[d] // den
        else:
            raise ValueError("instruction alphabet")
        value = sum(abs(c[d]) for c in cols)
        if value > peak:
            peak, witness = value, {"step": step, "row": d}
    return cols, peak, witness


def rational_trace(word, initial):
    """Separate scalar Fraction runs: no integer-halving evaluator is used.

    Accumulate the absolute scalar value at each changed coordinate across
    all basis columns. Check integrality on every operation, not just output.
    """
    totals = [Fraction(0) for _ in word]
    final = []
    integral = True
    for original in initial:
        values = list(map(Fraction, original))
        for index, (op, d, s, num, den) in enumerate(word):
            if op == "ADD":
                values[d] = values[d] + num * values[s]
            elif op == "SCALE":
                values[d] = values[d] * Fraction(num, den)
            else:
                raise ValueError("rational instruction alphabet")
            integral &= values[d].denominator == 1
            totals[index] += abs(values[d])
        final.append(values)
    initial_peak = max(sum(abs(c[j]) for c in initial) for j in range(len(initial)))
    return final, max([initial_peak, *totals]), integral


def chronological_contexts(readers, m):
    """Record boundaries by executing the eager echo, including literal inverse.

    No closed-form accumulated-reader context is used to manufacture a state.
    """
    neutral = [leaf(r, m) + [("ADD", d, s, -1, 1) for d, s in pairs(m)]
               for r in readers]
    n = 2 + 4*m
    fg = [apply(transfer(m, 1), identity(n))[0]]
    ig = [identity(n)]
    for ops in neutral:
        fg.append(apply(ops, fg[-1])[0])
        ig.append(apply(ops, ig[-1])[0])
    fu = [None] * (len(readers)+1)
    iu = [None] * (len(readers)+1)
    fu[-1] = apply(transfer(m, -1), fg[-1])[0]
    iu[-1] = apply(transfer(m, 1), ig[-1])[0]
    for i in range(len(readers)-1, -1, -1):
        fu[i] = apply(undo(neutral[i]), fu[i+1])[0]
        iu[i] = apply(undo(neutral[i]), iu[i+1])[0]
    return {"fg": fg, "fu": fu, "ig": ig, "iu": iu}


def bill(word):
    add = sum(x[0] == "ADD" for x in word)
    scale = sum(x[0] == "SCALE" for x in word)
    require(add + scale == len(word), "cost alphabet")
    return add, scale


def edge_checks(readers, m, rational_finals=True):
    states = chronological_contexts(readers, m)
    k = len(readers)
    edges, contextual, rational_columns = [], 0, 0
    primitive_steps = 0
    for a in range(k):
        for b in range(a+1, k+1):
            fused = b == k
            ops = interval(readers, a, b, m, fused)
            child_add = sum(bill(leaf(r, m))[0] for r in readers[a:b])
            add, scale = bill(ops)
            trials = []
            if fused:
                for source, target, sign in (("fg", "fu", -1), ("ig", "iu", 1)):
                    trials.append((ops + transfer(m, sign) + undo(ops),
                                   states[source][a], states[target][a]))
            else:
                for label in ("fg", "fu", "ig", "iu"):
                    inverse = label in ("fu", "iu")
                    trials.append((undo(ops) if inverse else ops,
                                   states[label][b if inverse else a],
                                   states[label][a if inverse else b]))
            peaks = []
            for word, entrance, expected in trials:
                end, peak, _ = apply(word, entrance)
                require(end == expected, f"interval endpoint {a}:{b}")
                if fused and rational_finals:
                    f_end, f_peak, integral = rational_trace(word, entrance)
                    require(f_end == end and f_peak == peak and integral,
                            f"Fraction terminal trace {a}:{b}")
                    rational_columns += len(entrance)
                contextual += 1
                primitive_steps += len(word)
                peaks.append(peak)
            # Same canonical field schema as the source digest, only for comparison.
            edges.append({"a": a, "b": b, "add": add-child_add, "scale": scale,
                          "peak": max(peaks), "contexts": peaks, "fused": fused})
    return edges, states, {"contextual_executions": contextual,
                          "fraction_terminal_columns": rational_columns,
                          "contextual_instruction_steps": primitive_steps}


def suffix_optimum(edges, k, cap):
    """Bellman recurrence from the terminal endpoint, unlike source prefix DP."""
    outgoing = [[] for _ in range(k)]
    for e in edges:
        require(0 <= e["a"] < e["b"] <= k, "edge domain")
        if e["peak"] <= cap:
            outgoing[e["a"]].append(e)
    suffix = [None] * (k+1)
    suffix[k] = 0
    for a in range(k-1, -1, -1):
        values = [e["add"]+e["scale"]+suffix[e["b"]] for e in outgoing[a]
                  if suffix[e["b"]] is not None]
        if values:
            suffix[a] = min(values)
    return suffix


def expected_endpoint(readers, m, sign=1):
    answer = identity(2+4*m)
    for j in range(2*m):
        for d in range(2):
            answer[2+j][d] += sign * sum(r[d][j] for r in readers)
    return answer


def word_report(word, n):
    _, fw, fw_witness = apply(word, identity(n))
    _, iv, iv_witness = apply(undo(word), identity(n))
    add, scale = bill(word)
    return {"add": add, "scale": scale, "operations": len(word),
            "data_reads": 2*add+scale, "data_writes": len(word),
            "instruction_reads": len(word), "forward_peak": fw,
            "inverse_peak": iv, "peak": max(fw, iv),
            "forward_witness": fw_witness, "inverse_witness": iv_witness}
