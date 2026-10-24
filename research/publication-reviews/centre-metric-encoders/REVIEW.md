# Independent publication review: centre metric encoders

The package passes this local publication review. No open mathematical or
replay defect was found in the stated scope. One claim limit needed a
correction: the transpose companion is a native interface, but its selected
sixteen outputs do not decode the original reciprocal reader L. The final
README now states this limit.

The reviewed package manifest SHA256 is
`f7aa100a7389e94518b980fe93e91773602f53b5d782a7c677612be4c9790866`.
The manifest covers 253 files. The 185 immutable inputs, the runner, and
the portable signed checker are unchanged from the cold replay. The proof
and result files were not edited. The coordinator must still check the
final PR description, commit links, GitHub rendering, and publication
readback. This review did not create a commit, push, PR, or frontier change.

## Reproduction and evidence

The reviewer copied the package to `cold/package` in this review directory.
The replay output is in `cold/replay`. The command ran one check process at
a time with the numerical thread limits set to one. The checkers use Python
exact arithmetic and the standard library. The measured run used Python
3.14.7 on macOS arm64. The sum of the fourteen check times was 74.053 seconds.

All seven selected checks passed in normal Python and in optimized Python.
Every computed result receipt matched its frozen receipt byte for byte.
The two Python modes also matched. The replay checked all 185 immutable
source hashes before and after execution. Compressed payload hashes also
matched. See [the cold receipt](cold/replay/REPLAY.json).

The checks include eight complete C24 native words and thirty signed-code
or transpose-interface native words. Each full word was checked on 640
arbitrary complex input fields. The 416 auxiliary fields remain unchanged
at this local interface. The C24 check also checks eight distinct new H8
operators on all 512 spatial columns. The signed words reuse exact pinned
phase records; they add no new spatial operator.

The review used a separate small exact engine for the main matrix claims.
It imports no package code. Its receipt is [DIRECT-CHECKS.json](DIRECT-CHECKS.json),
and its source is [direct_check.py](direct_check.py). The package and source
checks are in [PACKAGE-CHECKS.json](PACKAGE-CHECKS.json) and
[check_package.py](check_package.py). The exact commands are in
[COMMANDS.sh](COMMANDS.sh).

## Mathematical checks

The original-reader theorem has the required scope. For a row space of
dimension r with Gram rank s over an odd finite field, its radical has
dimension r-s. A containing nondegenerate coordinate space therefore has
dimension at least 2r-s. Orthogonal encoding preserves the row rank and
Gram. Exact recovery from selected coordinates forces zero coefficients
outside those coordinates. This last step also holds for nonlinear
recovery because all encoded output coordinates can vary independently.
Arbitrary borrowed inputs, tensor products with identity, and the stated
dyadic input and output frame changes preserve these premises.

The direct check obtains `V V*=diag(12 I8,8 I8)`. Realification gives row
rank 32 and Gram rank 16 modulo three. The lower bound is thus 24 complex
coordinates, or 24N complex coordinates for arrays of length N. It counts
capacity. It does not apply to unrestricted register names, promised zero
inputs, approximate recovery, or general nonunitary codes. The actual C24
matrix is unitary in both product orders. Its exact decoder has support
24 and recovers V. The proof of its native support uses the stated Haar
normalization, dyadic reflection, and output assignment.

The reciprocal reader is a different matrix. The direct check obtains
`L L^T=diag(10 I8,7 I8)` and `L K L^T=diag(4 I8,2 I8)`. Its real row rank
is 32 modulo three, five, and seven. Its real Gram rank is 32 modulo three
and 16 modulo five or seven. The 24-coordinate Euclidean-unitary bound
therefore uses five or seven for L. The old modulo-three instance cannot
be substituted. The signed code avoids the Euclidean-unitary premise.
It captures `E-P`, of rank sixteen, rather than `E-I`, of rank thirty-two.
Physical P changes 32 ports and has 160 nonzero entries. Its paid scalar
word costs 728 real primitives before view costs.

The signed dual algebra includes both input banks. From `A K A^T=G`,
one gets `A^-T=G^-1 A K`. The complete two-bank correction is
`diag(G,G) F_A^-T diag(K^-1,G^-1)`. The ordinary target baseline is
arbitrary, so its input metric cannot be omitted. The complete replay
rejects that omission. It also checks the signs, selected-bank relabeling,
actual endpoint adapters, and chronological inverse-adjoint. The original
C transpose has 32 ordinary support violations. The paid 80-primitive
selected-pair suffix produces Cbar and repairs this support defect.

The review found a scope ambiguity in the summary of the three code
families. The unique decoder `L Cbar^-1` uses the sixteen selected outputs.
In contrast, `L Cbar^-T`, which decodes L after Cbar transpose, uses 96
outputs. This does not refute the transpose native word. It shows that its
sixteen selected outputs are a different interface. The final README
separates these claims and retains the paid recovery of individual L
readers from Cbar. No frozen proof was changed.

