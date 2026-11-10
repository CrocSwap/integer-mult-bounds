# A first-success field and slice from raw matrices

This package takes PR6451's explicit raw-witness question: construct the least
successful extension and an actual invertible projective slice of a regular
square pencil, without listing every irreducible through the degree threshold.
The result is a deterministic arithmetic algorithm and written proof, with a
bounded prime-field reference and separate literal-field corroboration.

For supplied exact K=Fq and raw A,B, the orientation is det(tA+B), and infinity
is det(A). The output includes the first degree, field modulus, projective
point, literal matrix and a two-sided inverse. Infinity is allowed at degree1.
The sharp worst-case threshold and attaining pencils belong to Nick Petalas/
PR6451; the general determinant and factoring methods are classical.

## Construction and cost

1. Test infinity, then obtain f(t)=det(tA+B) by polynomial Bareiss elimination.
   Reject an identically zero determinant. Test at most min(q,n+1) base points.
2. If all base points fail, scan degrees sequentially using
   gcd(f,t^(q^d)-t). The first degree with a missing root is the least success.
   Integer extension degrees are not assumed to be monotone in feasibility.
3. At that first e>1, Q=(t^(q^e)-t)/gcd(f,t^(q^e)-t) has only degree-e
   irreducible factors. Classical Berlekamp fixed-space splitting follows
   one proper-factor branch until one such h is obtained.
4. In K[t]/h, take alpha=t mod h, form alpha A+B, and invert it explicitly.

Previous failure gives q^(e-1)<=deg f<=n-1. Base failure also gives q<=n-1.
Hence the dense degree q^e is at most (n-1)^2, and the scalar scans are small
in exactly the branch that uses them. The large-q base branch never makes a
dense degree-q polynomial. [PROOF.md](PROOF.md) proves these claims, the
minimality and a conservative O(n^8 log n) base-field operation upper bound.
It includes determinant extraction, exact divisions, powering, gcds, fixed-
space kernels, scalar scans, extension arithmetic, inverse and product checks.
This is a loose arithmetic bound, not a timing or physical speedup claim.

K's exact arithmetic and element enumeration are supplied premises. Requests
for distinct elements are explicitly counted. This does not construct a base
field for free, establish bit/tape complexity, or supply a reversible circuit.
The executable supports bounded prime-field inputs; the written algorithm
treats supplied representations of every prime-power field.
Its exact API domain is q in {2,3,5,1000003} and 0<=n<=17, with square canonical
matrices. Dimension0 is an empty-matrix calibration, not part of the n>=1 theorem.

## Reproduction and finite boundary

Use CPython3.12 and the standard library:

```sh
python3.12 -I -W error -B research/pencil-first-slice-constructor/verify.py
python3.12 -I -W error -B research/pencil-first-slice-constructor/oracle.py
```

Repeat with -O. Strict defaults require retained receipts. --emit prints a
candidate receipt without overwriting package files. Both programs authenticate
the exact two inert predecessor documents and PENCILS.json before reading them.
No author scientific executable or census is imported or rerun.

The frozen census consists of all raw pencils for F2 dimensions0,1,2; F3
dimensions1,2; F5 dimension1; and every diagonal binary dimension3 pencil:
6,920 raw matrix pairs in total, including identically singular inputs.
The zero-dimensional case is an empty-matrix calibration, outside the n>=1
theorem statement. Matrix entries use row-major base-q digits, coordinate0
least significant; A's code is outermost and B's innermost. Diagonal domains
encode only diagonal entries. One transcript byte is zero for an identically
singular pencil and otherwise its least successful positive degree.

PENCILS.json contains 17 explicit named raw inputs and their source/elementary
expectations. Binary dimension3/5/11 attain first degrees2/3/4; F3 dimension4
and F5 dimension6 require degree2. Original and strict-equivalent scrambled
versions exercise raw matrix processing. Further cases cover infinity-only
success, the source's nonmonotone dimension17 example, a large base field
q=1,000,003 with a constant determinant, and a mandatory row pivot. These are
input recipes, not a table of computed constructor outputs. Attainment and
nonmonotonicity themselves are credited predecessor examples.

The primary checks every constructed census answer internally. The separate
oracle compares all declared census status/degree streams and independently
checks every NAMED primary-returned modulus, point, literal slice and both
inverse products. It is not claimed to recheck every primary census inverse.
Its trial-division finite-field construction and literal matrix evaluation do
not use the Frobenius-gcd/Berlekamp witness algorithm. Exact measured outcomes,
first-run history, controls and receipt hashes appear in VALIDATION.md.

Both engines agree on all seven streams: 617 singular pencils and 6,303 regular
pencils, of which 6,297 first succeed in degree1 and six in degree2. All 17
named primary answers pass separate literal-field checks, including different
valid modulus choices. Normal/optimized emissions and strict defaults pass.
Finite outcomes corroborate the written algorithm and do not prove its
all-prime-power quantifiers or asymptotic cost.

## Scope, source and credit

Canonical base7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority8, selected6030.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19365968).
PR6451 head e9548573ead05bbecaaa6e194f9f8298d9a6923a has its exact README and
PROOF retained under SOURCE-PINS.json. The 488-open-PR snapshot, fresh latest
page, bounded all-state constructor searches and current1166Hub were checked.
Arbitrary diffs, hidden replies, sparse history and unpublished work remain
outside this coverage. The formal-interface card is explicitly changed to
this arithmetic side construction, with no Lean or selected-assumption claim.

Credit Nick Petalas/6451 for the sharp degree theorem, attaining pencils and
raw-witness question, and5250 for the earlier invertible-slice interface;
Ali Romman/5689/5692/5712 for raw regular-pencil interfaces, decomposition and
transport; apoursh/5672 for singular-block context; David Ganz and retained
tensor-atlas/native lineage. PR5692 already uses polynomial raw Kronecker
extraction and classical factorization for a fixed field; neither is claimed
as new here. PR6422's norm-subfield question and6309's raw product improvement
are adjacent different contracts. Original notices remain in the pinned files.

Classical methods retain their credit: [Bareiss1968](https://www.ams.org/mcom/1968-22-103/S0025-5718-1968-0226829-0/)
and [Berlekamp1967](https://doi.org/10.1002/j.1538-7305.1967.tb03174.x), Frobenius,
the Chinese remainder theorem and ordinary matrix algebra. No global literature
priority or new general factorization algorithm is claimed. The proof is
self-contained at the stated classical finite-field/minor-identity premises.
ToikY with substantial OpenAI Codex assistance and separate AI implementation/
static review, Apache-2.0. No independent human or formal-kernel acceptance.

Extension invertibility supplies no original-field SL transport, determinant-
character preservation, native call, dirty physical restoration or paid caller.
Coefficient maps, field descent, access/routing, precision, stock, tapes,
compiler and outer admission remain separate. All five selected assumptions
retain their status. No selected cold/native replay, Lean or Docker is run;
there is no new kappa, merge or selected-frontier change.

## Open next questions

- Implement and independently check a supplied nonprime finite-field backend
  for this raw constructor. Start with F4 and a fixed explicit base encoding;
  the current executable covers prime fields, although the proof treats Fq.
- Charge one concrete field representation, extension arithmetic and descent
  in the actual original-field consumer. Start with its exact raw pencil and
  restored-input contract; a polynomial field-operation count is not a paid
  bit/tape or native invoice.
- Have an independent human or proof kernel check the first-degree/equal-factor
  and deterministic cost arguments. Finite examples corroborate, and do not
  establish, their quantified scope.
