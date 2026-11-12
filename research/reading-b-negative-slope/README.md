# Reading B existence test for a negative slope

**Result.** For a nondecreasing concave tariff \(\varphi\) with \(\varphi(0)=0\) and
a negative slope \(d\), Reading B frees a shortest piece. A partition strictly
improves on the unsplit target if and only if a two-part partition does. The
threshold is the best short-free two-part gain

\[
G=\max_{1\le b\le\lfloor R/2\rfloor}
  \bigl(\varphi(b)+(1-d)\varphi(R-b)-\varphi(R)\bigr),
\]

and the improvement exists exactly when the flat fee satisfies \(c<G\). Every
partition with \(m\) extra pieces has credit at most \(m(G-c)\). **No new κ.**
The selected record stays \(363005817/100000000000\).

**Evidence class.** [PROOF.md](PROOF.md) is a written proof for every rank and
every real \(d<0\). The verifier's grid is an exhaustive finite census of the
declared box \(2\le R\le 22\), seven tariffs and five negative slopes. That
census corroborates the proof and checks the failure controls. It is not a
substitute for the proof, and the proof's hypotheses are part of the claim.

This package does not construct a caller, read a selected invoice, or admit a
supplier. A positive credit is an accounting comparison under the stated fee.

## Contract

Reading B charges \(c+d\,\varphi(r_i)\) on every piece after the first. The free
piece maximises the credit. For \(d<0\) that piece has minimum tariff, so it
may be taken to be a shortest piece. The predecessor
[#7299](https://github.com/CrocSwap/integer-mult-bounds/pull/7299) proves the
same existence statement when \(d\ge 0\), freeing a longest piece, and states
this negative-slope case as an open question. Its nonnegative proof does not
transfer: the long-free threshold is smaller than \(G\) on unequal pieces, and
a charged piece need not be at most \(\lfloor(R-1)/2\rfloor\).

The argument that replaces that step is a one-piece gap bound. Along any order
of the charged pieces, the first piece contributes no gap because
\(\varphi(0)=0\), and each later gap is at most \(G/(1-d)\).

## What the test does and does not decide

The test is an existence statement. Three exact comparisons show the boundary.

- Identity tariff, \(R=6\), \(d=-1\). The short-free threshold is \(5\) and the
  long-free threshold used by #7299 is \(3\). At \(c=4\), the split \((5,1)\)
  has credit \(1\). In \((4,1,1)\) the free piece is \(1\) and a charged piece
  is \(4>\lfloor 5/2\rfloor\).
- Harmonic tariff, \(R=6\), \(d=-1\), \(c=0\). The balanced split \((2,2,2)\)
  scores \(101/20\), strictly above the best two-part score \(193/60\). Its
  per-piece ratio \(101/40\) remains below \(193/60\).
- Cap \(\varphi(n)=\min(n,1)\), \(R=8\), \(d=-1\). The split \((6,1,1)\) meets
  the per-piece bound with equality: its \(c\)-free credit is \(4=2G\).

Concavity is necessary. On \(\varphi=(0,0,1,1,1,3)\) at rank \(5\), with
\(d=-1\) and \(c=0\), every two-part credit is nonpositive and \((2,2,1)\)
scores \(1\). The nonconcave table \((0,0,1,1,1,1,2)\) from #7299 separates the
same statement at rank \(6\), \(d=-1\) and \(c=1\).

For \(d=1/2\) on the harmonic tariff at rank \(6\), the long-free threshold is
\(23/60\) and the short-free threshold is \(3/10\). The fee \(c=1/3\) lies
strictly between them. The short-free test is the negative-slope contract.

## Scope

Catalogue card `coverage-law-change`, priority revision 8, base
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **changed**. The card
asks for one completed call with a legal producer and consumer bill. This
package answers only the negative-slope existence question left by #7299. It
does not reprove the nonnegative theorems in that PR, and it does not cross the
family expansion gate: there is no new word, operator, or invoice.

Overlap checked on 2026-11-12 against open and merged PR titles and bodies for
the negative-slope Reading B test. #7299 states the question, gives a census
through rank \(18\) on five tariffs, and says that census is not a proof.
Merged #6651 is the uniform-fee theorem, the case \(d=0\). #5769 and #5909
supply the earlier fee-charged partition contract and are not recomputed.
#7303 cites #7299 while bounding a different fixed-word P104 split. No match is
not a novelty certificate. The physical-adapter question and the shared-adapter
question in #7299 are different contracts and are not taken here.

The predecessor proof is the open PR head
`bfcb85c0b7298392607092f751df4a7b1afb60c6` on
`cursor/rank-dependent-target-fee-7c04`. That commit is not an ancestor of
this base, so this package does not pin it as a Git input. The definitions it
uses are restated in [PROOF.md](PROOF.md). The verifier imports no code from
that PR.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/reading-b-negative-slope/verify.py
python3 -O -B research/reading-b-negative-slope/verify.py
python3 -B scripts/research_package.py --package research/reading-b-negative-slope --check-only
```

The marker is `PASS_READING_B_NEGATIVE_SLOPE`. The census bound is rank \(22\).

Not run: `make frontier7000-verify`, any selected-invoice export, and any
native or caller replay. The selected-record read in the verifier checks the
pinned κ string only.

## Open next questions

- Which partition maximises \(\Delta_B\) for a negative slope? The existence
  test does not answer this. On the harmonic tariff at rank \(6\), \(d=-1\) and
  \(c=0\), \((2,2,2)\) scores \(101/20\) and the best two-part split scores
  \(193/60\). On the identity tariff every split that contains a \(1\) ties the
  best two-part split when \(c=0\). On \(\varphi(n)=\min(n,1)\) the three-part
  split \((6,1,1)\) meets the per-piece bound with equality. First step: at
  \(c=0\), classify the maximiser by the length of the free piece for the
  harmonic tariff through rank \(12\). The blocker is mathematical. Neither
  the balanced partition nor the extreme partition wins on every concave
  tariff, so a majorisation comparison does not name the maximiser.

The legal-adapter question and the shared-adapter question stated in #7299
remain open and are not questions of this package.

## Credit

Nick Petalas, #6651, for the uniform-fee theorem and the rank-dependent
question. Ali Romman, #5769, for the fee-charged target-partition contract.
#5909 for the unit-fee threshold at exponent \(99/100\), which is not
recomputed. #7299 for the nonnegative-slope proof, the Reading B formula, the
explicit statement that the negative-slope test was open, and the nonconcave
table reused as a control. The one-piece gap bound is elementary and replaces
the suffix-window step for this sign.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review or proof-kernel check is claimed.
