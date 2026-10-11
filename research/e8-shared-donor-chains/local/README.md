# Portable changed local gauge admission

Python3.11+, standard library only. No public proof pipeline is run. Keep bare helper781 and signed candidate781 baseline inputs external; pass their paths explicitly.

    python local_admit.py CANDIDATE.json NEW_OUTPUT_DIRECTORY --helper-baseline HELPER781.json --signed-baseline CANDIDATE781.json

Default deps and prior-phase paths are relative to this script. Override with --deps and --prior-phase when reorganizing the root package. Input JSON may be gzip compressed. Do not use python -O. Preserve upstream notices.

Dependencies: deps/{complex_labels.py,complex_scalars.py,complex_splice.py,p10pins.py,scatter.py,clifford_exact.py}; prior-phase/{CLIFFORD-REVIEW.json,CLIFFORD-RECIPES.json,SOURCE-REUSE.json}. SOURCE-REUSE binds the audited prior gzip source to the exact decoded bare baseline and pins engine/old recipes. Every new/reflected phase pair is independently checked with exact Gaussian global phase. Isotropic entrances use canonical T_E, not Cq.

Outputs: RESULT.json,LOCAL-PROGRAMS.json.gz,NEW-PHASE-RECIPES.json,ENTRY-CHARTS.json and explicit adapted functions/pins. LOCAL-PROGRAMS contains candidate_sha256,local_programs,bills,checks,local_profile,entry_charts. Bills include scalar_macros,real_component_primitive_steps,schedule_sha256. Entry physical chart is T_E, normalized helper token is T_E^-1. Residual F*T_E^-1 needs architecture's separate two-sided bank receipt. No bank residual adapter is silently injected.

This is finite local admission. Global bank ownership, paid residuals/padding/phase integration, finite invoice and outer assembly remain separate required checks. No unconditional theorem or kappa follows from this runner alone.
