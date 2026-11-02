# Once-rounded rational gates with smaller arithmetic words

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped arithmetic construction and written proof with exact
finite corroboration. A two-coordinate Gaussian rational gate can compute
each output with one final nearest rounding, using signed arithmetic words
of width B+4C+2. Here B is the signed input-numerator width, and C bounds
the bit length of every coefficient component's numerator magnitude and
positive denominator. B>=2 and C>=1; the input fractional grid is arbitrary.

The cited rational FFT/Full allowance is 2B+8C+32. The new sufficient width
is half that allowance minus fourteen bits. [PROOF.md](PROOF.md) proves the
all-width bound by four-term common-denominator accumulation and bounded
binary multiplication/division. [kernel.py](kernel.py) implements it with
integer shifts, tests, additions, subtraction and comparisons. It uses no
machine multiplication/division instruction or intermediate rounding.
All four real inputs are saved before output writes.

This answers the arithmetic question left open by Armin Pourshafeie in
[PR5240](https://github.com/CrocSwap/integer-mult-bounds/pull/5240).
The result is a new implementation and resource bound, not an audit of the
predecessor's rounded-layer theorem. No new kappa or selected-frontier
change is claimed. The bound is sufficient, not proved minimal.

## Evidence and reproduction

The exact finite checks cover 50,625 four-term rows, 3,600 two-term rows,
31,744 binary divisions, 50 large-height rows and 768 complete complex-gate
cases. Eight semantic checks distinguish signed ties, product rounding and
input overwrite. Seventeen invalid-domain/overflow requests reject.
The largest tested data/coefficient widths are 2048 and 256 bits.
The word observer checks arithmetic intermediates at each operation.

The retained phase factory at precision four supplies an actual butterfly
with component height fifteen. For B=18, our construction uses 80-bit
temporaries; the cited formula evaluated at those same parameters gives
188 bits. This does not assert a particular full caller allocated 188 bits.
The verifier compares all four rounded output components with the retained
saved-input executor, on three grids and all 256 stated input combinations.

From the repository root, standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/integer-rounded-gate/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/integer-rounded-gate/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/integer-rounded-gate
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/integer-rounded-gate --check-source-history --check-modes
```

Other machines can substitute their CPython 3.12 path. Both registered
commands have a 120-second cap. The direct marker is
`PASS_INTEGER_ROUNDED_GATE`. Its generated stdout receipt binds every
package file by SHA256. Verification writes no package files. No receipt
is handwritten or committed. Source pins and the complete originating
card are in [SOURCES.json](SOURCES.json) and [TASK.json](TASK.json).

## Scope and credit

The theorem concerns arithmetic data words, given supplied coefficients.
The executable accepts 2<=B<=2048 and 1<=C<=256. Its word observer uses
host arithmetic to detect overflow; it is not a physical machine emitter.
Output values fit W=B+4C+2 bits. Returning them to B-bit data storage still
requires the caller's separate amplitude contract. No total-live-storage,
runtime or bit-tape improvement is claimed.

Coefficient preparation, its local temporaries, reversible cleanup, actual
instruction encoding, tape movement, all-size compiler funding and supplier
admission remain open. All five selected framework assumptions remain.
No selected scientific replay, native/Lean/Docker build, independent human
review or proof-kernel acceptance is claimed.

Credit Armin Pourshafeie / apoursh for PR5240's explicit arithmetic seam;
Jose Manuel / jmbarrancoml for the rational executor, phase producer and
coefficient/temporary contracts; Vlado Vojdanovski for the schedule;
Chafik Boukhalfa for phases; Brian / JoyboyBrian and James Reed for the
retained cut/allocator work; Cinna Davis and the numerical/compiler lineage.
Common-denominator arithmetic, long multiplication/division and nearest
rounding are classical. Nick Petalas's PR5940 concerns conditioned operator
interpolation; that theorem and its follow-up question are not extended.
Predecessor files and their credit lines remain unchanged.

Base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priority revision eight, selected PR6030. The source-binding baseline passed.
The supplier-boundary-audit card explicitly changes to this constructive
arithmetic side result, because a missing local kernel separates stored-state
bounds from an implementation. This does not change a supplier family or
admit a new one. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361639)
reserves the same scope.

Live claims, local reservations, open/account PRs, main formula/object
searches, merged searches and the cached card report were checked. The
cache covered 370 open PRs and 6,284 Discussion records, with complete
remote pagination. Its sparse local corpus covered 115 of 8,917 notes;
relevant packages were materialized and main README searches supplemented
it. Arbitrary historical diffs and unpublished work remain coverage limits.

## Open next questions

Bind this kernel to one complete Full allocation and charge its exact live
word count, source snapshots, output staging, bit operations, cleanup and
tape movement. Start from one emitted two-wire call and its proved input
and output amplitude bounds. A physical arithmetic/ownership contract and
the complete caller invoice remain missing. The present maximum word width
does not settle those costs. No further optimization is reserved.

## Code constraints

Foundational Thinking fixes grid numerators and coefficient pairs before
arithmetic. Build the Lever supplies the retained kernel and independent
Fraction oracle. Prove It Works requires actual source-produced gate
conformance, overflow checks and rejection controls.

All new functions fit sixty lines. There is no recursion or generated code
in the new kernel. Each multiplication scans at most W-1 multiplier bits;
each division scans exactly W-1 positions; W<=3074. Gate loops have four
iterations. Fixed finite verification domains bound all other loops.
Explicit exceptions retain checks under optimized Python.

Power of Ten rule 3 deviation: CPython allocates integers and containers
during this bounded reference execution. Fixed B,C limits, four-coordinate
state and one current row bound the kernel's live collections. A static
memory backend is needed before a fixed-allocation claim. The width
observer's capacity and operation counters are verification metadata outside the
claimed data-word program. Rule 8/9 fixture deviation: the unchanged phase
factory executes its authenticated interval source; imports and dispatch
are limited to the five declared inputs and their standard-library imports.
Its preparation is outside the arithmetic-width theorem. The 120-second
registered timeout also bounds this finite fixture. Warning-strict normal
and optimized replay and AST/function-size checks supply local diagnostics;
no separate type analyzer or linter is claimed.
