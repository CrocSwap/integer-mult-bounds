> **Retained #6805 review.** This text and its numbers describe the #6805 word it was written for. The lifted word here has 66,888 paid requests and paid rank mass 178,044; see `RESULT.json` and `VALIDATION.md`.

# Final proof and README audit

**Corrected pass within the stated conditional scope.** The earlier version
of this review missed the additional canonical-job adapter charges and
incorrectly accepted 252,223,008 as a complete ordinary bound. That statement
is withdrawn: 252,223,008 was a partial estimate. The complete independently
recounted bound is **535,415,008 < 10^9**. Existing audit #6763, pinned at
`c3e0500c7645b1bc228ebe5e5190e304a2da46ca`, supplied the explicit adapter
contract; this review's own checker independently reconstructs its counts
from the current literal caller. The Gaussian invoice, field allocation,
strict gain and final kappa qualification are unchanged.

This audit
reads the frozen `PROOF.md`, `README.md`, relevant emitted-word/checker code,
the final combined receipt and the separately written local/invoice receipts.
It does not rerun the expensive native/physical/compiler suite or claim human
or proof-kernel acceptance.

Reviewed document hashes:

| File | SHA-256 |
|---|---|
| PROOF.md | `3bf08ba92bf0f878737f3bf61610e9c911d006319c1751af5b76fd1853bbe9dc` |
| README.md | `243b7f52ae54a7b8a3d93a6cc98a4cf08c87f83b77ccbe61eb8cd8ee3110dbf9` |

The combined receipt must incorporate the updated independent invoice during
the final normal/optimized/cold replays. No earlier receipt's partial ordinary
subsection should be used as a complete-budget certificate.

## Rectangular maps and owned domains

The proof does not require an invertible prefix or suffix. Its precise
well-typed interpretation is as follows. Let `X = Q^771` be the original
public-input/output space and `Z = Q^800` the padded cut-state space, including
all 29 owned labels. The prefix `P: X -> Z` includes the explicit owned
initialization. The suffix `S: Z -> X` means the formal suffix followed by
projection to the public outputs. Consequently `SP = M`, where `M` is the
old public native map. Inactive owned slots may be padded with zero; they
are not additional independent public inputs.

The boundary basis `G` is an automorphism of X, supported entirely on
equal-boundary helpers. The cut basis `J` is an automorphism of Z; it is the
identity away from the listed public roles at frame 243. Thus

\[
Q=JPG^{-1}:X\to Z,\qquad R=GSJ^{-1}:Z\to X
\]

are legitimate rectangular maps. The checked identities imply

\[
e_p^TQ=cG^{-1}=e_p^T,\qquad
Re_p=GSb=Gd=e_p.
\]

Since `G` acts only on an identity helper block of M, it commutes with M,
so `RQ=GMG^-1=M`. Replacing the cut coordinate by arbitrary z gives

\[
R\bigl(Qx+(z-x_p)e_p\bigr)
=Mx+(z-x_p)e_p.
\]

The old role p has already returned the value `x_p` at frame 243; the suffix
coordinate p is renamed to fresh role 771 and returns z at frame 127. Every
other public output is unchanged. This explains both boundary maps and
requires neither an inverse of P/S nor a zero assumption on the fresh input.
The stronger complete local audit also verifies that final owned outputs are
zero and that no initial owned value contributes to any output.

The channel identities alone would not prove the legality of a guarded COPY
after arbitrary cut replacement. The proof correctly cites a separate
candidate-wide pre-COPY monitor; it passes for every arbitrary public input.
The independently evaluated suffix direction b also passes its COPY-zero
guard. CLEAR functions may change under the basis. The proof explicitly
retains the owned-erasure premise instead of treating their unchanged count
as a proof of unconditional erasure. The 47 lifetimes, 45 nonzero CLEAR
observations and zero/nonzero pattern agree with the independent receipt.

## Retiming and the general economic criterion

The source event and contact-free interval agree with the checked witness.
The prepared path is `749 -> 243 -> 127`, with dimensions `3 -> 4 -> 9`;
the helper's entry is frame 3 of dimension zero. All required strict span
inclusions were checked by the local audit. The common intermediate chart
permits the supplied dyadic bases; there is no hidden cross-chart exchange.

The literal deltas are correctly stated as
`delta P = H1 + H5 - H6` and `delta T = H4 + H5 - H9`. Their difference
`H4 + H6 - H1 - H9` is strictly positive throughout `0 < t < 1` by the
displayed integral. Both rank masses are unchanged.

The proposed general economic pattern is also correct. For dimensions
`e < a < f < v`, write `u=f-a`, `h=a-e` and `s=v-f`, all positive. Its
left side equals

