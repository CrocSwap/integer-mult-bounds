"""Check the two-return displacement floor and complete one-pair price."""
import ast
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from math import comb
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/PHYSICAL-BINDING.json": "ade5f8cbb2e30677b1d48d23a1aa270b3d0b72e2504472ab9fdb71d124b075b5",
    "inputs/PROJECTOR.json": "c36cb8d3fae7bccd15566c2f83f2d2bd8abeeb334381cbf3212d5d9b3d965c35",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/signed_child.py": "ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b",
}


def stop(*_):
    raise TimeoutError("45-second exact gate cap")


def tensor_classes(bits):
    return [sum(comb(bits, i) for i in range(j, bits+1, 4)) for j in range(4)]


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(45)
    raw = {p: (ROOT/p).read_bytes() for p in PINS}
    for path, h in PINS.items():
        assert sha256(raw[path]).hexdigest() == h, path
    c = loads(raw["inputs/CALLER.json"])
    b = loads(raw["inputs/PHYSICAL-BINDING.json"])
    p = loads(raw["inputs/PROJECTOR.json"])
    invoice = loads(raw["inputs/R92-PRICE.json"])
    assert b["caller_sha256"] == PINS["inputs/CALLER.json"]
    assert b["occurrence_and_geometry"]["ambient"] == c["ambient_rank"] == 145
    assert c["stages"] == 17 and len(c["events"]) == 4783
    assert p["head"] == invoice["head"] and p["caller"] == invoice["caller_head"]
    assert p["inclusive_window"] == [4646,4660] and p["rank"] == 2
    assert [c["events"][i] for i in p["inclusive_window"]] == [["B","IDLE_ONE",36,[17]]] * 2
    ports = c["types"]["B"]["ports"]
    assert ports == [15,17,27,34,35,42,47,55]
    assert list(range(9 + 8 * 16,145)) == list(range(137,145))

    node, = [n for n in ast.parse(raw["inputs/signed_child.py"]).body if isinstance(n,ast.Assign)
             and isinstance(n.targets[0],ast.Name) and n.targets[0].id == "C"]
    gate = ast.literal_eval(node.value)
    for sign, phase in ((1,(1,0)),(-1,(0,1))):
        vector = (1,sign)
        for row, v in zip(gate,vector,strict=True):
            assert tuple(sum(row[j][i]*vector[j] for j in range(2)) for i in range(2)) == tuple(2*v*x for x in phase)
    counts = tensor_classes(8)
    assert counts == [72,64,56,64]
    spectrum = [0] * 4
    for column in range(512):
        # One frozen spectator bit. The low eight Walsh bits carry the body.
        spectrum[(column & 255).bit_count() % 4] += 1
    assert spectrum == [2*n for n in counts]
    rank = 512 - spectrum[0]
    required = Fraction(2*rank,512)
    assert rank == 368 and required == Fraction(23,16)
    assert Fraction(rank,512) < required
    assert sum(spectrum) == 512

    tariff = run_path(str(ROOT/"inputs/pricing.py"))
    k = Fraction(invoice["old_crossing_upper"])
    h8 = tariff["power_bounds"](8,k)
    h16 = tariff["power_bounds"](16,k)
    affordable = (2*h8[0]/h16[1],2*h8[1]/h16[0])
    assert affordable[1] < Fraction(1003,1000) < required
    paid = tariff["cost"]({8:16,16:-8*required},k)
    assert paid[1] < 0
    alarm(0)
    print(dumps({"head":p["head"],"caller":p["caller"],"stage":17,"clocks":p["inclusive_window"],
        "width1_walsh_multiplicities_one_spectator":spectrum,"width1_columns_per_lane":512,
        "width1_rank_per_lane":rank,"width1_rank_both_lanes":2*rank,
        "width1_erased_rank_both_lanes":0,"uniform_volume_lower":required,
        "affordable_rank16_volume":affordable,"raw_gain_interval_upper_model":paid,
        "scope":"physical D17 versus matching identity erasure, one body-dependent core, unchanged body-independent bypass",
        "cases":2,"hard_cap_seconds":45,"pins":PINS},default=str,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
