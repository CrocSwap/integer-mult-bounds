# A carried elementary-word ledger for the selected binary compiler

## 1. Scoped theorem and source boundary

Fix the selected binary source at `e54523517d0f03e58352e647c403a5af3e525a57`, the complete dyadic bases accepted in #8092, and Ali Romman's literal `product.py` / `schedule.py` at #7828 head `03b572b3b9ab72c6ba67762e85e1630cda1daad5`. There is a source-compatible implementation of that finite generated grammar which carries an explicit elementary right word with every complete basis and route. Every word is chosen before q; every addition coefficient lies in `Z[1/2]`, and every scale is a signed power of two. The words and their inverses therefore work at every odd prime power.

This note gives constructive recurrences for their actual elementary counts, the earlier-target swap brackets, signed-scale expansion and all high-coordinate carries. It extends the finite 513-entry descriptor catalogue to the **generated syntax**, using carried words rather than a new short-pivot search at each node. It does not assert the generic bounds `2N^3,N^3,N^2` for the resulting longer words, materialize the astronomical selected template, or give a literal tape runtime. The selected exponent and retained physical/analytic premises do not change.

Classical elementary factorizations, direct-sum/Kronecker lifts and carry identities are not new. The contribution is their explicit source binding, the complete seed inventory, orientation-preserving constructor ledger, and correct source-sized invoice. #7840 supplies the existing full-GL route and carry interface; #8092 supplies the carried dyadic basis grammar; the preceding finite descriptor appendix supplies its 513 relative words. All original coupled-port adapters remain exact and shared between their coupled roles.

`INPUTS.json` authenticates the retained source bytes. Newly produced bases and descriptors are identified as generated artifacts, not as files present at the canonical source commit.

## 2. Right words, counters and complete seeds

An instruction is a coordinate swap, `x_i <- x_i+c x_j` with i distinct from j, or `x_i <- a x_i`. A right word for M sends a row x to xM. When x is represented as a column by the interpreter, its endpoint is **M transpose**. Accordingly, concatenating a right word for A and one for B represents AB; reversing the word and inverting every instruction represents M inverse. This convention fixes all product and guard orientations below.

Attach the vector

`c(W)=(t,a,u,d,h)`

to a word: swaps, additions, additions whose target index is earlier than the source, fixed unit scales, and expanded signed-dyadic scale atoms. A scale `+/-2^e` uses `max(|e|,1_{negative})` atoms from `{-1,2,-2,1/2,-1/2}`. Reversal/inversion preserves all five counters, including u, because it preserves each addition's ordered pair of indices.

The complete seed inventory is:

- all 636 literal raw frame bases `G=[B^t A^t]`;
- the eight complete reference bases, one for each rank 1 through 8, used by the accepted finite matcher catalogue;
- all 111 original coupled-port bases `U_i` from the selected receipt;
- full coordinate permutations and identities, generated directly.

The first three classes contain 755 fixed matrices. Each receives a genuine Euclidean dyadic word. For a seed M, reduce M transpose. In a remaining column, use integer Euclidean row additions and swaps to reduce its entries to their gcd after a common power-of-two denominator is cleared conceptually. The common denominator need not be applied as a physical scale. Any odd divisor of this gcd would make the remaining determinant vanish modulo that odd prime, contrary to its dyadic-unit determinant. The resulting pivot is therefore a dyadic unit. Normalize it and clear the column; recurse on the remaining block. Integer remainders decrease, so the construction terminates. Reverse/invert the reduction to obtain the right word for M.

For every accepted difference P, the preceding catalogue supplies `S_P=B_P B_R^-1`. Its relative word alone is insufficient to factor B_P. Concatenate it with the newly supplied reference word for B_R, giving `B_P=S_P B_R`. This explicitly closes that seed dependency for all 513 complete bases.

The short search using coefficients `+/-1,+/-2` is not used for new seeds or generated nodes. The unimodular matrix `[[7,2],[17,5]]` has first-column entries 7 and 17, with no unit entry or such short combination. It remains a rejection control; the Euclidean construction handles its transpose as a right-word seed.

