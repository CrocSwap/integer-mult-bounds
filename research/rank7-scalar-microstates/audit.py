# SPDX-License-Identifier: Apache-2.0
"""Compare independently derived proof-relevant fields to the pinned PR3090 claim."""

from vendor.format_source.format import require

CAPACITY = ("fractional_bits", "symmetric_amplitude_in_input_L", "signed_width")
FINGERPRINTS = ("source_writes", "scratch_macros", "recipe_sha256")


def compare(derived, claimed):
    require(
        set(derived) == set(claimed["providers"]) == {"base", "extra"}, "provider scope"
    )
    cases = 0
    for provider in ("base", "extra"):
        streams = claimed["providers"][provider]["streams"]
        require(
            set(derived[provider]) == set(streams) == {"forward", "backward"},
            "directions",
        )
        for direction in ("forward", "backward"):
            actual = derived[provider][direction]
            source = streams[direction]
            require(
                set(actual)
                == set(source["policies"])
                == {"scratch", "source_walk", "target_walk"},
                "policies",
            )
            for policy in ("scratch", "source_walk", "target_walk"):
                own, claim = actual[policy], source["policies"][policy]
                require(
                    own["macros"] == source["scalar_macros"],
                    "macro census corroboration",
                )
                require(
                    own["real_instruction_slots"]
                    == 2 * claim["single_component_instructions"],
                    "instruction census corroboration",
                )
                for field in FINGERPRINTS:
                    require(
                        own[field] == claim[field],
                        "literal recipe corroboration: " + field,
                    )
                for ours, theirs in (
                    ("envelope", "microstates_only"),
                    ("combined_with_native", "capacity"),
                ):
                    require(
                        all(own[ours][key] == claim[theirs][key] for key in CAPACITY),
                        "capacity corroboration: " + ours,
                    )
                cases += 1
    require(cases == 12, "complete independent comparison")
    return {
        "status": "CORROBORATED_NO_DEFECT_IN_CHECKED_ARITHMETIC_SCOPE",
        "source_pr": 3090,
        "source_head": "47a2bcec53667f490df6d40550e14a8ae465cba4",
        "cases": cases,
        "compared_fields": [
            "macros",
            "real_instruction_slots",
            *FINGERPRINTS,
            "microstate_grid_norm_width",
            "combined_grid_norm_width",
        ],
        "not_compared": "First-witness labels and observation counts differ because this audit also observes recipe entrances.",
    }
