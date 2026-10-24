"""Check the complete rank9 contraction with an independent phase interpreter."""

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SELF_PIN = sha256(Path(__file__).read_bytes()).hexdigest()
N = 25
UNIT = tuple(1 << j for j in range(N))
SOURCES = {
    "packet": ("bridge-access-20261017/rank9-completion-20261020/RANK9-PROGRAMS.json.gz",
               "9a8e4f1e34b23f97435ea7d953f1a6e1a1059f88920f314712fa592be52ddaac"),
    "native": ("oblique-native-20261017/matched-native-involution/MATCHED-NATIVE-PROGRAM.json.gz",
               "95f11d2b13fc75cb0d07e79ea17afdf3f46b4aca294117ffe1a988779e99f025"),
    "permutation": ("history-encoding/permutation64-native-20261018/PERMUTATION64-PROGRAMS.json.gz",
                    "87c76a500f8e22e4b500a5f5a64f23ef8cecadd0036785d7f54b2415972f1ff9"),
    "triple": ("bridge-access-20261017/matched-stage-access-20261018/TRIPLE25-PROGRAMS.json.gz",
               "b65a2b14a1e61c566063195d0ef363c7dae0d06bb2232e4c872275479f327419"),
    "views": ("bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
              "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473"),
    "producer_proof": ("bridge-access-20261017/rank9-completion-20261020/RANK9.md",
                       "a9271f13f08a25d48906051216200ed4424c52de2dabde4e7227eceffb49ef99"),
    "controller": ("encoded-controller/one-pair-current-codes-20261018/PROGRAM.json",
                   "f66186f2f67ea00eb8ae6447ec9cbddbdf410f141e61149871b0915e599845d7"),
    "full_gauge": ("independent-review-20261017/matched-full-gauge-20261018/FULL-GAUGE.json",
                   "ea8717a63861b7bc9acc2d8e8b0501503a928859042e453234a2fc0c65797f89"),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def act(rows, x):
    return sum(parity(row & x) << j for j, row in enumerate(rows))


def transpose(rows):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(len(rows)))


def act_columns(columns, x):
    result = 0
    for j, column in enumerate(columns):
        if x >> j & 1:
            result ^= column
    return result


def rank(vectors):
    basis = {}
    for x in vectors:
        while x:
            j = x.bit_length()-1
            if j in basis:
                x ^= basis[j]
            else:
                basis[j] = x
                break
    return len(basis)


@lru_cache(None)
def inverse(rows):
    size = len(rows)
    left, right = list(rows), [1 << j for j in range(size)]
    for j in range(size):
        pivot = next(i for i in range(j, size) if left[i] >> j & 1)
        left[j], left[pivot] = left[pivot], left[j]
        right[j], right[pivot] = right[pivot], right[j]
        for i in range(size):
            if i != j and left[i] >> j & 1:
                left[i] ^= left[j]
                right[i] ^= right[j]
    need(tuple(left) == tuple(1 << j for j in range(size)), "Invertible affine matrix")
    return tuple(right)


def monomial(record):
    if record is None:
        return []
    size = len(record["matrix_rows"])
    need(size in (9, 25), "Declared monomial dimension")
    rows = tuple(record["matrix_rows"]) + UNIT[size:]
    quadratic = tuple(record["quadratic_rows"]) + (0,)*(N-size)
    linear = tuple(record["linear_Z4"]) + (0,)*(N-size)
    need(all(((quadratic[i] >> j) & 1) == ((quadratic[j] >> i) & 1)
             for i in range(N) for j in range(N)), "Symmetric quadratic phase")
    need(all(((quadratic[i] >> i) & 1) == linear[i] % 2 for i in range(N)),
         "Quadratic phase diagonal convention")
    inverse(rows)
    return [("D", quadratic, linear), ("P", rows), ("X", record["offset"]),
            ("PHASE", record["phase"])]


def native(record):
    return (monomial(record["right"]) +
            [("C", 1 << j, 1) for j in range(record["rank"])] +
            monomial(record["left"]))


def adjoint(circuit):
    out = []
    for gate in reversed(circuit):
        tag = gate[0]
        if tag == "P":
            out.append(("P", inverse(gate[1])))
        elif tag == "D":
            out.append(("D", gate[1], tuple((-x) % 4 for x in gate[2])))
        elif tag in ("C", "PHASE"):
            out.append((*gate[:-1], -gate[-1]))
        else:
            need(tag == "X", "Adjoint gate")
            out.append(gate)
    return out


def phase_value(gate, x):
    value = sum(c for j, c in enumerate(gate[2]) if x >> j & 1)
    for j, row in enumerate(gate[1]):
        if x >> j & 1:
            value += 2*parity((row >> (j+1)) & (x >> (j+1)))
    return value % 4


def pauli(circuit, x, z):
    power = 0
    for gate in circuit:
        tag = gate[0]
        if tag == "P":
            x = act(gate[1], x)
            z = act(transpose(inverse(gate[1])), z)
        elif tag == "X":
            power += 2*parity(z & gate[1])
        elif tag == "D":
            power += phase_value(gate, x)
            z ^= act(gate[1], x)
        elif tag == "C":
            if parity(z & gate[1]):
                x ^= gate[1]
                power -= gate[2]
        else:
            need(tag == "PHASE", "Pauli interpreter opcode")
    return x, z, power % 4


