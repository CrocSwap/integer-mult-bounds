# Physical Full tensor service and exact scalar cost

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance.
Apache-2.0; retained source notices remain authoritative.

This is the physical part of the source-emitted global caller in
[PROOF.md](PROOF.md). It binds that caller's actual H masks and coefficient
pages to a sealed fixed-tape implementation. It does not replace the source
compiler's numerical proof, prove the selected native tariff, or establish
an unconditional multiplication bound. **No new κ.**

## 1. Exact dependencies and interface

The canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
[PHYSICAL-SOURCES.json](PHYSICAL-SOURCES.json) authenticates all physical
inputs before import. [PHYSICAL-RECEIPT.json](PHYSICAL-RECEIPT.json) records the
executed commands, exact implementation bytes and finite observations.
The byte-identical boundary files are exported from
[@CubeJerry's source-owned H boundary](https://github.com/CubeJerry/integer-mult-bounds/tree/271f1d4c3128a89d49694e7508c1c88bba8cc981/research/compiler-t74-global-boundary),
public commit `271f1d4c3128a89d49694e7508c1c88bba8cc981` (author commit
`52e4c67ae46c04cf280a9fec135c7fe2d0c52121`, identical tree).
That contribution supplies the exact signed-grid raw-H bridge to #3627.

The scalar child here is `physical-ring-product.WordProduct` from #3709,
at every word width. Its signed codecs and `Arithmetic.complex_product`
come from the same authenticated source. The cold source export opens the
same #3627 cohort used by the boundary: `composed_sources.py`,
`composed_engine.py`, and `composed_plan.py` have exactly the Git blobs
`5b9a507a5f5eb7d32d76792cac4b876070d29e91`,
`646c451a4cbdf0244c7782d958f257f6606b962f`, and
`300ee75d4171c8f0d97118a01a4e439b72ca01d6`. The loader rejects preloaded scalar module aliases, checks their resolved
canonical paths and then checks runtime class identity. Three forged module
aliases are rejected before opening the physical cohort.
One `Count`, `Tape`, scratch/lease and ownership vocabulary serves both
children. No second mutable cohort or another worktree is needed.

The archive also preserves numerical Fourier code needed by its historical
loader. The scalar service does **not** instantiate or call `RingProduct`,
`FftWord`, a Fourier transform, or H. In particular, #3709's numerical
convolution recovery is not a premise of the exact Karatsuba subroutine.
This does not remove numerical premises inherited by the H child.

Write `N=2^m`, `K=2^c`, `T=K N^g=2^n`, where `n=c+gm`, `m,g>=1`.
Axis zero is fastest, with coarse labels outermost. A completed state has
T Gaussian integer numerator pairs on the common F grid. Its component
word width is W. The source supplies factor, cached-coefficient and raw
product widths `W_d,W_c,W_t`. Let `U=max(W,W_d,W_c,W_t)`.

`PreparedFull` consumes the immutable events of the actual `FullTensor`.
It verifies all event dimensions, stage indices and widths, then encodes
H positions and D pages. D pages are emitted highest axis first, preserving
the source's label and digit orders. A complete input is borrowed on grid
`F0<=F`, with signed width `W0=F0+r+2`, where the source radius is `R=2^r`.
Only source preparation and independent checkers use host payload integers.
The sealed invocation does not decode a payload or an unbounded metadata
value into a Python integer.

## 2. Physical admission and the H boundary

Before lifting, `admit_radius` reads all incoming signed words. For each
component it calls the actual word child on the magnitude squared, adds
the exact result to an encoded accumulator and compares with
`2^(2(F0+r))`. Nonnegative summands permit immediate rejection when the
bound is exceeded. On success this proves precisely

```
sum_j (a_j^2+b_j^2) <= 2^(2(F0+r)).
```

There are 2T physical squares. A safe accumulator allowance is
`2W0+n+O(1)` bits; early rejection also prevents an accepted running sum
from exceeding the declared limit. No semantic host norm checker stands
in for this operation. The input remains borrowed and unchanged.

The grid child appends exactly `F-F0` low zeros and enough high sign bits
to produce width W. All movements and copies are paid. For each actual
H event, the predecessor bridge uses service precision `P=W+g`.
The incoming signed integer pair `(a,b)` is encoded as `(a+ib)/2^W`,
whose modulus is strictly less than one. Appending g low zeros supplies
its P-grid numerator. With `H0=H/2`, the complete normalized call returns
the exact numerator of raw H on the original F grid. This is an exact-grid
identity, not a numerical-error-to-equality inference.

The returned signed width is `W+g+2`. The source's complete raw-prefix
bound gives `||state||_2<=4A(R+1)<=2^h` and `W=F+h+2`.
Thus every actual numerator fits W bits with headroom. A second grid call
uses **zero low-bit discard**, checks redundant high sign bits and restores
width W. Fractional precision is unchanged. The H callee returns its
original address frame before the following diagonal accesses its pages.

The accelerated #3627 cost retains its own long-field domain `n=Theta(P)`
and `g<=P^.997`, with its authentic native, internal BIT-stock and ownership
premises. An isolated small local matrix does not acquire that tariff.
This package already uses contiguous complete tensor coordinates. A caller
starting with scattered original low bits must separately pay the earlier
boundary's initial and final gather; its sufficient condition is
`gm<=P^.997`. That gather cost is not hidden in support-local H calls.

## 3. Exact complex products and fresh rounded suffixes

The retained `Arithmetic.complex_product` computes four exact integer
products and two exact signed sums:

```
(a+ib)(c+id) = (ac-bd) + i(ad+bc).
```

Only after these complete numerators exist does `ring_words.truncate`
discard F low magnitude bits and restore the finite sign. This is
componentwise truncation toward zero. The raw result is checked against
the source's `W_t` allowance, and the rounded output against its actual
destination width. The word child returns its complete 2u raw bits for
input magnitude width u, even when the result has a shorter canonical
magnitude. Those padded words and the extra signed-sum bit are included
in O(U), not hidden inside a narrower field-width claim.

For a fixed label, let `d_a(j)` be the supplied F-grid factor on axis a.
The required diagonal is the already-established #4178 protocol:

```
q_g = 1;
q_a = R_F(d_a(j_a) q_(a+1)),  a=g-1,...,0;
output = R_F(q_0 input).
```

`coefficient_field` starts by sign-extending the highest-axis page:
`R_F(d_(g-1)*1)=d_(g-1)` exactly, so no multiplication is necessary there.
For each subsequent axis, it scans each old rounded suffix, rewinds that
axis's complete local page, multiplies the suffix by each digit's factor,
rounds once, and appends the result. Induction on the number of processed
axes proves its value and ordering: the new lower-axis digit is the inner
loop, so axis zero is fastest at completion. It computes exactly the same
nested values as the fresh suffix cache, with a different sequential
storage schedule. This does not repeat #4178's error theorem.

The suffix list has lengths N, N², ..., N^g. For one label, the number of
coefficient complex products is `sum_(j=2)^g N^j < 2N^g`; for g=1 it is
zero. There are N^g data complex products. Each makes four word calls.
Zero factors are legal: there is no division by an old table entry.
Old/new suffix levels, page copies, rewinds and clears sum geometrically
to O(N^g U). Every label's coefficient field is cleared before the next
label and reconstructed afresh at every diagonal. H never touches this
auxiliary bank.

Metadata is also paid. Updating length `N^k` by encoded multiplication
with N costs O(k m²) with the retained schoolbook cardinality primitive.
Summing over axes gives O((gm)²) per label. For `gm>=1`, this is O(2^(gm)),
so it is included in O(N^g U). Counter initialization, ripple control,
table starts and resets satisfy the same bound. No g-factor random-access
oracle or g independent physical tape banks are assumed.

## 4. Exact all-width scalar theorem and complete invoice

The source `physical-ring-product/PROOF.md` §2 proves the actual
`WordProduct` recurrence, including frame movement:

```
M(u) <= 3 M(ceil(u/2)) + O(u),  for u>16.
M(u) = O(u^log2(3));  live scalar workspace = O(u).
```

The code uses the exact Karatsuba difference identity. Its three children
all have width `ceil(u/2)`; the difference sign is finite control.
Schoolbook `Count.product` is called only at the fixed <=16-bit leaves.
Its eleven canonical roles are serialized and restored with O(u) work at
the parent's current width. The stack is a geometric series. No child
scans a root-width padded frame. The caller consumes the full protected
2u-bit result after each product. This is an inherited exact-integer
algorithm theorem, independent of the numerical FFT sections of #3709.

Let H and D now denote event **counts**, and let `C_H(n,W+g,g)` denote the
complete physical raw-H bill, including its metadata, lifting, routing,
internally funded stock, return and sign-only shrink. The complete bill is

```
S_Full + S_encode + S_constructor
  + O(T M(W0+n+1) + T U
      + D T (M(U)+U)
      + poly(n + log(U+2) + log(H+D+2)))
  + H C_H(n,W+g,g).
```

`S_Full` is the actual source/root coefficient preparation and validation
work from the main proof; it is not declared free. `S_encode` includes
all page traversal, signed encoding and immutable metadata preparation.
`S_constructor` includes the inherited compiled native owners and the fixed
private-port inventory. The input term includes the physical radius check.
The D term includes all four real products, exact sums, truncations, table
movement, coefficient buffers, copies, resets and disposal. The global
polynomial term pays cardinalities such as 2^n and control counters; the
per-label metadata was accounted for in §3.

The exact prepared control length, using `b=max(1,ceil(log2 n))`, is

```
S_code = 2(H+D+1) + H g b + 2D KgN W_d  bits.
```

This is an all-stage immutable program, not a lazy stage callback.
After F-grid pages have been generated, the bit-emission work is linear in
this length: one byte conversion per integer is followed by fixed eight-bit
shifts. There is no repeated full-width integer shift for each encoded bit.
Preparation-counter operations can additionally be charged
`O((H+D+DKgN) log(2+H+D+DKgN+n+U))`; they remain in `S_encode`.
Actual source validation, F-grid page generation and conversion from the
original rational source are part of `S_Full`, with the main proof's
explicit preparation cost.

Owned live working space is O(TU) plus metadata and the inherited H-owner
inventory. Total space also includes **S_code**, the source preparation's
own peak/workspace, and already-retained entry backing. `PreparedFull`
does not retain the decoded source program after encoding. On repeated
calls, cleared tape arrays retain their largest old blank extents. With
a fixed number of physical roles the history allowance is
`O(B_entry + max_call(TU) + max_call(S_code) + preparation_space)`, not a
bound on only the latest smaller live payload. Source preparation and its
disposal remain separately charged; clearing does not release old backing.

If `U=O(p)`, `W=Theta(p)`, `n=Theta(p)`, `m=O(log p)` and
`g=Theta(p^beta)` for fixed `0<beta<.997`, then `gm<=p^.997` eventually.
For polynomially bounded stage counts and `N=poly(p)`, `DgN/N^g` tends to
zero, so the control storage is absorbed by the complete field. This is
not asserted uniformly for constant g, particularly g=1 with unbounded
stage count. Source preparation retains its own bill.

For the actual synchronized compiler, `D/H=(8m+3)/(8m+2)=O(1)`. Under the
retained H premises its per-event cost is, up to fixed logarithmic powers,
`V g^alpha`, where `V=2WT` and `alpha=.99827101`. Exact Karatsuba contributes
`O(D V p^(log2(3)-1))`; admission has the same conservative power when
`W0+n=O(p)`. The diagonal power is smaller only when

```
beta > (log2(3)-1)/alpha = approximately .5859756468.
```

For `beta=39/40=.975`, H has power `.97331423475`, above the scalar power
`.5849625007`; the actual source depth factor is paid on both sides. This
is a favorable interface regime, conditional on every stated H, setup,
layout and width premise. Some earlier outer regimes have tiny grouped
dimension exponents; there the Karatsuba term dominates H and remains in
the complete sum. Newer large-dimension outer regimes may be compatible
after a separately checked grouping/retuning. This package establishes no
outer admission, fast scalar tariff for the tiny-dimension regimes, global
elimination of scalar FFT, or change to κ.

## 5. Ownership, diagnostics and physical interpretation

The wrapper has a fixed pool and separate physical children. Parent leases
are exposed as borrowed physical views while its allocation scope is
suspended. Every word/H/grid result is read or copied completely, cleared
and has its owned marker erased before reuse. The prior current field is
released only after its replacement is ready. Each diagonal page and old
suffix level is retired before the next. The caller consumes the protected
final output before another invocation. Prepared control/metadata tapes
are caller-owned, preserved on return, and explicitly disposed by
`PreparedFull.close` at the end of their lifetime.

Before execution, `private_tapes` compiles the constructed fixed owner graph
into a finite forbidden-port inventory. It reads references, not payload
cells. Aliasing with wrapper, word or H private roles is rejected before
tape traffic. All loop counters are encoded. Tape/Arena constructors are
sealed during execution. Successful calls restore the owned workspaces.
The tested radius/endpoint controls have their narrower recorded cleanup
checks; arbitrary interrupted-child recovery is not claimed.

Production supplies no external observer. `WordProduct.calls`, the inherited
boundary call map and the new event map become fixed-key null maps: reads
return zero and writes ignore the value. `UnobservedArithmetic.products`
also always reads zero. Each passive `+=1` consequently has bounded finite
operands rather than a growing host integer accumulated across products.
Opt-in fixtures use ordinary diagnostic maps. These fields never select
a branch, tape operation or numerical operand in the retained kernel or
wrapper. Deleting their updates preserves the operational trace by induction
over execution steps. A paired physical replay checks equal output and
equal registered Tape/Word reads, writes and moves with diagnostics on/off.

Inherited callee call-count, low-level Meter, scratch-peak and allocation
statistics remain the retained emulator's separate observation layer. Their host arithmetic is not part of
the compiled tape algorithm, as in the predecessor model. Fixture timings
and meter counts are not used to establish an all-size asymptotic rate.

## 6. Decisive finite evidence and limitations

From the repository root with Python 3.12 and `sympy==1.13.3`, the physical
checks are:

```sh
python3.12 -B research/full-global-tensor-caller/verify_physical.py --progress
python3.12 -O -B research/full-global-tensor-caller/verify_physical.py --progress
python3.12 -B research/full-global-tensor-caller/verify_physical_controls.py
python3.12 -O -B research/full-global-tensor-caller/verify_physical_controls.py
```

The completion markers are `PASS_PHYSICAL_FULL` and
`PASS_PHYSICAL_FULL_CONTROLS`. The receipt records the actual bounded runs;
[PHYSICAL-RESULTS.json](PHYSICAL-RESULTS.json) preserves their complete
results after removing only the measured `actual_elapsed_seconds` fields.
Normal and optimized outputs are compared in that representation.

The complete actual source fixture is the stored inverse of `(2+i) I_2`,
with target 8, incoming grid 0 and radius 2. Its unchanged source allocation
is F407, W608, factor width 410, cache width 411 and temporary width 1018.
All 21 stages execute: 10 actual raw-H calls and 11 actual complex diagonals,
including the initial physical norm check and final protected return.
The exact physical output agrees with the independent source oracle and
meets the source's complete root-error bound. No input, factor or data grid
was lowered to make the fixture smaller.

This scalar fixture has zero nonzero *stage arithmetic* roundings: its
prepared source approximation is dyadic on the generously allocated grid.
It does execute nonzero imaginary scalar products, and its source-operator
approximation error is nonzero. A separate explicit service fixture has
three axes, two coarse labels and two successive nonconstant complex
diagonals with zeros. It has 40 nonzero fresh-reference roundings. Physical
wrong-label, wrong-axis and stale-stage-page mutations each fail endpoint
comparison. These service pages are not called actual Full compiler output.

A second small service witness separates cached and data-product rounding:
`(3+3i)(2+2i)` has imaginary numerator 12; at F3, complete-numerator
truncation returns 1 whereas separately truncating the two products returns 0.
The physical tests mutate coefficient and data rounding independently and
reject both. Radius rejection, 14 private payload/metadata alias guards,
protected-output reuse rejection, successful same-owner reuse, and final
scratch restoration are checked. Normal and optimized modes use explicit
guards rather than assertions.

The H physical fixture uses #3627's declared reduced q2 source binding.
Its actual metadata plans run, except for a certified finite specialization
of two costly floor-power helpers at the declared fixture values. Each
constant is checked by `r^b<=n^a<(r+1)^b`; encoded comparisons choose it.
Unlisted values delegate to the unchanged original routine. Wrong table
entries are rejected, and a sentinel control proves fallback delegation
without pretending to execute the expensive out-of-domain power. Exact
values, calls and source/fixture scope are in the physical receipts. This
does not test a production native, long-field rate, full multidimensional
Full invocation, or selected supplier.

Cold replay imports the actual source graph and runs physical arithmetic;
it does not just validate a saved successful endpoint. The one-time 534-bit
calibration executed the same exact Karatsuba child through the allowed
fixed-cutoff #3787 wrapper, then that unnecessary wrapper was removed.
Its 2.638-second word run is a finite feasibility observation, not a fitted
cost bound or a retained scalar FFT dependency.

## Open next questions

* Bind a particular admitted outer Gaussian/Toeplitz cohort, its complete
  source preparation bill and grouping parameters to this global service.
  Generic local width or a favorable beta value is not outer admission.
* Supply an exact faster scalar option where small g makes the explicit
  Karatsuba term binding, preserving the same encoded lifecycle.
* Replace all-stage controls with a priced stage producer if general
  constant-g space is important, retaining original page provenance.
* Extend the finite whole-Full replay to multiple axes at unchanged proved
  precision only when that cost resolves a specific remaining obligation.

Credit #3709's exact word implementation, #3627's H/support composition,
#4178's rounded suffix/height contract, #4205/#4253's Full and fixed-H
producers, and the source-owned boundary above. Separate agent checks are
not independent human acceptance or formal-kernel verification.
