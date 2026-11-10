# Independent review of the odd native common-grid draft

Reviewer: same-session research subagent, with substantial OpenAI assistance.
This is author-side independent-method review, not a human or formal-kernel
acceptance. No root-owned files were modified.

## Frozen scope

The reviewer froze the pre-clarification draft during the run. Its SHA-256 pins were:

- `PROOF.md`: `0a3b37c82869c37afbcea50ed1e440a8c8e6e9f01f3a84476c004586c1bec82e`
- `audit_bounds.py`: `1e859d997e667514864871fd64e2b01039107708a848ddfec340e3947d0bbbcb`

The exact source word/caller and threshold source are recorded in
`SOURCE-BYTES.json` and the executed `INDEPENDENT-BOUNDS.json`. Canonical base remains
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The source-specific mathematical
claim is the per-call scale-1125 precision implication for candidate #6934,
not a proof of the candidate's native maps, physical supplier or complete bill.

## Verdict

No mathematical counterexample or blocking gap was found within the stated
ideal endpoint, same-root-factor, ownership, scheduling and source interfaces.
The conclusion remains conditional on those interfaces. The independent
integer engines reproduce the finite bounds used in the all-size argument.

Two wording clarifications would improve the proof and make the inherited
scope harder to misread:

1. Section 2's fresh helper mass 1 and height 0 are **relative to the current
   raw-call entrance**. A helper introduced inside a nested compiler call
   carries its actual entrance expansion in original root inputs; its root
   mass/debt is not reset to 1/0. Section 3 and the credited #6901 proof imply
   this interpretation, but the present short sentence should say so.
2. Interface 1 should explicitly say **Gaussian-dyadic Clifford**, including
   absolute phase. A generic Clifford with an arbitrary global phase would
   not imply the stated binary grid. The source construction is in the
   Gaussian-dyadic subgroup; no extension to arbitrary global phases follows.

It is also useful to state the short compiler size check: 153<2^8 and
8*1920<H imply the fixed N exceeds the carrier m=153^1920. The source
threshold already checks the stronger written inequality, so this is
exposition rather than a failing gate.

## Independent finite evidence

The reviewer did not import the author's `audit_bounds.py` implementation.
`independent_bounds.py` uses two different representations:

- Native rows are sparse **integers on one fixed 24-bit fractional grid**,
  initially scaled by 1125. Every scalar multiplication uses exact integer
  quotient/remainder, including separate pre-ADD products. This independently
  checks the finite precision certificate and computes the least common
  multiple of the actual odd coefficient denominators from gcds.
- Caller mass is propagated as a **78 by 78 positive transfer matrix** on an
  increasing common integer grid. Row sums give the noncommutative triangle
  bound. No numerical character or commuting-operator identity is used.

The word engine visits all 14,060,742 coefficient instances and finds:
minimal odd scale 1125, dyadic height 24, mass
1636447290138225/16384, and literal numerator bit length 24. Two insufficient
scales reject at precise events: 225 at event 1101 and 375 at event 36915.

The separate caller matrix engine obtains height 163 and maximum mass
16246698892210214036146399419475929893435/256. Before a joint event, the
maximum mass is 758143798823020519902612486795530419693/64, below 2^124;
the maximum height is 154. Thus the local-plus-caller envelopes A=178 and
B=161 agree exactly with the proof's safe integer bounds.

The threshold routine reads candidate/tested rationals and logarithm power
2224 by AST from the retained source, without executing its scientific
program. It regenerates the integer threshold and checks both neighboring
indices. It verifies the 14,066-bit K_star and 14,075-bit 357*K_star; N itself
is never constructed.

Reproduction, from this run's workspace:

```sh
python -I -B research/odd-native-common-grid/independent_bounds.py
```

The final marker is `PASS_INDEPENDENT_ODD_GRID_BOUNDS`. The lead rebound only this audit script's source paths to the byte-identical
package-local snapshots and expected bounds. The registered verifier reruns
its independent engines. The audit is part of this package, not an additional
contribution or external human acceptance.

## All-size reasoning checked

The ideal recursion is defined before numerical execution. Compiler exits and
complements strictly reduce rank; ordinary substitution reduces selected width.
Thus using ideal endpoint identities to reset only **extra entrance-relative
debt** is not a circular assumption of exact finite-precision child returns.
Completed siblings leave no extra debt, whereas already present entrance debt
persists. Per-call scale 1125 applies independently to each unfinished local
context. A one-time outer factor 1125 is a different program and would fail
under nesting; the proof correctly excludes that shortcut.

The compiler recurrence bounds source dependence depth, not bank count. Its
inherited contraction is applicable after separation because paid ranks are
strictly below every productive rank and the latter are at least two. The
ordinary root bound t=K_star*floor(log_N D), together with
357*K_star<N and N*ell<=N^ell<=D, gives 356t<D, also at ell=0.

Every completed root-factor Clifford row has dyadic entry denominator at
most 2^ceil(D/2) and unit Euclidean norm. Combining this once with exterior
denominator 178t and mass 2*2^(161t), rather than charging the Clifford
denominator at each recursive level, gives the stated F and magnitude
requirements. Integer parity of D gives 178t<=floor(D/2), so F=p+D and
W=p+h+2D+3 suffice. The W recomputation correctly accounts for the raised
fractional grid.

Temporary W+26 bits safely cover signed multiplication by a numerator of
at most 24 bits and the subsequent addition; the complete four-term Gaussian
pair numerator is smaller. Quotients are exact because their ideal results
are proved to be grid values. No rounding of individual Gaussian summands is
licensed. A partial in-place field need not have a Clifford-vector form;
the no-consumer-before-return premise and old/new component bounds are the
correct way to cover those writes. A complete external row is required:
projecting on a selected ancestor coordinate would invalidate the invariant.

## Limits

This review does not establish arbitrary-width native map/phase identities,
the full root preprocessing or H0 boundary, owned erasure, a physical scalar
table, storage capacity, source access or complete asymptotic admission. It
does not rerun #6934's supplier invoice or selected certificate. Those remain
explicit obligations, and no new kappa or unconditional theorem follows.

## Lead response before package freeze

Both wording clarifications above were applied. The carrier-size inequality
was added. No scientific bound or finite receipt changed. The independent
engines were rebound to package-local byte-authenticated sources and replayed
as part of the registered normal/optimized gates; see VERIFICATION.md.
