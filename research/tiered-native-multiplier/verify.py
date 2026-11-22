"""Replay one scope on a fresh, authenticated signed multiplier."""

from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import run
import json
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from bootstrap import install


def worker(name, target):
    cmd = [sys.executable, "-IB", str(PACKAGE / name), str(target)]
    return run(cmd, check=True, capture_output=True, text=True).stdout


def check_binary():
    from upstream import install as activate
    activate()
    sys.path.append(str(PACKAGE / "source"))
    from check_binary_k7 import check_archives_and_ledger, check_charts, check_outer_word
    from check_binary_k7 import check_weighted_sparse, run_registers
    from strong_binary import caller, graph
    g, root = graph(), caller()
    assert g == check_archives_and_ledger()
    assert sum(v[0]=="LOCAL" for v in root["events"]) == 36
    assert run_registers(g["program"], g["start"], g["final"], root["ports"]) == (3426,2796)
    check_outer_word(root)
    assert check_charts(g,root["ports"]) == (636,2353,44734)
    check_weighted_sparse(g,root)
    print("PASS_K7_ALL_630_ROLES_AND_WEIGHTED_ROUTES")


def check_product():
    from band_product import multiply, multiply_tapes
    from check_product import physical_product
    from installations import ENTRY, TERMINAL
    from io import BytesIO

    for a,b in ((0,0),(-1,0),(-1,-1),(-741503,466013),(741503,466013),
                (2**127-1,-2**73+3),(-(2**4096+9),2**41-1)):
        assert multiply(a,b) == a*b
    for profile in (ENTRY,TERMINAL):
        left = BytesIO(b"pre"+(741503).to_bytes(6,"little")+b"post")
        right = BytesIO(b"pre"+(466013).to_bytes(5,"little")+b"end")
        left.seek(3)
        right.seek(3)
        out = BytesIO()
        sign, size = multiply_tapes(left,6,right,5,out,left_negative=True,profile=profile)
        assert sign and size == 5 and -int.from_bytes(out.getvalue(),"little") == -345550037539
        assert left.tell()==3 and right.tell()==3
    result = physical_product(ENTRY)
    assert result["coefficients_prefix"] == [11811,10996,4152,868,77]
    print(json.dumps(result,sort_keys=True))
    print("PASS_SIGNED_PRODUCT_AND_RESTORATION")


def main(scope):
    if not __debug__:
        raise RuntimeError("Enable Python assertions for this replay")
    with TemporaryDirectory(prefix="tier-machine-") as name:
        dst = Path(name)
        install(dst)
        sys.path.insert(0, str(dst))
        if scope == "price":
            receipt = json.loads(worker("receipt.py",dst))
            assert receipt == json.loads((PACKAGE/"RESULT.json").read_bytes())
            print(worker("check_placement.py",dst),end="")
            print("PASS_COMPLETE_RATE_STOCK_AND_CLOCK",receipt["complete_log2_C"])
        elif scope == "binary":
            check_binary()
        elif scope == "gaussian":
            print(worker("check_gaussian.py",dst),end="")
            print(worker("check_phase_passes.py",dst),end="")
        elif scope == "setup":
            measured = json.loads(worker("check_serial_setup.py",dst))
            assert measured == json.loads((PACKAGE/"MEASUREMENTS.json").read_bytes())["serial_setup"]
            print("PASS_SERIAL_FIXED_INSTALL", measured["setup_exponent"])
        elif scope == "product":
            check_product()
        elif scope == "interval":
            print(worker("independent_price.py",dst),end="")
        else:
            raise ValueError("Unknown replay scope")


if __name__ == "__main__":
    main(sys.argv[1])
