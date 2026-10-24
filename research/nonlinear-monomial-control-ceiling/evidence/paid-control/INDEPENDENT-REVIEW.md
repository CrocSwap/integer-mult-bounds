# Independent review of the translation-valued paid-control gate

**PASS within the stated fresh-input, translation-valued, commuting-X-Gaussian, FREE-terminal scope.** The ordered shear/inverse/raw-dual identities and the direct 228-H1 additional invoice are correct. The new r>=112 theorem uses a valid whole-translation-module cut; it does not repeat the invalid scalar identity-coefficient rank argument. No blocking mathematical gap was found under the retained source facts and explicit scope below.

Reviewed author report: `outputs/operator-valued-paid-control-gate-20261023/REPORT.md`, SHA256 **`19932a49cda97acb2e3f4933f95d4bed5598e441d7593132bd07d15a63c23731`**. Scientific source pin: `4c0a359d88f22f05189d51f48387750b801a45d4`; #5126 proof pin: `0e8a13c251a9be1029114cda8b4194f05f3a23ec`. SOURCES.json authenticates the report's six declared inputs and seven supporting captures. This was a source-reading and exact algebra review. No operator evaluator, source-pair enumeration, solver, native, compiler, Lean or numerical experiment ran.

## Literal one-child shear, inverse and raw dual

Let U be a 112-by-1 operator column and V a 1-by-112 operator row, with `U_i=P_i`, `V_i=c_i P_i^-1`, `P_i=X_(q_i)` and 56 signs of each kind. Matrix multiplication gives `VU=(sum c_i)I=0` exactly at every column width. Therefore, in the noncommuting operator ring,

```
(UQV)^2 = UQ(VU)QV = 0,
(I+UQV)^-1 = I-UQV.
```

No assumption that Q is free or involutive enters this inverse. Source Pauli translations commute with the actual central Q and with D3, so `Q^-1 T Q=D3 T D3^-1=T`, including their ordered inverses. The actual Q square remains a Pauli translation. The fixed owner sum is evaluated on lifted address operators; it is not tensor-powered as a whole owner matrix.

The literal schedule reads all original owners into an owned gather before updating them, applies one Q child, scatters and resets only owned fields. Its inverse reverses the scatter sign while using the same Q. Thus original arbitrary inputs are not silently replaced by scratch. For transpose rather than Hermitian adjoint, Q^T=Q and P_i^T=P_i, giving

```
T^-T = I-V^T Q U^T.
```

The raw-dual gather/scatter described by the author has the correct indices and signs: gather `sum P_i x_i`, then scatter `-c_i P_i g`. T^T changes that last sign. The source native backward X-only Q²/Ds² corrections remain separate. This proves the algebraic word on the declared normalized fields; it does not certify a physical Tape implementation, finite precision or a full controller emitter. The ordinary COPY/translation/ADD/reset counts are field-level allowances; initial zero-bank provisioning and all scans/precision remain nonzero work.

## Direct whole-control recursive bill and original owners

The middle block is implemented as `X <- T(-C1 X+QY)` and `Y <- -C3 T Y`, with QY obtained before overwriting old Y. It therefore uses two T applications plus the already-priced 112-H1 central query bank. At the main endpoint, t^-1 contributes one more T^-1 application. The exact ordered terminal inverse

```
E^-1 = Q C1^-1 T^-1 C3^-1 Q
```

runs rightmost first: Q on 112 fields, C3^-1, T^-1, C1^-1, then Q on 112 fields. Its price is 224+1=225 H1. Thus the direct additional control price is **2+1+225=228 H1**. The original 112-H1 query bank is already included in the base invoice and is not charged again. Two one-child shears use 4m+224=232 H1 under the same direct policy. These are upper construction bills, not optimality or paid-E lower bounds.

The two middle recodings C1/C3 and two terminal inverse recodings are the stated four native C/C^-1 macros. Their scalar/monomial/odd-division costs, signs, query ownership and raw-dual normalizers remain separate nonzero obligations. Reusing a helper as scratch, deleting a complement or dropping a required inverse is not part of this bill.