The C24 component proof requires complete complex-linear blocks at a
common complex frame. Individual real-component ADDs need not preserve
that frame. The native checker checks block matrices and boundaries and
excludes native or map events inside them. The signed words have real
scalar coefficients at their required common frames. The inverse-adjoint
keeps each exact unitary native operator in its chronological position.
The checks bind its global phase, field, and adapters.

The general signed-family proof works for every `k=2^r`, including k=1.
The displayed Walsh contrasts and the three remaining rows give the
diagonal Gram with dyadic-unit entries. The literal six-instruction middle
word gives the stated basis. The two extra butterflies give the prices
86, 96, and `10kr+76+4r` in the three stated cases. The finite checks through
k=64 are controls for this proof, not its all-size justification. The
package correctly says that the bridge review supplied the basis and then
checked the root's word and price. It does not call that a second
independent proof of the same basis. General native row placement remains
open.

The rational comparison uses the first actual C16 packing. Its separate
odd scans stay in the invoice. The complete words cost 5702 dyadic real
primitives plus sixteen multiplication-by-three and sixteen
division-by-three real scans in each direction. The exhaustive quartet
test accepts 729 of 6561 residue inputs in each direction. The prefix
conditions depend only on these residues, which justifies the exact
Gaussian-dyadic division domain.

The direct matrix calculation gives `trace(C16)=(11+7i)/6`. The trace of
`3C16` modulo three is `1+2i`, which is nonzero. Thus its residue is not
nilpotent, and every positive power has a nonzero residue. Together with
the entrywise upper bound, this proves `h3(C16^m)=m`. The adjoint proof is
the conjugate argument. The complete residue has Gaussian rank four, not
one. Rank one applies to a single quartet numerator. The matched inverse
word retraces the forward word, so the matched pair has prefix odd height
one. This does not bound unmatched repeated calls. The root-grid method
still requires a dyadic endpoint on every completed recursive child's
roles. All 96 ordinary C16 diagonals are nonzero, so this scalar packing
does not have the current C24 native realization.

## Costs and unresolved composition work

The replay derives the local invoices from the literal words. C24 costs
16020 real scalar primitives. The signed C, Cbar, and transpose-interface
raw words cost 9988, 10068, and 10324. Their metric-selected duals cost
11252, 11284, and 11156. The Q-entry native rank mass is 1792. The I-entry
mass is 1816 for C24 and 1808 for each signed or transpose interface. The
side-map counts are upper bounds, not finite map execution prices.

The package supplies no complete routed caller, saved-record restoration,
terminal decoder, recursive helper host, complete precision bound, or
complete supplier cost. The local auxiliary identity is not a recursive
hosting proof. No complete kappa improvement follows. The refreshed
selected record at main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51` names
PR #4470 and `60403/20000000`. The final provenance file explicitly marks
the reviewed words as historical local constructions and does not apply
them to that selected construction.

## Portability, controls, and credit

The signed-checker adaptation changes only its source-directory binding
and its absolute source-path resolution. The reviewed diff preserves all
arithmetic, original payload pins, endpoint checks, phase checks, invoices,
and negative controls. The cold run's file-access records stay within the
copied package, check output, or Python runtime. The control that tries to
read outside those paths fails at the stated check in both modes. The
explicit false-requirement control also fails in both modes. No Python
file read by the checks contains an `assert` statement that optimization
could remove. Some files are read only to verify their hashes; this is not
a claim that every read file was imported. The audit hook is a
reproducibility check, not a security sandbox.

The reviewer checked all 185 immutable inputs against their original
campaign bytes. The retained odd-grid source, Apache license, and upstream
NOTICE match the pinned local Git objects at `bce54fb3`. The source notice
credits icekylinx for the stopped product-ring and grid work. The final
package states that credit next to the retained source.

The refreshed PR #3133 README and retained credit record name dcharb78 for
the coupled folds. The PR #3148 README names Jeremy Diviney for its
packing exchange, integration, and verification. The PR #2588 notice
separates Cinna Davis's dirty-borrowing method, Rohan Arun's new package
work, Jeremy Kothe's retained methods, and the earlier lineage. The review
checked those refreshed source hashes against the retained immutable
GitHub readback records. It did not infer authorship from a PR submitter
account or attribute every inherited compiler file to one person.

The review did not rerun the archived producer emitters, all historical
predecessor suites, the selected frontier, a complete recursive supplier,
or a Lean formalization. It did not repeat the old spatial interpreter for
unchanged signed phase records. Final GitHub link and rendering checks
remain with the publication coordinator. No fragile code workaround was
introduced into the package.
