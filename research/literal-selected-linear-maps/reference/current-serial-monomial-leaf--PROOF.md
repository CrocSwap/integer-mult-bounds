# Direct current monomials without ordinary runtime calls

**Conditional enabling lemma; executed gates and complementary review passed. No new kappa.**
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Exact unchanged monomial dependency:
`CubeJerry/integer-mult-bounds@7d1ff23714e6f9182c1d0ff9214f65def2f30e04`,
`research/current-coded-gaussian-monomial`. Every reused byte is separately
authenticated by DEPENDENCIES.json. No retained monomial, Compact, Count,
Tape, or ordinary constructor source is changed.

## Claim, useful domain and predecessor distinction

The retained monomial already has a genuine one-column branch with no ordinary
runtime invocation. That fact and source history/action analysis are prior
results, including [#3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087)
and [#4172](https://github.com/CrocSwap/integer-mult-bounds/pull/4172). Current
descriptor adaptation is the public monomial package above. Literal local
header views are also supplied by public commit
`772198276518065c6ae42ef4bafc77df9c3c73b3`. These mechanisms are not claimed new.
The new implication serializes a complete valid current multi-column monomial
through actual one-column calls, with an exact private descriptor identity,
absolute tensor phases, a physically encoded iterator, and its repeated bill.

**Conditional theorem.** On valid current geometry and the domain where every
serialized intermediate signed phase fits, SerialProvider executes exactly
the parent tensor monomial, including its absolute phase, without any ordinary
runtime call. A sufficient uniform domain has every real and imaginary signed
component strictly between -2^(h-1) and 2^(h-1). This is narrower than the
original batched provider's success domain; see the counterexample in section4.

This is a direct leaf alternative, with all costs below. It does not establish
the faster nonleaf ordinary tariff or an accepted recursive recurrence. It
removes a completed ordinary runtime numerical/rate premise from this route,
while retaining its finite constructor/inventory and all digit-permutation,
signed-phase, physical-tape, ownership and format contracts.

## 1. Exact geometry and operator identity

Retain the monomial provider's complete coded-field contract: uniform signed
component width h>=2, its exact record delimiters and common quantum, supplied
local LEFT markers and aligned origins, and actually disjoint public, context
and private segments. Current private prefixes start physically blank; previous
erased backing remains allocated. These are caller premises, not inferred
from object identity or a short fixture.

Let a valid parent monomial descriptor have fixed recipe rank m, positive f,K,
0<=rho<K, active start u, back start z, address width a, positive H,G, and
remainder e with 0<=e<m. Its selected axes are mf+e<=d. It obeys

    (f-1)G <= H,  2H <= u,  u+mfK <= z,  z+H <= a.

The complete row satisfies row_bits=record_bits*2^a, with unchanged outer
count, row count, signed component width and common grid. The parent recipe
acts on bit positions u+(if+j)K+rho, for i=0,...,m-1 and j=0,...,f-1.

For column j construct a private descriptor with exactly four changed fields:

    f'=1,  K'=fK,  rho'=jK+rho,  selected_axes'=m+e.

All nineteen other fields remain unchanged, including e,p,d,H,G,u,z,a,
entry_start, row_bits, record_bits, grids and cutoff. This private monomial
view is never supplied to an ordinary provider. It need not preserve unused
global producer relationships involving p or entry_start. Only the exact
retained monomial consumer and its stated guards receive it.

We have 0<=rho'<K' and m+e<=mf+e<=d. The used compact reservation t' is zero;
before=u-2H and after=z-u-mfK are unchanged. Used widths become
(0,H,0,H,before,fK,...,fK,after,0). The coefficient suffix grows to a-z,
exactly offsetting the smaller enumerated address extent z, so no complete
field bit is dropped. The chosen position is exactly
u+iK'+rho'=u+(if+j)K+rho. Each actual one-column call therefore applies the
recipe on column j, preserving every other coordinate, coefficient and row.

Different columns use disjoint coordinate factors. Their complete linear maps
commute and their product is the parent tensor monomial. The constant Gaussian
phase occurs once per column, giving i^(f*c), not i^c. Inverse one-column maps
likewise multiply to the inverse parent map. Equality includes absolute phase.

The unchanged engine computes n=f'-1=0 and uses single_column_rows for every
affine gate. Its flip_digit/digit_permutation route never calls compact_gate
or the ordinary engine. Signed phases, full-field conversion/copying and
cleanup still execute. Exact numerical success requires the stated additional
intermediate representability condition.

## 2. Physically encoded descriptor iteration

column_view.py emits finite PREPARE, NEXT and RELEASE tables from the unchanged
Builder. Runtime instructions are local symbol reads/writes, unit moves,
jumps and two fixed terminal labels. Forty-five fixed private raw binary ports
hold decoded fields, saved f and K, a counter, sum and private child view.
No runtime shape is decoded into a Python integer or used to allocate work.

PREPARE decodes 23 canonical fields, checks positive f,K and computes fK by
physically encoded repeated addition of K, comparing an encoded counter to f.
It writes f'=1 and m+e, resets j=0 and emits the first view. NEXT destroys the
private view, increments j and compares it with f. For j<f it adds old K to
rho' and encodes another complete view; at equality it returns `finished`.
RELEASE clears all current private prefixes and restores origins. The wrapper
invokes one real unchanged monomial provider between `ready` and NEXT.

The provider is constructed/bound once and never reset or recreated between
columns; its closed ordinary object remains allocated. Parent bytes and all
ancestor prefixes are read-only. Valid parent geometry is an input premise,
not a consequence of checking canonical encoding and positive f,K.

Let E be the original descriptor length. bitlength(fK)<=bitlength(f)+bitlength(K)
and bitlength(jK+rho)<=bitlength(fK), so child and working lengths are O(E+1).
PREPARE costs O(f(E+1)), each NEXT O(E+1), and RELEASE O(E+1). Thus metadata
cost is O(f(E+1)), with O(E+1) current backing per fixed role. Historical
backing remains counted. Later small calls scan their current prefixes and
receive no free allocator/history reset.

## 3. Full optimistic invoice and useful asymptotic domain

Write C=outer*rows, R1=2hr*2^(a-z), M1=C*2^z, Vraw=M1*R1,
and A1=2+z+ceil(log2(R1+1)). Let g count the finite affine gates and V be the
complete coded field length. Each one-column call pays its entire inherited
bill, codec, encoded setup and retirement, hence

    F_template + O_m(f*((g+1)*(Vraw+M1*A1^6) + V + (E+1)^4 + Q)).

Q includes the complete fixed work inventory, including unused ordinary
tapes. Setup is paid f times; provider/ancestor historical maxima remain in
the space bill. No ordinary cost is subtracted from an unrelated upper bound.
Under explicit R1>=A1^6 and (E+1)^4+Q=O(V), this is F_template+O_m(fV).
The larger displayed bill remains if either absorption condition fails.

This can match a direct PAID-leaf budget when a separate global cutoff admits
the complete source construction, including rf<=cutoff for a rank-r leaf.
No such cutoff, compiled stock/precision substitution, new supplier rate or
assembled kappa is established here.

## 4. Strict numerical-domain distinction and rejection

Phases act as signed permutations of the real/imaginary components. Strict
symmetric component headroom is invariant under every such phase and address
permutation, proving all intermediate representability in the sufficient
domain. The unchanged common grid needs no extra arithmetic rounding.

The original combined-phase admission does not suffice. For a constant-phase-2
monomial with f=2, the tensor phase is +1, so a most-negative h-bit component
can pass the batched phase. The first serialized column multiplies it by -1,
which cannot fit. Thus the two acceptance domains are provably different.
For the actual selected right recipe, whose constant is1, f=4 and an input
supported on the all-zero selected bits similarly has combined phase +1;
serial quarter rotations can expose an unrepresentable intermediate negation.
This caveat was found by the separate native worker's adversarial review.

Each retained one-column call preserves its input on its named arithmetic
rejection. Earlier completed columns can nevertheless have changed the serial
field. SerialProvider therefore has no whole-job rollback guarantee. A full
protected stage, such as the separately published atomic MOVE wrapper, must
pay transfer/commit/retirement to obtain that property. No interruption or
malformed-success rollback is claimed.

Global native source correctness, the full compiler placement, ownership,
precision and analytic multiplication assumptions remain. Finite witnesses
do not discharge those universal premises, and no accepted certificate changes.