## 3. Constructive word recurrences

All counters below are componentwise. Let A have dimension n and B dimension m. Let p(order) denote the number of transpositions in the emitted full permutation, equivalently dimension minus its cycle count. A permutation adds `(p,0,0,0,0)` to the ledger.

| Matrix constructor | Emitted construction | Counter recurrence |
| --- | --- | --- |
| AB | A word followed by B word | c(A)+c(B) |
| A inverse | Reverse and invert | c(A) |
| A directsum B | A on the first block, B on the second | c(A)+c(B) |
| A tensor B | m interleaved copies of A, then n contiguous copies of B | m c(A)+n c(B) |
| A directsum I | Same local word, full spectator identity | c(A) |
| T A T inverse | T, A, T inverse | 2c(T)+c(A) |

For the tensor constructor, use flat coordinate `(i,j) -> im+j`. A copy of A at fixed j uses the increasing map `i -> im+j`; a copy of B in block i uses the increasing map `j -> im+j`. Both preserve whether an addition has an earlier target. The endpoint is `(A tensor I_m)(I_n tensor B)=A tensor B`. Interleaved copies are not mistaken for contiguous blocks.

A tagged projector is `(B,r)` with `P=B E_r B^-1` and a right word for the **complete** B. Constructors carry:

- Conjugation by a carried T: basis TB, rank r, cost c(T)+c(B).
- Direct sum: first B directsum C, then a full column permutation placing the two image blocks first; rank r+s. Add the permutation's swaps to c(B)+c(C).
- Tensor: first B tensor C, then a full column permutation placing precisely the `(image,image)` columns first; rank rs. Add those swaps to m c(B)+n c(C).
- A split by an ordered subset J of the r carried image columns: use `B_J=B Pi_J`, with J first and **every** unselected image and old kernel column afterwards. Rank is |J| and cost c(B)+c(Pi_J). An empty split still has a complete invertible basis.
- Identity extension with projector zero on unused coordinates: append the identity basis and retain rank r.
- A complete coordinate placement Pi into a larger ambient space: use `Pi(B directsum I)`, retaining all exterior columns. Its basis cost is c(Pi)+c(B). A route conjugated by a placement instead pays both Pi and Pi inverse.

Every permutation is an actual word of paid swaps. The construction does not silently relabel arbitrary physical indices and assume u is unchanged. When an equivalent implementation chooses direct relabeling, it must recount upper additions against those actual indices. The emitted implementation instead retains full permutations explicitly and uses only increasing maps within tensor copies.

For equal-rank tags of the same complete dimension, the matcher is `S=B_P B_Q^-1`. Its word concatenates those two carried words and has cost c(B_P)+c(B_Q). Both image and kernel are matched. Rank is carried by integer addition, multiplication and subset cardinality; no generated submatrix is inverted and no fresh Gaussian rank decision is made.

### Guarded sectors

Let E have dimension m, carried basis C and rank k, so `E=C E_k C^-1`. For S of dimension n, put `H=I_n tensor C`. Then

`L_E(S)=S tensor E + I_n tensor (I_m-E)`

equals `H L_(E_k)(S) H^-1`. The middle factor is k copies of S on the interleaved coordinates `i -> im+j`, `0<=j<k`, and identity elsewhere. The emitted right chronology is H, those copies, H inverse. Thus

`c(L_E(S)) = 2n c(C) + k c(S)`.

This is an exact ledger for the unoptimized emitted word, including k=0 and k=m; cancellations could shorten it but are not assumed. Its inverse keeps the same C and reverses/inverts S, giving exactly the same counter vector. It does not replace C by C inverse as the sector basis. A further ambient conjugation by T adds 2c(T).

Because E is a carried projector, `E^2=E`, and `L_E(S)L_E(T)=L_E(ST)` with inverse `L_E(S^-1)`. Arbitrary matrix sums or non-idempotent sectors are not admitted. The checker includes a nonorthogonal valid sector and a non-idempotent rejection control.

