#!/usr/bin/env python3
"""Exact constructive replay. SHIN09-git with OpenAI Codex assistance. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0,str(PACKAGE))
from construction_check import (check_count_formulas, check_predecessor, construction_grid,
                                labeled_codes, need, rejection_controls, worked_example)
from tariffs import check_certificates, literal_prices, parity_family


PINS = {
    "source/6691-README.md":"0cbcb749f758e2b8badf6bd5a87512b4b709331c894f0bcdb3126e1002df3e09",
    "source/6691-PROOF.md":"a6db4dfce4ece302678e9c94e63bc85b550e976d056f273378c25b792cd09b6d",
    "source/6691-RESULT.json":"e8fd2b58ed9c2e359d20c11d0885014058f8567219bfc6aa5ce692e1c6ac17d7",
    "source/3997-TERNARY-SCREEN.txt":"ded4c54c486864dd3d3c2084bbb15f471bb7926af21f6d0c8a4582312a1001ac",
    "source/LICENSE":"c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
}


def read(name):
    return json.loads((PACKAGE/name).read_bytes())


def construct():
    files = read("SOURCES.json")["files"]
    for name, digest in PINS.items():
        rows = [r for r in files if r.get("vendored_as") == name]
        actual = hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest()
        need(len(rows) == 1 and actual == digest == rows[0]["sha256"], "retained source hash")
    baseline = check_predecessor(PACKAGE,read("source/6691-RESULT.json"))
    grids, six = construction_grid()
    regular = labeled_codes(3,3)
    binary = labeled_codes(3,3,True)
    need(len(regular) == 33727 and len(binary) == 30547, "six-port labeled counts")
    summary = dict(four_port_control=baseline, grids=grids, invalid_cases=rejection_controls(),
                   tariff_certificates=check_certificates(read("PRICE-CERTIFICATES.json")),
                   parity_tariffs=parity_family(), monotone_prices=literal_prices(regular,binary,3,6),
                   closed_counts=check_count_formulas(), zero_one_example=worked_example())
    return summary, six


def main():
    summary, witnesses = construct()
    rows = read("SIX-PORTS.json")
    actual = {tuple(r["counts"]):{k:v for k,v in r.items() if k not in ("counts","pairs_per_label_F2_F3")} for r in rows}
    need(len(rows) == len(actual) and witnesses == actual, "stored witness certificate differs")
    need(summary == read("RESULT.json")["construction"], "stored construction summary differs")
    print(json.dumps({"status":"PASS_TWO_BLOCK_SIGNATURES","result":summary},sort_keys=True))


if __name__ == "__main__":
    main()
