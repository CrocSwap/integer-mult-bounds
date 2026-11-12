# SPDX-License-Identifier: Apache-2.0
"""Exact timed carrier and return-restoration checks on the #7404 sources."""

from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys

HERE = Path(__file__).resolve().parent
PORT = (0, 112, 772, 882)
CARRIER_CLOCKS = (32194, 32641, 32643, 32691, 35131, 36593, 36597, 38599)
READOUT_CHARTS = (0, 249, 251, 128, 245, 1091, 260)
REPAIR_CHARTS = (140, 150)
PINS = {
    "RESULT.json": "eba0ebfac85759cc9c884b3a12237975ff487c76b17f6095949e80d2fbca60fc",
    "verify.py": "94b60998d375a943ce3823abd7fbbae679f07885231d0e9542d386fcf0ec090d",
    "inputs/WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}


def read_pinned(name):
    data = (HERE / name).read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError("changed predecessor input " + name)
    return data


def add_entry(row, key, value):
    total = row.get(key, 0) + value
    if total:
        row[key] = total
    else:
        row.pop(key, None)


def add_scaled(row, values, factor):
    for i, value in values.items():
        add_entry(row, i, factor * value)


def collect_observations(word):
    """Record each available value on creation, entry or write to a live row."""
    live = dict(enumerate(word["initial"]))
    observations = {chart: [] for chart in READOUT_CHARTS + REPAIR_CHARTS}
    for role, chart in live.items():
        if chart in observations:
            observations[chart].append((0, role))
    for clock, (op, role, *args) in enumerate(word["program"]):
        if op == "MOVE":
            assert live[role] == args[0]
            live[role] = args[1]
        elif op == "INIT":
            assert role not in live
            live[role] = args[0]
        elif op == "CLEAR":
            del live[role]
        if live.get(role) in observations:
            observations[live[role]].append((clock + 1, role))
    assert [len(observations[c]) for c in observations] == [10, 16, 8, 10, 78, 296, 29, 10, 9]
    return observations


def reverse_rows(tape, observations, routes, n, walk):
    rows = {}
    for chart, bank in observations.items():
        rows[chart] = []
        for cut, r in bank:
            row, _ = walk(tape[:cut], {r: Q(1)}, reverse=True)
            row = {j: x for j, x in row.items() if j < n}
            for j, (clock, carrier) in enumerate(routes):
                if clock < cut:
                    contribution, _ = walk(tape[clock+1:cut], {r: Q(1)}, reverse=True)
                    if carrier in contribution:
                        row[n+j] = contribution[carrier]
            rows[chart].append(row)
    return rows


def forward(program, observations, starts, injections):
    """Check the reverse receipt with a separate chronological column walk."""
    snapshots = {}
    clock_roles = {}
    for cut, role in observations:
        clock_roles.setdefault(cut, set()).add(role)
    state = dict(starts)
    guards = []
    for clock in range(len(program) + 1):
        for role in clock_roles.get(clock, ()):
            snapshots[clock, role] = state.get(role, 0)
        if clock == len(program):
            break
        op, d, *args = program[clock]
        if clock in injections:
            r, a = injections[clock]
            assert op == "MOVE" and d == r
            add_entry(state, r, a)
        if op == "ADD":
            s, factor = args[:2]
            if s in state:
                add_entry(state, d, Q(factor) * state[s])
        elif op == "SCALE":
            if d in state:
                state[d] *= Q(args[0])
        elif op == "COPY":
            assert args[1] == "1"
            if state.get(d):
                guards.append(clock)
            state.pop(d, None)
            add_entry(state, d, state.get(args[0], 0))
        elif op in ("INIT", "CLEAR"):
            state.pop(d, None)
        else:
            assert op == "MOVE"
    return snapshots, state, guards


def reduce_rows(rows, n, grant_port_inputs):
    """Rank of old inputs and of responses modulo their column space."""
    dirty_pivots, response_pivots = {}, {}
    for old in rows:
        row = {k: Q(v) for k, v in old.items() if not grant_port_inputs or k not in PORT}
        while row:
            k = min(row)
            pivots = dirty_pivots if k < n else response_pivots
            if k not in pivots:
                pivots[k] = {i: v/row[k] for i, v in row.items()}
                break
            add_scaled(row, pivots[k], -row[k])
    return len(dirty_pivots), len(response_pivots)


def input_imitation(rows, n):
    """Represent each injected column by original non-port-0 input columns."""
    basis = {}
    used = sorted({j for row in rows for j in row if j < n and j not in PORT})
    for source in used:
        v = {i: row[source] for i, row in enumerate(rows) if source in row}
        form = {source: Q(1)}
        while v:
            k = min(v)
            f = v[k]
            if k not in basis:
                basis[k] = ({i: x/f for i, x in v.items()}, {i: x/f for i, x in form.items()})
                break
            piv, equiv = basis[k]
            add_scaled(v, piv, -f)
            add_scaled(form, equiv, -f)
    witnesses = []
    for j in range(8):
        v = {i: row[n+j] for i, row in enumerate(rows) if n+j in row}
        form = {}
        while v:
            k = min(v)
            f = v[k]
            piv, equiv = basis[k]
            add_scaled(v, piv, -f)
            add_scaled(form, equiv, f)
        witnesses.append(form)
    return witnesses


def inverse_native(word, y):
    """Inverse of the sealed stage endpoint in the native chart-normalized basis."""
    x = {r: Q(c) for r, c in y.items()}
    pairs = zip(word["hosted"]["X2"], word["hosted"]["Y2"], strict=True)
    second = dict(zip(word["hosted"]["Dports"], pairs, strict=True))
    for i, r in enumerate(word["live"]):
        s = r + 112
        a, b = Q(y.get(r, 0)), Q(y.get(s, 0))
        if i in second:
            x[r], x[s] = a, b-a
            u, v = second[i]
            a, b = Q(y.get(u, 0)), Q(y.get(v, 0))
            x[u], x[v] = a+b, b
        else:
            x[r], x[s] = a/2+b, b-a/2
    return {r: c for r, c in x.items() if c}


def required_minor(receipt, determinant):
    plus, minus = receipt["phase_receipts"][0], receipt["phase_receipts"][2]
    assert plus["q_i_power"] == 0 and not plus["retimed_extra_entries"]
    assert minus["q_i_power"] == 2
    group_a, group_b = receipt["additional_input_aggregates"]
    changes = minus["representative_columns"]

    def coefficient(out, inp):
        result = {(0, 8): -2, (18, 26): 2}.get((out, inp), 0)
        j = str(inp)
        p, k = ("1", group_a[j]) if j in group_a else ("19", group_b[j]) if j in group_b else (j, 1)
        for imaginary, powers, coeff in changes[p].get(str(out), []):
            assert imaginary == 0
            result += k * Q(coeff)   # every body equals one
        return Q(result)

    rr, cc = (0,8,18,19), (8,1,26,19)
    m = [[coefficient(i, j) for j in cc] for i in rr]
    assert determinant(m) == -32
    return {"rows": rr, "columns": cc, "entries": [[str(x) for x in r] for r in m],
            "determinant": "-32", "scope": "q=-1 minus q=+1 at unit bodies"}


def check_paid_egress(word):
    """Independently check full-state input separators for the late exits."""
    moves = [(i, e[1]) for i, e in enumerate(word["program"])
             if i >= 43929 and e[0] == "MOVE" and e[2:4] == [128,127]]
    assert moves == [(45889,819),(46545,870),(49263,48),(49350,100)]
    witness = json.loads((HERE / "EGRESS-DUALS.json").read_bytes())
    assert [(row["clock"], row["carrier"]) for row in witness] == moves
    for case, (clock, role) in zip(witness, moves, strict=True):
        delta = {int(j):Q(v) for j,v in case["unit_witness"].items()}
        assert all(0 <= j < word["public"] and j not in PORT for j in delta)
        assert case["scope"] == "full live state"
        _, after, guards = forward(word["program"][:clock+1], (), delta, {})
        assert not guards and after == {role:1}
        next_event = word["program"][clock+1]
        operands = next_event[1:3] if next_event[0] in ("ADD","COPY") else next_event[1:2]
        assert role in operands and next_event[-1] == 127
    return len(witness)


def main():
    old = json.loads(read_pinned("RESULT.json"))
    read_pinned("verify.py")
    word = json.loads(gzip.decompress(read_pinned("inputs/WORD.json.gz")))
    verify = run_path(str(HERE / "verify.py"))
    routes = [tuple(m[:2]) for m in old["carrier_checks"]["rank_one_central_moves"]]
    assert tuple(c for c,r in routes) == CARRIER_CLOCKS
    assert old["native_role_binding"] == {"0":112,"8":0,"18":772,"26":882}
    program = word["program"]
    n = word["public"]
    assert n == 1501
    observation_banks = collect_observations(word)
    rows = reverse_rows(list(enumerate(program)), observation_banks, routes, n, verify["walk"])
    all_sites = {site for bank in observation_banks.values() for site in bank}

    terminal = []
    for j, (clock, carrier) in enumerate(routes):
        a, y, guards = forward(program, all_sites, {}, {clock: (carrier, Q(1))})
        assert not guards
        for c in observation_banks:
            assert [a[site] for site in observation_banks[c]] == [r.get(n+j, 0) for r in rows[c]]
        terminal.append(y)

    port_responses = [{r: str(y[r]) for r in PORT if r in y} for y in terminal]
    assert port_responses == [{}, {112:"1"}, {}, {112:"1"}, {}, {}, {}, {}]

    union = [row for c in READOUT_CHARTS for row in rows[c]]
    assert len(union) == 447
    assert reduce_rows(union,n,False) == (80,0)
    assert reduce_rows(union,n,True) == (76,1)
    assert reduce_rows(rows[0],n,True) == (4,0)

    late = {}
    for cut, r, scale in [(43790,112,-2),(43791,48,1),(43929,100,1)]:
        i = observation_banks[128].index((cut,r))
        add_scaled(late,rows[128][i],scale)
    assert late == {0: -2, 112: -2, n+1: -2, n+3: -2}
    assert reduce_rows(rows[128],n,True) == (4,1)

    repair = {}
    for c,r in [(140,125),(150,137)]:
        # Verify by actual forward imitations, not solely rank comparison.
        d = input_imitation(rows[c],n)
        for j, imitate in enumerate(d):
            a, y, guards = forward(program, observation_banks[c], imitate, {})
            assert not guards
            assert [a[site] for site in observation_banks[c]] == [x.get(n+j,0) for x in rows[c]]
            assert y.get(r,0) == terminal[j].get(r,0)
        assert word["final"][r] == c and r not in PORT
        assert r in [role for _,role in observation_banks[c]]
        repair[c] = {"observations": len(rows[c]),"protected_return": r,
                     "clean_rank":0,
                     "carrier_column_imitations": [{i:str(x) for i,x in a.items()} for a in d],
                     "return_response": [str(a.get(r,0)) for a in terminal]}
    assert [terminal[j].get(125,0)+terminal[j].get(137,0) for j in range(8)] == [0,1,0,1,0,0,0,0]

    # The allowed common-chart entrance compensation for carrier 225.
    clock, role = routes[1]
    assert (clock,role) == (32641,225)
    assert program[clock] == ["MOVE",225,3,0,False]
    restored = inverse_native(word,terminal[1])
    _, natural, guards = forward(program, (), restored, {})
    assert natural == terminal[1] and not guards
    assert restored.pop(112) == 1
    assert len(restored) == 395 and all(word["initial"][r] == 3 for r in restored)
    pre = {r:-x for r,x in restored.items()}
    _, actual, guards = forward(program, (), pre, {clock:(role,Q(1))})
    _, control, guard2 = forward(program, (), {112:Q(1)}, {})
    assert actual == control == {112: 1} and not guards and not guard2
    # A weakened restoration leaving one protected input uncorrected must fail.
    bad = dict(pre)
    removed = min(bad)
    del bad[removed]
    _, weakened, _ = forward(program, (), bad, {clock:(role,Q(1))})
    assert weakened != control and removed not in PORT
    check_paid_egress(word)
    return {"source_hashes":PINS,"carriers":routes,
            "readout_banks":[{"chart":c,"observations":len(rows[c]),
                              "rank_original":reduce_rows(rows[c],n,False)[0],
                              "extra_responses":reduce_rows(rows[c],n,True)[1]} for c in READOUT_CHARTS],
            "union_readout":{"observations":len(union),"original_rank":80,
                             "extra_responses_all_original_dirty":0,
                             "extra_responses_granting_port_inputs":1,
                             "chart128_functional":{j:str(v) for j,v in late.items()}},
            "chart_local_return_checks":repair, "native_port_0_terminal_responses":port_responses,
            "chart3_entrance_layout":{"carrier":(clock,role),"ordinary_entrance_adds":len(pre),
                "entrance_coefficients":{r:str(v) for r,v in pre.items()},
                "return_effect":{"112":"1"},"equals_add_at_112_entrance":True,
                "omitted_compensation_control":removed},
            "required_phase_difference":required_minor(old,verify["determinant"])}


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Run this exact check with assertions enabled")
    result = json.dumps(main(), indent=2, sort_keys=True)+"\n"
    if sys.argv[1:] == ["--emit"]:
        print(result,end="")
    elif not sys.argv[1:]:
        assert (HERE/"TEMPORAL-RESULT.json").read_text() == result, "receipt changed"
        print("PASS 466 timed observations, two return obstructions, coframed entrance restoration, and four late exit witnesses")
    else:
        raise SystemExit("usage: verify_temporal.py [--emit]")
