# Odd dihedral groups: exact joint reflection tariffs with dirty workspace

**Scoped all-parameter theorem; no new kappa.** For every odd rotation
period `n=2m+1>=3`, arbitrary heterogeneous diagonal targets in formal
`F2[D_(2n)]` cannot share paid reflection calls below their direct bill,
even with arbitrary free scalar register mixing and any finite restored
dirty workspace. The missing joint charge is one call for **each** longest
reflection, not merely the parity of their number.

This closes the odd-period question explicitly left by Adam Gall's
[PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941), pinned at
`5938ce3e91bbb8b5c2227af7976d444b2fbac7d4`. Its two separate cut bounds are
credited and extended to unequal halves. The new step uses a cut in the
faithful regular action to obtain the full joint charge. The proof is in
[PROOF.md](PROOF.md); finite checks support that proof rather than imply it.

## Model and sharp result

Let `r=xy`, `x^2=y^2=1`, `r^n=1`. A paid unit is
`I+([g]+1)N`, where `g` is **only x or y**, and `N=uv^T` is any binary
rank-one idempotent (`v^T u=1`). Scalar `GL_R(F2)` operations are free in
this optimistic model. No other free address maps, COPYs, erasures or clean
allocations are permitted; every preparation/restoration call is counted.

For the complete endpoint
`diag([r^k_1 x^e_1],...,[r^k_W x^e_W],1,...,1)`, with every input arbitrary,
define

```
A = sum_i d_n(k_i+e_i),   B = sum_i d_n(k_i),
t = number of i with e_i=1 and k_i=m mod n,
d_n(k) = min(k mod n, n-(k mod n)).
```

Every circuit has `X>=A`, `Y>=B`, and **`X+Y>=A+B+t`**. Every pair
`(A+j,B+t-j)`, `0<=j<=t`, is attained by coordinate-role words. Thus the
exact optimum for arbitrary nonnegative real prices is

```
alpha*A + beta*B + t*min(alpha,beta).
```

The attaining circuits require zero extra roles or scalar changes of basis,
and no uncharged cleanup. These are sharp formal tariffs, not physical
supplier costs or recursive moments.

For example, two longest reflections at `n=5` have `A=B=4`, `t=2`.
The separate bounds and parity alone permit an eight-call bill. The new
regular cut forces ten calls; the sharp pairs are `(4,6),(5,5),(6,4)`.
At `n=3`, the result covers any number of coordinate-SWAP targets and any
number of restored dirty spectators. Previously established special cases
retain their credit; the contribution is the uniform odd-period argument.

## Why the new cut works

Represent the group by left multiplication on its own `2n` elements,
written `(a,e)=r^a x^e`. Use

```
H = {(-m,0),..., (0,0)} union {(0,1),..., (m-1,1)}.
```

Both x and y have one crossing from H to its complement. The crossing
rank of a target is its shortest alternating-word length:
`d_n(k+e)+d_n(k)+1_(e=1,k=m)`. Crossing rank is subadditive under operator
composition and additive on the required diagonal endpoint. A scalar map
does not cross addresses, and an arbitrary rank-one scalar projector
multiplies a generator's crossing rank by one. These facts give the bound
with no limit on role count or word length. Literal formal words attain it.

## Exact evidence and reproduction

