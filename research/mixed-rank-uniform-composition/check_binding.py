"""Check the ownership and precision bindings for the 480-factor application."""

import gzip
import hashlib
import json
import sys
from fractions import Fraction
from math import prod
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bind_compiler import MIXED, MP, blob, document


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(condition, label):
    if not condition:
        raise ValueError(label)


def check_binary(word, adjoint):
    public = word["public"]
    live = set(range(public))
    budget = public + word["owned_fields"]
    peak = public
    allocations = 0
    program = reversed(word["program"]) if adjoint else word["program"]
    for opcode, owner, *args in program:
        if opcode in ("INIT","CLEAR"):
            check(public <= owner < budget, "public or unknown private owner")
            opens = (opcode == "CLEAR") if adjoint else (opcode == "INIT")
            if opens:
                check(owner not in live, "aliased fresh owner")
                live.add(owner)
                allocations += 1
            else:
                check(owner in live, "double clear")
                live.remove(owner)
        elif opcode in ("ADD", "SWAP"):
            other = args[0]
            check(owner in live and other in live and owner != other, "invalid pair")
        elif opcode == "MOVE":
            check(owner in live, "paid address has no owner")
        else:
            raise ValueError(opcode)
        peak = max(peak, len(live))
    check(live == set(range(public)), "unretired owner")
    return peak, allocations


def check_complex(graph):
    public = len(graph["initial"])
    forms = dict(graph["forms"])
    available = {~i for i in range(public)}
    returned = {i for i,_,_ in graph["moves"]}
    terminal = set(range(graph["first_output"], graph["first_output"]+public))
    check(not returned & terminal, "output/return collision")
    check(set(forms) == returned | terminal, "unknown or omitted row")
    check(len(available) == public, "input alias")
    terms = 0
    for row in graph["schedule"]:
        check(row not in available, "reused immutable result")
        for donor, scalar in forms[row]:
            check(donor in available and Fraction(scalar), "unavailable donor")
            terms += 1
        available.add(row)
    check(available.issuperset(returned | terminal), "unfinished return")
    return public, len(returned), terms


def main():
    pins = {row["path"]: row for row in document(MIXED, f"{MP}/SOURCES.json")}
    def source(path):
        row = pins[path]
        raw = blob(row["head"], path)
        check(digest(raw) == row["sha256"], f"source digest differs for {path}")
        return raw
    p = "research/p104-chart306-chain"
    raw = gzip.decompress(source(f"{p}/DOUBLE-CANDIDATE.json.gz"))
    binary = json.loads(gzip.decompress(source("research/p104-iterated-returns/binary/WORD.json.gz")))
    application = json.loads(source(f"{p}/DOUBLE-APPLICATION.json"))
    claim = document(MIXED, f"{MP}/RESULT.json")
    bit = document(MIXED, f"{MP}/BIT.json")
    canonical = json.dumps(binary, separators=(",",":"), sort_keys=True).encode()
    check(digest(raw) == claim["rational_word"] ==
          "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48",
          "complex word differs")
    check(digest(canonical) == claim["binary_word"] ==
          "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d",
          "binary word differs")
    check(int(claim["power"]) == 480 and claim["paid_cutoffs"] ==
          {"grades_1_to_4":10, "grades_above_4":11}, "wrong mixed rule")
    print("complex immutable banks and donor reads", check_complex(json.loads(raw)))
    print("binary peak live including public, total private opens",
          check_binary(binary, False), check_binary(binary, True))
    factors = application["conversion"]["odd_factors"]
    root = application["common_root"]
    check(prod(factors) == root["native_odd"]["tested"], "wrong odd scale")
    check(max(f.bit_length() for f in factors) <= 24, "odd scalar too wide")
    H = int(application["common_depth_guards"]["tested"]["compiler_H"])
    c = 2 * max(root["context_binary_bits"], root["context_mass_bits"])
    d = (c*1920*153**1920*(H+1)**2).bit_length()
    check((c, d) == (856, 14083) and d < H, "depth limit")
    print("root c, exact context product bit length, compiler H", c, d, H)
    cover = bit["delayed_cover_and_stock"]
    covered = Fraction(cover["covered"])
    rho = Fraction(cover["rho"])
    cold = (1-rho)*covered
    seed = Fraction(cover["seed"])
    check(cold > seed and rho > seed, "cold start misses ordinary seed")
    previous = seed
    for record in cover["stages"]:
        result = Fraction(record["claim"])
        check(previous == Fraction(record["previous"]) and
              result < min(rho, 1-rho, (1-rho)*covered+rho*previous), "stage gap")
        previous = result
    check(len(cover["stages"]) == 5 and previous == Fraction(claim["binary_ordinary"]),
          "stage binding")
    print("ordinary stages including cold stage", 1+len(cover["stages"]),
          "cold excess over seed", cold-seed)


if __name__ == "__main__":
    main()
