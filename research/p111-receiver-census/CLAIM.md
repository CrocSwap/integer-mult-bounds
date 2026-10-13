# Bit supplier claim — seed 15

- Started 2026-10-13 07:35 PDT; finish by 08:35 PDT. Stop experiments by 08:20 and reserve the final 15 minutes for verification and handoff.
- OS randomness: `secrets.randbelow(100)` returned **15** (bit supplier).
- Exact base: `007664306fff84fbb1c9a1b4053b69f439764034`.
- Current selected result: PR890, conditional kappa `1661957774647029/10^18`, retaining the PR589/555 bit supplier.
- Object: PR555's frozen puncture set `[10,15,51,53,56,66,72,89,111]`, L3 plan and `plan_thirds` seed 552, retained by PR589.
- Hypothesis: choosing different receivers for the nine pseudo-target totals can reduce the complete helper count below 439.
- Domain: every one of the `3^9 = 19,683` receiver vectors with entries 1, 2 or 3, retaining the source generator's ordered mini-node solves, iterative missing-carrier closure, and extra-carrier reuse before allocating junk wires. This is a generator-defined class, not unrestricted helper optimality.
- Deliverable: an exact complete helper census, an independent calculation, source pins, meaningful failure controls, and either a verified improved candidate or a scoped negative result.
- Three narrow candidates: (0) this receiver census; (1) orientation/precision repair of a frozen PR941 matching optimum; (2) complete small-wire phase-A resynthesis. Seed `15 % 3 = 0` selects the receiver census. Candidate 1 depends on a large pending closure; candidate 2 overlaps PR904/936/952. The original PR555 discovery sampled only 3–6 receiver choices per keeper-plan seed, rather than this complete domain.
- Overlap: open PR metadata inspected through #955, plus all-state receiver/puncture searches. Frame-only and single-relocation work (#886/#933), decoder copy floors, and recent circuit resynthesis are distinct and are not reopened. No open sprint coordination issue was found among the current issues (#650 and #913); claim recorded locally.
- All work stays under this package. No selected-frontier change or merge is authorized. Prepared for ToikY with substantial OpenAI Codex assistance; Apache-2.0 and predecessor credits retained.

## Result and handoff

Completed the declared cube: 19,683 receiver assignments, represented by 60
block-local records and checked separately by a full-vector set-valued engine.
All use 439–443 helpers; 2,646 attain 439. The shipped receiver choice already
attains the fixed-family minimum. One completed census was the stopping rule;
no further keeper-plan or circuit search followed. Scope and remaining supplier
obligations are in PROOF.md and README.md.

Both complete record digests match; seven package tests, 59 original-generator
controls, twelve base source-object checks and seventeen selected-record tests
pass. The final overlap refresh reached PR961 and found no receiver-family
census duplicate; upstream main still equals the recorded base. No coordination
issue was available. The result's source branch is
https://github.com/ToikY/integer-mult-bounds/tree/codex/bit-supplier-seed15 .
No new kappa is claimed.