Python 3.12+, standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/odd-dihedral-joint-tariff
python3.12 -I -O -B research/odd-dihedral-joint-tariff/verify.py
```

`verify.py` compares full formal coefficient matrices with a separately
specified faithful regular-action interpreter. The latter builds the group
from literal permutations, then applies every call to all basis columns;
it does not use the formal multiplication or update routines. Both receive
the same declared `(label,u,v)` factors. Binary elimination computes actual
crossing ranks. Neither proof-representation equality nor hashes alone
certify an endpoint.

The fixed [RECEIPT.json](RECEIPT.json) records:

| Covered finite domain | Checks |
| --- | ---: |
| Every group element, odd `n=3..31` | 510 targets, 525 attaining words |
| Every group-element pair, odd `n=3..15` | 2,716 independent multiplication comparisons |
| Every rank-one projector through four roles, `n=3,5,7,9,11` | 1,550 factor checks |
| Every paid word of lengths 0–3 on two roles, `n=3,5` | 3,770 full operator comparisons |
| All ordered target pairs, `n=3,5,7`, with one dirty spectator | 392 forward and 392 inverse words |
| Mixed tuples with 0–5 longest reflections, up to eight roles | 84 words, every surplus-letter split |
| All scalar invertible maps through three roles | 4,741 projector conjugations; 350 zero-cut checks |
| Nonnegative rational prices, including zero | 8,300 comparisons |

All 2,478 single-call omission controls reject. Additional controls cover
missing joint charges, each separate-letter underbill, dirty leakage,
unrestored spectators, wrong noncommuting order, illegal labels/projectors,
and even-period misuse. An invertible dirty shear by
`sum_(g in G)[g]` is invisible in both small proof representations but is
rejected by the full formal endpoint and detected by the faithful action.
A non-coordinate cancelling presentation is accepted.

The package tests remove the actual x, y, joint, and endpoint detectors
in disposable in-memory variants; the associated negative-control harness
then fails. They also reject a missing/duplicate/corrupted receipt and
changed source bytes, compare explicit regeneration byte for byte, and run
an isolated optimized replay from a minimal read-only relocation. Normal
verification never regenerates missing evidence. `--emit` prints a fresh
receipt only when explicitly requested.

A separate specialist wrote [independent_check.py](independent_check.py) without
importing this package. It checks all 5,200 single targets over odd periods
3–101 using set images and literal-word Pareto search through length n, plus 216
full-matrix scalar conjugations. It requires assertions and explicitly refuses
optimized execution; the main checker supports `-O`.

These are finite software checks. The universal statement comes from the
written proof; no Lean, independent human proof review, native admission,
selected cold replay, or hosted CI success is inferred from them. Actual
local commands and environment are in [VALIDATION.json](VALIDATION.json).

## Provenance, overlap, and credit

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; one OS chooser draw
`721bc4f2e2d9f3c304d6dab0f34c1803`, bit-mechanisms / bit-new-register-model,
target-specific relaxation method, priority revision 3. [TASK.json](TASK.json)
records the refinement, bounds, stop rule and next question. The initial
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1955)
precedes the package computation. [SOURCES.json](SOURCES.json) binds the
context and selected-record provenance; predecessor code is not imported.
[OVERLAP.json](OVERLAP.json) records coverage and its limits.

Credit Adam Gall's PR1941 even-period cut construction and explicit open
question, and PR1911 infinite-dihedral theorem; commdata2338's PR1414
coordinate-CNOT proof; Cinna Davis's PR1541 arbitrary-workspace three-swap
theorem and PR1870
two-role S3 census and PR1953 three-role D10 inverse-rotation result;
Ross Richardson's PR1766 full-occupancy four-swap theorem and its explicit
dirty-workspace gap; Aaron Wang's PR1763 finite rotation-target census; and
eumemic PR288, Ali Romman PR468, Gareth Davidson PR1333 and the retained
register-model lineage. The relevant live heads are pinned in SOURCES.
Known finite or all-register special cases are not claimed as newly open.
No literature-priority claim is made for rank subadditivity.

Prepared for Ross Richardson with substantial OpenAI Codex assistance in
proof, implementation, testing and writing. A bit-supplier specialist wrote
the proof; a separate exact-verification specialist reviewed it and the
code. This is AI-assisted checking, not independent human review.
Apache-2.0. Frozen inputs and the selected frontier are unchanged.

## Open next questions

The two-reflection model now has no formal sharing headroom. A useful next
step must change a material hypothesis: specify one physically justified
new native operation and price its full entrance/exit map, child histogram,
restoration, frames and hosting. Compare its cut ranks to the complete bill
before attempting construction. A source-bound compiler/hosting/precision/
tape bridge and a replacement complete recursive profile are still missing;
the current result supplies neither. See the structured question in TASK.
