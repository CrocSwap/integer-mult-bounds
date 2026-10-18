# Exact boundary for constant-row shears of the historical complex center

**Scoped negative result; no new κ.** For every even h≥10, the factor exhibited
in [PR937](https://github.com/CrocSwap/integer-mult-bounds/pull/937) uniquely
minimizes the complete gather/scatter cost in the integer constant-row shear
family defined below, for a fixed pivot. This includes simultaneous shears of
arbitrary support. At h=26 its cost is **42,600**. Further improvement requires
leaving this family or changing its scalar pricing/alphabets.

This is an algebraic classification and cost proof, accompanied by an exact
checker. It is not an unrestricted circuit optimum, a new construction, a new
κ, a measured runtime improvement, or a formal proof of integer multiplication.
PR937 already supplies the minimizing factor and its savings. The new result
closes the specified family beyond the one-step search in PR809 and the
second-step search in PR937. It does not reopen those searches with more trials.

The starting base is `47481c89fd30a43f8f882eb4b391e89c29273fd0`. Its accepted
conditional saving is **0.001661957774647029**, PR890/U8-T21 with PR589/555.
The selected certificate, its actual T21 construction and maintainer review
were read; the historical center studied here is not that selected supplier.

## Reproduce

Python 3.11+ standard library, offline, from the repository root:

```sh
python3 -I -B research/dyadic-center-anchor-bound/verify.py
```

Expected final line:

```text
PASS_CENTER_ANCHOR_BOUND h=26 orbits=26 admissible=15276 optimum=42600 all_even_h_ge_10 controls=14 no_new_kappa
```

The same command works with `-O` and from another working directory. It does
not write files. `--write` regenerates only this package's `EXPECTED.json`.
`test_package.py` adds relocation, corruption and independent arithmetic tests.

## Exact family and identity

Let S,T range over the triples of h coordinates, fix a pivot p, and write s_i,
t_i for their indicators. Keep one constant gather row and all other rows in
the form

```
V[p,T] = 1,                 V[i,T] = t_i - b_i       (i != p),
U[S,p] = (3-k)*s_p + |S∩B| - 1,
U[S,i] = s_i - s_p          (i != p),
```

where B is the set of coordinates with b_i=1 and k=|B|. Before imposing the
gather alphabet, allow every integer b_i. Both t_i=0 and t_i=1 occur among
triples. Therefore the two values −b_i and 1−b_i both belong to {−1,0,1}
**if and only if b_i is 0 or 1**. This proves the reduction from an unbounded
integer domain to all binary anchors; it is not a finite search assumption.

The repository's original factor is p=0, B={1,2}. Starting from it, every
matrix `A=I+sum(a_i E[i,p])`, with integral a_i and i≠p, gives exactly this
family: `b_i=b_i_original-a_i`, `V'=A V`, `U'=U A^-1`.
The off-diagonal part N has N²=0, so A^-1=I−N. A relabeling gives any pivot.
We change the factor tables; A is **not** an extra operation on dirty centers.
Mixing two nonconstant rows, rescaling rows, changing the constant row,
nonintegral coefficients, helpers, frames and cross-macro sharing are outside
this class. In particular PR809's `I-E[1,2]` move is outside the class itself.

For the displayed factor,

```
(UV)[S,T] = 3*s_p - 1 + sum(i!=p, (s_i-s_p)*t_i)
          = |S∩T| - 1,
```

because sum(t_i)=3. Thus the center still supplies (|S∩T|−1)/2. Its four
steps `y-=Uc/2; c+=Vx; y+=Uc/2; c-=Vx` add UVx/2 to y and restore every
arbitrary initial center c. Reversing the order and signs supplies the inverse.
The checker compares the affine coefficients modulo sum(t_i)=3, then separately
executes these literal steps on independent input columns at h=8 and h=10.

## Admissibility is completely classified

Use the signed scatter numerator alphabet {−2,−1,0,1,2}; numerator ±2 costs
one signed addition, and ±1 costs one halving and one addition. This is the
signed extension explicitly priced in PR809. The original repository validator
allows only {−1,0,1,2}; it is unchanged and is treated separately here.

All nonpivot scatter entries are in {−1,0,1}. At the pivot, a triple with
s_p=0 and j coordinates in B has numerator j−1. A triple with s_p=1 has
numerator 2−k+j, where it contains two other coordinates. For k≤4 these are
all in the signed alphabet. For k≥5 the smallest achievable numerator is

```
2-k + max(0, 2-(h-1-k)) = max(2-k, 5-h) <= -3   (h>=8).
```

There are enough coordinates to realize that minimum. Hence exactly k=0,…,4
are admissible. With the original narrower alphabet exactly k=0,…,3 are
admissible: k=4 realizes −2. Algebraically correct factors outside the alphabet
are rejected as **unpriced**, not called counterexamples to the factor identity.

Permutations fixing p act transitively on anchors of each size, and preserve
the tables' cost. Thus all 2^(h−1) binary anchors reduce to h size orbits.
At h=26 this covers 33,554,432 anchors, of which 15,276 satisfy the signed
alphabet (2,626 satisfy the original alphabet). The minimum is unique for
each fixed pivot; there are h equivalent choices when the pivot may vary.

## Exact cost proof for every even h≥10

Set n=C(h,3), d=C(h−1,2), e=C(h−2,2), and let c(0)=0, c(±1)=2, c(±2)=1.
Every gather read/addition and scatter operation is charged:

```
G_k = n + (h-1)*d + k*(n-2*d)
H_k = 4*(h-1)*e
      + sum(s=0,1) sum(j=0,...,3-s)
          C(k,j)*C(h-1-k,3-s-j)*c((3-k)*s+j-1).
```

A binomial coefficient outside its combinatorial range is zero. G follows
because an unshifted row has d nonzeros and a shifted row has n−d. Each
nonpivot scatter row has e entries of each sign, at cost two each. The final
sum counts every pivot numerator by its two independent subset choices.

For D_k=(G_k+H_k)−(G_0+H_0), write x=h−10. Exact expansion gives

| k | C(x,0) | C(x,1) | C(x,2) | C(x,3) |
|---|---:|---:|---:|---:|
| 1 | 20 | 19 | 7 | 1 |
| 2 | 5 | 21 | 11 | 2 |
| 3 | 53 | 48 | 19 | 3 |
| 4 | 122 | 72 | 24 | 4 |

`CERTIFICATE.json` contains these coefficients. The checker constructs the
cost polynomials by rational polynomial multiplication, independently expands
the binomial basis, and compares **all polynomial coefficients**. It does not
infer an identity or a tail bound from numeric samples. For integer x≥0,
every C(x,j) is nonnegative and the constant coefficients above are positive.
Therefore D_k>0 for all four alternatives, proving the claimed unique optimum.

At h=8 the five costs are 714, 713, **702**, 716 and 748. Size two is optimal,
with C(7,2)=21 anchors per fixed pivot. This supplies a concrete counterexample
to extending the size-zero claim to h=8; it is included as a positive control
for an adverse result, not described as a failed search.

## Full accounting and what cannot follow

For the historical side circuit, M=158,444, C=J=10,400 at h=26. The inherited
invoice is

```
signed invocation = 4*M + 2*C + 4*J + 2*G_k + 2*H_k
three-stage scalar bound = 3*n^2 * signed invocation.
```

The factors of two pay for both gathers, both scatters, compensation and
restoration. The complete side work is included. At h=26:

| k | G | H | G+H | Complete signed invocation |
|---|---:|---:|---:|---:|
| 0 | 10,100 | 32,500 | **42,600** | **781,376** |
| 1 | 12,100 | 32,224 | 44,324 | 784,824 |
| 2 (original) | 14,100 | 31,281 | 45,381 | 786,938 |
| 3 | 16,100 | 31,281 | 47,381 | 790,938 |
| 4 (signed extension) | 18,100 | 30,894 | 48,994 | 794,164 |

The minimum three-stage bound is 15,846,305,280,000, matching PR937. These
are corroborated predecessor savings, not savings newly claimed here.
The checker binds the original h=8/10/26 factors to the actual inherited
generator and the h=26 invoice to `certificates/dyadic-central-factor.json`.
All side constants and phase/recursive obligations are inherited rather than
freshly established by this package. No additional helper, runtime conversion,
source operation, copy or recursive child is introduced by the class proof.

Retaining all grouped incidences, including zero coefficients, retains the
same h center roles and frame history. The historical W, m, s and paid rank
profile are unchanged. Thus even reaching the class optimum does not improve
the recursive exponent. No composition with PR863's different side-circuit
change, the selected U8 word, or other pending work is asserted.

## Evidence, limits and attribution

`EXPECTED.json` records complete all-anchor censuses at h=8 and h=10 (128 and
512 anchors), all 26 literal orbit representatives at h=26, 67,600 h=26 affine
row obligations, and 3,700 central input-column/direction obligations at the
two small sizes. Seed **33**, drawn from OS randomness, chooses pivots 1, 3
and 7 for these finite diagnostics. The classification and proof cover every
pivot; the seed is not a coverage claim. There is no heuristic search, early
stopping or solver dependency. The experiment stops at the declared class.

Fourteen controls distinguish wrong maps, unrestored dirty data, forbidden
alphabets, undercharged execution, invalid polynomial certificates and the
h=8 exception. There is no full-size side-circuit replay, new physical/global
admission, selected cold replay, Lean proof or remote CI result here. The
inherited all-size compiler, realization, whole-call hosting, precision/tape
and analytic obligations remain open. A finite replay is not a proof of the
whole multiplication theorem; the all-h family result rests on the written
classification and polynomial proof above.

`CLAIM.json` records the three candidates, exact base, time budget, seed and
local coordination fallback. No pinned sprint issue was present. Source pins
are in `SOURCES.json`; all executable inputs are already on the starting base.
No pending code is imported. PR809 is pinned at
`66cabb478385fbaa1a8060123cd57545d703d84e`; PR937 at
`b303fed6dfe2066dcd78c0d8ed74d2a3b153ba72`. Their search domains and lack of a
general optimum claim were checked. The final overlap check and actual test
results are in `VALIDATION.md`.

Credit **Douglas R. Colkitt** for the original factor, signed invocation and
complete invoice, **Curtis Dransfield** for PR809's basis-shear mechanism and
signed alphabet accounting, and **Ross Richardson's PR937** for the minimizing
factor and its complete saving. This contribution adds the exact family
boundary. Prepared by **Ross Richardson (@RossRichardson)** with substantial
**OpenAI Codex assistance** in research, implementation, proof writing and
verification. The checks are not independent human review. Apache-2.0; original
notices and `upstream/` are unchanged.
