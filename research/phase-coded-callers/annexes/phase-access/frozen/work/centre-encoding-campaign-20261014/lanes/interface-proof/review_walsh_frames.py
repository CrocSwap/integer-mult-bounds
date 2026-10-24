"""Check exact common-line Walsh phases, routes, and native child kernels."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import importlib.util
import json


FIXED_CHARTS = {}


def require(value, message):
    if not value:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def rank(columns):
    pivots = {}
    for column in columns:
        while column:
            bit = column.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = column
                break
            column ^= pivots[bit]
    return len(pivots)


def apply(columns, value):
    result = 0
    for i, column in enumerate(columns):
        if value >> i & 1:
            result ^= column
    return result


def inverse(columns):
    size = len(columns)
    rows = [sum(((column >> i) & 1) << j for j, column in enumerate(columns))
            | (1 << (size + i)) for i in range(size)]
    for i in range(size):
        pivot = next((j for j in range(i, size) if rows[j] >> i & 1), None)
        require(pivot is not None, "Singular address chart")
        rows[i], rows[pivot] = rows[pivot], rows[i]
        for j in range(size):
            if j != i and rows[j] >> i & 1:
                rows[j] ^= rows[i]
    return [sum(((row >> (size+i)) & 1) << j for j, row in enumerate(rows))
            for i in range(size)]


def transpose(columns):
    return [sum(((column >> i) & 1) << j for j, column in enumerate(columns))
            for i in range(len(columns))]


def fixed_walsh(state, common, size):
    key = common, size
    if key not in FIXED_CHARTS:
        chart = [(1 << i) ^ 256 for i in range(8)] + [common]
        chart += [1 << i for i in range(9, size)]
        back = inverse(chart)
        FIXED_CHARTS[key] = chart, back, transpose(chart), transpose(back)
    chart, back, chart_t, back_t = FIXED_CHARTS[key]
    x, z = apply(back, state[0]), apply(chart_t, state[1])
    return (apply(chart, (x & ~255) | (z & 255)),
            apply(back_t, (z & ~255) | (x & 255)))


def growing_walsh(state, size):
    x, z = state
    omega = (1 << size) - 1
    delta = (x ^ z) & omega
    if parity(delta):
        delta ^= omega
    return x ^ delta, z ^ delta


def line(state, label):
    x, z = state
    return x ^ (label if parity(z & label) else 0), z


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def rotate(a, power):
    x, y = a
    return ((x, y), (-y, x), (-x, -y), (y, -x))[power % 4]


def native_coefficients(size):
    powers_a, powers_b = [(1, 0)], [(1, 0)]
    for _ in range(size):
        powers_a.append(multiply(powers_a[-1], (1, 1)))
        powers_b.append(multiply(powers_b[-1], (1, -1)))
    return [multiply(powers_a[size-i], powers_b[i]) for i in range(size+1)]


def endpoint_case(size, x, y, coefficients):
    a, b = parity(x), parity(y)
    exponent = x.bit_count()-a+y.bit_count()-b
    actual = rotate(coefficients[(x ^ y).bit_count()], exponent)
    wanted = (1, 1) if a == b else (1, -1)
    if parity(x & y) ^ (a & b):
        wanted = (-wanted[0], -wanted[1])
    scale = 1 << ((size-1)//2)
    require(actual == (scale*wanted[0], scale*wanted[1]),
            "Exact productive endpoint kernel")


def main():
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("independent_routes", here/"verify_bridge_operators.py")
    routes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(routes)
    source = here.parent/"coherent-port/COVARIANCE.json"
    raw = source.read_bytes()
    pin = "6466d082f376bcbd8f7d953d8a2625f5e31eb164ffa61f430b1cdf6e6ef30b38"
    require(sha256(raw).hexdigest() == pin, "Completed port table pin")
    labels = json.loads(raw)["labels"]
    require(len(labels) == 120 and all(parity(q) for q in labels), "Odd completed ports")
    common = 11
    phase_cases = 0
    for q in labels:
        v = q ^ common
        require(not parity(v), "Even difference from common line")
        for frequency in range(256):
            b = parity(frequency & v)
            original = [(1, 1), (1, -1) if not b else (-1, 1)]
            factored = [rotate((1, 1), b), rotate((1, -1), b)]
            if b:
                factored.reverse()
            require(factored == original, "Common-line exact two-term phase")
            phase_cases += 2
    fixed_records = []
    for first, second in ((0, 0), (1, 1), (1, 0), (2, 1)):
        size = 9+8*max(first, second)
        counts = Counter()
        for q in labels:
            chart = routes.basis(q)
            columns = []
            for i in range(size):
                x, z = fixed_walsh((0, 1 << i), common, size)
                x, z = (routes.route(x, chart, second), routes.route(z, chart, second))
                x, z = (routes.route(x, chart, first), routes.route(z, chart, first))
                columns.append(fixed_walsh(line((x, z), q), common, size)[0])
            counts[rank(columns)] += 1
        require(counts == {1 if first == second else 17: 120}, "Fixed-chart transition rank")
        fixed_records.append({"from_stage": second, "to_stage": first,
                              "rank_histogram": dict(counts)})
    growing_records = []
    for stage in range(1, 9):
        size, previous = 9+8*stage, 1+8*stage
        omega = (1 << size)-1
        counts = [Counter(), Counter()]
        for q in labels:
            chart = routes.basis(q)
            rho = [routes.route(1 << i, chart, stage) for i in range(size)]
            require(apply(rho, omega) == omega, "Current route fixes the common line")
            require(all(parity(a & b) == (i == j)
                        for i, a in enumerate(rho) for j, b in enumerate(rho)),
                    "Current route preserves the exact Walsh kernel")
            for odd in range(2):
                columns = []
                for i in range(size):
                    x, z = growing_walsh((0, 1 << i), previous)
                    x, z = routes.route(x, chart, stage-1), routes.route(z, chart, stage-1)
                    x, z = routes.route(x, chart, stage), routes.route(z, chart, stage)
                    if odd:
                        x, z = line((x, z), q)
                    columns.append(growing_walsh((x, z), size)[0])
                counts[odd][rank(columns)] += 1
        require(counts == [{8: 120}, {9: 120}], "Growing transition ranks")
        growing_records.append({"stage": stage, "width": size,
                                "even_phase_rank": dict(counts[0]),
                                "odd_phase_rank": dict(counts[1])})
    child_cases = []
    for child_size in (8, 9):
        coefficients = native_coefficients(child_size)
        count = 0
        for x in range(1 << child_size):
            bx = (x & 255) ^ (255 if parity(x & 255) else 0)
            moved = bx | (x & 256)
            for y in range(1 << child_size):
                actual = rotate(coefficients[(moved ^ y).bit_count()],
                                bx.bit_count()+(y & 255).bit_count())
                sign = -1 if parity(bx & y) else 1
                wanted = (1, 0) if child_size == 8 else (
                    (1, 1) if not ((x ^ y) & 256) else (1, -1))
                wanted = tuple(16*sign*a for a in wanted)
                require(actual == wanted, "Exact common native child kernel")
                count += 1
        child_cases.append({"rank": child_size, "basis_matrix_entries": count})
    endpoint_records = []
    for size in range(9, 74, 8):
        coefficients = native_coefficients(size)
        if size == 9:
            points = ((x, y) for x in range(512) for y in range(512))
        else:
            points = ((value & ((1 << size)-1), value >> size)
                      for value in routes.phase_points(2*size))
        count = 0
        for x, y in points:
            endpoint_case(size, x, y, coefficients)
            count += 1
        endpoint_records.append({"width": size, "kernel_cases": count,
                                 "complete_quadratic_phase_witness": True})
    report = {
        "status": "PASS_INDEPENDENT_EXACT_WALSH_FRAMES",
        "root_table_sha256": pin,
        "fixed_common_line": common,
        "exact_common_line_coefficients": phase_cases,
        "fixed_chart_transitions": fixed_records,
        "growing_chart_transitions": growing_records,
        "common_native_child_kernels": child_cases,
        "productive_endpoint_kernels": endpoint_records,
        "endpoint_identity": "C_omega G_n = D_n F_n D_n for n=9+8s; D_n(x)=(-1)^sum_(i<j) x_i x_j",
        "tensor_scope": "Exact base operators and phases tensor to every positive lambda",
        "limits": ["No source-dependent mode-content closure",
                   "No owner or scalar controller emission",
                   "Finite monomial maps, source access, and full recursive bill remain open",
                   "The rank-17 result concerns the full operator, not a restriction to a centre image"],
    }
    (here/"WALSH-FRAME-REVIEW.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(report["status"])


if __name__ == "__main__":
    main()