\[
\int_u^{u+h}
\left[t x^{t-1}-t(x+s)^{t-1}\right]\,dx>0.
\]

The inequality pays for the donor subdivision. It is a sufficient accounting
pattern only when the required legal frames and independent-channel identities
exist. The proof explicitly states this limitation and makes no general
existence, optimality or second-gain claim.

## Receipt and claim consistency

The primary receipt and independent invoice have identical complete T/P
histograms: 13,688 productive fields, 66,870 paid requests, paid rank mass
178,080 and surplus 760. The eighteen new helper allocations, 20,304 total
helper normalizers, local scalar allowance 138,374 and per-call count 5,533,374
all agree. The corrected complete ordinary upper bound is 535,415,008 as
derived below. The stated physical
counts match the receipt: 2,940 distinct native maps, 208 main adapters,
1,128 helper normalizers per call, 1,536 changed-pair explicit columns,
7,488 caller contacts and 53,248 central-square columns.

The final receipt claims `165407/50000000 = 0.00330814` and tests
`661629/200000000 = 0.003308145`. Both exact engines report tested margin
in the interval
`[0.000043164272593392920133476725,
  0.000043164272593392920133476726]`.
The raw bracket and compiler gap agree with the independent final-parameter
audit. The receipt has all 54 strict and four functional outer inequalities,
the retained BIT saving 17/5000, and `word_materialized=false`.

The README's gain 0.00000094 over the pending claim 0.00330720 is exact;
its stated approximate relative increase 0.0284% is correctly rounded. The
selected-frontier flag is false and the README explicitly retains the
selected value 0.003125804.

## Corrected canonical adapters and ordinary budget

The old flat allowance of 1000 units for each of the 3,536 main-output routes
did not account for every canonical-job boundary on the full 153-axis
carrier. It also omitted the explicit whole-idle and thin-query adapters.
This is an ordinary-cost omission; none of the Gaussian rank requests changes.

For each selected coordinate set I of rank r, the independently written
checker pairs coordinates missing from the first r positions with selected
coordinates outside those positions. It constructs the actual involutive
permutation and verifies that it maps the canonical set to I. Both boundaries
pay for all resulting two-axis swaps. It separately verifies the orthonormal
q bases, maps q to coordinate zero, and reconstructs all 512 nine-bit addresses
for each of the 104 bases. Both q-basis boundaries and the `Q^2` translation
for a negative q exponent are counted.

| Canonical adapter | Elementary maps |
|---|---:|
| Main two-axis swaps | 144,768 |
| Main q-basis maps | 6,656 |
| Main endpoint translations | 3,328 |
| Whole-idle two-axis swaps | 127,296 |
| Thin-query q-basis maps | 3,120 |
| Thin-query translations | 1,560 |
| **Total** | **286,728** |

Every elementary map has support at most nine axes. The retained fixed-map
rate is charged separately for every map; it is not applied once to an
arbitrary full-carrier map. The previous 3,536,000 flat route units are
replaced by 286,728,000 units, a net correction of 283,192,000. Main-output
scalar work remains 91,936. The full budget is

\[
18\cdot10^7+68570112+24960+91936+286728000=535415008<10^9.
\]

Using the counted native work gives 455,015,740. All helper normalizers remain
separately included in each local call. The updated independent checker passes
both normal and optimized execution with byte-identical results. The corrected
PROOF and README now state the full bound and identify the former partial
estimate. The existing compiler's one-billion envelope remains sufficient.

The precision paragraph is properly conditional: scalar majorants, charged
Gaussian rank mass, additive COPY errors, owned erasure and movement scratch
remain within the stated implementation contracts. It does not incorrectly
identify exact overwrite notation with physical removal of approximation
errors, or assume descriptor constants are absorbed at the displayed finite
supplier threshold.

## Attribution and limits

Ali Romman's helper-basis mechanism, the #6702 and #6726 sources, and the
retained native, caller, compiler, interval and analytic authors are credited.
The adapter note identifies the modified drivers and preserves the distinction
between adapted code and unchanged retained sources. The claim is explicitly
author-side, conditional on the same five named assumptions, and dependent
on pinned pending predecessors. It claims neither independent human
acceptance nor a materialized full multiplier, exhaustive novelty search,
historical ancestry authentication, global optimum or selected-frontier change.

The ordinary-accounting repair above is required and does not alter the frozen
positive native construction. After incorporating it and regenerating the
combined receipt, no further discrepancy was identified on the points reviewed
here. Separate exploratory failures do not change this verdict and are not
used as universal obstructions.

Reviewed for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
