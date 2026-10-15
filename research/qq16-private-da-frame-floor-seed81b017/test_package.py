"""Package-level positive and negative controls, active even under -O."""

from pathlib import Path
from hashlib import sha256
import json
import runpy


HERE = Path(__file__).resolve().parent
VERIFY = runpy.run_path(str(HERE / "verify.py"))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    raw = (HERE.parents[1] / "research/joint-query/certificate.json.gz").read_bytes()
    packet = VERIFY["load_certificate"](raw)
    result = VERIFY["calculate"](packet)
    need(result["status"] == "PASS_QQ16_PRIVATE_DA_FRAME_FLOOR",
         "Exact frame result")
    need(result["registered_maps_checked"] == 3650 and
         result["single_map_hits"] == 0, "Complete one-map census")
    need(result["rank_one_line_calls_lower_bound"] == 144,
         "Eight exact 18-term line distances")
    saved = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    expected = dict(result)
    expected["verify_py_sha256"] = sha256((HERE / "verify.py").read_bytes()).hexdigest()
    expected["test_package_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    need(saved == expected, "Saved exact result and package code pins")

    damaged = bytearray(raw)
    damaged[len(damaged) // 2] ^= 1
    try:
        VERIFY["load_certificate"](bytes(damaged))
    except ValueError:
        pass
    else:
        raise ValueError("Mutated certificate must be rejected")

    print("PASS_QQ16_PRIVATE_DA_PACKAGE_CONTROLS identity=1 one_term=1 "
          "wrong_stage=1 wrong_port=1 mutated_pin=1")


if __name__ == "__main__":
    main()
