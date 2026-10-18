#!/usr/bin/env python3
"""Stock-margin chain: every remaining cutoff pair lands in the previous stopped range.

Extends the native stage-2 handoff (discussion comment 18949652) and the
stage-3 audit (research/stage3-stock-margin) to native stages 4-7 and to the
whole conservative branch (stages 2-7).  Exact rational arithmetic on the frozen
selected receipt.  The stock coefficient itself stays unresolved; no supplier
replay and no kappa claim.
"""
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RESULT = ROOT / "research/selected-bootstrap-stock-audit/RESULT.json"

# Bytes audited here: the frozen selected-bootstrap stock receipt.
AUDITED_RECEIPT_SHA256 = "f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917"

BRANCHES = ("bootstrap", "conservative_bootstrap")

# Recorded cutoffs L_1..L_7 (log2) of the two selected bootstrap branches.
CUTOFFS = {
    "bootstrap": [
        4785575287428,
        1704765459304159860,
        607288590542446415285737,
        216334411393790970429839007220,
        77064806225479172206224871399132079,
        27452795513701194724472919763925196307643,
        9779509200503493187646549135972282547372018449,
    ],
    "conservative_bootstrap": [
        4785575320504,
        1704765476910090189,
        607288598888548790921228,
        216334415105865784879411203134,
        77064807811065157671403130893305387,
        27452796172306184037585992127352896661365,
        9779509468522638102470520685957791421407368732,
    ],
}

# Expected floor(s*L_j - L_{j-1}) and floor((1-s)*L_{j-1}) per branch and stage.
# Native stages 2 and 3 are the published positive controls; the rest are new.
EXPECTED = {
    "bootstrap": {
        2: (2851485324488315, 4777557234646),
        3: (1015784602045963452130, 1701909188404384116),
        4: (361852943409004062662957360, 606271101174941147673746),
        5: (128902872114845343680818492656976, 215971951161791423920760764122),
        6: (45919069451025819974017753079498485812, 76935687018952933071573623067467882),
        7: (16357749867431357886201881301751734180286423, 27406799379443943425326695785974298689751),
    },
    "conservative_bootstrap": {
        2: (2851485349075174, 4777557267681),
        3: (1015784614274199324771, 1701909205985694510),
        4: (361852949001065216196285881, 606271109508797681506267),
        5: (128902874547204377208495156774925, 215971954868265831114423996024),
        6: (45919070474352818766043006228287526563, 76935688602102847428409756325327327),
        7: (16357750287845003715345973449256621277195623, 27406800037024020153662277717993715829414),
    },
}

PUBLISHED_CONTROLS = {"bootstrap": {2: 2851485324488315, 3: 1015784602045963452130}}

FIRST_STAGE_BIT_COEFFICIENT = 8194
HEADROOM_GUARD = math.ceil(math.log2(8 * FIRST_STAGE_BIT_COEFFICIENT))


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def floor_fraction(value):
    return value.numerator // value.denominator


def branch_margins(stages, cutoffs):
    """Return s and the stage -> (margin, routing room) table for one branch."""
    gap = Fraction(stages[0]["gaps"]["stock"])
    require(
        all(Fraction(stage["gaps"]["stock"]) == gap for stage in stages),
        "stock gap is not uniform across the branch",
    )
    s = 1 - gap
    table = {}
    for j in range(2, 8):
        margin = s * cutoffs[j - 1] - cutoffs[j - 2]
        table[j] = (margin, (1 - s) * cutoffs[j - 2])
    return s, table


