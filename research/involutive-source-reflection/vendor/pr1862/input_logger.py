"""Build four input-only source-code examples.

The matrices come from the pinned local supplier. The certificate fixes
two port sets and the eight exact positive input-line recipes.
Research used OpenAI Codex under the user's direction.
"""

from fractions import Fraction as Q
from hashlib import sha256
import json


CERTIFICATE_SHA256 = "f9ab470df50d7a9f9bc1e03fc0c1d30976c8f45f7bcbc0fb3ee371befdced652"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(target, source, coefficient=1):
    for j, value in source.items():
        value = target.get(j, 0) + coefficient * value
        if value:
            target[j] = value
        else:
            target.pop(j, None)


def product(left, right):
    result = []
    for row in left:
        value = {}
        for j, coefficient in row.items():
            add(value, right[j], coefficient)
        result.append(value)
    return result


def transpose(rows, count):
    result = [{} for _ in range(count)]
    for i, row in enumerate(rows):
        for j, value in row.items():
            result[j][i] = value
    return result


def serial(rows):
    return [{str(j): str(value) for j, value in sorted(row.items())} for row in rows]


def inverse(matrix):
    n = len(matrix)
    rows = [dict(row) | {n + i: Q(1)} for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i].get(j)), None)
        require(pivot is not None, "The source parameter is singular")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        value = rows[j][j]
        rows[j] = {k: coefficient / value for k, coefficient in rows[j].items()}
        for i in range(n):
            if i != j and rows[i].get(j):
                add(rows[i], rows[j], -rows[i][j])
    return [{j - n: value for j, value in row.items() if j >= n} for row in rows]


def admit(parameter, Z):
    require(len(parameter) == 8 and all(set(row) <= set(range(112)) for row in parameter),
            "The source parameter must have eight rows and 112 columns")
    require(all(value.denominator & (value.denominator - 1) == 0
                for row in parameter for value in row.values()), "The source parameter is not dyadic")
    small = product(parameter, Z)
    for k, row in enumerate(small):
        add(row, {k: Q(1)})
    small_inverse = inverse(small)
    require(all(value.denominator & (value.denominator - 1) == 0
                for row in small_inverse for value in row.values()), "The source inverse is not dyadic")
    return small, [{j: -value for j, value in row.items()} for row in product(small_inverse, parameter)]


def load_certificate(directory):
    raw = (directory / "certificate.json").read_bytes()
    require(sha256(raw).hexdigest() == CERTIFICATE_SHA256, "The fixed input certificate changed")
    return json.loads(raw)


def matrices(data, certificate):
    R = data["R"]
    alpha = Q(certificate["alpha"])
    compensation_ports, query_ports = set(certificate["compensation_ports"]), set(certificate["query_ports"])
    K = [{k: value / 4 for k, value in row.items()} for row in transpose(R, 112)]
    Z = [{k: value * (2 - alpha if p in compensation_ports else 1) for k, value in row.items()}
         for p, row in enumerate(K)]
    query = [{p: value for p, value in row.items() if p not in query_ports} for row in R]
    return K, Z, query, product(data["J"], Z)


def scalar_add(target, source, coefficient, frame=0):
    coefficient = Q(coefficient)
    require(coefficient != 0, "A zero ADD is not emitted")
    return ["scalar", ["add", target, source, coefficient.numerator, coefficient.denominator], frame]


def read_source(row, buffer=0):
    return [["scalar", ["clear", ["C", buffer]], 0]] + [
        scalar_add(["C", buffer], ["L", 112 + j], value) for j, value in sorted(row.items())]


def preparation(name, parameter, Z, JZ, streamed):
    """Use C0 for compensation, then one or eight source snapshots."""
    small, _ = admit(parameter, Z)
    if streamed:
        require(all(set(row) <= {k} for k, row in enumerate(small)),
                "A streamed source parameter has a non-diagonal response")
    compensation = product(JZ, parameter)
    target_events = [["phase", name + "_target"]]
    for p, row in enumerate(compensation):
        if not row:
            continue
        target_events += read_source(row)
        target_events.append(["input_private_C", 0, p, 1])
        target_events.append(scalar_add(["L", p], ["C", 0], 1, ["input_C", p]))
        target_events.append(["scalar", ["clear", ["C", 0]], 0])
    source_events = [["phase", name + ("_source" if streamed else "_snapshot")]]
    if not streamed:
        for k, row in enumerate(parameter):
            source_events += read_source(row, k)
        source_events.append(["phase", name + "_source"])
    for k, column in enumerate(transpose(Z, 8)):
        buffer = 0 if streamed else k
        if streamed:
            source_events += read_source(parameter[k])
        source_events += [scalar_add(["L", 112 + p], ["C", buffer], value)
                          for p, value in sorted(column.items())]
        source_events.append(["scalar", ["clear", ["C", buffer]], 0])
    return target_events, source_events


def produce(data, certificate):
    K, Z, query, JZ = matrices(data, certificate)
    mixed = [row.copy() for row in data["R"]]
    add(mixed[1], data["R"][0])
    _, mixed_inverse = admit(mixed, Z)
    parameters = {"query_log": (query, True),
                  "query_unlog": ([{j: -value for j, value in row.items()} for row in query], True),
                  "non_diagonal": (mixed, False), "non_diagonal_inverse": (mixed_inverse, False)}
    examples = {}
    for name, (parameter, streamed) in parameters.items():
        target_events, source_events = preparation("input_only_" + name, parameter, Z, JZ, streamed)
        prelude = target_events + source_events
        examples[name] = {"B_rows": serial(parameter), "streamed": streamed, "input_compensation": target_events,
                          "source_update": source_events, "prelude": prelude,
                          "program": prelude + data["clean_programs"]["backward"]}
    return {"schema": "input-only-source-code-programs-v1", "certificate_sha256": CERTIFICATE_SHA256,
            "K_rows": serial(K), "Z_rows": serial(Z), "query_rows": serial(query),
            "JZ_rows": serial(JZ), "examples": examples}
