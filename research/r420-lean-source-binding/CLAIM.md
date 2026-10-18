# Independent source-expression audit

- Track: independent verification; OS-random assignment seed **75**.
- Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
- Started: 2026-10-13 06:35 UTC. Target finish: 07:50 UTC, reserving the final quarter for verification and handoff.
- Object: the external correspondence between PR612's literal/derived Lean data and PR543's historical R420 circuit, including the inherited PR590 data.
- Method: independently tokenize the restricted source grammar, require the actual alias and derived expressions, reconstruct the seven ordered fields, and compare them with the supplier payload. Exercise expressions ignored by the historical correspondence script.
- Deliverable: a portable, fail-closed checker, reproducible controls, source pins and a concise scope statement. No new kappa or Lean kernel replay is proposed.

The three candidates were (1) a separate prime-power cyclic-inverse identity engine, rejected because #621/#668/#796/#804/#820 already cover the natural independent methods; (2) the R420 Lean-to-supplier correspondence, chosen after narrowing it to expressions that the historical audit does not read; and (3) packed selected-bit finite verification, rejected because #735/#763/#773 already audit the guards and carry behavior. Seed 75 selected the verification track and favored an older formal-interface dependency rather than the latest frontier.

The repository ledger and `im-cold617-formal-binding.py` already record successful R420 literal correspondence. This work does not claim first verification. The bounded hypothesis is that a restricted source parser can detect changes to aliases and derived expressions that its predecessor's separate literal extraction leaves unchecked. Such a mutation is not a counterexample to the original circuit or to the complete hash-pinned Lean build.

No pinned coordination issue was found (the open Discussions request #650 is unrelated). The claim is local. Overlap searches included PR612, source correspondence, independent verification, cyclic inverses and packed-bit audits. Workers stay within the chosen parser, controls and review scope.

Final overlap refresh covered new arrivals through #833 and focused searches for PR612/source correspondence. No matching source-expression audit was found. Main advanced to `f567884aeb8851b6e794af1184119a3bfbe1e631`; all nine consumed/context source files are unchanged. The package retains its exact original base. Outcome: all 13 fields match, six altered expressions expose the historical check's narrower coverage, and the new checker rejects all 33 negative cases. See VALIDATION.md for the checks and limitations.

Submitted as [PR #834](https://github.com/CrocSwap/integer-mult-bounds/pull/834). The contribution is complete for external review; maintainer acceptance and hosted workflow approval are separate.
