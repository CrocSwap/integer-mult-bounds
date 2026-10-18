# SPDX-License-Identifier: Apache-2.0
"""Bind covered native classes to the actual serialized recipes and exact kernel.

The compiler and packed Gaussian-integer kernel are retained, credited inputs.
This file adds event-to-class binding and expected caller chart compositions.
Substantial OpenAI Codex assistance; no new kernel or full supplier is claimed.
"""
import json


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def conjugate(circuit):
    result = []
    for gate in circuit:
        tag = gate[0]
        if tag == "D":
            result.append((tag, gate[1], [(-a) % 4 for a in gate[2]]))
        elif tag in ("C", "PH"):
            result.append((tag, gate[1], -gate[2]) if tag == "C" else (tag, -gate[1] % 4))
        else:
            require(tag in ("P", "X"), "native conjugate gate")
            result.append(gate)
    return result


def compiled(kernel, record):
    rank = record["rank"]
    require(type(rank) is int and 0 <= rank <= 9, "native rank domain")
    require(kernel.well_formed(record["left"]), "native left monomial schema")
    left = kernel.monomial(record["left"])
    if rank == 0:
        require(record["right"] is None, "rank-zero right side")
        return left
    require(kernel.well_formed(record["right"]), "native right monomial schema")
    return kernel.monomial(record["right"]) + kernel.fourier(rank) + left


def warp(kernel, columns):
    require(type(columns) is list and len(columns) == 9 and
            all(type(x) is int and 0 <= x < 512 for x in columns), "warp matrix domain")
    grow = kernel.transpose(columns)
    gi_columns = kernel.transpose(kernel.f2_inverse(grow))
    q = [(1 << i) ^ sum(kernel.parity(gi_columns[i] & gi_columns[j]) << j
                        for j in range(9)) for i in range(9)]
    alpha = [(q[i] >> i) & 1 for i in range(9)]
    return [("P", grow), ("D", q, alpha)]


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {x ^ vector for x in result}
    require(len(result) <= 512, "native span domain")
    return result


def classes(events, included, canonical):
    frames = canonical["frames"]
    ids = {tuple(f): i for i, f in enumerate(frames)}
    require(len(ids) == len(frames), "unique ordered canonical frames")
    result = {}
    for index in included:
        event, key = events[index], None
        tag = event[0]
        if tag == "climb":
            key = ("child", ids[event[3]], ids[event[4]])
        elif tag == "center":
            key = ("child", ids[event[2]], ids[event[3]])
        elif tag == "warp":
            key = ("warp", 1 if event[2] > 0 else -1, abs(event[2]), ids[event[3]], ids[event[4]])
        elif tag == "residual_adapter":
            key = ("wrapper", ids[event[3]], ids[event[4]] if len(event) == 5 else 1)
        elif tag == "adapter":
            number, f = int(event[2][1:]), ids[event[3]]
            if event[1] == "old_to_new" and number < 112:
                key = ("endpoint", "source", number, f, "direct")
            elif event[1] == "new_to_old" and 112 <= number < 224:
                key = ("endpoint", "target", number - 112, f, "inverse")
            else:
                require((event[1] == "old_to_new" and f == 0) or
                        (event[1] == "new_to_old" and f == 1), "ordinary helper/unused endpoint convention")
                key = ("identity",)
        else:
            require(tag in ("scalar", "zero_buffer"), "covered native event tag")
        if key is not None:
            result.setdefault(key, []).append(index)
    return result


def recipe_maps(recipes):
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    endpoints = {(r["role"], r["port"], r["frame"]): r for r in recipes["endpoint_adapters"]}
    warps = {(r["sign"], r["op"], r["old"], r["new"]): r for r in recipes["warps"]}
    require(len(children) == len(recipes["children"]) and
            len(endpoints) == len(recipes["endpoint_adapters"]) and
            len(warps) == len(recipes["warps"]), "unique native recipe keys")
    return children, endpoints, warps


