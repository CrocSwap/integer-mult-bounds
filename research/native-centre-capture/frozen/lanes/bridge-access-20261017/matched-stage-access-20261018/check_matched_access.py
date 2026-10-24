"""Check the actual matching response in complete supplier stage views."""

from collections import Counter, defaultdict
import ast
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "matching": ("controller-followthrough-20261017/matched-involution-20261018/MATCHED-INVOLUTION-PROGRAM.json", "plain", "e2443eee2a7081ce3b57b9b7afcf4f1b061b9d8ddf0fbbeb5f7b29ce0d148902"),
    "permutation64": ("history-encoding/permutation64-native-20261018/PERMUTATION64-PROGRAMS.json.gz", "gzip", "87c76a500f8e22e4b500a5f5a64f23ef8cecadd0036785d7f54b2415972f1ff9"),
    "views": ("bridge-access-20261017/BRIDGE-PROGRAMS.json.gz", "compressed", "1da2f6a6058661f19e971bb31f1823585f01c2494dca813e208af45aea7a582f"),
    "phase": ("bridge-access-20261017/cycle-cover-response-20261018/check_cycle_cover.py", "python", "cf39b15752fcb96cc22b9013dce38e13a4399d99b30dc9f53eef788d5ded2bf4"),
    "scalar_price": ("new-core-transfer-20261017/emit_raw_selected.py", "source", "a07cf4894a2599993006c7b99e6cb62146ece82f2ae6df72a28100ccb3a689bc"),
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def load():
    data = {}
    for name, (rel, kind, pin) in PINS.items():
        raw = (LANES / rel).read_bytes()
        if kind == "gzip":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, name + " source pin")
        if kind == "python":
            spec = importlib.util.spec_from_file_location("matched_access_phase", LANES / rel)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            base, ports = module.load()
        elif kind != "source":
            data[name] = json.loads(gzip.decompress(raw) if kind == "compressed" else raw)
    return base, ports, data


def rows(matrix):
    return [{int(j): F(c) for j, c in row.items() if F(c)} for row in matrix]


def product(a, b):
    result = []
    for row in a:
        out = defaultdict(F)
        for j, c in row.items():
            for k, d in b[j].items():
                out[k] += c * d
        result.append({j: c for j, c in out.items() if c})
    return result


def inverse_word(word):
    return [[op, p, q, str(-F(c))] if op == "add" else [op, p, q, str(1 / F(c))]
            for op, p, q, c in reversed(word)]


def scale(word, p, c):
    if c != 1:
        word.append(["scale", p, p, str(c)])


def swap(word, p, r, sign=1):
    word += [["add", p, r, "1"], ["add", r, p, "-1"], ["add", p, r, "1"]]
    scale(word, r, F(-1))
    scale(word, p, F(sign))
    scale(word, r, F(sign))


def pair_word(source):
    word = []
    for pair in source["pair_codes"]:
        p, r = pair["ports"]
        a, b = map(F, pair["matrix"][0])
        c, d = map(F, pair["matrix"][1])
        need(d == -c * b / a and abs(a) == abs(b) == abs(c) == 1, "Signed pair code")
        scale(word, p, a)
        scale(word, r, b)
        word += [["add", p, r, "1"], ["scale", r, r, "-2"], ["add", r, p, "1"]]
        scale(word, r, c / a)
        need([source["modes"][j]["carrier"] for j in pair["mode_ids"]] == [p, r], "Mode carrier order")
    return word


def scalar_word(source, permutation):
    pre = pair_word(source)
    word = list(pre)
    for vertex in source["vertex_matchings"]:
        for pair in vertex["matching_pairs"]:
            p, r = [source["modes"][j]["carrier"] for j in pair["modes"]]
            swap(word, p, r, pair["weight"])
    word += inverse_word(pre)
    for p, r in sorted((int(p), int(r)) for p, r in permutation["partner"].items() if int(p) < int(r)):
        swap(word, p, r, -1)
    return word


def replay(word, target):
    state = [{p: F(1)} for p in range(112)]
    peak = F(1)
    price = 0
    census = Counter()
    for op, p, r, raw in word:
        c = F(raw)
        a, b = abs(c.numerator), c.denominator
        need(b & (b - 1) == 0, "Dyadic scalar")
        if op == "add":
            need(p != r, "Distinct scalar rows")
            out = defaultdict(F, state[p])
            for j, d in state[r].items():
                out[j] += c * d
            state[p] = {j: d for j, d in out.items() if d}
            price += 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)
        else:
            need(op == "scale" and a & (a - 1) == 0, "Dyadic unit scale")
            state[p] = {j: c * d for j, d in state[p].items()}
            price += 2 * (abs(a.bit_length() - b.bit_length()) + int(c < 0))
        census[op] += 1
        peak = max(peak, sum(abs(c) for c in state[p].values()))
    need(state == target, "All 112 scalar input columns")
    return {"events": len(word), "census": dict(census), "real_scalar_primitives": price,
            "peak_row_one_norm": str(peak), "native_children": 0, "owned_fields": 0}


def compose(base, *maps):
    out = list(base.UNIT)
    for item in reversed(maps):
        out = [base.act(item, v) for v in out]
    return out


