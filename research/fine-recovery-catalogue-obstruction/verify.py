"""Bounded replay for the source-bound fine-theta recovery obstruction.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import json
from audit import finite_domain, guard_controls, large_parameters, recovery_controls
from source import authenticate, source_controls


def main():
    canonical, public = authenticate()
    result = {
        "claim_type": "source-bound scoped refusal and conditional ABI lower bound",
        "no_new_kappa": True,
        "canonical_source_files": canonical,
        "public_proof_dependencies": public,
        "source": source_controls(),
        "bounded_necessary_domain": finite_domain(),
        "large_parameter_controls": large_parameters(),
        "guard_controls": guard_controls(),
        "independent_recovery_controls": recovery_controls(),
        "universal_proof": "PROOF.md Sections 3-6; finite replay is corroboration only",
        "physical_production_execution": False,
    }
    print("PASS_FINE_RECOVERY_CATALOGUE_OBSTRUCTION")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
