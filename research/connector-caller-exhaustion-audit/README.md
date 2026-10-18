# Seven-source gap traversal and caller exhaustion audit

This package closes the gap-enumeration and caller-admission handoff left by
[PR3276](https://github.com/CrocSwap/integer-mult-bounds/pull/3276).
It supplies a written source-bound implication and separate finite checks.
No source defect was found within this scope.

The audited sources are conorholds' canonical-main
`research/connector-covering-code/{cycle_search.cpp,verify_cycles.py}` at
`463113d675af7410ac91d53a4fed51ec6494eb9a`. Their exact Git blobs and SHA256
hashes are in `SOURCES.json`. All executable inputs are in canonical main.
No pending PR object or foreign cached Git history is needed.

## Result and limits

For each supplied low template, the actual `Engine::enumerate` visits every
bounded gap vector exactly once unless a word is found or a timeout is recorded.
Its `true` return excludes both interruptions. The full Python caller requests
the default complete native mode, requires all 82 named orbit records, and
rejects incomplete or found-word receipts. Controls-only is a separate result
with zero completed orbits.

The native audit checks 45,189,640 **gap visits**, not that many distinct words.
There are 102,552 gap vectors per A template and 286,780 per B template.
All five A and 77 B templates run with each of the two conditional-cover flags:

```text
2 * (5 * 102552 + 77 * 286780) = 45189640 visits
2 * (5 * ceil(102552/257) + 77 * ceil(286780/257)) = 175864 search handoffs
```

Every visit is checked against its independent lexicographic rank. The audit
replaces capacity and search with deterministic finite test doubles. It does
**not** exhaust the scientific path assignments, execute the original positive
word controls, validate f(7)=24, or admit a supplier. Synthetic Python receipts
are labelled synthetic and are not exclusion evidence. No new kappa or selected
frontier change is claimed.

## Proof of the scoped implication

### Gap domain

Fix a low template with `b` blocks and high-step total `H`. The required gap
domain is

```text
G(b,H) = {g in {0,...,7}^b : sum(g) = H}.
```

In `Engine::enumerate`, `remaining` initially equals `H`. At recursive depth
`position`, it equals `H` minus the chosen prefix sum. The loop visits each next
digit from zero through `min(7,remaining)` exactly once. It preserves a
nonnegative remainder. At depth `b`, the function emits a leaf exactly when
the remainder is zero. Thus every emitted vector belongs to `G(b,H)`, and each
member has exactly one root-to-leaf path. The loops order the vectors
lexicographically. The traversal has depth at most eleven stack frames for
these eight/ten-block templates. For example, `G(2,2)` has exactly
`(0,2),(1,1),(2,0)` in that order.

The independent audit uses coefficients
`D(s,h) = [x^h](1+x+...+x^7)^s`, with `D(0,0)=1`. The lexicographic rank of a
vector is the sum, at every position, of `D` for smaller possible digits and
the remaining suffix sum. This does not execute the recursive generator. Each
actual leaf must have the next rank, starting at zero, and the final count must
equal `D(b,H)`. Together these checks exclude omissions, duplicates, reordering
and wrong-sum leaves, without storing the vectors or accepting a hash collision.

The adapter changes exactly three unique statements. It inserts the leaf-rank
check, substitutes the capacity predicate, and substitutes the search handoff.
All digit loops, recursive calls, deadline checks, counters, surrounding stops
and final return execute from the authenticated source. Production sources
remain unchanged. The instrumented file is private disposable scratch.

### Interruption and search handoff

Each capacity survivor triggers exactly one root search call. The audit accepts
ranks `0 mod 257`, independently counts those calls, and checks the production
`capacity_survivors` counter. Separate controls set `found` or `timed_out` at
the first or 137th handoff, in both patterns. No later gap may be visited, and
the return must be false. Two expired real-clock tests reach the actual
256-composition checkpoint and must set `timed_out` and return false.

The production leaf ignores the Boolean return of `search`. That is safe only
with the inherited search contract: a witness sets `found`, interruption sets
`timed_out`, and a false return with neither flag means the branch exhausted.
The enclosing visit checks these flags, and the final result is
`!timed_out && !found`. This audit checks that caller-side consequence. It does
not independently establish the search contract, propagation soundness or
candidate representation. PR3276, PR3244 and PR3261 address those separate
obligations.

### Native selection and Python admission

The pinned native `main` defaults to `pattern="both"`, no requested IDs,
`list_only=false`, `controls_only=false`, `premises_only=false`, and
`conditional_cover=true`. For an empty ID request it constructs IDs 1 through
the entire supplied template list, for A then B. Each completed enumeration
increments `completed` only for an exhausted orbit. A deadline before a new
orbit sets `all_exhausted=false`. An interrupted orbit makes that conjunction
false. A found candidate is independently checked and returns status 2;
incomplete execution returns 3; exceptions return 1. Only the complete default
census returns 0 with all 82 completions. The other status-zero modes are not
full-census evidence.

The authenticated Python `main` compiles the source and invokes
`--premises-only`, then `--seconds 300` with no pattern, template or mode filter.
The separate harness executes its actual parsing, call selection and receipt
checks, substituting only compilation and native-process results. Admission
requires exactly 82 cycle records with exactly the expected `(pattern,ID)` set.
Length plus set equality excludes duplicates and omissions. Every cycle must
have `exhausted is True` and `found is False`; the last record must report all
requested orbits exhausted and count 82. Both path controls and all three
premise records must also pass. The controls-only path invokes only that mode
and emits `complete_orbits=0`.

Twelve synthetic receipt mutations exercise these conditions. The actual
`run_json` subprocess boundary separately rejects a nonzero exit, malformed JSON
and a real timeout. These are tests of the caller, not authenticated proof
receipts. The wrapper does not authenticate arbitrary supplied logs or verify
every statistics field. Its scientific interpretation requires the pinned
native producer and that producer's independently justified mathematics.

## Reproduction

Python 3.12 or later, an installed C++17 compiler, and no Python dependencies:

```sh
python3.12 -I -W error -B scripts/research_package.py \
  --package research/connector-caller-exhaustion-audit
```

Direct commands work in a Git-free exported source tree:

```sh
python3.12 -I -W error -B research/connector-caller-exhaustion-audit/verify.py --controls
python3.12 -I -O -W error -B research/connector-caller-exhaustion-audit/check_caller.py
python3.12 -I -O -W error -B research/connector-caller-exhaustion-audit/check_boundaries.py
```

`CXX` selects an installed compiler and flags. `TMPDIR` can direct all temporary
builds to a session-owned directory. Compilation uses C++17, `-O2 -Wall -Wextra
-Wpedantic -Werror`. Four compiled semantic mutants must fail. Nine source and
adapter controls reject changed input bytes and absent/ambiguous hook sites.
`RESULT.json` records exact counters, environment and commands. The dedicated
hosted workflow adds address/undefined-behavior checking. Hosted CI is separate
from local evidence and is reported at the exact publication head.

## Engineering boundaries

The inherited source is frozen. Its recursive generator and dynamic collections
are retained only inside this bounded audit. Recursion depth is at most eleven;
the independent coefficient table has 11 by 81 entries. Every new loop has a
finite source-derived bound, and new functions stay below 60 lines. Temporary
files and compilation/process resources have scoped owners and timeouts.
Python runtime allocation and C++ library/table initialization are unavoidable
runtime deviations from fixed allocation; the input is exactly three pinned
files, no unbounded network or user-controlled search domain. Ordinary and
optimized Python use explicit executable checks, never disabled assertions.

A single simple `main` rename permits inclusion of the frozen C++ source.
Exactly three source substitutions have explicit uniqueness checks and negative
controls. Python `runpy` loads only the authenticated caller and package-local
checker; two explicit process test doubles are bounded substitution points.
These metaprogramming/test-dispatch deviations avoid modifying predecessor code.
They are not a reusable production plugin system. Native diagnostics run at
every build; Ruff and formatting checks cover all new Python. A future
production successor should expose an ordinary observation interface before
adding more source substitutions.

## Scope and credit

Task `census-pruning-audit`, priority revision 6, refined to the successor's
remaining gap-enumeration/caller implication. Earlier parity, capacity,
representation, propagation and recursive search results are not recounted as
new. The first working baseline command passed source bindings only.

Credit conorholds for the actual covering-code reduction and native/Python
sources; Nick Petalas/PR3276 at
`b7b576c0fc8bf016d67af7f3fa6a4927bc2b1df8` for the explicit caller handoff;
Krzysztof Wójt/PR3261 at `aa47cff758c956304327f1fc67dac61e970cfb3d` for the
representation audit; Nick Petalas/PR3244/3224 and the retained propagation and
capacity lineage; Nicholas Stone/PR2973 and its corrected-census successors;
Ross Richardson/PR943 and Douglas Colkitt/PR1185 for the singleton connector
model and predecessor bounds. Ytrehus, Struik, Davydov, Marcugini and Pambianco
retain credit for the coding/classification premises, which are not checked
here. The original sources retain their full notices. New work by Nick Petalas
is Apache-2.0. Automated drafting and implementation support was used; no
independent human or formal-kernel review is claimed.

## Open next questions

1. Independently validate the complete native B exclusion, with explicit source
   and environment binding. That is the remaining scientific search obligation,
   not answered by this caller audit. Start with the registered predecessor
   replay under a separately approved resource budget. An independent solver
   or implementation must not count timeouts as exclusions.
2. Independently audit the published coding/classification-to-walk reduction.
   It is needed before this collection of local checks can support the complete
   f(7) theorem. Start with the cited literature and the exact transcribed
   representatives, not another gap census. No full theorem admission is made.

No automatic construction expansion is justified. Native restoration,
physical routing, supplier moments, all-size compilation, precision/tape and
analytic multiplication transfer remain outside this local combinatorial audit.
Lean, Docker and the selected cold replay were not run.
