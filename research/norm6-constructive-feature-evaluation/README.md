# Explicit norm-six dyadic feature evaluation

The 19600-term dyadic bound is already PR5084's result. This package supplies
what that result left open: an explicit transform of PR2222's actual19648
integer-valued cubic features into19600 evaluable pairs, without a full-shell
matrix, general integer normal-form computation or coefficient lookup table.

For the pinned P48p Gram,21 diagonal-six coordinates use mixed-cubic pivots
of coefficient4;26 diagonal eights and one ten use linear pivots1 or2. One
anchor substitution completes the transform. Its54996 nonzero coefficients
are quarter-integral, with scaled magnitude<=48 and target accumulation mass52.
Source features are unchanged retained integral polynomials; target features
are integer numerators over256. PROOF.md gives the exact all-port identity,
setup bounds, integer-operation counts, working widths and workspace slots.
This is an indexed arithmetic evaluator, not physical tape execution.

The independent checker expands all48 relations in ordinary monomials, checks
their complete polynomial ideal identities and coefficient bounds, then checks
988 complete feature pairings on the26 original actual-Gram shell vectors and
12 wider target vectors. It rejects a corrupted transform, omitted cubic
correction, off-shell source, wrong normalization, invalid diagonal and the
non-dyadic shortcut premise. Source hashes and frozen result are mandatory.

    python3.12 -B scripts/research_package.py --package research/norm6-constructive-feature-evaluation
    python3.12 -I -O -B research/norm6-constructive-feature-evaluation/verify.py

No predecessor scientific verifier is imported or replayed. The small source
fixture recipe and original feature identity retain Cinna Davis's credit.
PR5084's proof and implementation were inspected at exact head
9d7f7805d147028fe5f0174e267ee05b73703f0b and are now retained in the base20a1
source ancestry. Its evaluated-matrix factorizer does not implement this
symbolic transform. Source manifest bytes remain unchanged.

## Open next questions

The algebraic support bound remains49*19600=960400; no new term bound, physical
invoice, selected frontier or kappa is claimed. P48p geometry, minimum, complete
shell and binary chart remain inherited. Physical source acquisition, I-K side
program, frame/owner legality, dirty restoration, precision/Tape placement,
matched bit supplier and compiler/outer admission remain open. The explicit
integer arithmetic costs do not make these unknown costs zero.

Before further optimization, bind one actual physical source/target block to
these features and its full paid allowance. Sharper coefficient bounds alone
are not a reason to extend this family. The mechanism decision is to change
from recent Core/Gaussian work to the source-independent norm-six evaluator;
stop construction if the actual consumer cannot afford its complete invoice.

Credit Cinna Davis PR2222, DreamingOfClouds PR2244, Dugongue PR4494, Nick Petalas
PR5084, Nebe/Sloane and the retained Leech/Niemeier lineage. Original source
notices are preserved. New work by JoyboyBrian with substantial OpenAI Codex
assistance, Apache-2.0. No independent human or formal proof-kernel acceptance.

Canonical claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19143416
Read-only scout covered325 PR bodies and4246 Discussion records, followed by
root's execution refresh307 PRs/4264 Discussions/6884 notes. This is bounded
coordination evidence, not a novelty guarantee. R7–R9 scoped work and active
coded-caller claims were checked; the latter motivated the mechanism change.