The original 224 main owners still receive rank-17 targets after the declared decoder, and all 816 distinct helper owners remain completed once to rank nine. The promised base price decomposes as `2P0+112H1+(94H1+14H2+56H5)`; those helper complements are retained. Adding the direct 228 H1 gives `P1=4836`, with other coefficients unchanged. It adds no productive cache/query/scratch targets. This is a complete **conditional recursive** census, not a complete physical tariff or a new admission of the helper-complement contacts.

The independently frozen raw budget gives M(C) between approximately 44.67696 and 52.13312 for C in `[0.0030217758,0.00339999]`, with maximal uniform integer extra-H1 allowance 44. The direct 228-H1 policy therefore fails before ordinary work or compiler reserve. No root or compiler arithmetic was rerun for this review. That budget remains conditional on the unrealized unchanged T/P, not actual caller funding.

## Source-pair coefficient isolation

The essential new implication is `E FREE => projection_B(T)=0`, for the **entire translation subgroup algebra B**, not merely its scalar identity coefficient. I checked its ordered relative-word calculation.

First make explicit the general commutation link: every allowed free coefficient is a sum of X translations, and every allowed paid child is an X-Gaussian. They all commute with Q and D3. Consequently every circuit entry of T also commutes with those maps, so t=T in the theorem's endpoint. This is why the displayed endpoint expansion applies to the general circuit, not only to the one-child example.

Choose a nonzero coefficient of translation X_b in T[r,s], and choose i,j with A[i,r]A[s,j] nonzero. Such rows/columns exist in the pinned source. Its endpoint word is

```
W = Q^-1 K3_i^-1 K3_r X_b K1_s^-1 K1_j Q^-1.
```

X_b changes affine translation/phase data, not the symplectic linear obstruction. A monomial endpoint would require the first-stage central direction to have no U component after the intermediate source map: `G1_s^-1 q_j=e_q`, hence s=j by the distinct source directions. Its coefficient would then contain A[j,j]=0. Thus every supported chosen translation term is nonmonomial. This uses the actual disjoint q+U / q+W embeddings and signed source K words; it does not substitute scalar A for the physical C_s.

If an A-group letter H at another owner pair (r',s') produced the same projective endpoint in this fixed i,j block, cancellation of the outside invertible factors gives exactly

```
H = phase * K3_r'^-1 K3_r X_b K1_s^-1 K1_s'.
```

The right side is monomial. H commutes with every X translation because it belongs to the commuting-X group. A monomial commuting with all translations must have constant multiplier and affine permutation x->x+a, hence is projectively a translation. Its binary linear part is identity, forcing

```
G3_r'^-1 G3_r = G1_s'^-1 G1_s.
```

The left map is supported on q+W, the right on q+U. Their intersection fixes U and W pointwise and can only fix the single common nonzero binary axis q; hence it is identity. Distinct source q_i then force r'=r and s'=s, and the full operator equation forces H=X_b projectively. Therefore neither another owner pair nor another address letter cancels the chosen coefficient.

At a sufficiently large faithful width, that nonzero isolated nonmonomial coefficient is independent of every monomial word in a proposed fixed FREE endpoint implementation. E cannot then be FREE. Applying this to each nonzero translation coefficient proves the claimed projection condition. Signed phases are retained as scalar cocycles and do not change the linear-part or monomiality arguments.

This review authenticates and uses the source facts—zero diagonal, nonempty 52-entry row/column supports, orthogonal embedded normalizers, distinct q_i—from their pinned predecessor checks. It does not newly replay all ports/pairs, the normalizer evaluator or the native all-input theorem.

## Finite projective algebra and faithful widths

The declared algebra must be fixed before width varies. Pauli-X translations have finite order; the actual X-Gaussians C_v commute and have finite projective order (their squares are translations). A fixed finite list therefore generates a finite projective address group A. The fixed monomial-Clifford endpoint alphabet is projectively finite on the same 17 one-column axes. Include all A letters, source endpoint products and proposed free endpoint letters in the fixed finite set used for separation.

Choose representatives by projective class and group equal classes first. Multiplication at width f has the representative cocycle raised to f, while owner coefficients are applied once. Pairwise nonproportional operator vectors have linearly independent literal tensor powers at every sufficiently large f, by the retained separating-functionals or Gram argument. This gives faithful evaluation of A_f, B_f and the endpoint comparison spaces uniformly over width-dependent scalar coefficients. It does not assert a 112-call bound at every small width; width-one identities can have extra linear dependencies.