def selected(kernel, key, canonical, recipes, adapters):
    children, endpoints, warps = recipe_maps(recipes)
    frames = canonical["frames"]
    kind = key[0]
    if kind == "child":
        old, new = key[1:]
        record = children[old, new]
        require(record["rank"] == abs(len(frames[new]) - len(frames[old])), "child rank")
        reference = kernel.adjoint(kernel.canonical_frame(frames[old])) + kernel.canonical_frame(frames[new])
        return compiled(kernel, record), reference, record
    if kind == "warp":
        sign, op, old, new = key[1:]
        table = {w["op"]: w for w in canonical["warps"]}
        record = warps[sign, op, old, new]
        require(record["rank"] == 0 and record["G_columns"] == table[op]["G_columns"], "warp selected source matrix")
        domain, image = (frames[old], frames[new]) if sign > 0 else (frames[new], frames[old])
        grow = kernel.transpose(table[op]["G_columns"])
        require({kernel.apply_rows(grow, x) for x in span(domain)} == span(image), "native warp carries common chart")
        logical = warp(kernel, table[op]["G_columns"])
        if sign < 0:
            logical = kernel.adjoint(logical)
        reference = kernel.adjoint(kernel.canonical_frame(frames[old])) + logical + kernel.canonical_frame(frames[new])
        return compiled(kernel, record), reference, record
    if kind == "endpoint":
        role, port, f, orientation = key[1:]
        record = endpoints[role, port, f]
        q = canonical["ports"][port]
        old = [("C", q, 1)] if role == "source" else [("C", q, -1)] + kernel.fourier(9)
        reference = kernel.adjoint(old) + kernel.canonical_frame(frames[f])
        candidate = compiled(kernel, record)
        require(record["rank"] == 0, "endpoint adapter rank")
        if orientation == "inverse":
            candidate, reference = kernel.adjoint(candidate), kernel.adjoint(reference)
        return candidate, reference, record
    if kind == "identity":
        return [], [], {"implicit_common_boundary_convention": True}
    require(kind == "wrapper", "native class kind")
    entrance, terminal = key[1:]
    label = str(entrance) if terminal == 1 else str(entrance) + ":" + str(terminal)
    record = adapters["recipes"][label]
    require(record["frame"] == entrance and record["vectors"] == frames[entrance], "selected wrapper entrance")
    require((terminal == 1) or (record["terminal"] == terminal and record["terminal_vectors"] == frames[terminal]), "selected wrapper terminal")
    require(record["rank"] == len(frames[terminal]) - len(frames[entrance]), "wrapper width")
    reference = kernel.adjoint(kernel.canonical_frame(frames[entrance])) + kernel.canonical_frame(frames[terminal])
    return compiled(kernel, record), reference, record


def check(kernel, key, canonical, recipes, adapters, backward):
    candidate, reference, record = selected(kernel, key, canonical, recipes, adapters)
    original_reference = reference
    if backward:
        candidate, reference = conjugate(candidate), conjugate(reference)
    require(kernel.same_operator(candidate, reference), "exact native class mismatch " + repr(key))
    if key[0] == "wrapper":
        left, right = kernel.monomial(record["left"]), kernel.monomial(record["right"])
        wrapped = kernel.adjoint(right) + original_reference + kernel.adjoint(left)
        target = kernel.fourier(record["rank"])
        # Form the physical wrapped product first, then conjugate the entire word.
        if backward:
            wrapped = conjugate(wrapped)
            target = conjugate(target)
        require(kernel.same_operator(wrapped, target), "exact wrapped native residual")
    return {"key": list(key), "inverse_transpose": backward, "columns": 512,
            "global_phase_included": True,
            "selected_recipe": record,
            "boundary_convention": "normalized source coordinates; physical cold helper has F7 / inverse F7 after wrappers"}


def stable_key(key):
    return json.dumps(key, separators=(",", ":"))
