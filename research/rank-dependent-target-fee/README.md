# Rank-dependent fees for one target split

**Result.** For a nondecreasing concave tariff \(\varphi\) with \(\varphi(0)=0\), a
nonnegative flat fee \(c\) and a rational slope \(d\), the fee shape
\(c + d\,\varphi(r_i)\) has an exact answer in both readings left open by the
uniform-fee theorem. **No new κ.** The selected record stays
\(363005817/100000000000\).

This is a written proof with an exhaustive finite corroboration. It is not a
search, a caller, an invoice reading, or a supplier admission.

## Two fee readings

A positive integer partition \(r_1+\cdots+r_k=R\) replaces one productive
target of rank \(R\). The predecessor charges the flat fee \(c\) once for each
piece after the first, and proves that the balanced partition is optimal and
that a strict improvement exists exactly when the balanced halving gain exceeds
\(c\). The stated next step is the rank-dependent fee \(c + d\,\varphi(r_i)\).
That sentence has two contracts.

**Reading A.** Every piece pays \(c + d\,\varphi(r_i)\), and the unsplit target
pays the same formula. The credit difference is

\[
\Delta_A = (1-d)\Bigl(\sum_i \varphi(r_i)-\varphi(R)\Bigr)-(k-1)c.
\]

**Reading B.** Only the \(k-1\) extra pieces pay, and the free piece is chosen
to maximise the credit. This is the predecessor's \((k-1)\)-fee count with a
rank slope added. At \(d=0\) the two readings agree.

## Theorems

The argument is [PROOF.md](PROOF.md). Under the tariff hypotheses above:

- **Reading A, \(d<1\).** The balanced partition maximises each fixed length.
  The best length is the first \(k\) whose balanced forward difference is at
  most \(c\). A strict improvement exists if and only if
  \((1-d)\bigl(\varphi(\lfloor R/2\rfloor)+\varphi(\lceil R/2\rceil)-\varphi(R)\bigr)>c\).
- **Reading A, \(d\ge 1\).** No partition improves on the unsplit target. Among
  a fixed length \(k\ge 2\), the extreme partition \((R-k+1,1,\ldots,1)\) is
  best and the balanced partition is worst. They differ exactly when their
  \(\varphi\)-sums differ. For the harmonic tariff at \(R=6\), \(d=2\) and
  \(c=0\), those losses are \(-49/30\) and \(-41/20\).
- **Reading B, \(d\ge 1\).** No partition improves on the unsplit target.
- **Reading B, \(d\ge 0\).** A strict improvement exists if and only if some
  two-part split improves. The test frees the longer part:
  \(\max_{1\le b\le\lfloor R/2\rfloor}\bigl(\varphi(R-b)+(1-d)\varphi(b)-\varphi(R)\bigr)>c\).
  The maximiser need not be balanced, and it need not have two parts. For
  \(\varphi(n)=n\), \(R=6\), \(d=1/2\) and \(c=0\), \((2,2,2)\) scores \(-2\)
  and \((4,1,1)\) scores \(-1\). For the harmonic tariff with the same
  parameters, \((4,1,1)\) scores \(19/30\), the balanced split scores
  \(11/20\), and the best two-part split is \((4,2)\) at \(23/60\).
- **Reading B, \(d<0\).** Balancedness already fails: the same linear example
  with \(d=-1\) scores \(4\) on \((2,2,2)\) and \(5\) on \((4,1,1)\). The
  two-part existence test is not proved for a negative slope.

The hypotheses are sharp. The nonconcave table \((0,0,1,1,1,1,2)\) at \(R=6\)
has halving gain \(0\) and three-part gain \(1\) when \(d=c=0\). A negative
flat fee lets a slope \(d=2\) pay: \(\Delta_A=1\) at \(c=-1\), and
\(\Delta_B=1\) at \(c=-3\), both on the partition \((1,3)\) of the identity
tariff.

## Finite census for the unproved negative slope

For Reading B with \(d<0\), the verifier exhausts every integer partition of
every rank \(3\le R\le 18\), for the five tariffs identity, harmonic numbers,
\(\min(n,3)\), \(n(36-n)\) and \(n/(n+1)\), and for each slope in
\(\{-2,-1,-1/2,-1/3\}\). In that box, no nonnegative flat fee makes a split of
length at least \(3\) strictly positive while every two-part split is
nonpositive. This is an exhaustive finite census of that box. It is not a
proof for every rank, every concave tariff, or every negative slope.

The grid also recomputes both closed forms on every partition of every rank
through \(18\), for nine slopes and seven nonnegative fees, and checks the
suffix-window bound used in the Reading B proof on those same partitions.

## Scope

Catalogue card `coverage-law-change`, priority revision 8, base
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **changed**. The card
asks for one completed call with a legal producer and consumer bill. This
package answers the rank-dependent fee question in
`research/uniform-fee-target-refinement`, which is an accounting test for when
an independent-target split can raise the signed credit. It stops before a
word, a native operator, or an invoice. The selected-invoice splitting claim
in discussion comment 19530156, and the fixed-profile ceilings in open #7175,
are different objects; this verifier does not read the #7000 ledger.

The orientation command `python3 -B scripts/research_selected_baseline.py`
printed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for
\(\kappa = 363005817/100000000000\). That check is metadata only.

Overlap was checked against open and closed PR titles and bodies for the
phrases `rank-dependent` and `uniform-fee target`. The only match is merged
#6651, which states this question and does not answer it. No match is not a
novelty certificate. The live discussion claims from 2026-11-11 do not name
this fee shape.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/rank-dependent-target-fee/verify.py
python3 -O -B research/rank-dependent-target-fee/verify.py
python3 -B scripts/research_package.py --package research/rank-dependent-target-fee --check-only
```

The marker is `PASS_RANK_DEPENDENT_TARGET_FEE`. Both direct runs on CPython
3.12 printed `partitions=7980 comparisons=5670 R<=18 tariffs=5`.

Not run: `make frontier7000-verify`, any selected-invoice export, and any
native or caller replay.

## Open next questions

- Does Reading B with a negative slope still have a two-part existence test?
  The finite census above found no counterexample in its box. The suffix-window
  proof uses that the free piece is a longest part, which is the nonnegative
  slope. A negative slope frees a shortest part, and a charged part may then
  be longer than half the rank.
- Which of the two readings, if either, is the legal adapter on one selected
  #7000 helper? First step: name the physical fee, then apply Theorem A or B.
  This package does not open the ledger. The selected splitting claim in
  discussion comment 19530156 is a different question.
- When several targets share one fixed adapter plus a per-piece fee, what is
  the joint optimum? That is the third question of #6651. The one-target
  argument here does not price a shared fee.

## Credit

Nick Petalas, #6651, for the uniform-fee theorem, the balanced halving test,
and the rank-dependent question answered here. Ali Romman, #5769, for the
fee-charged target-partition contract. #5909 for the unit-fee threshold at
exponent \(99/100\), which is not recomputed. Karamata's inequality and the
concavity of perspective functions are classical, as in #6651. The signed
mixed-target invoice model is zxv's, as credited in
`docs/research/recursive-invoice-preflight.md`; it is context, not an input
to the verifier.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review or proof-kernel check is claimed.
