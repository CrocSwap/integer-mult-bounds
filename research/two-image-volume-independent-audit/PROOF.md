# Independent audit of the completed two-image boundary

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0. This is an independent written scoped proof and exact finite source audit, not proof-assistant verification or acceptance of a complete multiplication construction.

## Audit finding

PR4991's nonsingular coefficient classification and its enlarged-alphabet affine determinant invariant are correct under their stated uniform full-state hypotheses. Its singular coefficient paragraph needs a separate rank argument: singularity alone does not contradict a language that syntactically permits singular register mixing. Section 4 below supplies that argument. Thus the claimed exclusion survives, with this explicit additional proof step. PR4998's compensated partner is a valid boundary escape; it is not a restored dirty bank.

## 1. Literal source and quantifiers

Use the retained PR4688 definitions on addresses `x=x0+2*x1+4*x2`: `U(x0,x1,x2)=(x0,x1,x2+x0)`, `V(x0,x1,x2)=(x1,x0,x2)`, with additions modulo two. The actual paid operator is `C=((1+i)/2)I+((1-i)/2)X0`. Because `X0` is a Hermitian involution, `C` has eigenvalues 1 and i and is unitary; replacing it by an unnormalized rank-equivalent operator would be invalid for this audit.

The retained PR4710 code defines `S e_x=i^popcount(x)e_x`, `P=SUS`, and `Q=SVS`. These are actual linear maps, including global phases. The checker evaluates only the literal source defining expressions using a separately written composition routine, then checks them against independent bit-coordinate formulas. It never imports or executes a predecessor module. PR4991 and PR4998 verifiers were not read or retained. Retained bytes, Git blob IDs, source commits and paths are in RETAINED-SOURCES.json; their notices are preserved.

For positive integer f, tensorize each letter individually. For fixed complex alpha,beta let `F_f=C_f(alpha U_f+beta V_f)C_f`; the repaired family replaces U,V with P,Q. In particular, the mixture is not `(alpha U+beta V)^(tensor f)`. A completed isolated target on q>=1 banks is `diag(F_f,H_2,f,...,H_q,f)`, where each H is unitary, including identity. All q inputs are arbitrary and independent; all q outputs are specified. There is no clean initialization, omitted output or discarded garbage.

The language is one finite uniform word: fixed finite q, fixed register mixing matrices M acting as `M tensor I_(8^f)`, and fixed invertible 8-by-8 address letters B acting as `B^(tensor f)` on selected banks. Arbitrary full-state unitary letters, even depending on f, are also granted. Word length, nonunitary coefficients and base address matrices are fixed across f. Singular register mixing is syntactically permitted. The exclusion concerns all positive f, and also eventual equality at every f>=f0. It does not concern separate words chosen for separate widths.

## 2. Character multiplicities from the actual phases

Direct coordinate composition gives `R=U^-1 V` with cycles `(0)(4)(1 2 5 6)(3 7)`. Thus `R^4=I` and the traces at powers 0,1,2,3 are `(8,2,4,2)`. For the repaired pair, literal multiplication gives `P^-1 Q=S^-1 R S`, with no residual scalar phase. Consequently their tensor powers have identical traces and spectra. Merely matching projective monomials is insufficient: replacing Q by iQ changes the relative trace from 2 to 2i while retaining its underlying permutation.

Trace multiplicativity gives `tr((R^(tensor f))^k)=(tr R^k)^f`. Apply the four order-four character projectors, in eigenvalue order `(1,i,-1,-i)`, to obtain

`m_f=((8^f+4^f+2*2^f)/4, (8^f-4^f)/4, (8^f+4^f-2*2^f)/4, (8^f-4^f)/4)`.

These are integer multiplicities independently because `m_0=(1,0,0,0)` and `m_(f+1)` is cyclic convolution of `m_f` with `(4,1,2,1)`. In particular all four entries are strictly positive at f=1 and remain so by convolution. Each is strictly less than `d=8^f`, since the other three entries are positive. This proves both bounds for every positive width, rather than extrapolating a finite receipt.

For alpha=1,beta=2, factor the middle sum as `U_f(I+2R_f)`. The unitary outer factors have absolute determinant one, so `D_f=|det F_f|=3^(m_f,1) 5^(m_f,i)`. The repaired family has exactly the same D_f. Widths one and two give `(m_1,m_i)=(4,1),(22,12)`. The formula at width three gives `(148,112)` and hence `D_3 D_1^64/D_2^16=3^52/5^16 !=1`. Width three is used through the proved symbolic formula, not a direct matrix replay.

## 3. All fixed nonsingular complex coefficient pairs

For invertible final output every full-state factor is invertible. In particular every register mixing actually used must be invertible. The normalized logarithmic absolute determinant of any allowed word is `a+b f`: a mixing contributes `log|det M|`; a selected-bank address letter contributes `(f/8)log|det B|`, by the Kronecker determinant formula `det(B^(tensor f))=(det B)^(f*8^(f-1))`; every full-state unitary contributes zero. Summing these finitely many terms proves the invariant for arbitrary fixed invertible address matrices, not just the original permutation/phase alphabet. Fixed bank count ensures the mixing determinant is a fixed number. Arbitrary unitary helper targets do not alter the target profile.

