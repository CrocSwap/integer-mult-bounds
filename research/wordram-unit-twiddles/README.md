# Save 47,523 executed instructions in the bounded NTT multiplier

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped program-refinement proof with a source-bound finite
certificate. Replace each constant-one transform-twiddle reduction in David
Ganz / Dugongue's [PR #5466](https://github.com/CrocSwap/integer-mult-bounds/pull/5466)
by two literal Word RAM instructions. The replacement preserves complete
memory, including the scratch temporary, on every admitted input.

For transform size n, the static saving is exactly 141(n-1) instructions and
the executed saving is exactly 93(n-1). At n=512, all 1,533 unit-twiddle
sites are enumerated: static length falls from 507,701 to 435,650, and every
input saves 47,523 executed instructions. [PROOF.md](PROOF.md) proves the
all-input block simulation and counting formula. These are exact instruction
counts, with no runtime benchmark or optimality claim.

The original bounded multiplication theorem and residue-range invariants
are cited premises, not audit targets. Frozen source bytes remain unchanged.
This arithmetic refinement is separate from Nick Petalas's #5886 address
allocation and #6435 optimized-checklist portability. It does not extend
their open questions. Constant-one specialization and block simulation are
standard; the new contribution is the exact full-state rewrite and complete
charged saving for this literal program.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/wordram-unit-twiddles/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/wordram-unit-twiddles/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/wordram-unit-twiddles
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/wordram-unit-twiddles --check-source-history
```

Substitute another CPython 3.12 executable as needed. The direct verifier
prints `PASS_WORDRAM_UNIT_TWIDDLES` in a generated JSON receipt bound to every
package file and to all nine emitted refined-program hashes. It writes no
files. SOURCES.json authenticates the exact producer/runtime/proof inputs;
VERIFY.json declares all six external inputs for replay selection. A Git-free
export must retain those repository-relative input paths.

The finite checks cover all 65,537 local residues, nine balanced templates
with operand lengths 1,2,4,8,16,32,64,128,256, 36 full dirty-memory cases,
and five structural rejection controls. Both complete and local memory are
compared at every address represented by the executed direct-address programs.
The proof supplies preservation at every exterior address, since neither
program writes it. All original setup, constants, carrying, clearing and halt
instructions remain. The template census is not a complete length-pair census.

## Scope and coordination

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision
8. The selected-record binding baseline passed. TASK.json explicitly changes
the formal-interface-lemma card to this bounded compiler/cost side result:
there is no proof-assistant formalization or selected assumption discharge.
The selected complex supplier still binds, and its recursive rank invoice
differs from this kernel's ISA invoice. No new kappa is claimed.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19441308)
reserves this original arithmetic-refinement question. Live PR bodies and
handoffs, all-state #5466/Word RAM/NTT searches, and merged/main searches for
unit-twiddle and constant-specialization terms were checked. The overlap helper
reported complete live pagination of 744 open PRs and 6,864 Discussion records;
its sparse local note coverage was incomplete. Targeted main searches also
read the retained liveness and assertion-portability packages. No equivalent
arithmetic rewrite was found in that coverage; unpublished work and arbitrary
historical diffs remain outside it.

No asymptotic algorithm, unrestricted instruction optimum, independent human
or proof-kernel review, full machine formalization or selected consumer is
claimed. No Lean, Docker, selected cold replay or approximate FFT backend
check is part of this contribution.

## Open next questions

- Can one known nonunit twiddle use a shorter fully charged macro? First
  specify the constant and prove complete memory and cost equivalence.
  No such refinement is supplied here.
- Can an actual selected consumer use this kernel at a favorable complete
  cost? First name its sizes, conversions, restoration and charged machine
  model. The two interfaces and cost models are currently different.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Verifier constraints

The transformer accepts at most 600,000 direct-address instructions and
scans each finite list with a fixed list-length bound. The verifier accepts no
CLI inputs: its local domain is 65,537 residues, its template list has nine
entries, and each has four full fixtures. Source inputs are each under one
MiB. Functions stay below 60 lines; explicit exceptions keep every new check
active under -O. Warning-strict normal and optimized commands are registered.
There is no recursion, subprocess or network in the new code.

Power of Ten rule 3 deviation: CPython allocates integers, tuples, dictionaries
and source-produced plans dynamically. The fixed domains, program cap and
serial execution bound live data to a fixed multiple of one largest template;
no unbounded stream or concurrent plan cache exists. Rule 8 deviation: the
transformer emits a literal instruction list, required for this compiler
refinement. The bounded, authenticated input and explicit old-to-new label
map constrain generation; the full macro and instruction-simulation checks
inspect the emitted result. There is no Python eval, exec or source rewriting.
Rule 9 deviation: the
authenticated producer and its exact ISA interpreter are imported from their
fixed declared source directory. Calls have these named targets only. The
original interpreter's nested helper and bounded instruction loop remain
unchanged; this package adds no dependency on arbitrary callback dispatch.
An embedded fixed-allocation implementation and source-to-machine theorem
would need a separate implementation. Normal/optimized replay and the source
hash gates verify these scoped controls; no external static analyzer is claimed.

## Credit

David Ganz / Dugongue supplied PR #5466's bounded multiplier, ISA interpreter,
NTT schedule and original correctness/cost arguments. Shilun-Allan-Li and the
tcslib contributors, Thomas Ahle and FastPoly, Bas Spitters and CatCrypt, and
Brett Saiki and mpfx retain the original interface credit and the predecessors
named in the unchanged source NOTICE.txt. The new arithmetic refinement,
simulation proof and verifier were produced by Nick Petalas. No predecessor
notice or credit line is edited.
