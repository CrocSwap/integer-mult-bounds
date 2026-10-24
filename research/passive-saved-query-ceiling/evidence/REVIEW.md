# Independent review of the fixed passive saved-cut gate

Verdict: **PASS with the two retained written clarifications.** The exact macro dependency trace and all 5,408 source-pair grades reproduce independently. The large-width argument is valid for the fixed finite columnwise Clifford alphabet, with the scope stated below. It rejects this passive recovery proposal as an identity required at every positive width; it does not assert impossibility at every small finite width.

The six-file author freeze is authenticated by `FILES.json` SHA256 `a7d684b92f2bc54ac2a201dcabdc52c549dba8089a1141bb54167806a92d6deb`. In particular, the reviewed grade checker is `5e1e3f18033cf6482094edb050ff4274515b85e7bb333647b41ad38d4f172a68`, its receipt is `8267ff814fd7fa86638b6ce6384f0ac717a341d871bd302742de6aaf8ba00b6d`, and the proof is `02ccd0a9d93b381286e441afa4c28a902db153a4d0dae4d761cf813ede9f2f6d`. The unchanged original freeze is accompanied by:

* `UNIFORM-ALPHABET-ADDENDUM.md`, SHA256 `f51448dc7551e8b61613c642d9487282f06e2ddc6274b1693276920688d5496f`;
* `OWNED-RESET-CLARIFICATION.md`, SHA256 `bd30b35ff2364fb6b430e31bd6cc3de969454a3e81d73adf4fc2f633ac0d9484`.

The first makes the finite alphabet uniform in width, including width-dependent decoder coefficient/control choices. The second avoids reading the original cleanup bookkeeping as a universal reversible-uncomputation requirement. Direct owned CLEAR/reset can be granted whenever the model permits it, even for free; the negative result does not use a cleanup-cost lower bound. These are written qualifications, not a new computation or search.

## Exact source and dependency trace

The source is PR4948 at `86e474038e05f99a76d41f71d81946ad2327e4a4`. Its actual signed K words, nonsymmetric F, and Clifford primitives are retained byte-exact in `inputs/`, with upstream paths and hashes in `SOURCES.json`. The transpose is used: `C_s=diag(K_s)^-1 F^T diag(K_s)`. This review inherits the source's normalized reverse primitive `diag(D_s,D_s)U(-Q C_s)`; it does not replay a new all-owner native raw dual. The same exact K/F source bytes and their all-112 absolute-phase commutation with full F9 were already independently checked in our preceding mixed-gate review. No native phase campaign is silently promoted here.

The declared word retains the standard scalar right/left boundaries, paid initial IDLE, bridges, and signed swaps. The three thins remain, in chronological order, `L(C1 Q^-1)`, `L(Q^-1 C1)`, and `L(Q^-1 C3)`. The nine specified boundaries and three actual paid responses give 39 observed bank fields. The responses are saved in their actual order; a saved result is a field value, not an oracle accepting replacement inputs.

My `independent.py` uses our separately written D-left semidirect-product interpreter, rather than the author's D-right interpreter, span routine, or grade checker. For original arbitrary main input bank 0, it reproduces all 39 coefficients, comparing author receipt terms only after independently converting their normal form. Their exact census is:

| Original-input-0 path | Number of observed bank coefficients |
|---|---:|
| zero | 27 |
| I | 2 |
| Q^-1 | 1 |
| C1 Q^-1 | 1 |
| Q^-1 C1 D1 | 7 |
| -Q^-1 C1 D1 | 1 |

FULL1 cancels this original input's X coefficient. The inverse bridge cancels its pair-1 Y coefficient before FULL3, so it receives no D3 factor. Both later paid query responses have zero coefficient on this original input. The original input is tracked before the right scalar boundary, so this reasoning does not relabel a dependent later field as an independent source.

The preliminary 273-generator bank-scalar span is correctly separated from the stronger port-level necessary condition. I reran the frozen span and its uncoded control but do not rely on that bank-scalar negative as a proof about arbitrary per-port scalar controls.

## Actual all-pair grade audit

The actual F diagonal is 12 at ports `[0,7,20,23,86,93,108,111]` and zero at the other 104 ports. For every zero-diagonal source port j, the late observation has exactly 52 supported output ports i, with coefficient

`(F^T)[i,j] Q^-1 K_i^-1 K_j D1`.

I composed each literal word from the pinned source K words in chronological order `D1`, `K_j`, `K_i^-1`, `Q^-1`, and used a separately written GF(2) rank routine on its signed tableau. Every one of the 5,408 words has Fourier grade 7. All pair indices, rational coefficients, source supports and grades match the author receipt, not just its final histogram. The nine-axis calculation embeds with the other fresh eight axes as identity spectators in ambient 17.