Suppose alpha*beta!=0, put t=beta/alpha, and first exclude t in `{1,-1,i,-i}`. All four eigenvalue factors are then nonzero. Define real finite numbers `A=log|1+t|`, `B=log|1-t|`, `E=log|1+t^2|`. The multiplicities in section 2 give exactly

`log|det F_f|/8^f = log|alpha|+(A+B+E)/4+(A+B-E)/(4*2^f)+(A-B)/(2*4^f)`.

The repaired family has the same formula. If this profile equals an affine function for every sufficiently large integer f, its convergent limit forces the affine slope to be zero. Subtract that limit and multiply by 2^f: taking f to infinity first gives `A+B-E=0`, and the remaining equality then gives `A-B=0`. This proves independence of the two decay modes on any infinite tail; it does not infer eventual behavior from the first three widths.

Now `A=B` implies `|1+t|^2=|1-t|^2`, so Re(t)=0. Write t=iy for real y. The second condition requires `1+y^2=|1-y^2|`. For `y^2>0` the left side is strictly larger, whether `y^2<=1` or `y^2>=1`. Thus y=0 and t=0, contradicting beta!=0. This closes the critical pure-imaginary case as well as general fixed complex ratios. Therefore no nonsingular nonzero coefficient pair can be isolated by the uniform language, even eventually.

## 4. The singular coefficient cases require rank, not volume

For t in `{1,-1,i,-i}`, exactly one fourth-root eigenspace is killed by `I+tR_f`. Since every multiplicity is positive and strictly smaller than d, both literal prefix families satisfy `0<rank F_f<d` for every positive f. This uses the actual source spectrum; singularity alone would not suffice.

Fix one such width and the same q banks as in section 1. The desired full-state target has rank `(q-1)d+rank F_f`, strictly between `(q-1)d` and qd. All address letters and unitary letters are invertible. If all register mixings were invertible too, their product could not equal a singular target. Hence some q-by-q register mixing M must be singular. But `rank(M tensor I_d)=d*rank M <=(q-1)d`. Multiplication by any other square factors cannot increase rank, so the whole word has rank at most `(q-1)d`, a contradiction. A mixing on a subset of banks has the same bound after adjoining its identity block.

This argument includes q=1, arbitrary many but fixed helper banks, and unitary helper outputs. It is pointwise in width, so also excludes any eventual family. It does not take the logarithm of a zero determinant. This is the explicit completion of the singular branch of PR4991's all-coefficient statement.

If exactly one of alpha,beta is zero and the other is nonzero, the target is a scalar times a composition of individually tensorized unitary letters. It is implementable by that literal single-image word and a fixed scalar mixing; its normalized volume is constant. These allowed boundary cases are not accidentally excluded.

## 5. Compensated and clean-input boundary controls

PR4998 has two arbitrary independent inputs and outputs `diag(F_f,F_f^-1)`. Its absolute determinant is one at every width, so its second bank cancels the first bank's volume profile. Its all-width block identity is `W(D)W(-I)=diag(D,D^-1)`, where `W(D)=E12(D)E21(-D^-1)E12(D)=[[0,D],[-D^-1,0]]`. Ordinary block multiplication proves this without commuting D with any outside C. Taking D to be the source middle sum and sandwiching with `diag(C_f,C_f^-1)` gives the claimed pair. The finite checker independently interprets retained PROGRAM.json at widths one/two and compares every independent input column with a target built from the literal source matrices and direct modular inversion. It confirms that the second output is not identity. It does not audit native rounding, the instruction invoice or Gaussian-consumer admission.

Likewise the PR4688 clean-scratch implementation remains compatible. A full-space singular map may be injective on a proper clean-input subspace: `[[2,0],[0,0]]` maps `(x,0)` to `(2x,0)` injectively while its full determinant is zero. Thus the invertible full-space premise used in section 3 and the retained-dirty rank requirement in section 4 do not follow from correctness on clean inputs. Clean-workspace projector mechanisms and width-dependent nonunitary words are outside this theorem, and no statement about arbitrary global continuations of the prefix follows.

## 6. Evidence and remaining scope

The independent checker uses no external dependencies or predecessor imports. Exact monomial phases, source bytes, character traces and integer Bareiss determinants are checked at widths one/two. The all-width convolution and all-complex classification are written proofs above. The curvature witness is symbolic. The literal compensated program comparison is exact over F17 with i=4, a finite positive boundary control rather than a rational all-width program certificate. Semantic controls reject tensorizing a sum, dropping the absolute phase, calling the transformed inverse partner returned dirt, and extending a full-space invariant to clean input. Normal and optimized replays use explicit exceptions, so correctness does not rely on Python assertions.

No five-in-fourteen conclusion, paid-call lower bound, native supplier, precision/tape acceptance, selected-frontier change, new kappa or full multiplication theorem is established. Original construction, spectrum and invariant credit remain with their authors; this audit adds independent source/quantifier coverage and the singular rank argument.