def main():
    base, ports, data = load()
    q = [p["q"] for p in ports]
    source = data["matching"]
    identity = [{p: F(1)} for p in range(112)]
    matched = rows(source["response"])
    permuted = [dict(row) for row in matched]
    for p in data["permutation64"]["active_ports"]:
        permuted[p] = rows([data["permutation64"]["response"][p]])[0]
    for response in (matched, permuted):
        need(product(response, response) == identity, "Both full response involutions")
        need(all(p not in row for p, row in enumerate(response)), "Every physical diagonal is zero")
    word = scalar_word(source, data["permutation64"])
    invoice = replay(word, permuted)
    need(replay(inverse_word(word), permuted)["native_children"] == 0, "Exact inverse word")
    syntax = ast.parse((LANES / PINS["scalar_price"][0]).read_text())
    price_node = next(node for node in syntax.body if isinstance(node, ast.FunctionDef) and node.name == "core_price")
    price_scope = {"Q": F, "need": need}
    exec(compile(ast.Module(body=[price_node], type_ignores=[]), "pinned_core_price", "exec"), price_scope)
    billed = []
    for op, p, r, raw in word:
        c = F(raw)
        gate = [op, ["D", p]] + ([["D", r]] if op == "add" else []) + [c.numerator, c.denominator]
        billed.append(["scalar", gate, 0])
    need(price_scope["core_price"](billed) == invoice["real_scalar_primitives"], "Pinned source scalar invoice")
    views = {(v["stage"], v["port"], v["side"]): v for v in data["views"]["views"]}
    route = {(s, p): views[s, p, "X"]["route_columns"] for s in range(1, 9) for p in range(112)}
    full = base.product([(e, 1) for e in base.UNIT])
    past_checks = 0
    for s in range(1, 9):
        for p in range(112):
            view = views[s, p, "X"]
            rho, delta = route[s, p], view["translation_after_route"]
            phase = base.product([(v, 1) for v in rho])
            need(base.add_phase(phase, base.line(delta, 2)) == full, "Literal final-FULL stage view")
            need(base.act(rho, q[p]) == q[p], "Own intrinsic line is fixed")
            past_checks += 1
    reports = {}
    witness = None
    for name, response in (("half_hadamard64", matched), ("permutation64", permuted)):
        stage_rows = []
        for s, t in ((1, 2), (3, 4), (5, 6), (7, 8)):
            grouped = defaultdict(dict)
            count = 0
            for p, row in enumerate(response):
                for j, c in row.items():
                    for r, d in response[j].items():
                        mapping = compose(base, route[s, p], route[s, j], route[t, j], route[t, r])
                        key = tuple(mapping)
                        need(key not in grouped[p, r], "Distinct intermediate ports have distinct owner maps")
                        grouped[p, r][key] = c * d
                        second = base.act(mapping, q[r])
                        fresh = ((1 << 8) - 1) << (9 + 8 * (t - 1))
                        need(second & fresh, "The second intrinsic line has a nonzero future component")
                        need(q[p] != second, "Two distinct positive intrinsic lines")
                        correction = base.add_phase(full, base.negative(base.product([(v, 1) for v in mapping])))
                        need(correction[0] == correction[2] == 0, "FULL cover conjugation is a translation")
                        phase = base.add_phase(base.product([(q[p], 1), (second, 1)]), correction)
                        need(phase[0] == q[p] ^ second, "Full Z4 phase has the required odd mask")
                        count += 1
                        if witness is None:
                            witness = {"stages": [s, t], "target": p, "middle": j, "source": r,
                                       "coefficient": str(c * d), "route_columns": mapping,
                                       "lines": [q[p], second], "FULL_translation": correction[1],
                                       "phase": list(phase)}
            stage_rows.append({"stages": [s, t], "nonzero_path_blocks": count,
                               "output_port_rows": len({p for p, r in grouped}),
                               "port_blocks": len(grouped), "rank_two_path_blocks": count})
        reports[name] = {"local_nonzero_entries": sum(map(len, response)), "stage_pairs": stage_rows}
    a, b = witness["lines"]
    kernel = {0: 1, a: 0, b: 0, a ^ b: 3}
    need(len(kernel) == 4, "Four nonzero one-copy entries")
    expanded = {0: 0}
    support = []
    for width in range(1, 6):
        expanded = {old ^ (v << (73 * (width - 1))): (phase + power) % 4
                    for old, phase in expanded.items() for v, power in kernel.items()}
        need(len(expanded) == 4**width, "Exact tensor support")
        support.append(len(expanded))
    program = {"schema": "matched-final-full-gauge-v1", "source_pins": PINS,
               "response": [{str(j): str(c) for j, c in row.items()} for row in permuted],
               "scalar_word": word, "inverse_scalar_word": inverse_word(word),
               "stage_contract": {"stages": list(range(1, 9)), "completed_level": 8,
                                  "view_source": PINS["views"][0], "view_side": "X",
                                  "order": ["apply_all_literal_stage_views", "scalar_word", "invert_all_literal_stage_views"],
                                  "monomial_view_calls": 224}, "invoice": invoice}
    (HERE / "FULL-GAUGE-PROGRAM.json").write_text(json.dumps(program, sort_keys=True, indent=2) + "\n")
    result = {"status": "PASS_MATCHED_RESPONSE_STAGE_ACCESS", "source_pins": PINS,
              "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "literal_FULL_view_checks": past_checks, "terminal_upper_blocks": reports,
              "witness": witness, "tensor_support": support, "FULL_gauge_invoice": invoice,
              "scope": "Exact specified responses and raw phase operator. No full supplier or general native lower bound."}
    (HERE / "CHECKS.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
