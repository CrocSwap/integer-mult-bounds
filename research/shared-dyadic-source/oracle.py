"""Independent interpreters; no constructor or predecessor code imports.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
ADDRESS arithmetic is rational/modular; VALUE arithmetic is over F2.
"""
from collections import Counter
from fractions import Fraction


class CheckError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CheckError(message)


def integer(value):
    return type(value) is int


def validate_word(word, outputs, shared=None):
    require(isinstance(word, list), "word must be a list")
    for event in word:
        require(isinstance(event, list) and len(event) == 3, "bad event shape")
        op, row, argument = event
        require(integer(row) and integer(argument), "event arguments must be integers, not Boolean")
        if op == "Q":
            require(0 <= row <= outputs, "query role outside the data rows")
            require(argument != 0 and abs(argument) & (abs(argument) - 1) == 0, "nondyadic query")
            if shared is not None:
                require((row == 0) if shared else (row != 0), "query on a forbidden role")
        elif op == "X":
            require(1 <= row <= outputs and argument == 0, "XOR must read distinct source into output")
        else:
            raise CheckError("unknown event")


def inverse_word(word):
    return [[op, row, -argument if op == "Q" else argument]
            for op, row, argument in reversed(word)]


def laurent(word, rows):
    """One set of (incoming row, integer exponent) monomials per output row."""
    state = [{(row, 0)} for row in range(rows)]
    for op, row, argument in word:
        if op == "Q":
            state[row] = {(source, exponent + argument) for source, exponent in state[row]}
        elif op == "X":
            state[row] ^= state[argument]
        else:
            raise CheckError("unknown Laurent event")
    return state


def wanted_laurent(masks):
    state = [{(row, 0)} for row in range(len(masks) + 2)]
    for row, mask in enumerate(masks, 1):
        for index in mask:
            state[row] ^= {(0, 2 ** index), (0, -(2 ** index))}
    return state


def orbit_replay(word, state, modulus):
    """Bit-packed regular cyclic representation; positive query is a push."""
    mask = (1 << modulus) - 1
    state = list(state)
    for op, row, argument in word:
        if op == "Q":
            shift = argument % modulus
            value = state[row]
            state[row] = ((value << shift) | (value >> (modulus - shift))) & mask
        else:
            state[row] ^= state[argument]
    return state


def orbit_expected(masks, incoming, modulus):
    """Scatter individual source values by the desired formula, without a word."""
    result = list(incoming)
    for address in range(modulus):
        if (incoming[0] >> address) & 1:
            for row, mask in enumerate(masks, 1):
                for index in mask:
                    result[row] ^= 1 << ((address + 2 ** index) % modulus)
                    result[row] ^= 1 << ((address - 2 ** index) % modulus)
    return result


def parse_native(events):
    require(isinstance(events, list), "native program must be a list")
    parsed = []
    for event in events:
        require(isinstance(event, list) and len(event) == 3, "bad native event")
        op, target, payload = event
        require(integer(target) and 0 <= target < 6, "bad native target")
        if op == "C":
            require(target == 0 and integer(payload) and payload == 5, "wrong ordinary child")
            parsed.append((op, target, payload))
            continue
        require(op == "A" and isinstance(payload, list), "bad affine event")
        terms = []
        seen = set()
        for term in payload:
            require(isinstance(term, list) and len(term) == 2, "bad affine term")
            source, coefficient = term
            require(integer(source) and 0 <= source <= target and source not in seen,
                    "unordered or duplicate affine control")
            require(isinstance(coefficient, str), "rational coefficient must be a string")
            value = Fraction(coefficient)
            require(value != 0, "zero coefficient is not canonical")
            require(value.denominator & (value.denominator - 1) == 0, "non-dyadic denominator")
            seen.add(source)
            terms.append((source, value))
        diagonal = dict(terms).get(target, Fraction(0))
        require(diagonal != 0 and abs(diagonal.numerator) & (abs(diagonal.numerator) - 1) == 0,
                "diagonal is not a unit at every odd modulus")
        parsed.append((op, target, terms))
    return parsed


def inverse_native(parsed):
    result = []
    for op, target, payload in reversed(parsed):
        if op == "C":
            result.append((op, target, payload))
        else:
            diagonal = dict(payload)[target]
            result.append((op, target, [(source, 1 / diagonal if source == target else -v / diagonal)
                                       for source, v in payload]))
    return result


def specialize(parsed, modulus):
    require(integer(modulus) and modulus > 1 and modulus % 2 == 1, "only odd moduli are admitted")
    return [(op, target, payload if op == "C" else
             [(source, value.numerator * pow(value.denominator, -1, modulus) % modulus)
              for source, value in payload]) for op, target, payload in parsed]


# Two binary spectator fields are interleaved between the six ordered controls.
FIELDS = (0, 2, 3, 4, 5, 7)


def native_replay(parsed, incoming, modulus=None):
    state = list(incoming)
    for op, target, payload in parsed:
        target = FIELDS[target]
        if op == "C":
            other = FIELDS[payload]
            state[target], state[other] = state[other], state[target]
        else:
            state[target] = sum(value * state[FIELDS[source]] for source, value in payload)
            if modulus is not None:
                state[target] %= modulus
    return state


def native_expected(power, incoming, modulus=None):
    # Derive the rank-one nilpotent action directly, independently of all seven events.
    state = list(incoming)
    a, _, c, d, _, f = [incoming[i] for i in FIELDS]
    coefficient = Fraction(power, 4) if modulus is None else power * pow(4, -1, modulus) % modulus
    delta = coefficient * (a - c - d + f)
    for index, sign in zip(FIELDS, (1, 0, 1, -1, 0, -1)):
        state[index] += sign * delta
        if modulus is not None:
            state[index] %= modulus
    return state


def recount(word, lowerings):
    children = affines = scans = 0
    powers = Counter()
    for op, _, argument in word:
        if op == "X":
            scans += 1
            continue
        powers[str(argument)] += 1
        require(str(argument) in lowerings, "missing paid native lowering")
        events = parse_native(lowerings[str(argument)])
        children += sum(e[0] == "C" for e in events)
        affines += sum(e[0] == "A" for e in events)
    return {"queries": sum(powers.values()), "ordinary_children": children,
            "affine_events": affines, "xor_scans": scans, "extra_full_rows": 0,
            "query_powers": dict(sorted(powers.items(), key=lambda pair: int(pair[0])))}


def incidence_counts(masks):
    # Count starts of occupied integer intervals, independently of the tour constructor.
    union = set().union(*map(set, masks))
    components = sum(j - 1 not in union for j in union)
    separate = sum(2 * len(mask) + sum(j - 1 not in mask for j in mask) for mask in masks)
    return 2 * len(union) + components, separate, 2 * sum(map(len, masks))
