"""Check cold funding, all source application guards and the native evidence pins."""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cover import require


def read(path):
    return json.loads(path.read_bytes())


def outer(k, bit, g):
    b, a, s = k + 5 * g, k + 4 * g, k + 3 * g
    eps, beta, r0 = 1 - g, 1 - 3 * g, g / 10
    sigma, tau = 1 - b, 1 - a
    internal = tau + (1 - g) * max(sigma - tau, 0)
    leaf = sigma + g * (1 - sigma)
    lam = 1 - (s + a) / 2
    xi = eps * (1 + s) - Q(3, 32) + g
    key = beta + 1 - eps
    savings = dict(
        main_transform=eps * s,
        global_coordinate_router=a,
        fused_gaussian=1 - eps + s * beta,
        group_bit_router=1 - eps + a * beta,
        group_scans=1 - eps + beta,
        boundary_algebraic_matrix=Q(3, 32) + xi - eps,
        sparse_union_movement=xi + Q(1, 2) - eps,
        polynomial_products=eps,
        microbox_face_corrections=1 - (eps + beta + 48 - 128 + 2),
    )
    strict = [
        bit - a,
        b - a,
        s,
        b - s,
        a - s,
        g,
        1 - g,
        (1 - g) * b - a,
        1 - internal - s,
        1 - leaf - s,
        lam - tau,
        lam - sigma,
        lam - internal,
        1 - s - lam,
        1 - s - leaf,
        eps,
        1 - eps,
        xi - Q(1, 2),
        eps - xi,
        beta,
        eps - beta,
        1 - beta,
        1 - (2 * xi - 2) - r0 - beta,
        1 - (2 * xi - 2) - beta,
        1 - eps - r0,
        1 - eps,
        r0,
        1 - key,
        1 - beta - 2 * (1 - eps),
        128 - 48 - beta,
        g,
        eps - a,
        Q(1, 32) - b,
        2**45 - 7**16,
        2,
        2 - xi,
        5,
        1 - beta,
        1 - beta,
        1 - eps,
        savings["fused_gaussian"] - savings["main_transform"],
        g,
        k - Q("0.001730970419199163702738"),
        1 - eps,
        Q(11, 2),
    ]
    strict.extend(saving - k for saving in savings.values())
    functional = [
        1 - beta,
        beta * (1 - Q(3, 1000)),
        128 - 48 - eps - beta - 1,
        beta * (1 - Q(1, 250)),
    ]
    require(
        len(strict) == 54 and len(functional) == 4 and min(strict + functional) > 0,
        "exact outer requirements",
    )
    return dict(
        strict=len(strict),
        functional=len(functional),
        minimum=str(min(strict + functional)),
        limiting=min(savings, key=savings.get),
        savings={k: str(v) for k, v in savings.items()},
    )


def run():
    for row in read(HERE / "ORIGINS.json"):
        raw = (HERE / row["local"]).read_bytes()
        require(
            sha256(raw).hexdigest() == row["sha256"], "retained source " + row["local"]
        )
    old = read(HERE / "retained/grade14-result.json")
    bit = read(HERE / "retained/grade14-bit.json")
    check = read(HERE / "retained/grade14-audit.json")
    claim = Q(old["claim"])
    require(
        old["premises"]
        == check["premises"]
        == [
            "native_all_columns",
            "owned_erasure",
            "compiler",
            "precision_tape",
            "analytic_recovery",
        ],
        "exact scope of source claim",
    )
    require(
        old["rational_word"] == check["word"]
        and old["binary_word"] == bit["word_sha256"],
        "same funded source words",
    )
    selected = read(HERE.parents[1] / "certificates/frontier7000/CLAIM.json")
    expected = "Retained native operators, phase conventions, spectators and whole-job adapters work at every positive column multiplicity."
    require(
        selected["assumptions"][0]["statement"] == expected
        and old["premises"] == [premise["id"] for premise in selected["assumptions"]],
        "literal selected framework statements",
    )
    covered = Q(bit["covered"])
    rho = Q(1, 250)
    old_seed = Q(bit["ordinary_bootstrap"][0]["previous"])
    cap = Q(0)
    stages = []
    for index, current in enumerate(
        [old_seed] + [Q(s["claim"]) for s in bit["ordinary_bootstrap"]]
    ):
        envelope = (1 - rho) * covered + rho * cap
        require(
            cap < current < envelope < rho < 1 - envelope,
            "complete elementary-funded stage",
        )
        if index:
            source = bit["ordinary_bootstrap"][index - 1]
            require(
                cap == Q(source["previous"])
                and all(Q(x) == envelope for x in source["envelope"]),
                "literal four published stages",
            )
        stages.append(
            dict(
                previous=str(cap), admitted=str(current), slack=str(envelope - current)
            )
        )
        cap = current
    gate = check["outer"]["finite_compiler"]
    require(
        cap == Q(old["binary_ordinary"]) == Q(check["outer"]["pinned_binary_cap"]),
        "full ordinary cap",
    )
    require(
        Q(gate["tested"]) - claim == 7 * Q(gate["compiler_gap"])
        and cap > Q(gate["tested"])
        and Q(gate["raw_bracket"][0]) > Q(gate["tested"]),
        "exact comparison with both suppliers",
    )
    full = outer(claim, cap, Q(gate["compiler_gap"]))
    require(
        full["minimum"] == old["sharp_outer"]["minimum_margin"]
        and full["limiting"] == "main_transform",
        "sharp outer",
    )
    h = int(gate["H"])
    c = check["common_root"]["common_context_c"]
    depth_guard = (c * 1920 * 153**1920 * (h + 1) ** 2).bit_length()
    require(
        depth_guard == 14083 < h
        and (c, check["common_root"]["temporary_width"]) == (856, "W+26"),
        "complete current root format",
    )
    cm = check["ordinary"]
    require(
        cm["ordinary_elementary_record_upper"]
        == 4 * (153 + 1) ** 2 * cm["ordinary_map_slots"],
        "raw complex movements",
    )
    homes = cm["native_numeric_homes"]
    resets, transfers = cm["native_selected_resets"], cm["native_selected_transfers"]
    selector = 63 * homes - 7 * homes.bit_count() + 27 * homes.bit_length() + 59
    slope = resets * (14 * homes + 11) + transfers * (14 * homes + 137)
    fixed = resets * (selector + 3) + transfers * (selector + 320)
    require(
        cm["selected_steps_linear_and_constant"] == [slope, fixed],
        "complete padded field sweeps",
    )
    require(
        32 * cm["extra_allowance_all_48_native_calls"] == 12793344
        and cm["ordinary_scalar_services"] == 1315098624,
        "pre-factor incidence and scalar charge",
    )
    movements = dict(
        full_field="N_c*(2*(W+26)+3)",
        slope=slope,
        constant=fixed,
        elementary_map_records=cm["ordinary_elementary_record_upper"],
        scalar_services=cm["ordinary_scalar_services"],
    )
    return dict(
        kappa=str(claim),
        movements=movements,
        source_assumption_count=len(old["premises"]),
        remaining=old["premises"][1:],
        stages=stages,
        ordinary=str(cap),
        dense_bit_threshold_log=int(bit["uniform"]["H"]),
        complex_carrier_log=h,
        depth_guard_bits=depth_guard,
        outer=full,
    )


if __name__ == "__main__":
    result = run()
    if "--emit" not in sys.argv:
        require(
            result == read(HERE / "RESULT.json")["application"],
            "frozen complete application",
        )
    print(json.dumps(result, sort_keys=True))
    print("PASS_GRADE14_FOUR_PREMISE_APPLICATION")
