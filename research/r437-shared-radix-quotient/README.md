# Share the radix traversal at the fresh-row quotient port

This contribution is produced by Nick Petalas. Apache-2.0.

## Result and boundary

The opt-in [adapter](adapter.py) retains every division by the original small
constant q while sharing one encoded radix traversal across the fixed m^2
coordinates of `fresh_rows.quotient`. For every valid fixed context, it returns
the same quotient on exactly the same positive row integers, preserves borrowed
binary Counts and residue words with their heads, and disposes of temporary
state. The successful old-minus-new residue action vector is exactly

    (m^2 - 1) rho(q,w,L),

where rho is one complete original `radix_power` traversal, including validation
and cleanup, at fixed residue width L. The complete Count record action vector
and ordered division arguments, input widths and remainders are identical. The
maximum simultaneous residue inventory is unchanged. These are a scoped
refinement and an exact source-action invoice, not a physical-machine speedup
or a new multiplication bound.

This answers Open next question 2 of
[Brian's #4794](https://github.com/CrocSwap/integer-mult-bounds/pull/4794),
head `4cc9b9719fdab59f0f33243b9c323fe4d69346f5`. That predecessor compiles the
large divisor q^(m^2), reducing Count divisions while incurring large arithmetic
and control setup. This adapter uses q throughout, requires no large-divisor
construction, and reduces only repeated radix traversal. A complete paid
comparison between the alternatives remains open.

ToikY's [#4025](https://github.com/CrocSwap/integer-mult-bounds/pull/4025)
already gives this loop-interchange method and traversal invoice for directory
production. Chris R #4062 extends sharing to Context construction, and Tekalign
#4077 extends it to variable-exponent geometry. The new contribution applies it
to the actual quotient port, with complete local invoice and restoration
checks. Neither the general technique nor primitive traversal counts are new.

## Scoped proof

Fix a valid source context with prime q, positive fixed dimension m, positive
fixed family factor F, positive fixed low-code factor G, and encoded modulus
q^w with w>=1. The modulus fits the original Ring format with its high-bit
margin. All Count tapes are independent of Ring residue storage. Let R denote
the borrowed positive row integer and D=m^2(w-1). Composite q>=2 also works
when the same valid encoded-power representation is supplied.
Borrowed inputs enter at the source API's canonical head position 1.

Both programs copy R and divide by F and G, requiring zero remainders. The
original then executes m^2 complete radix traversals, each yielding w times.
Each traversal skips its first yield and divides the Count by q at its other
w-1 yields. The candidate executes one traversal, skips its first yield, and
performs m^2 divisions by q at each remaining yield. Thus both Count sequences
are `divide(F), divide(G)` followed by exactly D copies of `divide(q)`.

They use the same deterministic Count code and initial tape, with no other
intervening Count mutation. Induction on that call sequence gives identical
quotient tapes, division input widths and remainders at every division. This
also identifies the same first failed divisibility predicate on rejecting row
integers. Accepted inputs are exactly the positive multiples of F G q^D;
the returned integer is R/(F G q^D). The final nonempty test is retained.

For a valid Ring, a complete radix traversal restores every borrowed residue
word and head and erases its own words. The Count divisions use independent
record tapes. Moving traversals among Count operations cannot affect either
subsystem's arithmetic or head state. Each traversal therefore has the same
complete residue action vector rho. The old program performs m^2 traversals;
the candidate performs one. This proves the displayed saving. The identical
Count call sequence proves equality of the entire record invoice, including
returned-Count disposal when both callers dispose of their output alike.

All division constants and their bit widths are retained. In particular, the
high divisions still have q remainder states, with no q^(m^2) constant or
controller. Repeating a traversal increases total allocation calls but not its
simultaneous residue requirement. Count allocation/disposal is unchanged, so
peak simultaneous residue inventory is equal. A fixed m^2 scalar repetition
is inherited from the source; a physical implementation of that control is a
separate obligation.

The candidate uses `closing` to explicitly close the active radix generator
before closing its owned Count on a failing high division. In a valid context,
the source generator's existing `finally` restores residue state. The original
comparison runs on CPython 3.12, which also finalizes its abandoned iterator.
Malformed Ring/modulus contexts and the out-of-domain cleanup leak reported in
#4794 are outside the theorem and are neither repaired nor retested here.
Exception-time action savings are not claimed to equal the successful formula.

## Exact evidence

The first discriminating fixture has q=3, m=2, w=2, F=4,
G=|GL_2(F_3)|=48 and returned quotient 7. It saves 5,442 residue reads,
1,032 writes and 5,592 unit moves. Both complete Count bills are 495 reads,
111 writes and 456 moves, including output disposal. Both peak at nine live
residue words with an unrelated dirty word retained.

The eight-case suite includes q=2,3,5; m=1,2,3,64; w=1,2,3,4;
two m=1 equality cases; and m=64,w=1 with the exact GL64 low factor and
returned quotient 9475. This last local fixture saves 2,141,685 residue reads,
389,025 writes and 2,276,820 moves. These are the same primitive traversal
savings reported at a different port in #4025. All 247,343 Count actions remain
paid in this fixture. No m=64,w=2 comparison or selected caller is executed.

Every case independently computes R/(F G q^D), compares all division
constants/input widths/remainders and the whole local invoice, preserves an
unrelated dirty Count and residue word, and erases owned state. Eleven rejected
inputs cover zero rows, family/GL failure and every possible first high-factor
failure in an eight-division fixture. Four controls detect a missing division,
an extra division, a same-output implementation skipping validation at w=1,
and forgetting to charge the retained traversal.

The checker authenticates all eleven live source files before import, disables
`Word.inspect` during execution, and uses checks that survive optimization.
Fixture-only raw-cell snapshots and division observations add no source
operations. Generated JSON receipts include the invoices and SHA256 hashes of
all live inputs and package files. There is no handwritten receipt and no
predecessor package verifier is run.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/r437-shared-radix-quotient
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/r437-shared-radix-quotient/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/r437-shared-radix-quotient/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/r437-shared-radix-quotient --check-source-history
```

The final command checks committed publication bytes. The manifest registers
both direct modes with separate 60-second limits. Each emits a source-bound
JSON receipt followed by
`PASS_R437_SHARED_RADIX_QUOTIENT cases=8 rejections=11 controls=4`.
Output is stdout only; no package or input files are regenerated.

## Sources and verification limits

All live inputs are unchanged at canonical main
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
[SOURCES.json](SOURCES.json) records Git blob IDs and hashes. Pending #4794 is
a pinned written handoff, not a runtime or Git-history dependency. No pending
branch must be fetched for reproduction.

The harness supplies the attributes consumed at this port with actual Ring
and Count implementations, exact GL cardinalities and a structural context
object. It does not construct a full directory Context or execute Machine.node,
Program, the 9475 guard, field payloads, recursion or admission. An identical
returned Count is sufficient for an unchanged consumer under the stated
contract; it does not certify that entire consumer.

The measured interval starts with borrowed Counts and context live, executes
the quotient, and disposes of its returned Count. Context/input construction
and final borrowed-state disposal are outside it. Those fixed endpoints agree
in the matched harness. Counts are exact source Tape/Word operations, not
elapsed-time measurements, physical-machine steps or a compiler/allocator
tariff. No complete supplier, new kappa or full multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed. No Lean,
Docker or historical replay is needed or run.

Power-of-Ten scope is the new adapter/checker. The adapter uses fixed-coordinate
control around the existing iterator; a valid q^w fitting L bits has w<L.
Checker inputs are fixed, functions are below 60 lines, instrumentation is
restored in `finally`, and all checks survive `-O`. Python and the inherited
variable-width Tape/Word routines allocate managed objects; no allocation-free
implementation is claimed. The suite bounds m<=64,w<=4, row width<=6507 bits
and Arena capacity 32. Bounded callbacks and raw-cell inspection are checker
instrumentation deviations, outside the proposed runtime algorithm.

## Open next questions

1. Compose this quotient with an actual admitted caller, preserving its stock
   guard, payload and cleanup. Start with an existing admitted root fixture;
   the local structural context is not that caller.
2. Price the small-q divider, encoded radix iterator and fixed-coordinate control
   on a complete physical machine, then compare with #4794's large-divisor
   alternative under the same amortization/storage contract. Unknown costs
   prevent a whole-machine saving claim.

## Credit

David Arias #2753 supplies the quotient, Count and cardinality runtime, within
Jose Manuel's retained caller/word/record lineage. ToikY #4025, following ywz65
#2590/#2566, supplies shared traversal and exact source-action accounting.
Chris R #4062 and Tekalign #4077 supply its Context and geometry extensions.
Brian #4794 supplies the explicit alternative-divider handoff. Nick Petalas
#3246, Tekalign #3264, Mihir Srivastava #4685 and codyw912 #4734 retain stock,
entry and ordinal credit. R437/OQ4 construction and caller work retain the
predecessors credited in those packages, including ywz65, unpaidmoon,
ai-nanachi, Ali Romman, Sagar Thakrar, Rohan Arun, zxv and Ross Richardson.
Existing source files and credit remain unchanged.

The new opt-in quotient-port refinement, proof and checker are produced by
Nick Petalas. No literature-priority claim is made for loop interchange.
