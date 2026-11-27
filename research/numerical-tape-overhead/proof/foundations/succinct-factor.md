# Succinct execution of a full-rate cyclic factor

Status: **proved algebraic representation and scoped tape executor; pending independent review**. This removes explicit matrix enumeration from one well-defined interface. It is not a complete multiplication or improved-overhead theorem.

Source pins: programme `0607d044d1d09489580da0e5828588820e1a6775`; OpenAI math `3344da59991ed94f9ba711217b29c1d760badfa6`. Dependencies read: [formula-full-rate-linearization.md](formula-full-rate-linearization.md), [power-two-degree-predictor.md](power-two-degree-predictor.md), [structured-shift-check-refinement.md](structured-shift-check-refinement.md); tape manuscript `build/interchange.tex` and `build/walsh.tex`. The cyclic tensor construction is established matrix-factorization mathematics, credited in the predecessor note. The contribution here is an explicit succinct representation of its **individual factors**, with a physical packed-row execution bound.

## 1. Grammar, indices, and precise claim

Work over F4, or a finite extension K represented in h F4 coordinates with a supplied valid monic irreducible defining polynomial. The theorem charges copying and using that polynomial; it does not assert a polynomial-h constructor for an arbitrary extension. In the intended application h=O(log m), and the previously proved bounded enumeration costs polynomial(m). Consider a formula with S nodes and positive assigned factor lengths at most D. Its affine leaves have at most a fixed number b of query terms. A leaf of length one is its affine polynomial. A scalar leaf of longer prescribed length is its scalar at phase zero and identity at every other phase. The remaining constructors are:

* `Pad(f,d)`, with d at least the child's length, inserts identity factors at the end.
* `Scale(c,f)` multiplies the phase-zero factor by c.
* `Mul(f,g)` concatenates the two tensor-factor lists.
* `Add(f,g,d)`, where d is a power of two, pads both children to d and takes the characteristic-two untwisted cyclic sum.

Zero scalars and identically zero formulas are permitted. No cancellation lowers any assigned degree. The grammar is the power-of-two construction already proved in the predecessor notes; it includes the carry/count predictor after explicit padding and scalar nodes are retained. Let r be its full independent row width. At an addition node of length d, index rows by `(i,u,v)` with `0<=i<d`, u a left-child row and v a right-child row. At a multiplication node use `(u,v)`. Concatenating these fields in preorder gives one mixed-radix row address. Only addition nodes introduce grade fields. Therefore

    log2 r <= S log2 D.

A coordinate rotation increments one designated addition grade modulo its radix, leaving all other row and data coordinates unchanged. Different grade rotations commute. A **weighted masked rotation** consists of a product pi of such increments and a coefficient function c(x) in K, with zero allowed. It sends basis row x to c(x) times basis row pi(x).

**Theorem B1 (succinct factor).** Every phase-t affine factor A_t of this formula has a representation

    A_t = C_(t,0) + sum_q C_(t,q) q,
    C_(t,q) = sum_(nu<=c S) Rot_(pi_nu) Diag(c_(nu,t,q)),    (B1)

for an absolute c depending only on b. Each pi_nu increments a fixed subset of grade fields. The coefficient functions can be evaluated from the row address, t and the formula in polynomial(S,log(D+1),h) bit operations and workspace. The complete description has polynomial size and can be generated in that time. It does not list the r rows or r-by-r matrices. Every row remains an arbitrary independent input.

The same list of rotations can serve every query slice; a missing leaf query coefficient is zero. There is no assertion that different q act freely on physical addresses: this theorem executes scalar coefficient slices, not their query operators.

## 2. Proof by a single-factor traversal

Maintain the current local phase while descending the formula. A path to a leaf or a padding identity is a token. There are at most S such terminal tokens after explicit padding is included.

At an addition, let the incoming total phase be t and the input row be `(i,u,v)`. Under the grade convention of the cyclic construction, its factor is exactly the sum of:

    (i,u,v) -> (i+1 mod d, A_i u, v),
    (i,u,v) -> (i, u, B_((t-i) mod d) v).                 (B2)

In the first branch record an increment of this grade, pass local phase i to the left child, and retain the right row. In the second record no increment here, pass phase `(t-i) mod d` to the right child, and retain the left row. The twist is one because d is a power of two in characteristic two.

At multiplication, the incoming phase chooses the left child if it is below the left length, and otherwise chooses the right child with that length subtracted. The unchosen child's rows are untouched. This becomes a computable zero/nonzero mask on every fixed terminal token; it does not create a product of two affine query expressions. At padding the extra phases are identity tokens. At a scaling node multiply the token weight by c precisely when the incoming local phase is zero. All these tests use the **input** row grades; phase updates are computed before any recorded output increment.

