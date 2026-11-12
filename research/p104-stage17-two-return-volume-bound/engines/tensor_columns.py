"""Reconstruct a physical-body displacement and the necessary field volume."""
import ast
import json
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/7113-SHA256.json": "064e11ecfedce9937ea1782e5baee37e89b3c9eebabed5b4a9ba84f412bbe078",
    "inputs/7113-signed-child.py": "ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b",
    "inputs/7113-application.py": "d98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184",
    "inputs/7397-PROOF.md": "1b5f670a1fd044b92905639b2cfb81eaf71c1dcdf63c114b73d2841919c58e32",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PORTS = [15, 17, 27, 34, 35, 42, 47, 55]
CLOCKS = [4646, 4660]
ROLES = [36, 37, 52, 53]
EIGENVALUE = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def read(name):
    content = (HERE / name).read_bytes()
    if sha256(content).hexdigest() != PINS[name]:
        raise ValueError(f"changed source {name}")
    return content


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col, strict=True)) for col in zip(*b)] for row in a]


def matadd(a, b):
    return [[x+y for x, y in zip(r, s, strict=True)] for r, s in zip(a, b, strict=True)]


def product(a, b):
    x, y = a
    u, v = b
    return x*u-y*v, x*v+y*u


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def caller_projector(caller):
    assert caller["types"]["B"]["ports"] == PORTS
    tape = caller["events"]
    assert len(tape) == 4783
    assert tape[CLOCKS[0]] == tape[CLOCKS[1]] == ["B", "IDLE_ONE", 36, [17]]
    interior = tape[CLOCKS[0]+1:CLOCKS[1]]
    assert len(interior) == 13
    ident = [[Q(i == j) for j in range(4)] for i in range(4)]

    def transform(events, invert):
        a = [row[:] for row in ident]
        for kind, op, dst, *args in events:
            assert kind == "B"
            j = ROLES.index(dst)
            if op == "ADD":
                k = ROLES.index(args[0])
                q = Q(args[1]) * (-1 if invert else 1)
                a[j] = [x+q*y for x, y in zip(a[j], a[k], strict=True)]
            else:
                assert op == "SCALE"
                q = Q(args[0])
                a[j] = [x/q if invert else x*q for x in a[j]]
        return a

    m = transform(interior, False)
    inv = transform(reversed(interior), True)
    assert mm(inv, m) == mm(m, inv) == ident
    e = [[Q(i == j == 0) for j in range(4)] for i in range(4)]
    f = mm(mm(inv, e), m)
    zero = [[Q(0) for _ in range(4)] for _ in range(4)]
    assert mm(e, f) == mm(f, e) == zero
    p = matadd(e, f)
    assert mm(p, p) == p and sum(p[i][i] for i in range(4)) == 2
    assert mm(e, e) != zero
    return p


def tensor_numerator(column, axes, gate):
    out = column[:]
    for axis in axes:
        for j in range(len(out)):
            if j & axis:
                continue
            k = j | axis
            u, v = out[j], out[k]
            out[j] = add(product(gate[0][0], u), product(gate[0][1], v))
            out[k] = add(product(gate[1][0], u), product(gate[1][1], v))
    return out


def physical_response(gate):
    # The ninth bit is an unchanged spectator. All 512 columns form a
    # Walsh basis on this literal C^8 tensor slice.
    axes = tuple(1 << i for i in range(8))
    phases = [0]*4
    for c in range(512):
        erased = [((-1)**((r & c).bit_count() & 1), 0) for r in range(512)]
        actual = tensor_numerator(erased, axes, gate)
        phase = (c & 255).bit_count() % 4
        phases[phase] += 1
        eigen = tuple(256*v for v in EIGENVALUE[phase])
        assert actual == [product(eigen, x) for x in erased]
    assert phases == [144, 128, 112, 128]
    # Negative control. Omit one paid axis on its Walsh minus direction.
    omitted = [((-1)**((r & 128).bit_count() & 1), 0) for r in range(512)]
    assert tensor_numerator(omitted, axes[:-1], gate) != [
        product((0, 128), x) for x in omitted
    ]
    return phases


def stop(*_):
    raise TimeoutError("45-second response cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(45)
    body = ast.parse(read("inputs/7113-signed-child.py"))
    gate, = [ast.literal_eval(node.value) for node in body.body
             if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "C" for t in node.targets)]
    assert gate == (((1, 1), (1, -1)), ((1, -1), (1, 1)))
    sources = json.loads(read("inputs/7113-SHA256.json"))
    assert sources["replay/supplier7112/short-caller/signed_child.py"] == PINS["inputs/7113-signed-child.py"]
    assert sources["replay/supplier7112/short-caller/upstream_application.py"] == PINS["inputs/7113-application.py"]
    assert sources["expected/ODD-TYPE-AB-CALLER.json"] == PINS["inputs/CALLER.json"]
    application = read("inputs/7113-application.py").decode()
    assert "body = terms((1 << j, 1) for j in range(9+8*(stage-1), 9+8*stage))" in application
    assert "rank = 8*len(selected); idle_uses += len(kind['ports'])" in application
    caller = json.loads(read("inputs/CALLER.json"))
    p = caller_projector(caller)

    # Diagonalize the identical responses on each of the two independent
    # active lanes. Direct sums add ranks on arbitrary dirty inputs.
    phases = physical_response(gate)
    modes = 512
    one_lane_rank = modes - phases[0]
    finite_rank = 2*one_lane_rank
    assert phases == [2*sum(comb(8, k) for k in range(j, 9, 4)) for j in range(4)]
    floor = 2*(Q(3, 4)-Q(1, 2**5))
    assert Q(finite_rank, modes) == floor == Q(23, 16)

    old = json.loads(read("inputs/R92-PRICE.json"))
    assert old["head"] == HEAD and old["caller_head"] == CALLER
    read("inputs/pricing.py")
    q = run_path(str(HERE/"inputs/pricing.py"))
    assert b"volume-linear new charge" in read("inputs/7397-PROOF.md")
    k = Q(old["old_crossing_upper"])
    h8, h16 = (q["power_bounds"](r, k) for r in (8, 16))
    affordable = 2*h8[1]/h16[0]
    raw_upper = 8*(2*h8[1]-floor*h16[0])
    assert affordable < Q(1003, 1000) < floor
    assert raw_upper < -55
    canonical_floor = floor/(Q(3, 4)+Q(1, 2**9))
    assert canonical_floor == Q(736, 385)
    alarm(0)
    print(json.dumps({
        "benchmark": HEAD, "caller": CALLER, "stage": 17, "ports": PORTS,
        "clocks": CLOCKS, "physical_stage_axes": list(range(137, 145)),
        "scope": "unchanged identity-erased bypass; one field; volume-linear tariff",
        "pins": PINS, "projector": [[str(x) for x in row] for row in p],
        "tested_responses": ["literal physical D17", "fixed erased I"],
        "basis_columns_per_lane": modes, "lane_count": 2,
        "eigenphase_counts_per_lane": phases,
        "one_lane_displacement_rank": one_lane_rank,
        "combined_displacement_rank": finite_rank,
        "volume_lower_all_widths": str(floor),
        "rank16_affordability_upper": str(affordable),
        "eight_port_raw_delta_upper": str(raw_upper),
        "rank16_canonical_fourth_root_phase_volume_lower": str(canonical_floor),
        "negative_controls": ["duplicate projector has nonzero product", "omitted body axis fails on Walsh minus input"],
        "runner_cap_seconds": 45,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