def tableau(circuit):
    return ([pauli(circuit, 1 << j, 0) for j in range(N)] +
            [pauli(circuit, 0, 1 << j) for j in range(N)])


def rotate(pair, power):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def state_zero(circuit):
    state, denominator = {0: (1, 0)}, 0
    for gate in circuit:
        tag = gate[0]
        if tag == "C":
            out = {}
            sign, direction = gate[2], gate[1]
            for x, (a, b) in state.items():
                for address, value in ((x, (a-sign*b, b+sign*a)),
                                       (x ^ direction, (a+sign*b, b-sign*a))):
                    old = out.get(address, (0, 0))
                    out[address] = old[0]+value[0], old[1]+value[1]
            state = {x: c for x, c in out.items() if c != (0, 0)}
            denominator += 1
        elif tag == "P":
            state = {act(gate[1], x): c for x, c in state.items()}
        elif tag == "X":
            state = {x ^ gate[1]: c for x, c in state.items()}
        elif tag == "D":
            state = {x: rotate(c, phase_value(gate, x)) for x, c in state.items()}
        else:
            need(tag == "PHASE", "Exact state interpreter opcode")
            state = {x: rotate(c, gate[1]) for x, c in state.items()}
    while denominator and all(a % 2 == b % 2 == 0 for a, b in state.values()):
        state = {x: (a//2, b//2) for x, (a, b) in state.items()}
        denominator -= 1
    return state, denominator


def equal(a, b, label):
    ta, tb = tableau(a), tableau(b)
    need(ta == tb, label+" signed Pauli generators")
    need(state_zero(a) == state_zero(b), label+" exact global phase")
    return ta


def main():
    data = {}
    for name, (relative, pin) in SOURCES.items():
        raw = (LANES/relative).read_bytes()
        if relative.endswith(".gz"):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, "Source pin "+name)
        if not relative.endswith(".md"):
            data[name] = json.loads(raw)
    packet, permutation, triple = data["packet"], data["permutation"], data["triple"]
    need(data["controller"]["program"][-2:] == [["forward", 2], ["code_X", 1, -1]],
         "Only the final X code follows the last forward call")
    final_cut = triple["five_scalar_codes"][-1]
    need(final_cut["cut"] == "after_F2" and final_cut["side"] == "X"
         and final_cut["scalar_gauge_sha256"] == SOURCES["full_gauge"][1],
         "The exact final current-cut gauge")
    for event in data["full_gauge"]["events"]:
        need(event[0] in ("add", "scale") and 0 <= event[1] < 112,
             "The final gauge writes only X fields")
        if event[0] == "add":
            need(0 <= event[2] < 112, "The final gauge reads only X fields")
    views = {(row["stage"], row["port"]): row for row in data["views"]["entries"]}
    q = {p: views[0, p]["q"] for p in range(112)}
    active = set(permutation["active_ports"])
    paths = [row for row in triple["path_records"]["T_inverse"] if row["target"] in active]
    need(len(paths) == 64 and len({row["target"] for row in paths}) == 64, "Unique terminal paths")
    paths = {row["target"]: row for row in paths}
    reports = {}
    for provider in ("base", "extra"):
        word = permutation["providers"][provider]["forward"]
        whole = data["native"]["providers"][provider]["forward"]
        need(whole["events"][whole["inherited_64_first_event"]:] == word["events"], "Literal native suffix")
        adapters = {(row["port"], row["role"]): row for row in word["endpoint_adapters"]}
        records = packet["providers"][provider]
        need(len(records) == 64 and {row["output_port"] for row in records} ==
             {row["source_port"] for row in records} == active, "Full cover source-port bijection")
        checks, coefficients, later_events = 0, 0, 0
        for record in records:
            p, r = record["output_port"], record["source_port"]
            path = paths[p]
            need(path["source"] == r and path["coefficient"] == "-1", "Actual preferred terminal path")
            transfer = next(row for row in word["transfers"] if row["source_port"] == p)
            need(transfer["target_port"] == r, "The final source and target pair")
            position = transfer["event"]+2
            event = word["events"][position]
            need(position == record["removed_native_event"] and event[:2] == ["native", 112+r]
                 and event[4] == 7 and event[5] == record["old_completion_recipe_key"],
                 "Actual removed completion")
            need(event[2] == transfer["frame"], "The target is at the actual source line frame")
            for later in word["events"][position+1:]:
                touched = [later[1]] if later[0] == "native" else later[1][1:3]
                need(112+r not in touched, "No later local target read or write")
                later_events += 1
            completion = word["native_recipes"][event[5]]
            need(completion == whole["native_recipes"][event[5]], "Actual complete-core child recipe")
            source_adapter = native(adapters[p, "source"])
            target_adapter = native(adapters[r, "target"])
            local = native(completion)+adjoint(target_adapter)
            conventional = (adjoint(source_adapter) + [("C", q[p], -1), ("C", q[r], -1)] +
                            [("C", 1 << j, 1) for j in range(9)])
            equal(local, conventional, "Canonical completion")
            complement = record["local_seven_axes"]
            basis = [q[r], q[p]]+complement
            need(len(complement) == 7 and all(x < 512 for x in basis) and
                 all(parity(x & y) == (i == j) for i, x in enumerate(basis) for j, y in enumerate(basis)),
                 "Exact local orthonormal complement")
            delta = record["local_full_translation"]
            for chi in range(512):
                difference = (chi.bit_count()-sum(parity(x & chi) for x in basis)) % 4
                need(difference == 2*parity(delta & chi), "All local full-frame Fourier phases")
            factored = adjoint(source_adapter)+[("C", x, 1) for x in complement]+[("X", delta)]
            equal(local, factored, "Seven-axis local factor")
            route = path["route_columns"]
            rho = views[2, r]["route_columns"]
            composed = [act_columns(route, column) for column in rho]
            need(route == record["terminal_route_columns"] and rho == record["stage2_route_columns"]
                 and composed == record["cover_route_columns"], "Literal owner routes")
            need(rank(composed) == N and all(parity(x & y) == (i == j)
                 for i, x in enumerate(composed) for j, y in enumerate(composed)), "Cover-group owner map")
            exit_shift = views[2, r]["literal_stage_alignment"]["exit_Y"]
            a, b = path["lines"]
            need(a == q[p] and b == act_columns(route, q[r]), "The two terminal lines")
            axes = [a, b]+[act_columns(composed, x) for x in complement]
            tau = path["FULL_translation"] ^ act_columns(route, exit_shift ^ act_columns(rho, delta))
            need(axes == record["native_axes"] and tau == record["output_translation"], "Nine axes and exact shift")
            need(all(parity(x & y) == (i == j) for i, x in enumerate(axes) for j, y in enumerate(axes)),
                 "Nine orthonormal directions")
            actual = (local + [("P", transpose(rho)), ("X", exit_shift), ("X", q[r]),
                              ("P", transpose(route)), ("C", b, -1), ("C", a, 1),
                              ("X", path["FULL_translation"]), ("PHASE", 2)])
            compiled = (monomial(record["right"])+[("C", 1 << j, 1) for j in range(9)] +
                        monomial(record["left"])+[("PHASE", 2)])
            t = equal(actual, compiled, "Complete contraction")
            need(rank([x for x, z, power in t[N:]]) == 9, "Exact Fourier rank")
            need(state_zero(actual) != state_zero(compiled[:-1]), "The negative sign is required")
            wrong_left = dict(record["left"], offset=record["left"]["offset"] ^ 1)
            wrong = monomial(record["right"])+[("C", 1 << j, 1) for j in range(9)]+monomial(wrong_left)
            need(tableau(actual) != tableau(wrong), "A wrong translation is rejected")
            need(record["source_field_before_signed_exchange"] == 112+r
                 and record["source_field_after_signed_exchange"] == r
                 and record["output_field"] == p and record["rank"] == 9
                 and record["sign"] == -1, "Arbitrary-state exchange roles")
            checks += 1
            coefficients += len(state_zero(compiled)[0])
        reports[provider] = {"complete_operator_equalities": checks, "local_operator_equalities": 2*checks,
                             "signed_Pauli_columns": 3*checks*2*N,
                             "exact_state_coefficients_final": coefficients,
                             "local_Fourier_phase_values": checks*512,
                             "later_event_nonaccess_checks": later_events,
                             "wrong_sign_controls": checks, "wrong_translation_controls": checks,
                             "source_and_owner_assignment_bijection": True}
        print(provider, "PASS_INDEPENDENT_RANK9", flush=True)
    before = {int(r): c for r, c in packet["complete_native_profile_before"].items()}
    after = {int(r): c for r, c in packet["complete_native_profile_after"].items()}
    expected = Counter(before)
    expected.subtract({7: 64, 2: 64})
    expected.update({9: 64})
    need(dict(expected) == after and sum(r*c for r, c in before.items()) ==
         sum(r*c for r, c in after.items()) == 5600, "Exact full-profile substitution")
    need(sum(before.values())-sum(after.values()) == 64, "Child count reduction")
    need(packet["new_wrapper_calls"] == 128 and packet["real_sign_primitives"] == 128
         and packet["owned_fields"] == packet["private_fields"] == 0, "Local invoice")
    need(sha256(Path(__file__).read_bytes()).hexdigest() == SELF_PIN, "Fixed checker")
    receipt = {"status": "PASS_INDEPENDENT_RANK9_COMPLETION",
               "checker_sha256": SELF_PIN, "source_pins": SOURCES, "providers": reports,
               "complete_native_profile": after, "native_rank_mass": 5600,
               "child_count": sum(after.values()), "new_monomial_wrappers": 128,
               "new_complex_signs": 64, "unchanged_sign_primitive_price": 128,
               "final_X_only_gauge_checked": True,
               "scope": "Exact local operator and chronology contraction, all widths by tensorization. No rank saving or full finite supplier invoice."}
    (HERE/"CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