All constructors only copy seed coefficients or negate an addition/invert a scale. The generated **linear-word** coefficient alphabet is therefore the finite seed alphabet closed under those two operations. Dense matrix entries may grow; they need not be used as new linear-word coefficients. Low-controlled representative carries are separate and are not included in this finite-alphabet claim.

## 4. Literal source coverage and exact coupled ports

The two pinned Python files receive a normalized paid boundary `(owner, axes)`. They do not discover a basis from an untagged matrix. The carried implementation supplies that normalization from the complete seeds and preceding inductive constructions.

| Literal source site | What is introduced | Word/rank rule |
| --- | --- | --- |
| `product.compose` | Distinct suspended outer callbacks at multiplied column counts; complete placement before the inner callback and inverse afterwards | Tensor/multiplicity and complete permutation; retain the suspended adapter until return |
| `product.specialize`, role selection | Whole independent public or zero fields; all source paid requests remain | No new linear basis or matrix-rank decision; ownership/retirement unchanged |
| `product.specialize`, request slices | Consecutive slices of an already normalized axis tuple | Carried image split, with its full complement |
| `schedule.complete_order` | Active tuple followed by every unused coordinate | Full permutation, not a rectangular minor |
| `schedule.expand` | Tiles, recursively completed native requests, positive tails and inverse placements | Complete placement, carried split, known coordinate rank-one leaves |
| #7828 `APPLICATION.md`, binary embedding | Multiplicity, identity extension, changed basis and a restricted column sector | Tensor/direct sum, carried conjugation and the guarded rule |

The matrix rank at a generated node is already certified by these constructions. Source comparisons of tuple lengths check this known rank; they are not calls to rational rank elimination. There is no further uncarried basis or rank choice in this source-compatible implementation. An externally injected arbitrary change-of-basis matrix or untagged idempotent would require another admitted seed or separate construction and is outside this grammar claim.

Tag bookkeeping does not itself execute a basis change. Only route/adapter symbols actually emitted at their source positions are lowered. An outer normalizer remains active across its paid slices and is not silently re-entered for every child. Every complete word substitution has the same matrix endpoint as that source symbol. No scalar ADD is tensor-distributed and no adapter is commuted through a coupled scalar contact.

For actual port i and stage s retain exactly

`S_(i,s)=(U_i directsum I_126) Pi_s (U_i^-1 directsum I_126)`.

Pi_s exchanges the original seven central body axes with the fresh seven-space, fixing the actual head and every other coordinate. Its word contains seven swaps. Its 134-dimensional right-word count is therefore `2c(U_i)+(7,0,0,0,0)`. Both members of each coupled pair use that same symbol; an arbitrary equal-rank matcher is not substituted. All 111 U_i are present. The 18 stage positions produce 1,998 distinct port-stage symbols. The source's 36 native occurrences and two coupled mains require four directed adapters per port per occurrence, retaining 15,984 directed uses.

The caller's 38 target patterns are an optional actual head plus selected fresh seven-spaces. In basis `U_i directsum I_126`, these are known coordinate subsets. Their complete bases append a full image-first permutation; all 4,218 port/target pairs have their own computed count. Omitted central body directions remain kernel columns. No rank computation is hidden in these choices.

Structural induction covers every finite generated expression and every explicit adapter occurrence of the unchanged selected compiler. The enormous selected expression is not instantiated by the bounded test. Its descriptor generator is finite and effective, and its count follows the recurrences without expanding dense matrix entries.

## 5. Full-row invoice and representative carry

Let a generated fixed route have dimension N and counter vector `(t,a,u,d,h)`. Apply its right word separately to all N high rows. An earlier-target addition is lowered by a completed swap, a later-target addition, and the inverse swap. The sufficient bill per direction is

`N(t+2u)` ordinary swaps,

`Na+N^2` ordered additions/translations,

`Nd` fixed unit scalings, or `Nh` signed-dyadic scale atoms after expansion.

