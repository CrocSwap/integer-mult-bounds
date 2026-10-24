"""Check the terminal order in the free commuting fourth-root group."""

from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
OTHER = HERE.parents[1] / "coherent-port"
PINS = {
    "SPECTATOR-TERMINAL-PRODUCT.md":"588446b16cfcda173ce78092d6ef53ecec41ba5de54f7fae5191e836c326fb54",
    "check_spectator_terminal_product.py":"43191fd9133470757d097f3374672173cd52b6627e1dd47d690780c6030e40b0",
    "SPECTATOR-TERMINAL-PRODUCT.json":"3eda58b1b4b3e86e7dd739c1bceeedf75cc0e176f49f54e0078bcd53de09c900",
}


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    for name,pin in PINS.items():
        need(sha256((OTHER/name).read_bytes()).hexdigest() == pin,"Frozen terminal input: "+name)
    count = 0
    for m in range(1,33):
        epsilon = [1 if (m-j) % 2 == 0 else -1 for j in range(1,m+1)]
        for initial_z in range(2):
            exponents = [0]*m
            z = initial_z
            for j in range(m):
                exponents[j] = (1 if z else -1) % 4
                z ^= 1
            diagonal = [(sign if not z else -sign) % 4 for sign in epsilon]
            affine = [(1+2*int(sign == -1)+2*z) % 4 for sign in epsilon]
            need(exponents == diagonal == affine,"Product in the free fourth-root group")
            # Apply Q_all^-1, then X_Vminus, D_V, and S^m.
            decoded = [(value-1+2*int(sign == -1)+2*z) % 4
                       for value,sign in zip(exponents,epsilon)]
            need(decoded == [0]*m and z ^ (m % 2) == initial_z,"Exact inverse order")
            if m % 2:
                wrong = [(value-1+2*int(sign == -1)+2*(z^1)) % 4
                         for value,sign in zip(exponents,epsilon)]
                need(wrong != [0]*m,"Wrong inverse order negative control")
            count += 1
    result = {"status":"PASS_INDEPENDENT_TERMINAL_PRODUCT_ORDER",
              "input_sha256":PINS,"free_group_cases":count,
              "review":"The general alternating-exponent proof was checked directly. Finite checks use independent formal fourth-root generators, not the producer kernel code.",
              "scope":"Equations (1)-(4) and their ordering; no native admission or full-layer endpoint review.",
              "new_corollary_condition":"A layer conjugation must act as identity on z, or explicitly commute with other T factors. Fixing the z address alone is not enough."}
    (HERE/"TERMINAL-PRODUCT-REVIEW.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
