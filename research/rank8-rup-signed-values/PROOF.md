# Direct signed-literal replay equivalence

Claim type: scoped implementation-equivalence proof with exact finite conformance
and local performance evidence. This contribution was produced by Nick Petalas.
No new decoder theorem, supplier, kappa or multiplication theorem is claimed.

## State relation

The predecessor stores one ternary value `a[v]` per variable `1 <= v <= n`.
It evaluates a literal `l` as `a[abs(l)] * sign(l)`. Replace this by a list `s`
of length `2*n+1` satisfying

```
s[v] = a[v]
s[-v] = -a[v]
```

Python translates index `-v` to `2*n+1-v`. The positive slots are `1..n` and
the negative slots are `n+1..2*n`; they are disjoint and in bounds. Slot zero
is unused. Thus direct lookup `s[l]` equals the old literal value for both
signs, including the unassigned value zero.

To assign literal `l` true, set `s[l],s[-l] = 1,-1`. This preserves the state
relation whether `l` is positive or negative. To erase its trail entry, set
both slots to zero. The empty initial table satisfies the relation. The case
`n=0` has no legal nonzero literal and is unchanged.

## Trace induction

`adapter.signed_source` changes exactly one authenticated function. It makes
seven bounded text replacements with checked occurrence counts: allocation,
removal of the old value helper, its two read sites, all three trail-reset
sites, and the two assignment sites. All source outside that function remains
byte-identical. Missing or changed replacement sites fail before execution.

Induct over the original propagation trace. Corresponding seed literals have
the same value by the state relation. A conflict takes the same early exit
and clears the same trail. A new assignment updates both representations
consistently and appends the same literal to the same queue and trail. Each
clause visit therefore sees the same sequence of literal values. It takes
the same satisfied, multiple-unassigned, unit or conflict branch. Unit updates
and all normal-exit resets preserve the state relation. Consequently each
propagation call returns the same conflict decision and resets to the same
empty assignment.

The parser, clause database, occurrence lists, top-level units, proof order,
deletions, duplicate handling, checked count, limit handling and error strings
are unchanged. Induction over proof lines gives identical complete return
triples. Every accepted and rejected RUP call is identical. The complete main
program therefore takes the same later branches, constructs the same certificate
and emits the same stdout. This argument covers the legal input contract,
not only the finite certificate fixtures used in the measurements.

This is a representation improvement to the existing occurrence-list
algorithm. RUP soundness and the predecessor's mathematical decoder arguments
are cited premises. Neither is claimed as new or independently audited here.
The two-watched-literal algorithms in the P108/P110 successors and PR4360 are
prior alternative checkers; this change keeps PR1212's original visit order.

## Cost and finite evidence

The original complete P112 profile executes 205,432,164 `value` calls. The new
function has no value helper, so every one of those calls and their `abs`/sign
operations disappears on the equivalent trace. Parser range checks still use
`abs`; the claim does not remove every absolute-value operation. Assignment
and reset sites now write two slots. The ternary table grows from `n+1` to
`2*n+1` slots, an increase of exactly `n` list slots. The largest retained unit
has 4,032 variables, so the increase is 32,256 list-slot bytes on the measured
64-bit CPython host. No claim about total process memory reduction is made.

The exact small-domain checks compare the real original and transformed
functions, including parser errors, comments, deletions, duplicates, empty
clauses, proof limits and repeated propagation resets. The complete checks
compare every stdout byte and every certificate field for P112 and P120.
Across those two commands all eight pinned proof files and all 61/41 retained
check lines remain reached. All live inputs are hash-checked before loading;
corruption of each of the nine live files and a missing proof fail admission.
A changed adapter replacement site also fails admission. Counts are emitted by
the checker, rather than handwritten as a receipt.

Five alternating fresh-process measurements per side and live unit measure
complete CLI execution, including source authentication, geometry, every RUP
proof, rational calculations, existing rejection controls and output validation.
The benchmark refuses unequal stdout, unequal certificate objects, nonzero
exits, stderr or scientific failures. BENCHMARK.json contains the measured
samples, environment, source hashes and check counts. Profiling is separate
from the timed samples. No individual RUP microbenchmark is used as the
headline improvement.

## Engineering scope

All new loops range over pinned manifest entries, bounded source AST nodes,
fixed replacement sites or explicit finite test domains. Production replay
uses the predecessor's existing bounded files and variable domains. Each new
subprocess has a 150-second timeout and all registered checks have a
240-second outer limit or less. Source files are not mutated. Scratch is
owned by temporary directories or the benchmark's explicitly new output
folder. The verifier writes only stdout after temporary cleanup.

Power of Ten rule 3 has a managed-runtime deviation: Python lists, AST nodes,
strings and exact integers allocate dynamically. The changed ternary table has
an explicit `2*n+1` capacity; the original clause and proof storage are unchanged.
Rule 8 has a constrained source-adapter deviation: exact SHA256-bound source,
one AST-selected function, seven checked replacement entries and unchanged
surrounding bytes. No supplied code is evaluated beyond the pinned predecessor
and these replacements. Existing predecessor recursion and large main function
are retained unchanged, not claimed as Power of Ten compliant. New functions
stay below 60 physical lines. Warning-strict normal/optimized checks provide
the available Python diagnostics; no external static analyzer or proof kernel
is claimed.

## Limits and next question

Timings are local performance evidence and are not portable runtime guarantees.
Default adoption, complete Linux workflow timing, scientific supplier admission,
selected cold replay, native all-columns, ownership, compiler, precision/tape
and analytic recovery obligations remain outside scope. Independent human and
formal proof-kernel review are unclaimed. The exact next adoption question is
recorded in TASK.json. Frozen predecessor files and the selected frontier stay
unchanged.

## Credit

Brett Halligan / burntout76's PR1212, head
`57099cb5684f38877f31d149d598801671a633db`, supplies the complete verifier,
proof certificates, theorem and failure controls. Its DreamingOfClouds / PR717,
themilkman216 / PR968, GamingPuzzled / PR620, Mihir Srivastava / PR845,
woklerx / PR998 and related decoder lineage retain full predecessor credit.
Classical signed arrays, induction and RUP are not claimed as novel algorithms.
The new adapter, equivalence argument, conformance and complete-command
performance measurements were produced by Nick Petalas. Apache-2.0.
