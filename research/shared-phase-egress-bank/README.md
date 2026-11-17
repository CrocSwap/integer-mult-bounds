# Share the literal phase and egress bank on twenty tapes

This contribution was produced by Nick Petalas. It answers the shared-bank
question in CubeJerry's [PR #7425](https://github.com/CrocSwap/integer-mult-bounds/pull/7425).

**Scoped constructive proof with finite executable corroboration; no new kappa.**
The source's direct boundary wrapper uses 36 physical tapes. The new fixed graph
uses **20**, including its two public owners. It shares all sixteen egress
private roles with the phase's eighteen private roles after successful
retirement, retaining the same identities and histories across changing calls.
This is an inventory upper-bound improvement, not a global minimum or a claim
of lower total visited space.

The graph has 19,960 locations and two entry points. Entry 17,814 performs the
input phase. Entry 0 performs normalization/egress and then the final phase.
The egress success halt becomes one fixed jump; no tape copy, allocation or
head reset occurs between components. Its successful exit costs exactly the
sum of the original egress and final-phase instruction counts.

The [proof](PROOF.md) gives the supplied-interface theorem, complete additive
time bound and rolewise historical-union argument. Successful retirement and
the numerical meaning of the unchanged components are cited predecessor
premises. Their original code and notices remain byte-exact in `inputs/`.
`EXPORT-PINS.json` records their source commits, paths, Git blobs and SHA256.
These pending source heads need no network or cached Git objects at replay.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/shared-phase-egress-bank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/shared-phase-egress-bank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shared-phase-egress-bank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shared-phase-egress-bank --check-source-history --check-modes
```

Another machine may substitute its CPython 3.12 path. The direct marker is
`PASS_SHARED_PHASE_EGRESS_BANK`. Replay prints a generated receipt bound to
the package and graph hashes, and writes no generated files.

The new composition check executes 19 calls with 378 Gaussian coefficients
and 1,297,236 literal instructions. The same twenty objects persist through
growing and shrinking geometries, including coefficient, outer and spectator
repetitions and both active positions in a two-bit chunk. Each return checks
complete values, original owner, every head, private erasure, opaque exterior,
old-tail cleanup and monotone history unions. All sixteen egress private roles
share visited histories with the phase. Five controls reject invalid jumps,
nonliteral instructions, aliased physical tapes, exhausted execution budget
and an omitted final phase.

The interpreter and direct Cartesian Gaussian/Walsh oracle are new and do not
import predecessor execution or verification code. The oracle C producer and
its format installation are explicitly external test services. Finite tests
corroborate the composition proof; they do not independently establish either
inherited component theorem or all global multiplication assumptions.

## Scope and overlap

Base canonical main is `e54523517d0f03e58352e647c403a5af3e525a57`.
Task `formal-interface-lemma`, priority revision 8, changes scope from a formal
binding to this physical boundary construction. The contextual picker reports
that its older #5599 assessment differs from the selected #7000 record.
Selected kappa remains `0.00363005817` and all five framework assumptions remain.

Live open PRs, recent handoffs, all-account PRs, merged title/body searches,
the main README corpus and the cached overlap helper were consulted. The helper
had 800 open PRs and 7,397 Discussion records, but only 225 of 10,178 main note
paths were materialized at initial orientation. Main was therefore also searched
directly through Git. This is bounded overlap evidence, not a novelty guarantee.
No same sharing result was found. #7477's reversal rejection cleanup is a
different contract and is not a dependency or a source of this question.

## Limitations

Private windows must be supplied blank for the union of both routines' visits,
including newly reached cells of a larger invocation. This does not combine
two arbitrary existing dirty banks. Failed or interrupted calls have no new
cleanup, reuse or rollback promise. The final phase has its original signed
range condition. Initial backing and erased history remain charged.

## Open next questions

Bind one actual C producer with the same header, address order, common grid,
signed headroom and retired private-bank boundary. Begin with one pinned caller
occurrence and price its format conversion and allocation. Those obligations
are additional; the supplied C test oracle is not a physical implementation.
Further tape reduction would require changing simultaneous component liveness.
This result provides neither that construction nor a lower bound.

No selected cold replay, independent human review, proof-kernel acceptance,
complete native supplier or complete multiplier is claimed. Hosted CI is
separate from the local package checks.

## Credit

CubeJerry / Jerry Chen supplies #7425's literal phase, the direct wrapper and
its explicit sharing question, and #7422's retained literal egress. Ali Romman
supplies #5375's sequential phase and amortization. Retain the egress lineage
of Tekalign #3127, Jose Manuel #2287 and #3087/#3091/#3098, JoyboyBrian #5329,
Cinna Davis and Ryanson Jonathan #4325, the upstream stream/layer authors and
the unchanged controller-source notices. The shared two-entry graph and its
composition proof are the new contribution. New material is Apache-2.0.
