# Ternary star refinement: conditional kappa = 3.8e-9

This contribution refines Zhihao Chen (jacklightChen)'s
[ternary five-subset network in PR #7](https://github.com/CrocSwap/integer-mult-bounds/pull/7),
pinned at `6725c6a17b17871a35353fd29157f4ed851bc114`. It saves another **170,400
addition nodes** in the producer and supports the conditional witness

$$
\kappa=\frac{19}{5\cdot10^9}=3.8\times10^{-9}>2^{-28}
$$

in `T(n) = O(n (log n)^(1-kappa))`. That is `380/373`, approximately **1.88%**,
above PR #7's `3.73e-9` headline witness. It is an asymptotic exponent-saving
comparison, not a measured runtime improvement or a global optimality claim.

**Status: unreviewed, conditional circuit refinement.** The general arguments
in PR #7, its complex network, eumemic's faster Gaussian resampling in
[PR #5](https://github.com/CrocSwap/integer-mult-bounds/pull/5), the compact-control
interfaces, and the pinned upstream multiplication theorem remain assumptions.
There is no full formal multiplication proof or integrated manuscript patch.

The same earlier `5.9e-10` witness as this fork's geometric exploration was
already proposed in eumemic's [PR #3](https://github.com/CrocSwap/integer-mult-bounds/pull/3).
The present refinement therefore starts from PR #7 rather than treating the
geometric exploration as the strongest community candidate.

## What changes

PR #7 replaces each four-point star's interior with a monotone circuit for its
required boundary sums. A star has variables `x_(B union {u})` for a fixed
four-set `B`; its requested sums are represented by exact masks of the varying
point `u`. PR #7's greedy rule prioritizes the most frequent pair of current
terms, then the smallest union support.

The new rule instead favors the **largest union support** when the frequency
is tied. The driver compares the published rule and two versions of this
alternative, with ascending and descending union masks. It prunes unused
addition ancestors, verifies each candidate, and retains the smallest circuit
for each canonical template. This is a reproducible heuristic, not a proof
that the templates are optimal.

Other tested approaches were not promoted: transposed incidence circuits and
dyadic circuits lost on the twelve most frequent templates; multi-term bundle
factoring sometimes beat the published rule but did not beat the selected
large-support rule on those examples. Aligning contracted pair groups produced
a larger global producer. The committed `star_duality.py` retains those
experimental methods; the certificate uses only its specified three-candidate
selection rule.

## Why the replacement preserves the mathematical interface

Each current expression is a partition of its requested source mask. Replacing
two disjoint terms by their union preserves its coefficient vector. An
already computed union may be reused; collapsing other partitions of that
same union again preserves coefficients. Thus every generated addition is
cancellation-free and every requested boundary sum remains exact. Deleting
nodes with no path to a boundary output preserves the map.

The independent C++ pass reconstructs all original star boundaries from the
complete producer. It checks every selected gate's operands and disjointness,
and checks every required output against the independently reconstructed
mask. Repeated enumeration must also reproduce the demands byte-for-byte.
It checks all 20,475 stars and 365 canonical templates.

All new nodes remain inside the same fixed four-point star. Their source
indicators therefore contain a common pair, as required by PR #7's rational
label argument for `H = I - (2/25)J`. For a vector `u` in such a source span,
the two common coordinates both equal `t`, and the coordinate sum is `5t`.
Consequently `u^T H u` equals the sum of squares of the other coordinates.
It is positive for nonzero `u`: if those coordinates vanish, their sum `3t`
forces `t=0`. Every new source span is therefore nondegenerate. Disjoint sums
give nested source spans; unchanged side outputs retain their target
orthogonality. Complement frames supply the reversed inclusions.

The generic outgoing-use/pivot compiler uses `c+q` auxiliary roles and the
same dirty-scratch cancellation argument. The retained-total outputs, their
span dimensions, stage-bank joins, endpoint corrections, and decreasing
dimensions are unchanged. Conditional on PR #7's general tensor and transfer
arguments, only the auxiliary-width constant changes in its rank formula.

## Exact counts and witness

| Quantity | PR #7 | This refinement |
| --- | ---: | ---: |
| Four-point-star additions | 2,623,060 | 2,452,660 |
| Complete producer additions `c` | 10,857,762 | 10,687,362 |
| Designated output uses `q` | 983,178 | 983,178 |
| Auxiliary roles per invocation `R=c+q` | 11,840,940 | 11,670,540 |
| Certified ternary-network saving | `7.5e-9` | `7.61e-9` |
| Conditional headline witness | `3.73e-9` | `3.8e-9` |

Set `h=28`, `v=binom(28,5)=98280`, `m=h^3`, and `N=v^3`. The retained rank
accounting gives

$$
W=2v^2(v+R),\qquad L=3v^2\binom{h}{2}(h-2),\qquad s=Wm-N+2L.
$$

The new deficit fraction is exactly

$$
\eta=\frac{Wm-s}{Wm}=\frac{117}{1537792480}.
$$

An exact rational logarithm enclosure proves
`eta > (761/10^11) log(m)`; `exp(-x) > 1-x` therefore supplies the strict
motif saving `a_b=761/10^11`. Retain `a_c=39/10^9` from PR #7. Choose

| Parameter | Exact value |
| --- | --- |
| epsilon | `4999/10000` |
| c | `9999/10000` |
| beta | `19/25` |
| delta | `1/10^6` |
| zeta | `1/10000` |
| C1 | `19601/10000` |
| lambda | `1-7609/10^12` |
| lambda prime | `1-7608/10^12` |

All 29 inherited fast-Gaussian/compact-control constraints are strict. The
minimum of the seven assembly margins is

$$
G_* = \frac{4754049}{1250000000000000}
     = 3.8032392\times10^{-9} > \kappa.
$$

The exact gap is `4049/1250000000000000`. This fixed positive gap supplies
the retained asymptotic absorption of logarithmic factors. The complex
precision guard is unchanged and its constants are checked again.

## Reproduce and review

From the repository root, using Python 3.11 or newer with assertions enabled
and a C++17 compiler:

```sh
python3.11 research/prime-field-followup/verify.py
make verify
git diff --exit-code -- upstream certificates patches
```

No third-party Python packages or network access are needed. Intermediate
files and the compiler output stay under `build/prime-field-followup/`.
The global checker needs approximately 1.2 GB memory. It reconstructs the
complete size-28 producer rather than sampling a subset.

The [certificate](certificate.json) includes exact counts, rational inequalities,
source and dependency hashes, and each selected template's hash and control
results. For every selected template, ternary bit-plane arithmetic checks all
source, target, and dirty-scratch basis directions simultaneously in both
orientations; actual compiled role-support paths are checked as well. The
retained size-eight network separately checks all 1,156 scalar basis directions
and both rational-frame schedules. That small network is the inherited
producer, not a full simulation of the modified size-28 network.

Review should examine whether preservation of the star boundaries and common
pair property is sufficient for the inherited global frame, bank-sharing,
finite-alphabet, and complete-layer interfaces. The finite checks and positive
parameter margins do not independently establish those general arguments.

## Attribution

The ternary motif, paired degree-three producer, initial four-point-star
resynthesis, and stronger complex producer are **Zhihao Chen (jacklightChen)'s
PR #7 contribution**, prepared with substantial OpenAI Codex assistance.
Pinned reference files are retained unchanged under `vendor/`, with full paths
and hashes in [provenance.json](provenance.json).

Preceding work remains credited to Douglas Colkitt (framework), Bortlesboat
(aligned pairing), dleen (retained totals and stage sharing), and eumemic
(complex compression, faster Gaussian resampling, and cheaper centers).
The original multiplication manuscript is OpenAI's.

The template-selection refinement, additional exact controls, and updated
parameter witness were prepared with substantial OpenAI Codex assistance at
Rohan Arun's request. This does not imply independent review, worldwide
priority, or OpenAI endorsement. The repository's Apache-2.0 license applies.
