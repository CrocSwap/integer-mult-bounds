# Four-bit residue reduction for reversible P104 lifting

**Scoped mathematical reduction and executable reference; no new κ or admitted
fast recursive supplier.** The rank-seven nonlinear transform of
[PR3025](https://github.com/CrocSwap/integer-mult-bounds/pull/3025) can be evaluated
with one wide exact linear transform and a lifting pass on just four input bits
per real component. This preserves the entire nonlinear map, its literal inverse
and the collector's exact cleanup. A direct integer Walsh backend demonstrates
2.08×–3.75× speedups at 4,096–65,536 input bits on this machine; 64-bit inputs are
slower. The reduction exposes a precise backend contract and an unresolved
low-precision regime, rather than assuming either away.

Base: `d8e0f83f00191df62174b641e9fff055c357f641`.
Predecessor: PR3025 at `a544ef068a46f4de3bc47d1d02149cbdc3ba547f`.
The byte-identical vendored `lifting.py` is authenticated by
[PREDECESSOR.json](PREDECESSOR.json) before execution. The actual rank-seven
native calls are word events 2031/2033, between gather/ungather at 2025–2039,
from PR2586 at `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`.
[SOURCES.json](SOURCES.json) pins their archived bytes on this base. The selected
κ is still 0.001672660197076918 (PR1094); this package does not alter it.

## Exact reduction

Work over Gaussian integer vectors of length N=2^n, with 1≤r≤n. Let P be the
componentwise-floor pair lift from PR3025:

```
d = a-b; s = b+floor(d/2); d = i*d;
b' = s-floor(d/2); a' = b'+d.
```

Its ideal is C(a,b)=((a+b+i(a-b))/2, (a+b-i(a-b))/2).
If d=p+iq and t=(q mod 2)-(p mod 2), then

```
P(a,b) = C(a,b) + (t(1-i)/2, t(1-i)/2).
```

Let L_r apply P along distinct address bits 0,…,r−1; let U_r apply C on those
bits. Arbitrary exact Gaussian monomial wrappers may be attached on both sides.
Put **g=⌊r/2⌋+1**. For all Gaussian integer x,z,

```
L_r(x + 2^g z) = L_r(x) + 2^g U_r(z).                 (1)
```

The same equation holds for the literal inverse, using L_r⁻¹ and U_r⁻¹.
Consequently, componentwise Euclidean division x=2^g q+s, 0≤Re(s),Im(s)<2^g,
gives

```
L_r(x) = 2^g U_r(q) + L_r(s).                       (2)
```

This is a statement for all signed inputs, not just tested bounded integers.
It is a mathematical proof in ordinary prose, not a machine-checked theorem.

### Proof of (1)

Each nonzero coefficient of a product of j distinct ideal factors is a Gaussian
unit times (1+i)^j/2^j. It therefore has real and imaginary denominators dividing
2^⌈j/2⌉. Suppose the translated and untranslated computations agree up to their
ideal translation after j stages. Before stage j+1, their difference is
2^g times the j-factor ideal image of z. For 0≤j≤r−1,

```
g ≥ ⌈j/2⌉+1,
```

so every real and imaginary component of this difference is even. In particular,
both difference parities p mod 2 and q mod 2 in every next pair are unchanged.
The displayed parity correction is unchanged, and the next difference is
exactly its ideal linear image. Induction proves (1), and also the integrality
of its right-hand translation. Signed floors cause no exception: parities use
Euclidean residues in {0,1}. Wrappers preserve the Gaussian lattice and its
2^g sublattice. For the inverse, reverse the order, use −i, and invert both
wrappers. The correction still depends only on the two parities and the ideal
prefix denominators are the conjugates of the same j-factor denominators.
Thus the identical induction applies.

### The uniform forward threshold is sharp

It suffices to consider no wrappers and N=2^r. No uniform smaller power of two
works for this word. If a smaller lattice worked, translating repeatedly by its
generators would also give equivariance for 2^(g−1), so only that case is needed.

For r=2k+1, 2^k U_r(e_0) has half-integral real and imaginary components.
It cannot equal the difference of two Gaussian integer outputs.

For r=2k, set x=e_0 and translate by 2^k e_0. The first 2k−1 stages are equivariant
at this scale by (1). Their unshifted output is i e_t, where
`t = sum(2^j for odd j < 2k−1)`: on a previously untouched bit, a unit real impulse
becomes a unit imaginary impulse at the lower endpoint; the next such stage
moves it to a unit real impulse at the upper endpoint. Their ideal translation
has every active coefficient in {±1±i}. In the final stage, the pair at t has
unshifted difference i, with parity correction t_parity=1. Translation flips
both parities, giving t_parity=−1. Its two outputs therefore each change by
(−1,+1) *in addition* to the ideal translation. Every other pair has zero
unshifted difference and equal translated parities, so no correction change.
This proves failure. The replay exhibits these two failing outputs for even
r≤10 and all 2^r failing outputs for odd r≤9. Those finite witnesses corroborate
the argument; they are not its proof. We do not need inverse minimality here.

## Executable exact linear backend

Write H_r for the unnormalized Walsh transform on the active bits and
D[x,x]=(−i)^popcount(x mod 2^r). The elementary 2×2 identity gives

```
U_r = ((1+i)/2)^r D H_r D
2^g ((1+i)/2)^r = 2 i^k          if r=2k,
                       (1+i)i^k if r=2k+1.
```

Both final multipliers are Gaussian integers. `split.linear` uses only exact
integer additions, differences, signs and these multipliers. The inverse uses
the conjugate phases and reversed adjoint wrappers. The verifier compares both
directions with independent rational butterfly numerators on every one of the
512 basis columns of the actual native recipe. Since this backend is linear,
those column checks are complete for that finite matrix. Separate nonlinear
checks compare (2) with the unchanged predecessor implementation.

`split.kernel` extracts signed quotient and nonnegative residue into two owned
arrays, computes the wide and narrow maps, recombines into the caller's array,
and resets both auxiliary arrays to zero. Its optional observer only checks
those final values; it is absent in the benchmark. This is an ordinary mutable
integer implementation. Reset is paid overwrite, **not reversible uncomputation**.
Python allocation/assignment is not evidence of an admissible tape or dirty
workspace implementation. A backend is trusted to satisfy its exact contract;
the caller has no cost-free runtime oracle for detecting a wrong backend.
The verifier deliberately injects a one-unit backend fault and detects it.

The collector test substitutes only this kernel into the byte-identical PR3025
collector. All query, grid, entrance, sent, returned and private-zero values must
match. The old scalar-operation meter is deliberately not reused as a price
for this implementation; the new logical invoice is separate.

## Full cost boundary

Here W bounds the magnitude bits of each real input component, W≥g. All widths
below include O(1) sign/carry bits. The model is fixed-width integer bit work on
owned mutable arrays with charged reads, writes and reset; it is not a physical
native supplier tariff. Wrapper plans and pair schedules are public recipe data. The reference
recomputes cycle traversal/visited sets per call; its address work is included
below. Plan construction, address work and routing are not free.

Let E(N,r,w) be the **complete** cost of an exact scaled linear backend with
w-bit signed inputs, including its two wrappers, all workspace and cleanup.
The scale is 2^g; its output can use w+O(r) bits. The residue lift uses at most
g+r+2 signed bits: one pair increases the component magnitude bound M to at
most 2M+1. Thus a complete split transport has the bound

```
S(N,r,W) ≤ E(N,r,W−g+1)
           + O(N r(g+r) + N(W+r) + N r n) + Setup(N,n).       (3)
```

The terms respectively pay for: the full narrow lift; extraction, recombination,
allocation and reset plus the narrow wrappers; address/schedule processing;
and one-time public plan construction. Here wrapper permutation accesses are
charged at their moved bit widths in an addressed-array model; physical routing
may cost more and remains open. Explicit plans take O(Nn) bits; expanding the
pinned degree-two wrapper description costs O(Nn²) elementary bit operations.
The O(Nrn) term allows n-bit address processing per pair. The small rank-seven
case uses exact N=512 plans; no variable-size native recipe is inferred from it.

Per transport the residue pass pays rN/2 pairs, 4Nr real additions, 2Nr floor
halves, rN/2 quarter turns and 2N wrapper values. Pair reads/writes and all
cycle swaps are also recorded in the source-bound logical invoice. Extraction reads 4N components in the two Python
passes and writes 2N quotient plus 2N residue components. Combination reads 4N
components, performs 2N additions and writes 2N components. Final reset writes
4N components. Both Gaussian arrays and the bounded pair/cycle scratch are
charged. Backend operations, including its own two wrappers, are additional.
For N=512,r=7 this is one backend call, 1,792 narrow pairs, 14,336 narrow real
additions, 7,168 narrow halves and 2,048 reset component writes. Wide and narrow
wrapper passes are both present; neither is silently shared.

For a direct backend, on one active block the Walsh recurrence is

```
H(0,w)=O(w),
H(r,w)=2 H(r−1,w)+O(2^r(w+r)),
```

with 2^(n−r) blocks and the wrapper/phase/reset work added. Hence it costs
O(Nr(W+r)); our implementation is still a direct transform. Its wide butterfly
uses four real additions per pair instead of the predecessor's eight plus four
floor-halves. Narrow correction adds work, and the asymptotic order is unchanged.

For the full collector, let M be the maximum integer component of the gathered
source S, f the incoming fractional precision, and b the error request. As in
PR3025, if M=0 take F=f; otherwise h=⌊log₂ M⌋−f and
`F=max(f,b+8−h)`. Set W_C large enough for S at grid F and its intermediate sent
value (the latter needs at most O(r) extra magnitude bits). A complete collector
bound is

```
C ≤ S(N,7,W_C) + S(N,7,W_C+O(r))
    + O(N(W_source+W_query+W_C+n)) + public setup.
```

The last term pays **all five gathers, query promotion and addition, five
ungathers, magnitude/grid scans, two embeddings, exact downshift, C initialization,
zero check and erasure**, with reads and writes at their actual widths. There
are two exact backend calls in the collector. Source/query storage remains with
its owner; two additional owned buffers are reused for each transport. Exact
map equality transfers PR3025's error guarantees and exact return of private C.
It does not transfer an unproved cheap recursive cost or internal dirty-memory
contract. No new source accesses, helper transports or restoration calls are
hidden in E; an implementation requiring them must charge them there.

### When could this support a faster recursive implementation?

Conditionally suppose an admitted exact backend, including its workspace,
wrappers and cleanup, satisfies E=O(NW r^(1−a)), 0<a<1. For n=Θ(r), (3) has
O(Nr²+NW) extra work. It inherits the assumed bound in the regime
**W=Ω(r^(1+a))**, including setup. At W=Θ(r), this explicit residue algorithm
only supplies O(Nr²), so it does not establish the desired saving. This is a
limit of the priced reduction, not an impossibility theorem for other methods.
If a proposed backend calls recursive children, their full recurrence belongs
inside E; this package constructs no such backend and assigns none a cheap cost.

Nor may a merely relative-accurate native child silently replace E. Exact output
is required, or certified component absolute error <1/2 before integer recovery.
For |input component|<2^W and W≥g, ||q||₂≤√(2N)2^(W−g), hence
||2^g U_r(q)||₂≤√(2N)2^W. A sufficient relative error request is

```
u ≤ 2^(−W−ceil((n+1)/2)−2),
```

which puts the Euclidean error at most 1/4 and ensures unique nearest-integer
recovery. The same calculation applies to the inverse. Zero input must be
exact. This may demand far greater precision than the collector's original b;
its cost cannot be replaced by that original request. A one-unit fault and a
half-integer tie are explicit controls. Certified recovery work also belongs in E.

## Evidence and reproduction

From repository root, with Python 3.12 (stdlib only):

```sh
python3.12 scripts/research_package.py --package research/p104-lifting-residue-reduction
```

Expected: `PASS_P104_LIFTING_RESIDUE_REDUCTION`, eight control tests passing,
and the package runner's PASS. [RESULT.json](RESULT.json) is an exact typed
receipt; verification never rewrites it. The bounded coverage is ranks 1–10 in
both directions with deterministic seed 53, 2,592 exhaustive signed pair cases,
all 512 native columns in both directions, five native paired widths and four
full dirty collector fixtures. Stopping rule: prove/refute the uniform guard,
finish that fixed coverage and measure the five declared widths. No open-ended
search or claim of exhaustive large-rank inputs is made. Tests reject source,
native-event, wrapper-phase, inverse-order and typed-receipt drift; a read-only,
Git-free export runs the public verifier with assertions disabled.

Timing reproduction (observations vary; no speed threshold in CI):

```sh
python3.12 -I -B research/p104-lifting-residue-reduction/benchmark.py
```

[BENCHMARK.json](BENCHMARK.json) retains all seven paired timings per width,
interpreter/platform and seed. Both algorithms receive identical signed data;
execution order alternates, every output is compared exactly, and both wrapper
passes, residue processing, allocations and resets are timed. Only the equal
initial input copies and verifier comparisons lie outside the timer. Measurements
are forward transports using the actual outbound recipe, not a whole-supplier or
end-to-end multiplication benchmark. No repeated best-run selection was used.

| Input magnitude bits | Direct median ms | Split median ms | Speedup |
|---:|---:|---:|---:|
| 64 | 3.690 | 4.856 | 0.76× |
| 512 | 4.839 | 4.776 | 1.01× |
| 4,096 | 15.425 | 7.414 | 2.08× |
| 32,768 | 103.199 | 29.997 | 3.44× |
| 65,536 | 200.299 | 53.416 | 3.75× |

## Open next questions

1. Can the exact scaled linear map use an admitted recursive child at a price
   favorable after the W-dependent precision request? Start with one explicit
   rank-seven call and price precision conversion, all children and cleanup.
   The blocker is a full exact/certified-recovery backend, not equation (2).
2. Can the narrow correction be evaluated in o(Nr²) bit work when W=Θ(r)?
   Start by exploiting its bounded residue alphabet and the proven translation
   lattice. Its input dimension still grows with N; a lookup table is not free.
3. Can the two owned buffers be realized within the project's physical storage
   and restoration rules? Start by assigning addresses and paying every reset
   or replacing it with priced uncomputation. Private C returning zero does not
   resolve this separate internal workspace obligation.

## Scope selection and credit

This is an explicit user-assigned recursive-implementation follow-up, not a
fresh randomized supplier search. Seed 53 only diversifies fixtures. The three
scoped candidates were a macro-shear wrapper (at least three wide native calls),
retained rounding history (storage/extra passes), and the chosen residue split.
The latter preserves the original map with one wide call per transport. Initial recent
PR/discussion metadata through PR3025 and the retained historical corpus were
searched for low-bit, bit-plane, half-angle, Cayley, precision-splitting and lifting
work; no overlapping implementation was found. This is not a full literature
or all-diffs novelty claim. The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18981105)
is on Discussion2750. A pre-submission refresh read the 30 most recently updated
PR bodies through PR3030 and eight recent canonical-thread comments. New
PR3028/3030 address larger-stock conditional packing releases, a distinct
obligation; no new overlapping residue implementation was found. Main and the
PR3025 source head remained unchanged. Coverage limits are in TASK.json.

Prepared by **Tekalign**, with substantial **OpenAI Codex assistance** in the
proof, implementation, tests, benchmark and write-up. Apache-2.0. PR3025 supplies
the reversible lifting map, collector, parity/error analysis and original Python
reference; this package contributes the sharp translation lattice, exact split,
Walsh backend and complete cost/precision boundary. The occurrence-binding
verifier is adapted from PR3025/PR2999 with credit retained. `ywz65`'s PR2586
supplies the pinned physical word/native recipes. PR2555 supplies the earlier
full-grid/rounded-shear restoration precedent; neither generic reversible shears
nor the Walsh factorization is claimed as novel. The P104 supplier and broader
project retain their original contributors and conditional assumptions. Frozen
sources, shared checkers and the selected frontier are unchanged.
