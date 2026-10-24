"""Check binary ranks for a growing even-subspace Walsh frame."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json


def require(value, message):
    if not value:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def rank(columns):
    pivots = {}
    for value in columns:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def even_projection(value, width):
    omega = (1 << width) - 1
    local = value & omega
    return local ^ (omega if parity(local) else 0)


def walsh(state, width):
    x, z = state
    delta = even_projection(x ^ z, width)
    return x ^ delta, z ^ delta


def c_line(state, label, power=1):
    x, z = state
    return x ^ (label if (power & 1) and parity(label & z) else 0), z


def route_vector(value, label, stage):
    if stage == 0:
        return value
    zero = next(i for i in range(9) if not (label >> i) & 1)
    v = label ^ (1 << zero)
    basis = []
    for i in range(9):
        point = 1 << i
        if zero and (point & 1) != ((point >> zero) & 1):
            point ^= 1 | (1 << zero)
        basis.append(point ^ (v if parity(point & v) else 0))
    require(basis[0] == label, "The port basis does not begin at its label.")
    offset = 9 + 8 * (stage - 1)
    result = value & ~(511 | (255 << offset))
    if parity(value & label):
        result ^= label
    for i, point in enumerate(basis[1:]):
        if parity(value & point):
            result ^= 1 << (offset + i)
        if (value >> (offset + i)) & 1:
            result ^= point
    return result


def route(state, label, stage):
    return tuple(route_vector(value, label, stage) for value in state)


def native_rank(operation, width):
    return rank([operation((0, 1 << i))[0] for i in range(width)])


def main():
    source = Path(__file__).resolve().parents[1] / "lanes/circuit-interface/INTERFACE.json"
    raw = source.read_bytes()
    data = json.loads(raw)
    labels = data["ports"]
    require(len(labels) == 112, "The old port count has changed.")
    require(all(parity(q) for q in labels), "A source label is even.")
    records = []
    for stage in range(1, 9):
        current = 9 + 8 * stage
        previous = current - 8
        omega = (1 << current) - 1
        old_omega = (1 << previous) - 1
        for label in labels:
            for bit in range(current):
                vector = 1 << bit
                require(even_projection(even_projection(vector, current), previous) ==
                        even_projection(vector, previous), "The projections do not nest.")
                for state in ((vector, 0), (0, vector)):
                    require(walsh(route(state, label, stage), current) ==
                            route(walsh(state, current), label, stage),
                            "The growing Walsh frame does not commute with the route.")
        def cross(state, label, power):
            state = walsh(state, previous)
            state = route(state, label, stage - 1)
            state = route(state, label, stage)
            state = c_line(state, label, power)
            return walsh(state, current)
        cross_ranks = {str(power): dict(Counter(native_rank(
            lambda state, label=label: cross(state, label, power), current)
            for label in labels)) for power in (0, 1, 2, 3)}
        transition_ranks = {}
        typed_cross_ranks = {}
        for before in range(2):
            for after in range(2):
                def transition(state):
                    state = c_line(state, old_omega, before)
                    state = walsh(state, previous)
                    state = walsh(state, current)
                    return c_line(state, omega, after)
                transition_ranks[f"{before}->{after}"] = native_rank(transition, current)
                def typed_cross(state, label):
                    state = c_line(state, old_omega, before)
                    state = cross(state, label, 1)
                    return c_line(state, omega, after)
                typed_cross_ranks[f"{before}->{after}"] = dict(Counter(native_rank(
                    lambda state, label=label: typed_cross(state, label), current)
                    for label in labels))
        records.append({"stage": stage, "width": current,
                        "cross_ranks": cross_ranks,
                        "frame_transition_ranks": transition_ranks,
                        "typed_cross_ranks": typed_cross_ranks})
    final_ranks = {}
    for phase in range(2):
        final_ranks[str(phase)] = native_rank(
            lambda state: c_line(walsh(state, 73), (1 << 73) - 1, phase), 73)
    result = {"status": "PASS_BINARY_GROWING_WALSH_GEOMETRY",
              "source_sha256": sha256(raw).hexdigest(), "source_base": data["base"],
              "records": records, "final_frame_ranks": final_ranks,
              "scope": "Exact binary ranks and commutation only. Full phases, native lowering, arbitrary-mode closure, and a supplier invoice remain separate checks."}
    Path(__file__).with_name("GROWING-WALSH.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