def check_branch(name, stages, cutoffs, expected):
    require(len(stages) == 7, name + ": expected seven stages")
    require(
        [stage["stage"] for stage in stages] == list(range(1, 8)),
        name + ": stage numbers are not 1..7 in order",
    )
    require(
        all(stage["actual_stock_coefficient"] is None for stage in stages),
        name + ": a stock coefficient is already stored",
    )
    require(
        [int(stage["cutoff_log2"]) for stage in stages] == cutoffs,
        name + ": recorded cutoffs differ from the audited table",
    )
    s, table = branch_margins(stages, cutoffs)
    for j, (margin, room) in table.items():
        floor_margin = floor_fraction(margin)
        floor_room = floor_fraction(room)
        require(floor_margin > 0, name + f": stage {j} margin is not positive")
        require(
            floor_margin == expected[j][0],
            name + f": stage {j} margin {floor_margin} != expected {expected[j][0]}",
        )
        require(
            floor_room == expected[j][1],
            name + f": stage {j} routing room {floor_room} != expected {expected[j][1]}",
        )
        # Failure control: reusing the previous cutoff in place of L_j must not
        # stay nonnegative.
        stale = s * cutoffs[j - 2] - cutoffs[j - 2]
        require(stale < 0, name + f": stage {j} stale-cutoff control stayed nonnegative")
    require(
        all(HEADROOM_GUARD <= stage["stock_headroom_log2"] for stage in stages),
        name + ": recorded headroom does not cover the 8194 guard",
    )
    return s, table


def main():
    payload = RESULT.read_bytes()
    require(
        hashlib.sha256(payload).hexdigest() == AUDITED_RECEIPT_SHA256,
        "stock receipt bytes differ from the audited revision",
    )
    receipt = json.loads(payload.decode("utf-8"))
    require(set(receipt["branches"]) == set(BRANCHES), "unexpected branch inventory")

    for name in BRANCHES:
        check_branch(name, receipt["branches"][name]["stages"], CUTOFFS[name], EXPECTED[name])

    # Positive controls: the two published native integers are reproduced above,
    # but fail explicitly if either expected table entry drifts.
    for name, controls in PUBLISHED_CONTROLS.items():
        s, table = branch_margins(receipt["branches"][name]["stages"], CUTOFFS[name])
        for j, value in controls.items():
            require(
                floor_fraction(table[j][0]) == value,
                f"published control {name} stage {j} not reproduced",
            )

    # Cross-branch control: applying one branch's saving to the other branch's
    # cutoffs must not reproduce the same margins.
    s_native, native_table = branch_margins(
        receipt["branches"]["bootstrap"]["stages"], CUTOFFS["bootstrap"]
    )
    s_conservative, conservative_table = branch_margins(
        receipt["branches"]["conservative_bootstrap"]["stages"],
        CUTOFFS["conservative_bootstrap"],
    )
    for j in range(2, 8):
        swapped = floor_fraction(
            s_native * CUTOFFS["conservative_bootstrap"][j - 1]
            - CUTOFFS["conservative_bootstrap"][j - 2]
        )
        require(
            swapped != floor_fraction(conservative_table[j][0]),
            f"cross-branch saving control matched at stage {j}",
        )

    # Receipt-tamper control: a receipt whose stage-7 cutoff equals stage 6's
    # must be rejected by the same branch check.
    tampered = json.loads(payload.decode("utf-8"))
    stages = tampered["branches"]["bootstrap"]["stages"]
    stages[6]["cutoff_log2"] = str(stages[5]["cutoff_log2"])
    try:
        check_branch(
            "bootstrap",
            stages,
            CUTOFFS["bootstrap"],
            EXPECTED["bootstrap"],
        )
    except SystemExit:
        pass
    else:
        raise SystemExit("tampered receipt passed the branch check")

    smallest = min(
        floor_fraction(table[j][0]) for table in (native_table, conservative_table) for j in table
    )
    print(
        "PASS_STOCK_MARGIN_CHAIN "
        "native_stages=2-7 conservative_stages=2-7 new_pairs=10 published_controls=2 "
        f"min_margin={smallest} coefficient=unresolved headroom_guard={HEADROOM_GUARD} "
        f"native_s={s_native.numerator}/{s_native.denominator} "
        f"conservative_s={s_conservative.numerator}/{s_conservative.denominator}"
    )


if __name__ == "__main__":
    main()
