#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the archived bytes and recompute the two saved ordinary totals."""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
SOURCE = "fa84fcdecb534700cd00dc81b74889f549a653daa2fb3658cb8142e1eeb9b9e6"
CANDIDATE = "f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def load(name):
    return json.loads((HERE / name).read_bytes())


def inventory():
    return sorted(
        path.relative_to(HERE).as_posix() for path in HERE.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
        and path.relative_to(HERE).parts[0] != "signed-replay"
    )


def check_custody():
    files = load("MANIFEST.json")["files"]
    require(sorted(files) == inventory(), "appendix file inventory differs")
    for name, pin in files.items():
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and path.as_posix() == name,
                f"unsafe receipt path {name}")
        file = HERE / path
        require(file.resolve() == file, f"aliased receipt {name}")
        raw = file.read_bytes()
        require(len(raw) == pin["bytes"] and digest(raw) == pin["sha256"], f"receipt pin {name}")
    origins = load("SOURCE-INPUTS.json")
    for section in ("resource_engine_files", "observed_driver_files"):
        for name, pin in origins[section].items():
            require(all(files[name][key] == pin[key] for key in ("bytes", "sha256")), f"source pin {name}")
    archive_pins = origins["native_archive_members"]
    with ZipFile(HERE / "native-replay/predecessor-pairs.zip") as archive:
        require(sorted(archive.namelist()) == sorted(archive_pins), "predecessor member inventory")
        for name, pin in archive_pins.items():
            raw = archive.read(name)
            require(len(raw) == pin["bytes"] and digest(raw) == pin["sha256"], f"predecessor pin {name}")
    return len(files), len(archive_pins)


def check_native():
    document = load("receipts/native/RESULT.json")
    require(document["status"] == "PASS_STRICT_379_NATIVE_FINITE"
            and document["source"]["raw_sha256"] == SOURCE
            and document["candidate"]["raw_sha256"] == CANDIDATE, "native comparison custody")
    counts = document["pair_counts"]
    require((counts["union"], counts["fresh"], counts["reused"]) == (2959, 7, 2952),
            "native pair closure")
    route = document["route_columns"]
    require(route["all_forward"] == route["all_adjoint"] == 512 and route["wrong_phase"] == "rejected",
            "exact composed MOVE")
    launch = load("receipts/native/run7658-r2.launch.json")
    require(launch["exit"] == 0 and launch["candidate_canonical_sha256"] == CANDIDATE
            and launch["native_result_sha256"] == digest((HERE / "receipts/native/RESULT.json").read_bytes()),
            "native launch custody")
    for suffix in ("stdout", "stderr", "time"):
        name = f"receipts/native/run7658-r2.{suffix}"
        require(digest((HERE / name).read_bytes()) == launch[f"{suffix}_sha256"], f"native launch {suffix}")
    for name in ("START.json", "OPERATORS.json", "PHYSICAL-1000000009.json", "PHYSICAL-998244353.json"):
        raw = (HERE / "receipts/native" / name).read_bytes()
        require(digest(raw) == document["artifacts"][name], f"native generated receipt {name}")
    for comparison in document["finite_replays"]:
        name = f"receipts/native/PHYSICAL-{comparison['prime']}.json"
        finite = load(name)
        require(finite["seed"] == comparison["seed"] and finite["endpoint_rows"] == 1501
                and finite["digests"] == comparison["digests"]
                and finite["digests"]["source"] == finite["digests"]["candidate"], "finite physical replay")


def check_resource(case, raw):
    base = f"receipts/{case}/"
    grid = load(base + "GRID.json")
    tape = load(base + "TAPE-SCALAR.json")
    ordinary = load(base + "ORDINARY.json")
    tariff = load(base + "TARIFF.json")
    literal = load(base + "LITERALS.json")
    require({grid["decompressed_sha256"], tape["source_raw_sha256"], ordinary["source_word_raw_sha256"],
             tariff["word_sha256"], literal["word_sha256"]} == {raw}, "resource word custody")
    require({grid["caller_sha256"], tape["caller_sha256"], ordinary["caller_sha256"]} == {CALLER},
            "resource caller custody")
    rational, integer = grid["rational_grid"], grid["integer_grid"]
    expected = (225, 14, Fraction(58120605, 2), 24277036)
    require(
        (integer["odd_scale_lcm"], integer["dyadic_height"], Fraction(integer["maximum_scaled_mass"]),
         integer["coefficient_visits"])
        == (rational["odd_scale"], rational["fractional_bits"], Fraction(rational["scaled_maximum_mass"]),
            rational["coefficient_visits"]) == expected,
        "native rational and integer grid",
    )
    require(grid["context_c"] == 2064 and integer["numerator_bits"] == 18
            and not literal["failures_by_guard"], "context and literal guards")
    require(tape["native_invocations"] == 17 and tape["native_nonmove_per_call"] == 143844
            and ordinary["declared_inventory"]["lifetimes"] == 234, "ordinary and tape denominators")
    services = sum(tape["scalar_macro_inputs"].values()) * 32
    require(services == tape["scalar_services_upper"] == 83895232
            and tape["scalar_steps_coefficient"] == services * 2**20, "conditional scalar coefficient")
    terms = ordinary["base"]
    routing = sum(terms["route_items"].values()) * 1000
    require(terms["routing"] == routing, "ordinary route count")
    caller_total = sum(sum(part.values()) for part in terms["caller_items"].values())
    require(terms["caller_total"] == caller_total, "ordinary caller count")
    subtotal = 17 * (terms["scalar_upper"] + routing) + caller_total
    require(terms["raw_upper"] == subtotal, "ordinary subtotal")
    modeled = subtotal + terms["per_input_conversion"] + terms["lambda_second_charge"]
    require(terms["conservative_total"] == modeled, "ordinary retained conservative allowance")
    modeled += ordinary["all_caller_scalar_surcharge"] + ordinary["charged_caller_odd_conversions"]
    require(modeled == ordinary["retained_signed_model_total"] == tariff["retained_signed_model_total"],
            "ordinary signed surcharge")
    scale = integer["odd_scale_lcm"]
    rate = 4 * (scale.bit_length() + 1 + scale.bit_count())
    sites = 2 * 17 * 1501
    require((sites, rate, sites * rate) == (tariff["native_conversion_sites"], tariff["units_per_site"],
                                             tariff["extra_conversion_ordinary"]), "all native conversions")
    total = modeled + sites * rate
    require(total == tariff["conservative_total"] and 10**9 - total == tariff["margin"]
            and total < 10**9 and tariff["strict_ceiling_met"], "strict ordinary ceiling")
    return total


def main():
    files, archive = check_custody()
    check_native()
    source = check_resource("source", SOURCE)
    candidate = check_resource("candidate", CANDIDATE)
    require((source, candidate, source - candidate) == (815821876, 815804876, 17000), "matched ordinary delta")
    print(json.dumps({"status": "PASS_ARCHIVED_BYTES_AND_ORDINARY_ARITHMETIC", "files": files,
                      "prior_archive_members": archive, "ordinary_before": source, "ordinary_after": candidate},
                     sort_keys=True))


if __name__ == "__main__":
    main()
