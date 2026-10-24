# Doubled centre Gram degree at least 410

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

The actual historical doubled centre Gram has scalar minimal-polynomial
degree at least **410 at every positive tensor size**, improving Ali
Romman's PR4958 bound 409. Thus PR4958 Open next question 1 has a negative
answer: its full operator does not have degree exactly 409. Whenever
alpha I+beta A is invertible with beta!=0, a scalar-polynomial inverse
has degree at least 409, improving the necessary bound 408.

Claim type: a new finite exact certificate, with a scoped written
characteristic-zero and all-positive-tensor-size proof. The exact full
minimal polynomial is not determined. No new kappa follows.

The new step joins the distinct Bell blocks c=1 and c=11 as invariant
summands. On their 8,192-dimensional direct sum, 819 new moments give a
410-by-410 Hankel determinant **58805 modulo 65537**. The certificate uses
new seeds and does not consume or rerun the predecessor's 409 minor.
[PROOF.md](PROOF.md) states the operator, seeds, arithmetic bounds and
all-size/inverse deductions.

## Reproduce

From the repository root, using CPython 3.12 and NumPy 2.5.4:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/centre-gram-degree410/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/centre-gram-degree410/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/centre-gram-degree410
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/centre-gram-degree410 --check-source-history
```

Any equivalent Python 3.12 path can replace the local interpreter. The
direct marker is PASS_CENTRE_GRAM_DEGREE410. Both operator implementations
agree on all 1,638 block Krylov vectors; two exact determinant algorithms
agree on the new minor. Eight controls cover the missing new block,
linear dependence, pivoting, source corruption and truncated moments.
The complete generated receipt is available by adding --emit-result;
redirect it outside the checkout. It binds all package files and the
sole live input by SHA256. No receipt is handwritten.

VERIFY.json registers both warning-strict normal and optimized modes,
with 180-second limits. The actual query JSON is the sole live external
input. SOURCES.json also pins the original card, selected record and
PR4958's mathematical/source documents as historical provenance. The
scientific verifier needs neither Git nor any predecessor executable.
The official committed-package export includes the declared input and
can replay offline with the same Python/NumPy installation.

## Scope, overlap and credit

Base: canonical main 81e9bd69e4a5b00ba9c713a1620e36d576d5522e, priority
revision 7. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19142769).
TASK.json changes the formal-interface-lemma card to this explicit
algebraic handoff. The current selected source-binding orientation passed;
that check is metadata orientation, not scientific admission.

Credit Ali Romman's [PR4958](https://github.com/CrocSwap/integer-mult-bounds/pull/4958),
head c8c48ef5a497ffd7f7e778434c1f074b7b777a03, for the actual query,
Bell-block identity, common fixed vector, degree-409 certificate and open
question. PR4720 retains the historical query and source/native lineage;
PR1719 supplies the doubled port representation. The historical selected
source is bce54fb3f895cbe5cd4c0eb477c3afeed100190f. Retain icekylinx's
Gauge44 attribution and the K-triangle, porting, helper, compiler and
upstream lineage in PR4958's unchanged NOTICE.md and retained notices.
No predecessor code or notice is copied or modified. Krylov/Hankel minors
and modular nonvanishing are standard methods; no literature-priority
claim is made for those methods.

The live pre-claim overlap covered 323 open PR records and 4,243 Discussion
records with complete remote pagination. Sparse local coverage was
incomplete and was supplemented by distinctive-term searches of all
main-tree research READMEs and merged/all-state PRs. The target is
PR4958's open question, rather than a recent own-account follow-up.
No exhaustive arbitrary-diff or unpublished-work coverage is asserted.

This is one local obstruction, with no family construction round. Native
access, rounded precision, dirty restoration, storage, physical movement,
recursive pricing and complete supplier admission remain unknown. General
ADD circuits, rational expressions and matrix-valued encodings are outside
the scalar-polynomial restriction. No selected frontier, complete
multiplication theorem, independent human acceptance or formal proof-kernel
acceptance is claimed. Lean, Docker, predecessor scientific replays and the
selected cold replay were not run.

## Open next questions

- What is the exact full minimal-polynomial degree? Start by deriving a
  characteristic-zero annihilator from the joint Bell-block decomposition.
  The new modular minor gives a lower bound, not that missing upper bound.
- Can a useful decoder avoid scalar polynomials? Start with one specified
  general ADD, rational-expression or matrix-valued decoder and its source,
  output, dirty restoration and complete cost contract. Native access and
  the paid implementation remain blockers.

The structured versions, relevance and first steps are in TASK.json.
