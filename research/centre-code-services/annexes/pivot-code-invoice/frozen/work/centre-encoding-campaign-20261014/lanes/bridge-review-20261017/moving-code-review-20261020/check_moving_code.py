"""Check the actual constant readers and complete entry words."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from math import lcm
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SELF_PIN = sha256(Path(__file__).read_bytes()).hexdigest()
SOURCE = LANES / "new-core-transfer-20261017/low-displacement-20261020"
SOURCES = {
    "rank30": (SOURCE / "run-normal/RESPONSE-PROGRAM.json",
               "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c", False),
    "rank16": (SOURCE / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
               "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4", True),
    "directions": (
        LANES / "history-encoding/independent-skeleton-20261018/fresh-three-child/FRESH-THREE-CHILD-PROGRAMS.json.gz",
        "b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5", True),
    "actual_data_views": (
        LANES / "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473", False),
    "constant_word_proof": (
        LANES / "native-escape-20261017/rational-code-admission-20261020/CENTRE-CONSTANTS.md",
        "d231301931e0877825b9ff3b4005dff865268d6e0557e8f8e05766375543e86a", False),
    "entry_code_proof": (
        LANES / "coherent-port/section-entry-20261020/SECTION.md",
        "8b1eaa55da0ce4b15d1618f0fa7279977be2fb59f86cfbd31604b071795b44ea", False),
    "rank30_code": (
        LANES / "coherent-port/section-entry-20261020/SECTION.json",
        "23568099ea426947015eca86f7d86742a4758f33327e725b047441daab7c8bd7", False),
    "rank16_code": (
        SOURCE / "pivot-codes/final-normal/PIVOT-CODES.json",
        "49044ce1a2ef7a591084ba344e6d13d16e3e47ea56fd977c8c2218aed6b3a670", False),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def sparse(rows):
    return [{int(j): F(c) for j, c in row.items()} for row in rows]


def clean(row):
    return {j: c for j, c in row.items() if c}


def plus(a, b, scale=F(1)):
    out = dict(a)
    for j, c in b.items():
        out[j] = out.get(j, F(0)) + scale*c
    return clean(out)


def product(a, b):
    out = []
    for row in a:
        result = {}
        for j, c in row.items():
            result = plus(result, b[j], c)
        out.append(result)
    return out


def identity(n):
    return [{i: F(1)} for i in range(n)]


def inverse(a):
    n = len(a)
    rows = [[a[i].get(j, F(0)) for j in range(n)] +
            [F(i == j) for j in range(n)] for i in range(n)]
    determinant = F(1)
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        if pivot != j:
            rows[pivot], rows[j] = rows[j], rows[pivot]
            determinant *= -1
        value = rows[j][j]
        determinant *= value
        rows[j] = [x/value for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                value = rows[i][j]
                rows[i] = [x-value*y for x, y in zip(rows[i], rows[j])]
    return [clean({j: rows[i][n+j] for j in range(n)}) for i in range(n)], determinant


def add(target, source, c):
    return ["ADD", target, source, c.numerator, c.denominator]


def scale(target, c):
    n, d = abs(c.numerator), c.denominator
    need(n & (n-1) == 0 and d & (d-1) == 0, "A dyadic unit scale")
    word = []
    word += [["DOUBLE", target]]*(n.bit_length()-1)
    word += [["HALF", target]]*(d.bit_length()-1)
    if c < 0:
        word.append(["NEGATE", target])
    return word


def reverse_word(word):
    inverse_op = {"DOUBLE": "HALF", "HALF": "DOUBLE",
                  "NEGATE": "NEGATE", "MUL_ODD": "DIV_ODD",
                  "DIV_ODD": "MUL_ODD", "TRANSLATE": "TRANSLATE"}
    result = []
    for gate in reversed(word):
        if gate[0] == "ADD":
            result.append(add(gate[1], gate[2], -F(gate[3], gate[4])))
        else:
            result.append([inverse_op[gate[0]], *gate[1:]])
    return result


def b_word(rank, b):
    word = []
    if rank == 30:
        for i in range(0, 16, 2):
            x, y = 112+i, 113+i
            word.append(add(y, x, F(-1)))
            word.append(["MUL_ODD", x, 3])
            word.append(add(x, y, F(-1)))
            word += [["DOUBLE", y], ["NEGATE", x], ["NEGATE", y]]
        for i in range(16, rank):
            need(b[i] == {i: b[i][i]}, "The small block is scalar")
            odd = int(-b[i][i])
            need(odd in (3, 5), "Actual odd clique size")
            word += [["MUL_ODD", 112+i, odd], ["NEGATE", 112+i]]
    else:
        need(rank == 16, "The rank16 word")
        for i in range(rank):
            if i < 8:
                word.append(["MUL_ODD", 112+i, 3])
                word += scale(112+i, F(-2))
            else:
                word += scale(112+i, F(-8))
    return word


def apply_gate(state, gate):
    op, target = gate[:2]
    if op == "ADD":
        state[target] = plus(state[target], state[gate[2]], F(gate[3], gate[4]))
    elif op == "TRANSLATE":
        state[target] = {(field, g ^ gate[2]): c for (field, g), c in state[target].items()}
    else:
        factors = {"DOUBLE": F(2), "HALF": F(1, 2), "NEGATE": F(-1)}
        if op == "MUL_ODD":
            c = F(gate[2])
        elif op == "DIV_ODD":
            c = F(1, gate[2])
        else:
            c = factors[op]
        state[target] = {j: c*x for j, x in state[target].items()}


def word_invoice(word):
    scalar = 0
    odd = Counter()
    maps = 0
    for gate in word:
        op = gate[0]
        if op == "ADD":
            c = F(gate[3], gate[4])
            n, d = abs(c.numerator), c.denominator
            need(d & (d-1) == 0, "The ADD word is dyadic")
            scalar += 2*(1+n.bit_length()+n.bit_count()+d.bit_length())
        elif op == "TRANSLATE":
            maps += 1
        elif op in ("MUL_ODD", "DIV_ODD"):
            odd[op+"_"+str(gate[2])] += 1
        else:
            scalar += 2
    return {"dyadic_real_primitives": scalar, "uniform_translation_map_calls": maps,
            "complex_odd_scans": dict(sorted(odd.items())), "literal_opcodes": len(word),
            "owned_array_count": 0, "new_native_children": 0}


def summary_matrix(a):
    return {"nonzero_entries": sum(map(len, a)),
            "denominator_lcm": lcm(*(c.denominator for row in a for c in row.values())),
            "infinity_norm": str(max(sum(map(abs, row.values())) for row in a))}


def gf2_rank(vectors):
    basis = {}
    for x in vectors:
        while x:
            bit = x.bit_length()-1
            if bit in basis:
                x ^= basis[bit]
            else:
                basis[bit] = x
                break
    return len(basis)


def square_code_check(name, payload, u, d, e, centre):
    rank = len(d)
    if name == "rank30":
        code, code_inverse = sparse(payload["C0"]), sparse(payload["C0_inverse"])
        carriers = payload["selected_carriers"]
        minor = [u[p] for p in carriers]
        minor_inverse, det = inverse(minor)
        need(str(det) == payload["minor_determinant"] == "-1/256", "Actual unit minor")
        need(minor_inverse == sparse(payload["minor_inverse"]), "Independent actual minor inverse")
        need(all(c.denominator == 1 for row in minor_inverse for c in row.values()),
             "The minor inverse is integral")
        u_minor_inverse = product(u, minor_inverse)
        expected = []
        carrier_index = {p: j for j, p in enumerate(carriers)}
        for p in range(112):
            if p in carrier_index:
                expected.append(d[carrier_index[p]])
            else:
                expected.append(plus({p: F(1)}, {carriers[j]: -c for j, c in u_minor_inverse[p].items()}))
        need(code == expected, "The normalized section code is the stated physical matrix")
        target = identity(112)
        for i, p in enumerate(carriers):
            target[p] = {carriers[j]: c for j, c in centre[i].items()}
        need(target == sparse(payload["encoded_response"]), "The actual encoded response")
    else:
        code, code_inverse = sparse(payload["code"]), sparse(payload["code_inverse"])
        carriers = payload["pivots"]
        need(len(carriers) == rank and len(set(carriers)) == rank, "Actual sixteen pivots")
        target = identity(112)
        for i, p in enumerate(carriers):
            target[p] = {p: F(-5 if i < 8 else -7)}
        need(target == sparse(payload["diagonal_response"]), "Diagonal action in physical pivot slots")
        for word_name, expected in (("code", code), ("inverse_code", code_inverse)):
            state = identity(112)
            for op, target_field, source_field, coefficient in payload["scalar_words"][word_name]:
                c = F(coefficient)
                if op == "add":
                    state[target_field] = plus(state[target_field], state[source_field], c)
                else:
                    need(op in ("scale", "fixed_multiply", "fixed_divide"), "Actual pivot opcode")
                    if op == "fixed_divide":
                        c = 1/c
                    state[target_field] = {j: c*x for j, x in state[target_field].items()}
            need(state == expected, "Independent pivot word replay: "+word_name)
    need(product(code, code_inverse) == product(code_inverse, code) == identity(112),
         "Both actual square-code inverse orders")
    need(product(product(code, e), code_inverse) == target, "Full C E C^-1 endpoint")
    return {"all_input_columns": 112, "carriers": carriers,
            "code": summary_matrix(code), "inverse": summary_matrix(code_inverse),
            "encoded_response_diagonal": all(set(row) == {i} for i, row in enumerate(target)),
            "literal_pivot_words_checked": name == "rank16",
            "normalized_section_form_checked": name == "rank30"}


def main():
    data = {}
    for name, (path, pin, compressed) in SOURCES.items():
        raw = path.read_bytes()
        if compressed:
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, "Source pin: "+name)
        if path.suffix != ".md":
            data[name] = json.loads(raw)
    q = [row["q"] for row in data["directions"]["transfers"]]
    actual_q = {row["port"]: row["q"] for row in data["actual_data_views"]["entries"] if row["stage"] == 0}
    need(q == [actual_q[i] for i in range(112)], "All actual directions")
    results, programs = {}, {}
    for name in ("rank30", "rank16"):
        model = data[name].get("model", data[name])
        u, v = sparse(model["correction_U"]), sparse(model["correction_V"])
        e, ei = sparse(model["response"]), sparse(model["response_inverse"])
        r = len(v)
        need(len(u) == len(e) == len(ei) == 112, "Actual array dimensions")
        uv = product(u, v)
        need(e == [plus(row, {i: F(1)}) for i, row in enumerate(uv)], "E=I+UV")
        need(product(e, ei) == product(ei, e) == identity(112), "Actual E inverse in both orders")
        b = product(v, u)
        bi, determinant_b = inverse(b)
        need(product(b, bi) == product(bi, b) == identity(r), "B0 inverse in both orders")
        m = [plus(row, {i: F(1)}) for i, row in enumerate(b)]
        mi, determinant_m = inverse(m)
        d = product(bi, v)
        need(product(d, u) == identity(r), "D0 U=I")
        if r == 30:
            expected = []
            for i in range(0, 16, 2):
                expected += [{i: F(-4), i+1: F(1)}, {i: F(2), i+1: F(-2)}]
            expected += [{i: F(-len(clique))} for i, clique in enumerate(model["small_cliques"], 16)]
            need(b == expected and determinant_m == 2**25, "Actual rank30 small blocks and determinant")
        else:
            need(b == [{i: F(-6 if i < 8 else -8)} for i in range(16)], "Actual rank16 constant reader")
            need(determinant_m == 35**8, "Rank16 determinant")
        expected_ei = [plus({i: F(1)}, row, F(-1))
                       for i, row in enumerate(product(product(u, mi), v))]
        need(ei == expected_ei, "Actual full inverse agrees with the centre code")
        square_code = square_code_check(name, data[name+"_code"], u, d, e, m)

        bw = b_word(r, b)
        bwi = reverse_word(bw)
        for word, matrix in ((bw, b), (bwi, bi)):
            state = [{(i, 0): F(1)} for i in range(112+r)]
            for gate in word:
                apply_gate(state, gate)
            need(state[:112] == [{(i, 0): F(1)} for i in range(112)], "B0 word does not change data")
            need(state[112:] == [{(112+j, 0): c for j, c in row.items()} for row in matrix],
                 "Actual B0 word matrix")
            for gate in reverse_word(word):
                apply_gate(state, gate)
            need(state == [{(i, 0): F(1)} for i in range(112+r)], "Literal inverse order")

        u_adds = [add(p, 112+j, c) for p, row in enumerate(u) for j, c in sorted(row.items())]
        v_adds = [add(112+i, p, -c) for i, row in enumerate(v) for p, c in sorted(row.items())]
        translations = [["TRANSLATE", p, q[p]] for p in range(112)]
        middle = bw+v_adds+bwi
        word = translations+u_adds+middle+u_adds+[["NEGATE", 112+i] for i in range(r)]+translations
        state = [{(i, 0): F(1)} for i in range(112+r)]
        max_norm, max_odd_height = F(1), {3: 0, 5: 0, 7: 0}
        for gate in word:
            apply_gate(state, gate)
            row = state[gate[1]]
            max_norm = max(max_norm, sum(map(abs, row.values())))
            for c in row.values():
                odd = c.denominator
                while odd % 2 == 0:
                    odd //= 2
                for prime in max_odd_height:
                    height = 0
                    while odd % prime == 0:
                        height += 1
                        odd //= prime
                    max_odd_height[prime] = max(max_odd_height[prime], height)
                need(odd == 1, "No other odd denominator")
        ud = product(u, d)
        expected = []
        for p, row in enumerate(ud):
            out = {(p, 0): F(1)}
            out = plus(out, {(j, q[p] ^ q[j]): -c for j, c in row.items()})
            out = plus(out, {(112+j, q[p]): c for j, c in u[p].items()})
            expected.append(out)
        expected += [{(p, q[p]): c for p, c in row.items()} for row in d]
        need(state == expected, "All arbitrary input columns of the physical entry swap")
        for gate in word:
            apply_gate(state, gate)
        need(state == [{(i, 0): F(1)} for i in range(112+r)], "Two complete entry swaps restore all fields")
        invoice = word_invoice(word)
        need(invoice["dyadic_real_primitives"] == (5076 if r == 30 else 4448), "Exact scalar bill")
        need(invoice["uniform_translation_map_calls"] == 224, "Two complete translation passes")

        # A coefficient check suffices for the free-Q identities:
        # D_out J_out = B^-1 V Q^-1 Q U and
        # J_out B D_out = Q (U B B^-1 V) Q^-1.
        need(product(product(u, b), d) == uv, "Exact output correction coefficients")
        need(product(m, mi) == product(mi, m) == identity(r), "Centre response inverse")
        obstruction = []
        if r == 16:
            for i, clique in enumerate(model["small_cliques"]):
                lines = [q[p] for p in clique]
                chi = next(x for x in range(512)
                           if sum(1-2*((x & line).bit_count() % 2) for line in lines) == 0)
                obstruction.append({"clique": i, "ports": clique, "direction_rank": gf2_rank(lines),
                                    "zero_character": chi,
                                    "signs": [1-2*((chi & line).bit_count() % 2) for line in lines]})
                need(gf2_rank(lines) == 8, "Each actual even clique has independent directions")
        serial = lambda a: [{str(j): str(c) for j, c in sorted(row.items())} for row in a]
        programs[name] = {"B0": serial(b), "B0_inverse": serial(bi), "D0": serial(d),
                          "centre_response": serial(m), "centre_response_inverse": serial(mi),
                          "B0_word": bw, "B0_inverse_word": bwi, "entry_word": word,
                          "layout": {"data": [0, 111], "centres": [112, 111+r]},
                          "scalar_endpoint": "((I-U D0)a+Uz,D0a)",
                          "physical_endpoint": "((I-L U D0 L)a+L Uz,D0 L a)"}
        results[name] = {
            "correction_rank": r, "arbitrary_input_fields": 112+r,
            "B0_determinant": str(determinant_b), "centre_determinant": str(determinant_m),
            "B0_inverse": summary_matrix(bi), "D0": summary_matrix(d),
            "centre_response_inverse": summary_matrix(mi),
            "entry_invoice": invoice, "middle_shear_invoice": word_invoice(middle),
            "max_atomic_opcode_prefix_row_norm": str(max_norm),
            "max_atomic_opcode_prefix_odd_height": max_odd_height,
            "old_phase_section_singular_witnesses": obstruction,
            "physical_translation_group_ring_replay": True,
            "both_literal_B0_inverse_orders": True,
            "both_entry_swap_applications_restore_all_inputs": True,
            "square_code": square_code,
        }
    raw = (json.dumps(programs, sort_keys=True, separators=(",", ":"))+"\n").encode()
    (HERE/"MOVING-CODE-PROGRAM.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    need(sha256(Path(__file__).read_bytes()).hexdigest() == SELF_PIN, "Checker stayed fixed")
    receipt = {
        "status": "PASS_INDEPENDENT_MOVING_CODE",
        "checker_sha256": SELF_PIN,
        "source_pins": {name: {"path": str(path), "sha256": pin, "decompressed": compressed}
                        for name, (path, pin, compressed) in SOURCES.items()},
        "results": results,
        "code_cycle_Q_exponents": [[0, 2], [3, 3], [2, 0], [1, 1], [0, 2]],
        "program_decompressed_sha256": sha256(raw).hexdigest(),
        "scope": "Actual matrices, complete arbitrary-input entry words, and all-width algebra. The native phase premise, productive centre lifetime, legal global routes, odd-grid admission, and complete recursive cost remain separate.",
    }
    (HERE/"CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(receipt["status"])
    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
