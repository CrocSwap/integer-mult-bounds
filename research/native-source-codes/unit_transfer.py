"""Build the backward unit transfer and its forward companion.

The source factor order is part of each literal word. All new native
copies occur at the inherited input or the complete physical exit.
Research used OpenAI Codex under the user's direction.
"""

from fractions import Fraction as Q
from hashlib import sha256
import json


CERTIFICATE_SHA256 = "6f9a382f600e74fa5b20b458097a0038405028156fc49eec3366e8e52de7ebbe"


def load_certificate(directory):
    raw = (directory / "unit-transfer-certificate.json").read_bytes()
    if sha256(raw).hexdigest() != CERTIFICATE_SHA256:
        raise ValueError("The unit-transfer certificate changed")
    return json.loads(raw)


def matrices(data, certificate, base):
    R = data["R"]
    A, T = certificate["compensation_ports"], certificate["query_ports"]
    K = [{k: row[p] / 4 for k, row in enumerate(R) if p in row} for p in range(112)]
    P = [row.copy() if p in A else {} for p, row in enumerate(K)]
    L = [{p: value for p, value in row.items() if p in T} for row in R]
    query = [row.copy() for row in R]
    for k, row in enumerate(L):
        base.add(query[k], row, -1)
    small = base.product(R, K)
    for k, row in enumerate(small):
        base.add(row, {k: Q(1)}, -1)
    Z = [row.copy() for row in K]
    for p, row in enumerate(base.product(P, small)):
        base.add(Z[p], row, -1)
    G, inverse = [{p: Q(1)} for p in range(112)], [{p: Q(1)} for p in range(112)]
    for target, left, right, sign in ((G, Z, query, 1), (G, P, R, -1),
                                      (inverse, P, L, 1), (inverse, Z, R, -1)):
        for p, row in enumerate(base.product(left, right)):
            base.add(target[p], row, sign)
    correction = base.product(data["J"], G)
    for p, row in enumerate(correction):
        base.add(row, {p: Q(1)}, -1)
    return {"R": R, "K": K, "P": P, "L": L, "Q": query, "Z": Z,
            "G": G, "G_inverse": inverse, "JG_minus_I": correction}


def source_word(matrices, bank, frame, inverse, base):
    query, Z = matrices["Q"], matrices["Z"]
    logger = []
    for k, row in enumerate(query):
        logger.append(["scalar", ["clear", ["C", 0]], frame])
        logger += [base.scalar_add(["C", 0], ["L", bank + p], value, frame)
                   for p, value in sorted(row.items())]
        logger += [base.scalar_add(["L", bank + p], ["C", 0], (-1 if inverse else 1) * row[k], frame)
                   for p, row in enumerate(Z) if k in row]
        logger.append(["scalar", ["clear", ["C", 0]], frame])
    selected = [base.scalar_add(["L", bank + p], ["L", bank + j], -value, frame)
                for p, row in enumerate(base.product(matrices["P"], matrices["L"]))
                for j, value in sorted(row.items())]
    if inverse:
        selected = [["scalar", [gate[0], gate[1], gate[2], -gate[3], gate[4]], common]
                    for _, gate, common in reversed(selected)]
        return selected + logger
    return logger + selected


def produce(data, certificate, base):
    word = data["word"]
    values = matrices(data, certificate, base)
    A, full = certificate["compensation_ports"], word["final"][0]
    backward_input = [["phase", "unit_transfer_selected_input_correction"]]
    forward_output = [["phase", "unit_transfer_selected_exit_correction"]]
    for p in A:
        label, entry, hole = word["ports"][p], word["start"][p], word["final"][112 + p]
        row = values["JG_minus_I"][p]
        backward_input.append(["scalar", ["clear", ["C", 0]], 0])
        backward_input += [base.scalar_add(["C", 0], ["L", 112 + j], value)
                           for j, value in sorted(row.items())]
        backward_input.append(["unit_transfer_input_line", p, label, 0, entry, 1])
        backward_input.append(base.scalar_add(["L", p], ["C", 0], 1, entry))
        backward_input.append(["scalar", ["clear", ["C", 0]], 0])
        forward_output.append(["scalar", ["clear", ["C", 0]], full])
        forward_output += [base.scalar_add(["C", 0], ["L", j], -value, full)
                           for j, value in sorted(row.items())]
        forward_output.append(["unit_transfer_exit_line", p, label, -1, full, hole, 1])
        forward_output.append(base.scalar_add(["L", 112 + p], ["C", 0], 1, hole))
        forward_output.append(["scalar", ["clear", ["C", 0]], 0])
    source = source_word(values, 112, 0, False, base)
    inverse_source = source_word(values, 112, 0, True, base)
    exit_source = source_word(values, 0, full, True, base)
    backward = backward_input + [["phase", "unit_transfer_source_G"]] + source + data["clean_programs"]["backward"]
    forward = data["clean_programs"]["forward"] + [["phase", "unit_transfer_source_G_inverse"]] + exit_source + forward_output
    return {"schema": "finite-order-unit-transfers-v1", "certificate_sha256": CERTIFICATE_SHA256,
            "matrices": {name: base.serial(rows) for name, rows in values.items()},
            "blocks": {"backward_input": backward_input, "source_G": source,
                       "source_G_inverse": inverse_source, "forward_source": exit_source,
                       "forward_output": forward_output},
            "programs": {"backward": backward, "forward": forward}}
