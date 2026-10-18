# SPDX-License-Identifier: Apache-2.0
"""Decode the selected serialized wrappers and selective climb recipes exactly."""


def dual(circuit):
    result = []
    for gate in circuit:
        kind = gate[0]
        if kind == "C":
            result.append((kind, gate[1], -gate[2]))
        elif kind == "D":
            result.append((kind, gate[1], [(-a) % 4 for a in gate[2]]))
        elif kind == "PH":
            result.append((kind, -gate[1] % 4))
        else:
            if kind not in ("P", "X"):
                raise ValueError("unknown native gate")
            result.append(gate)
    return result


def decode(kernel, recipe):
    if not kernel.well_formed(recipe["left"]) or not kernel.well_formed(recipe["right"]):
        raise ValueError("monomial schema")
    return (kernel.monomial(recipe["right"]) + kernel.fourier(recipe["rank"])
            + kernel.monomial(recipe["left"]))


def check(kernel, recipe, old, new, require):
    require(type(recipe["rank"]) is int and recipe["rank"] == len(new) - len(old),
            "native rank difference")
    actual = decode(kernel, recipe)
    expected = kernel.adjoint(kernel.canonical_frame(old)) + kernel.canonical_frame(new)
    require(kernel.same_operator(actual, expected), "phase-exact native recipe")
    require(kernel.same_operator(dual(actual), dual(expected)), "dual native recipe")
    return actual


def wrappers(kernel, recipe, terminal, require):
    check(kernel, recipe, [], terminal, require)
    # Actual event semantics: pre executes R^-1, post executes L^-1.
    pre = kernel.adjoint(kernel.monomial(recipe["right"]))
    post = kernel.adjoint(kernel.monomial(recipe["left"]))
    middle = kernel.canonical_frame(terminal)
    require(kernel.same_operator(pre + middle + post, kernel.fourier(7)),
            "selected inverse wrappers give F7")
    require(kernel.same_operator(dual(pre + middle + post), kernel.fourier(7, -1)),
            "dual inverse wrappers give inverse F7")
    return {"pre": "inverse of selected right monomial",
            "post": "inverse of selected left monomial", "columns_per_orientation": 512}
