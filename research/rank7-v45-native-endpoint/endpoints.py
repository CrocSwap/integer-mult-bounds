# SPDX-License-Identifier: Apache-2.0
"""Pull back two output covectors without replaying the producer's state rows."""

from fractions import Fraction

HELPER = 249
PRIVATE = 704 + HELPER
DUAL = 1_000_000
MAX_GATES = 20_000
MAX_TERMS = 4096
MAX_WORD = 64
MAX_TOTAL_TERMS = 16_384


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def append_word(left, right):
    out = list(left)
    require(len(left) + len(right) <= MAX_WORD, "operator word bound")
    for op in right:
        require(type(op) is int and op != 0, "signed operator")
        if out and out[-1] == -op:
            out.pop()
        else:
            out.append(op)
    return tuple(out)


def accumulate(target, source, coefficient, operators=()):
    for word, value in tuple(source.items()):
        key = append_word(word, operators)
        result = target.get(key, Fraction(0)) + coefficient * value
        if result:
            target[key] = result
        else:
            target.pop(key, None)
    require(len(target) <= MAX_TERMS, "covector term bound")


def dual_operator(op):
    require(0 < abs(op) < DUAL, "original operator range")
    return (1 if op > 0 else -1) * (abs(op) + DUAL)


def pull_gate(rows, gate, dual):
    tag, target = gate[:2]
    if tag == "warp":
        op = dual_operator(gate[2]) if dual else gate[2]
        replacement = {}
        accumulate(replacement, rows[target], Fraction(1), (op,))
        rows[target] = replacement
    elif tag == "scale":
        coefficient = Fraction(gate[2], gate[3])
        require(coefficient != 0, "nonzero scale")
        if dual:
            coefficient = 1 / coefficient
        rows[target] = {w: coefficient * q for w, q in rows[target].items()}
    elif tag in ("add", "corr"):
        source = gate[2]
        require(target != source, "distinct shear registers")
        coefficient = Fraction(gate[3], gate[4])
        operators = () if tag == "add" else tuple(gate[5])
        if dual:
            operators = tuple(-dual_operator(op) for op in reversed(operators))
            target, source, coefficient = source, target, -coefficient
        accumulate(rows[source], rows[target], coefficient, operators)
    else:
        raise ValueError("unknown covector gate")


def program(word):
    require(
        (word["report"]["v"], word["report"]["h"], word["report"]["R"])
        == (112, 9, 480),
        "word geometry",
    )
    result = []
    for correction in word["initial_corrections"]:
        q = Fraction(correction["coefficient"])
        result.append(
            [
                "corr",
                correction["target"],
                correction["source"],
                q.numerator,
                q.denominator,
                correction["operator_word"],
            ]
        )
    for section in ("precondition", "compensation", "A", "cut"):
        require(len(word[section]) <= 10_000, "section bound")
        result.extend(word[section])
    require(len(word["warps"]) <= 480, "warp count bound")
    by_position = {}
    for index, warp in enumerate(word["warps"], 1):
        position, lender = warp[:2]
        require(0 <= position <= len(word["B"]), "warp position")
        by_position.setdefault(position, []).append(["warp", lender, index])
    require(len(word["B"]) <= 10_000, "B length bound")
    for position in range(len(word["B"]) + 1):
        result.extend(by_position.get(position, []))
        if position < len(word["B"]):
            result.append(word["B"][position])
    for section in ("restore", "cleanup"):
        require(len(word[section]) <= 10_000, "section bound")
        result.extend(word[section])
    require(len(result) <= MAX_GATES, "program length bound")
    return result


def endpoint(gates, output, dual, live, buffers):
    rows = [{} for _ in range(1408)]
    rows[output] = {(): Fraction(1)}
    allowed = live | buffers
    total_terms = 1
    for gate in reversed(gates):
        regs = gate[1:3] if gate[0] in ("add", "corr") else gate[1:2]
        require(all(type(r) is int and r in allowed for r in regs), "legal register")
        before = sum(len(rows[r]) for r in regs)
        pull_gate(rows, gate, dual)
        total_terms += sum(len(rows[r]) for r in regs) - before
        require(0 <= total_terms <= MAX_TOTAL_TERMS, "total covector capacity")
    return [
        (r, word, str(q))
        for r in sorted(allowed)
        for word, q in sorted(rows[r].items())
    ]


def check(word):
    require(
        len(word["removed"]) == len(set(word["removed"])) == 72,
        "removed helper inventory",
    )
    live = set(range(704)) - set(word["removed"])
    require(len(live) == 632, "632 arbitrary original inputs")
    require(len(word["helper_final"]) == 91, "91 private buffers")
    buffers = {704 + int(r) for r in word["helper_final"]}
    require(HELPER in live and PRIVATE in buffers, "chosen helper and private buffer")
    gates = program(word)
    result = {}
    for dual in (False, True):
        helper = endpoint(gates, HELPER, dual, live, buffers)
        private = endpoint(gates, PRIVATE, dual, live, buffers)
        require(helper == [(HELPER, (), "1")], "restored helper endpoint")
        require(private == [(PRIVATE, (), "1")], "private buffer identity endpoint")
        result["inverse_transpose" if dual else "forward"] = {
            "helper_full_input_terms": helper,
            "private_full_input_terms": private,
        }
    return {
        "gates": len(gates),
        "arbitrary_original_inputs": len(live),
        "zero_private_inputs": len(buffers),
        "endpoints": result,
    }


def omission_control(word):
    index = 72
    require(
        word["cleanup"][index][:5] == ["add", 62, PRIVATE, 1, 1],
        "exact private-read control preimage",
    )
    live = set(range(704)) - set(word["removed"])
    buffers = {704 + int(r) for r in word["helper_final"]}
    gates = program(word)
    position = len(gates) - len(word["cleanup"]) + index
    mutant = gates[:position] + gates[position + 1 :]
    terms = {}
    for dual in (False, True):
        row = endpoint(mutant, PRIVATE, dual, live, buffers)
        original = [term for term in row if term[0] in live]
        terms["inverse_transpose" if dual else "forward"] = original
    require(terms["forward"] == [], "omission forward zero-buffer control")
    require(
        [term for term in terms["inverse_transpose"] if term[0] == 11]
        == [(11, (), "-1/2")],
        "omission inverse-transpose original-input11 witness",
    )
    return {
        "cleanup_index": index,
        "omitted_gate": word["cleanup"][index],
        "private_original_input_terms": terms,
    }