The `N^2` term charges every high-field carry slot, including zeros and spectators inside the complete cover dimension. Inverse words have the same bill and are charged again. There is no assertion that t,a,u,d,h obey the old generic Gaussian-elimination counts. This construction uses its own computed totals even when they are larger.

For low representatives g0 and h0 of g0S modulo q, define the exact localized carry `C_S(g0)=(g0S-h0)/q`. Then

`rho_S(g0,X)=(h0,XS+C_S(g0) mod q^(w-1))`.

Every carry lies in `Z[1/2]`; it need not be an ordinary integer. The identities `C_ST=C_S T+C_T` and `rho_(S^-1) rho_S=id` hold with the appropriate intermediate low representatives. The inverse recomputes its own carry. At w=1 the high cube is a singleton, so high primitives are skipped; the displayed ledger remains conservative. Universal odd q,w follow from exact dyadic words and the ring homomorphism, not from extrapolating modular fixtures.

Carry preparation may evaluate the fixed word/matrix or accumulate its cocycle, then perform the final N^2 high translations. That preparation, low selection/unselection, temporary coefficients, scanning and inverse return remain separately charged services. The N^2 translations do not make preparing C_S free. Performing a carry after every elementary operation would require its own recounted translation ledger.

## 6. Verification, comparison and remaining obligations

`factor_words.py` implements lazy constructors, exact counter recurrences and genuine Euclidean seed reduction. `build.py` emits fixed seed words, derived complete bases, the port/target ledger and bounded constructor examples. The separate `verify.py` consumes those data using an independent rational matrix engine, without importing either construction module. Normal and optimized verification are required; logical checks use explicit exceptions. Frozen receipts contain deterministic mathematical fields. Verification outputs may be written outside this package so replay does not overwrite the accepted receipt.

The finite source inventory contains 755 seeds and 513 derived bases, and the bounded examples cover the constructor identities, full complement, nonorthogonal sectors, exact port matrices and orientation-sensitive products. The checker compares forward/inverse words, lowered endpoints and independently recounted bills. It also checks low/high reconstruction, all carry coordinates and controls rejecting wrong order, a non-idempotent sector and the false universal short-pivot rule. Exact counts and hashes are in the completed evidence; tests corroborate the universal structural proof rather than materialize the selected enormous program.

This is a new effective ledger, not an optimization of #7840's q-dependent Gaussian factorization. That predecessor may still be chosen with its own proved N-dependent counts. The explicit q-independent words here may be longer. The old finite eight-dimensional maxima 472/496/64 do not apply to generated nodes, and no unchanged `N^51` bound for expanded elementary records is inferred from the predecessor's separate logical-record bound.

All basis/matcher arithmetic remains valid at every odd prime, but the large-cover condition `q>2^45 N^5` and growing outer fine-prime conditions remain. Generated route dimensions are fixed by the selected finite compiler before operand length varies; a runtime outer numerical multiplicity and its separate recursion are not silently included in one fixed catalogue count. A caller using another dimension or grammar must recompute its words and charges.

Owned nonzero erasure, full owner/stock restoration, fixed-tape movement and precision, coefficient/carry production, low-type scans, temporary widths and analytic recovery are not discharged. The common coupled-route and ancestor-only weight conditions are preserved, not replaced by algebraic invertibility. This construction gives no total transition count and no unconditional multiplier.

### Open next questions

1. Instantiate one actual generated descriptor in a recursive owner bank and price the complete low/high route, including carry preparation and original-owner return.
2. Compare the carried-word ledger with a separately charged q-dependent factorization for the same generated node; never substitute the smaller count without implementing its word.
3. Derive a useful size bound for this structural word grammar if a family-uniform physical estimate is needed. The present result gives effective fixed-expression counts, not that additional asymptotic theorem.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. Credit Ali Romman for #7828 and the native/compiler lineage, #7840 for source-specific full routes, the accepted #8092 dyadic/finite-route authors and reviewers, JoyboyBrian's #5052 scale interface, and the ordered-route predecessors. Classical elementary matrix facts remain classical. Independent human or formal proof-kernel acceptance is not claimed.