The earlier observed words have grade 0 or 1: I is grade zero, Q^-1 is grade one, and each term of C1 Q^-1 is a monomial left factor times Q^-1. The required original first-bank target `D1 Q^-1` has grade 9. Positive controls verify that all eight nonzero diagonal source terms expose grade 9, as does the uncoded identity frame. Artificially homogenizing an off-diagonal K factor also produces grade 9; hence the reported grade-7 census is tied to the actual distinct native port frames.

Multiplication on the left by a monomial Clifford preserves Fourier grade: it applies an invertible linear map to the X components of the images of the Z generators. Every actual C1/C3 entry is a scalar multiple of a monomial Clifford, and every allowed passive finite code expansion is a scalar sum of monomial left factors. Arbitrary per-port scalar controls, linear COPY, and extra decoder arrays cannot create a new pure address word outside this support. Mixing independent source owners cannot repair the missing coefficient of one source owner; isolate that arbitrary owner by setting the others to zero. Thus, for each of the 104 source inputs, all supported pure words retain grades in `{0,1,7}` after the allowed passive controls.

This is not a statement about the grade of a sum of operators or about linear independence of one-column Clifford matrices. It is a statement about pure-word support, combined with the following tensor separation.

## Uniform large-width argument

All one-column address words lie in the Clifford group on fixed ambient 17, whose projective quotient is finite. Fix representatives for this whole finite universe, including the target. Actual root phases are retained or absorbed after tensor lift as scalar phase-to-f coefficients; grade is invariant under such phases. This gives a finite projective alphabet independent of f, even if scalar coefficients or permitted passive control choices depend on f. Arbitrary f-specific noncolumnwise address maps are outside this premise.

For distinct projective unitary representatives A_r and A_s on dimension d, the normalized Hilbert–Schmidt overlap satisfies `|tr(A_r* A_s)/d|<1`. The Gram matrix of the pure f-fold tensor powers has diagonal 1 and off-diagonal entries equal to these overlaps raised to f. If there are N representatives and the largest off-diagonal modulus is rho<1, then `(N-1)rho^f<1` makes the Gram matrix strictly diagonally dominant and positive definite. Hence the tensor powers are linearly independent for every sufficiently large f, uniformly over the allowed reconstruction coefficients.

The grade-9 target is in none of the observed grade-0/1/7 projective classes. Therefore it cannot be expressed by these passive observations for sufficiently large f. An identity claimed at every positive width is consequently excluded. No one-column matrix-independence claim, tensor-of-a-sum substitution, or fixed small-width counterexample is needed. The source scalar owner coefficients occur once outside each pure-word tensor lift; they are not themselves raised to f.

## Ownership, cost and limits

The four original main banks comprise 448 arbitrary fields. The two native invocations retain all 816 independent inherited helper jobs once. An all-snapshot implementation would add at most 4,368 dependent observed fields; these earn no new arbitrary-input reward. The negative argument grants all new storage, initialization, COPY, scalar operations, finite code operations, and permitted owned CLEAR/reset operations for free. It does not require an inverse-uncompute reset, and it does not discard independent original main/helper data.

The preexisting optimistic target/paid moment remains only a relaxation. No endpoint is recovered here, so no strictification/compiler reserve or positive kappa is funded. This review does not recalculate a new profile or infer a better offer from the count of missing directions.

The result covers **passive observation and left decoding of this exact word**. It excludes active feedback into a later paid gate, native internal prefix taps, other cuts or thin placements, additional Gaussian calls, changed targets, arbitrary noncolumnwise width-dependent routing, and a complete physical caller. In particular, injecting a saved response into a future paid gate changes the trace and needs its own contract; it is not rejected here.

## Execution and provenance

Both frozen author checkers passed normal and optimized read-only replay and matched their respective receipts. Our independent trace and all-pair grade checker passed normal and optimized execution with identical output. Verbose JSON was captured in private review outputs; routine replay need not print the 5,408-word receipt. The independent checker is Git-free after the source bytes are supplied and writes nothing by default; only `--emit` writes its own receipt.

Own outputs only were created. No shared source, frozen predecessor, PR, discussion, or remote ref was changed. Credit: A's passive-cut/grade construction, G's separate predecessor work, the PR4948/4940/4933/4935/4943 source authors, and our independent Codex gpt-6.1-sol review. Source licenses remain present in their pinned bytes; the independent scripts include substantial AI assistance.