A token reaches at most one affine leaf. Its query coefficients are thus the leaf coefficients times scalar weights accumulated on its path. No product of query variables arises. Its output row differs from its input only by the recorded independent increments, so its map is a masked permutation with a fixed rotation list. Each token has path length at most S; all local phases and grades have O(log D) bits. Evaluating the masks and weights, or generating their straight-line descriptions, is polynomial in the stated parameters. Summing the tokens proves (B1) column by column.

This argument is about one factor, not the product of all D factors. Expanding the whole polynomial or all row coordinates would discard the saving. The product of the succinct factors is the same whole-identity scalar polynomial product as in the predecessor cyclic proof.

## 3. Packed-row tape execution

Let V be the encoded bit volume of an array consisting of all r rows, each with an arbitrary common positive data-range length, written in lexicographic order. Each K scalar is stored in a fixed-width 2h-bit record. Extra fixed prefix and suffix ranges are allowed. Given a coefficient slice C_(t,q), one fixed finite-alphabet multitape interpreter evaluates it in

    V poly(S,log(D+1),h) + poly(S,log(D+1),h,log(V+2))

actual tape steps, and visits

    O(V) + poly(S,log(D+1),h,log(V+2))

cells. Constants, tape count and alphabet are independent of S,D,r,h,V. The formula description and all generation work are included in the polynomial terms. No exponential matrix table or variable tape count is used.

For each token, copy the original input to a work stream while computing the token mask and field coefficient from counters, multiplying each record accordingly. These are sequential scans; even recomputing the entire path separately for every record costs the displayed polynomial factor. Field multiplication uses schoolbook polynomial arithmetic and the supplied degree-h defining polynomial; copying and parsing that supplied description is included in the descriptor cost. Constructing the irreducible polynomial is a separate cost as specified above. Over F4, h=1. No full log(V)-bit position counter is rescanned per scalar. Formula masks use only the O(S log D) row-grade counter, which remains fixed across a trailing data range. Grade-counter work can even be recomputed per scalar within the displayed polynomial factor. Boundaries of large trailing ranges use amortized binary countdowns; each decrement and reset has aggregate linear cost over a complete range. Large prefix counters are only advanced, not copied into every record.

Next apply its recorded coordinate increments, one field at a time. A grade increment is a cyclic rotation of d equal contiguous blocks inside each complete prefix fibre. Copy blocks 0 through d-2 sequentially to one auxiliary stream and block d-1 to another, then concatenate block d-1 followed by the rest. A nested scan performs this at every prefix. Arbitrary trailing row/data coordinates form part of each block; no transpose or randomly addressed lookup is needed. Each such pass and its head returns costs O(V), apart from the displayed polynomial counter/setup term. Binary counters and amortized ripple carries locate the block boundaries. The number of passes per token is at most S.

Add the resulting stream into the output accumulator by a scan. The original input, one token stream, its rotation workspace, and the accumulator require only a fixed number of O(V) reusable regions. Complete one token before the next. Sequential siblings and factors reuse these same regions, so the bound is on cells ever visited, not merely peak live data. A token coefficient must be applied **before** its rotation; reversing that order is generally wrong.

This proves the claimed physical interface. The operation is a scalar row transformation. It makes no recursive spatial-query calls, and says nothing about the time needed to execute q itself.

## 4. Application and exact remaining gap

The accepted power-two count predictor has S=m^O(1), D=O(sqrt m), and row width r=2^{m^O(1)}. The existing structured-shift refinement has polynomially many shifts and K-coordinate degree O(log m). Theorem B1 gives polynomial description/generation and polynomial per-bit time for every scalar row-coefficient slice of each predictor factor, despite its exponential independent row width. The affine predictor still uses exactly D shared-pencil stages: this replacement changes ordinary coefficient execution, not the recursive query count.

This is a genuine removal of the dense-matrix expansion expense at this interface. It is **not sufficient** to substitute a polynomial template profile into the existing multiplier theorem. Remaining costs include: assembly of many row slices inside shared endpoint routing without changing its recursive call mass; actual label rank/rectangle maps; rational address scalings and compatible radix; row regrouping and leading-batch creation; shift-check interpolation depending on spectral tuples; finite repair unrolling; numerical Walsh and precision; and uniform space/threshold composition. In particular, the existing general address compiler bounds some numeric multiplier magnitudes exponentially in polynomial m. Theorem B1 does not change those magnitudes.

The exponential row width itself is not proved harmless for all callers: the source first-digit batch split uses an address radix above the complete batch width. A compact alternate batch extraction needs its own proof. No new complete overhead bound is claimed.
