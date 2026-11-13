"""Exact physical, native forward and signed ordinary replay for the chart115 cancellation."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import modules, stderr, version_info
from time import perf_counter
from types import ModuleType

PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "independent/engines/clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "independent/engines/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "independent/engines/audit_native.py": "c7d81ad6620de5e46abf97259f62da0138b58a02759c3189e57b8ab176db6bd5",
}
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CAP_SECONDS = 360
DELETIONS = {36448, 38004}
CONTACTS = {
    36448: ["ADD", 1276, 751, "-1", 3],
    38002: ["MOVE", 1276, 3, 115, False],
    38003: ["MOVE", 751, 3, 115, False],
    38004: ["ADD", 1276, 751, "1", 115],
}
FWD_ADAPTATIONS = (
    ("2**24", "2**25"),
    ("25 - (abs(value) & -abs(value)).bit_length()", "26 - (abs(value) & -abs(value)).bit_length()"),
)


def emit(**record):
    print(dumps(record, sort_keys=True), flush=True)


def check_and_build(word):
    assert len(word["program"]) == 76475 and word["public"] == len(word["initial"]) == 1501
    roles = {751, 1276}
    found = {i: e for i, e in enumerate(word["program"])
             if e[1] in roles or e[0] in ("ADD", "COPY") and e[2] in roles}
    assert found == CONTACTS
    protected = set(word["live"]) | {r + 112 for r in word["live"]}
    protected |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(protected) == 400 and roles.isdisjoint(protected)
    assert all(word["initial"][r] == 3 and word["final"][r] == 115 for r in roles)
    assert word["frames"][3] == [] and len(word["frames"][115]) == 5
    old = list(enumerate(word["program"]))
    edited = [(i, e) for i, e in old if i not in DELETIONS]
    return old, edited


def module(name, path):
    spec = spec_from_file_location(name, path)
    obj = module_from_spec(spec)
    modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def physical(root, word):
    c = module("chart115_compiler", root / "independent/engines/clifford_exact.py")
    v = module("chart115_interpreter", root / "independent/engines/native_verify.py")
    a, b = (c.canonical_frame(9, tuple(word["frames"][r])) for r in (3, 115))
    recipe, _ = c.lower_child(a.adjoint().then(b))
    actual = v.recipe(recipe)
    expected = v.adjoint(v.frame(word["frames"][3], 9)) + v.frame(word["frames"][115], 9)
    assert recipe["rank"] == 5
    v.equal(actual, expected, "chart3→115 signed action and exact phase")
    adj_actual, adj_expected = v.adjoint(actual), v.adjoint(expected)
    for column in range(512):
        assert v.state(actual, column) == v.state(expected, column), ("forward", column)
        assert v.state(adj_actual, column) == v.state(adj_expected, column), ("adjoint", column)
    bad = deepcopy(recipe)
    bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
    try:
        v.equal(v.recipe(bad), expected, "one phase step")
    except ValueError as exc:
        assert "exact global phase" in str(exc)
    else:
        raise AssertionError("one-phase-step mutant accepted")
    return {"chart_pair": [3, 115], "move_clocks": [38002, 38003], "rank": recipe["rank"],
            "forward_columns": 512, "adjoint_columns": 512, "phase_mutant_rejected": True,
            "recipe_sha256": sha256(dumps(recipe, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}


def forward(root, word, old, edited, pinned_audit):
    path = root / "independent/engines/audit_native.py"
    source = pinned_audit.decode()
    for find, replace in FWD_ADAPTATIONS:
        assert source.count(find) == 1
        source = source.replace(find, replace)
    obj = ModuleType("chart115_grid_forward")
    obj.__file__ = str(path)
    exec(compile(source, str(path), "exec"), obj.__dict__)
    old_state, old_grid = obj.replay(word, old, set())
    print("PASS_PINNED_OLD_FORWARD_GRID", file=stderr, flush=True)
    new_state, new_grid = obj.replay(word, edited, set())
    assert old_state == new_state
    rows, _, clear, copy, lifetimes, moves = new_state
    assert len(clear) == len(lifetimes) == 74 and len(copy) == 1
    assert all(old_grid[k] == new_grid[k] for k in old_grid if k != "opcodes")
    assert old_grid["opcodes"] - new_grid["opcodes"] == {"ADD": 2}
    assert not new_grid["opcodes"] - old_grid["opcodes"]
    assert new_grid["odd_grid_lcm"] == 1125 and new_grid["dyadic_height"] == 25
    assert new_grid["owned_peak"] == 50 and new_grid["owned_rise_mass"] == 56
    assert sum(new_grid["paid"].values()) == 6279
    unit = 1125 * 2**25
    target = [{r: unit} if r < word["public"] else {} for r in range(len(rows))]
    hosted = word["hosted"]
    dports = set(hosted["Dports"])
    for i, x in enumerate(word["live"]):
        y = x + 112
        if i in dports:
            target[y][x] = unit
        else:
            target[x][y] = -unit
            target[y] = {x: unit // 2, y: unit // 2}
    for x, y in zip(hosted["X2"], hosted["Y2"], strict=True):
        target[x][y] = -unit
    assert rows == target and len(rows) == word["public"] + word["owned_fields"]
    return {"all_rows": len(rows), "owned_clear_rows": len(clear), "copy_guards": len(copy),
            "owned_move_ledger": len(moves), "native_grid": new_grid,
            "adapted_audit_sha256": sha256(source.encode()).hexdigest()}


def scalar_cost(value, additive):
    q = Q(value)
    a, d = abs(q.numerator), q.denominator
    return 4 * (a.bit_length() + d.bit_length() + 1 + (a.bit_count() if additive else 0))


def ordinary(word, events, caller, inventory):
    calls = sum(e[0] == "J" for e in caller["events"])
    assert calls == caller["stages"] == 17
    ports_a = len(caller["types"]["A"]["ports"])
    ports = sum(len(t["ports"]) for t in caller["types"].values())
    scalar = sum(scalar_cost(e[-2], e[0] != "SCALE") for _, e in events if e[0] in ("ADD", "COPY", "SCALE"))
    routing = 1000 * (sum(inventory["paid"].values()) + 2 * (word["public"] - 400)
                      + 6 * (ports + ports_a) + 4 * inventory["owned_lifetimes"])
    signed = caller["events"]
    caller_cost = 0
    terms = {}
    for name, ty in caller["types"].items():
        p, roles = len(ty["ports"]), ty["roles"]
        envelope = 32 * roles * p * sum(e[0] in (name, "J") for e in signed)
        query = [e for e in signed if e[:2] == [name, "QUERY"]]
        idle = [e for e in signed if e[:2] == [name, "IDLE_ONE"]]
        lam = sum(e[:2] == [name, "LAMBDA"] for e in signed)
        fused = sum(e[:2] == [name, "IDLE_ODD"] for e in signed)

        def swaps(axes):
            return len(set(axes) - set(range(len(axes))))

        output_routes = 0
        for qp, _, *mask in ty["diagonal"]:
            axes = ([0] if qp else []) + [a for k, bit in enumerate(mask) if bit for a in range(9 + 8*k, 17 + 8*k)]
            output_routes += p * 1000 * (2 * swaps(axes) + 2 * bool(qp) + (qp == -1))
        idle_routes = sum(2 * p * 1000 * swaps([a for k in e[3] for a in range(1 + 8*k, 9 + 8*k)]) for e in idle)
        query_routes = sum(p * 1000 * (2 + (e[4] == -1)) for e in query)
        caller_scalars = p * sum(scalar_cost(e[-1], e[1] == "ADD") for e in signed
                                 if e[0] == name and e[1] in ("ADD", "SCALE"))
        subtotal = (envelope + 16 * p * len(query) + 26 * roles * p + output_routes + idle_routes
                    + query_routes + 36500 * p * fused + 1000 * p * lam + caller_scalars)
        terms[name] = subtotal
        caller_cost += subtotal
    # Inherited signed exact-grid receipt has minimal odd exponents (3,2).
    signed_odd_scale = 3**3 * 5**2
    conversions = 2 * sum(t["roles"] * len(t["ports"]) for t in caller["types"].values())
    caller_odd = conversions * 4 * (signed_odd_scale.bit_length() + 1 + signed_odd_scale.bit_count())
    input_conversion = calls * len(word["initial"]) * 104
    total = calls * (scalar + routing) + caller_cost + caller_odd + input_conversion
    return {"scalar_per_native_call": scalar, "routing_per_native_call": routing,
            "caller_by_type": terms, "caller_odd_conversions": caller_odd,
            "native_input_conversions": input_conversion, "conservative_total": total}


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("replay_root", type=Path)
    args = parser.parse_args()
    root = args.replay_root.resolve()
    started = perf_counter()
    completed = []

    def on_cap(_signal, _frame):
        emit(status="CAP", completed=completed, cap_seconds=CAP_SECONDS, seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP_SECONDS)
    data = {p: (root / p).read_bytes() for p in PINS}
    assert {p: sha256(raw).hexdigest() for p, raw in data.items()} == PINS
    canonical = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(canonical).hexdigest() == NATIVE
    word = loads(canonical)
    app = loads(data["inputs/7481-APPLICATION.json"])
    caller = loads(data["inputs/7113-CALLER.json"])
    assert app["candidate_canonical_sha256"] == NATIVE
    assert app["caller_head"] == CALLER and app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    old, edited = check_and_build(word)
    physics = physical(root, word)
    completed.append("all signed physical columns and phase mutant")
    print("PASS_CHART115_ALL_PHYSICAL_COLUMNS", file=stderr, flush=True)
    inventory = forward(root, word, old, edited, data["independent/engines/audit_native.py"])
    completed.append("complete native forward/grid/owner equality")
    print("PASS_CHART115_COMPLETE_FORWARD_GRID", file=stderr, flush=True)
    old_ordinary, new_ordinary = (ordinary(word, es, caller, inventory["native_grid"]) for es in (old, edited))
    assert old_ordinary["conservative_total"] == app["ordinary_bound"] == 782785912
    assert old_ordinary["conservative_total"] - new_ordinary["conservative_total"] == 544
    assert old_ordinary["scalar_per_native_call"] - new_ordinary["scalar_per_native_call"] == 32
    completed.append("complete reconstructed ordinary source-unit upper bill")
    new_word = dict(word, program=[e for _, e in edited])
    new_sha = sha256(dumps(new_word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    emit(status="PASS_CHART115_PHYSICAL_FORWARD_ORDINARY", completed=completed, physical=physics,
         forward=inventory, ordinary_original=old_ordinary, ordinary_edited=new_ordinary, ordinary_saved=544,
         canonical_candidate_sha256=new_sha, caller_head=CALLER, pins=PINS,
         cap_seconds=CAP_SECONDS, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