No closure assertion that arbitrary monomial maps with arbitrary paid operators generate a finite group is being used. No tensor power is distributed over an owner sum, and no width-growing/noncolumnwise free alphabet is admitted.

## Chronological module cut

Saving all paid responses puts a data-independent linear r-call circuit into

```
y_k = H_k(b_k x + sum_(s<k) e_ks y_s),
T x = F0 x + sum_k l_k y_k,
```

with b_k,e_ks,l_k,F0 over B_f. This form retains active feedback, dense operator-valued gathers/scatters, saved fields, fanout and owned reset. It assumes **fresh equal-width inputs and no initially supplied nonfree observations** of those inputs.

For r<112, the stacked direct-input map `B_f^112 -> B_f^r` has a nonzero complex-vector-space kernel column w, since its domain dimension is 112 dim(B_f) and codomain dimension is r dim(B_f). No division-ring rank, determinant, semisimplicity or absence of zero divisors is required. Choosing x=w z makes every paid input and response zero inductively, including feedback, so `T w=F0 w` lies in B_f^112.

But `projection_B(T)=0` places T's entries in nontrivial right cosets of the translation subgroup in A. Right multiplication by entries of w in B preserves those cosets. Thus Tw also lies in their direct sum, disjoint from B_f^112, and Tw=0. At the chosen faithful width w evaluates nontrivially; one can choose z so w z is a nonzero actual input tuple. Actual invertibility of T then contradicts Tw=0. Correlated values in that tuple are permitted because correctness is required on every arbitrary tuple of distinct input fields.

This proves **r>=112** for the declared model. It uses no extracted scalar coefficient-rank inequality; the earlier operator-valued counterexample remains valid and is not contradicted. It also supplies the new source-specific projection premise rather than merely applying #5126's named-endpoint theorem to an unknown T.

## Scope and pricing boundary to retain in any follow-up

Every nontrivial paid recursive Gaussian has rank at least one and price at least one on the declared interval. Hence a **fresh standalone T implementation in this model** already costs at least 112, exceeding the conditional 44-H1 allowance. This rules out the one-/two-child FREE-E proposals and every smaller-than-112-call implementation under these premises.

It is **not** a lower bound for amortizing a control inside the complete released caller using already-paid QY/native/IDLE/centre observations. For example, a bank of previously supplied QY is nonfree initial information for a T(Y) subproblem and breaks the normal-form starting premise. The complete caller would need its own source access and full invoice. This exclusion should remain explicit beside the budget conclusion, not only implicit in the fresh-input theorem.

The proof also does not cover arbitrary/nontranslation monomial gathers or C/K recodings inside the T circuit, noncommuting paid children, wider packed channels, approximate endpoints, data-dependent nonlinear controls, a paid E/E^-1, changed targets, or another native/controller contract. The 225-H1 direct E^-1 construction is not a lower bound for a cheaper paid decoder. A translation-only negative result must not be promoted to those broader classes.

Two clarity additions are recommended for a focused follow-up, without changing the mathematics: state the general T/Q/D3 commutation link and finite-order generators explicitly; and repeat the fresh-standalone/no-already-paid-observation boundary beside the 44-versus-112 conclusion. The former is already implicit in the declared X alphabet; the latter prevents an invalid complete-caller inference. The ordinary field-pass counts should retain their stated separation from initialization, precision and complete Tape tariffs.

A focused follow-up could publish the ordered one-child word, its direct conditional bill and the scoped translation-module theorem with these hypotheses and inherited source facts. It should retain paid E and nontranslation/noncommuting or correlated-native access as open routes, preserve predecessor credit, and make no native/physical/compiler or κ admission claim. No such PR or public post was created in this review.

Credit the released Dillon template and #5126 input-kernel method, the source #4929/#4933 normalizers and code, the earlier #5160 intersection review, the scalar-rank counterexample and paper-worker conceptual check, and all retained native/helper/query/compiler/precision contributors. This independent read/derive review used substantial OpenAI Codex assistance; no independent human or formal-kernel acceptance is claimed.
